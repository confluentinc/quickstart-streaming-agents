---
document_id: flink_how-to-guides_convert-serialization-format_chunk_1
source_file: flink_how-to-guides_convert-serialization-format.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/convert-serialization-format.html
title: Convert the Serialization Format of a Topic with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 5
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
