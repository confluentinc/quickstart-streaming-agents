---
document_id: flink_reference_queries_match_recognize_chunk_2
source_file: flink_reference_queries_match_recognize.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/match_recognize.html
title: SQL Pattern Recognition Queries in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 10
---

= 'c' ) AS T

## Pattern recognition¶

It is a common use case to search for a set of event patterns, especially in case of data streams. Apache Flink® comes with a complex event processing (CEP) library, which enables pattern detection in event streams. Furthermore, the Flink SQL API provides a relational way of expressing queries with a large set of built-in functions and rule-based optimizations that you can use out of the box.

In December 2016, the International Organization for Standardization (ISO) released a new version of the SQL standard which includes _Row Pattern Recognition in SQL_ ([ISO/IEC TR 19075-5:2016](https://standards.iso.org/ittf/PubliclyAvailableStandards/c065143_ISO_IEC_TR_19075-5_2016.zip)). It enables Flink to consolidate CEP and SQL API using the `MATCH_RECOGNIZE` clause for complex event processing in SQL.

A `MATCH_RECOGNIZE` clause enables the following tasks:

  * Logically partition and order the data that is used with the `PARTITION BY` and `ORDER BY` clauses.
  * Define patterns of rows to seek using the `PATTERN` clause. These patterns use a syntax similar to that of regular expressions.
  * The logical components of the row pattern variables are specified in the `DEFINE` clause.
  * Define measures, which are expressions usable in other parts of the SQL query, in the `MEASURES` clause.

This topic explains each keyword in more detail and illustrates more complex examples.

Important

The Flink implementation of the `MATCH_RECOGNIZE` clause is a subset of the full standard. Only the features documented in the following sections are supported. For more information, see Known limitations.

### Installation¶

To use the `MATCH_RECOGNIZE` clause in the Flink SQL CLI, no action is necessary, because all dependencies are included by default.

### SQL semantics¶

Every `MATCH_RECOGNIZE` query consists of the following clauses:

  * PARTITION BY \- defines the logical partitioning of the table, similar to a `GROUP BY` operation.
  * ORDER BY \- specifies how the incoming rows should be ordered, which is essential, because patterns depend on an order.
  * MEASURES \- defines the output of the clause, similar to a `SELECT` clause.
  * ONE ROW PER MATCH \- output mode that defines how many rows per match to produce.
  * AFTER MATCH SKIP \- specifies where the next match should start. This is also a way to control how many distinct matches a single event can belong to.
  * PATTERN \- enables constructing patterns that will be searched for using a syntax that’s similar to regular expressions.
  * DEFINE \- defines the conditions that the pattern variables must satisfy.

### Examples¶

These examples assume that a table `Ticker` has been registered. The table contains prices of stocks at a particular point in time.

The table has a following schema:

    Ticker
         |-- symbol: String                           # symbol of the stock
         |-- price: Long                              # price of the stock
         |-- tax: Long                                # tax liability of the stock
         |-- rowtime: TimeIndicatorTypeInfo(rowtime)  # point in time when the change to those values happened

For simplicity, only the incoming data for a single stock, named `ACME`, is considered. A ticker could look similar to the following table, where rows are continuously appended.

    symbol         rowtime         price    tax
    ======  ====================  ======= =======
    'ACME'  '01-Apr-11 10:00:00'   12      1
    'ACME'  '01-Apr-11 10:00:01'   17      2
    'ACME'  '01-Apr-11 10:00:02'   19      1
    'ACME'  '01-Apr-11 10:00:03'   21      3
    'ACME'  '01-Apr-11 10:00:04'   25      2
    'ACME'  '01-Apr-11 10:00:05'   18      1
    'ACME'  '01-Apr-11 10:00:06'   15      1
    'ACME'  '01-Apr-11 10:00:07'   14      2
    'ACME'  '01-Apr-11 10:00:08'   24      2
    'ACME'  '01-Apr-11 10:00:09'   25      2
    'ACME'  '01-Apr-11 10:00:10'   19      1

The task is to find periods of a constantly decreasing price of a single ticker. To accomplish this, you could write a query like the following:

    SELECT *
    FROM Ticker
        MATCH_RECOGNIZE (
            PARTITION BY symbol
            ORDER BY $rowtime
            MEASURES
                START_ROW.rowtime AS start_tstamp,
                LAST(PRICE_DOWN.$rowtime) AS bottom_tstamp,
                LAST(PRICE_UP.$rowtime) AS end_tstamp
            ONE ROW PER MATCH
            AFTER MATCH SKIP TO LAST PRICE_UP
            PATTERN (START_ROW PRICE_DOWN+ PRICE_UP)
            DEFINE
                PRICE_DOWN AS
                    (LAST(PRICE_DOWN.price, 1) IS NULL AND PRICE_DOWN.price < START_ROW.price) OR
                        PRICE_DOWN.price < LAST(PRICE_DOWN.price, 1),
                PRICE_UP AS
                    PRICE_UP.price > LAST(PRICE_DOWN.price, 1)
        ) MR;
