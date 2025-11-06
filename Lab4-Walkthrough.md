# Lab4 - Agentic Fleet Management using Confluent Intelligence

[Current NOLA Keynote Demo](https://youtu.be/qSwVl72etgY?si=F6v119wshtIYlpGa&t=4410)

The Agentic Fleet Management Demo is an end-to-end demo that pulls together elements of all the previous Streaming Agent Labs we've created so far. It showcases:
- MCP tool calling and Agent Definition (`CREATE AGENT`) from Lab1,
- Vector search and RAG from Lab2,
- Anomaly Detection from Lab3, and
- Use of Confluent's new **[Real-Time Context Engine](https://www.confluent.io/blog/introducing-real-time-context-engine-ai/)**.

## Prerequisites
You will need to have these credentials ready in order to deploy all labs:
  - `zapier_sse_endpoint` - see [Lab1 Zapier MCP server instructions.](./Lab1-Walkthrough.md#zapier-remote-mcp-server-setup)
  - `mongodb_connection_string` - looks like `mongodb+srv://cluster0.c45vbkg.mongodb.net/` - no username and password in the string. See [Lab2 MongoDB setup instructions](./Lab2-Walkthrough.md#step-1-create-mongodb-atlas-account-and-cluster).
  - `mongodb_username` and `mongodb_password`- these are database-specific credentials, not your mongodb.com login. See [Lab2 MongoDB setup instructions](./Lab2-Walkthrough.md#step-1-create-mongodb-atlas-account-and-cluster).

## Deploy the Demo

- Once you have these credentials ready, run the following command and choose **All Labs** when prompted:

  ```sql
  uv run deploy
  ```

## SQL Queries

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



```sql
SET 'client.statement-name'='anomalies-enriched-rag-create';
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

```sql
SET 'client.statement-name'='create-agent-tool';
CREATE TOOL zapier
USING CONNECTION `zapier-mcp-connection`
WITH (
  'type' = 'mcp',
  'allowed_tools' = 'webhooks_by_zapier_get, webhooks_by_zapier_custom_request, gmail_send_email',
  'request_timeout' = '30'
);
```

```sql
SET 'client.statement-name'='create-boat-dispatch-agent';
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
- Consider boat capacity when selecting vessels
- Dispatch more boats for larger surges (up to 8 boats)
- Your response MUST contain these three labeled sections
- The dispatch JSON must be valid and contain only the structure shown above
- Always execute the POST request and include the API response
- Do NOT include any other explanatory text outside these three sections'
USING TOOLS `zapier`
WITH (
  'max_iterations' = '5'
);
```

```sql
SET 'client.statement-name'='completed-actions-create';
CREATE TABLE completed_actions (
    PRIMARY KEY (pickup_zone) NOT ENFORCED
)
WITH ('changelog.mode' = 'append')
AS
SELECT
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

