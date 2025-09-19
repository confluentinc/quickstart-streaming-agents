---
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-function.html
title: Flink SQL CREATE TABLE Statement in Confluent Cloud
hierarchy: ['reference', 'statements', 'create-function.html']
scraped_date: 2025-09-05T13:48:22.862164
---

# CREATE FUNCTION Statement¶

Confluent Cloud for Apache Flink® enables registering customer user defined functions (UDFs) by using the CREATE FUNCTION statement. When your UDFs are registered in a Flink database, you can use it in your SQL queries.

## Syntax¶

    CREATE FUNCTION <function-name>
      AS <class-name>
      USING JAR 'confluent-artifact://<plugin-id>/<version-id>';

## Description¶

Register a user defined function (UDF) in the current database.

To remove a (UDF) from the current database, use the DROP FUNCTION statement.

