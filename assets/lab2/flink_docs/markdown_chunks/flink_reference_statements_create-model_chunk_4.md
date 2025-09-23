---
document_id: flink_reference_statements_create-model_chunk_4
source_file: flink_reference_statements_create-model.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-model.html
title: SQL CREATE MODEL Statement in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 7
---

MODEL `<model-name>$<version>` SET ('k1'='v1', 'k2'='v2');

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
