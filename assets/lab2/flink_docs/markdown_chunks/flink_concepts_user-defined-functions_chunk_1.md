---
document_id: flink_concepts_user-defined-functions_chunk_1
source_file: flink_concepts_user-defined-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/user-defined-functions.html
title: User-defined Functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 6
---

# User-defined Functions in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® supports user-defined functions (UDFs), which are extension points for running custom logic that you can’t express in the system-provided Flink SQL [queries](../reference/queries/overview.html#flink-sql-queries) or with the [Table API](../reference/table-api.html#flink-table-api).

You can implement user-defined functions in Java, and you can use third-party libraries within a UDF. Confluent Cloud for Apache Flink supports scalar functions (UDFs), which map scalar values to a new scalar value, and table functions (UDTFs), which map multiple scalar values to multiple output rows.

* **Create an example UDF:** [Create a User Defined Function](../how-to-guides/create-udf.html#flink-sql-create-udf)
* **Add logging to your UDFs:** [Enable Logging in a User Defined Function](../how-to-guides/enable-udf-logging.html#flink-sql-enable-udf-logging)
* **Availability:** UDF regional availability
* **Limitations:** UDF limitations
* **Example code:** [Flink UDF Java Examples](https://github.com/confluentinc/flink-udf-java-examples)

## Artifacts¶

Artifacts are Java packages, or JAR files, that contain user-defined functions and all of the required dependencies. Artifacts are uploaded to Confluent Cloud and scoped to a specific region in a Confluent Cloud environment. To be used for UDF, artifacts must follow a few common implementation principles, which are described in the following sections.

To use a UDF, you must register one or more functions that reference the artifact.

## Functions¶

Functions are SQL objects that reference a class in an artifact and can be used in any SQL Statement or Table API program.

Once an artifact is uploaded, you register a function by using the [CREATE FUNCTION](../reference/statements/create-function.html#flink-sql-create-function) statement.

Once a function is registered, you can invoked it from any SQL statement or Table API program.

The following example shows how to register a `TShirtSizingIsSmaller` function and invoke it in a SQL statement.

    -- Register the function.
    CREATE FUNCTION is_smaller
      AS 'com.example.my.TShirtSizingIsSmaller'
      USING JAR 'confluent-artifact://<artifact-id>/<version-id>';

    -- Invoke the function.
    SELECT IS_SMALLER ('L', 'M');

To build and upload a UDF to Confluent Cloud for Apache Flink for use in Flink SQL or the Table API, see [Create a UDF](../how-to-guides/create-udf.html#flink-sql-create-udf).

## RBAC¶

To upload artifacts, register functions, and invoke functions, you must have the FlinkDeveloper role or higher. For more information, see [Grant Role-Based Access](../operate-and-deploy/flink-rbac.html#flink-rbac).

## Shared responsibility¶

Confluent supports the UDF infrastructure in Confluent Cloud only. It is your responsibility to troubleshoot custom UDF issues for functions you build or that are provided to you by others. The following provides additional details about shared support responsibilities.

* **Customer Managed** : You are responsible for function logic. Confluent does not provide any support for debugging services and features within UDFs.
* **Confluent Managed** : Confluent is responsible for managing the Flink services and custom compute platform, and provides support for these.

## Scalar functions¶

A user-defined scalar function maps zero, one, or multiple scalar values to a new scalar value. You can use any data type listed in [Data Types](../reference/datatypes.html#flink-sql-datatypes) as a parameter or return type of an evaluation method.

To define a scalar function, extend the `ScalarFunction` base class in `org.apache.flink.table.functions` and implement one or more evaluation methods named `eval(...)`.

The following code example shows how to define your own hash code function.

    import org.apache.flink.table.annotation.InputGroup;
    import org.apache.flink.table.api.*;
    import org.apache.flink.table.functions.ScalarFunction;
    import static org.apache.flink.table.api.Expressions.*;

    public static class HashFunction extends ScalarFunction {

      // take any data type and return INT
      public int eval(@DataTypeHint(inputGroup = InputGroup.ANY) Object o) {
        return o.hashCode();
      }
    }

The following example shows how to call the `HashFunction` UDF in a Flink SQL statement.

    SELECT HashFunction(myField) FROM MyTable;

To build and upload a UDF to Confluent Cloud for Apache Flink for use in Flink SQL, see [Create a User Defined Function](../how-to-guides/create-udf.html#flink-sql-create-udf).
