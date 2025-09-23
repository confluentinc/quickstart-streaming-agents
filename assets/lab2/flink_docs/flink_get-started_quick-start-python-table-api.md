---
source_url: https://docs.confluent.io/cloud/current/flink/get-started/quick-start-python-table-api.html
title: Python Table API Quick Start on Confluent Cloud for Apache Flink
hierarchy: ['get-started', 'quick-start-python-table-api.html']
scraped_date: 2025-09-05T13:46:01.267486
---

# Python Table API Quick Start on Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports programming applications with the Table API. Confluent provides a plugin for running applications that use the Table API on Confluent Cloud.

For more information, see [Table API](../reference/table-api.html#flink-table-api).

For code examples, see [Python Examples for Table API on Confluent Cloud](https://github.com/confluentinc/flink-table-api-python-examples).

Note

The Flink Table API is available for preview.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

Comments, questions, and suggestions related to the Table API are encouraged and can be submitted through the [established channels](../get-help.html#ccloud-flink-help).

## Prerequisites¶

  * Access to Confluent Cloud
  * A [compute pool](../operate-and-deploy/create-compute-pool.html#flink-sql-manage-compute-pool) in Confluent Cloud
  * A Apache Kafka® [cluster](../../clusters/create-cluster.html#cloud-create-cluster), if you want to run examples that store data in Kafka
  * Java version 11 or later
  * Environment variables as defined in [Environment variables](../reference/table-api.html#flink-table-api-environment-variables).
  * The [uv](https://docs.astral.sh/uv/) package manager to manage your Python versions and environments. Only Python versions 3.9 to 3.12 are supported.

To run Table API and Flink SQL programs, you must generate an API key that’s specific to the Flink environment. Also, you need Confluent Cloud account details, like your organization and environment identifiers.

  * **Flink API Key:** Follow the steps in [Generate a Flink API key](../operate-and-deploy/flink-rest-api.html#flink-rest-api-generate-api-key). For convenience, assign your Flink key and secret to the FLINK_API_KEY and FLINK_API_SECRET environment variables.
  * **Organization ID:** The identifier your organization, for example, `b0b421724-4586-4a07-b787-d0bb5aacbf87`. For convenience, assign your organization identifier to the ORG_ID environment variable.
  * **Environment ID:** The identifier of the environment where your Flink SQL statements run, for example, `env-z3y2x1`. For convenience, assign your environment identifier to the ENV_ID environment variable.
  * **Cloud provider name:** The name of the cloud provider where your cluster runs, for example, `aws`. To see the available providers, run the `confluent flink region list` command. For convenience, assign your cloud provider to the CLOUD_PROVIDER environment variable.
  * **Cloud region:** The name of the region where your cluster runs, for example, `us-east-1`. To see the available regions, run the `confluent flink region list` command. For convenience, assign your cloud region to the CLOUD_REGION environment variable.

    export CLOUD_PROVIDER="aws"
    export CLOUD_REGION="us-east-1"
    export FLINK_API_KEY="<your-flink-api-key>"
    export FLINK_API_SECRET="<your-flink-api-secret>"
    export ORG_ID="<your-organization-id>"
    export ENV_ID="<your-environment-id>"
    export COMPUTE_POOL_ID="<your-compute-pool-id>"

Note

The Flink Python API communicates with a Java process. You must have at least Java 11 installed. Check that your `JAVA_HOME` environment variable is set correctly. Checking only `java -version` might not be sufficient.

    echo $JAVA_HOME

If required, install openjdk and export the `JAVA_HOME` variable:

    brew install openjdk && export JAVA_HOME=$(/usr/libexec/java_home) && echo $JAVA_HOME

## Setup your environment and run a Table API program¶

Use [uv](https://docs.astral.sh/uv/) to create a virtual environment that contains all required dependencies and project files.

  1. Use one of the following commands to install uv.

         curl -LsSf https://astral.sh/uv/install.sh | sh
         # or
         brew install uv
         # or
         pip install uv

  2. Create a new virtual environment.

         uv venv --python 3.11

  3. Copy the following code into a file named `hello_table_api.py`.

         # /// script
         # requires-python = ">=3.9,<3.12"
         # dependencies = [
         #   "confluent-flink-table-api-python-plugin>=1.20.52",
         # ]
         # ///

         from pyflink.table.confluent import ConfluentSettings, ConfluentTools
         from pyflink.table import TableEnvironment, Row
         from pyflink.table.expressions import col, row

         def run():
             # Set up the connection to Confluent Cloud
             settings = ConfluentSettings.from_global_variables()
             env = TableEnvironment.create(settings)

             # Run your first Flink statement in Table API
             env.from_elements([row("Hello world!")]).execute().print()

             # Or use SQL
             env.sql_query("SELECT 'Hello world!'").execute().print()

             # Structure your code with Table objects - the main ingredient of Table API.
             table = env.from_path("examples.marketplace.clicks") \
                 .filter(col("user_agent").like("Mozilla%")) \
                 .select(col("click_id"), col("user_id"))

             table.print_schema()
             print(table.explain())

             # Use the provided tools to test on a subset of the streaming data
             expected = ConfluentTools.collect_materialized_limit(table, 50)
             actual = [Row(42, 500)]
             if expected != actual:
                 print("Results don't match!")

         if __name__ == "__main__":
             run()

  4. Run the following command to execute the Table API program from the directory where you created `hello_table_api.py`.

         uv run hello_table_api.py
