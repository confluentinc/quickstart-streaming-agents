---
document_id: flink_reference_keywords_chunk_1
source_file: flink_reference_keywords.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/keywords.html
title: Flink SQL Keywords in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 3
---

# Flink SQL Reserved Keywords in Confluent Cloud for Apache Flink¶

Keywords are words that have significance in Confluent Cloud for Apache Flink®. Some keywords, like AND, CHAR, and SELECT are _reserved_ and require special treatment for use as identifiers like table names, column names, and the names of built-in functions.

You can use reserved words as identifiers if you quote them with backtick characters. If you want to use one of the reserved words as a field name, enclose it with backticks, for example:

    `DATABASES`
    `RAW`

You can use _nonreserved_ keywords as identifiers without enclosing them with backticks.

In the following tables, reserved keywords are shown in **bold**.

Some string combinations are reserved as keywords for future use.

## Index¶

A | B | C | D | E
---|---|---|---|---
F | G | H | I | J
K | L | M | N | O
P | Q | R | S | T
U | V | W | X | Y
Z |  |  |  |

## A¶

A | **ABS** | ABSENT | ABSOLUTE | ACTION
---|---|---|---|---
ADA | ADD | ADMIN | AFTER | **ALL**
**ALLOCATE** | **ALLOW** | **ALTER** | ALWAYS | **AND**
**ANALYZE** | **ANY** | APPLY | **ARE** | **ARRAY**
ARRAY_AGG | ARRAY_CONCAT_AGG | **ARRAY_MAX_CARDINALITY** | **AS** | ASC
**ASENSITIVE** | ASSERTION | ASSIGNMENT | **ASYMMETRIC** | **AT**
**ATOMIC** | ATTRIBUTE | ATTRIBUTES | **AUTHORIZATION** | **AVG**

## B¶

BEFORE | **BEGIN** | **BEGIN_FRAME** | **BEGIN_PARTITION** | BERNOULLI
---|---|---|---|---
**BETWEEN** | **BIGINT** | **BINARY** | **BIT** | **BLOB**
**BOOLEAN** | **BOTH** | BREADTH | **BUCKETS** | **BY**
**BYTES** |  |  |  |

## C¶

C | **CALL** | **CALLED**
---|---|---
**CARDINALITY** | CASCADE | **CASCADED**
**CASE** | **CAST** | CATALOG
CATALOG_NAME | **CATALOGS** | **CEIL**
**CEILING** | CENTURY | CHAIN
**CHANGELOG_MODE** | **CHAR** | **CHARACTER**
CHARACTERISTICS | CHARACTERS | **CHARACTER_LENGTH**
CHARACTER_SET_CATALOG | CHARACTER_SET_NAME | CHARACTER_SET_SCHEMA
**CHAR_LENGTH** | **CHECK** | CLASS_ORIGIN
**CLASSIFIER** | **CLOB** | **CLOSE**
**COALESCE** | COBOL | **COLLATE**
COLLATION | COLLATION_CATALOG | COLLATION_NAME
COLLATION_SCHEMA | **COLLECT** | **COLUMN**
**COLUMNS** | COLUMN_NAME | COMMAND_FUNCTION
COMMAND_FUNCTION_CODE | **COMMENT** | **COMMIT**
COMMITTED | **COMPACT** | **COMPILE**
**COMPUTE** | **CONDITION** | CONDITION_NUMBER
CONDITIONAL | **CONNECT** | CONNECTION
CONNECTION_NAME | **CONSTRAINT** | CONSTRAINTS
CONSTRAINT_CATALOG | CONSTRAINT_NAME | CONSTRAINT_SCHEMA
CONSTRUCTOR | **CONTAINS** | CONTAINS_SUBSTR
CONTINUE | **CONTINUOUS** | **CONVERT**
**CORR** | **CORRESPONDING** | **COUNT**
**COVAR_POP** | **COVAR_SAMP** | **CREATE**
**CROSS** | **CUBE** | **CUME_DIST**
**CURRENT** | **CURRENT_CATALOG** | **CURRENT_DATE**
**CURRENT_DEFAULT_TRANSFORM_GROUP** | **CURRENT_PATH** | **CURRENT_ROLE**
**CURRENT_ROW** | **CURRENT_SCHEMA** | **CURRENT_TIME**
**CURRENT_TIMESTAMP** | **CURRENT_TRANSFORM_GROUP_FOR_TYPE** | **CURRENT_USER**
**CURSOR** | CURSOR_NAME | **CYCLE**

## D¶

DATA | DATABASE | **DATABASES** | **DATE**
---|---|---|---
DATE_DIFF | DATE_TRUNC | **DATETIME** | DATETIME_DIFF
DATETIME_INTERVAL_CODE | DATETIME_INTERVAL_PRECISION | **DAY** | DAYOFWEEK
DAYS | DAYOFYEAR | DATETIME_TRUNC | **DEALLOCATE**
**DEC** | DECADE | **DECIMAL** | **DECLARE**
**DEFAULT** | DEFAULTS | DEFERRABLE | DEFERRED
**DEFINE** | DEFINED | DEFINER | DEGREE
**DELETE** | **DENSE_RANK** | DEPTH | **DEREF**
DERIVED | DESC | **DESCRIBE** | DESCRIPTION
DESCRIPTOR | **DETERMINISTIC** | DIAGNOSTICS | **DISALLOW**
**DISCONNECT** | DISPATCH | **DISTINCT** | **DISTRIBUTED**
**DISTRIBUTION** | DOMAIN | DOT | **DOUBLE**
DOW | DOY | **DRAIN** | **DROP**
**DYNAMIC** | DYNAMIC_FUNCTION | DYNAMIC_FUNCTION_CODE |

## E¶

**EACH** | **ELEMENT** | **ELSE** | **EMPTY** | ENCODING
---|---|---|---|---
**END** | **END-EXEC** | **END_FRAME** | **END_PARTITION** | **ENFORCED**
EPOCH | **EQUALS** | ERROR | **ESCAPE** | **ESTIMATED_COST**
**EVERY** | **EXCEPT** | EXCEPTION | EXCLUDE | EXCLUDING
**EXEC** | **EXECUTE** | **EXISTS** | **EXP** | **EXPLAIN**
**EXTEND** | **EXTENDED** | **EXTERNAL** | **EXTRACT** |

## F¶

**FALSE** | **FETCH** | **FILTER** | FINAL | FIRST
---|---|---|---|---
**FIRST_VALUE** | **FLOAT** | **FLOOR** | FOLLOWING | **FOR**
**FOREIGN** | FORMAT | FORTRAN | FOUND | FRAC_SECOND
**FRAME_ROW** | **FREE** | **FRESHNESS** | **FRIDAY** | **FROM**
**FULL** | **FUNCTION** | **FUNCTIONS** | **FUSION** |

## G¶

G | GENERAL | GENERATED | GEOMETRY | **GET**
---|---|---|---|---
**GLOBAL** | GO | GOTO | **GRANT** | GRANTED
**GROUP** | **GROUPING** | **GROUPS** | GROUP_CONCAT |

## H¶

**HAVING** | **HASH** | HIERARCHY | **HOLD** | HOP
---|---|---|---|---
**HOUR** | HOURS |  |  |
