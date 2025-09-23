---
document_id: flink_reference_statements_create-connection_chunk_2
source_file: flink_reference_statements_create-connection.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-connection.html
title: SQL CREATE CONNECTION Statement in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

string is converted to bytes.

## Examples¶

    -- example AzureML connection with API key
    CREATE CONNECTION `my-azureml-connection`
      WITH (
        'type' = 'AZUREML',
        'endpoint' = 'https://myworkspace.myregion.inference.ml.azure.com/test',
        'api_key' = '<your-api-key>'
      );

    -- example AzureML connection with comment
    CREATE CONNECTION `my-azureml-connection`
      COMMENT 'Connection Comment'
      WITH (
        'type' = 'AZUREML',
        'endpoint' = 'https://myworkspace.myregion.inference.ml.azure.com/test',
        'api_key' = '<your-api-key>'
      );

    -- example Couchbase connection with basic authorization
    CREATE CONNECTION `my-couchbase-connection`
      WITH (
        'type' = 'COUCHBASE',
        'endpoint' = 'couchbases://my-cluster.cloud.couchbase.com',
        'username' = '<user-name>',
        'password' = '<password>'
      );

    -- example Bedrock connection with AWS authentication
    CREATE CONNECTION `my-bedrock-connection`
      WITH (
        'type' = 'BEDROCK',
        'endpoint' = 'https://bedrock-runtime.us-east-1.amazonaws.com/model/my-model/invoke',
        'aws-access-key' = '<aws-access-key-id>',
        'aws-secret-key' = '<aws-secret-access-key>',
        'aws-session-token' = '<aws-session-token>'
      );

### MongoDB external table¶

    -- Create a MongoDB connection with basic authorization.
    CREATE CONNECTION `my-mongodb-connection`
      WITH (
        'type' = 'MONGODB',
        'endpoint' = 'mongodb+srv://myCluster.mongodb.net/myDatabase',
        'username' = '<atlas-user-name>',
        'password' = '<atlas-password>'
      );

    -- Use the MongoDB connection to create a MongoDB external table.
    CREATE TABLE mongodb_movies_full_text_search (
        title STRING,
        plot STRING
    ) WITH (
        'connector' = 'mongodb',
        'mongodb.connection' = 'my-mongodb-connection',
        'mongodb.database' = 'sample_mflix',
        'mongodb.collection' = 'movies',
        'mongodb.index' = 'default'
    );

### Confluent JDBC¶

    -- Create a Confluent JDBC connection with basic authorization.
    CREATE CONNECTION `jdbc-postgres-connection`
      WITH (
        'type' = 'confluent_jdbc',
        'endpoint' = 'jdbc:postgresql://my.example.com:5432/mydatabase',
        'username' = '<user-name>',
        'password' = '<password>');

    -- Use the Confluent JDBC connection to create a table.
    CREATE TABLE jdbc_postgres (
        show_id STRING,
        type STRING,
        title STRING,
        cast_members STRING,
        country STRING,
        date_added DATE,
        release_year INT,
        rating STRING,
        duration STRING,
        listed_in STRING,
        description STRING
    ) WITH (
        'connector' = 'confluent-jdbc',
        'confluent-jdbc.connection' = 'jdbc-postgres-connection',
        'confluent-jdbc.table-name' = 'netflix_shows'
    );
