# Complete MongoDB Vector Search Implementation

## Overview
This document contains the complete, tested implementation for MongoDB vector search with Confluent Flink SQL. All queries have been validated and corrected.

---

## Step 1: Populate Embedding Tables

### Populate documents_embed (IMPROVED VERSION)
```sql
-- 🔧 IMPROVED: Optimized chunking strategy for demo corpus
-- - 5000 chars max for excellent context preservation
-- - 200 char overlap for continuity
-- - Splits only on # or ## headings (not ###)
-- - Target: 500-1000 embeddings total for demo

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
- `5000` - Max chunk size (characters) - excellent context preservation (~800-1200 tokens)
- `200` - Overlap size - ensures continuity between chunks (4% overlap)
- `'"^#{1,2}\\s"'` - Regex for # or ## headings only (not ###, ####, etc.)
- `true, true, true, 'START'` - Enable regex, case-sensitive, trim whitespace, start mode

### Populate queries_embed
```sql
INSERT INTO queries_embed
SELECT
  query,
  embedding
FROM queries,
LATERAL TABLE(ML_PREDICT('llm_embedding_model', query));
```

---

## Step 2: Create MongoDB External Table

```sql
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

```sql
-- Creates search_results table with all 3 vector search results per query
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

---

## Step 4: Create RAG Response Table

```sql
-- =================================================================
-- CONFIGURABLE PROMPT - MODIFY AS NEEDED
-- =================================================================
-- Default prompt - change this to customize the LLM behavior
-- Available variables: {query}, {doc1_id}, {doc1_chunk}, {doc1_score},
--                     {doc2_id}, {doc2_chunk}, {doc2_score},
--                     {doc3_id}, {doc3_chunk}, {doc3_score}

-- =================================================================
-- SEARCH RESULTS RESPONSE - GENERIC VERSION
-- =================================================================
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
            'PROMPT: Based on the following search results, provide a helpful response to the user query.

USER QUERY: ', sr.query, '

SEARCH RESULTS:

Document 1 (Score: ', CAST(sr.score_1 AS STRING), '):
ID: ', sr.document_id_1, '
Content: ', sr.chunk_1, '

Document 2 (Score: ', CAST(sr.score_2 AS STRING), '):
ID: ', sr.document_id_2, '
Content: ', sr.chunk_2, '

Document 3 (Score: ', CAST(sr.score_3 AS STRING), '):
ID: ', sr.document_id_3, '
Content: ', sr.chunk_3, '

Please provide a comprehensive response that synthesizes information from the most relevant documents above.'
        )
    )
) AS pred;
```

---

## Execution Order

1. **Step 1**: Populate `documents_embed` (this streams to MongoDB via your Terraform connector)
2. **Step 2**: Create `documents_vectordb` external table
3. **Step 3**: Create `search_results` table
4. **Step 4**: Create `search_results_response` table for RAG

---

## Corpus Size Estimation

**Your Text Splitter Settings Analysis:**
- **5000 characters per chunk** (~800-1200 tokens) - excellent context preservation
- **Splits only on # or ## headings** + token ceiling
- **200 character overlap** (4% overlap for continuity)

**Expected Embedding Count Estimation:**

With 5000-character chunks:
- **Small documents** (<5000 chars): 1 embedding each
- **Medium documents** (5000-15000 chars): 2-4 embeddings each
- **Large documents** (>15000 chars): Split at major headings + size limit
- **Demo corpus estimate**: 500-1500 total embeddings (perfect for demo!)

**Your settings are excellent for demo because:**
- ✅ **5000 chars preserves excellent context** (much better than smaller chunks)
- ✅ **Major heading splits** maintain logical boundaries
- ✅ **200 char overlap** ensures continuity
- ✅ **Manageable chunk count** for demo purposes
- ✅ **Better performance** with larger, more meaningful chunks

**MongoDB Performance Considerations:**
- Ensure your MongoDB index can handle the expected volume
- Consider `mongodb.numCandidates` setting (currently 500) based on corpus size
- Monitor query performance as corpus grows

---

## Alternative: Flattened Results (For Reference)

If you prefer one row per search result instead of fixed columns:

```sql
-- Alternative flattened approach using CROSS JOIN UNNEST
CREATE TABLE search_results_flat AS
SELECT
  base.query,
  T.document_id,
  T.chunk,
  T.score
FROM (
  SELECT
    qe.query,
    vs.search_results
  FROM queries_embed AS qe,
  LATERAL TABLE(VECTOR_SEARCH_AGG(
      documents_vectordb,
      DESCRIPTOR(embedding),
      qe.embedding,
      3
  )) AS vs
) AS base
CROSS JOIN UNNEST(base.search_results) AS T(document_id, chunk, embedding, score);
```

This creates a flattened structure with one row per search result, but the main implementation above is recommended for your use case.
