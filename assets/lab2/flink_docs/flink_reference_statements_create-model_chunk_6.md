---
document_id: flink_reference_statements_create-model_chunk_6
source_file: flink_reference_statements_create-model.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-model.html
title: SQL CREATE MODEL Statement in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 7
---

model. This property is optional.

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
