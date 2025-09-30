---
document_id: flink_how-to-guides_create-udf_chunk_5
source_file: flink_how-to-guides_create-udf.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/create-udf.html
title: Create a User-Defined Function with Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 7
---

see [Create a Flink artifact](../operate-and-deploy/flink-rest-api.html#flink-rest-api-create-artifact).

## Step 3: Register the UDF¶

UDFs are registered inside a Flink database, which means that you must specify the Confluent Cloud environment (Flink catalog) and Kafka cluster (Flink database) where you want to use the UDF.

You can use the Confluent Cloud Console, the Confluent CLI, the Confluent Terraform provider, or the REST API to register your UDF.

Confluent Cloud ConsoleConfluent CLITerraformREST API

  1. In the Flink page, click **Compute pools**.
  2. In the tile for the compute pool where you want to run the UDF, click **Open SQL workspace**.
  3. In the **Use catalog** dropdown, select the environment where you want to run the UDF.
  4. In the **Use database** dropdown, select Kafka cluster that you want to run the UDF.

  1. Run the following command to start the Flink shell.

         confluent flink shell --environment ${ENV_ID} --compute-pool ${COMPUTE_POOL_ID}

  2. Run the following statements to specify the catalog and database.

         -- Specify your catalog. This example uses the default.
         USE CATALOG default;

Your output should resemble:

         +---------------------+---------+
         |         Key         |  Value  |
         +---------------------+---------+
         | sql.current-catalog | default |
         +---------------------+---------+

Specify the database you want to use, for example, `cluster_0`.

         -- Specify your database. This example uses cluster_0.
         USE cluster_0;

Your output should resemble:

         +----------------------+-----------+
         |         Key          |   Value   |
         +----------------------+-----------+
         | sql.current-database | cluster_0 |
         +----------------------+-----------+

You can register a previously uploaded UDF by using the Confluent Terraform provider. For more information, see [confluent_flink_artifact Resource](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_flink_artifact)

You can register a UDF by sending a POST request to the [Create Artifact endpoint](/cloud/current/api.html#tag/Flink-Artifacts-\(artifactv1\)/operation/createArtifactV1FlinkArtifact). For more information, see [Create a Flink artifact](../operate-and-deploy/flink-rest-api.html#flink-rest-api-create-artifact).

* In Cloud Console or the Confluent CLI, run the [CREATE FUNCTION](../reference/statements/create-function.html#flink-sql-create-function) statement to register your UDF in the current catalog and database. Substitute your UDF’s value for `<artifact-id>`.

        CREATE FUNCTION is_smaller
          AS 'com.example.my.TShirtSizingIsSmaller'
          USING JAR 'confluent-artifact://<artifact-id>';

Your output should resemble:

        Function 'is_smaller' created.

## Step 4: Use the UDF in a Flink SQL query¶

Once it is registered, your UDF is available to use in queries.

  1. Run the following statement to view the UDFs in the current database.

         SHOW USER FUNCTIONS;

Your output should resemble:

         +---------------+
         | function name |
         +---------------+
         | is_smaller    |
         +---------------+

  2. Run the following statement to create a `sizes` table.

         CREATE TABLE sizes (
           `size_1` STRING,
           `size_2` STRING
         );

  3. Run the following statement to populate the `sizes` table with values.

         INSERT INTO sizes VALUES
           ('XL', 'L'),
           ('small', 'L'),
           ('M', 'L'),
           ('XXL', 'XL');

  4. Run the following statement to view the rows in the `sizes` table.

         SELECT * FROM sizes;

Your output should resemble:

         size_1 size_2
         XL     L
         small  L
         M      L
         XXL    XL

  5. Run the following statement to execute the `is_smaller` function on the data in the `sizes` table.

         SELECT size_1, size_2, is_smaller (size_1, size_2)
           AS is_smaller
           FROM sizes;

Your output should resemble:

         size_1 size_2 is_smaller
         XL     L      FALSE
         small  L      TRUE
         M      L      TRUE
         XXL    XL     FALSE

## Step 5: Implement UDF logging (optional)¶

If you want to log UDF status messages to a Kafka topic, follow the steps in [Enable UDF Logging](enable-udf-logging.html#flink-sql-enable-udf-logging).
