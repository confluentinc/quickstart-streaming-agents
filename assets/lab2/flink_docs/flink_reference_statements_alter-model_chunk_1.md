---
document_id: flink_reference_statements_alter-model_chunk_1
source_file: flink_reference_statements_alter-model.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/alter-model.html
title: SQL ALTER MODEL Statement in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# ALTER MODEL Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables real-time inference and prediction with AI models. Use the [CREATE MODEL](create-model.html#flink-sql-create-model) statement to register an AI model.

## Syntax¶

    -- Rename a model.
    ALTER MODEL [IF EXISTS][catalog_name.][database_name.]model_name
    RENAME TO [catalog_name.][database_name.]new_model_name

    -- Alter model options.
    ALTER MODEL [IF EXISTS] [catalog_name.][database_name.]model_name[$version_id]
    SET (key1=val1[, key2=val2]...)

    -- Reset model options.
    ALTER MODEL [IF EXISTS] [catalog_name.][database_name.]model_name[$version_id]
    RESET (key1[, key2]...)

## Description¶

Rename an AI model or change model options.

Use the `<model_name>$<model_version>` syntax to change a specific version of a model. For more information, see [Model versioning](create-model.html#flink-sql-create-model-input-model-versioning).

ALTER MODEL options apply only to model metadata, not model data.

If the IF EXISTS clause is provided, and the model doesn’t exist, nothing happens.

If the IF EXISTS clause is provided, and the model version doesn’t exist, nothing happens.

For RESET, the specified model option keys are reset to the default value.

## Examples¶

    -- Rename a model.
    ALTER MODEL `my_model` RENAME TO `my_new_model`

    -- Check for model existence and rename if it exists.
    ALTER MODEL IF EXISTS `my_model` RENAME TO `my_new_model`

    -- Change options for version 2.
    ALTER MODEL `my_model$2` SET (
      tag = 'prod',
      description = "new_description"
    );

    -- Reset the tag option.
    ALTER MODEL `my_model` RESET (tag)
