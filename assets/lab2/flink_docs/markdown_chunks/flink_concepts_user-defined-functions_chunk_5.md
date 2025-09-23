---
document_id: flink_concepts_user-defined-functions_chunk_5
source_file: flink_concepts_user-defined-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/user-defined-functions.html
title: User-defined Functions in Confluent Cloud for Apache Flink
chunk_index: 5
total_chunks: 6
---

the name, type, and whether a parameter is required.
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
