---
document_id: flink_concepts_schema-statement-evolution_chunk_2
source_file: flink_concepts_schema-statement-evolution.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/schema-statement-evolution.html
title: Schema and Statement Evolution with Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 4
---

on which resource was deleted.

## Schema compatibility modes¶

When a statement is created, it must be bootstrapped from its source tables. For this, Flink must be able to read the source tables from the beginning (or any other specified offsets). As mentioned previously, statements use the latest schema version, at the time of statement creation, for each source table as the read schema.

You have these options for handling changes to base schemas:

  * Compatibility Mode FULL or FULL_TRANSITIVE
  * BACKWARD_TRANSITIVE compatibility mode and upgrade consumers first
  * Compatibility groups and migration rules

To maximize compatibility with Flink, you should use `FULL_TRANSITIVE` or `FULL` as the schema compatibility mode, which eases migrations. Note that in Confluent Cloud, the default compatibility mode is `BACKWARD`.

Sometimes, you may need to make changes beyond what the `FULL_TRANSITIVE` and `FULL` modes enable, so Confluent Cloud for Apache Flink gives you the additional options of BACKWARD_TRANSITIVE compatibility mode and Compatibility groups and migration rules for handling changes to base schemas.

### Compatibility Mode FULL or FULL_TRANSITIVE¶

If you use the `FULL` or `FULL_TRANSITIVE` compatibility mode, the order you upgrade your statements doesn’t matter. `FULL` limits the changes that you can make to your tables to adding and removing optional fields. You can make any compatible changes to the source tables, and none of the statements that reference them will break.

### BACKWARD_TRANSITIVE compatibility mode and upgrade consumers first¶

`BACKWARD_TRANSITIVE` mandates that consumers are upgraded prior to producers. This means that if you evolve your schema according to the `BACKWARD_TRANSITIVE` rules (delete fields, add optional fields), you always need to upgrade all statements that are reading from the corresponding source tables before producing any records to the table that uses the next schema version, as described in Query Evolution.

### Compatibility groups and migration rules¶

If you need to make a non-compatible change to a table, either using `FULL` or `BACKWARD_TRANSITIVE`, Confluent Cloud for Apache Flink also supports compatibility groups and migration rules. For more information, see [Data Contracts for Schema Registry on Confluent Cloud](../../sr/fundamentals/data-contracts.html#sr-data-contracts).

Note

If you need to make changes to your schemas that aren’t possible under schema compatibility mode `FULL`, use compatibility mode `FULL` for all topics and rely on compatibility groups and migration rules.

## Statements and schema evolution¶

When following the practices in the previous section, statements won’t fail when fields are added or optional fields are removed from its source tables, but these new fields aren’t picked up or forwarded to the sink tables. They are ignored by any previously created statements, and the `*`-operators are not evaluated dynamically when the schema changes.

Note

If you’re interested in to providing feedback about configuring statements to pick up schema changes of sources tables dynamically, reach out to Confluent Support or your account manager.
