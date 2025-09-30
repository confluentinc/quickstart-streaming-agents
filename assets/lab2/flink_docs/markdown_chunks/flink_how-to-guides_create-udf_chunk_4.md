---
document_id: flink_how-to-guides_create-udf_chunk_4
source_file: flink_how-to-guides_create-udf.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/create-udf.html
title: Create a User-Defined Function with Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 7
---

output should resemble: com/example/my/TShirtSizingIsSmaller$Size.class com/example/my/TShirtSizingIsSmaller.class

## Step 2: Upload the jar as a Flink artifact¶

You can use the Confluent Cloud Console, the Confluent CLI, or the REST API to upload your UDF.

Confluent Cloud ConsoleConfluent CLIREST API

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

         confluent flink artifact create udf_example \
         --artifact-file target/udf_example-1.0.jar \
         --cloud ${CLOUD_PROVIDER} \
         --region ${CLOUD_REGION} \
         --environment ${ENV_ID}

Your output should resemble:

         +--------------------+-------------+
         | ID                 | cfa-ldxmro  |
         | Name               | udf_example |
         | Version            | ver-81vxm5  |
         | Cloud              | aws         |
         | Region             | us-east-1   |
         | Environment        | env-z3q9rd  |
         | Content Format     | JAR         |
         | Description        |             |
         | Documentation Link |             |
         +--------------------+-------------+

Note the artifact ID and version of your UDTF, which in this example are `cfa-ldxmro` and `ver-81vxm5`, because you use them later to register the UDTF in Flink SQL and to manage it.

  3. Run the following command to view all of the available UDFs.

         confluent flink artifact list \
         --cloud ${CLOUD_PROVIDER} \
         --region ${CLOUD_REGION}

Your output should resemble:

         ID     |    Name     | Cloud |  Region   | Environment
         -------------+-------------+-------+-----------+--------------
         cfa-ldxmro | udf_example | AWS   | us-east-1 | env-z3q9rd

  4. Run the following command to view the details of your UDF. You can use the artifact ID from the previous step or the artifact name to specify your UDF.

         # use the artifact ID
         confluent flink artifact describe \
         cfa-ldxmro \
         --cloud ${CLOUD_PROVIDER} \
         --region ${CLOUD_REGION}

         # use the artifact name
         confluent flink artifact describe \
         udf_example \
         --cloud ${CLOUD_PROVIDER} \
         --region ${CLOUD_REGION}

Your output should resemble:

         +--------------------+-------------+
         | ID                 | cfa-ldxmro  |
         | Name               | udf_example |
         | Version            | ver-81vxm5  |
         | Cloud              | aws         |
         | Region             | us-east-1   |
         | Environment        | env-z3q9rd  |
         | Content Format     | JAR         |
         | Description        |             |
         | Documentation Link |             |
         +--------------------+-------------+

You can upload your JAR file by requesting a presigned upload URL, then uploading the file by using the presigned URL information. For more information, see [Create a Flink artifact](../operate-and-deploy/flink-rest-api.html#flink-rest-api-create-artifact).
