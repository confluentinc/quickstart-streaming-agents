---
document_id: flink_reference_functions_model-inference-functions_chunk_4
source_file: flink_reference_functions_model-inference-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html
title: AI Model Inference and Machine Learning Functions in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 8
---

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
