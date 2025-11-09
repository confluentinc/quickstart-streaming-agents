---
document_id: flink_operate-and-deploy_deploy-flink-sql-statement_chunk_5
source_file: flink_operate-and-deploy_deploy-flink-sql-statement.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/deploy-flink-sql-statement.html
title: Deploy a Flink SQL Statement in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 5
---

in your Confluent Cloud organization.

## Step 5. Deploy a Flink SQL statement¶

To use Flink, you must create a Flink compute pool. A compute pool represents a set of compute resources that are bound to a region and are used to run your Flink SQL statements. For more information, see [Compute Pools](../concepts/compute-pools.html#flink-sql-compute-pools).

  1. Create a new compute pool by adding the following code to “main.tf”.

         # Create a Flink compute pool to execute a Flink SQL statement.
         resource "confluent_flink_compute_pool" "my_compute_pool" {
           display_name = "my_compute_pool"
           cloud        = local.cloud
           region       = local.region
           max_cfu      = 10

           environment {
             id = confluent_environment.my_env.id
           }

           depends_on = [
             confluent_environment.my_env
           ]
         }

  2. Create a Flink-specific API key, which is required for submitting statements to Confluent Cloud, by adding the following code to “main.tf”.

         # Create a Flink-specific API key that will be used to submit statements.
         data "confluent_flink_region" "my_flink_region" {
           cloud  = local.cloud
           region = local.region
         }

         resource "confluent_api_key" "my_flink_api_key" {
           display_name = "my_flink_api_key"

           owner {
             id          = confluent_service_account.my_service_account.id
             api_version = confluent_service_account.my_service_account.api_version
             kind        = confluent_service_account.my_service_account.kind
           }

           managed_resource {
             id          = data.confluent_flink_region.my_flink_region.id
             api_version = data.confluent_flink_region.my_flink_region.api_version
             kind        = data.confluent_flink_region.my_flink_region.kind

             environment {
               id = confluent_environment.my_env.id
             }
           }

           depends_on = [
             confluent_environment.my_env,
             confluent_service_account.my_service_account
           ]
         }

  3. Deploy a Flink SQL statement on Confluent Cloud by adding the following code to “main.tf”.

The statement consumes data from `examples.marketplace.orders`, aggregates in 1 minute windows and ingests the filtered data into `sink_topic`.

Because you’re using a Service Account, the statement runs in Confluent Cloud continuously until manually stopped.

         # Deploy a Flink SQL statement to Confluent Cloud.
         resource "confluent_flink_statement" "my_flink_statement" {
           organization {
             id = data.confluent_organization.my_org.id
           }

           environment {
             id = confluent_environment.my_env.id
           }

           compute_pool {
             id = confluent_flink_compute_pool.my_compute_pool.id
           }

           principal {
             id = confluent_service_account.my_service_account.id
           }

           # This SQL reads data from source_topic, filters it, and ingests the filtered data into sink_topic.
           statement = <<EOT
             CREATE TABLE my_sink_topic AS
             SELECT
               window_start,
               window_end,
               SUM(price) AS total_revenue,
               COUNT(*) AS cnt
             FROM
             TABLE(TUMBLE(TABLE `examples`.`marketplace`.`orders`, DESCRIPTOR($rowtime), INTERVAL '1' MINUTE))
             GROUP BY window_start, window_end;
             EOT

           properties = {
             "sql.current-catalog"  = confluent_environment.my_env.display_name
             "sql.current-database" = confluent_kafka_cluster.my_kafka_cluster.display_name
           }

           rest_endpoint = data.confluent_flink_region.my_flink_region.rest_endpoint

           credentials {
             key    = confluent_api_key.my_flink_api_key.id
             secret = confluent_api_key.my_flink_api_key.secret
           }

           depends_on = [
             confluent_api_key.my_flink_api_key,
             confluent_flink_compute_pool.my_compute_pool,
             confluent_kafka_cluster.my_kafka_cluster
           ]
         }

  4. Push all changes to your repository and check the **Actions** page to ensure the workflow runs successfully.

  5. In Confluent Cloud Console, verify that the statement has been deployed and that `sink_topic` is receiving the data.

You have a fully functioning CI/CD pipeline with Confluent Cloud and Terraform. This pipeline enables automating the deployment and management of your infrastructure, making it more efficient and scalable.
