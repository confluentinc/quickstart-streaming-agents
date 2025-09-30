---
document_id: flink_reference_functions_model-inference-functions_chunk_7
source_file: flink_reference_functions_model-inference-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html
title: AI Model Inference and Machine Learning Functions in Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 8
---

) AS verified_result FROM claims_verified;

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
