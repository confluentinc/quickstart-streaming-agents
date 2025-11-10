---
document_id: flink_how-to-guides_resolve-common-query-problems_chunk_1
source_file: flink_how-to-guides_resolve-common-query-problems.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/resolve-common-query-problems.html
title: Resolve Common SQL Query Problems in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Resolve Statement Advisor Warnings with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® includes a Statement Advisor feature that provides real-time warnings for Flink SQL queries that might cause operational problems, high costs, or undesired output. While these warnings don’t directly prevent query execution, addressing them can help optimize performance, reduce resource consumption, and avoid problems occurring over the course of time.

This page explains the common warnings your queries may produce and how to resolve them.

## Primary key differs from derived upsert key¶

    [Warning] The primary key "" does not match the upsert key ""
    that is derived from the query. If the primary key and upsert key don't match, the system needs
    to add a state-intensive operation for correction, which can result in a DEGRADED statement
    and higher CFU consumption. If possible, revisit the table declaration with the primary key or
    change your query. For more information, see
    https://cnfl.io/primary_vs_upsert_key.

This warning occurs when you insert data into a table where the table’s defined `PRIMARY KEY` doesn’t align with the key columns derived from the `INSERT INTO ... SELECT` or `CREATE TABLE ... AS SELECT` query’s grouping or source. When the keys mismatch, Flink must introduce an expensive internal operator (`UpsertMaterialize`) to ensure correctness, which consumes more state and resources.

The following example illustrates a query that triggers this warning:

    -- Create a table to store customer total orders
    CREATE TABLE customer_orders (
        total_orders INT PRIMARY KEY NOT ENFORCED, -- Primary Key is total_orders
        customer_name STRING
    );

    -- Insert aggregated order counts per customer
    INSERT INTO customer_orders
    SELECT
        SUM(order_count), customer_name -- Upsert key derived from GROUP BY is customer_name
    FROM ( VALUES
        ('Bob', 2),      -- Bob placed 2 orders
        ('Alice', 1),    -- Alice placed 1 order
        ('Bob', 2)       -- Bob placed 2 more orders
    ) AS OrderData(customer_name, order_count)
    GROUP BY customer_name;

To resolve this warning:

Align Primary Key
    Modify the `PRIMARY KEY` definition in your `CREATE TABLE` statement to match the columns used to uniquely identify rows in your `INSERT` query (often the `GROUP BY` columns). In the example above, changing the primary key to `customer_name` resolves the warning.
Modify Query
    Adjust your `INSERT INTO ... SELECT` query so the selected columns or grouping aligns with the existing primary key definition. This might involve changing the `GROUP BY` clause or the columns being selected.

## High state operator without state TTL¶

    [Warning] Your query includes one or more highly state-intensive operators but does not set a
    time-to-live (TTL) value, which means that the system potentially needs to store an infinite amount
    of state. This can result in a DEGRADED statement and higher CFU consumption. If possible, change
    your query to use a different operator, or set a time-to-live (TTL) value.
    For more information, see https://cnfl.io/high_state_intensive_operators.

Certain SQL operations, like joins on unbounded streams or aggregations without windowing, require Flink to maintain internal state. If this state isn’t configured to expire (using a Time-To-Live or TTL setting), it can grow indefinitely, leading to excessive memory usage, performance degradation, and higher costs.

The following example illustrates a query that triggers this warning:

    -- Joining two unbounded streams without TTL
    SELECT c.*, o.*
    FROM `examples`.`marketplace`.`clicks` c
    INNER JOIN `examples`.`marketplace`.`orders` o
    ON c.user_id = o.customer_id;

To resolve this warning:

Set State TTL
    Configure a state time-to-live (TTL) for the table(s) involved in the stateful operation. This ensures that state older than the specified duration is automatically cleared. This can done for the full statement via [SET ‘sql.state-ttl’](../reference/statements/set.html#flink-sql-set-statement) option or for individual tables via [State TTL Hints](../reference/statements/hints.html#flink-sql-hints).
Use Windowed Operations
    If applicable, rewrite your query to use windowed operations, like windowed joins or windowed aggregations, instead of unbounded operations. Windows limit the amount of state required inherently.
Refactor Query
    Analyze if the stateful operation is necessary or if the query logic can be changed to avoid large state requirements.
