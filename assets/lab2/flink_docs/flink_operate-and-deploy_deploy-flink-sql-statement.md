---
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/deploy-flink-sql-statement.html
title: Deploy a Flink SQL Statement in Confluent Cloud for Apache Flink
hierarchy: ['operate-and-deploy', 'deploy-flink-sql-statement.html']
scraped_date: 2025-09-05T13:46:37.909960
---

# Deploy a Flink SQL Statement Using CI/CD and Confluent Cloud for Apache Flink¶

[GitHub Actions](https://docs.github.com/en/actions) is a powerful feature on GitHub that enables automating your software development workflows. If your source code is stored in a GitHub repository, you can easily create a custom workflow in GitHub Actions to build, test, package, release, or deploy any code project.

This topic shows how to create a CI/CD workflow that deploys an Apache Flink® SQL statement programmatically on Confluent Cloud for Apache Flink by using Hashicorp Terraform and GitHub Actions. With the steps in this topic, you can streamline your development process.

In this walkthrough, you perform the following steps:

  * Step 1: Set up a Terraform Cloud workspace
  * Step 2: Set up a repository and secrets in GitHub
  * Step 3. Create a CI/CD workflow in GitHub Actions
  * Step 4. Deploy resources in Confluent Cloud
  * Step 5. Deploy a Flink SQL statement

## Prerequisites¶

You need the following prerequisites to complete this tutorial:

  * [Access to Confluent Cloud](https://confluent.cloud/)
  * A [GitHub account](https://github.com/) to set up a repository and create the CI/CD workflow
  * A [Terraform Cloud](https://app.terraform.io/) account

## Step 1: Set up a Terraform Cloud workspace¶

You need a Terraform Cloud account to follow this tutorial. If you don’t have one yet, create an account for free at [Terraform Cloud](https://app.terraform.io/public/signup/account). With a Terraform Cloud account, you can manage your infrastructure-as-code and collaborate with your team.

### Create a workspace¶

  1. If you have created a new Terraform Cloud account and the Getting Started page is displayed, click **Create a new organization** , and in the **Organization name** textbox, enter “flink_ccloud”. Click **Create organization**.

Otherwise, from the Terraform Cloud homepage, click **New** to create a new workspace.

  2. In the **Create a new workspace page** , click the **API-Driven Workflow** tile, and in the **Workspace name** textbox, enter “cicd_flink_ccloud”.

  3. Click **Create** to create the workspace.

### Create a Terraform Cloud API token¶

By creating an API token, you can authenticate securely with Terraform Cloud and integrate it with GitHub Actions. Save the token in a secure location, and don’t share it with anyone.

  1. At the top of the navigation menu, click your user icon and select **User settings**.

  2. In the navigation menu, click **Tokens** , and in the **Tokens** page, click **Create an API token**.

  3. Give your token a meaningful description, like “github_actions”, and click **Generate token**.

Your token appears in the **Tokens** list.

  4. Save the API token in a secure location. It won’t be displayed again.

## Step 2: Set up a repository and secrets in GitHub¶

To create an Action Secret in GitHub for securely storing the API token from Terraform Cloud, follow these steps.

  1. Log in to your GitHub account and create a new repository.
  2. In the **Create a new repository** page, use the **Owner** dropdown to choose an owner, and give the repository a unique name, like “<your-name-flink-ccloud>”.
  3. Click **Create**.
  4. In the repository details page, click **Settings**.
  5. In the navigation menu, click **Secrets and variables** , and in the context menu, select **Actions** to open the **Actions secrets and variables** page.
  6. Click **New repository secret**.
  7. In the **New secret** page, enter the following settings.
     * In the **Name** textbox, enter “TF_API_TOKEN”.
     * In the **Secret** textbox, enter the API token value that you saved from the previous Terraform Cloud step.
  8. Click **Add secret** to save the Action Secret.

By creating an Action Secret for the API token, you can use it securely in your CI/CD pipelines, such as in GitHub Actions. Keep the secret safe, and don’t share it with anyone who shouldn’t have access to it.

## Step 3. Create a CI/CD workflow in GitHub Actions¶

The following steps show how to create an Action Workflow for automating the deployment of a Flink SQL statement on Confluent Cloud using Terraform.

  1. In the toolbar at the top of the screen, click **Actions**.

The **Get started with GitHub Actions** page opens.

  2. Click **set up a workflow yourself - >**. If you already have a workflow defined, click **new workflow** , and then click **set up a workflow yourself - >**.

  3. Copy the following YAML into the editor.

This YAML file defines a workflow that runs when changes are pushed to the main branch of your repository. It includes a job named “terraform_flink_ccloud_tutorial” that runs on the latest version of Ubuntu. The job includes these steps:

     * Check out the code
     * Set up Terraform
     * Log in to Terraform Cloud using the API token stored in the Action Secret
     * Initialize Terraform
     * Apply the Terraform configuration to deploy changes to your Confluent Cloud account
    
    on:
     push:
        branches:
        - main
    
    jobs:
     terraform_flink_ccloud_tutorial:
        name: "terraform_flink_ccloud_tutorial"
        runs-on: ubuntu-latest
        steps:
          - name: Checkout
            uses: actions/checkout@v4
    
          - name: Setup Terraform
            uses: hashicorp/setup-terraform@v3
            with:
             cli_config_credentials_token: ${{ secrets.TF_API_TOKEN }}
    
          - name: Terraform Init
            id: init
            run: terraform init
    
          - name: Terraform Validate
            id: validate
            run: terraform validate -no-color
    
          - name: Terraform Plan
            id: plan
            run: terraform plan
            env:
              TF_VAR_confluent_cloud_api_key: ${{ secrets.CONFLUENT_CLOUD_API_KEY }}
              TF_VAR_confluent_cloud_api_secret: ${{ secrets.CONFLUENT_CLOUD_API_SECRET }}
    
          - name: Terraform Apply
            id: apply
            run: terraform apply -auto-approve
            env:
              TF_VAR_confluent_cloud_api_key: ${{ secrets.CONFLUENT_CLOUD_API_KEY }}
              TF_VAR_confluent_cloud_api_secret: ${{ secrets.CONFLUENT_CLOUD_API_SECRET }}

  4. Click **Commit changes** , and in the dialog, enter a description in the **Extended description** textbox, for example, “CI/CD workflow to automate deployment on Confluent Cloud”.

  5. Click **Commit changes**.

The file `main.yml` is created in the `.github/workflows` directory in your repository.

With this Action Workflow, your deployment of Flink SQL statements on Confluent Cloud is now automatic.

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

## Related content¶

  * [Get Started with Confluent Cloud for Apache Flink](../get-started/overview.html#flink-sql-get-started)
  * [Compute Pools](../concepts/compute-pools.html#flink-sql-compute-pools)
