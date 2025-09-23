---
source_url: https://docs.confluent.io/cloud/current/flink/reference/table-api.html
title: Table API on Confluent Cloud for Apache Flink
hierarchy: ['reference', 'table-api.html']
scraped_date: 2025-09-05T13:45:29.196917
---

# Table API on Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports programming applications with the Table API in Java and Python. Confluent provides a plugin for running applications that use the Table API on Confluent Cloud.

The Table API enables a programmatic way of developing, testing, and submitting Flink pipelines for processing data streams. Streams can be finite or infinite, with insert-only or changelog data. Changelog data enables handling Change Data Capture (CDC) events.

To use the Table API, you work with tables that change over time, a concept inspired by relational databases. A Table program is a declarative and structured graph of transformations. The Table API is inspired by SQL and complements it with additional tools for manipulating real-time data. You can use both Flink SQL and the Table API in your applications.

A table program has these characteristics:

* Runs in a regular `main()` method (Java)
* Uses Flink APIs
* Communicates with Confluent Cloud by using REST requests, for example, [Statements endpoint](/cloud/current/api.html#tag/Statements-\(sqlv1\)/operation/createSqlv1Statement).

For a list of Table API functions supported by Confluent Cloud for Apache Flink, see [Table API functions](functions/table-api-functions.html#flink-table-api-functions).

For a list of Table API limitations in Confluent Cloud for Apache Flink, see Known limitations.

Use the Confluent for VS Code extension to generate a new Flink Table API project that interacts with your Confluent Cloud resources. This option is ideal if you’re learning about the Table API.

For more information see [Confluent for VS Code for Confluent Cloud](../../client-apps/vs-code-extension.html#cc-vscode-extension).

Note

The Flink Table API is available for preview.

A Preview feature is a Confluent Cloud component that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing preview releases of the Preview features at any time in Confluent’s’ sole discretion.

Comments, questions, and suggestions related to the Table API are encouraged and can be submitted through the [established channels](../get-help.html#ccloud-flink-help).

## Add the Table API to an existing Java project¶

To add the Table API to an existing project, include the following dependencies in the `<dependencies>` section of your pom.xml file.

    <!-- Apache Flink dependencies -->
    <dependency>
       <groupId>org.apache.flink</groupId>
       <artifactId>flink-table-api-java</artifactId>
       <version>${flink.version}</version>
    </dependency>

    <!-- Confluent Flink Table API Java plugin -->
    <dependency>
       <groupId>io.confluent.flink</groupId>
       <artifactId>confluent-flink-table-api-java-plugin</artifactId>
       <version>${confluent-plugin.version}</version>
    </dependency>

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

## Confluent utilities¶

The `ConfluentTools` class provides more methods that you can use for developing and testing Table API programs.

### `ConfluentTools.collectChangelog` and `ConfluentTools.printChangelog`¶

Runs the specified table transformations on Confluent Cloud and returns the results locally as a list of changelog rows or prints to the console in a table style.

These methods run `table.execute().collect()` and consume a fixed number of rows from the returned iterator.

These methods can work on both finite and infinite input tables. If the pipeline is potentially unbounded, they stop fetching after the desired number of rows has been reached.

JavaPython

    // On a Table object
    Table table = env.from("examples.marketplace.customers");
    List<Row> rows = ConfluentTools.collectMaterialized(table, 100);
    ConfluentTools.printMaterialized(table, 100);

    // On a TableResult object
    TableResult tableResult = env.executeSql("SELECT * FROM examples.marketplace.customers");
    List<Row> rows = ConfluentTools.collectMaterialized(tableResult, 100);
    ConfluentTools.printMaterialized(tableResult, 100);

    // For finite (i.e. bounded) tables
    ConfluentTools.collectMaterialized(table);
    ConfluentTools.printMaterialized(table);

    from pyflink.table.confluent import ConfluentSettings, ConfluentTools
    from pyflink.table import TableEnvironment

    settings = ConfluentSettings.from_global_variables()
    env = TableEnvironment.create(settings)
    # On a Table object
    table = env.from_path("examples.marketplace.customers")
    rows = ConfluentTools.collect_changelog_limit(table, 100)
    ConfluentTools.print_changelog_limit(table, 100)

    # On a TableResult object
    tableResult = env.execute_sql("SELECT * FROM examples.marketplace.customers")
    rows = ConfluentTools.collect_changelog_limit(tableResult, 100)
    ConfluentTools.print_changelog_limit(tableResult, 100)

    # For finite (i.e. bounded) tables
    ConfluentTools.collect_changelog(table)
    ConfluentTools.print_changelog(table)

### `ConfluentTools.collect_materialized` and `ConfluentTools.print_materialized`¶

Runs the specified table transformations on Confluent Cloud and returns the results locally as a materialized changelog. Changes are applied to an in-memory table and returned as a list of insert-only rows or printed to the console in a table style.

These methods run `table.execute().collect()` and consume a fixed number of rows from the returned iterator.

These methods can work on both finite and infinite input tables. If the pipeline is potentially unbounded, they stop fetching after the desired number of rows have been reached.

JavaPython

    // On a Table object
    Table table = env.from("examples.marketplace.customers");
    List<Row> rows = ConfluentTools.collectMaterialized(table, 100);
    ConfluentTools.printMaterialized(table, 100);

    // On a TableResult object
    TableResult tableResult = env.executeSql("SELECT * FROM examples.marketplace.customers");
    List<Row> rows = ConfluentTools.collectMaterialized(tableResult, 100);
    ConfluentTools.printMaterialized(tableResult, 100);

    // For finite (i.e. bounded) tables
    ConfluentTools.collectMaterialized(table);
    ConfluentTools.printMaterialized(table);

    from pyflink.table.confluent import ConfluentSettings, ConfluentTools
    from pyflink.table import TableEnvironment

    settings = ConfluentSettings.from_global_variables()
    env = TableEnvironment.create(settings)
    # On Table object
    table = env.from_path("examples.marketplace.customers")
    rows = ConfluentTools.collect_materialized_limit(table, 100)
    ConfluentTools.print_materialized_limit(table, 100)

    # On TableResult object
    tableResult = env.execute_sql("SELECT * FROM examples.marketplace.customers")
    rows = ConfluentTools.collect_materialized_limit(tableResult, 100)
    ConfluentTools.print_materialized_limit(tableResult, 100)

    # For finite (i.e. bounded) tables
    ConfluentTools.collect_materialized(table)
    ConfluentTools.print_materialized(table)

### `ConfluentTools.getStatementName` and `ConfluentTools.stopStatement`¶

Additional lifecycle methods for controlling statements on Confluent Cloud after they have been submitted.

JavaPython

    // On TableResult object
    TableResult tableResult = env.executeSql("SELECT * FROM examples.marketplace.customers");
    String statementName = ConfluentTools.getStatementName(tableResult);
    ConfluentTools.stopStatement(tableResult);

    // Based on statement name
    ConfluentTools.stopStatement(env, "table-api-2024-03-21-150457-36e0dbb2e366-sql");

    # On TableResult object
    table_result = env.execute_sql("SELECT * FROM examples.marketplace.customers")
    statement_name = ConfluentTools.get_statement_name(table_result)
    ConfluentTools.stop_statement(table_result)

    # Based on statement name
    ConfluentTools.stop_statement_by_name(env, "table-api-2024-03-21-150457-36e0dbb2e366-sql")

### Confluent table descriptor¶

A table descriptor for creating tables located in Confluent Cloud programmatically.

Compared to the regular Flink class, the `ConfluentTableDescriptor` class adds support for Confluent’s system columns and convenience methods for working with Confluent tables.

The `for_managed()` method corresponds to `TableDescriptor.for_connector("confluent")`.

JavaPython

    TableDescriptor descriptor = ConfluentTableDescriptor.forManaged()
      .schema(
        Schema.newBuilder()
          .column("i", DataTypes.INT())
          .column("s", DataTypes.INT())
          .watermark("$rowtime", $("$rowtime").minus(lit(5).seconds())) // Access $rowtime system column
          .build())
      .build();

    env.createTable("t1", descriptor);

    from pyflink.table.confluent import ConfluentTableDescriptor
    from pyflink.table import Schema, DataTypes
    from pyflink.table.expressions import col, lit

    descriptor = ConfluentTableDescriptor.for_managed() \
      .schema(
         Schema.new_builder()
           .column("i", DataTypes.INT())
           .column("s", DataTypes.INT())
           .watermark("$rowtime", col("$rowtime").minus(lit(5).seconds)) # Access $rowtime system column
           .build()) \
      .build()

    env.createTable("t1", descriptor)

## Known limitations¶

The Table API plugin is in Open Preview stage.

### Unsupported by Table API Plugin¶

The following features are not supported.

* Temporary catalog objects (including tables, views, functions)
* Custom modules
* Custom catalogs
* User-defined functions (including system functions)
* Anonymous, inline objects (including functions, data types)
* CompiledPlan features are not supported
* Batch mode
* Restrictions from Confluent Cloud
  * custom connectors/formats
  * processing time operations
  * structured data types
  * many configuration options
  * limited SQL syntax
  * batch execution mode

### Issues in Apache Flink¶

* Both catalog and database must be set, or identifiers must be fully qualified. A mixture of setting a current catalog and using two-part identifiers can cause errors.
* String concatenation with `.plus` causes errors. Instead, use `Expressions.concat`.
* Selecting `.rowtime` in windows causes errors.
* Using `.limit()` can cause errors.
