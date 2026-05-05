# Reference to core infrastructure
data "terraform_remote_state" "core" {
  backend = "local"
  config = {
    path = "../core/terraform.tfstate"
  }
}

# Local values
locals {
  cloud_provider = data.terraform_remote_state.core.outputs.cloud_provider
  cloud_region   = data.terraform_remote_state.core.outputs.cloud_region

  # Amazon MQ (ActiveMQ engine) credentials - workshop read-only access
  # Broker in AWS us-east-1, used via Confluent Cloud ActiveMQ Source connector
  activemq_url      = "ssl://b-f5cac8db-4315-42f8-9d2e-300a720feb46-1.mq.us-east-1.amazonaws.com:61617"
  activemq_username = "workshop-user"
  activemq_password = var.activemq_password
  activemq_queue    = "claims"

  # IBM MQ on IBM Cloud credentials
  # Queue manager: CLAIMSQM, IBM Cloud US South, port 32751
  ibmmq_hostname      = "claimsqm-3254.qm.us-south.mq.appdomain.cloud"
  ibmmq_port          = "32751"
  ibmmq_queue_manager = "CLAIMSQM"
  ibmmq_channel       = "CLOUD.APP.SVRCONN"
  ibmmq_username      = "app"
  ibmmq_password      = var.ibmmq_password
  ibmmq_queue         = "DEV.CLAIMS.1"

  # Claims Investigation Service (CIS) API endpoint (TO BE CREATED)
  cis_api_endpoint = "https://lab5-cis.example.com"  # Replace with actual endpoint

  # Watson X Data Lakehouse S3 bucket (TO BE CREATED)
  # Used by Tableflow connector for claims_reviewed_iceberg sink
  watsonx_s3_bucket = "lab5-insurance-fraud-watsonx"
  watsonx_s3_region = "us-east-1"

}

# Get organization data
data "confluent_organization" "main" {}

# Get Flink region data
data "confluent_flink_region" "lab5_flink_region" {
  cloud  = upper(local.cloud_provider)
  region = local.cloud_region
}

# ==============================================================================
# Lab 5 Topic Flow:
# 1. IBM MQ (AWS) -> claims topic (via MQ Source Connector)
# 2. Flink Anomaly Detection -> claims_anomalies topic
# 3. Flink Streaming Agent -> claims_reviewed topic
# 4. Real Time Context Engine serves claims_reviewed to external apps
# 5. Tableflow -> claims_reviewed_iceberg (S3 + Iceberg in Watson X Data Lakehouse)
# ==============================================================================

# Create claims table with WATERMARK for streaming
resource "confluent_flink_statement" "claims_table" {
  organization {
    id = data.confluent_organization.main.id
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
  rest_endpoint = data.confluent_flink_region.lab5_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "claims-create-table"

  statement = <<-EOT
    CREATE TABLE IF NOT EXISTS `claims` (
      `claim_id` STRING NOT NULL,
      `applicant_name` STRING,
      `city` STRING NOT NULL,
      `is_primary_residence` STRING,
      `damage_assessed` STRING,
      `claim_amount` STRING NOT NULL,
      `has_insurance` STRING,
      `insurance_amount` STRING,
      `claim_narrative` STRING,
      `assessment_date` STRING,
      `disaster_date` STRING,
      `previous_claims_count` STRING,
      `last_claim_date` STRING,
      `assessment_source` STRING,
      `shared_account` STRING,
      `shared_phone` STRING,
      `claim_timestamp` TIMESTAMP(3) NOT NULL,
      WATERMARK FOR `claim_timestamp` AS `claim_timestamp` - INTERVAL '5' SECOND
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    data.terraform_remote_state.core
  ]
}

# ==============================================================================
# claim_mq table — receives raw JMS envelope from IBM MQ Source connector
# The connector registers its own AVRO schema; this table just creates the topic.
# Flink INSERT (claim_mq_to_claims) will parse the text field into claims.
# ==============================================================================
resource "confluent_flink_statement" "claim_mq_table" {
  organization {
    id = data.confluent_organization.main.id
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
  rest_endpoint = data.confluent_flink_region.lab5_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "claim-mq-create-table"

  statement = <<-EOT
    CREATE TABLE IF NOT EXISTS `claim_mq` (
      `messageID` STRING,
      `messageType` STRING,
      `timestamp` BIGINT,
      `deliveryMode` INT,
      `text` STRING
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    data.terraform_remote_state.core
  ]
}

# Create claims_investigation table (CIS reference data, keyed by claim_id)
resource "confluent_flink_statement" "claims_investigation_table" {
  organization {
    id = data.confluent_organization.main.id
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
  rest_endpoint = data.confluent_flink_region.lab5_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "claims-investigation-create-table"

  statement = <<-EOT
    CREATE TABLE IF NOT EXISTS `claims_investigation` (
      `claim_id` STRING NOT NULL,
      `policy_owner_name` STRING NOT NULL,
      `policy_coverage_amount` STRING NOT NULL,
      `policy_status` STRING NOT NULL,
      `policy_history` STRING NOT NULL,
      `clue_history` STRING,
      `ip_country` STRING NOT NULL,
      `bank_account_country` STRING NOT NULL,
      `identity_verified` STRING NOT NULL,
      `ssn_matches_policyholder` STRING NOT NULL,
      `identity_theft_history` STRING NOT NULL
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    data.terraform_remote_state.core
  ]
}

# ==============================================================================
# Anomaly Detection CTAS
# Reads from claims (event-time windowed), applies ML_DETECT_ANOMALIES, and
# writes matching claims to claims_anomalies topic.
# Depends on claims_table so the source table exists before the job starts.
# ==============================================================================
# Anomaly Detection CTAS
# Reads from claims (event-time windowed), applies ML_DETECT_ANOMALIES, and
# writes matching claims to claims_anomalies topic.
# Depends on claims_table so the source table exists before the job starts.
# ==============================================================================
# ==============================================================================
# Flink CTAS: detects anomalous claim surge windows for Naples
# Emits ONE row per anomalous 1-hour window (the surge signal).
# ==============================================================================
resource "confluent_flink_statement" "claims_surge_windows_table" {
  organization {
    id = data.confluent_organization.main.id
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
  rest_endpoint = data.confluent_flink_region.lab5_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "claims-surge-windows-create-table"

  statement = <<-EOT
    CREATE TABLE IF NOT EXISTS `claims_surge_windows` AS
    WITH windowed AS (
        SELECT
            window_start,
            window_end,
            window_time,
            city,
            COUNT(*) AS claim_count,
            SUM(CAST(claim_amount AS DOUBLE)) AS total_claim_amount
        FROM TABLE(
            TUMBLE(TABLE `claims`, DESCRIPTOR(`claim_timestamp`), INTERVAL '1' HOUR)
        )
        WHERE city = 'Naples'
        GROUP BY window_start, window_end, window_time, city
    )
    SELECT
        window_start,
        window_end,
        city,
        claim_count,
        total_claim_amount,
        anomaly_result.upper_bound AS upper_bound,
        anomaly_result.is_anomaly AS is_anomaly
    FROM (
        SELECT
            *,
            ML_DETECT_ANOMALIES(
                CAST(claim_count AS DOUBLE),
                window_time,
                JSON_OBJECT(
                    'minTrainingSize' VALUE 3,
                    'maxTrainingSize' VALUE 50,
                    'confidencePercentage' VALUE 90.0,
                    'enableStl' VALUE FALSE
                )
            ) OVER (
                PARTITION BY city
                ORDER BY window_time
                RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS anomaly_result
        FROM windowed
    )
    WHERE anomaly_result.is_anomaly = TRUE
      AND CAST(claim_count AS DOUBLE) > anomaly_result.upper_bound
      AND claim_count >= 10;
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.claims_table
  ]
}

# ==============================================================================
# Flink CTAS: retrieves individual claims that fall within a detected surge window
# ==============================================================================
resource "confluent_flink_statement" "claims_anomalies_table" {
  organization {
    id = data.confluent_organization.main.id
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
  rest_endpoint = data.confluent_flink_region.lab5_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "claims-anomalies-create-table"

  statement = <<-EOT
    CREATE TABLE IF NOT EXISTS `claims_anomalies` AS
    SELECT
        c.`claim_id`,
        c.`applicant_name`,
        c.`city`,
        c.`claim_amount`,
        c.`damage_assessed`,
        c.`has_insurance`,
        c.`insurance_amount`,
        c.`is_primary_residence`,
        c.`claim_narrative`,
        c.`claim_timestamp`
    FROM `claims` c
    INNER JOIN `claims_surge_windows` w
        ON  c.`city`            = w.city
        AND c.`claim_timestamp` >= w.window_start
        AND c.`claim_timestamp` <  w.window_end
    WHERE c.`claim_narrative` <> ''
      AND c.`has_insurance`   = 'yes';
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.claims_surge_windows_table
  ]
}

# ==============================================================================
# Schema Registry: set NONE compatibility on claim_mq-value so the IBM MQ
# connector can register its AVRO schema even if a prior schema exists.
# ==============================================================================
resource "confluent_subject_config" "claim_mq_value" {
  schema_registry_cluster {
    id = data.terraform_remote_state.core.outputs.confluent_schema_registry_id
  }
  rest_endpoint = data.terraform_remote_state.core.outputs.confluent_schema_registry_rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_schema_registry_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_schema_registry_api_secret
  }

  subject_name          = "claim_mq-value"
  compatibility_level   = "NONE"
}

# ==============================================================================
# IBM MQ Source Connector (IBM Cloud — CLAIMSQM)
# Reads JMS messages from IBM MQ → claim_mq Kafka topic (raw JMS envelope).
# A Flink INSERT job (claim_mq_to_claims) parses the envelope into claims.
# ==============================================================================
resource "confluent_connector" "ibmmq_source" {
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }

  kafka_cluster {
    id = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_id
  }

  config_sensitive = {
    "mq.password" = local.ibmmq_password
  }

  config_nonsensitive = {
    "connector.class"          = "IbmMQSource"
    "name"                     = "IbmMQSourceConnector_0"
    "kafka.auth.mode"          = "SERVICE_ACCOUNT"
    "kafka.service.account.id" = data.terraform_remote_state.core.outputs.app_manager_service_account_id

    "mq.hostname"      = local.ibmmq_hostname
    "mq.port"          = local.ibmmq_port
    "mq.queue.manager" = local.ibmmq_queue_manager
    "mq.channel"       = local.ibmmq_channel
    "mq.username"           = local.ibmmq_username
    "mq.ssl.cipher.suite"   = "*TLS12ORHIGHER"

    "jms.destination.name" = local.ibmmq_queue
    "jms.destination.type" = "queue"

    "kafka.topic"        = "claim_mq"
    "output.data.format" = "AVRO"
    "tasks.max"          = "1"
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.claim_mq_table,
    confluent_subject_config.claim_mq_value,
  ]
}

# ==============================================================================
# Flink INSERT: claim_mq → claims
# Parses the JMS text field (JSON with Avro union encoding) into flat claims.
# ==============================================================================
resource "confluent_flink_statement" "claim_mq_to_claims" {
  organization {
    id = data.confluent_organization.main.id
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
  rest_endpoint = data.confluent_flink_region.lab5_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "claim-mq-to-claims-insert"

  # FLAT_JSON_SWITCH: The JSON paths below assume the ORIGINAL MQ message format
  # (Avro union envelope: $.value.field_name.string). If you switch to the flat
  # JSON publisher (scripts/publish_claims_to_ibmmq.py), replace ALL paths:
  #   $.value.claim_id           → $.claim_id
  #   $.value.applicant_name.string → $.applicant_name
  #   $.value.city               → $.city
  #   $.value.<field>.string     → $.<field>
  #   $.value.claim_timestamp    → $.claim_timestamp
  statement = <<-EOT
    INSERT INTO `claims`
    SELECT
      JSON_VALUE(`text`, '$.value.claim_id')                          AS `claim_id`,
      JSON_VALUE(`text`, '$.value.applicant_name.string')             AS `applicant_name`,
      JSON_VALUE(`text`, '$.value.city')                              AS `city`,
      JSON_VALUE(`text`, '$.value.is_primary_residence.string')       AS `is_primary_residence`,
      JSON_VALUE(`text`, '$.value.damage_assessed.string')            AS `damage_assessed`,
      JSON_VALUE(`text`, '$.value.claim_amount')                      AS `claim_amount`,
      JSON_VALUE(`text`, '$.value.has_insurance.string')              AS `has_insurance`,
      JSON_VALUE(`text`, '$.value.insurance_amount.string')           AS `insurance_amount`,
      JSON_VALUE(`text`, '$.value.claim_narrative.string')            AS `claim_narrative`,
      JSON_VALUE(`text`, '$.value.assessment_date.string')            AS `assessment_date`,
      JSON_VALUE(`text`, '$.value.disaster_date.string')              AS `disaster_date`,
      JSON_VALUE(`text`, '$.value.previous_claims_count.string')      AS `previous_claims_count`,
      JSON_VALUE(`text`, '$.value.last_claim_date.string')            AS `last_claim_date`,
      JSON_VALUE(`text`, '$.value.assessment_source.string')          AS `assessment_source`,
      JSON_VALUE(`text`, '$.value.shared_account.string')             AS `shared_account`,
      JSON_VALUE(`text`, '$.value.shared_phone.string')               AS `shared_phone`,
      TO_TIMESTAMP_LTZ(
        CAST(JSON_VALUE(`text`, '$.value.claim_timestamp') AS BIGINT),
        3
      )                                                               AS `claim_timestamp`
    FROM `claim_mq`;
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.claim_mq_table,
    confluent_flink_statement.claims_table,
  ]
}

# ==============================================================================
# HTTP Sink Connector
# Reads anomalous claims from claims_anomalies → POSTs to webhook_proxy.py
# (tunneled via ngrok static domain → localhost:8090 on the demo Mac)
# ==============================================================================
resource "confluent_connector" "fraud_investigation_http_sink" {
  environment {
    id = data.terraform_remote_state.core.outputs.confluent_environment_id
  }

  kafka_cluster {
    id = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_id
  }

  config_sensitive = {
    "schema.registry.basic.auth.user.info" = var.schema_registry_auth
  }

  config_nonsensitive = {
    "connector.class"          = "HttpSink"
    "name"                     = "fraud-investigation-sink"
    "kafka.auth.mode"          = "SERVICE_ACCOUNT"
    "kafka.service.account.id" = data.terraform_remote_state.core.outputs.app_manager_service_account_id

    "topics"              = "claims_anomalies"
    "http.api.url"        = "https://proacquittal-freddy-astigmic.ngrok-free.dev/alert"
    "request.method"      = "POST"
    "headers"             = "Content-Type: application/json"
    "request.body.format" = "json"
    "batch.max.size"      = "1"
    "tasks.max"           = "1"

    "input.data.format"                            = "AVRO"
    "schema.registry.url"                          = "https://psrc-1ry6wml.us-east-1.aws.confluent.cloud"
    "schema.registry.basic.auth.credentials.source" = "USER_INFO"
    "consumer.override.auto.offset.reset"          = "earliest"
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.claims_anomalies_table,
  ]
}

# # Run datagen — disabled; data now comes from IBM MQ connector + HTTP Source V2
# resource "null_resource" "run_datagen" {
#   provisioner "local-exec" {
#     command     = "uv run lab5_datagen"
#     working_dir = "${path.module}/../.."
#   }
#
#   depends_on = [
#     confluent_flink_statement.claims_table,
#     confluent_flink_statement.claims_investigation_table,
#   ]
# }

# ==============================================================================
# HTTP Source V2 Connector — DISABLED
# Previously polled ngrok/WatsonX for investigation results → claims_investigation.
# Replaced by: agent calls CIS directly via CREATE TOOL (webhooks_by_zapier_get).
# ==============================================================================
# resource "confluent_connector" "watsonx_response_http_source" {
#   environment {
#     id = data.terraform_remote_state.core.outputs.confluent_environment_id
#   }
#
#   kafka_cluster {
#     id = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_id
#   }
#
#   config_sensitive = {}
#
#   config_nonsensitive = {
#     "connector.class"          = "HttpSourceV2"
#     "name"                     = "watsonx-investigation-source"
#     "kafka.auth.mode"          = "SERVICE_ACCOUNT"
#     "kafka.service.account.id" = data.terraform_remote_state.core.outputs.app_manager_service_account_id
#
#     "output.data.format" = "AVRO"
#     "tasks.max"          = "1"
#
#     "http.api.base.url"               = "https://proacquittal-freddy-astigmic.ngrok-free.dev"
#     "auth.type"                        = "NONE"
#     "apis.num"                         = "1"
#     "api1.http.request.method"         = "GET"
#     "api1.http.offset.mode"            = "SIMPLE_INCREMENTING"
#     "api1.http.initial.offset"         = "0"
#     "api1.topics"                      = "claims_investigation"
#     "api1.request.interval.ms"         = "30000"
#     "api1.http.connect.timeout.ms"     = "30000"
#     "api1.http.request.timeout.ms"     = "30000"
#     "api1.max.retries"                 = "3"
#     "api1.retry.backoff.policy"        = "EXPONENTIAL_WITH_JITTER"
#     "api1.retry.backoff.ms"            = "3000"
#     "api1.retry.on.status.codes"       = "400-"
#     "behavior.on.error"                = "IGNORE"
#   }
#
#   lifecycle {
#     prevent_destroy = false
#   }
#
#   depends_on = [
#     confluent_flink_statement.claims_investigation_table
#   ]
# }

# ==============================================================================
# Flink: CREATE CONNECTION — Zapier MCP Server
# Required before CREATE TOOL can reference it.
# ==============================================================================
resource "confluent_flink_statement" "zapier_mcp_connection" {
  organization {
    id = data.confluent_organization.main.id
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
  rest_endpoint = data.confluent_flink_region.lab5_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "zapier-mcp-connection-create-lab5"

  statement = <<-EOT
    CREATE CONNECTION IF NOT EXISTS `${data.terraform_remote_state.core.outputs.confluent_environment_display_name}`.`${data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name}`.`zapier-mcp-connection`
    WITH (
      'type'           = 'MCP_SERVER',
      'endpoint'       = 'https://mcp.zapier.com/api/v1/connect',
      'token'          = '${var.zapier_token}',
      'transport-type' = 'STREAMABLE_HTTP'
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    ignore_changes  = [statement]
    prevent_destroy = false
  }

  depends_on = [
    data.terraform_remote_state.core
  ]
}

# ==============================================================================
# Flink: CREATE TOOL — Claims Investigation Service (CIS)
# Gives the fraud_review_agent GET access to the CIS Lambda endpoint.
# Endpoint: GET https://ildw2o0gik.execute-api.us-east-1.amazonaws.com/prod/investigation/{claim_id}
# ==============================================================================
resource "confluent_flink_statement" "cis_tool" {
  organization {
    id = data.confluent_organization.main.id
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
  rest_endpoint = data.confluent_flink_region.lab5_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "claims-investigation-service-create-tool"

  statement = <<-EOT
    CREATE TOOL IF NOT EXISTS `claims_investigation_service`
    USING CONNECTION `zapier-mcp-connection`
    WITH (
      'type'             = 'mcp',
      'allowed_tools'    = 'webhooks_by_zapier_get',
      'request_timeout'  = '30'
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.zapier_mcp_connection
  ]
}

# ==============================================================================
# Flink: CREATE AGENT for fraud review
# ==============================================================================
resource "confluent_flink_statement" "fraud_review_agent" {
  organization {
    id = data.confluent_organization.main.id
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
  rest_endpoint = data.confluent_flink_region.lab5_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "fraud-review-agent-create"

  statement = <<-EOT
    CREATE AGENT `fraud_review_agent`
    USING MODEL `llm_textgen_model`
    USING PROMPT 'OUTPUT RULES — read before anything else:
    1. Respond with ONLY these six labeled sections, in this exact order:
       Policy Coverage Amount:
       Policy Status:
       Verdict:
       Payment Amount:
       Issues Found:
       Summary:
    2. NO markdown. No asterisks, no bold, no headers, no pound signs. Plain text only.
    3. Verdict must be exactly one word: APPROVE or DENY.
    4. Payment Amount: if APPROVE, the dollar amount to pay (never exceeds Policy Coverage Amount); if DENY, write $0.
    5. Policy Coverage Amount: copy the exact coverage_amount value from the CIS response (e.g. $250,000).
    6. Policy Status: copy the exact policy status value from the CIS response (e.g. active, lapsed, cancelled).

    Correct format example:
    Policy Coverage Amount: $250,000

    Policy Status: active

    Verdict: DENY

    Payment Amount: $0

    Issues Found:
    - Policy purchased 2024-11-01, disaster occurred 2024-11-15. Policy active for only 14 days — less than the 30-day coverage fraud window.

    Summary:
    Claim denied. Policy was purchased within 30 days of the disaster, indicating potential coverage fraud.

    ---

    You are an insurance fraud review agent investigating flagged claims for hurricane damage in Naples, FL. Each claim was already identified as a statistical anomaly.

    STEP 1 — FETCH INVESTIGATION DATA:
    Before evaluating any fraud rules, you MUST call the webhooks_by_zapier_get tool to retrieve the full investigation record for this claim.
    Use this URL: https://ildw2o0gik.execute-api.us-east-1.amazonaws.com/prod/investigation/{claim_id}
    Replace {claim_id} with the claim_id provided in the input.
    The response contains: policy owner name, coverage amount, policy status, policy history, CLUE history, ip_country, bank_account_country, identity_verified, ssn_matches_policyholder, identity_theft_history.

    STEP 2 — APPLY FRAUD DETECTION RULES in order. Stop at the first DENY trigger.

    RULE 1 — COVERAGE FRAUD: Was the policy purchased less than 30 days before the disaster?
      Check policy.history for the purchase date vs the claim timestamp. If < 30 days, DENY.

    RULE 2 — PRE-EXISTING DAMAGE: Does the CLUE history show a prior claim for the same damage type where "Repair recorded: no"?
      If prior unrepaired damage matches the current claim type, DENY.

    RULE 3 — SANCTIONED COUNTRY / UNVERIFIABLE BANK: Is identity_verification.ip_country one of North Korea, Iran, or Russia? Is identity_verification.bank_account_country = "Unverifiable"?
      If either condition holds, DENY.

    RULE 4 — IDENTITY FAILURE: Is identity_verification.identity_verified = false or identity_verification.ssn_matches_policyholder = false?
      DENY if identity cannot be confirmed.

    RULE 5 — INACTIVE POLICY: Is policy.status anything other than "active"?
      DENY if the policy is lapsed, cancelled, or otherwise inactive.

    If all rules pass: APPROVE.

    PAYMENT AMOUNT:
    - APPROVE: pay min(claim_amount, policy.coverage_amount). Round to nearest dollar. Format as $XX,XXX.
    - DENY: $0.

    In Issues Found: state which rule triggered, or "None — all checks pass." if APPROVE. Quote the specific data field values from the CIS response.
    In Summary: one or two sentences explaining the decision.

    REMINDER: Plain text only. No asterisks, no bold, no markdown of any kind.'
    USING TOOLS `claims_investigation_service`
    WITH (
      'max_iterations' = '10'
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.cis_tool
  ]
}

# ==============================================================================
# Flink: CREATE TABLE claims_reviewed (schema only)
# ==============================================================================
resource "confluent_flink_statement" "claims_reviewed_table" {
  organization {
    id = data.confluent_organization.main.id
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
  rest_endpoint = data.confluent_flink_region.lab5_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "claims-reviewed-create-table"

  statement = <<-EOT
    CREATE TABLE IF NOT EXISTS `claims_reviewed` (
      `claim_id`              STRING NOT NULL,
      `applicant_name`        STRING,
      `city`                  STRING,
      `claim_amount`          STRING,
      `policy_coverage_amount` STRING,
      `policy_status`         STRING,
      `verdict`               STRING,
      `payment_amount`        STRING,
      `issues_found`          STRING,
      `summary`               STRING,
      `raw_response`          STRING
    );
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.claims_anomalies_table,
    confluent_flink_statement.claims_investigation_table,
    confluent_flink_statement.fraud_review_agent,
  ]
}

# ==============================================================================
# Flink INSERT: reads claims_anomalies, runs AI_RUN_AGENT (agent fetches CIS data)
# Agent calls CIS directly via webhooks_by_zapier_get — no join needed.
# ==============================================================================
resource "confluent_flink_statement" "claims_reviewed_insert" {
  organization {
    id = data.confluent_organization.main.id
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
  rest_endpoint = data.confluent_flink_region.lab5_flink_region.rest_endpoint
  credentials {
    key    = data.terraform_remote_state.core.outputs.app_manager_flink_api_key
    secret = data.terraform_remote_state.core.outputs.app_manager_flink_api_secret
  }

  statement_name = "claims-reviewed-insert"

  statement = <<-EOT
    INSERT INTO `claims_reviewed`
    SELECT
        claim_id,
        applicant_name,
        city,
        claim_amount,
        TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '\*{0,2}Policy Coverage Amount:\*{0,2}\s*(\$[\d,]+)', 1)) AS policy_coverage_amount,
        TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '\*{0,2}Policy Status:\*{0,2}\s*(\S+)', 1))              AS policy_status,
        TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '\*{0,2}Verdict:\*{0,2}\s*([A-Z]+)', 1))                 AS verdict,
        TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '\*{0,2}Payment Amount:\*{0,2}\s*(\$[\d,]+)', 1))        AS payment_amount,
        TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '\*{0,2}Issues Found:\*{0,2}\n([\s\S]+?)(?=\n\*{0,2}Summary:)', 1)) AS issues_found,
        TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '\*{0,2}Summary:\*{0,2}\n([\s\S]+?)$', 1))               AS summary,
        CAST(response AS STRING) AS raw_response
    FROM `claims_anomalies`,
    LATERAL TABLE(AI_RUN_AGENT(
        `fraud_review_agent`,
        CONCAT(
            'CLAIM FOR REVIEW: ', claim_id, '\n',
            'Applicant: ', applicant_name, '\n',
            'City: ', city, '\n',
            'Claim Amount: $', claim_amount, '\n',
            'Damage Assessed: $', COALESCE(damage_assessed, 'N/A'), '\n',
            'Has Insurance: ', COALESCE(has_insurance, 'unknown'), '\n',
            'Insurance Payout: $', COALESCE(insurance_amount, 'N/A'), '\n',
            'Is Primary Residence: ', COALESCE(is_primary_residence, 'unknown'), '\n',
            'Claim Narrative: ', COALESCE(claim_narrative, '(none)')
        )
    ));
  EOT

  properties = {
    "sql.current-catalog"  = data.terraform_remote_state.core.outputs.confluent_environment_display_name
    "sql.current-database" = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_display_name
    "sql.state-ttl"        = "14 d"
  }

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    confluent_flink_statement.claims_reviewed_table,
  ]
}

# ==============================================================================
# DISABLED: old claims_reviewed_insert — joined claims_anomalies with
# claims_investigation topic (populated by HTTP Source V2 / WatsonX connector).
# Replaced by: agent fetches CIS data directly via webhooks_by_zapier_get tool.
# ==============================================================================
# INSERT INTO `claims_reviewed`
# WITH enriched AS (
#     SELECT
#         a.`claim_id`,
#         a.`applicant_name`,
#         a.`city`,
#         a.`claim_amount`,
#         a.`damage_assessed`,
#         a.`has_insurance`,
#         a.`insurance_amount`,
#         a.`is_primary_residence`,
#         a.`claim_narrative`,
#         a.`claim_timestamp`,
#         i.`policy_owner_name`,
#         i.`policy_coverage_amount`,
#         i.`policy_status`,
#         i.`policy_history`,
#         i.`clue_history`,
#         i.`ip_country`,
#         i.`bank_account_country`,
#         i.`identity_verified`,
#         i.`ssn_matches_policyholder`,
#         i.`identity_theft_history`
#     FROM `claims_anomalies` a
#     JOIN `claims_investigation` i ON a.`applicant_name` = i.`policy_owner_name`
# )
# SELECT
#     claim_id, applicant_name, city, claim_amount,
#     policy_coverage_amount, policy_status,
#     TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '(?m)^Verdict:\s*([A-Z]+)', 1))            AS verdict,
#     TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '(?m)^Payment Amount:\s*(\$[\d,]+)', 1))   AS payment_amount,
#     TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '(?m)^Issues Found:\n([\s\S]+?)(?=\nSummary:)', 1)) AS issues_found,
#     TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '(?m)^Summary:\n([\s\S]+?)$', 1))          AS summary,
#     CAST(response AS STRING) AS raw_response
# FROM enriched,
# LATERAL TABLE(AI_RUN_AGENT(`fraud_review_agent`, CONCAT(...)));
