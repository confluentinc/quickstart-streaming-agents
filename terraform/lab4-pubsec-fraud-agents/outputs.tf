output "claims_table_statement_id" {
  description = "Flink statement ID for claims table"
  value       = confluent_flink_statement.claims_table.id
}

output "claims_table_name" {
  description = "Name of the claims table"
  value       = "claims"
}

output "lab4_deployment_status" {
  description = "Lab4 deployment status"
  value       = "Lab4 FEMA Fraud Detection infrastructure deployed successfully"
}
