---
document_id: flink_reference_statements_create-table_chunk_5
source_file: flink_reference_statements_create-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
title: SQL CREATE TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 14
---

[How to Set Idle Timeouts](https://www.youtube.com/watch?v=YSIhM5-Sykw).

## CREATE TABLE AS SELECT (CTAS)¶

Tables can also be created and populated by the results of a query in one create-table-as-select (CTAS) statement. CTAS is the simplest and fastest way to create and insert data into a table with a single command.

The CTAS statement consists of two parts:

* The SELECT part can be any SELECT query supported by Flink SQL.
* The CREATE part takes the resulting schema from the SELECT part and creates the target table.

The following two code examples are equivalent.

    -- Equivalent to the following CREATE TABLE and INSERT INTO statements.
    CREATE TABLE my_ctas_table
    AS SELECT id, name, age FROM source_table WHERE mod(id, 10) = 0;

    -- These two statements are equivalent to the preceding CREATE TABLE AS statement.
    CREATE TABLE my_ctas_table (
        id BIGINT,
        name STRING,
        age INT
    );

    INSERT INTO my_ctas_table SELECT id, name, age FROM source_table WHERE mod(id, 10) = 0;

Similar to CREATE TABLE, CTAS requires all options of the target table to be specified in the WITH clause. The syntax is `CREATE TABLE t WITH (…) AS SELECT …`, for example:

    CREATE TABLE t WITH ('scan.startup.mode' = 'latest-offset') AS SELECT * FROM b;

### Specifying explicit columns¶

The CREATE part enables you to specify explicit columns. The resulting table schema contains the columns defined in the CREATE part first, followed by the columns from the SELECT part. Columns named in both parts retain the same column position as defined in the SELECT part.

You can also override the data type of SELECT columns if you specify it in the CREATE part.

    CREATE TABLE my_ctas_table (
        desc STRING,
        quantity DOUBLE,
        cost AS price * quantity,
        WATERMARK FOR order_time AS order_time - INTERVAL '5' SECOND,
    ) AS SELECT id, price, quantity, order_time FROM source_table;

### Primary keys and distribution strategies¶

The CREATE part enable you to specify primary keys and distribution strategies. Primary keys work only on NOT NULL columns. Currently, primary keys only allow you to define columns from the SELECT part, which may be NOT NULL.

The following two code examples are equivalent.

    -- Equivalent to the following CREATE TABLE and INSERT INTO statements.
    CREATE TABLE my_ctas_table (
        PRIMARY KEY (id) NOT ENFORCED
    ) DISTRIBUTED BY HASH(id) INTO 4 BUCKETS
    AS SELECT id, name FROM source_table;

    -- These two statements are equivalent to the preceding CREATE TABLE AS statement.
    CREATE TABLE my_ctas_table (
        id BIGINT NOT NULL PRIMARY KEY NOT ENFORCED,
        name STRING
    ) DISTRIBUTED BY HASH(id) INTO 4 BUCKETS;

    INSERT INTO my_ctas_table SELECT id, name FROM source_table;
