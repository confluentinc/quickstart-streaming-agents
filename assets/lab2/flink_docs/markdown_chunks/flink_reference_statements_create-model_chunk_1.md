---
document_id: flink_reference_statements_create-model_chunk_1
source_file: flink_reference_statements_create-model.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-model.html
title: SQL CREATE MODEL Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 7
---

# CREATE MODEL Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables real-time inference and prediction with AI and ML models. The Flink SQL interface is available in Cloud Console and the Flink SQL shell.

Get started using AI models with [Run an AI Model](../../../ai/ai-model-inference.html#flink-sql-ai-model).

The following providers are supported:

  * AWS Bedrock
  * AWS Sagemaker
  * Azure Machine Learning (Azure ML)
  * Azure OpenAI
  * Google AI
  * OpenAI
  * Vertex AI

## Syntax¶

    CREATE MODEL [IF NOT EXISTS] [[catalogname].[database_name]].model_name
      [INPUT (input_column_list)]
      [OUTPUT (output_column_list)]
      [COMMENT model_comment]
      WITH(model_option_list)

## Description¶

Create a new AI model.

If a model with the same name exists already, a new version of the model is created. For more information, see version.

If the IF NOT EXISTS option is specified and a model with the same name exists already, the statement is ignored.

To view the currently registered models, use the [SHOW MODELS](show.html#flink-sql-show-models) statement.

To view the WITH options that were used to create the model, run the [SHOW CREATE MODEL](show.html#flink-sql-show-create-model) statement.

To view the versions, inputs, and outputs of the model, run the [Models](describe.html#flink-sql-describe-model) statement.

To change the name or options of an existing model, use the [ALTER MODEL](alter-model.html#flink-sql-alter-model) statement.

To delete a model from the current environment, use the [DROP MODEL](drop-model.html#flink-sql-drop-model) statement.

Tip

If you get a 429 error when you run a CREATE MODEL statement, the most likely cause is rate limiting by the model provider. Some providers, like Azure OpenAI, support increasing the default limit of tokens per minute. Increasing this limit to match your throughput may fix 429 errors.

### Task types¶

Confluent Cloud for Apache Flink supports these types of analysis for AI model inference:

  * **Classification:** Categorize input data into predefined classes or labels. This task is used in applications like spam detection, where emails are classified as “spam” or “not spam”, and image recognition.
  * **Clustering:** Group a set of objects so that objects in the same group, called a “cluster”, are more similar to each other than to those in other groups. This task is a form of unsupervised learning, because it doesn’t rely on predefined categories. Applications include customer segmentation in marketing and gene sequence analysis in biology.
  * **Embedding:** Transform high-dimensional data into lower-dimensional vectors while preserving the relative distances between data points. This is crucial for tasks like natural language processing (NLP), where words or sentences are converted into vectors, enabling models to understand semantic similarities. Embeddings are used in recommendation systems, search engines, and more.
  * **Regression:** Regression models predict a continuous output variable based on one or more input features. This task is used in scenarios like predicting house prices based on features like size, location, and number of bedrooms, or forecasting stock prices. Regression analysis helps in understanding the relationships between variables and forecasting.
  * **Text generation:** Generate human-like text based on input data. Applications include chatbots, content creation, and language translation.

When you register an AI or ML model, you specify the task type by using the task property. `task` is a required property, but it applies only when using the [ML_EVALUATE](../functions/model-inference-functions.html#flink-sql-ml-evaluate-function) function.
