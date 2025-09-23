---
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/group-aggregation.html
title: SQL Group Aggregation Queries in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'queries', 'group-aggregation.html']
scraped_date: 2025-09-05T13:49:23.487372
---

# Group Aggregation Queries in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables computing a single result from multiple input rows in a Flink SQL table.

## Description¶

Compute a single result from multiple input rows in a table.

Like most data systems, Apache Flink® supports aggregate functions. An aggregate function computes a single result from multiple input rows. For example, there are aggregates to compute the `COUNT`, `SUM`, `AVG` (average), `MAX` (maximum) and `MIN` (minimum) values over a set of rows.

The following example shows how to count the number of rows in a table, by using the `COUNT` function.

    SELECT COUNT(*) FROM orders

For streaming queries, Flink runs continuous queries that never terminate. A continuous query updates the result table according to the updates on its input tables. For the previous query, Flink outputs an updated count each time a new row is inserted into the `orders` table.

### GROUP BY clause¶

Flink SQL supports the standard `GROUP BY` clause for aggregating data.

The following example shows how to count the number of rows in a table and group the results by a table column.

    SELECT COUNT(*)
    FROM orders
    GROUP BY order_id

For streaming queries, the required state for computing the query result might grow indefinitely. State size depends on the number of groups and the number and type of aggregation functions.

For example, `MIN` and `MAX` are heavy on state size while `COUNT` is inexpensive.

### DISTINCT Aggregation¶

Distinct aggregates remove duplicate values before applying an aggregation function.

The following example counts the number of distinct `order_ids` instead of the total number of rows in an `orders` table.

    SELECT COUNT(DISTINCT order_id) FROM orders

For streaming queries, the required state for computing the query result might grow indefinitely. State size depends primarily on the number of distinct rows and the time that a group is maintained. Short-lived GROUP BY windows are not a problem.

### GROUPING SETS¶

Grouping sets enable more complex grouping operations than those you can describe with a standard `GROUP BY` clause. Rows are grouped separately by each specified grouping set, and aggregates are computed for each group just as for simple `GROUP BY` clauses.

The following example show how to use GROUPING SETS to

    SELECT supplier_id, rating, COUNT(*) AS total
    FROM (VALUES
        ('supplier1', 'product1', 4),
        ('supplier1', 'product2', 3),
        ('supplier2', 'product3', 3),
        ('supplier2', 'product4', 4))
    AS Products(supplier_id, product_id, rating)
    GROUP BY GROUPING SETS ((supplier_id, rating), (supplier_id), ())

Results:

    +-------------+--------+-------+
    | supplier_id | rating | total |
    +-------------+--------+-------+
    |   supplier1 |      4 |     1 |
    |   supplier1 | (NULL) |     2 |
    |      (NULL) | (NULL) |     4 |
    |   supplier1 |      3 |     1 |
    |   supplier2 |      3 |     1 |
    |   supplier2 | (NULL) |     2 |
    |   supplier2 |      4 |     1 |
    +-------------+--------+-------+

Each sublist of `GROUPING SETS` specifies zero or more columns or expressions and is interpreted as if it were used directly in the `GROUP BY` clause. An empty grouping set means that all rows are aggregated down to a single group, which is output even if no input rows were present.

References to the grouping columns or expressions are replaced by null values in result rows for grouping sets in which those columns don’t appear.

For streaming queries, the required state for computing the query result might grow indefinitely. State size depends on the number of group sets and type of aggregation functions.

#### ROLLUP¶

`ROLLUP` is a shorthand notation for specifying a common type of grouping set. It represents the given list of expressions and all prefixes of the list, including the empty list.

For example, the following query is equivalent to the previous GROUP BY GROUPING SETS query.

    SELECT supplier_id, rating, COUNT(*)
    FROM (VALUES
        ('supplier1', 'product1', 4),
        ('supplier1', 'product2', 3),
        ('supplier2', 'product3', 3),
        ('supplier2', 'product4', 4))
    AS Products(supplier_id, product_id, rating)
    GROUP BY ROLLUP (supplier_id, rating)

#### CUBE¶

`CUBE` is a shorthand notation for specifying a common type of grouping set. It represents the given list and all of its possible subsets, which is also known as the _power set_.

For example, the following two queries are equivalent.

    SELECT supplier_id, rating, product_id, COUNT(*)
    FROM (VALUES
        ('supplier1', 'product1', 4),
        ('supplier1', 'product2', 3),
        ('supplier2', 'product3', 3),
        ('supplier2', 'product4', 4))
    AS Products(supplier_id, product_id, rating)
    GROUP BY CUBE (supplier_id, rating, product_id)

    SELECT supplier_id, rating, product_id, COUNT(*)
    FROM (VALUES
        ('supplier1', 'product1', 4),
        ('supplier1', 'product2', 3),
        ('supplier2', 'product3', 3),
        ('supplier2', 'product4', 4))
    AS Products(supplier_id, product_id, rating)
    GROUP BY GROUPING SET (
        ( supplier_id, product_id, rating ),
        ( supplier_id, product_id         ),
        ( supplier_id,             rating ),
        ( supplier_id                     ),
        (              product_id, rating ),
        (              product_id         ),
        (                          rating ),
        (                                 )
    )

### HAVING¶

The `HAVING` clause eliminates group rows that don’t satisfy the specified condition.

`HAVING` is distinct from the `WHERE` clause, because `WHERE` filters individual rows _before_ the `GROUP BY`, while `HAVING` filters group rows _created by_ `GROUP BY`. Each column referenced in the condition must unambiguously reference a grouping column, unless it appears within an aggregate function.

    SELECT SUM(amount)
    FROM orders
    GROUP BY users
    HAVING SUM(amount) > 50

The presence of a `HAVING` clause turns a query into a grouped query, even if there is no `GROUP BY` clause. It’s the same as what happens when the query contains aggregate functions but no `GROUP BY` clause. The query considers all selected rows to form a single group, and the `SELECT` list and `HAVING` clause can reference only table columns from within aggregate functions. Such a query emits a single row if the `HAVING` condition is true, and zero rows if it’s not true.
