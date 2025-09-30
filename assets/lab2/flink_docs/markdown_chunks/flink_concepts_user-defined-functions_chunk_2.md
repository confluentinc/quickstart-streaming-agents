---
document_id: flink_concepts_user-defined-functions_chunk_2
source_file: flink_concepts_user-defined-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/concepts/user-defined-functions.html
title: User-defined Functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 6
---

[Create a User Defined Function](../how-to-guides/create-udf.html#flink-sql-create-udf).

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
