---
document_id: flink_concepts_dynamic-tables_chunk_2
source_file: flink_concepts_dynamic-tables.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/dynamic-tables.html
title: Tables and Topics in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 2
---

cluster, topics, schemas, and Flink](../overview.html#ccloud-flink-overview-metadata-mapping).

## Dynamic tables and continuous queries¶

Every table in Flink is equivalent to a stream of events describing the changes that are being made to that table. A stream of changes like this a _changelog stream_. Essentially, a stream is the changelog of a table, and every table is backed by a stream. This is also the case for regular database tables.

Querying a dynamic table yields a _continuous query_. A continuous query never terminates and produces dynamic results - another dynamic table. The query continuously updates its dynamic result table to reflect changes on its dynamic input tables. Essentially, a continuous query on a dynamic table is similar to a query that defines a materialized view.

The output of a continuous query is always equivalent to the result of the same query executed in batch mode on a snapshot of the input tables.

### Append-only table¶

Stream-table table duality for an append-only table¶

In this animation, the only changes happening to the `Orders` table are the new orders being appended to the end of the table. The corresponding changelog stream is just a stream of INSERT events. Adding another order to the table is the same as adding another INSERT statement to the stream, as shown below the table. This is an example of an append-only or insert-only table.

### Updating table¶

Not all tables are append-only tables. Tables can also contain events that modify or delete existing rows. The changelog stream used by Flink SQL contains three additional event types to accommodate different ways that tables can be updated. Besides the regular Insertion event, _Update Before_ and _Update After_ are a pair of events that work together to update an earlier result. The _Delete_ event has the effect you would expect, removing a record from the table.

Stream-table table duality for an updating table¶

This animation has the same starting point as the previous example that showed the append-only table. But this time, an order has been cancelled, and the item in that order hasn’t been sold. The result of this event is that the `Bestsellers` table is _updated_ , rather then doing another insert. The update starts with appending another order to the append-only/insert-only `Orders` table, which is registered as an INSERT event in the changelog stream.

Because the SQL statement is doing grouping, the result is an updating table instead of an append-only/insert-only table. In this example, an order for 15 hats is cancelled. To process the event with the 15-hat order cancellation, the query produces two update events:

* The first is an UPDATE_BEFORE event that retracts the current result that showed 50 hats as the bestselling item.
* The second is an UPDATE_AFTER event that replaces the old entry with a new one that shows 35 hats.

Conceptually, the UPDATE_BEFORE event is processed first, which removes the old entry from the `Bestsellers` table. Then, the sync processes the UPDATE_AFTER event, which inserts the updated results.

The following figure visualizes the relationship of streams, dynamic tables, and continuous queries:

  1. A stream is converted into a dynamic table.
  2. A continuous query is evaluated on the dynamic table yielding a new dynamic table.
  3. The resulting dynamic table is converted back into a stream.

Dynamic tables are a logical concept. The only state that is actually materialized by the Flink SQL runtime is whatever is strictly necessary to produce correct results for the specific query being executed. For example, the previous diagram shows a query executing a simple filter. This requires no state, so nothing is materialized.

### Changelog entries¶

Flink provides four different types of changelog entries:

Short name | Long name | Semantics
---|---|---
+I | Insertion | Records only the insertions that occur.
-U | Update Before | Retracts a previously emitted result. Update Before is an update operation with the previous content of the updated row. This kind occurs together with Update After (+U) for modeling an update that must retract the previous row first. It is useful in cases of a non-idempotent update, which is an update of a row that is not uniquely identifiable by a key.
+U | Update After | Updates a previously emitted result. Update After is an update operation with new content for the updated row. This kind _can_ occur together with Update Before (-U) for modeling an update that must retract the previous row first, or it can describe an idempotent update, which is an update of a row that is uniquely identifiable by a key.
-D | Delete | Deletes the last result.

The `-` character always means that a row is being removed.

If the downstream system supports upserting, you should use a primary key in Confluent Cloud for Apache Flink to avoid the need to use Update Before.

Depending on the combination of source, sink, and business logic applied, you can end up with the following types of changelog streams.

Changelog stream types | Stream category | Changelog entry types
---|---|---
Appending stream | Append stream | Contains only +I
Upserting streams | Update stream | +I, +U, -D (never contains -U but can contain +U and/or -D)
Retracting stream | Update stream | +I, +U, -U, -D (contains +I and can contain -U and/or -D)

* All streams can have +I / inserts.
* Both retract and upsert streams can have -D / deletes and +U / upserts (upsert afters).
* Only retract streams can have -U.
