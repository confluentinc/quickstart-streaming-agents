---
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/drop-connection.html
title: SQL DROP CONNECTION Statement in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'statements', 'drop-connection.html']
scraped_date: 2025-09-05T13:49:57.697579
---

# DROP CONNECTION Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports creating secure connections to external services and data sources. You can use these connections in your Flink statements. You remove these connections by using the DROP CONNECTION statement.

## Syntax¶

    DROP CONNECTION [IF EXISTS] [catalog_name.][db_name.]connection_name

## Description¶

Delete a connection from the Flink environment.

Dropping a connection deletes the corresponding credentials stored in the `SecretStore`.

## Example¶

    DROP CONNECTION `azure-openai-connection`;

## Related content¶

  * [ALTER CONNECTION](alter-connection.html#flink-sql-alter-connection)
  * [CREATE CONNECTION](create-connection.html#flink-sql-create-connection)
  * [DESCRIBE CONNECTION](describe.html#flink-sql-describe)
  * [SHOW CONNECTIONS](show.html#flink-sql-show-connections)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
