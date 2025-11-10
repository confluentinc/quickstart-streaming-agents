---
document_id: flink_concepts_user-defined-functions_chunk_4
source_file: flink_concepts_user-defined-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/user-defined-functions.html
title: User-defined Functions in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 6
---

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

             // Use the @ArgumentHint annotation to specify
