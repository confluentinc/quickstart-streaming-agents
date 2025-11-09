---
document_id: flink_operate-and-deploy_deploy-flink-sql-statement_chunk_1
source_file: flink_operate-and-deploy_deploy-flink-sql-statement.md
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/deploy-flink-sql-statement.html
title: Deploy a Flink SQL Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 5
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
