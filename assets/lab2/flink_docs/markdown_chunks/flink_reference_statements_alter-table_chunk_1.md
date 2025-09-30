---
document_id: flink_reference_statements_alter-table_chunk_1
source_file: flink_reference_statements_alter-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/alter-table.html
title: SQL ALTER TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 7
---

# ALTER TABLE Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables changing properties of an existing table.

## Syntax¶

    ALTER TABLE [catalog_name.][db_name.]table_name {
       ADD (metadata_column_name metadata_column_type METADATA [FROM metadata_key] VIRTUAL [COMMENT column_comment])
     | ADD (computed_column_name AS computed_column_expression [COMMENT column_comment])
     | MODIFY WATERMARK FOR rowtime_column_name AS watermark_strategy_expression
     | DROP WATERMARK
     | SET (key1='value1' [, key2='value2', ...])
     | RESET (key1 [, key2, ...])
    }

## Description¶

ALTER TABLE allows you to add metadata columns, computed columns, change or remove the [watermark](../../../_glossary.html#term-watermark), and modify [table properties](create-table.html#flink-sql-with-options). Physical columns cannot be added, modified, or dropped within Confluent Cloud for Apache Flink directly, but schemas can be [evolved in Schema Registry](../../../sr/fundamentals/schema-evolution.html#schema-evolution-and-compatibility).
