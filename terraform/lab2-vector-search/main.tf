# Reference to core infrastructure
data "terraform_remote_state" "core" {
  backend = "local"
  config = {
    path = "../core/terraform.tfstate"
  }
}

# Random ID for unique resource names for this lab
resource "random_id" "lab_suffix" {
  byte_length = 4
}

# Local values
locals {
  cloud_provider = data.terraform_remote_state.core.outputs.cloud_provider
  cloud_region   = data.terraform_remote_state.core.outputs.cloud_region

  # Cloud-specific MongoDB defaults
  mongodb_defaults = {
    aws   = { conn = "mongodb+srv://cluster0.c79vrkg.mongodb.net/", user = "workshop-user", pass = "xr6PvJl9xZz1uoKa" }
    azure = { conn = "mongodb+srv://cluster0.xhgx1kr.mongodb.net/", user = "public_readonly_user", pass = "sB948mVgIYqwUloX" }
  }

  effective_mongodb_conn = var.mongodb_connection_string != "" ? var.mongodb_connection_string : local.mongodb_defaults[local.cloud_provider].conn
  effective_mongodb_user = var.mongodb_username != "" ? var.mongodb_username : local.mongodb_defaults[local.cloud_provider].user
  effective_mongodb_pass = var.mongodb_password != "" ? var.mongodb_password : local.mongodb_defaults[local.cloud_provider].pass

  # Extract hostname from mongodb+srv://hostname
  mongodb_host = split("//", local.effective_mongodb_conn)[1]
}

# ------------------------------------------------------
# UNIFIED RESOURCES FOR LAB2-VECTOR-SEARCH
# ------------------------------------------------------

# Lab2 uses the shared LLM infrastructure from core
# LLM embedding and text generation models are available via core terraform state

# Create MongoDB Flink Connection for vector search
resource "confluent_flink_connection" "mongodb_connection" {
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

  display_name = "mongodb-connection"
  type         = "MONGODB"
  endpoint     = local.effective_mongodb_conn
  username     = local.effective_mongodb_user
  password     = local.effective_mongodb_pass

  lifecycle {
    prevent_destroy = false
  }
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

# Sample data insertion - insert one query for testing
resource "confluent_flink_statement" "queries_insert_sample" {
  statement_name = "queries-insert-sample"

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

  statement = "INSERT INTO queries VALUES ('How do I create a Flink table?');"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.queries_table
  ]
}

# Create documents_vectordb table (MongoDB vector store external table)
resource "confluent_flink_statement" "documents_vectordb_create_table" {
  statement_name = "documents-vectordb-create-table"

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

  statement = "CREATE TABLE IF NOT EXISTS documents_vectordb_lab2 ( document_id STRING, chunk STRING, embedding ARRAY<FLOAT> ) WITH ( 'connector' = 'mongodb', 'mongodb.connection' = 'mongodb-connection', 'mongodb.database' = '${var.MONGODB_DATABASE}', 'mongodb.collection' = '${var.MONGODB_COLLECTION}', 'mongodb.index' = '${var.MONGODB_INDEX_NAME}', 'mongodb.embedding_column' = 'embedding', 'mongodb.numCandidates' = '500' );"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_connection.mongodb_connection
  ]
}

# Populate queries_embed table with embedded queries
resource "confluent_flink_statement" "queries_embed_insert_into" {
  statement_name = "queries-embed-insert-into"

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

  statement = "INSERT INTO queries_embed SELECT query, embedding FROM queries, LATERAL TABLE(ML_PREDICT('llm_embedding_model', query));"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.queries_embed_table,
    confluent_flink_statement.documents_vectordb_create_table
  ]
}

# Create search_results table with vector search results
resource "confluent_flink_statement" "search_results_create_table" {
  statement_name = "search-results-create-table"

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

  statement = "CREATE TABLE IF NOT EXISTS search_results AS SELECT qe.query, vs.search_results[1].document_id AS document_id_1, vs.search_results[1].chunk AS chunk_1, vs.search_results[1].score AS score_1, vs.search_results[2].document_id AS document_id_2, vs.search_results[2].chunk AS chunk_2, vs.search_results[2].score AS score_2, vs.search_results[3].document_id AS document_id_3, vs.search_results[3].chunk AS chunk_3, vs.search_results[3].score AS score_3 FROM queries_embed AS qe, LATERAL TABLE(VECTOR_SEARCH_AGG( documents_vectordb_lab2, DESCRIPTOR(embedding), qe.embedding, 3 )) AS vs;"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.documents_vectordb_create_table,
    confluent_flink_statement.queries_embed_insert_into
  ]
}

# Create search_results_response table with RAG responses
resource "confluent_flink_statement" "search_results_response_create_table" {
  statement_name = "search-results-response-create-table"

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

  statement = "CREATE TABLE IF NOT EXISTS search_results_response AS SELECT sr.query, sr.document_id_1, sr.chunk_1, sr.score_1, sr.document_id_2, sr.chunk_2, sr.score_2, sr.document_id_3, sr.chunk_3, sr.score_3, pred.response FROM search_results sr, LATERAL TABLE( ml_predict( 'llm_textgen_model', CONCAT( 'Based on the following search results, provide a helpful and comprehensive response to the user query based upon the relevant retrieved documents. Cite the exact parts of the retrieved documents whenever possible.\\n\\nUSER QUERY: ', sr.query, '\\n\\nSEARCH RESULTS:\\n\\nDocument 1 (Similarity Score: ', CAST(sr.score_1 AS STRING), '):\\nSource: ', sr.document_id_1, '\\nContent: ', sr.chunk_1, '\\n\\nDocument 2 (Similarity Score: ', CAST(sr.score_2 AS STRING), '):\\nSource: ', sr.document_id_2, '\\nContent: ', sr.chunk_2, '\\n\\nDocument 3 (Similarity Score: ', CAST(sr.score_3 AS STRING), '):\\nSource: ', sr.document_id_3, '\\nContent: ', sr.chunk_3, '\\n\\nINSTRUCTIONS:\\n- Synthesize information from the most relevant documents above\\n- Provide specific, actionable guidance when possible\\n- Reference document sources in your response\\n- If the search results don''t contain relevant information, say so clearly\\n\\nRESPONSE:' ) ) ) AS pred;"

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.search_results_create_table
  ]
}

# Generate Flink SQL command summary
resource "null_resource" "generate_flink_sql_summary" {
  # Trigger regeneration when key resources change
  triggers = {
    queries_table         = confluent_flink_statement.queries_table.id
    mongodb_connection    = confluent_flink_connection.mongodb_connection.id
  }

  provisioner "local-exec" {
    command     = "cd ${path.module}/../.. && uv run generate_summaries ${local.cloud_provider}"
    working_dir = path.module
  }

  depends_on = [
    confluent_flink_statement.queries_table,
    confluent_flink_statement.queries_embed_table,
    confluent_flink_statement.documents_vectordb_create_table,
    confluent_flink_statement.search_results_create_table,
    confluent_flink_statement.search_results_response_create_table
  ]
}
