# Lab1 AWS Outputs
output "lab_name" {
  value = "lab1-tool-calling-aws"
}

# Core infrastructure outputs (pass-through from remote state)
output "confluent_environment_id" {
  value = data.terraform_remote_state.core.outputs.confluent_environment_id
}

output "confluent_kafka_cluster_id" {
  value = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_id
}

output "confluent_kafka_bootstrap_endpoint" {
  value = data.terraform_remote_state.core.outputs.confluent_kafka_cluster_bootstrap_endpoint
}

output "confluent_schema_registry_id" {
  value = data.terraform_remote_state.core.outputs.confluent_schema_registry_id
}

output "confluent_schema_registry_endpoint" {
  value = data.terraform_remote_state.core.outputs.confluent_schema_registry_rest_endpoint
}

output "confluent_flink_compute_pool_id" {
  value = data.terraform_remote_state.core.outputs.confluent_flink_compute_pool_id
}

# Lab-specific outputs
output "lab1_commands_file" {
  value = local_file.mcp_commands.filename
}

output "lab_suffix" {
  value = random_id.lab_suffix.hex
}
