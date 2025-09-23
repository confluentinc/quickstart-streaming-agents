---
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/convert-serialization-format.html
title: Convert the Serialization Format of a Topic with Confluent Cloud for Apache Flink
hierarchy: ['how-to-guides', 'convert-serialization-format.html']
scraped_date: 2025-09-05T13:47:30.920646
---

# Convert the Serialization Format of a Topic with Confluent Cloud for Apache Flink¶

This guide shows how to use Confluent Cloud for Apache Flink® to transform a topic serialized in Avro Schema Registry format to a topic serialized in JSON Schema Registry format. The Apache Flink® type system is used to map the datatypes between the these two different wire formats.

This topic shows the following steps:

  * Step 1: Create a streaming data source using Avro
  * Step 2: Inspect the source data
  * Step 3: Convert the serialization format to JSON
  * Step 4: Delete the long-running statement

## Prerequisites¶

You need the following prerequisites to use Confluent Cloud for Apache Flink.

  * Access to Confluent Cloud.

  * The organization ID, environment ID, and compute pool ID for your organization.

  * The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, reach out to your OrganizationAdmin or EnvironmentAdmin.

  * The Confluent CLI. To use the Flink SQL shell, update to the latest version of the Confluent CLI by running the following command:

        confluent update --yes

If you used homebrew to install the Confluent CLI, update the CLI by using the `brew upgrade` command, instead of `confluent update`.

For more information, see [Confluent CLI](https://docs.confluent.io/confluent-cli/current/overview.html).

## Step 1: Create a streaming data source using Avro¶

The streaming data for this topic is produced by a [Datagen Source Connector](../../connectors/cc-datagen-source.html#cc-datagen-source) that’s configured with the **Gaming player activity** template. It produces mock data to an Apache Kafka® topic named `gaming_player_activity_source`. The connector produces player score records that are randomly generated from the [gaming_player_activity.avro](https://github.com/confluentinc/kafka-connect-datagen/blob/master/src/main/resources/gaming_player_activity.avro) file.

  1. Log in to the Confluent Cloud Console and navigate to the environment that hosts Flink SQL.

  2. In the navigation menu, select **Connectors**.

The **Connectors** page opens.

  3. Click **Add Connector**

The **Connector Plugins** page opens.

  4. In the **Search connectors** box, enter “datagen”.

[](../../_images/cloud-search-datagen.png)
  5. From the search results, click the **Sample Data** connector. If the **Launch Sample Data** dialog opens, click **Advanced settings**.

  6. In the **Add Datagen Source Connector** page, complete the following steps.

1: Create a topic2: Kafka credentials3: Configuration4: Sizing5: Review and Launch

  1. Click **Add new topic** , and in the **Topic name** field, enter “gaming_player_activity_source”.

  2. Click **Create with defaults**. Confluent Cloud creates the Kafka topic that the connector produces records to.

Note

When you’re in a Confluent Cloud environment that has Flink SQL, a SQL table is created automatically when you create a Kafka topic.

  3. In the **Topics** list, select **gaming_player_activity_source** and click **Continue**.

  1. Select the way you want to provide **Kafka Cluster credentials**. You can choose one of the following options:

     * **My account** : This setting allows your connector to globally access everything that you have access to. With a user account, the connector uses an API key and secret to access the Kafka cluster. This option is not recommended for production.
     * **Service account** : This setting limits the access for your connector by using a [service account](../../connectors/service-account.html#s3-cloud-service-account). This option is recommended for production.
     * **Use an existing API key** : This setting allows you to specify an API key and a secret pair. You can use an existing pair or create a new one. This method is not recommended for production environments.

Note

Freight clusters support only service accounts for Kafka authentication.

  2. In the **Kafka credentials** pane, leave **Global access** selected, and click **Generate API key & download**. This creates an API key and secret that allows the connector to access your cluster, and downloads the key and secret to your computer.

  3. Click **Continue**.

  1. On the **Configuration** page, select **AVRO** for the output record value format.

Selecting **AVRO** configures the connector to associate a schema with the `gaming_player_activity_source` topic and register it with Schema Registry.

  2. In the **Select a template** section, click **Show more options** , click the **Gaming player activity** tile.

  3. Click **Show advanced configurations** , and in the **Max interval between messages (ms)** textbox, enter **10**.

  4. Click **Continue**.

  * For **Connector sizing** , leave the slider at the default of **1** task and click **Continue**.

  1. In the **Connector name** box, Select the text and replace it with “gaming_player_activity_source_connector”.

  2. Click **Continue** to start the connector.

The status of your new connector reads **Provisioning** , which lasts for a few seconds. When the status of the new connector changes from **Provisioning** to **Running** , you have a producer sending an event stream to your topic in the Confluent Cloud cluster.

## Step 2: Inspect the source data¶

  1. In Cloud Console, navigate to your environment’s [Flink workspace](../get-started/quick-start-cloud-console.html#flink-sql-quick-start-create-workspace), or using the Confluent CLI, open a [SQL shell](../get-started/quick-start-shell.html#flink-sql-quick-start-shell) from the Confluent CLI.

If you use the workspace in Cloud Console, set the **Use catalog** and **Use database** controls to your environment and Kafka cluster.

If you use the Flink SQL shell, run the following statements to set the current environment and Kafka cluster.

         USE CATALOG <your-environment-name>;
         USE DATABASE <your-cluster-name>;

  2. Run the following statement to see the data flowing into the `gaming_player_activity_source` table.

         SELECT * FROM gaming_player_activity_source;

Your output should resemble:

         key         player_id game_room_id points coordinates
         x'31303833' 1083      4634         85     [30,39]
         x'31303731' 1071      3406         432    [91,61]
         x'31303239' 1029      3078         359    [63,04]
         x'31303736' 1076      4501         256    [73,12]
         x'31303437' 1047      3644         375    [24,55]
         ...

  3. If you add `$rowtime` to the `SELECT` statement, you can see the Kafka timestamp for each record.

         SELECT $rowtime, * FROM gaming_player_activity_source;

Your output should resemble:

         $rowtime                key         player_id game_room_id points coordinates
         2023-11-08 14:27:27.647 x'31303838' 1088      4198         22     [02,86]
         2023-11-08 14:27:27.695 x'31303638' 1068      1446         132    [80,86]
         2023-11-08 14:27:27.729 x'31303536' 1056      4839         125    [35,74]
         2023-11-08 14:27:27.732 x'31303530' 1050      4517         221    [11,69]
         2023-11-08 14:27:27.746 x'31303438' 1048      3337         339    [91,10]
         ...

## Step 3: Convert the serialization format to JSON¶

  1. Run the following statement to confirm that the current format of this table is Avro Schema Registry.

         SHOW CREATE TABLE gaming_player_activity_source;

Your output should resemble:

         +-------------------------------------------------------------+
         |                      SHOW CREATE TABLE                      |
         +-------------------------------------------------------------+
         | CREATE TABLE `env`.`clus`.`gaming_player_activity_source` ( |
         |   `key` VARBINARY(2147483647),                              |
         |   `player_id` INT NOT NULL,                                 |
         |   `game_room_id` INT NOT NULL,                              |
         |   `points` INT NOT NULL,                                    |
         |   `coordinates` VARCHAR(2147483647) NOT NULL,               |
         | ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS                 |
         | WITH (                                                      |
         |   'changelog.mode' = 'append',                              |
         |   'connector' = 'confluent',                                |
         |   'kafka.cleanup-policy' = 'delete',                        |
         |   'kafka.max-message-size' = '2097164 bytes',               |
         |   'kafka.partitions' = '6',                                 |
         |   'kafka.retention.size' = '0 bytes',                       |
         |   'kafka.retention.time' = '604800000 ms',                  |
         |   'key.format' = 'raw',                                     |
         |   'scan.bounded.mode' = 'unbounded',                        |
         |   'scan.startup.mode' = 'earliest-offset',                  |
         |   'value.format' = 'avro-registry'                          |
         | )                                                           |
         |                                                             |
         +-------------------------------------------------------------+

  2. Run the following statement to create a second table that has the same schema but is configured with the value format set to JSON with Schema Registry. The key format is unchanged.

         CREATE TABLE gaming_player_activity_source_json (
           `key` VARBINARY(2147483647),
           `player_id` INT NOT NULL,
           `game_room_id` INT NOT NULL,
           `points` INT NOT NULL,
           `coordinates` VARCHAR(2147483647) NOT NULL
         ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS
         WITH (
           'value.format' = 'json-registry',
           'key.format' = 'raw'
         );

This statement creates a corresponding Kafka topic and Schema Registry subject named `gaming_player_activity_source_json-value` for the value.

  3. Run the following SQL to create a long-running statement that continuously transforms `gaming_player_activity_source` records into `gaming_player_activity_source_json` records.

         INSERT INTO gaming_player_activity_source_json
         SELECT
           *
         FROM gaming_player_activity_source;

  4. Run the following statement to confirm that records are continuously appended to the target table:

         SELECT * FROM gaming_player_activity_source_json;

Your output should resemble:

         key         player_id game_room_id points coordinates
         x'31303834' 1084      3583         211    [51,93]
         x'31303037' 1007      2268         55     [98,72]
         x'31303230' 1020      1625         431    [01,08]
         x'31303934' 1094      4760         43     [80,71]
         x'31303539' 1059      2822         390    [33,74]
         ...

Tip

Run the `SHOW JOBS;` statement to see the phase of statements that you’ve started in your workspace or Flink SQL shell.

  5. Run the following statement to confirm that the format of the `gaming_player_activity_source_json` table is JSON.

         SHOW CREATE TABLE gaming_player_activity_source_json;

Your output should resemble:

         +--------------------------------------------------------------------------------------+
         |                                  SHOW CREATE TABLE                                   |
         +--------------------------------------------------------------------------------------+
         | CREATE TABLE `jim-flink-test-env`.`cluster_0`.`gaming_player_activity_source_json` ( |
         |   `key` VARBINARY(2147483647),                                                       |
         |   `player_id` INT NOT NULL,                                                          |
         |   `game_room_id` INT NOT NULL,                                                       |
         |   `points` INT NOT NULL,                                                             |
         |   `coordinates` VARCHAR(2147483647) NOT NULL                                         |
         | ) DISTRIBUTED BY HASH(`key`) INTO 6 BUCKETS                                          |
         | WITH (                                                                               |
         |   'changelog.mode' = 'append',                                                       |
         |   'connector' = 'confluent',                                                         |
         |   'kafka.cleanup-policy' = 'delete',                                                 |
         |   'kafka.max-message-size' = '2097164 bytes',                                        |
         |   'kafka.partitions' = '6',                                                          |
         |   'kafka.retention.size' = '0 bytes',                                                |
         |   'kafka.retention.time' = '604800000 ms',                                           |
         |   'key.format' = 'raw',                                                              |
         |   'scan.bounded.mode' = 'unbounded',                                                 |
         |   'scan.startup.mode' = 'earliest-offset',                                           |
         |   'value.format' = 'json-registry'                                                   |
         | )                                                                                    |
         |                                                                                      |
         +--------------------------------------------------------------------------------------+

## Step 4: Delete the long-running statement¶

Your INSERT INTO statement is converting records in the Avro format to the JSON format continuously. When you’re done with this guide, free resources in your compute pool by deleting the long-running statement.

  1. In Cloud Console, navigate to the **Flink** page in your environment and click **Flink statements**.
  2. In the statements list, find the statement that has a status of **Running**.
  3. In the **Actions** column, click **…** and select **Delete statement**.
  4. In the **Confirm statement deletion** dialog, copy and paste the statement name and click **Confirm**.
