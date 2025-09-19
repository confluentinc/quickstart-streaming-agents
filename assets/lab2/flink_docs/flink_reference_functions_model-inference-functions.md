---
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html
title: AI Model Inference and Machine Learning Functions in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'functions', 'model-inference-functions.html']
scraped_date: 2025-09-05T13:50:16.946411
---

# AI Model Inference and Machine Learning Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides built-in functions for invoking remote AI/ML models in Flink SQL queries. These simplify developing and deploying AI applications by providing a unified platform for both data processing and AI/ML tasks.

  * AI_COMPLETE: Generate text completions.
  * AI_EMBEDDING: Create embeddings.
  * AI_FORECAST: Forecast trends.
  * AI_TOOL_INVOKE: Invoke model context protocol (MCP) tools.
  * ML_DETECT_ANOMALIES: Detect anomalies in your data.
  * ML_EVALUATE: Evaluate the performance of an AI/ML model.
  * ML_PREDICT: Run a remote AI/ML model for tasks like predicting outcomes, generating text, and classification.

## Search Functions¶

Confluent Cloud for Apache Flink also supports read-only external tables to enable search with federated query execution on external databases.

  * KEY_SEARCH_AGG: Perform exact key lookups in external databases like JDBC, REST APIs, MongoDB, and Couchbase.
  * TEXT_SEARCH_AGG: Execute full-text searches in external databases like MongoDB, Couchbase, and Elasticsearch.
  * VECTOR_SEARCH_AGG: Run semantic similarity searches using vector embeddings in databases like MongoDB, Pinecone, Elasticsearch, and Couchbase.

For machine-language preprocessing utilities, see [ML Preprocessing Functions](ml-preprocessing-functions.html#flink-sql-ml-preprocessing-functions).

## ML_PREDICT¶

Run a remote AI/ML model for tasks like predicting outcomes, generating text, and classification.

Syntax

    ML_PREDICT(`model_name[$version_id]`, column);
    
    -- map settings are optional
    ML_PREDICT(`model_name[$version_id]`, column, map['async_enabled', [boolean], 'client_timeout', [int], 'max_parallelism', [int], 'retry_count', [int]]);

Description

The ML_PREDICT function performs predictions using pre-trained machine learning models.

The first argument to the ML_PREDICT table function is the model name. The other arguments are the columns used for prediction. They are defined in the model resource INPUT for AI models and may vary in length or type.

Before using ML_PREDICT, you must register the model by using the [CREATE MODEL](../statements/create-model.html#flink-sql-create-model) statement.

For more information, see [Run an AI Model](../../../ai/ai-model-inference.html#flink-sql-ai-model).

Configuration

You can control how calls to the remote model execute with these optional parameters.

  * `async_enabled`: Calls to remote models are asynchronous and don’t block. The default is `true`.
  * `client_timeout`: Time, in seconds, after which the request to the model endpoint times out. The default is 30 seconds.
  * `debug`: Return a detailed stack trace in the API response. The default is `false`. Confluent Cloud for Apache Flink implements data masking for error messages to remove any secrets or customer input, but the stack trace may contain the prompt itself or some part of the response string.
  * `retry_count`: Maximum number of times the remote model request is retried if the request to the model fails. The default is 3.
  * `max_parallelism`: Maximum number of parallel requests that the function can make. Can be used only when `async_enabled` is `true`. The default is 10.

Example

After you have registered the AI model by using the [CREATE MODEL](../statements/create-model.html#flink-sql-create-model) statement, run the model by using the ML_PREDICT function in a SQL query.

The following example runs a model named `embeddingmodel` on the data in a table named `text_stream`.

    SELECT id, text, embedding FROM text_stream, LATERAL TABLE(ML_PREDICT('embeddingmodel', text));

The following examples call the ML_PREDICT function with different configurations.

    -- Specify the timeout.
    SELECT * FROM `db1`.`tb1`, LATERAL TABLE(ML_PREDICT('md1', key, map['client_timeout', 60 ]));
    
    -- Specify all configuration parameters.
    SELECT * FROM `db1`.`tb1`, LATERAL TABLE(ML_PREDICT('md1', key, map['async_enabled', true, 'client_timeout', 60, 'max_parallelism', 20, 'retry_count', 5]));

## ML_DETECT_ANOMALIES¶

Identify outliers in a data stream.

Syntax

    ML_DETECT_ANOMALIES(
     data_column,
     timestamp_column,
     JSON_OBJECT('p' VALUE 1, 'q' VALUE 1, 'd' VALUE 1, 'minTrainingSize' VALUE 10));

Description

The ML_DETECT_ANOMALIES function uses an [ARIMA model](../../../ai/builtin-functions/detect-anomalies.html#flink-sql-detect-anomalies-arima-model) to identify outliers in time-series data.

Your data must include:

  * A timestamp column.
  * A target column representing some quantity of interest at each timestamp.

For more information, see [Detect Anomalies in Data](../../../ai/builtin-functions/detect-anomalies.html#flink-sql-detect-anomalies).

Parameters
    For anomaly detection parameters, see [ARIMA model parameters](../../../ai/builtin-functions/detect-anomalies.html#flink-sql-detect-anomalies-arima-model-parameters).
Example

    SELECT
        ML_DETECT_ANOMALIES(
         total_orderunits,
         summed_ts,
         JSON_OBJECT('p' VALUE 1, 'q' VALUE 1, 'd' VALUE 1, 'minTrainingSize' VALUE 10))
        OVER (
            ORDER BY summed_ts
            RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS anomalies
    FROM test_table;

## ML_EVALUATE¶

Aggregate a table and return model evaluation metrics.

Syntax

    ML_EVALUATE(`model_name`, label, col1, col2, ...) FROM 'eval_data_table';

### Description¶

The ML_EVALUATE function is a table aggregation function that takes an entire table and returns a single row of model evaluation metrics. If run on all versions of a model, the function returns one row for each model version. After comparing the metrics for different versions, you can update the default version for deployment with the model that has the best evaluation metrics.

Internally, the ML_EVALUATE function runs ML_PREDICT and processes the results.

Before using ML_EVALUATE, you must register the model by using the [CREATE MODEL](../statements/create-model.html#flink-sql-create-model) statement.

The first argument to the ML_EVALUATE table function is the model name. The second argument is the true label that the output of the model should be evaluated against. Its type depends on the model OUTPUT type and the model task. The other arguments are the columns used for prediction. They are defined in the model resource INPUT for AI models and may vary in length or type.

The return type of the ML_EVALUATE function is `Map<String, Double>` for all types of tasks. Each task type has different metrics keys in the map, depending on the task type.

### Metrics¶

The metric columns returned by ML_EVALUATE depend on the [task type](../statements/create-model.html#flink-sql-create-model-task-types) of the specified model.

#### Classification¶

Classification models choose a group to place their inputs in and return one of N possible values. A classification model that returns only 2 possible values is called a _binary classifier_. If it returns more than 2 values, it is referred to as _multi-class_.

Classification models return these metrics:

  * [Accuracy](https://en.wikipedia.org/wiki/Accuracy_and_precision): Total Fraction of correct predictions across all classes.
  * [F1 Score](https://en.wikipedia.org/wiki/F1_score): Harmonic mean of precision and recall.
  * [Precision](https://en.wikipedia.org/wiki/Precision_and_recall): (Class X Correctly Predicted) / (# of Class X Predicted)
  * [Recall](https://en.wikipedia.org/wiki/Precision_and_recall): (Class X Correctly Predicted) / (# of actual Class X)

#### Clustering¶

Clustering models group the model examples into K groups. Metrics are a measure of how compact the clusters are.

Clustering models return these metrics:

  * [Davies Bouldin Index](https://en.wikipedia.org/wiki/Davies%E2%80%93Bouldin_index): A measure of how separated clusters are and how compact they are.
  * Intra-Cluster Variance (Mean Squared Distance): Average Squared distance of each training point to the centroid of the cluster it was assigned to.
  * [Silhouette Score](https://en.wikipedia.org/wiki/Silhouette_\(clustering\)): Compares how similar each point is to its own cluster with how dissimilar it is to other clusters.

#### Embedding¶

Embedding models return these metrics:

  * [Mean Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity): A measure of how similar two vectors are.
  * [Mean Jaccard Similarity](https://en.wikipedia.org/wiki/Jaccard_index): A measure of how similar two sets are.
  * [Mean Euclidean Distance](https://en.wikipedia.org/wiki/Euclidean_distance): A measure of how similar two vectors are.

#### Regression¶

Regression models predict a continuous output variable based on one or more input features.

Regression models return these metrics:

  * [Mean Absolute Error](https://en.wikipedia.org/wiki/Mean_absolute_error): The average of the absolute differences between the predicted and actual values.
  * [Mean Squared Error](https://en.wikipedia.org/wiki/Mean_squared_error): The average of the squared differences between the predicted and actual values.

#### Text generation¶

Text generation models generate text based on a prompt. Text generation models return these metrics:

  * [Mean BLEU](https://en.wikipedia.org/wiki/BLEU): A measure of how similar two texts are.
  * [Mean ROUGE](https://en.wikipedia.org/wiki/ROUGE_\(metric\)): A measure of how similar two texts are.
  * [Mean Semantic Similarity](https://en.wikipedia.org/wiki/Semantic_similarity): A measure of how similar two texts are.

#### Example metrics¶

The following table shows example metrics for different task types.

Task type | Example metrics  
---|---  
Classification | {Accuracy=0.9999991465990892, Precision=0.9996998081063332, Recall=0.0013025368892873059, F1=0.0013025368892873059}  
Clustering | {Mean Davies-Bouldin Index=0.9999991465990892}  
Embedding | {Mean Cosine Similarity=0.9999991465990892, Mean Jaccard Similarity=0.9996998081063332, Mean Euclidean Distance=0.0013025368892873059}  
Regression | {MAE=0.9999991465990892, MSE=0.9996998081063332, RMSE=0.0013025368892873059, MAPE=0.0013025368892873059, R²=0.0043025368892873059}  
Text generation | {Mean BLEU=0.9999991465990892, Mean ROUGE=0.9996998081063332, Mean Semantic Similarity=0.0013025368892873059}  
  
### Example¶

After you have registered the AI model by using the [CREATE MODEL](../statements/create-model.html#flink-sql-create-model) statement, run the model by using the ML_EVALUATE function in a SQL query.

The following example statement registers a remote OpenAI model for a classification task.

    CREATE MODEL `my_remote_model`
    INPUT (f1 INT, f2 STRING)
    OUTPUT (output_label STRING)
    WITH(
      'task' = 'classification',
      'type' = 'remote',
      'provider' = 'openai',
      'openai.endpoint' = 'https://api.openai.com/v1/llm/v1/chat',
      'openai.api_key' = '<api-key>'
    );

The following statements show how to run the ML_EVALUATE function on various versions of `my_remote_model` using data in a table named `eval_data`.

    -- Model evaluation with all versions
    SELECT ML_EVALUATE(`my_remote_model$all`, label, f1, f2) FROM `eval_data`;
    
    -- Model evaluation with default version
    SELECT ML_EVALUATE(`my_remote_model`, label, f1, f2) FROM `eval_data`;
    
    -- Model evaluation with specific version 2
    SELECT ML_EVALUATE(`my_remote_model$2`, label, f1, f2) FROM `eval_data`;

## KEY_SEARCH_AGG¶

Run a key search over an external table.

Syntax

    KEY_SEARCH_AGG(<external_table>, DESCRIPTOR(<input_column>), <search_column>);

Description

Use the KEY_SEARCH_AGG function to run key searches over external databases in Confluent Cloud for Apache Flink.

The KEY_SEARCH_AGG function uses a combination of serialized table properties and configuration settings to interact with external databases. It’s designed to handle the deserialization of table properties and manage the runtime environment for executing search queries.

The output of KEY_SEARCH_AGG is an array with all rows in the external table that have a matching key in the search column.

<input_column> | Search result  
---|---  
<input_column_key> | array[row1<column1, column2…>, row2<column1, column2…>, …]  
  
## ML_FORECAST¶

Perform continuous forecasting on a table.

Syntax

    ML_FORECAST(
     data_column,
     timestamp_column,
     JSON_OBJECT('p' VALUE 1, 'q' VALUE 1, 'd' VALUE 1, 'minTrainingSize' VALUE 10));

Description

The ML_FORECAST function uses an [ARIMA model](../../../ai/builtin-functions/forecast.html#flink-sql-forecast-arima-model) to perform time-series forecasting.

Your data must include:

  * A timestamp column.
  * A target column representing some quantity of interest at each timestamp.

For more information, see [Forecast Data Trends](../../../ai/builtin-functions/forecast.html#flink-sql-forecast).

Parameters
    For forecasting parameters, see [ARIMA model parameters](../../../ai/builtin-functions/forecast.html#flink-sql-forecast-arima-model-parameters).
Example

    SELECT
        ML_FORECAST(
         total_orderunits,
         summed_ts,
         JSON_OBJECT('p' VALUE 1, 'q' VALUE 1, 'd' VALUE 1, 'minTrainingSize' VALUE 10))
        OVER (
            ORDER BY summed_ts
            RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS forecast
    FROM test_table;

## AI_COMPLETE¶

Invoke a large language model (LLM) to generate text completions, summaries, or answers.

Syntax

    AI_COMPLETE(model_name, input_prompt [, invocation_config]);

Description
    The AI_COMPLETE function provides a streamlined approach for generating text, taking a single string as input and returning a single string as output. This functionality enables you to leverage LLMs to produce text based on any given prompt.
Configuration

  * `model_name`: Name of the model entity to call to for prediction [STRING].
  * `input_prompt`: Input prompt to pass to the LLM for prediction [STRING].
  * `invocation_config[optional]`: Map to pass the configuration to manage function behavior, for example, `MAP['debug', true]`.

Example

The following example shows how to invoke an LLM to generate text completions.

    # Create an OpenAI connection.
    CREATE CONNECTION openai_connection
      WITH (
        'type' = 'openai',
        'endpoint' = 'https://api.openai.com/v1/chat/completions',
        'api-key' = '<api-key>'
      );
    
    CREATE MODEL description_extractor
      INPUT (input STRING)
      OUTPUT (output_json STRING)
    WITH(
        'provider' = 'openai',
        'openai.connection' = 'openai_connection',
        'openai.system_prompt' = 'Extract json from input free text',
        'task' = 'text_generation'
      );
    
    CREATE TABLE claims_with_structured_description(id INT, customer_id INT, output_json STRING);
    
    INSERT INTO claims_with_structured_description
      SELECT id, customer_id, output_json FROM claims_submitted, LATERAL TABLE(AI_COMPLETE('description_extractor', description));

## AI_EMBEDDING¶

Generate vector embeddings for text or other data using a registered embedding model.

    AI_EMBEDDING(model_name, input_text [, invocation_config]);

Description
    The AI_EMBEDDING function provides a straightforward interface, accepting a single string input and returning an array of floats as the embedding response. This functionality enables you to leverage large language models (LLMs) to generate embeddings for text efficiently.
Configuration

  * `model_name`: Name of the model entity to call to for embeddings [STRING].
  * `input_text`: Input text to pass to the LLM for embeddings [STRING].
  * `invocation_config[optional]`: Map to pass the configuration to manage function behavior, for example, `MAP['debug', true]`.

Example

The following example shows how to generate vector embeddings for text or other data using a registered embedding model.

    # Create an OpenAI connection.
    CREATE CONNECTION openai_embedding_connection
      WITH (
        'type' = 'openai',
        'endpoint' = 'https://api.openai.com/v1/embeddings',
        'api-key' = '<api-key>'
      );
    
      CREATE MODEL description_embedding
      INPUT (input STRING)
      OUTPUT (embeddings ARRAY<FLOAT>)
      WITH(
        'provider' = 'openai',
        'openai.connection' = 'openai_embedding_connection',
        'task' = 'embedding'
      );
    
      CREATE TABLE claims_embeddings(id INT, customer_id INT, embeddings ARRAY<FLOAT>);
    
      INSERT INTO claims_embeddings
        SELECT id, customer_id, embeddings FROM claims_submitted, LATERAL TABLE(AI_EMBEDDING('description_embedding', description));

## AI_TOOL_INVOKE¶

Invoke a registered tool, either externally by using an MCP server or locally by using a [UDF](../../concepts/user-defined-functions.html#flink-sql-udfs), as part of an AI workflow.

Syntax

    AI_TOOL_INVOKE(model_name, input_prompt, remote_udf_descriptor, mcp_tool_descriptor [, invocation_config]);

Description

The AI_TOOL_INVOKE function enables large language models (LLMs) to access various tools. The LLM decides which tools should be accessed, then the AI_TOOL_INVOKE function invokes the tools, gets the responses, and returns the responses to the LLM. The function returns a map that includes all the tools that were accessed, along with their responses and the status of the call, indicating whether it was a SUCCESS or FAILURE.

This function supports only SSE-based MCP servers.

The following models are supported:

  * Anthropic
  * AzureOpenAI
  * Gemini
  * OpenAI

Note

The AI_TOOL_INVOKE function is available for preview.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

Configuration

  * `model_name`: Name of the model entity to call [STRING].
  * `input_prompt`: Input prompt to pass to the LLM [STRING].
  * `remote_udf_descriptor`: Map to pass UDF names as key and function description as value [MAP<String, String>]. A maximum of 3 UDFs can be passed.
  * `mcp_tool_descriptor`: Map to pass MCP tool names as key and tool description as value [MAP<String, String>]. A maximum of 5 tools can be passed. This additional description is passed to the LLM as “Additional description”. If the MCP server already has a description, and if the server doesn’t have a description, `mcp_tool_descriptor` is added as the description. You can leave it empty, in which case no changes are made to the description provided by the server.
  * `invocation_config[optional]`: Map to pass the config to manage function behavior, for example, `MAP['debug', true, 'on_error', 'continue']`.

Example

The following example shows how to invoke a UDF and a registered external tool or API as part of an AI workflow.

When you create an MCP server connection, specify the following options:

  * `endpoint`: Defines the base URL for all non-SSE communications with the MCP server, including other http calls and general data exchange.
  * `sse_endpoint`: Specifies the explicit URL endpoint used to establish a Server-Sent Events (SSE) connection with the MCP server. If omitted, the client defaults to constructing the SSE endpoint by appending `/sse` to the domain specified in `endpoint`.

    # Create an MCP server connection.
    CREATE CONNECTION claims_mcp_server
      WITH (
        'type' = 'mcp_server',
        'endpoint' = 'https://mcp.deepwiki.com',
        'sse-endpoint' = 'https://mcp.deepwiki.com/sse',
        'api-key' = 'api_key'
      );

    -- Create a model that uses the MCP server connection.
    CREATE MODEL tool_invoker
      INPUT (input_message STRING)
      OUTPUT (tool_calls STRING)
      WITH(
        'provider' = 'openai',
        'openai.connection' = openai_connection,
        'openai.system_prompt' = 'Select the best tools to complete the task',
        'mcp.connection' = 'claims_mcp_server'
      );
    
    -- Create a table that contains the input prompts.
    CREATE TABLE claims_verified (
      id int,
      customer_id int
    );
    
    -- Run the AI_TOOL_INVOKE function.
    SELECT
      id,
      customer_id,
      AI_TOOL_INVOKE(
        'tool_invoker',
        customer_id,
        MAP['udf_1', 'udf_1 description', 'udf_2', 'udf_2 description'],
        MAP['tool_1', 'tool_1_description', 'tool_2', 'tool_2_description']
      ) AS verified_result
    FROM claims_verified;

## TEXT_SEARCH_AGG¶

Run a text search over an external table.

Syntax

    SELECT * FROM key_input,
      LATERAL TABLE(TEXT_SEARCH_AGG(<external_table>, DESCRIPTOR(<input_column>), <search_column>, <LIMIT>));

Description

Use the TEXT_SEARCH_AGG function to run full-text searches over external databases in Confluent Cloud for Apache Flink.

The TEXT_SEARCH_AGG function uses a combination of serialized table properties and configuration settings to interact with external databases. It’s designed to handle the deserialization of table properties and manage the runtime environment for executing search queries.

The output of TEXT_SEARCH_AGG is an array with all rows in the external table that have matching text in the search column.

<input_column> | Search result  
---|---  
<input_column_text> | array[row1<column1, column2…>, row2<column1, column2…>, …]  
  
## VECTOR_SEARCH_AGG¶

Run a vector search over an external table.

Syntax

    VECTOR_SEARCH_AGG(<external_table>, DESCRIPTOR(<input_column>), <embedding_column>, <LIMIT>);

Note

Vector Search is an Open Preview feature in Confluent Cloud.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

Description

Use the VECTOR_SEARCH_AGG function in conjunction with AI model inference to enable LLM-RAG use cases on Confluent Cloud.

The VECTOR_SEARCH_AGG function uses a combination of serialized table properties and configuration settings to interact with external databases. It’s designed to handle the deserialization of table properties and manage the runtime environment for executing search queries.

The output of VECTOR_SEARCH_AGG is an array with all rows in the external table that have a matching vector in the search column.

<input_column> | Search result  
---|---  
<input_column_vector> | array[row1<column1, column2…>, row2<column1, column2…>, …]  
Example

After you have registered the AI inference model by using the [CREATE MODEL](../statements/create-model.html#flink-sql-create-model) statement, you can start running vector searches. The following example assumes a vector search endpoint as shown in [Elasticsearch Quick Start Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started.html) and an API key as shown in [Kibana API Keys](https://www.elastic.co/guide/en/kibana/current/api-keys.html).

Once your vector search is created, the following example shows these steps:

  1. Create a connection resource with the Elasticsearch endpoint and API key.
  2. Create an Elasticsearch external table.
  3. Create an input vector table.
  4. Run the vector search.

  1. Run the following statement to create a connection resource named _elastic-connection_ that uses your AWS credentials.
         
         CREATE CONNECTION elastic-connection
           WITH (
             'type' = 'elastic',
             'endpoint' = '<ELASTICSEARCH_ENDPOINT>',
             'api-key' = '<ELASTIC_API_KEY>'
           );

  2. Run the following statements to creates the tables and run the vector search.
         
         -- Create the external table.
         CREATE TABLE elastic (
           vector array<FLOAT>,
           text string
         ) WITH (
           'connector' = 'elastic',
           'elastic.connection' = 'elastic-connection',
           'elastic.index' = 'vector-search-index'
         );
         
         -- Create the embedding output table.
         CREATE TABLE embedding_output (text string, embedding array<float>);
         
         -- Insert mock data.
         INSERT INTO embedding_output values ('hello world', ARRAY[1, 5, -20]);
         
         -- Run the vector search.
         SELECT * FROM embedding_output, LATERAL TABLE(VECTOR_SEARCH_AGG('elastic', DESCRIPTOR(embedding), embedding, 3));

For more examples, see [Vector Search with Confluent Cloud for Apache Flink](../../../ai/external-tables/vector-search.html#flink-sql-vector-search).

## Other built-in functions¶

  * [Aggregate Functions](aggregate-functions.html#flink-sql-aggregate-functions)
  * [Collection Functions](collection-functions.html#flink-sql-collection-functions)
  * [Comparison Functions](comparison-functions.html#flink-sql-comparison-functions)
  * [Conditional Functions](conditional-functions.html#flink-sql-conditional-functions)
  * [Datetime Functions](datetime-functions.html#flink-sql-datetime-functions)
  * [Hash Functions](hash-functions.html#flink-sql-hash-functions)
  * [JSON Functions](json-functions.html#flink-sql-json-functions)
  * [ML Preprocessing Functions](ml-preprocessing-functions.html#flink-sql-ml-preprocessing-functions)
  * Model Inference Functions
  * [Numeric Functions](numeric-functions.html#flink-sql-numeric-functions)
  * [String Functions](string-functions.html#flink-sql-string-functions)
  * [Table API Functions](table-api-functions.html#flink-table-api-functions)

