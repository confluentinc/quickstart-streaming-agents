---
document_id: flink_jobs_sql-statements_use-interactive-shell_chunk_1
source_file: flink_jobs_sql-statements_use-interactive-shell.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/sql-statements/use-interactive-shell.html
title: Use the Interactive CLI SQL Shell with Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Use the Interactive CLI SQL Shell with Confluent Manager for Apache Flink¶

The Confluent CLI provides an interactive SQL shell that can connect to CMF and execute SQL statements. The SQL shell visualizes the results of the statements, if applicable, and is designed to support the development process of SQL statements and explorative use cases.

Important

The examples in this topic assume that CMF was installed with the examples catalog enabled (`cmf.sql.examples-catalog.enabled=true`).

## Starting the CLI SQL Shell¶

The SQL shell is started with the following Confluent CLI command:

    confluent --environment env-1 --compute-pool pool \
    --catalog examples --database marketplace \
    --flink-configuration /path/to/flink-config.json \
    flink shell

This command starts a SQL shell that creates statements in the `env-1` Environment and executes them using the pool Compute Pool. The shell sets the default catalog to examples and the default database to marketplace. All statements are configured with the Flink properties in the flink-config.json file. Of these arguments, only `environment` and `compute-pool` are required.

## Using the CLI SQL Shell¶

After the CLI SQL Shell is started, it shows a prompt and waits for user input. The user can submit all Statements that are supported by CMF, including:

  * `LIST TABLES;`
  * `LIST DATABASES;`
  * `LIST CATALOGS;`
  * `SHOW CURRENT DATABASE;`
  * `SHOW CURRENT CATALOG;`
  * `DESCRIBE <table>;`
  * `SELECT ...;`
  * `INSERT INTO ...;`

In addition, the user can execute `USE CATALOG` and `USE` commands to change the default catalog and database and `SET` commands to change properties.

Note

A statement is submitted by terminating it with a semicolon and hitting Enter.
