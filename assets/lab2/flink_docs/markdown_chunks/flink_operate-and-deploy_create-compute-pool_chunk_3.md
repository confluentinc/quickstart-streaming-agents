---
document_id: flink_operate-and-deploy_create-compute-pool_chunk_3
source_file: flink_operate-and-deploy_create-compute-pool.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/create-compute-pool.html
title: Manage Flink Compute Pools in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 7
---

Your output should resemble:

Response from a request to create a compute pool

    {
        "api_version": "fcpm/v2",
        "id": "lfcp-6g7h8i",
        "kind": "ComputePool",
        "metadata": {
            "created_at": "2024-02-27T22:44:27.18964Z",
            "resource_name": "crn://confluent.cloud/organization=b0b21724-4586-4a07-b787-d0bb5aacbf87/environment=env-z3y2x1/flink-region=aws.us-east-1/compute-pool=lfcp-6g7h8i",
            "self": "https://api.confluent.cloud/fcpm/v2/compute-pools/lfcp-6g7h8i",
            "updated_at": "2024-02-27T22:44:27.18964Z"
        },
        "spec": {
            "cloud": "AWS",
            "display_name": "my-compute-pool",
            "environment": {
                "id": "env-z3y2x1",
                "related": "https://api.confluent.cloud/fcpm/v2/compute-pools/lfcp-6g7h8i",
                "resource_name": "crn://confluent.cloud/organization=b0b21724-4586-4a07-b787-d0bb5aacbf87/environment=env-z3y2x1"
            },
            "http_endpoint": "https://flink.us-east-1.aws.confluent.cloud/sql/v1/organizations/b0b21724-4586-4a07-b787-d0bb5aacbf87/environments/env-z3y2x1",
            "max_cfu": 5,
            "region": "us-east-1"
        },
        "status": {
            "current_cfu": 0,
            "phase": "PROVISIONING"
        }
    }

To create a compute pool by using the Confluent Terraform provider, use the [confluent_flink_compute_pool](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_compute_pool) resource.

  1. Configure your Terraform file. Provide your Confluent Cloud API key and secret.

         terraform {
           required_providers {
             confluent = {
               source = "confluentinc/confluent"
               version = "2.38.0"
             }
           }
         }

         provider "confluent" {
           cloud_api_key    = var.confluent_cloud_api_key    # optionally use CONFLUENT_CLOUD_API_KEY env var
           cloud_api_secret = var.confluent_cloud_api_secret # optionally use CONFLUENT_CLOUD_API_SECRET env var
         }

  2. Define the environment where the compute pool will be created.

         resource "confluent_environment" "development" {
           display_name = "Development"
           lifecycle {
             prevent_destroy = true
           }
         }

  3. Define the `confluent_flink_compute_pool` resource with the required parameters, like `display_name`, `cloud`, `region`, `max_cfu`, and the environment ID.

         resource "confluent_flink_compute_pool" "main" {
           display_name = "standard_compute_pool"
           cloud        = "AWS"
           region       = "us-east-1"
           max_cfu      = 5

           environment {
             id = confluent_environment.development.id
           }
         }

  4. Run the `terraform apply` command to create the resources.

         terraform apply

  5. If you need to import an existing compute pool, use the `terraform import` command.

         export CONFLUENT_CLOUD_API_KEY="<cloud_api_key>"
         export CONFLUENT_CLOUD_API_SECRET="<cloud_api_secret>"
         terraform import confluent_flink_compute_pool.main <your-environment-id>/<compute-pool-id>

For more information, see [confluent_flink_compute_pool resource](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_compute_pool).
