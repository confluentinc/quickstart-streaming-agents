---
document_id: flink_reference_queries_set-logic_chunk_1
source_file: flink_reference_queries_set-logic.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/set-logic.html
title: SQL Set Logic in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Set Logic in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables set logic operations on tables in SQL statements.

* EXCEPT
* EXISTS
* IN
* INTERSECT
* UNION

## Example data¶

The following examples use these tables to show how the different logical operators work.

    -- Create tables for the set logic operations.
    CREATE TABLE t1(chr CHAR);
    INSERT INTO t1 VALUES('c'), ('a'), ('b'), ('b'), ('c');

    CREATE TABLE t2(chr CHAR);
    INSERT INTO t2 VALUES('d'), ('e'), ('a'), ('b'), ('b');

## EXCEPT¶

`EXCEPT` and `EXCEPT ALL` return the rows that are found in one table but not the other.

* `EXCEPT` returns only distinct rows.
* `EXCEPT ALL` doesn’t remove duplicates from the result rows.

The following code example shows output from the `EXCEPT` function on tables `t1` and `t2`.

    (SELECT chr FROM t1) EXCEPT (SELECT chr FROM t2);

Your output should resemble:

    chr
    c

The following code example shows output from the `EXCEPT ALL` function on tables `t1` and `t2`.

    (SELECT chr FROM t1) EXCEPT ALL (SELECT chr FROM t2);

Your output should resemble:

    +----+
    | chr|
    +----+
    |   c|
    |   c|
    +----+

## EXISTS¶

    SELECT user, amount
    FROM orders
    WHERE product EXISTS (
        SELECT product FROM NewProducts
    )

Returns TRUE if the sub-query returns at least one row. Only supported if the operation can be rewritten in a join and group operation.

The optimizer rewrites the `EXISTS` operation into a join and group operation. For streaming queries, the required state for computing the query result might grow infinitely depending on the number of distinct input rows.

## IN¶

Returns TRUE if an expression exists in a table sub-query. The sub-query table must consist of one column. This column must have the same data type as the expression.

    SELECT user, amount
    FROM orders
    WHERE product IN (
        SELECT product FROM NewProducts
    )

The optimizer rewrites the IN condition into a join and group operation. For streaming queries, the required state for computing the query result might grow infinitely depending on the number of distinct input rows.

## INTERSECT¶

`INTERSECT` and `INTERSECT ALL` return the rows that are found in both tables.

* `INTERSECT` returns only distinct rows.
* `INTERSECT ALL` doesn’t remove duplicates from the result rows.

The following code example shows output from the `INTERSECT` function on tables `t1` and `t2`.

    (SELECT chr FROM t1) INTERSECT (SELECT chr FROM t2);

Your output should resemble:

    chr
    a
    b

The following code example shows output from the `INTERSECT ALL` function on tables `t1` and `t2`.

    (SELECT chr FROM t1) INTERSECT ALL (SELECT chr FROM t2);

Your output should resemble:

    chr
    a
    b
    b

## UNION¶

`UNION` and `UNION ALL` return the rows that are found in either table.

* `UNION` returns only distinct rows.
* `UNION ALL` doesn’t remove duplicates from the result rows.

The following code example shows output from the `UNION` function on tables `t1` and `t2`.

    (SELECT chr FROM view1) UNION (SELECT chr FROM view2);

Your output should resemble:

    chr
    c
    a
    b
    d
    e

The following code example shows output from the `UNION ALL` function on tables `t1` and `t2`.

    (SELECT chr FROM t1) UNION ALL (SELECT chr FROM t2);

Your output should resemble:

    chr
    c
    a
    b
    b
    c
    d
    e
    a
    b
    b
