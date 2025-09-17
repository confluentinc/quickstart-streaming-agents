---
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/drop-model.html
title: SQL DROP MODEL Statement in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'statements', 'drop-model.html']
scraped_date: 2025-09-05T13:48:51.219129
---

# DROP MODEL Statement in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables real-time inference and prediction with AI models. Use the [CREATE MODEL](create-model.html#flink-sql-create-model) statement to register an AI model.

## Syntax¶

    -- Delete the default version. The min version becomes the new default.
    DROP MODEL [IF EXISTS] [[catalog_name].[database_name]].model_name
    
    -- Delete the specified version.
    DROP MODEL [IF EXISTS] [[catalog_name].[database_name]].model_name[$version-id]
    
    -- Delete all versions and the model.
    DROP MODEL [IF EXISTS] [[catalog_name].[database_name]].model_name[$all]

## Description¶

Delete an AI model in Confluent Cloud for Apache Flink.

Use the `<model-name>$<model-version>` syntax to delete a specific version of a model. For more information, see [Model versioning](create-model.html#flink-sql-create-model-input-model-versioning).

If `version_id` is not specified, DROP deletes the default version, and the min version becomes the default version.

`DROP MODEL <model-name>$all` deletes all versions.

When the IF EXISTS clause is provided and the model or version doesn’t exist, no action is taken.

## Examples¶

    -- Delete the default version. The min version becomes the new default.
    DROP MODEL `<model-name>`;
    
    -- Delete a specific version of the model.
    DROP MODEL `<model-name>$<version>`;
    
    -- Delete all versions and the model.
    DROP MODEL `<model-name>$all`;

## Related content¶

  * [CREATE MODEL](create-model.html#flink-sql-create-model)
  * [ALTER MODEL](alter-model.html#flink-sql-alter-model)
  * [Run an AI Model](../../../ai/ai-model-inference.html#flink-sql-ai-model)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
