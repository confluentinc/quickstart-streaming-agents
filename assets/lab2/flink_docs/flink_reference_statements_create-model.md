---
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-model.html
title: SQL CREATE MODEL Statement in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'statements', 'create-model.html']
scraped_date: 2025-09-05T13:48:42.571757
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

## Model versioning¶

A model can have multiple versions. A version is an integer number that starts at 1. The default version for a new model is 1. Currently, the maximum number of supported versions is 10.

New versions are created by the CREATE MODEL statement for the same model name. A new version increments the current maximum version by 1.

To view the versions of a model, use the [DESCRIBE MODEL](describe.html#flink-sql-describe-model) statement.

Only model options are versioned, which that means input/output format and comments don’t change across versions. The statement fails if input format, output format, or comments change. For model options, model task changes are not permitted.

The following code example shows the result of running CREATE MODEL twice with the same model name.

    CREATE MODEL `my-model` ...
    
    -- Output
    `my-model` with version 1 created. Default version: 1
    
    CREATE MODEL `my-model` ...
    
    -- Output
    `my-model` with version 2 created. Default version: 1

By default, version 1 is the default version when a model is first created. As more versions are created by the CREATE MODEL statement, you can change the default version by using the ALTER MODEL statement.

The following example shows how to change the default version of an existing model.

    ALTER MODEL <model-name> SET ('default_version'='<version>');

You can access a specific version of a model in queries by using the `<model_name>$<model_version>` syntax. If no version is specified, the default version is used.

The following code examples show how to use a specific version of a model in a query.

    -- Use version 2 of the model.
    SELECT * FROM `my-table` LATERAL TABLE (ML_PREDICT('my-model$2', col1, col2));
    
    -- Use the default version of the model.
    SELECT * FROM `my-table` LATERAL TABLE (ML_PREDICT('my-model', col1, col2));

Use the `<model_name>$<model_version>` syntax to delete a specific version of a model:

    -- Delete a specific version of the model.
    DROP MODEL `<model-name>$<version>`;
    
    -- Delete all versions and the model.
    DROP MODEL `<model-name>$all`;

The maximum version number is the next default version. If all versions are dropped, the whole model is deleted.

To change the version of an existing model, use the [ALTER MODEL](alter-model.html#flink-sql-alter-model) statement. If no version is specified, the default version is changed.

    ALTER MODEL `<model-name>$<version>` SET ('k1'='v1', 'k2'='v2');

## WITH options¶

Specify the details of your AI inference model by using the WITH clause.

The following tables show the supported properties in the WITH clause.

Model Provider | Property  
---|---  
Common | 

  * {PROVIDER}.client_timeout
  * {PROVIDER}.connection
  * {PROVIDER}.input_format
  * {PROVIDER}.input_content_type
  * {PROVIDER}.output_format
  * {PROVIDER}.output_content_type
  * {PROVIDER}.PARAMS.*
  * {PROVIDER}.system_prompt

OpenAI | 

  * openai.input_format
  * openai.model_version

Azure OpenAI | 

  * azureopenai.input_format
  * azureopenai.model_version

Azure ML | 

  * azureml.input_format
  * azureml.deployment_name

Google AI | 

  * googleai.input_format

Sagemaker | 

  * sagemaker.custom_attributes
  * sagemaker.enable_explanations
  * sagemaker.inference_component_name
  * sagemaker.inference_id
  * sagemaker.input_content_type
  * sagemaker.output_content_type
  * sagemaker.target_container_hostname
  * sagemaker.target_model
  * sagemaker.target_variant

Vertex AI | 

  * vertexai.service_key
  * vertexai.input_format

### Connection resource¶

Secrets must be set by using a connection resource that you create by using the [CREATE CONNECTION](create-connection.html#flink-sql-create-connection) statement. The connection resource securely contains the provider endpoint and secrets like the API key.

For example, the following code example shows how to create a connection to OpenAI, named _openai-cli-connection_.

    CREATE CONNECTION openai-connection
      WITH (
        'type' = 'openai',
        'endpoint' = 'https://api.openai.com/v1/chat/completions',
        'api-key' = '<your-api-key>'
      );

Specify the connection by name in the {PROVIDER}.connection property of the WITH clause.

The environment, cloud, and region options in the [CREATE CONNECTION](create-connection.html#flink-sql-create-connection) statement must be the same as the compute pool which uses the connection.

The following code example shows how to refer to the connection named `openai-cli-connection` in the WITH clause:

    'openai.connection' = 'openai-cli-connection'

The maximum secret length is 4000 bytes, which is checked after the string is converted to bytes.

### Common properties¶

The following properties are common to all of the model providers.

#### {PROVIDER}.client_timeout¶

Set the request timeout to the client endpoint.

#### {PROVIDER}.connection¶

Set the credentials for connecting to a model provider. Create the connection resource by using the [CREATE CONNECTION](create-connection.html#flink-sql-create-connection) statement.

This property is required.

#### {PROVIDER}.input_format¶

Set the json, text, or binary input format used by the model. Each provider has a default value.

This property is optional.

For supported input formats, see Text generation and LLM model formats and Other formats.

#### {PROVIDER}.input_content_type¶

The HTTP content media type header to set when calling the model. The value is a [Media/MIME type](https://www.iana.org/assignments/media-types/media-types.xhtml). The default is chosen based on `input_format`.

Usually, this property is required only for Sagemaker and Bedrock models.

#### {PROVIDER}.output_format¶

Set the json, text, or binary output format used by the model. The default is chosen based on `input_format`.

This property is optional.

For supported output formats, see Text generation and LLM model formats and Other formats..

#### {PROVIDER}.output_content_type¶

The HTTP `Accept` media type header to set when calling the model. The value is a [Media/MIME type](https://www.iana.org/assignments/media-types/media-types.xhtml). The default is chosen based on `output_format`.

Usually, this property is required only for Sagemaker and Bedrock models.

#### {PROVIDER}.PARAMS.*¶

Provide parameters based on the `input_format`. The maximum number of parameters you can set is 32.

This property is optional.

For more information, see Parameters.

#### {PROVIDER}.system_prompt¶

A system prompt passed to an LLM model to give it general behavioral instructions. The value is a string.

Not all models support a system prompt.

This property is optional.

#### task¶

Specify the kind of analysis to perform.

Supported values are:

  * “classification”
  * “clustering”
  * “embedding”
  * “regression”
  * “text_generation”

This property is required, but it applies only when using the [ML_EVALUATE](../functions/model-inference-functions.html#flink-sql-ml-evaluate-function) function.

### OpenAI properties¶

#### openai.input_format¶

Set the input format used by the model. The default is `OPENAI-CHAT`.

This property is optional.

#### openai.model_version¶

Set the version string of the requested model. The default is `gpt-3.5-turbo`.

This property is optional.

### Azure OpenAI properties¶

Properties for OpenAI models deployed in Azure AI Studio. Azure OpenAI accepts all of the OpenAI parameters, but with a different endpoint.

#### azureopenai.input_format¶

Set the input format used by the model. The default is `OPENAI-CHAT`.

This property is optional.

#### azureopenai.model_version¶

Set the version string of the requested model. The default is `gpt-3.5-turbo`.

This property is optional.

### Azure ML properties¶

Properties for both Azure Machine Learning and LLM models from Azure AI Studio can use this provider.

#### azureml.input_format¶

Set the input format used by the model. The default is `AZUREML-PANDAS-DATAFRAME`.

For AI Studio LLMs, `OPENAI-CHAT` is usually the correct format, even for non-OpenAI models.

This property is optional.

#### azureml.deployment_name¶

Set the model name.

### Bedrock properties¶

The default `input_format` for Bedrock is determined automatically based on the model endpoint, or `AMAZON-TITAN-TEXT` if there is no match. If necessary, change it to match the model for your endpoint.

### Google AI properties¶

#### googleai.input_format¶

Set the input format used by the model. The default is `GEMINI-GENERATE`.

This property is optional.

### Sagemaker properties¶

#### sagemaker.custom_attributes¶

Set a model-dependent value that is passed through to Sagemaker in the header of the same name.

This property is optional.

#### sagemaker.enable_explanations¶

Enable writing explanations, if your model supports them. Passed through to Sagemaker in the header of the same name.

If your model supports writing explanations, they should be disabled, because Confluent Cloud for Apache Flink currently doesn’t support reading them.

Don’t set `enable_explanations` if the model doesn’t support explanations, because this causes Sagemaker to return an error.

This property is optional.

#### sagemaker.inference_component_name¶

Specify which inference component to use in the endpoint. Passed through to Sagemaker in the header of the same name.

This property is optional.

#### sagemaker.inference_id¶

Set an ID that is passed through to Sagemaker in the header of the same name. Used for tracking request origins.

This property is optional.

#### sagemaker.input_content_type¶

The HTTP content media type header to set when calling the model.

Setting this property overrides the `Content-type` header for the model request. Many Sagemaker models use this header to determine their behavior, but set it only if choosing an appropriate `input_format` is not sufficient.

This property is optional.

#### sagemaker.output_content_type¶

The HTTP `Accept` media type header to set when calling the model.

Setting this property overrides the `Accept` header for the model request. Some Sagemaker models use this header to determine their outputs, but set it only if choosing an appropriate `output_format` is not sufficient.

This property is optional.

#### sagemaker.target_container_hostname¶

Allows calling a specific container when the endpoint has multiple containers. Passed through to Sagemaker in the header of the same name.

This property is optional.

#### sagemaker.target_model¶

Enables calling a specific model from multiple models deployed to the same endpoint. Passed through to Sagemaker in the header of the same name.

This property is optional.

#### sagemaker.target_variant¶

Enables calling a specific version of the model from multiple deployed variants. Passed through to Sagemaker in the header of the same name.

This property is optional.

### Vertex AI properties¶

#### vertexai.service_key¶

Set the Service Account Key of a service account with permission to call the inference endpoint. This value is a secret.

This property is required.

#### vertexai.input_format¶

Set the input format used by the model. The default is `TF-SERVING`.

Defaults to `GEMINI-GENERATE` if the endpoint is for a published Gemini model.

This property is optional.

## Supported input/output formats¶

The following input/output formats for text generation and LLM models are supported.

AI-21-COMPLETE | AMAZON-TITAN-EMBED | AMAZON-TITAN-TEXT  
---|---|---  
ANTHROPIC-COMPLETIONS | ANTHROPIC-MESSAGES | AZURE-EMBED  
BEDROCK-LLAMA | COHERE-CHAT | COHERE-EMBED  
COHERE-GENERATE | GEMINI-GENERATE | GEMINI-CHAT  
MISTRAL-CHAT | MISTRAL-COMPLETIONS | OPENAI-CHAT  
OPENAI-EMBED | VERTEX-EMBED |   
  
The following additional input/output formats are supported.

AZUREML-PANDAS-DATAFRAME | AZUREML-TENSOR | BINARY  
---|---|---  
CSV | JSON | JSON-ARRAY  
JSON:wrapper | KSERVE-V1 | KSERVE-V2  
MLFLOW-TENSOR | PANDAS-DATAFRAME | TEXT  
TF-SERVING | TF-SERVING-COLUMN | TRITON  
VERTEXAI-PYTORCH |  |   
  
### Parameters¶

The text generation and LLM formats support some or all of the following parameters.

#### {PROVIDER}.PARAMS.temperature¶

Controls the randomness or “creativity” of the output. Typical values are between 0.0 and 1.0.

This parameter is model-dependent. Its type is `Float`.

#### {PROVIDER}.PARAMS.top_p¶

The probability cutoff for token selection. Usually, either temperature or top_p are specified, but not both.

This parameter is model-dependent. Its type is `Float`.

#### {PROVIDER}.PARAMS.top_k¶

The number of possible tokens to sample from at each step.

This parameter is model-dependent. Its type is `Float`.

#### {PROVIDER}.PARAMS.stop¶

A CSV list of strings to pass as stop sequences to the model.

#### {PROVIDER}.PARAMS.max_tokens¶

The maximum number of tokens for the model to return.

Its type is `Int`.

### Text generation and LLM model formats¶

The following formats are intended for text generation models and LLMs. They require that the model has a single STRING input and a single STRING output.

#### AI-21-COMPLETE¶

This format is for models using the [AI21 Labs J2 Complete API](https://docs.ai21.com/reference/j2-complete-ref), including the AI21 Labs Foundation models on AWS Bedrock.

This format does not support the top_k parameter.

#### AMAZON-TITAN-EMBED¶

This format is for [Amazon Titan Text Embedding](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-embed-text.html) models.

#### AMAZON-TITAN-TEXT¶

The format is for [Amazon’s Titan Text models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-text.html). This is the default format for the AWS Bedrock provider.

This format does not support the top_k parameter.

#### ANTHROPIC-COMPLETIONS¶

This format is for models using the [Anthropic Claude Text Completions API](https://docs.anthropic.com/claude/reference/complete_post), including some Anthropic models on AWS Bedrock.

#### ANTHROPIC-MESSAGES¶

This format is for models using the [Anthropic Claude Messages API](https://docs.anthropic.com/claude/reference/messages_post), including some Anthropic models on AWS Bedrock.

Some Anthropic models accept both this and the Completions API format.

#### AZURE-EMBED¶

The embedding format used by other foundation models on Azure. This format is the same as OPENAI-EMBED.

#### BEDROCK-LLAMA¶

The format used by [Llama models on AWS Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-meta.html).

This format does not support the top_k or stop parameters.

#### COHERE-CHAT¶

The [Cohere Chat API](https://docs.cohere.com/reference/chat) format.

#### COHERE-EMBED¶

Cohere’s [Embedding API](https://docs.cohere.com/reference/embed) format.

#### COHERE-GENERATE¶

The legacy [Cohere Chat API](https://docs.cohere.com/reference/generate) format.

This format is used by AWS Bedrock Cohere Command models.

#### GEMINI-GENERATE¶

The [Google Gemini API](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini#gemini-1.0-pro) format.

This is the default format for the Google AI provider, but you can also use it with Gemini models on the Google Vertex AI.

#### GEMINI-CHAT¶

Same as the GEMINI-GENERATE format.

#### MISTRAL-CHAT¶

The standard [Mistral API](https://docs.mistral.ai/api/) format.

#### MISTRAL-COMPLETIONS¶

The legacy [Mistral Completions API](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-mistral.html) format used by AWS Bedrock.

#### OPENAI-CHAT¶

The [OpenAI Chat API](https://platform.openai.com/docs/api-reference/chat) format. This is the default for the OpenAI and Azure OpenAI providers. It is also generally used by most non-OpenAI LLM models deployed in Azure AI Studio using the Azure ML provider.

#### OPENAI-EMBED¶

The [OpenAI Embedding model](https://platform.openai.com/docs/guides/embeddings) format.

#### VERTEX-EMBED¶

The [Embedding format](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings) for Vertex AI Gemini models.

### Other formats¶

The following formats are intended for predictive models running on providers like Sagemaker, Vertex AI, and Azure ML. Usually, these models are used for tasks like classification, regression, and clustering.

Currently, none of these formats support PARAMS.

Unless specified, each input format defaults to the associated output format with the same name.

#### AZUREML-PANDAS-DATAFRAME¶

[Azure ML’s version](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-mlflow-models#payload-example-for-a-json-serialized-pandas-dataframe-in-the-split-orientation) of the Pandas Dataframe Split format. The only difference is that this version has “input_data” as the top-level field, instead of “dataframe_split”.

This is the default format for Azure ML models.

The output format defaults to JSON-ARRAY.

#### AZUREML-TENSOR¶

[Azure ML’s version](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-mlflow-models#payload-example-for-a-named-tensor-input) of named input tensors. Equivalent to the “JSON:input_data” input format. the output format defaults to “JSON:outputs”.

#### BINARY¶

Raw binary inputs, serialized in little-endian byte order. This input format accepts multiple input columns, which are packed in order.

#### CSV¶

Comma separated text. This is the default format for Sagemaker models, but Sagemaker models vary widely, and most models must choose a different format.

#### JSON¶

The inputs are formatted as a JSON object, with field names equal to the column names of the model input schema.

The JSON format supports user-defined parameters. If you specify `'{provider}.params.some_key'='value'` in the WITH options, the key and value are used in the JSON input as `{"some_key": "value"}`.

Example:

    {
      "column1": "String Data",
      "column2": [1,2,3,4]
    }

#### JSON-ARRAY¶

The inputs are formatted as a JSON array, including [] brackets, but without the {} braces of a top-level JSON object. Column names are not included in the format.

If the model takes a single input array column, it will be output as the top-level array. Models with multiple inputs have their arrays nested in JSON fashion.

This format is usually appropriate for models that expect Numpy arrays.

Example:

    [1,2,3,"String Data"]

#### JSON:wrapper¶

Similar to the default JSON behavior, but all fields are wrapped in a named top-level object. The wrapper may be any valid JSON string.

Example:

    {
      "wrapper": {
        "column1": "String Data",
        "column2: [1,2,3,4]
      }
    }

#### KSERVE-V1¶

Same as the TF-SERVING format.

#### KSERVE-V2¶

Same as the TRITON format.

#### MLFLOW-TENSOR¶

The format used by some MLFlow models. It is the same format as TF-SERVING-COLUMN.

#### PANDAS-DATAFRAME¶

The [Pandas Dataframe Split](https://mlflow.org/docs/latest/deployment/deploy-model-locally.html#json-input) format used by most MLFlow models.

The output format defaults to JSON-ARRAY.

#### TEXT¶

Model input values formatted as raw text. Use newlines to separate multiple inputs.

#### TF-SERVING¶

The [Tensorflow Serving Row](https://www.tensorflow.org/tfx/serving/api_rest#request_format_2) format. This is the default format for Vertex AI models. It is generally the correct format to use for most predictive models trained in Vertex AI.

#### TF-SERVING-COLUMN¶

The [TensorFlow Serving Column](https://www.tensorflow.org/tfx/serving/api_rest#specifying_input_tensors_in_column_format) format. It is exactly equivalent to “JSON:inputs”. The output format defaults to “JSON:outputs”.

#### TRITON¶

The [Triton/KServeV2](https://github.com/kserve/kserve/blob/master/docs/predict-api/v2/required_api.md) format used by NVidia Triton Inference Servers.

When possible, this format serializes data in the protocol’s mixed json+binary format. Note that some Tensor datatypes, like 16-bit floats, do not have an exact equivalent in Flink SQL, but they are converted, when possible.

#### VERTEXAI-PYTORCH¶

[Vertex AI’s format for PyTorch models](https://cloud.google.com/vertex-ai/docs/predictions/get-online-predictions#request-body-details). This format is the TF-SERVING format with an extra wrapper around the data.

The output format defaults to TF-SERVING.

