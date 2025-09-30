---
document_id: flink_reference_statements_create-model_chunk_2
source_file: flink_reference_statements_create-model.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-model.html
title: SQL CREATE MODEL Statement in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 7
---

when using the [ML_EVALUATE](../functions/model-inference-functions.html#flink-sql-ml-evaluate-function) function.

## Examples¶

The following code example shows how to run an AI model. The model must be created with the model provider and registered by using the CREATE MODEL statement with `<model-name>`.

    SELECT * FROM my_table, LATERAL TABLE(ML_PREDICT('<model-name>', column1, column2));

All of the CREATE MODEL statements require a connection resource that you create by using the [CREATE CONNECTION](create-connection.html#flink-sql-create-connection) statement. For example, the following code example shows how to create a connection for AWS Bedrock.

    # Example command to create a connection for AWS Bedrock.
    CREATE CONNECTION bedrock-cli-connection
      WITH (
        'type' = 'bedrock',
        'endpoint' = 'https://bedrock-runtime.us-west-2.amazonaws.com/model/amazon.titan-embed-text-v1/invoke',
        'aws-access-key' = '<aws-access-key>',
        'aws-secret-key' = '<aws-secret-key>',
        'aws-session-token' = '<aws-session-token>'
      );

### Classification task¶

The following example shows how to create an OpenAI classification model. For more information, see [Sentiment analysis with OpenAI LLM](../../../ai/ai-model-inference.html#flink-sql-ai-model-sentiment-analysis).

    CREATE MODEL sentimentmodel
    INPUT(text STRING)
    OUTPUT(sentiment STRING)
    COMMENT 'sentiment analysis model'
    WITH (
      'provider' = 'openai',
      'task' = 'classification',
      'openai.connection' = '<cli-connection>',
      'openai.model_version' = 'gpt-3.5-turbo',
      'openai.system_prompt' = 'Analyze the sentiment of the text and return only POSITIVE, NEGATIVE, or NEUTRAL.'
    );

### Clustering task¶

The following example shows how to create an Azure ML clustering model. It requires that a K-Means model has been trained and deployed on Azure. Replace `<ENDPOINT>` and `<REGION>` with your values.

    CREATE MODEL clusteringmodel
    INPUT (vectors ARRAY<FLOAT>, other_feature INT, other_feature2 STRING)
    OUTPUT (cluster_num INT)
    WITH (
      'task' = 'clustering',
      'provider' = 'azureml',
      'azureml.connection' = '<cli-connection>'
    );

### Embedding task¶

The following example shows how to create an AWS Bedrock text embedding model. Replace `<REGION>` with your value. For more information, see [Text embedding with AWS Bedrock and Azure OpenAI](../../../ai/ai-model-inference.html#flink-sql-ai-model-text-embedding).

    CREATE MODEL embeddingmodel
    INPUT (text STRING)
    OUTPUT (embedding ARRAY<FLOAT>)
    WITH (
      'task' = 'embedding',
      'provider' = 'bedrock',
      'bedrock.connection' = '<cli-connection>'
    );

### Text generation task¶

The following example shows how to create an OpenAI text generation task for translating from English to Spanish.

    CREATE MODEL translatemodel
    INPUT(english STRING)
    OUTPUT(spanish STRING)
    COMMENT 'spanish translation model'
    WITH (
      'provider' = 'openai',
      'task' = 'text_generation',
      'openai.connection' = '<cli-connection>',
      'openai.model_version' = 'gpt-3.5-turbo',
      'openai.system_prompt' = 'Translate to spanish'
    );

For more examples, see [Run an AI Model](../../../ai/ai-model-inference.html#flink-sql-ai-model).
