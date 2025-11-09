---
document_id: flink_how-to-guides_convert-serialization-format_chunk_2
source_file: flink_how-to-guides_convert-serialization-format.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/convert-serialization-format.html
title: Convert the Serialization Format of a Topic with Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 5
---

more information, see [Confluent CLI](https://docs.confluent.io/confluent-cli/current/overview.html).

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
