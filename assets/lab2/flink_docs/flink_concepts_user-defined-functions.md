---
source_url: https://docs.confluent.io/cloud/current/flink/concepts/user-defined-functions.html
title: User-defined Functions in Confluent Cloud for Apache Flink
hierarchy: ['concepts', 'user-defined-functions.html']
scraped_date: 2025-09-05T13:45:31.365787
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

## Table functions¶

Confluent Cloud for Apache Flink also supports user-defined table functions (UDTFs), which take multiple scalar values as input arguments and return multiple rows as output, instead of a single value.

To create a user-defined table function, extend the `TableFunction` base class in `org.apache.flink.table.functions` and implement one or more of the evaluation methods, which are named `eval(...)`. Input and output data types are inferred automatically by using reflection, including the generic argument `T` of the class, for determining the output data type. Unlike scalar functions, the evaluation method itself doesn’t have a return type. Instead, a table function provides a `collect(T)` method that’s called within every evaluation method to emit zero, one, or more records.

In the [Table API](../reference/table-api.html#flink-table-api), a table function is used with the `.joinLateral(...)` or `.leftOuterJoinLateral(...)` operators. The `joinLateral` operator cross-joins each row from the outer table (the table on the left of the operator) with all rows produced by the table-valued function (on the right side of the operator). The `leftOuterJoinLateral` operator joins each row from the outer table with all rows produced by the table-valued function and preserves outer rows, for which the table function returns an empty table.

Note

User-defined table functions are distinct from the [Table API](../reference/table-api.html#flink-table-api) but can be used in Table API code.

In SQL, use `LATERAL TABLE(<TableFunction>)` with `JOIN` or `LEFT JOIN` with an `ON TRUE` join condition.

The following code example shows how to implement a simple string splitting function.

    import org.apache.flink.table.annotation.DataTypeHint;
    import org.apache.flink.table.annotation.FunctionHint;
    import org.apache.flink.table.api.*;
    import org.apache.flink.table.functions.TableFunction;
    import org.apache.flink.types.Row;
    import static org.apache.flink.table.api.Expressions.*;
    
    @FunctionHint(output = @DataTypeHint("ROW<word STRING, length INT>"))
    public static class SplitFunction extends TableFunction<Row> {
    
      public void eval(String str) {
        for (String s : str.split(" ")) {
          // use collect(...) to emit a row
          collect(Row.of(s, s.length()));
        }
      }
    }

The following example shows how to call the `SplitFunction` UDTF in a Flink SQL statement.

    SELECT myField, word, length
    FROM MyTable
    LEFT JOIN LATERAL TABLE(SplitFunction(myField)) ON TRUE;

To build and upload a user-defined table function to Confluent Cloud for Apache Flink for use in Flink SQL, see [Create a User Defined Table Function](../how-to-guides/create-udf.html#flink-sql-implement-udtf-function).

## Implementation considerations¶

All UDFs adhere to a few common implementation principles, which are described in the following sections.

  * Function class
  * Evaluation methods
  * Type inference
  * Named parameters
  * Scalar functions
  * Table functions

The following code example shows how to implement a simple scalar function and how to call it in Flink SQL.

For the [Table API](../reference/table-api.html#flink-table-api), you can register the function in code and invoke it.

For SQL queries, your UDF must be registered by using the [CREATE FUNCTION](../reference/statements/create-function.html#flink-sql-create-function) statement. For more information, see [Create a User-defined Function](../how-to-guides/create-udf.html#flink-sql-create-udf).

    import org.apache.flink.table.api.*;
    import org.apache.flink.table.functions.ScalarFunction;
    import static org.apache.flink.table.api.Expressions.*;
    
    // define function logic
    public static class SubstringFunction extends ScalarFunction {
      public String eval(String s, Integer begin, Integer end) {
        return s.substring(begin, end);
      }
    }

The following example shows how to call the `SubstringFunction` UDF in a Flink SQL statement.

    SELECT SubstringFunction('test string', 2, 5);

### Function class¶

Your implementation class must extend one of the system-provided base classes.

  * Scalar functions extend the `org.apache.flink.table.functions.ScalarFunction` class.
  * Table functions extend the `org.apache.flink.table.functions.TableFunction` class.

The class must be declared public, not abstract, and must be accessible globally. Non-static inner or anonymous classes are not supported.

### Evaluation methods¶

You define the behavior of a scalar function by implementing a custom evaluation method, named `eval`, which must be declared `public`. You can overload evaluation methods by implementing multiple methods named `eval`.

The evaluation method is called by code-generated operators during runtime.

Regular JVM method-calling semantics apply, so these implementation options are available:

  * You can implement overloaded methods, like `eval(Integer)` and `eval(LocalDateTime)`.
  * You can use var-args, like `eval(Integer...)`.
  * You can use object inheritance, like `eval(Object)` that takes both `LocalDateTime` and `Integer`.
  * You can use combinations of these, like `eval(Object...)` that takes all kinds of arguments.

The `ScalarFunction` base class provides a set of optional methods that you can override, `open()`, `close()`, `isDeterministic()`, and `supportsConstantFolding()`. You can use the `open()` method for initialization work and the `close()` method for cleanup work.

Internally, Table API and SQL code generation works with primitive values where possible. To reduce overhead during runtime, a user-defined scalar function should declare parameters and result types as primitive types instead of their boxed classes. For example, DATE/TIME is equal to `int`, and TIMESTAMP is equal to `long`.

The following code example shows a user-defined function that has overloaded `eval` methods.

    import org.apache.flink.table.functions.ScalarFunction;
    
    // function with overloaded evaluation methods
    public static class SumFunction extends ScalarFunction {
    
      public Integer eval(Integer a, Integer b) {
        return a + b;
      }
    
      public Integer eval(String a, String b) {
        return Integer.valueOf(a) + Integer.valueOf(b);
      }
    
      public Integer eval(Double... d) {
        double result = 0;
        for (double value : d)
          result += value;
        return (int) result;
      }
    }

### Type inference¶

The Table API is strongly typed, so both function parameters and return types must be mapped to a data type.

The Flink planner needs information about expected types, precision, and scale. Also it needs information about how internal data structures are represented as JVM objects when calling a user-defined function.

_Type inference_ is the process of validating input arguments and deriving data types for both the parameters and the result of a function.

User-defined functions in Flink implement automatic type-inference extraction that derives data types from the function’s class and its evaluation methods by using reflection. If this implicit extraction approach with reflection fails, you can help the extraction process by annotating affected parameters, classes, or methods with `@DataTypeHint` and `@FunctionHint`.

#### Automatic type inference¶

Automatic type inference inspects the function’s class and evaluation methods to derive data types for the arguments and return value of a function. The `@DataTypeHint` and `@FunctionHint` annotations support automatic extraction.

For a list of classes that implicitly map to a data type, see [Data type extraction](../reference/datatypes.html#flink-sql-data-type-extraction).

#### Data type hints¶

In some situations, you may need to support automatic extraction inline for parameters and return types of a function. In these cases you can use data type hints and the `@DataTypeHint` annotation to define data types.

The following code example shows how to use data type hints.

    import org.apache.flink.table.annotation.DataTypeHint;
    import org.apache.flink.table.annotation.InputGroup;
    import org.apache.flink.table.functions.ScalarFunction;
    import org.apache.flink.types.Row;
    
    // user-defined function that has overloaded evaluation methods.
    public static class OverloadedFunction extends ScalarFunction {
    
      // No hint required for type inference.
      public Long eval(long a, long b) {
        return a + b;
      }
    
      // Define the precision and scale of a decimal.
      public @DataTypeHint("DECIMAL(12, 3)") BigDecimal eval(double a, double b) {
        return BigDecimal.valueOf(a + b);
      }
    
      // Define a nested data type.
      @DataTypeHint("ROW<s STRING, t TIMESTAMP_LTZ(3)>")
      public Row eval(int i) {
        return Row.of(String.valueOf(i), Instant.ofEpochSecond(i));
      }
    
      // Enable wildcard input and custom serialized output.
      @DataTypeHint(value = "RAW", bridgedTo = ByteBuffer.class)
      public ByteBuffer eval(@DataTypeHint(inputGroup = InputGroup.ANY) Object o) {
        return MyUtils.serializeToByteBuffer(o);
      }
    }

#### Function hints¶

In some situations, you may want one evaluation method to handle multiple different data types, or you may have overloaded evaluation methods with a common result type that should be declared only once.

The `@FunctionHint` annotation provides a mapping from argument data types to a result data type. It enables annotating entire function classes or evaluation methods for input, accumulator, and result data types. You can declare one or more annotations on a class or individually for each evaluation method for overloading function signatures.

All hint parameters are optional. If a parameter is not defined, the default reflection-based extraction is used. Hint parameters defined on a function class are inherited by all evaluation methods.

The following code example shows how to use function hints.

    import org.apache.flink.table.annotation.DataTypeHint;
    import org.apache.flink.table.annotation.FunctionHint;
    import org.apache.flink.table.functions.TableFunction;
    import org.apache.flink.types.Row;
    
    // User-defined function with overloaded evaluation methods
    // but globally defined output type.
    @FunctionHint(output = @DataTypeHint("ROW<s STRING, i INT>"))
    public static class OverloadedFunction extends ScalarFunction<Row> {
    
      public void eval(int a, int b) {
        collect(Row.of("Sum", a + b));
      }
    
      // Overloading arguments is still possible.
      public void eval() {
        collect(Row.of("Empty args", -1));
      }
    }
    
    // Decouples the type inference from evaluation methods.
    // The type inference is entirely determined by the function hints.
    @FunctionHint(
      input = {@DataTypeHint("INT"), @DataTypeHint("INT")},
      output = @DataTypeHint("INT")
    )
    @FunctionHint(
      input = {@DataTypeHint("BIGINT"), @DataTypeHint("BIGINT")},
      output = @DataTypeHint("BIGINT")
    )
    @FunctionHint(
      input = {},
      output = @DataTypeHint("BOOLEAN")
    )
    
    public static class OverloadedFunction extends ScalarFunction<Object> {
    
      // Ensure a method exists that the JVM can call.
      public void eval(Object... o) {
        if (o.length == 0) {
          collect(false);
        }
        collect(o[0]);
      }
    }

### Named parameters¶

When you call a user-define function, you can use parameter names to specify the values of the parameters. Named parameters enable passing both the parameter name and value to a function. This approach avoids confusion caused by incorrect parameter order, and it improves code readability and maintainability. Also, named parameters can omit optional parameters, which are filled with `null` by default. Use the `@ArgumentHint` annotation to specify the name, type, and whether a parameter is required or not.

The following code examples demonstrate how to use `@ArgumentHint` in different scopes.

  1. Use the `@ArgumentHint` annotation on the parameters of the `eval` method of the function:
         
         import com.sun.tracing.dtrace.ArgsAttributes;
         import org.apache.flink.table.annotation.ArgumentHint;
         import org.apache.flink.table.functions.ScalarFunction;
         
         public static class NamedParameterClass extends ScalarFunction {
         
             // Use the @ArgumentHint annotation to specify the name, type, and whether a parameter is required.
             public String eval(@ArgumentHint(name = "param1", isOptional = false, type = @DataTypeHint("STRING")) String s1,
                               @ArgumentHint(name = "param2", isOptional = true, type = @DataTypeHint("INT")) Integer s2) {
                 return s1 + ", " + s2;
             }
         }

  2. Use the `@ArgumentHint` annotation on the `eval` method of the function.
         
         import org.apache.flink.table.annotation.ArgumentHint;
         import org.apache.flink.table.functions.ScalarFunction;
         
         public static class NamedParameterClass extends ScalarFunction {
         
           // Use the @ArgumentHint annotation to specify the name, type, and whether a parameter is required.
           @FunctionHint(
                   argument = {@ArgumentHint(name = "param1", isOptional = false, type = @DataTypeHint("STRING")),
                           @ArgumentHint(name = "param2", isOptional = true, type = @DataTypeHint("INTEGER"))}
           )
           public String eval(String s1, Integer s2) {
             return s1 + ", " + s2;
           }
         }

  3. Use the `@ArgumentHint` annotation on the class of the function.
         
         import org.apache.flink.table.annotation.ArgumentHint;
         import org.apache.flink.table.functions.ScalarFunction;
         
         // Use the @ArgumentHint annotation to specify the name, type, and whether a parameter is required.
         @FunctionHint(
                 argument = {@ArgumentHint(name = "param1", isOptional = false, type = @DataTypeHint("STRING")),
                         @ArgumentHint(name = "param2", isOptional = true, type = @DataTypeHint("INTEGER"))}
         )
         public static class NamedParameterClass extends ScalarFunction {
         
           public String eval(String s1, Integer s2) {
             return s1 + ", " + s2;
           }
         }

The `@ArgumentHint` annotation already contains the `@DataTypeHint` annotation, so you can’t use it with `@DataTypeHint` in `@FunctionHint`. When applied to function parameters, `@ArgumentHint` can’t be used with `@DataTypeHint` at the same time, so you should use `@ArgumentHint` instead.

Named parameters take effect only when the corresponding class doesn’t contain overloaded functions and variable parameter functions, otherwise using named parameters causes an error.

### Determinism¶

Every user-defined function class can declare whether it produces deterministic results or not by overriding the `isDeterministic()` method. If the function is not purely functional, like `random()`, `date()`, or `now()`, the method must return `false`. By default, `isDeterministic()` returns `true`.

Also, the `isDeterministic()` method may influence the runtime behavior. A runtime implementation might be called at two different stages.

#### During planning¶

During planning, in the so-called _pre-flight_ phase, if a function is called with constant expressions, or if constant expressions can be derived from the given statement, a function is pre-evaluated for constant expression reduction and might not be executed on the cluster. In these cases, you can use the `isDeterministic()` method to disable constant expression reduction. For example, the following calls to ABS are executed during planning:

    SELECT ABS(-1) FROM t;
    SELECT ABS(field) FROM t WHERE field = -1;

But the following call to ABS is not executed during planning:

    SELECT ABS(field) FROM t;

#### During runtime¶

If a function is called with non-constant expressions or `isDeterministic()` returns `false`, the function is executed on the cluster.

#### System function determinism¶

The determinism of system (built-in) functions is immutable. According to Apache Calcite’s `SqlOperator` definition, there are two kinds of functions which are not deterministic: _dynamic_ functions and _non-deterministic_ functions.

    /**
     * Returns whether a call to this operator is guaranteed to always return
     * the same result given the same operands; true is assumed by default.
     */
    public boolean isDeterministic() {
      return true;
    }
    
    /**
     * Returns whether it is unsafe to cache query plans referencing this
     * operator; false is assumed by default.
     */
    public boolean isDynamicFunction() {
      return false;
    }

The `isDeterministic()` method indicates the determinism of a function is evaluated per-record during runtime if it returns `false`.

The `isDynamicFunction()` method implies the function can be evaluated only at query-start if it returns `true`. It will be pre-evaluated during planning only for batch mode. For streaming mode, it is equivalent to a non-deterministic function, because the query is executed continuously under the abstraction of a continuous query over [dynamic tables](dynamic-tables.html#flink-sql-dynamic-tables), so the dynamic functions are also re-evaluated for each query execution, which is equivalent to per-record in the current implementation.

The `isDynamicFunction` method applies only to system functions.

The following system functions are always non-deterministic, which means they are evaluated per-record during runtime, both in batch and streaming mode.

  * CURRENT_ROW_TIMESTAMP
  * RAND
  * RAND_INTEGER
  * UNIX_TIMESTAMP
  * UUID

The following system temporal functions are dynamic and are pre-evaluated during planning (query-start) for batch mode and evaluated per-record for streaming mode.

  * CURRENT_DATE
  * CURRENT_TIME
  * CURRENT_TIMESTAMP
  * LOCALTIME
  * LOCALTIMESTAMP
  * NOW

## UDF regional availability¶

Flink UDFs are available in the following AWS regions.

  * ap-east-1
  * ap-northeast-2
  * ap-south-1
  * ap-southeast-1
  * ap-southeast-2
  * ca-central-1
  * eu-central-1
  * eu-central-2
  * eu-north-1
  * eu-west-1
  * eu-west-2
  * me-south-1
  * sa-east-1
  * us-east-1
  * us-east-2
  * us-west-2

Flink UDFs are available in the following Azure regions.

  * australiaeast
  * brazilsouth
  * centralindia
  * centralus
  * eastus
  * eastus2
  * francecentral
  * northeurope
  * southcentralus
  * southeastasia
  * spaincentral
  * uaenorth
  * uksouth
  * westeurope
  * westus2
  * westus3

## UDF limitations¶

User-defined functions have the following limitations.

  * Confluent CLI version 4.13.0 or later is required.
  * External network calls from UDFs are not supported.
  * JDK 17 is the latest supported Java version for uploaded JAR files.
  * Each Flink statement can have no more than 10 UDFs.
  * Each organization/cloud/region/environment can have no more than 100 Flink artifacts.
  * The size limit of each artifact is 100 MB.
  * Aggregates are not supported.
  * Table aggregates are not supported.
  * Temporary functions are not supported.
  * The ALTER FUNCTION statement is not supported.
  * UDFs can’t be used in combination with [MATCH_RECOGNIZE](../reference/queries/match_recognize.html#flink-sql-pattern-recognition).
  * Vararg functions are not supported.
  * User-defined structured types are not supported.
  * Python is not supported.
  * Both inputs and outputs of the UDF have a row-size limit of 4MB.
  * Custom type inference is not supported.
  * Constant expression reduction is not supported.
  * The UDF feature is optimized for streaming processing, so the initial query may be slow, but after the initial query, a UDF runs with low latency.

### File system access limitations¶

The file system is read-only in the runtime environment. UDFs can’t create, write, or modify files on the file system. This includes temporary files, model files, or any other file operations. Libraries that require file system write access, like those using JNI/native binaries that extract files from JARs, are not supported.

### JNI and native binary limitations¶

Libraries that use Java Native Interface (JNI) or require native binaries are not supported due to filesystem restrictions and potential architecture compatibility issues.

## UDF logging limitations¶

  * **Public Kafka destinations only:** Private networked cluster types aren’t supported as logging destinations.
  * **Log4j logging only:** External UDF loggers can be composed only with the Apache Log4j logging framework.
  * **Burst rate to 1000/s** : UDF logging supports up to 1000 log events per second for each UDF during a short burst of high activity. This helps to optimize performance and to reduce noise in logs. Events that exceed the maximum rate are dropped.

## Related content¶

  * [CREATE FUNCTION](../reference/statements/create-function.html#flink-sql-create-function)
  * [Create a User-defined Function](../how-to-guides/create-udf.html#flink-sql-create-udf).
  * [Flink SQL Queries](../reference/queries/overview.html#flink-sql-queries)
  * [Flink UDF Java Examples](https://github.com/confluentinc/flink-udf-java-examples)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
