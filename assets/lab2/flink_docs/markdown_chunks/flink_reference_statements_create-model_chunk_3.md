---
document_id: flink_reference_statements_create-model_chunk_3
source_file: flink_reference_statements_create-model.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/create-model.html
title: SQL CREATE MODEL Statement in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 7
---

see [Run an AI Model](../../../ai/ai-model-inference.html#flink-sql-ai-model).

## Model versioning¶

A model can have multiple versions. A version is an integer number that starts at 1. The default version for a new model is 1. Currently, the maximum number of supported versions is 10.

New versions are created by the CREATE MODEL statement for the same model name. A new version increments the current maximum version by 1.

To view the versions of a model, use the [DESCRIBE MODEL](describe.html#flink-sql-describe-model) statement.

Only model options are versioned, which that means input/output format and comments don’t change across versions. The statement fails if input format, output format, or comments change. For model options, model task changes are not permitted.

The following code example shows the result of running CREATE MODEL twice with the same model name.

    CREATE MODEL `my-model` ...

    -- Output
    `my-model` with version 1 created. Default version: 1

    CREATE MODEL `my-model` ...

    -- Output
    `my-model` with version 2 created. Default version: 1

By default, version 1 is the default version when a model is first created. As more versions are created by the CREATE MODEL statement, you can change the default version by using the ALTER MODEL statement.

The following example shows how to change the default version of an existing model.

    ALTER MODEL <model-name> SET ('default_version'='<version>');

You can access a specific version of a model in queries by using the `<model_name>$<model_version>` syntax. If no version is specified, the default version is used.

The following code examples show how to use a specific version of a model in a query.

    -- Use version 2 of the model.
    SELECT * FROM `my-table` LATERAL TABLE (ML_PREDICT('my-model$2', col1, col2));

    -- Use the default version of the model.
    SELECT * FROM `my-table` LATERAL TABLE (ML_PREDICT('my-model', col1, col2));

Use the `<model_name>$<model_version>` syntax to delete a specific version of a model:

    -- Delete a specific version of the model.
    DROP MODEL `<model-name>$<version>`;

    -- Delete all versions and the model.
    DROP MODEL `<model-name>$all`;

The maximum version number is the next default version. If all versions are dropped, the whole model is deleted.

To change the version of an existing model, use the [ALTER MODEL](alter-model.html#flink-sql-alter-model) statement. If no version is specified, the default version is changed.

    ALTER MODEL `<model-name>$<version>` SET ('k1'='v1', 'k2'='v2');
