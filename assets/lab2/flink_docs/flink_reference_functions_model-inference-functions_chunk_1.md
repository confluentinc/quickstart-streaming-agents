---
document_id: flink_reference_functions_model-inference-functions_chunk_1
source_file: flink_reference_functions_model-inference-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html
title: AI Model Inference and Machine Learning Functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 8
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
