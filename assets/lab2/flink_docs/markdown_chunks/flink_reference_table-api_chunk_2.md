---
document_id: flink_reference_table-api_chunk_2
source_file: flink_reference_table-api.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/table-api.html
title: Table API on Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 5
---

## Configure the plugin¶

The plugin requires a set of configuration options for establishing a connection to Confluent Cloud. The following configuration options are supported.

Property key | Command-line argument | Environment variable | Required | Notes
---|---|---|---|---
client.catalog-cache |  |  | No | Expiration time for catalog objects, for example, `'5 min'`. The default is `'1 min'`. `'0'` disables caching.
client.cloud | –cloud | CLOUD_PROVIDER | Yes | Confluent identifier for a cloud provider. Valid values are `aws`, `azure`, and `gcp`.
client.compute-pool | –compute-pool | COMPUTE_POOL_ID | Yes | ID of the compute pool, for example, `lfcp-8m03rm`
client.context | –context |  | No | A name for the current Table API session, for example, my_table_program.
client.environment | –environment | ENV_ID | Yes | ID of the environment, for example, `env-z3y2x1`.
client.flink-api-key | –flink-api-key | FLINK_API_KEY | Yes | API key for Flink access. For more information, see [Generate an API Key](../operate-and-deploy/generate-api-key-for-flink.html#flink-generate-api-key).
client.flink-api-secret | –flink-api-secret | FLINK_API_SECRET | Yes | API secret for Flink access. For more information, see [Generate an API Key](../operate-and-deploy/generate-api-key-for-flink.html#flink-generate-api-key).
client.organization | –organization | ORG_ID | Yes | ID of the organization, for example, `b0b21724-4586-4a07-b787-d0bb5aacbf87`.
client.principal-id | –principal | PRINCIPAL_ID | No | Principal that runs submitted statements, for example, `sa-23kgz4` for a service account.
client.region | –region | CLOUD_REGION | Yes | Confluent identifier for a cloud provider’s region, for example, `us-east-1`. For available regions, see [Supported Regions](../overview.html#ccloud-flink-overview-everywhere) or run `confluent flink region list`.
client.rest-endpoint | –rest-endpoint | REST_ENDPOINT | No | URL to the REST endpoint, for example, `proxyto.confluent.cloud`.
client.statement-name | –statement-name |  | No | Unique name for statement submission. By default, generated using a UUID.

### `ConfluentSettings` class¶

The `ConfluentSettings` class provides configuration options from various sources, so you can combine external input, code, and environment variables to set up your applications.

The following precedence order applies to configuration sources, from highest to lowest:

* CLI arguments or properties file
* Code
* Environment variables

The following code example shows a `TableEnvironment` that’s configured by a combination of command-line arguments and code.

JavaPython

    public static void main(String[] args) {
      // Args might set cloud, region, org, env, and compute pool.
      // Environment variables might pass key and secret.

      // Code sets the session name and SQL-specific options.
      ConfluentSettings settings = ConfluentSettings.newBuilder(args)
       .setContextName("MyTableProgram")
       .setOption("sql.local-time-zone", "UTC")
       .build();

      TableEnvironment env = TableEnvironment.create(settings);
    }

    from pyflink.table.confluent import ConfluentSettings
    from pyflink.table import TableEnvironment

    def run():
      # Properties file might set cloud, region, org, env, and compute pool.
      # Environment variables might pass key and secret.

      # Code sets the session name and SQL-specific options.
      settings = ConfluentSettings.new_builder_from_file(...) \
       .set_context_name("MyTableProgram") \
       .set_option("sql.local-time-zone", "UTC") \
       .build()

      env = TableEnvironment.create(settings)

### Properties file¶

You can store options in a `cloud.properties` file and reference the file in code.

    # Cloud region
    client.cloud=aws
    client.region=eu-west-1

    # Access & compute resources
    client.flink-api-key=XXXXXXXXXXXXXXXX
    client.flink-api-secret=XxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx
    client.organization-id=00000000-0000-0000-0000-000000000000
    client.environment-id=env-xxxxx
    client.compute-pool-id=lfcp-xxxxxxxxxx

Reference the `cloud.properties` file in code:

JavaPython

    // Arbitrary file location in file system
    ConfluentSettings settings = ConfluentSettings.fromPropertiesFile("/path/to/cloud.properties");

    // Part of the JAR package (in src/main/resources)
    ConfluentSettings settings = ConfluentSettings.fromPropertiesResource("/cloud.properties");

    from pyflink.table.confluent import ConfluentSettings

    # Arbitrary file location in file system
    settings = ConfluentSettings.from_file("/path/to/cloud.properties")

### Command-line arguments¶

You can pass the configuration settings as command-line options when you run your application’s jar:
