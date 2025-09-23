---
document_id: flink_how-to-guides_create-udf_chunk_7
source_file: flink_how-to-guides_create-udf.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/create-udf.html
title: Create a User-Defined Function with Confluent Cloud for Apache Flink
chunk_index: 7
total_chunks: 7
---

Your output should resemble: com/example/my/SplitFunction.class

## Step 2: Upload the UDTF jar as a Flink artifact¶

Confluent Cloud ConsoleConfluent CLI

  1. Log in to Confluent Cloud and navigate to your Flink workspace.
  2. Navigate to the environment where you want to run the UDF.
  3. Click **Flink** , in the Flink page, click **Artifacts**.
  4. Click **Upload artifact** to open the upload pane.
  5. In the **Cloud provider** dropdown, select **AWS** , and in the **Region** dropdown, select the cloud region.
  6. Click **Upload your JAR file** and navigate to the location of your JAR file, which in the current example is `target/udf_example-1.0.jar`.
  7. When your JAR file is uploaded, it appears in the **Artifacts** list. In the list, click the row for your UDF artifact to open the details pane.

  1. Log in to Confluent Cloud.

         confluent login --organization-id ${ORG_ID} --prompt

  2. Run the following command to upload the jar to Confluent Cloud.

         confluent flink artifact create udf_table_example \
         --artifact-file target/udf_example-1.0.jar \
         --cloud ${CLOUD_PROVIDER} \
         --region ${CLOUD_REGION} \
         --environment ${ENV_ID}

Your output should resemble:

         +--------------------+-------------------+
         | ID                 | cfa-l5xp82        |
         | Name               | udf_table_example |
         | Version            | ver-0x37m2        |
         | Cloud              | aws               |
         | Region             | us-east-1         |
         | Environment        | env-z3q9rd        |
         | Content Format     | JAR               |
         | Description        |                   |
         | Documentation Link |                   |
         +--------------------+-------------------+

Note the artifact ID and version of your UDTF, which in this example are `cfa-l5xp82` and `ver-0x37m2`, because you use them later to register the UDTF in Flink SQL and to manage it.

## Step 3: Register the UDTF¶

  1. In the Flink shell or the Cloud Console, specify the catalog and database (environment and cluster) where you want to use the UDTF, as you did in the previous section.

  2. Run the [CREATE FUNCTION](../reference/statements/create-function.html#flink-sql-create-function) statement to register your UDTF in the current catalog and database. Substitute your UDTF’s value for `<artifact-id>`.

         CREATE FUNCTION split_string
           AS 'com.example.my.SplitFunction'
           USING JAR 'confluent-artifact://<artifact-id>';

Your output should resemble:

         Function 'split_string' created.

## Step 4: Use the UDTF in a Flink SQL query¶

Once it is registered, your UDTF is available to use in queries.

  1. Run the following statement to view the UDFs in the current database.

         SHOW USER FUNCTIONS;

Your output should resemble:

         +---------------+
         | Function Name |
         +---------------+
         | split_string  |
         +---------------+

  2. Run the following statement to execute the `split_string` function.

         SELECT * FROM (VALUES 'A;B', 'C;D;E;F') as T(f), LATERAL TABLE(split_string(f, ';'))

Your output should resemble:

         f        word
         A;B      A
         A;B      B
         C;D;E;F  C
         C;D;E;F  D
         C;D;E;F  E
         C;D;E;F  F

  3. When you’re done with the example UDTF, drop the function and delete the JAR artifact as you did in Step 6: Delete the UDF.
