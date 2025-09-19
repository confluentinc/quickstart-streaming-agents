---
document_id: flink_reference_statements_create-model_chunk_5
source_file: flink_reference_statements_create-model.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-model.html
title: SQL CREATE MODEL Statement in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 7
---

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
