---
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/overview.html
title: SQL Queries in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'queries', 'overview.html']
scraped_date: 2025-09-05T13:48:20.757806
---

# Flink SQL Queries in Confluent Cloud for Apache Flink¶

In Confluent Cloud for Apache Flink®, Data Manipulation Language (DML) statements, also known as _queries_ , are declarative verbs that read and modify data in Apache Flink® tables.

Unlike Data Definition Language (DDL) statements, DML statements modify only data and don’t change metadata. When you want to change metadata, use [DDL statements](../../concepts/statements.html#flink-sql-statements).

These are the available DML statements in Confluent Cloud for Flink SQL.

[Deduplication Queries in Confluent Cloud for Apache Flink](deduplication.html#flink-sql-deduplication) | [Group Aggregation Queries in Confluent Cloud for Apache Flink](group-aggregation.html#flink-sql-group-aggregation) | [INSERT INTO FROM SELECT Statement in Confluent Cloud for Apache Flink](insert-into-from-select.html#flink-sql-insert-into-from-select-statement) | [INSERT VALUES Statement in Confluent Cloud for Apache Flink](insert-values.html#flink-sql-insert-values-statement)
---|---|---|---
[Interval joins](joins.html#flink-sql-interval-joins) | [LIMIT Clause in Confluent Cloud for Apache Flink](limit.html#flink-sql-limit) | [EXECUTE STATEMENT SET in Confluent Cloud for Apache Flink](statement-set.html#flink-sql-statement-set) | [ORDER BY Clause in Confluent Cloud for Apache Flink](orderby.html#flink-sql-order-by)
[Pattern Recognition Queries in Confluent Cloud for Apache Flink](match_recognize.html#flink-sql-pattern-recognition) | [Regular joins](joins.html#flink-sql-regular-joins) | [SELECT Statement in Confluent Cloud for Apache Flink](select.html#flink-sql-select) | [Set Logic in Confluent Cloud for Apache Flink](set-logic.html#flink-sql-set-logic)
[Temporal joins](joins.html#flink-sql-temporal-joins) | [Top-N Queries in Confluent Cloud for Apache Flink](topn.html#flink-sql-top-n) | [Window Aggregation Queries in Confluent Cloud for Apache Flink](window-aggregation.html#flink-sql-window-aggregation) | [Window Deduplication Queries in Confluent Cloud for Apache Flink](window-deduplication.html#flink-sql-window-deduplication)
[Window Join Queries in Confluent Cloud for Apache Flink](window-join.html#flink-sql-window-join) | [Window Top-N Queries in Confluent Cloud for Apache Flink](window-topn.html#flink-sql-window-top-n) | [Windowing Table-Valued Functions (Windowing TVFs) in Confluent Cloud for Apache Flink](window-tvf.html#flink-sql-window-tvfs) | [WITH Clause in Confluent Cloud for Apache Flink](with.html#flink-sql-with)

## Prerequisites¶

You need the following prerequisites to use Confluent Cloud for Apache Flink.

* Access to Confluent Cloud.

* The organization ID, environment ID, and compute pool ID for your organization.

* The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, reach out to your OrganizationAdmin or EnvironmentAdmin.

* The Confluent CLI. To use the Flink SQL shell, update to the latest version of the Confluent CLI by running the following command:

        confluent update --yes

If you used homebrew to install the Confluent CLI, update the CLI by using the `brew upgrade` command, instead of `confluent update`.

For more information, see [Confluent CLI](https://docs.confluent.io/confluent-cli/current/overview.html).

## Use a workspace or the Flink SQL shell¶

You can run queries and statements either in a Confluent Cloud Console workspace or in the Flink SQL shell.

* To run queries in the Confluent Cloud Console, follow these steps.

    1. Log in to the Confluent Cloud Console.

    2. Navigate to the **Environments** page.

    3. Click the tile that has the environment where your Flink compute pools are provisioned.

    4. Click **Flink**. The **Compute Pools** list opens.

    5. In the compute pool where you want to run statements, click **Open SQL workspace**.

The workspace opens with a cell for editing SQL statements.

* To run queries in the Flink SQL shell, run the following command:

        confluent flink shell --compute-pool <compute-pool-id> --environment <env-id>

You’re ready to run your first Flink SQL query.

## Hello SQL¶

Run the following simple query to print “Hello SQL”.

    SELECT 'Hello SQL';

Your output should resemble:

    EXPR$0
    Hello SQL

Run the following query to aggregate values in a table.

    SELECT Name, COUNT(*) AS Num
    FROM
      (VALUES ('Neo'), ('Trinity'), ('Morpheus'), ('Trinity')) AS NameTable(Name)
    GROUP BY Name;

Your output should resemble:

    Name     Num
    Neo      1
    Morpheus 1
    Trinity  2

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

## Syntax¶

Flink parses SQL using [Apache Calcite](https://calcite.apache.org/docs/reference.html), which supports standard ANSI SQL.

The following BNF-grammar describes the superset of supported SQL features.

    query:
        values
      | WITH withItem [ , withItem ]* query
      | {
            select
          | selectWithoutFrom
          | query UNION [ ALL ] query
          | query EXCEPT query
          | query INTERSECT query
        }
        [ ORDER BY orderItem [, orderItem ]* ]
        [ LIMIT { count | ALL } ]
        [ OFFSET start { ROW | ROWS } ]
        [ FETCH { FIRST | NEXT } [ count ] { ROW | ROWS } ONLY]

    withItem:
        name
        [ '(' column [, column ]* ')' ]
        AS '(' query ')'

    orderItem:
        expression [ ASC | DESC ]

    select:
        SELECT [ ALL | DISTINCT ]
        { * | projectItem [, projectItem ]* }
        FROM tableExpression
        [ WHERE booleanExpression ]
        [ GROUP BY { groupItem [, groupItem ]* } ]
        [ HAVING booleanExpression ]
        [ WINDOW windowName AS windowSpec [, windowName AS windowSpec ]* ]

    selectWithoutFrom:
        SELECT [ ALL | DISTINCT ]
        { * | projectItem [, projectItem ]* }

    projectItem:
        expression [ [ AS ] columnAlias ]
      | tableAlias . *

    tableExpression:
        tableReference [, tableReference ]*
      | tableExpression [ NATURAL ] [ LEFT | RIGHT | FULL ] JOIN tableExpression [ joinCondition ]

    joinCondition:
        ON booleanExpression
      | USING '(' column [, column ]* ')'

    tableReference:
        tablePrimary
        [ matchRecognize ]
        [ [ AS ] alias [ '(' columnAlias [, columnAlias ]* ')' ] ]

    tablePrimary:
        [ TABLE ] tablePath [ dynamicTableOptions ] [systemTimePeriod] [[AS] correlationName]
      | LATERAL TABLE '(' functionName '(' expression [, expression ]* ')' ')'
      | [ LATERAL ] '(' query ')'
      | UNNEST '(' expression ')'

    tablePath:
        [ [ catalogName . ] databaseName . ] tableName

    systemTimePeriod:
        FOR SYSTEM_TIME AS OF dateTimeExpression

    dynamicTableOptions:
        /*+ OPTIONS(key=val [, key=val]*) */

    key:
        stringLiteral

    val:
        stringLiteral

    values:
        VALUES expression [, expression ]*

    groupItem:
        expression
      | '(' ')'
      | '(' expression [, expression ]* ')'
      | CUBE '(' expression [, expression ]* ')'
      | ROLLUP '(' expression [, expression ]* ')'
      | GROUPING SETS '(' groupItem [, groupItem ]* ')'

    windowRef:
        windowName
      | windowSpec

    windowSpec:
        [ windowName ]
        '('
        [ ORDER BY orderItem [, orderItem ]* ]
        [ PARTITION BY expression [, expression ]* ]
        [
            RANGE numericOrIntervalExpression {PRECEDING}
          | ROWS numericExpression {PRECEDING}
        ]
        ')'

    matchRecognize:
        MATCH_RECOGNIZE '('
        [ PARTITION BY expression [, expression ]* ]
        [ ORDER BY orderItem [, orderItem ]* ]
        [ MEASURES measureColumn [, measureColumn ]* ]
        [ ONE ROW PER MATCH ]
        [ AFTER MATCH
          ( SKIP TO NEXT ROW
          | SKIP PAST LAST ROW
          | SKIP TO FIRST variable
          | SKIP TO LAST variable
          | SKIP TO variable )
        ]
        PATTERN '(' pattern ')'
        [ WITHIN intervalLiteral ]
        DEFINE variable AS condition [, variable AS condition ]*
        ')'

    measureColumn:
        expression AS alias

    pattern:
        patternTerm [ '|' patternTerm ]*

    patternTerm:
        patternFactor [ patternFactor ]*

    patternFactor:
        variable [ patternQuantifier ]

    patternQuantifier:
        '*'
      | '*?'
      | '+'
      | '+?'
      | '?'
      | '??'
      | '{' { [ minRepeat ], [ maxRepeat ] } '}' ['?']
      | '{' repeat '}'

    statementSet:
        EXECUTE STATEMENT SET
        BEGIN
          { insertStatement ';' }+
        END ';'

Flink uses a lexical policy for identifier (table, attribute, function names) that’s similar to Java.

* The case of identifiers is preserved whether or not they are quoted.

* After which, identifiers are matched case-sensitively.

* Unlike Java, back-ticks enable identifiers to contain non-alphanumeric characters, for example:

        SELECT a AS `my field` FROM t;

String literals must be enclosed in single quotes, for example, `SELECT 'Hello World'`. Duplicate a single quote for escaping, for example, `SELECT 'It''s me'`.

    SELECT 'Hello World', 'It''s me';

Your output should resemble:

    EXPR$0      EXPR$1
    Hello World It's me

Unicode characters are supported in string literals. If explicit unicode code points are required, use the following syntax.

Use the backslash (`\`) as the escaping character (default), for example, `SELECT U&'\263A'`:

    SELECT U&'\263A';

Your output should resemble:

    EXPR$0
    ☺

Also, you can use a custom escaping character with UESCAPE, for example, `SELECT U&'#2713' UESCAPE '#'`:

    SELECT U&'#2713' UESCAPE '#';

Your output should resemble:

    EXPR$0
    ✓
