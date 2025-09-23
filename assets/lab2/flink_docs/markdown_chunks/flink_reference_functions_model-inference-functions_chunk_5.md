---
document_id: flink_reference_functions_model-inference-functions_chunk_5
source_file: flink_reference_functions_model-inference-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html
title: AI Model Inference and Machine Learning Functions in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 8
---

FROM claims_submitted, LATERAL TABLE(AI_COMPLETE('description_extractor', description));

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
