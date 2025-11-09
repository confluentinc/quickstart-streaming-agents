---
document_id: flink_operate-and-deploy_deploy-flink-sql-statement_chunk_4
source_file: flink_operate-and-deploy_deploy-flink-sql-statement.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/deploy-flink-sql-statement.html
title: Deploy a Flink SQL Statement in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 5
---

The role binding gives the Service Account the necessary permissions to create topics, Flink statements, and other resources. In production, you may want to assign a less privileged role than OrganizationAdmin.

         # Create a new Service Account. This will used during Kafka API key creation and Flink SQL statement submission.
         resource "confluent_service_account" "my_service_account" {
           display_name = "my_service_account"
         }

         data "confluent_organization" "my_org" {}

         # Assign the OrganizationAdmin role binding to the above Service Account.
         # This will give the Service Account the necessary permissions to create topics, Flink statements, etc.
         # In production, you may want to assign a less privileged role.
         resource "confluent_role_binding" "my_org_admin_role_binding" {
           principal   = "User:${confluent_service_account.my_service_account.id}"
           role_name   = "OrganizationAdmin"
           crn_pattern = data.confluent_organization.my_org.resource_name

           depends_on = [
             confluent_service_account.my_service_account
           ]
         }

  4. Push all changes to your repository and check the **Actions** page to ensure the workflow runs successfully.

At this point, you should have a new environment, an Apache Kafka® cluster, and a Stream Governance package provisioned in your Confluent Cloud organization.
