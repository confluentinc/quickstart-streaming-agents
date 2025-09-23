---
document_id: flink_reference_table-api_chunk_4
source_file: flink_reference_table-api.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/table-api.html
title: Table API on Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 5
---

import ConfluentSettings settings = ConfluentSettings.from_global_variables()

## Confluent utilities¶

The `ConfluentTools` class provides more methods that you can use for developing and testing Table API programs.

### `ConfluentTools.collectChangelog` and `ConfluentTools.printChangelog`¶

Runs the specified table transformations on Confluent Cloud and returns the results locally as a list of changelog rows or prints to the console in a table style.

These methods run `table.execute().collect()` and consume a fixed number of rows from the returned iterator.

These methods can work on both finite and infinite input tables. If the pipeline is potentially unbounded, they stop fetching after the desired number of rows has been reached.

JavaPython

    // On a Table object
    Table table = env.from("examples.marketplace.customers");
    List<Row> rows = ConfluentTools.collectMaterialized(table, 100);
    ConfluentTools.printMaterialized(table, 100);

    // On a TableResult object
    TableResult tableResult = env.executeSql("SELECT * FROM examples.marketplace.customers");
    List<Row> rows = ConfluentTools.collectMaterialized(tableResult, 100);
    ConfluentTools.printMaterialized(tableResult, 100);

    // For finite (i.e. bounded) tables
    ConfluentTools.collectMaterialized(table);
    ConfluentTools.printMaterialized(table);

    from pyflink.table.confluent import ConfluentSettings, ConfluentTools
    from pyflink.table import TableEnvironment

    settings = ConfluentSettings.from_global_variables()
    env = TableEnvironment.create(settings)
    # On a Table object
    table = env.from_path("examples.marketplace.customers")
    rows = ConfluentTools.collect_changelog_limit(table, 100)
    ConfluentTools.print_changelog_limit(table, 100)

    # On a TableResult object
    tableResult = env.execute_sql("SELECT * FROM examples.marketplace.customers")
    rows = ConfluentTools.collect_changelog_limit(tableResult, 100)
    ConfluentTools.print_changelog_limit(tableResult, 100)

    # For finite (i.e. bounded) tables
    ConfluentTools.collect_changelog(table)
    ConfluentTools.print_changelog(table)

### `ConfluentTools.collect_materialized` and `ConfluentTools.print_materialized`¶

Runs the specified table transformations on Confluent Cloud and returns the results locally as a materialized changelog. Changes are applied to an in-memory table and returned as a list of insert-only rows or printed to the console in a table style.

These methods run `table.execute().collect()` and consume a fixed number of rows from the returned iterator.

These methods can work on both finite and infinite input tables. If the pipeline is potentially unbounded, they stop fetching after the desired number of rows have been reached.

JavaPython

    // On a Table object
    Table table = env.from("examples.marketplace.customers");
    List<Row> rows = ConfluentTools.collectMaterialized(table, 100);
    ConfluentTools.printMaterialized(table, 100);

    // On a TableResult object
    TableResult tableResult = env.executeSql("SELECT * FROM examples.marketplace.customers");
    List<Row> rows = ConfluentTools.collectMaterialized(tableResult, 100);
    ConfluentTools.printMaterialized(tableResult, 100);

    // For finite (i.e. bounded) tables
    ConfluentTools.collectMaterialized(table);
    ConfluentTools.printMaterialized(table);

    from pyflink.table.confluent import ConfluentSettings, ConfluentTools
    from pyflink.table import TableEnvironment

    settings = ConfluentSettings.from_global_variables()
    env = TableEnvironment.create(settings)
    # On Table object
    table = env.from_path("examples.marketplace.customers")
    rows = ConfluentTools.collect_materialized_limit(table, 100)
    ConfluentTools.print_materialized_limit(table, 100)

    # On TableResult object
    tableResult = env.execute_sql("SELECT * FROM examples.marketplace.customers")
    rows = ConfluentTools.collect_materialized_limit(tableResult, 100)
    ConfluentTools.print_materialized_limit(tableResult, 100)

    # For finite (i.e. bounded) tables
    ConfluentTools.collect_materialized(table)
    ConfluentTools.print_materialized(table)

### `ConfluentTools.getStatementName` and `ConfluentTools.stopStatement`¶

Additional lifecycle methods for controlling statements on Confluent Cloud after they have been submitted.

JavaPython

    // On TableResult object
    TableResult tableResult = env.executeSql("SELECT * FROM examples.marketplace.customers");
    String statementName = ConfluentTools.getStatementName(tableResult);
    ConfluentTools.stopStatement(tableResult);

    // Based on statement name
    ConfluentTools.stopStatement(env, "table-api-2024-03-21-150457-36e0dbb2e366-sql");

    # On TableResult object
    table_result = env.execute_sql("SELECT * FROM examples.marketplace.customers")
    statement_name = ConfluentTools.get_statement_name(table_result)
    ConfluentTools.stop_statement(table_result)

    # Based on statement name
    ConfluentTools.stop_statement_by_name(env, "table-api-2024-03-21-150457-36e0dbb2e366-sql")
