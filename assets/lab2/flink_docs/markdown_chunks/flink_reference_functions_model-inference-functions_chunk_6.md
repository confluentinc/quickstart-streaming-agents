---
document_id: flink_reference_functions_model-inference-functions_chunk_6
source_file: flink_reference_functions_model-inference-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html
title: AI Model Inference and Machine Learning Functions in Confluent Cloud for Apache Flink
chunk_index: 6
total_chunks: 8
---

FROM claims_submitted, LATERAL TABLE(AI_EMBEDDING('description_embedding', description));

## AI_TOOL_INVOKE¶

Invoke a registered tool, either externally by using an MCP server or locally by using a [UDF](../../concepts/user-defined-functions.html#flink-sql-udfs), as part of an AI workflow.

Syntax

    AI_TOOL_INVOKE(model_name, input_prompt, remote_udf_descriptor, mcp_tool_descriptor [, invocation_config]);

Description

The AI_TOOL_INVOKE function enables large language models (LLMs) to access various tools. The LLM decides which tools should be accessed, then the AI_TOOL_INVOKE function invokes the tools, gets the responses, and returns the responses to the LLM. The function returns a map that includes all the tools that were accessed, along with their responses and the status of the call, indicating whether it was a SUCCESS or FAILURE.

This function supports only SSE-based MCP servers.

The following models are supported:

* Anthropic
* AzureOpenAI
* Gemini
* OpenAI

Note

The AI_TOOL_INVOKE function is available for preview.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

Configuration

* `model_name`: Name of the model entity to call [STRING].
* `input_prompt`: Input prompt to pass to the LLM [STRING].
* `remote_udf_descriptor`: Map to pass UDF names as key and function description as value [MAP<String, String>]. A maximum of 3 UDFs can be passed.
* `mcp_tool_descriptor`: Map to pass MCP tool names as key and tool description as value [MAP<String, String>]. A maximum of 5 tools can be passed. This additional description is passed to the LLM as “Additional description”. If the MCP server already has a description, and if the server doesn’t have a description, `mcp_tool_descriptor` is added as the description. You can leave it empty, in which case no changes are made to the description provided by the server.
* `invocation_config[optional]`: Map to pass the config to manage function behavior, for example, `MAP['debug', true, 'on_error', 'continue']`.

Example

The following example shows how to invoke a UDF and a registered external tool or API as part of an AI workflow.

When you create an MCP server connection, specify the following options:

* `endpoint`: Defines the base URL for all non-SSE communications with the MCP server, including other http calls and general data exchange.
* `sse_endpoint`: Specifies the explicit URL endpoint used to establish a Server-Sent Events (SSE) connection with the MCP server. If omitted, the client defaults to constructing the SSE endpoint by appending `/sse` to the domain specified in `endpoint`.

# Create an MCP server connection

    CREATE CONNECTION claims_mcp_server
      WITH (
        'type' = 'mcp_server',
        'endpoint' = '<https://mcp.deepwiki.com>',
        'sse-endpoint' = '<https://mcp.deepwiki.com/sse>',
        'api-key' = 'api_key'
      );

    -- Create a model that uses the MCP server connection.
    CREATE MODEL tool_invoker
      INPUT (input_message STRING)
      OUTPUT (tool_calls STRING)
      WITH(
        'provider' = 'openai',
        'openai.connection' = openai_connection,
        'openai.system_prompt' = 'Select the best tools to complete the task',
        'mcp.connection' = 'claims_mcp_server'
      );

    -- Create a table that contains the input prompts.
    CREATE TABLE claims_verified (
      id int,
      customer_id int
    );

    -- Run the AI_TOOL_INVOKE function.
    SELECT
      id,
      customer_id,
      AI_TOOL_INVOKE(
        'tool_invoker',
        customer_id,
        MAP['udf_1', 'udf_1 description', 'udf_2', 'udf_2 description'],
        MAP['tool_1', 'tool_1_description', 'tool_2', 'tool_2_description']
      ) AS verified_result
    FROM claims_verified;
