---
source_url: https://docs.confluent.io/platform/current/flink/configure/catalog.html
title: Manage Flink SQL Catalogs for Confluent Manager for Apache Flink
hierarchy: ['platform', 'configure', 'catalog.html']
scraped_date: 2025-09-05T13:52:26.503216
---

# Manage Flink SQL Catalogs for Confluent Manager for Apache Flink¶

Flink SQL uses the concept of _Catalogs_ to connect to external storage systems.

Important

Flink SQL support in is available as an open preview. A Preview feature is a feature that is being introduced to gain early feedback from developers. Preview features can be used for evaluation and non-production testing purposes or to provide feedback to Confluent. The warranty, SLA, and Support Services provisions of your agreement with Confluent do not apply to Preview features. Confluent may discontinue providing releases of Preview features at any time at Confluent’s’ sole discretion. Comments, questions, and suggestions related to preview features are encouraged and can be submitted to your account representative.

A core concept of SQL are tables. Tables store data, represented as rows. Users can query and modify the rows of a table by running SQL queries and Data Definition Language (DDL) statements. Most database systems store, manage, and process table data internally. In contrast, Flink SQL is solely a processing engine and not a data store. Flink accesses external data storage systems to read and write data.

Catalogs bridge the gap between the SQL engine and external data storage systems, enabling users to access and manipulate data stored in various formats and locations.

Confluent Manager for Apache Flink® features built-in Kafka Catalogs to connect to Kafka and Schema Registry. A Kafka Catalog exposes Kafka topics as tables and derives their schema from Schema Registry.

You create a CATALOG that references the Kafka cluster (and optionally other clusters) and a Schema Registry instance. Each Kafka cluster is represented as a DATABASE and each topic of a cluster as a TABLE in that database.

Catalogs are accessible from all CMF environments, but there are ways to restrict access.

## Create a Catalog¶

There are several steps to create a Catalog in CMF. You configure the Catalog with a resource definition that contains the connection properties for the Kafka and Schema Registry clients. You then create a Secret that contains sensitive connection properties, such as credentials. Finally, you create an EnvironmentSecretMapping that maps the Secret to the Catalog’s connectionSecretId. This enables you to use different connection properties for each environment.

### Configure Kafka clusters and Schema Registry¶

A Kafka Catalog references a Schema Registry instance and one or more Kafka clusters. This assumes the schemas of all topics of all its configured Kafka clusters are managed by the configured Schema Registry instance. The catalog is configured with connection properties for the Kafka and Schema Registry clients. These properties are used to a) fetch the metadata that is needed during query translation and b) read data from and write data to topics during query execution. A Kafka Catalog is configured with the following resource definition

    {
       "apiVersion": "cmf.confluent.io/v1",
       "kind": "KafkaCatalog",
       "metadata": {
         "name": "kafka-cat"
       },
       "spec": {
         "srInstance": {
           "connectionConfig": {
             "schema.registry.url": "http://schemaregistry:8081"
           },
           "connectionSecretId": "sr-secret-id"
         },
         "kafkaClusters": [
           {
             "databaseName": "kafka-1",
             "connectionConfig": {
               "bootstrap.servers": "kafka-1:9092"
             },
             "connectionSecretId": "kafka-1-secret-id"
           },
           {
             "databaseName": "kafka-2",
             "connectionConfig": {
               "bootstrap.servers": "kafka-2:9092"
             }
           }
         ]
       }
     }

### Configure connection credentials¶

All Kafka and Schema Registry client properties specified in the `connectionConfig` field are used by all environments to translate and execute statements and are not handled as sensitive data. Sensitive connection properties, such as access credentials or properties that should only be used for statements in certain environments, must be stored in _Secrets_. A Secret is a set of properties (key-value pairs) that is concatenated with the public `connectionConfig` of a Kafka cluster or Schema Registry instance.

With Secrets and SecretMappings, you can configure different connection properties (including credentials) for Kafka clusters and Schema Registry instances per environment. Within an environment, CMF uses the same properties to translate and execute all statements, regardless of the user who submits the statement.

## Create a secret¶

First, create a Secret. A Secret is configured with the following resource definition:

    {
    "apiVersion": "cmf.confluent.io/v1",
    "kind": "Secret",
    "metadata": {
      "name": "kafka-1-secret"
    },
    "spec": {
      "data": {
      "sasl.mechanism": "PLAIN",
      "security.protocol": "SASL_PLAINTEXT",
      "sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"test\" password=\"testPw\";"
      }
    }
    }

The Secret’s name is `kafka-1-secret` and its `data` field contains a set of properties that are dynamically added to the `connectionConfig` once the secret is mapped to the `connectionSecretId` of a Kafka cluster.

The Secret is created via the REST API:

    curl -v -H "Content-Type: application/json" \
    -X POST http://cmf:8080/cmf/api/v1/secrets -d@/<path-to>/secret.json

## Map a secret to a ConnectionSecretId¶

An environment can map one secret to each unique `connectionSecretId` defined in a catalog. The mapping is established with an `EnvironmentSecretMapping` resource. The following JSON shows an example.

    {
    "apiVersion": "cmf.confluent.io/v1",
    "kind": "EnvironmentSecretMapping",
    "metadata": {
      "name": "kafka-1-secret-id"
    },
    "spec": {
      "secretName": "kafka-1-secret"
    }
    }

The name of the resource (in this example, `kafka-1-secret-id`) is identical to the `connectionSecretId` specified in the catalog definition. The `secretName`, `kafka-1-secret` is identical to the name of the Secret. The mapping is created for an environment `env-1` with the following REST request:

    curl -v -H "Content-Type: application/json" \
    -X POST http://cmf:8080/cmf/api/v1/environments/env-1/secret-mappings \
    -d@/<path-to>/kafka-1-mapping.json

With this mapping, statements created in environment `env-1` will use the following properties to configure the Kafka clients when accessing topics of database/cluster `kafka-1`:

    // from the plain "connectionConfig"
    "bootstrap.servers": "kafka-1:9092",
    // from the "kafka-1-secret"
    "sasl.mechanism": "PLAIN",
    "security.protocol": "SASL_PLAINTEXT",
    "sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"test\" password=\"testPw\";"

### Environments without Secret Mappings¶

If an environment does not have a mapping for a `connectionSecretId`, the corresponding catalog (for a Schema Registry `connectionSecretId`) or database (for a Kafka cluster `connectionSecretId`) will not be accessible from this environment. This indicates an incomplete configuration that would result in connection failures of the Schema Registry or Kafka clients.

This mechanism also allows restricting the access of environments to certain catalogs or databases.

## Delete a Catalog¶

A catalog can be deleted via the Confluent CLI or the REST API.

### Delete a catalog with the Confluent CLI¶

    confluent flink catalog delete kafka-cat

### Delete a Catalog with the REST API¶

    curl -v -H "Content-Type: application/json" \
    -X DELETE http://cmf:8080/cmf/api/v1/catalogs/kafka/kafka-cat

## Limitations¶

CMF 2.0 does not support any catalog other than the built-in `KafkaCatalog`. An exception is the example catalog enabled with the `cmf.sql.examples-catalog.enabled` configuration flag.

The following limitations apply for the `KafkaCatalog` in CMF 2.0:

  * It is not possible to update the specification of a `KafkaCatalog`. You need to delete and re-create it.
  * The catalog uses a default mechanism to translate topic and schema metadata into Flink table and connector metadata. This is the same mechanism that Confluent Cloud Flink SQL uses for inferred tables.
  * The catalog does not support altering, creating, or deleting tables. You can create or delete tables by creating or deleting topics and alter tables by changing their schemas.
  * The catalog uses the `TopicNameStrategy` to retrieve the key and value schemas of a topic. For a topic called `orders`, the catalog looks for two subjects called `orders-key` and `orders-value`. If these subjects are not present, the key or value schemas are read as raw bytes and exposed as single columns of type `BINARY`.
  * Compacted Kafka topics are not exposed as tables.
