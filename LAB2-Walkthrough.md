# Lab2: Vector Search / RAG Walkthrough

In this lab, we'll create a Retrieval-Augmented Generation (RAG) pipeline using Confluent Cloud for Apache Flink's vector search capabilities. The pipeline processes documents, creates embeddings, and enables semantic search to power intelligent responses through retrieval of relevant context.

<img src="./assets/lab2/00_lab2_architecture.png" alt="Lab2 Architecture Diagram"/>

## Prerequisites

- **LLM Access:** AWS Bedrock API keys **OR** Azure OpenAI endpoint + API key
  - **Easy key creation:** Run `uv run workshop-keys create` to quickly generate ready-to-use credentials
- **MongoDB vector database:** Pre-configured and managed for you - no setup required.

> [!WARNING]
>
> **AWS Bedrock Users:** You must request access to Claude Sonnet 4.5 by filling out an Anthropic use case form. Visit the [Model Catalog](https://console.aws.amazon.com/bedrock/home#/model-catalog), select Claude Sonnet 4.5, open it in the Playground, and send a message - the form will appear automatically.

## Deployment

Use the setup script and select "Lab2" when prompted to automatically deploy Lab2 infrastructure:

```bash
uv run deploy
```

The deployment script will:
- Prompt you to choose AWS or Azure for your LLM provider
- Ask for your LLM API credentials (Bedrock keys or Azure OpenAI endpoint/key)
- Automatically configure MongoDB connection (pre-configured, no setup needed!)
- Deploy the complete RAG pipeline:
- **6 Flink tables** for the document-to-response flow (intentionally in alphabetical order from beginning to end of pipeline, to keep things tidy!):
  - `documents`
  - `documents_embed`
  - `documents_vectordb_lab2`
  - `queries`
  - `queries_embed`
  - `search_results`
  - `search_results_response`

- **LLM models** for embeddings and text generation: `llm_textgen_model` and `llm_embedding_model`
- **MongoDB sink connector** to stream embeddings from `documents_embed` to Atlas

## Using the RAG Pipeline

### Load Confluent Flink Documentation

The lab uses real Confluent Flink documentation as the knowledge base. These pre-populated documents have been:

1. **Embedded** using an LLM embedding model
2. **Stored** in a MongoDB Atlas cluster with vector search index
3. **Made searchable** for semantic queries

### Query the RAG System

```bash
uv run publish_queries # starts interactive mode (recommended), or:
uv run publish_queries "How do window functions work in Flink SQL?"
```

Your queries land in the `queries` topic, which immediately feeds into `queries_embed`, where we instantly create and save embeddings for each query.

The vector search results can be found in the `search_results` table, and the RAG (retrieval-augmented generation) results can be found in the  `search_results_response` table. They contain:

- Source document snippets with similarity scores comparing query to document text
- Document ID
- AI-generated RAG response to your question based on retrieved documents from the vector store / knowledge base

### View Results in Confluent Cloud

Monitor the pipeline in Confluent Cloud SQL workspace:

```sql
-- Check data flow through pipeline
SELECT
  (SELECT COUNT(*) FROM queries) AS queries_count,                                    -- Your questions
  (SELECT COUNT(*) FROM queries_embed) AS queries_embed_count,                        -- Your questions in vector form
  (SELECT COUNT(*) FROM search_results) AS search_results_count,                      -- Vector search results
  (SELECT COUNT(*) FROM search_results_response) AS search_results_response_count;    -- RAG based on vector search results

-- See vector search results
SELECT * FROM search_results LIMIT 5;

-- View final RAG responses
SELECT query, response FROM search_results_response LIMIT 5;
```

## Troubleshooting

<details>
<summary>Click to expand</summary>

### Common Issues

1. **Pipeline not processing**: Wait 30-60 seconds after publishing documents for initial processing
2. **No query responses**: Check that LLM models are deployed. [Run test query #1](./LAB1-Walkthrough.md#test-query-1-base-llm-model) to verify `llm_textgen_model` is working
3. **Empty results**: Verify MongoDB sink connector status in Confluent Cloud UI
4. **Deployment failed**: Ensure you have valid LLM credentials (Bedrock keys or Azure OpenAI endpoint/key)

</details>

## Navigation

- **← Back to Overview**: [Main README](./README.md)
- **← Previous Lab**: [Lab1: Tool Calling Agent](./LAB1-Walkthrough.md)
- **→ Next Lab**: [Lab3: Agentic Fleet Management](./LAB3-Walkthrough.md)
- **🧹 Cleanup**: [Cleanup Instructions](./README.md#cleanup)
