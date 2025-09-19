---
document_id: flink_configure_catalog_chunk_2
source_file: flink_configure_catalog.md
source_url: https://docs.confluent.io/platform/current/flink/configure/catalog.html
title: Manage Flink SQL Catalogs for Confluent Manager for Apache Flink
chunk_index: 2
total_chunks: 2
---

user who submits the statement.

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
