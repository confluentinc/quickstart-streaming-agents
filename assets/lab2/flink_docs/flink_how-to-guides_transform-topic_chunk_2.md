---
document_id: flink_how-to-guides_transform-topic_chunk_2
source_file: flink_how-to-guides_transform-topic.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/transform-topic.html
title: Transform a Topic with Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

Region_3 Zee 1677260922 female Region_5

## Step 2: Apply the Transform Topic action¶

In the previous step, you created a Flink table and populated it with a few rows. In this step, you apply the Transform Topic action to create a transformed output table.

  1. Navigate to the [Environments](https://confluent.cloud/environments) page, and in the navigation menu, click **Data portal**.

  2. In the **Data portal** page, click the dropdown menu and select the environment for your workspace.

  3. In the **Recently created** section, find your **users** topic and click it to open the details pane.

  4. In the details pane, click **Actions** , and in the Actions list, click **Transform topic** to open the dialog.

  5. In the **Action details** section, set up the transformation.

     * **user_id** field: select the **Key field** checkbox.
     * **registertime** field: enter _registration_time_.
     * **Partition count** property: enter _3_.
     * **Serialization format** property: select **JSON Schema**.

By default, the name of the transformed topic is `users_transform`, and you can change this as desired.

  6. In the **Runtime configuration** section, configure how the transformation statement will run.

     * (Optional) Select the Flink compute pool to run the embedding query. The current compute pool is selected as the default.

     * (Optional) Select **Run with a service account** for production jobs. The service account you select must have the EnvironmentAdmin role to create topics, schemas, and run Flink statements.

     * (Optional) Select **Show SQL** to view the Flink statement that does the transformation work.

Your Flink SQL should resemble:

           CREATE TABLE `your-env`.`your-cluster`.`users_transform`
           DISTRIBUTED BY HASH (
               `user_id`
           ) INTO 3 BUCKETS WITH (
               'value.format' = 'json-registry',
               'key.format' = 'json-registry'
           ) AS SELECT
               `user_id`,
               `registertime` as `registration_time`,
               `gender`,
               `regionid`
           FROM `your-env`.`your-cluster`.`users`;

  7. Click **Confirm and run** to run the transformation statement.

A **Summary** page displays the result of the job submission, showing the statement name and other details.

## Step 3: Inspect the transformed topic¶

  1. In the **Summary** page, click the **Output topic** link for the **users_transform** topic, and in the topic’s details pane, click **Query** to open a Flink workspace.

  2. Run the following statement to view the rows in the **users_transform** table. Note the renamed **registration_time** column.

         SELECT * FROM `users_transform`;

Click **Stop** to end the statement.

  3. Run the following command to confirm that the `user_id` field in the transformed table is a key field.

         DESCRIBE `users_source_transform`;

Your output should resemble:

         +-------------------+-----------+----------+------------+
         |    Column Name    | Data Type | Nullable |   Extras   |
         +-------------------+-----------+----------+------------+
         | user_id           | STRING    | NULL     | BUCKET KEY |
         | registration_time | BIGINT    | NULL     |            |
         | gender            | STRING    | NULL     |            |
         | regionid          | STRING    | NULL     |            |
         +-------------------+-----------+----------+------------+

  4. Run the following command to confirm the serialization format and partition count on the transformed topic.

         SHOW CREATE TABLE `users_source_transform`;

Your output should resemble:

         CREATE TABLE `your-env`.`your-cluster`.`users_transform` (
           `user_id` VARCHAR(2147483647),
           `registration_time` BIGINT,
           `gender` VARCHAR(2147483647),
           `regionid` VARCHAR(2147483647)
         )
         DISTRIBUTED BY HASH(`user_id`) INTO 3 BUCKETS
         WITH (
           'changelog.mode' = 'append',
           'connector' = 'confluent',
           'kafka.cleanup-policy' = 'delete',
           'kafka.max-message-size' = '2097164 bytes',
           'kafka.retention.size' = '0 bytes',
           'kafka.retention.time' = '7 d',
           'key.format' = 'json-registry',
           'scan.bounded.mode' = 'unbounded',
           'scan.startup.mode' = 'earliest-offset',
           'value.format' = 'json-registry'
         )
