# MongoDB Vector Search Query Comparison

## Overview
This document compares the current (broken) vector search queries with corrected versions based on the working test example.

## Original Terraform-Generated Queries (From mongodb_commands.txt)

### Step 1: Populate Embedding Tables (ORIGINAL - with problems)

**Original documents_embed population:**
```sql
INSERT INTO `streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`.documents_embed
WITH chunked_texts AS (
  SELECT
    document_id,
    document_text,
    chunk
  FROM `streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`.documents
  CROSS JOIN UNNEST(
    ML_CHARACTER_TEXT_SPLITTER(
      document_text, 200, 20, '###', false, false, true, 'START'    -- ❌ Too small chunks
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

**Original queries_embed population:**
```sql
INSERT INTO `streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`.queries_embed
SELECT
  query,
  embedding
FROM `streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`.queries,
LATERAL TABLE(ML_PREDICT('llm_embedding_model', query));
```

## Current Queries (From Terraform/mongodb_commands.txt)

### ✅ Query 1: documents_vectordb External Table (CORRECT)
```sql
CREATE TABLE `streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`.documents_vectordb (
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

### ❌ Query 2: search_results Table (BROKEN)
```sql
CREATE TABLE `streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`.search_results AS
SELECT
qe.query,
-- Transform the array with named fields to exclude embeddings
ARRAY[
    CAST(ROW(vs.search_results[1].document_id, vs.search_results[1].chunk) AS ROW<document_id STRING, chunk STRING>),
    CAST(ROW(vs.search_results[2].document_id, vs.search_results[2].chunk) AS ROW<document_id STRING, chunk STRING>),
    CAST(ROW(vs.search_results[3].document_id, vs.search_results[3].chunk) AS ROW<document_id STRING, chunk STRING>)
] AS results
FROM
`streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`.queries_embed AS qe,
LATERAL TABLE(VECTOR_SEARCH(                           -- ❌ Wrong function name
    `streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`.documents_vectordb,
    3,                                                 -- ❌ Wrong parameter order
    DESCRIPTOR(embedding),
    qe.embedding
)) AS vs;
```

**Problems:**
1. Using `VECTOR_SEARCH` instead of `VECTOR_SEARCH_AGG`
2. Wrong parameter order: should be `(table, DESCRIPTOR(col), embedding, limit)`
3. Complex array casting that may not work properly

### ❌ Query 3: search_results_response Table (DEPENDENT ON BROKEN QUERY 2)
```sql
CREATE TABLE `streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`.search_results_response AS
SELECT
    qr.query,
    CAST(qr.results AS STRING) AS results_text,
    pred.response
FROM `streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`.search_results qr,
LATERAL TABLE(
    ml_predict(
        'llm_textgen_model',
        CONCAT(
            'You are an expert sales coach AI. Provide actionable sales guidance formatted as JSON.

## OUTPUT REQUIREMENTS:
1. Create a JSON response with these fields:
  - suggested_response: A concise, actionable talking point (75 words max)
  - sources: An array with 3 objects (one for each document) containing:
    * document_index: The document number (1, 2, or 3)
    * document_id: The full document ID as provided
    * title: Just the filename extracted from document_id
    * path: Just the directory path extracted from document_id
    * full_text: The complete document text
    * used_excerpt: Exact text you used from this document (or empty if unused)
  - reasoning: Brief explanation of your suggestion (25 words max)

2. For each document:
  - Extract the filename from the document_id (Example: from objection_response_playbooks/pricing_objection_playbook.md, extract pricing_objection_playbook.md)
  - Extract the directory path if present (Example: from objection_response_playbooks/pricing_objection_playbook.md, extract objection_response_playbooks/)
  - Include only the exact text passages you used to form your response in used_excerpt

3. Always include all 3 documents in your response, even if you did not use them all.

4. Ensure your response is valid JSON that can be automatically parsed.

## PROSPECT MESSAGE: ', qr.query,
            '\n\n## RAG DOCUMENTS:\n',
            'Document 1: ', qr.results[1].document_id, '\n',
            qr.results[1].chunk, '\n\n',
            'Document 2: ', qr.results[2].document_id, '\n',
            qr.results[2].chunk, '\n\n',
            'Document 3: ', qr.results[3].document_id, '\n',
            qr.results[3].chunk
        )
    )
) AS pred;
```

**Problems:**
1. Depends on broken `search_results` table structure
2. Complex array indexing that won't work with corrected structure
3. Sales coach specific - not generic

### Step 2: Original External Table (CORRECT)
```sql
CREATE TABLE `streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`.documents_vectordb (
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

## CORRECTED Queries

### ✅ Query 1: documents_vectordb External Table (No changes needed)
```sql
-- Same as existing - this one is correct
-- Removing full qualifications for easier testing
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

### ✅ Query 2: search_results Table (FIXED VERSION)

**IMPORTANT**: `VECTOR_SEARCH_AGG` returns an array structure:
```
search_results ARRAY<ROW<`document_id` STRING, `chunk` STRING, `embedding` ARRAY<FLOAT>, `score` DOUBLE>>
```

**Option A: CROSS JOIN UNNEST (Recommended)**
```sql
-- 🔧 CHANGES:
-- 1. VECTOR_SEARCH → VECTOR_SEARCH_AGG
-- 2. Parameter order: (table, DESCRIPTOR(col), embedding, limit)
-- 3. CROSS JOIN UNNEST to flatten the array structure
-- 4. Excludes embedding vectors, includes similarity score

CREATE TABLE search_results_flat AS
SELECT
  qe.query,
  T.document_id,
  T.chunk,
  T.score
FROM queries_embed AS qe,
LATERAL TABLE(VECTOR_SEARCH_AGG(
    documents_vectordb,
    DESCRIPTOR(embedding),
    qe.embedding,
    3
)) AS vs
CROSS JOIN UNNEST(vs.search_results) AS T(document_id, chunk, embedding, score);
```

**Option B: Array Indexing (Similar to original approach)**
```sql
-- Alternative: Direct array indexing if you need fixed structure
CREATE TABLE search_results_indexed AS
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

### ✅ Query 3: search_results_response Table (GENERIC VERSION)

**Recommended: Works with Option B (search_results_indexed)**
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
FROM search_results_indexed sr,
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

**Alternative: For Flattened Results (if using search_results_flat)**
```sql
-- Works with CROSS JOIN UNNEST flattened results
-- Aggregates all search results per query for comprehensive responses
CREATE TABLE search_results_response_aggregated AS
SELECT
    grouped.query,
    grouped.chunks,
    grouped.scores,
    pred.response
FROM (
    SELECT
        query,
        ARRAY_AGG(chunk) AS chunks,
        ARRAY_AGG(CAST(score AS STRING)) AS scores,
        ARRAY_AGG(document_id) AS document_ids
    FROM search_results_flat
    GROUP BY query
) AS grouped,
LATERAL TABLE(
    ml_predict(
        'llm_textgen_model',
        CONCAT(
            'PROMPT: Based on the following search results, provide a helpful response to the user query.

USER QUERY: ', grouped.query, '

SEARCH RESULTS:
', ARRAY_JOIN(grouped.chunks, '\n\n---\n\n'), '

Document IDs: ', ARRAY_JOIN(grouped.document_ids, ', '), '
Similarity Scores: ', ARRAY_JOIN(grouped.scores, ', '), '

Please provide a comprehensive response that synthesizes information from the most relevant documents above.'
        )
    )
) AS pred;
```

---

## Key Changes Summary

| Aspect | Current (Broken) | Corrected |
|--------|------------------|-----------|
| **Function Name** | `VECTOR_SEARCH` | `VECTOR_SEARCH_AGG` |
| **Parameter Order** | `(table, limit, DESCRIPTOR, embedding)` | `(table, DESCRIPTOR, embedding, limit)` |
| **Result Structure** | Complex ROW casting and array indexing | Direct field access |
| **RAG Processing** | Broken array indexing | Simple field access or ARRAY_AGG |

## Testing Order

1. **Test Query 1** (External table) - should work as-is
2. **Test Query 2** (Vector search) - this is the key fix
3. **Test Query 3** (RAG responses) - try Option A first, then Option B

## Deviation from Terraform

The corrected queries remove the full table qualifications (`streaming-agents-env-1fda8714`.`streaming-agents-cluster-1fda8714`) for easier testing. When updating Terraform, we'll need to add those back to the statement templates.
