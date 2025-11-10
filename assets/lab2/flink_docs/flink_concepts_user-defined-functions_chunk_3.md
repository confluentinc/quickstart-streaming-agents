---
document_id: flink_concepts_user-defined-functions_chunk_3
source_file: flink_concepts_user-defined-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/user-defined-functions.html
title: User-defined Functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 6
---

a User Defined Table Function](../how-to-guides/create-udf.html#flink-sql-implement-udtf-function).

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
