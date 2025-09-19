# Reference to core infrastructure
data "terraform_remote_state" "core" {
  backend = "local"
  config = {
    path = "../../core/terraform.tfstate"
  }
}

# Random ID for unique resource names for this lab
resource "random_id" "lab_suffix" {
  byte_length = 4
}

# Local values for extracting components from MongoDB connection string
locals {
  # Extract hostname from mongodb+srv://hostname
  mongodb_host = split("//", var.MONGODB_CONNECTION_STRING)[1]
}

# ------------------------------------------------------
# AWS-SPECIFIC RESOURCES FOR LAB2-VECTOR-SEARCH
# ------------------------------------------------------

# Lab2 uses the shared LLM infrastructure from core
# LLM embedding and text generation models are available via core terraform state

# Create documents table - basic Kafka table for document input
resource "confluent_flink_statement" "documents_table" {
  statement_name = "create-table-documents"
  organization {
    id = data.terraform_remote_state.core.outputs.confluent_organization_id
  }
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }
  compute_pool {
    id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
  }
  principal {
    id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
  }
  rest_endpoint = data.terraform_remote_state.core.outputs.confluent_flink_rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement = "CREATE TABLE `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.documents ( document_id STRING, document_text STRING );"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = "default"
  }

  lifecycle {
    prevent_destroy = false
  }
}

# Create documents_embed table schema first
resource "confluent_flink_statement" "documents_embed_table" {
  statement_name = "create-table-documents-embed"
  organization {
    id = data.terraform_remote_state.core.outputs.confluent_organization_id
  }
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }
  compute_pool {
    id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
  }
  principal {
    id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
  }
  rest_endpoint = data.terraform_remote_state.core.outputs.confluent_flink_rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement = "CREATE TABLE `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.documents_embed ( document_id STRING, chunk STRING, embedding ARRAY<FLOAT> );"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [confluent_flink_statement.documents_table]
}

# Create queries table - basic Kafka table for query input
resource "confluent_flink_statement" "queries_table" {
  statement_name = "create-table-queries"
  organization {
    id = data.terraform_remote_state.core.outputs.confluent_organization_id
  }
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }
  compute_pool {
    id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
  }
  principal {
    id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
  }
  rest_endpoint = data.terraform_remote_state.core.outputs.confluent_flink_rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement = "CREATE TABLE `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.queries ( query STRING NOT NULL );"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = "default"
  }

  lifecycle {
    prevent_destroy = false
  }
}

# Create queries_embed table schema first
resource "confluent_flink_statement" "queries_embed_table" {
  statement_name = "create-table-queries-embed"
  organization {
    id = data.terraform_remote_state.core.outputs.confluent_organization_id
  }
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }
  compute_pool {
    id = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
  }
  principal {
    id = data.terraform_remote_state.core.outputs.app_manager_service_account_id
  }
  rest_endpoint = data.terraform_remote_state.core.outputs.confluent_flink_rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement = "CREATE TABLE `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.queries_embed ( query STRING, embedding ARRAY<FLOAT> );"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [confluent_flink_statement.queries_table]
}

# MongoDB Sink Connector for streaming documents_embed to MongoDB
resource "confluent_connector" "mongodb_sink" {
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }

  kafka_cluster {
    id = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_id
  }

  config_sensitive = {
    "connection.password" = var.mongodb_password
    "kafka.api.secret"    = data.terraform_remote_state.core.outputs.app_manager_kafka_api_secret
  }

  config_nonsensitive = {
    "connector.class"                          = "MongoDbAtlasSink"
    "name"                                    = "mongodb-sink"
    "kafka.api.key"                           = data.terraform_remote_state.core.outputs.app_manager_kafka_api_key
    "topics"                                  = "documents_embed"
    "input.data.format"                       = "AVRO"
    "connection.host"                         = local.mongodb_host
    "connection.user"                         = var.mongodb_username
    "database"                               = var.MONGODB_DATABASE
    "collection"                             = var.MONGODB_COLLECTION
    "tasks.max"                              = "1"
    "value.converter.schemas.enable"          = "false"
    "value.converter.decimal.format"          = "BASE64"
    "max.num.retries"                        = "3"
    "retries.defer.timeout"                  = "5000"
    "delete.on.null.values"                  = "false"
    "writemodel.strategy"                    = "DefaultWriteModelStrategy"
    "max.batch.size"                         = "0"
    "use.ordered.bulk.writes"                = "true"
    "document.id.strategy"                   = "BsonOidStrategy"
    "document.id.strategy.overwrite.existing" = "false"
  }

  depends_on = [
    confluent_flink_statement.documents_embed_table
  ]
}

# Generate MongoDB setup commands file with CLI instructions
resource "local_file" "mongodb_commands" {
  filename = "${path.module}/mongodb_commands.txt"
  content  = <<-EOT
# Lab2 Vector Search - Generated Commands
#
# 🎉 AUTOMATED BY TERRAFORM:
# ✅ Core LLM infrastructure (deployed in core terraform)
# ✅ LLM embedding model: llm_embedding_model (available in core)
# ✅ LLM text generation model: llm_textgen_model (available in core)
# ✅ Basic Flink tables: documents, documents_embed, queries, queries_embed
#
# 📋 MANUAL STEPS REQUIRED:
# Run these commands after terraform apply completes

# Step 1: Create MongoDB Connection (CLI only - not supported by Terraform provider)
confluent flink connection create mongodb-connection \
  --cloud "AWS" \
  --region "${var.cloud_region}" \
  --type "mongodb" \
  --endpoint "${var.MONGODB_CONNECTION_STRING}" \
  --username "${var.mongodb_username}" \
  --password "${var.mongodb_password}" \
  --environment "${data.terraform_remote_state.core.outputs.confluent_environment_id}"

# Step 2: Populate Embedding Tables (run these in Confluent Cloud SQL workspace)

# Populate documents_embed table with chunked and embedded documents
INSERT INTO `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.documents_embed
WITH chunked_texts AS (
  SELECT
    document_id,
    document_text,
    chunk
  FROM `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.documents
  CROSS JOIN UNNEST(
    ML_CHARACTER_TEXT_SPLITTER(
      document_text, 200, 20, '###', false, false, true, 'START'
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

# Populate queries_embed table with embedded queries
INSERT INTO `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.queries_embed
SELECT
  query,
  embedding
FROM `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.queries,
LATERAL TABLE(ML_PREDICT('llm_embedding_model', query));

# Step 3: Create MongoDB Vector Store and Search Tables (run these in Confluent Cloud SQL workspace)

# Create documents_vectordb table (MongoDB vector store external table)
CREATE TABLE `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.documents_vectordb (
  document_id STRING,
  chunk STRING,
  embedding ARRAY<FLOAT>
) WITH (
  'connector' = 'mongodb',
  'mongodb.connection' = 'mongodb-connection',
  'mongodb.database' = '${var.MONGODB_DATABASE}',
  'mongodb.collection' = '${var.MONGODB_COLLECTION}',
  'mongodb.index' = '${var.MONGODB_INDEX_NAME}',
  'mongodb.embedding_column' = 'embedding',
  'mongodb.numCandidates' = '500'
);

# Create search_results table (vector search results)
CREATE TABLE `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.search_results AS
SELECT
qe.query,
-- Transform the array with named fields to exclude embeddings
ARRAY[
    CAST(ROW(vs.search_results[1].document_id, vs.search_results[1].chunk) AS ROW<document_id STRING, chunk STRING>),
    CAST(ROW(vs.search_results[2].document_id, vs.search_results[2].chunk) AS ROW<document_id STRING, chunk STRING>),
    CAST(ROW(vs.search_results[3].document_id, vs.search_results[3].chunk) AS ROW<document_id STRING, chunk STRING>)
] AS results
FROM
`${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.queries_embed AS qe,
LATERAL TABLE(VECTOR_SEARCH(
    `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.documents_vectordb,
    3,
    DESCRIPTOR(embedding),
    qe.embedding
)) AS vs;

# Create search_results_response table (RAG responses)
CREATE TABLE `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.search_results_response AS
SELECT
    qr.query,
    CAST(qr.results AS STRING) AS results_text,
    pred.response
FROM `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.search_results qr,
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

EOT
}