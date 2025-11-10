---
document_id: flink_operate-and-deploy_deploy-flink-sql-statement_chunk_2
source_file: flink_operate-and-deploy_deploy-flink-sql-statement.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/deploy-flink-sql-statement.html
title: Deploy a Flink SQL Statement in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 5
---

shouldn’t have access to it.

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
