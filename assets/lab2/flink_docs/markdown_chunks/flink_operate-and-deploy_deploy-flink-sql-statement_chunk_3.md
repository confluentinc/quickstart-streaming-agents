---
document_id: flink_operate-and-deploy_deploy-flink-sql-statement_chunk_3
source_file: flink_operate-and-deploy_deploy-flink-sql-statement.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/deploy-flink-sql-statement.html
title: Deploy a Flink SQL Statement in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 5
---

Confluent Cloud is now automatic.

## Step 4. Deploy resources in Confluent Cloud¶

In this section, you deploy a Flink SQL statement programmatically to Confluent Cloud that runs continuously until stopped manually.

  1. In VS Code or another IDE, clone your repository and create a new file in the root named “main.tf” with the following code.

Replace the organization and workspace names with your Terraform Cloud organization name and workspace names from Step 1.

         terraform {
           cloud {
             organization = "<your-terraform-org-name>"

             workspaces {
               name = "cicd_flink_ccloud"
             }
           }

           required_providers {
             confluent = {
               source  = "confluentinc/confluent"
               version = "2.2.0"
             }
           }
         }

  2. Commit and push the changes to the repository.

The CI/CD workflow that you created previously runs automatically. Verify that it’s running by navigating to the **Actions** section in your repository and clicking on the latest workflow run.

### Create a Confluent Cloud API key¶

To access Confluent Cloud securely, you must have a Confluent Cloud API key. After you generate an API key, you store securely it in your GitHub repository’s **Secrets and variables** page, the same way that you stored the Terraform API token.

  1. Follow the instructions [here](../../security/authenticate/workload-identities/service-accounts/api-keys/manage-api-keys.html#cloud-cloud-api-keys) to create a new API key for Confluent Cloud, and on the <https://confluent.cloud/settings/api-keys> page, select the **Cloud resource management** tile for the API key’s resource scope. You will use this API key to communicate securely with Confluent Cloud.

  2. Return to the **Settings** page for your GitHub repository, and in the navigation menu, click **Secrets and variables**. In the context menu, select **Actions** to open the **Actions secrets and variables** page.

  3. Click **New repository secret**.

  4. In the **New secret** page, enter the following settings.

     * In the **Name** textbox, enter “CONFLUENT_CLOUD_API_KEY”.
     * In the **Secret** textbox, enter the Cloud API key.
  5. Click **Add secret** to save the Cloud API key as an Action Secret.

  6. Click **New repository secret** and repeat the previous steps for the Cloud API secret. Name the secret “CONFLUENT_CLOUD_API_SECRET”.

  7. Your **Repository secrets** list should resemble the following:

[](../../_images/flink-terraform-github-actions-secrets.png)

### Deploy resources¶

In this section, you add resources to your Terraform configuration file and provision them when the GitHub Action runs.

  1. In your repository, create a new file named “variables.tf” with the following code.

         variable "confluent_cloud_api_key" {
           description = "Confluent Cloud API Key"
           type        = string
         }

         variable "confluent_cloud_api_secret" {
           description = "Confluent Cloud API Secret"
           type        = string
           sensitive   = true
         }

  2. In the “main.tf” file, add the following code.

This code references the Cloud API key and secret you added in the previous steps and creates a new environment and Kafka cluster for your organization. Optionally, you can choose to use an existing environment.

         locals {
           cloud  = "AWS"
           region = "us-east-2"
         }

         provider "confluent" {
           cloud_api_key    = var.confluent_cloud_api_key
           cloud_api_secret = var.confluent_cloud_api_secret
         }

         # Create a new environment.
         resource "confluent_environment" "my_env" {
           display_name = "my_env"

           stream_governance {
             package = "ESSENTIALS"
           }
         }

         # Create a new Kafka cluster.
         resource "confluent_kafka_cluster" "my_kafka_cluster" {
           display_name = "my_kafka_cluster"
           availability = "SINGLE_ZONE"
           cloud        = local.cloud
           region       = local.region
           basic {}

           environment {
             id = confluent_environment.my_env.id
           }

           depends_on = [
             confluent_environment.my_env
           ]
         }

         # Access the Stream Governance Essentials package to the environment.
         data "confluent_schema_registry_cluster" "my_sr_cluster" {
           environment {
             id = confluent_environment.my_env.id
           }
         }

  3. Create a Service Account and provide a role binding by adding the following code to “main.tf”.
