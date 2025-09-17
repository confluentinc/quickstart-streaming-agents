---
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/match_recognize.html
title: SQL Pattern Recognition Queries in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'queries', 'match_recognize.html']
scraped_date: 2025-09-05T13:48:25.038373
---

# Pattern Recognition Queries in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables pattern detection in event streams.

## Syntax¶

    SELECT T.aid, T.bid, T.cid
    FROM MyTable
        MATCH_RECOGNIZE (
          PARTITION BY userid
          ORDER BY $rowtime
          MEASURES
            A.id AS aid,
            B.id AS bid,
            C.id AS cid
          PATTERN (A B C)
          DEFINE
            A AS name = 'a',
            B AS name = 'b',
            C AS name = 'c'
        ) AS T

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

The query partitions the `Ticker` table by the `symbol` column and orders it by the `rowtime` time attribute.

The `PATTERN` clause specifies a pattern with a starting event `START_ROW` that is followed by one or more `PRICE_DOWN` events and concluded with a `PRICE_UP` event. If such a pattern can be found, the next pattern match will be seeked at the last `PRICE_UP` event as indicated by the `AFTER MATCH SKIP TO LAST` clause.

The `DEFINE` clause specifies the conditions that need to be met for a `PRICE_DOWN` and `PRICE_UP` event. Although the `START_ROW` pattern variable is not present it has an implicit condition that is evaluated always as `TRUE`.

A pattern variable `PRICE_DOWN` is defined as a row with a price that is smaller than the price of the last row that met the `PRICE_DOWN` condition. For the initial case or when there is no last row that met the `PRICE_DOWN` condition, the price of the row should be smaller than the price of the preceding row in the pattern (referenced by `START_ROW`).

A pattern variable `PRICE_UP` is defined as a row with a price that is larger than the price of the last row that met the `PRICE_DOWN` condition.

This query produces a summary row for each period in which the price of a stock was continuously decreasing.

The exact representation of the output rows is defined in the `MEASURES` part of the query. The number of output rows is defined by the `ONE ROW PER MATCH` output mode.

     symbol       start_tstamp       bottom_tstamp         end_tstamp
    =========  ==================  ==================  ==================
    ACME       01-APR-11 10:00:04  01-APR-11 10:00:07  01-APR-11 10:00:08

The resulting row describes a period of falling prices that started at `01-APR-11 10:00:04` and achieved the lowest price at `01-APR-11 10:00:07` that increased again at `01-APR-11 10:00:08`.

## Partitioning¶

It is possible to look for patterns in partitioned data, e.g., trends for a single ticker or a particular user. This can be expressed using the `PARTITION BY` clause. The clause is similar to using `GROUP BY` for aggregations.

It is highly advised to partition the incoming data because otherwise the `MATCH_RECOGNIZE` clause will be translated into a non-parallel operator to ensure global ordering.

## Order of events¶

Flink enables searching for patterns based on time, either [event time](../../concepts/timely-stream-processing.html#flink-sql-time-attributes-event-time). Processing time is not supported in Confluent Cloud for Apache Flink.

In the case of event time, the events are sorted before they are passed to the internal pattern state machine. As a consequence, the produced output will be correct regardless of the order in which rows are appended to the table. Instead, the pattern is evaluated in the order specified by the time contained in each row.

The `MATCH_RECOGNIZE` clause assumes a [time attribute](../../concepts/timely-stream-processing.html#flink-sql-time-attributes) with ascending ordering as the first argument to `ORDER BY` clause.

For the example `Ticker` table, a definition like `ORDER BY rowtime ASC, price DESC` is valid but `ORDER BY price, rowtime` or `ORDER BY rowtime DESC, price ASC` is not.

## Define and measures¶

The `DEFINE` and `MEASURES` keywords have similar meanings to the `WHERE` and `SELECT` clauses in a simple SQL query.

The `MEASURES` clause defines what will be included in the output of a matching pattern. It can project columns and define expressions for evaluation. The number of produced rows depends on the output mode setting.

The `DEFINE` clause specifies conditions that rows have to fulfill in order to be classified to a corresponding pattern variable. If a condition isn’t defined for a pattern variable, a default condition is used, which evaluates to TRUE for every row.

For a more detailed explanation about expressions that can be used in those clauses, see event stream navigation.

### Aggregations¶

Aggregations can be used in `DEFINE` and `MEASURES` clauses. [Built-in functions](../functions/overview.html#flink-sql-functions-overview) are supported.

Aggregate functions are applied to each subset of rows mapped to a match. To understand how these subsets are evaluated, see event stream navigation section.

The task of the following example is to find the longest period of time for which the average price of a ticker did not go below a certain threshold. It shows how expressible `MATCH_RECOGNIZE` can become with aggregations. The following query performs this task.

    SELECT *
    FROM Ticker
        MATCH_RECOGNIZE (
            PARTITION BY symbol
            ORDER BY rowtime
            MEASURES
                FIRST(A.rowtime) AS start_tstamp,
                LAST(A.rowtime) AS end_tstamp,
                AVG(A.price) AS avgPrice
            ONE ROW PER MATCH
            AFTER MATCH SKIP PAST LAST ROW
            PATTERN (A+ B)
            DEFINE
                A AS AVG(A.price) < 15
        ) MR;

Given this query and following input values:

    symbol         rowtime         price    tax
    ======  ====================  ======= =======
    'ACME'  '01-Apr-11 10:00:00'   12      1
    'ACME'  '01-Apr-11 10:00:01'   17      2
    'ACME'  '01-Apr-11 10:00:02'   13      1
    'ACME'  '01-Apr-11 10:00:03'   16      3
    'ACME'  '01-Apr-11 10:00:04'   25      2
    'ACME'  '01-Apr-11 10:00:05'   2       1
    'ACME'  '01-Apr-11 10:00:06'   4       1
    'ACME'  '01-Apr-11 10:00:07'   10      2
    'ACME'  '01-Apr-11 10:00:08'   15      2
    'ACME'  '01-Apr-11 10:00:09'   25      2
    'ACME'  '01-Apr-11 10:00:10'   25      1
    'ACME'  '01-Apr-11 10:00:11'   30      1

The query accumulates events as part of the pattern variable `A`, as long as their average price doesn’t exceed `15`. For example, such a limit exceeding happens at `01-Apr-11 10:00:04`. The following period exceeds the average price of `15` again at `01-Apr-11 10:00:11`.

Here are results of the query:

     symbol       start_tstamp       end_tstamp          avgPrice
    =========  ==================  ==================  ============
    ACME       01-APR-11 10:00:00  01-APR-11 10:00:03     14.5
    ACME       01-APR-11 10:00:05  01-APR-11 10:00:10     13.5

Aggregations can be applied to expressions, but only if they reference a single pattern variable. For example, `SUM(A.price * A.tax)` is valid, but `AVG(A.price * B.tax)` is not.

Note

`DISTINCT` aggregations aren’t supported.

## Define a pattern¶

The `MATCH_RECOGNIZE` clause enables you to search for patterns in event streams using a powerful and expressive syntax that is somewhat similar to the widely used regular expression syntax.

Every pattern is constructed from basic building blocks, called _pattern variables_ , to which operators (quantifiers and other modifiers) can be applied. The whole pattern must be enclosed in brackets.

The following SQL shows an example pattern:

    PATTERN (A B+ C* D)

You can use the following operators:

  * _Concatenation_ \- a pattern like `(A B)` means that the contiguity is strict between `A` and `B`, so there can be no rows that weren’t mapped to `A` or `B` in between.
  * _Quantifiers_ \- modify the number of rows that can be mapped to the pattern variable.
    * `*` — _0_ or more rows
    * `+` — _1_ or more rows
    * `?` — _0_ or _1_ rows
    * `{ n }` — exactly _n_ rows (_n > 0_)
    * `{ n, }` — _n_ or more rows (_n ≥ 0_)
    * `{ n, m }` — between _n_ and _m_ (inclusive) rows (_0 ≤ n ≤ m, 0 < m_)
    * `{ , m }` — between _0_ and _m_ (inclusive) rows (_m > 0_)

Important

Patterns that can potentially produce an empty match aren’t supported. For example, patterns like these produce an empty match:

    PATTERN (A*)
    PATTERN (A? B*)
    PATTERN (A{0,} B{0,} C*)

### Greedy and reluctant quantifiers¶

Each quantifier can be either _greedy_ (default behavior) or _reluctant_. Greedy quantifiers try to match as many rows as possible, while reluctant quantifiers try to match as few as possible.

To see the difference, the following example shows a query where a greedy quantifier is applied to the `B` variable:

    SELECT *
    FROM Ticker
        MATCH_RECOGNIZE(
            PARTITION BY symbol
            ORDER BY rowtime
            MEASURES
                C.price AS lastPrice
            ONE ROW PER MATCH
            AFTER MATCH SKIP PAST LAST ROW
            PATTERN (A B* C)
            DEFINE
                A AS A.price > 10,
                B AS B.price < 15,
                C AS C.price > 12
        )

Given the following input:

     symbol  tax   price          rowtime
    ======= ===== ======== =====================
     XYZ     1     10       2018-09-17 10:00:02
     XYZ     2     11       2018-09-17 10:00:03
     XYZ     1     12       2018-09-17 10:00:04
     XYZ     2     13       2018-09-17 10:00:05
     XYZ     1     14       2018-09-17 10:00:06
     XYZ     2     16       2018-09-17 10:00:07

The example pattern produces the following output:

     symbol   lastPrice
    ======== ===========
     XYZ      16

If the query is modified to be reluctant, changing `B*` to `B*?`, it produces the following output:

     symbol   lastPrice
    ======== ===========
     XYZ      13
     XYZ      16

The pattern variable `B` matches only the row with price _12_ instead of swallowing the rows with prices _12_ , _13_ , and _14_.

You can’t use a greedy quantifier for the last variable of a pattern. So a pattern like `(A B*)` isn’t valid. You can work around this limitation by introducing an artificial state, like `C`, that has a negated condition of `B`. The following query shows an example.

    PATTERN (A B* C)
    DEFINE
        A AS condA(),
        B AS condB(),
        C AS NOT condB()

Note

The optional-reluctant quantifier (`A??` or `A{0,1}?`) isn’t supported.

### Time constraint¶

Especially for streaming use cases, it’s often required that a pattern finishes within a given period of time. This enables limiting the overall state size that Flink must maintain internally, even in the case of greedy quantifiers.

For this reason, Flink SQL supports the additional (non-standard SQL) `WITHIN` clause for defining a time constraint for a pattern. The clause can be defined after the `PATTERN` clause and takes an interval of millisecond resolution.

If the time between the first and last event of a potential match is longer than the given value, a match isn’t appended to the result table.

Note

It’s good practice to use the `WITHIN` clause, because it helps Flink with efficient memory management. Underlying state can be pruned once the threshold is reached.

But the `WITHIN` clause isn’t part of the SQL standard. The recommended way of dealing with time constraints might change in the future.

The following example query shows the `WITHIN` clause used with `MATCH_RECOGNIZE`.

    SELECT *
    FROM Ticker
        MATCH_RECOGNIZE(
            PARTITION BY symbol
            ORDER BY rowtime
            MEASURES
                C.rowtime AS dropTime,
                A.price - C.price AS dropDiff
            ONE ROW PER MATCH
            AFTER MATCH SKIP PAST LAST ROW
            PATTERN (A B* C) WITHIN INTERVAL '1' HOUR
            DEFINE
                B AS B.price > A.price - 10,
                C AS C.price < A.price - 10
        )

The query detects a price drop of _10_ that happens within an interval of _1_ hour.

Assume the query is used to analyze the following ticker data.

    symbol         rowtime         price    tax
    ======  ====================  ======= =======
    'ACME'  '01-Apr-11 10:00:00'   20      1
    'ACME'  '01-Apr-11 10:20:00'   17      2
    'ACME'  '01-Apr-11 10:40:00'   18      1
    'ACME'  '01-Apr-11 11:00:00'   11      3
    'ACME'  '01-Apr-11 11:20:00'   14      2
    'ACME'  '01-Apr-11 11:40:00'   9       1
    'ACME'  '01-Apr-11 12:00:00'   15      1
    'ACME'  '01-Apr-11 12:20:00'   14      2
    'ACME'  '01-Apr-11 12:40:00'   24      2
    'ACME'  '01-Apr-11 13:00:00'   1       2
    'ACME'  '01-Apr-11 13:20:00'   19      1

The query produces the following results:

    symbol         dropTime         dropDiff
    ======  ====================  =============
    'ACME'  '01-Apr-11 13:00:00'      14

The resulting row represents a price drop from _15_ (at `01-Apr-11 12:00:00`) to `1` (at `01-Apr-11 13:00:00`). The `dropDiff` column contains the price difference.

Even though prices also drop by higher values, for example, by _11_ (between `01-Apr-11 10:00:00` and `01-Apr-11 11:40:00`), the time difference between those two events is larger than _1_ hour, they don’t produce a match.

## Output mode¶

The _output mode_ describes how many rows should be emitted for every found match. The SQL standard describes two modes:

  * `ALL ROWS PER MATCH`
  * `ONE ROW PER MATCH`

In Flink SQL, the only supported output mode is `ONE ROW PER MATCH`, and it always produces one output summary row for each found match.

The schema of the output row is a concatenation of `[partitioning columns] + [measures columns]`, in that order.

The following example shows the output of a query defined as:

    SELECT *
    FROM Ticker
        MATCH_RECOGNIZE(
            PARTITION BY symbol
            ORDER BY rowtime
            MEASURES
                FIRST(A.price) AS startPrice,
                LAST(A.price) AS topPrice,
                B.price AS lastPrice
            ONE ROW PER MATCH
            PATTERN (A+ B)
            DEFINE
                A AS LAST(A.price, 1) IS NULL OR A.price > LAST(A.price, 1),
                B AS B.price < LAST(A.price)
        )

For the following input rows:

     symbol   tax   price          rowtime
    ======== ===== ======== =====================
     XYZ      1     10       2018-09-17 10:00:02
     XYZ      2     12       2018-09-17 10:00:03
     XYZ      1     13       2018-09-17 10:00:04
     XYZ      2     11       2018-09-17 10:00:05

The query produces the following output:

     symbol   startPrice   topPrice   lastPrice
    ======== ============ ========== ===========
     XYZ      10           13         11

The pattern recognition is partitioned by the `symbol` column. Even though not explicitly mentioned in the `MEASURES` clause, the partitioned column is added at the beginning of the result.

## Pattern navigation¶

The `DEFINE` and `MEASURES` clauses enable navigating within the list of rows that (potentially) match a pattern.

This section discusses navigation for declaring conditions or producing output results.

### Pattern variable referencing¶

A _pattern variable reference_ enables referencoing a set of rows mapped to a particular pattern variable in the `DEFINE` or `MEASURES` clauses.

For example, the expression `A.price` describes a set of rows mapped so far to `A` plus the current row, if the query tries to match the current row to `A`. If an expression in the `DEFINE` / `MEASURES` clause requires a single row, for example, `A.price` or `A.price > 10`, it selects the last value belonging to the corresponding set.

If no pattern variable is specified, for example, `SUM(price)`, an expression references the default pattern variable `*`, which references all variables in the pattern. In other words, it creates a list of all the rows mapped so far to any variable plus the current row.

#### Example¶

For a more thorough example, consider the following pattern and corresponding conditions.

    PATTERN (A B+)
    DEFINE
      A AS A.price >= 10,
      B AS B.price > A.price AND SUM(price) < 100 AND SUM(B.price) < 80

The following table describes how these conditions are evaluated for each incoming event.

The table consists of the following columns:

  * `#` \- the row identifier that uniquely identifies an incoming row in the lists `[A.price]` / `[B.price]` / `[price]`.
  * `price` \- the price of the incoming row.
  * `[A.price]`/ `[B.price]`/ `[price]` \- describe lists of rows which are used in the `DEFINE` clause to evaluate conditions.
  * `Classifier` \- the classifier of the current row which indicates the pattern variable the row is mapped to.
  * `A.price`/ `B.price`/ `SUM(price)`/ `SUM(B.price)` \- describes the result after those expressions have been evaluated.

    == ===== ========== ========= ============== ================== ======= ======= ========== ============
    #  price Classifier [A.price] [B.price]      [price]            A.price B.price SUM(price) SUM(B.price)
    == ===== ========== ========= ============== ================== ======= ======= ========== ============
    #1 10    -> A       #1        -              -                  10      -       -          -
    #2 15    -> B       #1        #2             #1, #2             10      15      25         15
    #3 20    -> B       #1        #2, #3         #1, #2, #3         10      20      45         35
    #4 31    -> B       #1        #2, #3, #4     #1, #2, #3, #4     10      31      76         66
    #5 35               #1        #2, #3, #4, #5 #1, #2, #3, #4, #5 10      35      111        101
    == ===== ========== ========= ============== ================== ======= ======= ========== ============

The table shows that the first row is mapped to pattern variable `A`, and subsequent rows are mapped to pattern variable `B`. But the last row doesn’t fulfill the `B` condition, because the sum over all mapped rows, `SUM(price)`, and the sum over all rows in `B` exceed the specified thresholds.

### Logical offsets¶

_Logical offsets_ enable navigation within the events that were mapped to a particular pattern variable. This can be expressed with two corresponding functions.

Offset functions | Description  
---|---  
`LAST(variable.field, n)` | Returns the value of the field from the event that was mapped to the _n_ -th _last_ element of the variable. The counting starts at the last element mapped.  
`FIRST(variable.field, n)` | Returns the value of the field from the event that was mapped to the _n_ -th element of the variable. The counting starts at the first element mapped.  
  
#### Examples¶

For a more thorough example, consider the following pattern and corresponding conditions:

    PATTERN (A B+)
    DEFINE
      A AS A.price >= 10,
      B AS (LAST(B.price, 1) IS NULL OR B.price > LAST(B.price, 1)) AND
           (LAST(B.price, 2) IS NULL OR B.price > 2 * LAST(B.price, 2))

The following table describes how these conditions are evaluated for each incoming event.

The table consists of the following columns:

  * `price` \- the price of the incoming row.
  * `Classifier` \- the classifier of the current row which indicates the pattern variable the row is mapped to.
  * `LAST(B.price, 1)`/ `LAST(B.price, 2)` \- describes the result after these expressions have been evaluated.

    ===== ========== ================ ================ ========================================================================================
    price Classifier LAST(B.price, 1) LAST(B.price, 2) Comment
    ===== ========== ================ ================ ========================================================================================
    10    -> A
    15    -> B       null             null             Notice that ``LAST(B.price, 1)`` is null because there is still nothing mapped to ``B``.
    20    -> B       15               null
    31    -> B       20               15
    35               31               20               Not mapped because ``35 < 2 * 20``.
    ===== ========== ================ ================ ========================================================================================

It might also make sense to use the default pattern variable with logical offsets.

In this case, an offset considers all the rows mapped so far:

    PATTERN (A B? C)
    DEFINE
      B AS B.price < 20,
      C AS LAST(price, 1) < C.price

    ===== ========== ============== =====================================================================================
    price Classifier LAST(price, 1) Comment
    ===== ========== ============== =====================================================================================
    10    -> A
    15    -> B
    20    -> C       15             ``LAST(price, 1)`` is evaluated as the price of the row mapped to the ``B`` variable.
    ===== ========== ============== =====================================================================================

If the second row didn’t map to the `B` variable, the query returns the following results:

    ===== ========== ============== =====================================================================================
    price Classifier LAST(price, 1) Comment
    ===== ========== ============== =====================================================================================
    10    -> A
    20    -> C       10             ``LAST(price, 1)`` is evaluated as the price of the row mapped to the ``A`` variable.
    ===== ========== ============== =====================================================================================

It’s also possible to use multiple pattern variable references in the first argument of the `FIRST/LAST` functions. This way, you can write an expression that accesses multiple columns, but all of them must use the same pattern variable. In other words, the value of the `LAST`/ `FIRST` function must be computed in a single row.

this means that it’s possible to use `LAST(A.price * A.tax)`, but an expression like `LAST(A.price * B.tax)` is not valid.

## After-match strategy¶

The `AFTER MATCH SKIP` clause specifies where to start a new matching procedure after a complete match was found.

There are four different strategies:

  * `SKIP PAST LAST ROW` \- resumes the pattern matching at the next row after the last row of the current match.
  * `SKIP TO NEXT ROW` \- continues searching for a new match starting at the next row after the starting row of the match.
  * `SKIP TO LAST variable` \- resumes the pattern matching at the last row that is mapped to the specified pattern variable.
  * `SKIP TO FIRST variable` \- resumes the pattern matching at the first row that is mapped to the specified pattern variable.

This is also a way to specify how many matches a single event can belong to. For example, with the `SKIP PAST LAST ROW` strategy, every event can belong to at most one match.

### Examples¶

To better understand the differences between these strategies consider the following example.

For the following input rows:

     symbol   tax   price         rowtime
    ======== ===== ======= =====================
     XYZ      1     7       2018-09-17 10:00:01
     XYZ      2     9       2018-09-17 10:00:02
     XYZ      1     10      2018-09-17 10:00:03
     XYZ      2     5       2018-09-17 10:00:04
     XYZ      2     10      2018-09-17 10:00:05
     XYZ      2     7       2018-09-17 10:00:06
     XYZ      2     14      2018-09-17 10:00:07

Evaluate the following query with different strategies:

    SELECT *
    FROM Ticker
        MATCH_RECOGNIZE(
            PARTITION BY symbol
            ORDER BY rowtime
            MEASURES
                SUM(A.price) AS sumPrice,
                FIRST(rowtime) AS startTime,
                LAST(rowtime) AS endTime
            ONE ROW PER MATCH
            [AFTER MATCH STRATEGY]
            PATTERN (A+ C)
            DEFINE
                A AS SUM(A.price) < 30
        )

The query returns the sum of the prices of all rows mapped to `A` and the first and last timestamp of the overall match.

The query produces different results based on which `AFTER MATCH` strategy is used:

#### `AFTER MATCH SKIP PAST LAST ROW`¶

     symbol   sumPrice        startTime              endTime
    ======== ========== ===================== =====================
     XYZ      26         2018-09-17 10:00:01   2018-09-17 10:00:04
     XYZ      17         2018-09-17 10:00:05   2018-09-17 10:00:07

The first result matched against the rows #1, #2, #3, #4.

The second result matched against the rows #5, #6, #7.

#### `AFTER MATCH SKIP TO NEXT ROW`¶

     symbol   sumPrice        startTime              endTime
    ======== ========== ===================== =====================
     XYZ      26         2018-09-17 10:00:01   2018-09-17 10:00:04
     XYZ      24         2018-09-17 10:00:02   2018-09-17 10:00:05
     XYZ      25         2018-09-17 10:00:03   2018-09-17 10:00:06
     XYZ      22         2018-09-17 10:00:04   2018-09-17 10:00:07
     XYZ      17         2018-09-17 10:00:05   2018-09-17 10:00:07

Again, the first result matched against the rows #1, #2, #3, #4.

Compared to the previous strategy, the next match includes row #2 again for the next matching. Therefore, the second result matched against the rows #2, #3, #4, #5.

The third result matched against the rows #3, #4, #5, #6.

The forth result matched against the rows #4, #5, #6, #7.

The last result matched against the rows #5, #6, #7.

#### `AFTER MATCH SKIP TO LAST A`¶

     symbol   sumPrice        startTime              endTime
    ======== ========== ===================== =====================
     XYZ      26         2018-09-17 10:00:01   2018-09-17 10:00:04
     XYZ      25         2018-09-17 10:00:03   2018-09-17 10:00:06
     XYZ      17         2018-09-17 10:00:05   2018-09-17 10:00:07

Again, the first result matched against the rows #1, #2, #3, #4.

Compared to the previous strategy, the next match includes only row #3 (mapped to `A`) again for the next matching. Therefore, the second result matched against the rows #3, #4, #5, #6.

The last result matched against the rows #5, #6, #7.

#### `AFTER MATCH SKIP TO FIRST A`¶

This combination produces a runtime exception, because one would always try to start a new match where the last one started. This would produce an infinite loop and, so it’s not valid.

In case of the `SKIP TO FIRST/LAST variable` strategy, it may be possible that there are no rows mapped to that variable, for example, for pattern `A*`. In such cases, a runtime exception is thrown, because the standard requires a valid row to continue the matching.

## Time attributes¶

To apply some subsequent queries on top of the `MATCH_RECOGNIZE` it may be necessary to use [time attributes](../../concepts/timely-stream-processing.html#flink-sql-time-attributes). There are two functions for selecting these:

`MATCH_ROWTIME([rowtime_field])`

Returns the timestamp of the last row that was mapped to the given pattern.

The function accepts zero or one operand, which is a field reference with rowtime attribute. If there is no operand, the function returns the rowtime attribute with TIMESTAMP type. Otherwise, the return type is same as the operand type.

The resulting attribute is a rowtime attribute that you can use in subsequent time-based operations, like interval joins and group window or over-window aggregations.

## Control memory consumption¶

Memory consumption is an important consideration when writing `MATCH_RECOGNIZE` queries, because the space of potential matches is built in a breadth-first-like manner. This means that you must ensure that the pattern can finish, preferably with a reasonable number of rows mapped to the match, as they have to fit into memory.

For example, the pattern must not have a quantifier without an upper limit that accepts every single row. Such a pattern could look like this:

    PATTERN (A B+ C)
    DEFINE
      A as A.price > 10,
      C as C.price > 20

This query maps every incoming row to the `B` variable, so it never finishes. This query could be fixed, for example, by negating the condition for `C`:

    PATTERN (A B+ C)
    DEFINE
      A as A.price > 10,
      B as B.price <= 20,
      C as C.price > 20

Also, the query could be fixed by using the reluctant quantifier:

    PATTERN (A B+? C)
    DEFINE
      A as A.price > 10,
      C as C.price > 20

Note

The `MATCH_RECOGNIZE` clause doesn’t use a configured state retention time.

You may want to use the WITHIN clause <flink-sql-pattern-recognition-time-constraint> for this purpose.

## Known limitations¶

The Flink SQL implementation of the `MATCH_RECOGNIZE` clause is an ongoing effort, and some features of the SQL standard are not yet supported.

Unsupported features include:

  * Pattern expressions
    * Pattern groups - this means that e.g. quantifiers can not be applied to a subsequence of the pattern. Thus, `(A (B C)+)` is not a valid pattern.
    * Alterations - patterns like `PATTERN((A B | C D) E)`, which means that either a subsequence `A B` or `C D` has to be found before looking for the `E` row.
    * `PERMUTE` operator - which is equivalent to all permutations of variables that it was applied to e.g. `PATTERN (PERMUTE (A, B, C))` = `PATTERN (A B C | A C B | B A C | B C A | C A B | C B A)`.
    * Anchors - `^, $`, which denote beginning/end of a partition, those do not make sense in the streaming context and will not be supported.
    * Exclusion - `PATTERN ({- A -} B)` meaning that `A` will be looked for but will not participate in the output. This works only for the `ALL ROWS PER MATCH` mode.
    * Reluctant optional quantifier - `PATTERN A??` only the greedy optional quantifier is supported.
  * `ALL ROWS PER MATCH` output mode - which produces an output row for every row that participated in the creation of a found match. This also means:
    * The only supported semantic for the `MEASURES` clause is `FINAL`.
    * `CLASSIFIER` function, which returns the pattern variable that a row was mapped to, is not yet supported.
  * `SUBSET` \- which allows creating logical groups of pattern variables and using those groups in the `DEFINE` and `MEASURES` clauses.
  * Physical offsets - `PREV/NEXT`, which indexes all events seen rather than only those that were mapped to a pattern variable (as in the logical offsets case).
  * `MATCH_RECOGNIZE` is supported only for SQL. There is no equivalent in the Table API.
  * Aggregations
    * Distinct aggregations are not supported.

## Related content¶

  * [Time Attributes](../../concepts/timely-stream-processing.html#flink-sql-time-attributes)
  * [Flink SQL Queries](overview.html#flink-sql-queries)
  * [Flink SQL Functions](../functions/overview.html#flink-sql-functions-overview)
  * [Statements](../statements/overview.html#flink-sql-statements-overview)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
