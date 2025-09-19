---
document_id: flink_reference_queries_overview_chunk_2
source_file: flink_reference_queries_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/overview.html
title: SQL Queries in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

1 Morpheus 1 Trinity 2

## Functions¶

Flink supports many built-in functions that help you build sophisticated SQL queries.

Run the `SHOW FUNCTIONS` statement to see the full list of built-in functions.

    SHOW FUNCTIONS;

Your output should resemble:

    +------------------------+
    |     function name      |
    +------------------------+
    | %                      |
    | *                      |
    | +                      |
    | -                      |
    | /                      |
    | <                      |
    | <=                     |
    | <>                     |
    | =                      |
    | >                      |
    | >=                     |
    | ABS                    |
    | ACOS                   |
    | AND                    |
    | ARRAY                  |
    | ARRAY_CONTAINS         |
    | ...

Run the following statement to execute the built-in `CURRENT_TIMESTAMP` function, which returns the local machine’s current system time.

    SELECT CURRENT_TIMESTAMP;

Your output should resemble:

    CURRENT_TIMESTAMP
    2024-01-17 13:07:43.537

Run the following statement to compute the cosine of 0.

    SELECT COS(0) AS cosine;

Your output should resemble:

    cosine
    1.0

## Source Tables¶

As with all SQL engines, Flink SQL queries operate on rows in tables. But unlike traditional databases, Flink doesn’t manage data-at-rest in a local store. Instead, Flink SQL queries operate continuously over external tables.

Flink data processing pipelines begin with source tables. Source tables produce rows operated over during the query’s execution; they are the tables referenced in the `FROM` clause of a query.

Tables are created automatically in Confluent Cloud from all the Apache Kafka® topics. Also, you can create tables by using the SQL shell.

The Flink SQL shell supports [SQL DDL commands](../../concepts/statements.html#flink-sql-statements) similar to traditional SQL. Standard SQL DDL is used to [create](../statements/create-table.html#flink-sql-create-table) and [alter](../statements/alter-table.html#flink-sql-alter-table) tables.

The following statement creates an `employee_information` table.

    CREATE TABLE employee_information(
      emp_id INT,
      name VARCHAR,
      dept_id INT);

Confluent Cloud creates the corresponding `employee_information` topic automatically.

## Continuous Queries¶

You can define a continuous foreground query from the `employee_information` table that reads new rows as they are made available and immediately outputs their results. For example, you can filter for the employees who work in department `1`.

    SELECT * from employee_information WHERE dept_id = 1;

Although SQL wasn’t designed initially with streaming semantics in mind, it’s a powerful tool for building continuous data pipelines. A Flink query differs from a traditional database query by consuming rows continuously as they arrive and producing updates to the query results.

A [continuous query](../../concepts/dynamic-tables.html#flink-sql-dynamic-tables-and-continuous-queries) never terminates and produces a _dynamic table_ as a result. [Dynamic tables](../../concepts/dynamic-tables.html#flink-sql-dynamic-tables) are the core concept of Flink’s SQL support for streaming data.

Aggregations on continuous streams must store aggregated results continuously during the execution of the query. For example, suppose you need to count the number of employees for each department from an incoming data stream. To output timely results as new rows are processed, the query must maintain the most up-to-date count for each department.

    SELECT
       dept_id,
       COUNT(*) as emp_count
    FROM employee_information
    GROUP BY dept_id;

Such queries are considered _stateful_. Flink’s advanced fault-tolerance mechanism maintains internal state and consistency, so queries always return the correct result, even in the face of hardware failure.

## Sink Tables¶

When running the previous query, the Flink SQL provides output in real-time but in a read-only fashion. Storing results - to power a report or dashboard - requires writing out to another table. You can achieve this by using an `INSERT INTO` statement. The table referenced in this clause is known as a _sink table_. An `INSERT INTO` statement is submitted as a detached query to Flink.

    INSERT INTO department_counts
    SELECT
       dept_id,
    COUNT(*) as emp_count
    FROM employee_information;

Once submitted, this query runs and stores the results into the sink table directly, instead of loading the results into the system memory.
