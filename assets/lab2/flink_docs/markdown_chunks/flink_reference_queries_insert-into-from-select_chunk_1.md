---
document_id: flink_reference_queries_insert-into-from-select_chunk_1
source_file: flink_reference_queries_insert-into-from-select.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/insert-into-from-select.html
title: SQL INSERT INTO FROM SELECT Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# INSERT INTO FROM SELECT Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables inserting SELECT query results directly into a Flink SQL table.

## Syntax¶

    [EXECUTE] INSERT { INTO | OVERWRITE } [catalog_name.][database_name.]table_name
      [PARTITION (partition_column_name1=value1 [, partition_column_name2=value2, ...])]
      [(column_name1 [, column_name2, ...])]
      select_statement

**OVERWRITE**
    `INSERT OVERWRITE` overwrites all existing data in the table or partition. New records are appended.
**PARTITION**
     The `PARTITION` clause contains static partition columns for the insertion.
**COLUMN LIST**

For a table `T(a INT, b INT, c INT)`, Flink supports

    INSERT INTO T(c, b) SELECT x, y FROM S.

The `x` result is written to column `c`, and the `y` result is written to column `b`. If column `a` is nullable, `a` is set to NULL.

## Description¶

Insert query results into a table.

Use the INSERT INTO FROM SELECT statement to insert rows into a table from another table or query.

For example, if you have a table `T` with columns `a`, `b`, and `c`, and another table `S` with columns `x` and `y`, the following query writes the values of `x` and `y` from `S` into `c` and `b` of `T`, respectively.

    INSERT INTO T (c, b) SELECT x, y FROM S

If column `a` of `T` is nullable, Flink sets it to NULL.

## Examples¶

### Insert rows into a simple table¶

In the Flink SQL shell or in a Cloud Console workspace, run the following commands to see an example of the INSERT INTO FROM SELECT statement.

  1. Create a table for web page click events.

         -- Create a table for web page click events.
         CREATE TABLE clicks (
           ip_address VARCHAR,
           url VARCHAR,
           click_ts_raw BIGINT
         );

  2. Populate the table with mock clickstream data.

         -- Populate the table with mock clickstream data.
         INSERT INTO clicks
         VALUES( '10.0.0.1',  'https://acme.com/index.html',     1692812175),
               ( '10.0.0.12', 'https://apache.org/index.html',   1692826575),
               ( '10.0.0.13', 'https://confluent.io/index.html', 1692826575),
               ( '10.0.0.1',  'https://acme.com/index.html',     1692812175),
               ( '10.0.0.12', 'https://apache.org/index.html',   1692819375),
               ( '10.0.0.13', 'https://confluent.io/index.html', 1692826575);

Press ENTER to return to the SQL shell. Because INSERT INTO VALUES is a point-in-time statement, it exits after it completes inserting records.

  3. Create another table for filtered web page click events.

         CREATE TABLE filtered_clicks (
           ip_address VARCHAR,
           url VARCHAR,
           click_ts_raw BIGINT
         );

  4. Run the following statement to insert filtered rows into the `filtered_clicks` table. Only clicks that have an IP address of `10.0.0.1` are inserted.

         INSERT INTO filtered_clicks(
           ip_address,
           url,
           click_ts_raw
         )
         SELECT * FROM clicks WHERE ip_address = '10.0.0.1';

  5. View the rows in the `filtered_clicks` table.

         SELECT * FROM filtered_clicks;

Your output should resemble:

         ip_address url                         click_timestamp
         10.0.0.1   https://acme.com/index.html 2023-08-23 10:36:15
         10.0.0.1   https://acme.com/index.html 2023-08-23 10:36:15

### Fill a table without specifying all columns¶

    CREATE TABLE t_insert_gaps (c1 STRING, c2 STRING, c3 STRING, c4 STRING);

    INSERT INTO t_insert_gaps (c3) SELECT 'Bob';

    INSERT INTO t_insert_gaps (c3, c2) SELECT 'Bob', 'Alice';

    SELECT * FROM t_insert_gaps;

Properties

* A column list is defined between the table name and the SELECT in the INSERT INTO statement, so the SELECT statement uses a reduced schema.
* Columns `c1`, `c2`, are `c4` are filled with NULLs.
* If one of the columns is declared NOT NULL, an error occurs.
