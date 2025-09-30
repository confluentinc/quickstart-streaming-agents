---
document_id: flink_reference_functions_ml-preprocessing-functions_chunk_2
source_file: flink_reference_functions_ml-preprocessing-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/ml-preprocessing-functions.html
title: Machine-Learning Preprocessing Functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 4
---

'', TRUE, FALSE, TRUE, 'END');

## ML_FILE_FORMAT_TEXT_SPLITTER¶

Splits text into chunks based on specific file format patterns.

Syntax

    ML_FILE_FORMAT_TEXT_SPLITTER(text, chunkSize, chunkOverlap, formatName,
    [trimWhitespace] [, keepSeparator] [, separatorPosition])

Description

The `ML_FILE_FORMAT_TEXT_SPLITTER` function splits text into chunks based on specific file format patterns. It uses format-specific separators to split code intelligently or structure text.

The returned array of chunks has the same order as the input.

The function starts splitting the chunks with the first separator in the separators list. If a chunk is bigger than `chunkSize`, the function splits the chunk recursively using the next separator in the separators list for the given file format. If separators are exhausted, and the remaining text is bigger than `chunkSize`, the function returns the smallest chunk possible, even though it is bigger than `chunkSize`.

Arguments

* **text** : The input text to be split. If the input text is `NULL`, it is returned as is.

* **chunkSize** : The size of each chunk. If `chunkSize < 0` or `chunkOverlap > chunkSize`, an exception is thrown.

* **chunkOverlap** : The number of overlapping characters between chunks. If `chunkOverlap < 0`, an exception is thrown.

* **formatName** : ENUM of the format names. Valid values are:

Valid values for formatName
    *`C`
    * `CPP`
    *`CSHARP`
    * `ELIXIR`
    *`GO`
    * `HTML`
    *`JAVA`
    * `JAVASCRIPT`
    *`JSON`
    * `KOTLIN`
    *`LATEX`
    * `MARKDOWN`
    *`PHP`
    * `PYTHON`
    *`RUBY`
    * `RUST`
    *`SCALA`
    * `SQL`
    *`SWIFT`
    * `TYPESCRIPT`
    * `XML`

* **trimWhitespace** : (Optional) Whether to trim whitespace from chunks. The default is `TRUE`.
* **keepSeparator** : (Optional) Whether to keep the separator in the chunks. The default is `FALSE`.
* **separatorPosition** : (Optional) The position of the separator. Valid values are `START` or `END`. The default is `START`. `START` means place the separator at the start of the following chunk, and `END` means place the separator at the end of the previous chunk.

Example

    -- returns ['def hello_world():\n print("Hello, World!")', '# Call the function\nhello_world()']
    SELECT ML_FILE_FORMAT_TEXT_SPLITTER('def hello_world():\n print("Hello, World!")\n\n# Call the function\nhello_world()\n', 50, 0, 'PYTHON');

## ML_LABEL_ENCODER¶

Encodes categorical variables into numerical labels.

Syntax

    ML_LABEL_ENCODER(input, categories [, includeZeroLabel])

Description
    The `ML_LABEL_ENCODER` function encodes categorical variables into numerical labels. Each unique category is assigned a unique integer label.
Arguments

* **input** : Input value to encode.
  * If the input value is `NULL`, `NaN`, or `Infinity`, it is considered in the unknown category, which is given the `0` label.
  * If the input value is not one of the `categories`, it is labeled as `-1` or `0` depending on `includeZeroLabel`: `-1` if `includeZeroLabel` is TRUE and `0` if `includeZeroLabel` is FALSE.
* **categories** : Arrays of category values to encode input value to. Category values must be the same type as the `input` value.
  * If the `categories` array is empty, all inputs are considered to be in the unknown category, which is given the `0` label.
  * The `categories` array can’t be `NULL`, or an exception is thrown.
  * The `categories` array can’t have `NULL` or duplicate values, or an exception is thrown.
  * The `categories` array must be sorted in ascending lexicographical order, or an exception is thrown.
* **includeZeroLabel** : (Optional) The start index for valid categories is `0`. The default is `FALSE`.
  * If `includeZeroLabel` is `TRUE`, the valid categories index starts at `0`, and unknown values are labeled as `-1`.
  * If `includeZeroLabel` is `FALSE`, the valid categories index starts at `1`, and unknown values are labeled as `0`.

Example

    -- returns 1
    SELECT ML_LABEL_ENCODER('abc', ARRAY['abc', 'def', 'efg', 'hikj']);

    -- returns 0
    SELECT ML_LABEL_ENCODER('abc', ARRAY['abc', 'def', 'efg', 'hikj'], TRUE );

## ML_MAX_ABS_SCALER¶

Scales numerical values by their maximum absolute value.

Syntax

    ML_MAX_ABS_SCALER(value, absoluteMax)

Description
    The `ML_MAX_ABS_SCALER` function scales numerical values by dividing them by the maximum absolute value. This preserves zero entries in sparse data.
Arguments

* **value** : Numerical expression to be scaled. If the input value is `NULL`, `NaN`, or `Infinity`, it is returned as is.
* **absoluteMax** : Absolute Maximum value of the feature data seen in the dataset.
  * If `absoluteMax` is `NULL` or `NaN`, an exception is thrown.
  * If `absoluteMax` is `Infinity`, `0` is returned.
  * If `absoluteMax` is `0`, the scaled value is returned as is.

Example

    -- returns 0.2
    SELECT ML_MAX_ABS_SCALER(1, 5);
