output "claims_table_statement_id" {
  description = "Flink statement ID for claims table"
  value       = confluent_flink_statement.claims_table.id
}

output "claims_table_name" {
  description = "Name of the claims table"
  value       = "claims"
}

output "lab5_deployment_status" {
  description = "Lab5 deployment status"
  value       = "Lab5 Insurance Fraud Detection with IBM Watson X infrastructure deployed successfully"
}

output "external_resources_info" {
  description = "Information about external resources (created manually, not via Terraform)"
  value = {
    activemq_url         = local.activemq_url
    activemq_queue       = local.activemq_queue
    cis_api_endpoint     = local.cis_api_endpoint
    watsonx_s3_bucket    = local.watsonx_s3_bucket
    setup_guide          = "See LAB5-MANUAL-SETUP.md for external infrastructure setup instructions"
  }
}

output "demo_claim_ids" {
  description = "Pre-configured demo claim IDs in the CIS API"
  value = {
    fraud_case      = "CLM-77093"
    info_request    = "CLM-88241"
    legitimate_case = "CLM-55019"
  }
}
