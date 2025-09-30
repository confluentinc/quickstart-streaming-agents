---
document_id: flink_reference_queries_overview_chunk_3
source_file: flink_reference_queries_overview.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/overview.html
title: SQL Queries in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

results into the system memory.

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
