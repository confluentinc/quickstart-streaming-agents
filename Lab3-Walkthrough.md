# Lab3 - Agentic Fleet Management Using Confluent Intelligence

[Current NOLA Keynote Demo](https://youtu.be/qSwVl72etgY?si=F6v119wshtIYlpGa&t=4410)

The Agentic Fleet Management Demo is an end-to-end demo that pulls together elements of all the previous Streaming Agent Labs we've created so far. It showcases:
- MCP tool calling and Agent Definition (`CREATE AGENT`) from Lab1,
- Vector search and RAG from Lab2,
- Anomaly detection, and
- Use of Confluent's new **[Real-Time Context Engine](https://www.confluent.io/blog/introducing-real-time-context-engine-ai/)**.

## Prerequisites

You will need to have these credentials ready in order to deploy all labs:
  - `zapier_sse_endpoint` - see [Lab1 Zapier MCP server instructions.](./Lab1-Walkthrough.md#zapier-remote-mcp-server-setup)
  - `mongodb_connection_string` - looks like `mongodb+srv://cluster0.c45vbkg.mongodb.net/` - no username and password in the string. See [Lab2 MongoDB setup instructions](./Lab2-Walkthrough.md#step-1-create-mongodb-atlas-account-and-cluster).
  - `mongodb_username` and `mongodb_password`- these are database-specific credentials, not your mongodb.com login. See [Lab2 MongoDB setup instructions](./Lab2-Walkthrough.md#step-1-create-mongodb-atlas-account-and-cluster).

- ⚠️ **IMPORTANT: AWS Users Only:** To access Claude Sonnet 3.7 you must request access to the model by filling out an Anthropic use case form (or someone in your org must have previously done so) for your cloud region. To do so, visit the [Model Catalog](https://console.aws.amazon.com/bedrock/home#/model-catalog), select Claude 3.7 Sonnet and open it it in the Playground, then send a message in the chat - the form will appear automatically. ⚠️

## Deploy the Demo

Once you have these credentials ready, run the following command and choose **Lab3**:

  ```sql no-parse
  uv run deploy
  ```
  Then, publish the New Orleans local event documents to MongoDB by running the following command. Choose 'yes' to clear your MongoDB database of all documents when prompted, if you previously uploaded documents for Lab2:
```sql
uv run publish_docs --lab3
```
## SQL Queries

### 1. Detect surge in `ride_requests` using `ML_DETECT_ANOMALIES`

This query shows how to use the built-in Flink AI function, `ML_DETECT_ANOMALIES` to quickly identify unexpected surges or variances in real-time data streams. A common design pattern is for organizations to use anomaly detection as a trigger that kicks off a streaming agent, enabling it to take action given some change in the data.

Read the [blog post](https://docs.confluent.io/cloud/current/ai/builtin-functions/detect-anomalies.html) and view the [documentation](https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html#flink-sql-ml-anomaly-detect-function) on Flink anomaly detection for more details about how it works.

```sql
CREATE TABLE anomalies_detected_per_zone AS
WITH windowed_traffic AS (
    SELECT 
        window_start,
        window_end,
        window_time,
        pickup_zone,
        COUNT(*) AS request_count,
        SUM(number_of_passengers) AS total_passengers,
        SUM(CAST(price AS DECIMAL(10, 2))) AS total_revenue
    FROM TABLE(
        TUMBLE(TABLE ride_requests, DESCRIPTOR(request_ts), INTERVAL '5' MINUTE)
    )
    GROUP BY window_start, window_end, window_time, pickup_zone
),
anomaly_detection AS (
    SELECT 
        pickup_zone,
        window_time,
        request_count,
        total_passengers,
        total_revenue,
        ML_DETECT_ANOMALIES(
            CAST(request_count AS DOUBLE),
            window_time,
            JSON_OBJECT(
                'minTrainingSize' VALUE 287,
                'maxTrainingSize' VALUE 7000,
                'confidencePercentage' VALUE 99.999,
                'enableStl' VALUE FALSE           
            )
        ) OVER (
            PARTITION BY pickup_zone
            ORDER BY window_time 
            RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS anomaly_result
    FROM windowed_traffic
)
SELECT 
    pickup_zone,
    window_time,
    request_count,
    total_passengers,
    total_revenue,
    CAST(ROUND(anomaly_result.forecast_value) AS BIGINT) AS expected_requests,
    anomaly_result.upper_bound AS upper_bound,
    anomaly_result.lower_bound AS lower_bound,
    anomaly_result.is_anomaly AS is_surge
FROM anomaly_detection
WHERE anomaly_result.is_anomaly = true 
  AND request_count > anomaly_result.upper_bound;
```

> [!NOTE]
>
> It will typically take around five minutes for Flink to detect an anomaly. The reason for this is that we're detecting anomalies in 5-minute "windows", and we need to wait for the first window to close before Flink can detect one.

### 2. Enrich the `ride_requests` with possible causes of the anomaly using vector search

```sql
CREATE TABLE anomalies_enriched
WITH ('changelog.mode' = 'append')
AS SELECT
    pickup_zone,
    window_time,
    request_count,
    expected_requests,
    anomaly_reason,
    top_chunk_1,
    top_chunk_2
FROM (
    SELECT
        rad_with_rag.pickup_zone,
        rad_with_rag.window_time,
        rad_with_rag.request_count,
        rad_with_rag.expected_requests,
        rad_with_rag.is_surge,
        TRIM(llm_response.response) AS anomaly_reason,
        rad_with_rag.top_chunk_1,
        rad_with_rag.top_chunk_2
    FROM (
        SELECT
            rad.pickup_zone,
            rad.window_time,
            rad.request_count,
            rad.expected_requests,
            rad.is_surge,
            rad.query,
            vs.search_results[1].document_id AS top_document_1,
            vs.search_results[1].chunk AS top_chunk_1,
            vs.search_results[1].score AS top_score_1,
            vs.search_results[2].document_id AS top_document_2,
            vs.search_results[2].chunk AS top_chunk_2,
            vs.search_results[2].score AS top_score_2
        FROM (
            SELECT
                pickup_zone,
                window_time,
                request_count,
                expected_requests,
                is_surge,
                CONCAT(
                    'Transportation demand surge in ',
                    pickup_zone,
                    ' zone at ',
                    DATE_FORMAT(window_time, 'MMM. dd ''at'' HH:mm'),
                    '. Groups of passengers requesting rides simultaneously. Expected requests: ',
                    CAST(expected_requests AS STRING),
                    ', Actual requests: ',
                    CAST(request_count AS STRING),
                    ' (increase of ',
                    CAST(ROUND(((request_count - expected_requests) / expected_requests) * 100, 1) AS STRING),
                    '%). What events, conferences, festivals, or gatherings in or near ',
                    pickup_zone,
                    ' are causing this increase in ride requests?'
                ) AS query,
                emb.embedding
            FROM anomalies_detected_per_zone,
            LATERAL TABLE(ML_PREDICT('llm_embedding_model',
                CONCAT(
                    'Transportation demand surge in ',
                    pickup_zone,
                    ' zone at ',
                    DATE_FORMAT(window_time, 'MMM. dd ''at'' HH:mm'),
                    '. Groups of passengers requesting rides simultaneously. Expected requests: ',
                    CAST(expected_requests AS STRING),
                    ', Actual requests: ',
                    CAST(request_count AS STRING),
                    ' (increase of ',
                    CAST(ROUND(((request_count - expected_requests) / expected_requests) * 100, 1) AS STRING),
                    '%). What events, conferences, festivals, or gatherings in or near ',
                    pickup_zone,
                    ' are causing this increase in ride requests?'
                )
            )) AS emb
            WHERE is_surge = true
        ) AS rad,
        LATERAL TABLE(
            VECTOR_SEARCH_AGG(
                documents_vectordb,
                DESCRIPTOR(embedding),
                rad.embedding,
                2
            )
        ) AS vs
    ) AS rad_with_rag,
    LATERAL TABLE(
        ML_PREDICT(
            'llm_textgen_model',
            CONCAT(
                'Based on the retrieved event documents, provide a one-two sentence reason for the traffic increase. Include specific event names, expected attendance numbers, and peak times when available.\n\n',
                'USER QUERY: ', rad_with_rag.query, '\n\n',
                'RETRIEVED DOCUMENTS:\n',
                'Document 1 (Score: ', CAST(rad_with_rag.top_score_1 AS STRING), '):\n',
                'Source: ', rad_with_rag.top_document_1, '\n',
                rad_with_rag.top_chunk_1, '\n\n',
                'Document 2 (Score: ', CAST(rad_with_rag.top_score_2 AS STRING), '):\n',
                'Source: ', rad_with_rag.top_document_2, '\n',
                rad_with_rag.top_chunk_2, '\n\n',
                'Provide only the reason, no additional text.'
            )
        )
    ) AS llm_response
);
```
### 3. Run `CREATE TOOL` and `CREATE AGENT` to define agent tools, prompt, and capabilities

See [CREATE TOOL documentation](https://docs.confluent.io/cloud/current/flink/reference/statements/create-tool.html).
```sql
CREATE TOOL zapier
USING CONNECTION `zapier-mcp-connection`
WITH (
  'type' = 'mcp',
  'allowed_tools' = 'webhooks_by_zapier_get, webhooks_by_zapier_custom_request, gmail_send_email',
  'request_timeout' = '30'
);
```

See [CREATE AGENT documentation](https://docs.confluent.io/cloud/current/flink/reference/statements/create-agent.html#flink-sql-create-agent).
```sql
CREATE AGENT `boat_dispatch_agent`
USING MODEL `zapier_mcp_model`
USING PROMPT 'You are an intelligent boat dispatch coordinator for a riverboat ride-sharing service.

Your workflow:
1. ANALYZE the surge information provided (zone, time, request count, anomaly reason)
2. REVIEW the available vessels list
3. SELECT appropriate boats to dispatch based on:
   - Proximity to the target zone
   - Boat capacity
   - Current availability
   - Surge magnitude (dispatch up to 8 boats for large surges)
4. CREATE a JSON dispatch request with this exact structure:
   {
     "action": "dispatch_boats",
     "zone": "<target_zone>",
     "boats": [
       {
         "vessel_id": "<VESSEL-[10-40]>",
         "new_zone": "<target_zone>",
         "new_availability": "available"
       }
     ]
   }
5. USE the webhooks_by_zapier_custom_request tool to POST the dispatch request to:
   URL: https://p8jrtzaj78.execute-api.us-east-1.amazonaws.com/prod/api/dispatch
   Method: POST
   Headers: {"Content-Type": "application/json"}
   Data: <your generated JSON>

6. FORMAT your final response with these THREE sections:

Dispatch Summary:
Due to the surge in demand in [zone] as a result of [event], we dispatched [n] additional boats from [list of zones].

Dispatch JSON:
{your dispatch JSON here}

API Response:
{the response from the API call}

CRITICAL INSTRUCTIONS:
- Dispatch boats from nearby zones first
- Dispatch more boats with larger capacities for big surges (up to 8 boats)
- Your response MUST contain the three labeled sections
- The dispatch JSON must be valid and contain only the structure shown above
- Always execute the POST request and include the API response
- Do NOT include any other explanatory text outside these three sections'
USING TOOLS `zapier`
WITH (
  'max_iterations' = '5'
);
```
### 4. Invoke the agent with `AI_RUN_AGENT`

See [AI_RUN_AGENT documentation](https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html#flink-sql-ai-run-agent-function).
```sql
CREATE TABLE completed_actions (
    PRIMARY KEY (pickup_zone) NOT ENFORCED
)
WITH ('changelog.mode' = 'append')
AS SELECT
    pickup_zone,
    window_time,
    request_count,
    anomaly_reason,
    TRIM(REGEXP_EXTRACT(CAST(response AS STRING), 'Dispatch Summary:\s*\n(.+?)(?=\n\nDispatch JSON:)', 1)) AS dispatch_summary,
    TRIM(REGEXP_EXTRACT(CAST(response AS STRING), 'Dispatch JSON:\s*\n(?:```json\s*)?([\s\S]+?)(?:```)?(?=\n\nAPI Response:)', 1)) AS dispatch_json,
    TRIM(REGEXP_EXTRACT(CAST(response AS STRING), 'API Response:\s*\n(?:```json\s*)?([\s\S]+?)(?:```)?$', 1)) AS api_response
FROM anomalies_enriched,
LATERAL TABLE(AI_RUN_AGENT(
    `boat_dispatch_agent`,
    `anomaly_reason`,
    `pickup_zone`
));
```

## Troubleshooting
<details>
<summary>Click to expand</summary>

- **No anomalies detected?** Check that your data generation is running. The first anomaly should be detected after both data generation (run `uv run lab3_datagen`) and the anomaly detection query **(Query #1)** have been running for about 5 minutes. This is because the anomaly detection query uses 5-minute windows, and we have to wait for the first window to close before the detection algorithm can identify an anomaly.

- **Error when running Query #1?:** `The window function requires the timecol is a time attribute type, but is TIMESTAMP_WITH_LOCAL_TIME_ZONE(3).`
  - Run the query below and try again. This can occur if you drop the pre-created `ride_requests` table and then re-run data generation, because neither Flink nor the data generator know we want to use `request_ts` as our watermark column until we tell them.
```sql no-parse
ALTER TABLE ride_requests
MODIFY (WATERMARK FOR request_ts AS request_ts - INTERVAL '5' SECOND);
```
- **Email about a degraded Flink statement?**
  - Press "Stop" on the running `CREATE TABLE anomalies_detected_per_zone` statement in the SQL Workspace.
    - The anomaly detection algorithm expects data to be flowing through it, and the statement will change to "degraded" after some time if you turn off data generation. Turning it off will stop the problem, or it will automatically resume running properly once data begins flowing again.

- `Runtime received bad response code 403. Please also double check if your model has multiple versions.` error?
  - **AWS?** Ensure you've activated Claude 3.7 Sonnet in your AWS account. See: [Prerequisites](#prerequisites)
  - **Azure?** Increase the tokens per minute quota for your GPT-4 model. Quota is low by default.
</details>

## Navigation

- **← Back to Overview**: [Main README](./README.md)
- **← Previous Lab**: [Lab2: Vector Search & RAG](./LAB2-Walkthrough.md)
- **🧹 Cleanup**: [Cleanup Instructions](./README.md#cleanup)