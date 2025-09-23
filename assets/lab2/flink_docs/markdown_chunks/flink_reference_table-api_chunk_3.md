---
document_id: flink_reference_table-api_chunk_3
source_file: flink_reference_table-api.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/table-api.html
title: Table API on Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 5
---

java -jar my-table-program.jar \
      --cloud aws \
      --region us-east-1 \
      --flink-api-key key \
      --flink-api-secret secret \
      --organization-id b0b21724-4586-4a07-b787-d0bb5aacbf87 \
      --environment-id env-z3y2x1 \
      --compute-pool-id lfcp-8m03rm

Access the configuration settings from the command-line arguments by using the `ConfluentSettings.fromArgs` method:

JavaPython

    public static void main(String[] args) {
      ConfluentSettings settings = ConfluentSettings.fromArgs(args);
    }

    from pyflink.table.confluent import ConfluentSettings

    settings = ConfluentSettings.from_global_variables()

### Code¶

You can assign the configuration settings in code by using the builder provided with the `ConfluentSettings` class:

JavaPython

    ConfluentSettings settings = ConfluentSettings.newBuilder()
      .setCloud("aws")
      .setRegion("us-east-1")
      .setFlinkApiKey("key")
      .setFlinkApiSecret("secret")
      .setOrganizationId("b0b21724-4586-4a07-b787-d0bb5aacbf87")
      .setEnvironmentId("env-z3y2x1")
      .setComputePoolId("lfcp-8m03rm")
      .build();

    from pyflink.table.confluent import ConfluentSettings

    settings = ConfluentSettings.new_builder() \
      .set_cloud("aws") \
      .set_region("us-east-1") \
      .set_flink_api_key("key") \
      .set_flink_api_secret("secret") \
      .set_organization_id("b0b21724-4586-4a07-b787-d0bb5aacbf87") \
      .set_environment_id("env-z3y2x1") \
      .set_compute_pool_id("lfcp-8m03rm") \
      .build()

### Environment variables¶

Set the following environment variables to provide configuration settings.

    export CLOUD_PROVIDER="aws"
    export CLOUD_REGION="us-east-1"
    export FLINK_API_KEY="key"
    export FLINK_API_SECRET="secret"
    export ORG_ID="b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="env-z3y2x1"
    export COMPUTE_POOL_ID="lfcp-8m03rm"

    java -jar my-table-program.jar

In code, call:

JavaPython

    ConfluentSettings settings = ConfluentSettings.fromGlobalVariables();

    from pyflink.table.confluent import ConfluentSettings

    settings = ConfluentSettings.from_global_variables()
