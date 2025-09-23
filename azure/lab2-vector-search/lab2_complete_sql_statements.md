# Lab2 Vector Search - Complete SQL Statements

## Overview

This document contains all the corrected and optimized SQL statements for implementing the complete RAG pipeline in Lab2. These statements should be executed in order after Terraform deployment.

---

## Prerequisites

- Terraform has been applied successfully
- MongoDB connection is established
- LLM models (`llm_embedding_model` and `llm_textgen_model`) are available from core infrastructure

---

## Step 1: Populate Embedding Tables

### 1.1 Populate documents_embed with Optimized Chunking

```sql
-- IMPROVED: Optimized chunking strategy for better embeddings
-- - 5000 chars max for excellent context preservation (~800-1200 tokens)
-- - 200 char overlap for continuity between chunks
-- - Splits on # or ## headings for logical boundaries
-- - Expected output: 500-1500 embeddings for demo corpus

INSERT INTO documents_embed
WITH chunked_texts AS (
  SELECT
    document_id,
    document_text,
    chunk
  FROM documents
  CROSS JOIN UNNEST(
    ML_CHARACTER_TEXT_SPLITTER(
      document_text, 5000, 200, '"^#{1,2}\\s"', true, true, true, 'START'
    )
  ) AS t(chunk)
)
SELECT
  document_id,
  chunk,
  embedding AS embedding
FROM chunked_texts,
LATERAL TABLE(
  ML_PREDICT('llm_embedding_model', chunk)
);
```

**Text Splitter Parameters Explained:**

- `5000` - Max chunk size (characters) for excellent context preservation
- `200` - Overlap size ensuring continuity between chunks (4% overlap)
- `'"^#{1,2}\\s"'` - Regex pattern matching # or ## headings only
- `true, true, true, 'START'` - Enable regex, case-sensitive, trim whitespace, start mode

### 1.2 Populate queries_embed

```sql
-- Embed all incoming queries for vector search
INSERT INTO queries_embed
SELECT
  query,
  embedding
FROM queries,
LATERAL TABLE(ML_PREDICT('llm_embedding_model', query));
```

---

## Step 2: Create MongoDB Vector Store External Table

```sql
-- External table connecting to MongoDB vector database
-- This table references the MongoDB collection populated by the sink connector
CREATE TABLE documents_vectordb (
  document_id STRING,
  chunk STRING,
  embedding ARRAY<FLOAT>
) WITH (
  'connector' = 'mongodb',
  'mongodb.connection' = 'mongodb-connection',
  'mongodb.database' = 'vector_search',
  'mongodb.collection' = 'documents',
  'mongodb.index' = 'vector_index',
  'mongodb.embedding_column' = 'embedding',
  'mongodb.numCandidates' = '500'
);
```

---

## Step 3: Create Vector Search Results Table

### Option A: Fixed Column Structure (Recommended)

```sql
-- Creates search_results table with fixed columns for top 3 results
-- Includes similarity scores for analysis
CREATE TABLE search_results AS
SELECT
  qe.query,
  vs.search_results[1].document_id AS document_id_1,
  vs.search_results[1].chunk AS chunk_1,
  vs.search_results[1].score AS score_1,
  vs.search_results[2].document_id AS document_id_2,
  vs.search_results[2].chunk AS chunk_2,
  vs.search_results[2].score AS score_2,
  vs.search_results[3].document_id AS document_id_3,
  vs.search_results[3].chunk AS chunk_3,
  vs.search_results[3].score AS score_3
FROM queries_embed AS qe,
LATERAL TABLE(VECTOR_SEARCH_AGG(
    documents_vectordb,
    DESCRIPTOR(embedding),
    qe.embedding,
    3
)) AS vs;
```

## Step 4: Create RAG Response Table

### 4.1 Generic RAG Response

```sql
-- Generic RAG response table with configurable prompt
-- Includes all search results and similarity scores
CREATE TABLE search_results_response AS
SELECT
    sr.query,
    sr.document_id_1,
    sr.chunk_1,
    sr.score_1,
    sr.document_id_2,
    sr.chunk_2,
    sr.score_2,
    sr.document_id_3,
    sr.chunk_3,
    sr.score_3,
    pred.response
FROM search_results sr,
LATERAL TABLE(
    ml_predict(
        'llm_textgen_model',
        CONCAT(
            'Based on the following search results, provide a helpful and comprehensive response to the user query based upon the relevant retrieved documents. Cite the exact parts of the retrieved documents whenever possible.

USER QUERY: ', sr.query, '

SEARCH RESULTS:

Document 1 (Similarity Score: ', CAST(sr.score_1 AS STRING), '):
Source: ', sr.document_id_1, '
Content: ', sr.chunk_1, '

Document 2 (Similarity Score: ', CAST(sr.score_2 AS STRING), '):
Source: ', sr.document_id_2, '
Content: ', sr.chunk_2, '

Document 3 (Similarity Score: ', CAST(sr.score_3 AS STRING), '):
Source: ', sr.document_id_3, '
Content: ', sr.chunk_3, '

INSTRUCTIONS:
- Synthesize information from the most relevant documents above
- Provide specific, actionable guidance when possible
- Reference document sources in your response
- If the search results don''t contain relevant information, say so clearly

RESPONSE:'
        )
    )
) AS pred;
```

### Execution Order

Execute these statements in the following order:

1. **Step 1.1**: Populate `documents_embed` (streams to MongoDB automatically)
2. **Step 1.2**: Populate `queries_embed`
3. **Step 2**: Create `documents_vectordb` external table
4. **Step 3**: Create `search_results` table
5. **Step 4**: Create `search_results_response` table

---

## Testing Queries

After creating all tables, test the pipeline with these queries:

### Insert Sample Queries

```sql
-- Insert test queries to verify the pipeline
INSERT INTO queries VALUES ('How do I create a Flink table?');
INSERT INTO queries VALUES ('What are the supported data types in Confluent Flink?');
INSERT INTO queries VALUES ('How do I join two streams in Flink SQL?');
```

### Verify Results

```sql
-- Check embedding population
SELECT COUNT(*) as total_chunks FROM documents_embed;

-- Check vector search results
SELECT query, score_1, score_2, score_3 FROM search_results LIMIT 5;

-- Check RAG responses
SELECT query, LEFT(response, 200) as response_preview FROM search_results_response LIMIT 5;
```

---

## Performance Considerations

- **Chunking Strategy**: 5000-character chunks provide excellent context while maintaining reasonable performance
- **MongoDB Index**: Ensure your MongoDB vector index is properly configured for the expected corpus size
- **Compute Resources**: Vector search and LLM inference require adequate Flink compute pool resources
- **Monitoring**: Monitor CFU usage and query performance as data volume grows

---

## Troubleshooting

### Common Issues

1. **MongoDB Connection Timeout**: Verify MongoDB connection parameters and network access
2. **Vector Search Errors**: Ensure MongoDB vector index exists and matches the embedding dimensions
3. **LLM Model Errors**: Verify LLM models are properly deployed and accessible
4. **Resource Limits**: Monitor Flink compute pool CFU usage for large document sets

### Verification Steps

1. Check MongoDB sink connector status: `SHOW CONNECTORS;`
2. Verify document count in MongoDB matches Kafka topic
3. Test vector search with simple queries first
4. Monitor query execution time and resource usage
