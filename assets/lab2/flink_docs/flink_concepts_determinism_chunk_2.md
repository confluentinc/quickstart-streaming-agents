---
document_id: flink_concepts_determinism_chunk_2
source_file: flink_concepts_determinism.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/determinism.html
title: Determinism with continuous Flink SQL queries in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

repeated with identical input values.

## Determinism for regular batch queries¶

In a classic batch scenario, repeated execution of the same query for a given bounded data set will yield consistent results, which is the most intuitive understanding of determinism.

In practice, however, the same query does not always return consistent results on a batch process either, as shown by the following example queries.

### Two examples of batch queries with non-deterministic results¶

For example, consider a newly created website click log table:

    CREATE TABLE clicks (
        uid VARCHAR(128),
        cTime TIMESTAMP(3),
        url VARCHAR(256)
    )

Some new records are written to the table:

    +------+---------------------+------------+
    |  uid |               cTime |        url |
    +------+---------------------+------------+
    | Mary | 2023-08-22 12:00:01 |      /home |
    |  Bob | 2023-08-22 12:00:01 |      /home |
    | Mary | 2023-08-22 12:00:05 | /prod?id=1 |
    |  Liz | 2023-08-22 12:01:00 |      /home |
    | Mary | 2023-08-22 12:01:30 |      /cart |
    |  Bob | 2023-08-22 12:01:35 | /prod?id=3 |
    +------+---------------------+------------+

The following query applies a time filter to the click log table and wants to return the last two minutes of click records:

    SELECT * FROM clicks
    WHERE cTime BETWEEN TIMESTAMPADD(MINUTE, -2, CURRENT_TIMESTAMP) AND CURRENT_TIMESTAMP;

When the query was submitted at “2023-08-22 12:02:00”, it returned all 6 rows in the table, and when it was executed again a minute later, at “2023-08-22 12:03:00”, it returned only 3 items:

    +------+---------------------+------------+
    |  uid |               cTime |        url |
    +------+---------------------+------------+
    |  Liz | 2023-08-22 12:01:00 |      /home |
    | Mary | 2023-08-22 12:01:30 |      /cart |
    |  Bob | 2023-08-22 12:01:35 | /prod?id=3 |
    +------+---------------------+------------+

Another query wants to add a unique identifier to each returned record, since the `clicks` table doesn’t have a primary key.

    SELECT UUID() AS uuid, * FROM clicks LIMIT 3;

Executing this query twice in a row generates a different `uuid` identifier for each row:

    -- first execution
    +--------------------------------+------+---------------------+------------+
    |                           uuid |  uid |               cTime |        url |
    +--------------------------------+------+---------------------+------------+
    | aaaa4894-16d4-44d0-a763-03f... | Mary | 2023-08-22 12:00:01 |      /home |
    | ed26fd46-960e-4228-aaf2-0aa... |  Bob | 2023-08-22 12:00:01 |      /home |
    | 1886afc7-dfc6-4b20-a881-b0e... | Mary | 2023-08-22 12:00:05 | /prod?id=1 |
    +--------------------------------+------+---------------------+------------+

    -- second execution
    +--------------------------------+------+---------------------+------------+
    |                           uuid |  uid |               cTime |        url |
    +--------------------------------+------+---------------------+------------+
    | 95f7301f-bcf2-4b6f-9cf3-1ea... | Mary | 2023-08-22 12:00:01 |      /home |
    | 63301e2d-d180-4089-876f-683... |  Bob | 2023-08-22 12:00:01 |      /home |
    | f24456d3-e942-43d1-a00f-fdb... | Mary | 2023-08-22 12:00:05 | /prod?id=1 |
    +--------------------------------+------+---------------------+------------+

### Non-determinism in batch processing¶

The non-determinism in batch processing is caused mainly by the non-deterministic functions, as shown in the previous query examples, where the built-in functions `CURRENT_TIMESTAMP` and `UUID()` actually behave differently in batch processing. Compare with the following query:

    SELECT CURRENT_TIMESTAMP, * FROM clicks;

`CURRENT_TIMESTAMP` is the same value on all records returned

    +-------------------------+------+---------------------+------------+
    |       CURRENT_TIMESTAMP |  uid |               cTime |        url |
    +-------------------------+------+---------------------+------------+
    | 2023-08-23 17:25:46.831 | Mary | 2023-08-22 12:00:01 |      /home |
    | 2023-08-23 17:25:46.831 |  Bob | 2023-08-22 12:00:01 |      /home |
    | 2023-08-23 17:25:46.831 | Mary | 2023-08-22 12:00:05 | /prod?id=1 |
    | 2023-08-23 17:25:46.831 |  Liz | 2023-08-22 12:01:00 |      /home |
    | 2023-08-23 17:25:46.831 | Mary | 2023-08-22 12:01:30 |      /cart |
    | 2023-08-23 17:25:46.831 |  Bob | 2023-08-22 12:01:35 | /prod?id=3 |
    +-------------------------+------+---------------------+------------+

This difference is due to the fact that Flink SQL inherits the definition of functions from Apache Calcite, where there are two types of functions other than deterministic function: non-deterministic functions and dynamic functions.

* The non-deterministic functions are executed at runtime in clusters and evaluated per record.
* The dynamic functions determine the corresponding values only when the query plan is generated. They’re not executed at runtime, and different values are obtained at different times, but the same values are obtained during the same execution. Built-in dynamic functions are mainly temporal functions.
