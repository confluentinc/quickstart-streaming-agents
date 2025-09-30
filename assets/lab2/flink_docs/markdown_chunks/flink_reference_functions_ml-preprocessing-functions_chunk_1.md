---
document_id: flink_reference_functions_ml-preprocessing-functions_chunk_1
source_file: flink_reference_functions_ml-preprocessing-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/ml-preprocessing-functions.html
title: Machine-Learning Preprocessing Functions in Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 4
---

# Machine-Learning Preprocessing Functions in Confluent Cloud for Apache Flink¶

The following built-in functions are available for ML preprocessing in Confluent Cloud for Apache Flink®. These functions help transform features into representations more suitable for downstream processors.

ML_BUCKETIZE | ML_CHARACTER_TEXT_SPLITTER | ML_FILE_FORMAT_TEXT_SPLITTER
---|---|---
ML_LABEL_ENCODER | ML_MAX_ABS_SCALER | ML_MIN_MAX_SCALER
ML_NGRAMS | ML_NORMALIZER | ML_ONE_HOT_ENCODER
ML_RECURSIVE_TEXT_SPLITTER | ML_ROBUST_SCALER | ML_STANDARD_SCALER

## ML_BUCKETIZE¶

Bucketizes numerical values into discrete bins based on split points.

Syntax

    ML_BUCKETIZE(value, splitBucketPoints [, bucketNames])

Description
    The `ML_BUCKETIZE` function divides numerical values into discrete buckets based on specified split points. Each bucket represents a range of values, and the function returns the bucket index or name for each input value.
Arguments

* **value** : Numerical expression to be bucketized. If the input value is `NaN` or `NULL`, it is bucketized to the `NULL` bucket.
* **splitBucketPoints** : Array of numerical values that define the bucket boundaries, or _split points_.
  * If the `splitBucketPoints` array is empty, an exception is thrown.
  * Any split points that are `NaN` or `NULL` are removed from the `splitBucketPoints` array.
  * `splitBucketPoints` must be in ascending order, or an exception is thrown.
  * Duplicates are removed from `splitBucketPoints`.
* **bucketNames** : (Optional) Array of names of the buckets defined in `splitBucketPoints`.
  * If the `bucketNames` array is not provided, buckets are named `bin_NULL`, `bin_1`, `bin_2` … `bin_n`, with `n` being the total number of buckets in `splitBucketPoints`.
  * If the `bucketNames` array is provided, names must be in the same order as in the `splitBucketPoints` array.
  * Names for all of the buckets must be provided, including the `NULL` bucket, or an exception is thrown.
  * If the `bucketNames` array is provided, the first name is the name for the `NULL` bucket.

Example

    -- returns 'bin_2'
    SELECT ML_BUCKETIZE(2, ARRAY[1, 4, 7]);

    -- returns 'b2'
    SELECT ML_BUCKETIZE(2, ARRAY[1, 4, 7], ARRAY['b_null','b1','b2','b3','b4']);

## ML_CHARACTER_TEXT_SPLITTER¶

Splits text into chunks based on character count and separators.

Syntax

    ML_CHARACTER_TEXT_SPLITTER(text, chunkSize, chunkOverlap, separator,
    isSeparatorRegex [, trimWhitespace] [, keepSeparator] [, separatorPosition])

Description

The `ML_CHARACTER_TEXT_SPLITTER` function splits text into chunks based on character count and specified separators. This is useful for processing large text documents into smaller, manageable pieces.

If any argument other than `text` is `NULL`, an exception is thrown.

The returned array of chunks has the same order as the input.

The function tries to keep every chunk within the `chunkSize` limit, but if a chunk is more than the limit, it is returned as is.

Arguments

* **text** : The input text to be split. If the input text is `NULL`, it is returned as is.
* **chunkSize** : The size of each chunk. If `chunkSize < 0` or `chunkOverlap > chunkSize`, an exception is thrown.
* **chunkOverlap** : The number of overlapping characters between chunks. If `chunkOverlap < 0`, an exception is thrown.
* **separator** : The separator used for splitting.
* **isSeparatorRegex** : Whether the separator is a regex pattern.
* **trimWhitespace** : (Optional) Whether to trim whitespace from chunks. The default is `TRUE`.
* **keepSeparator** : (Optional) Whether to keep the separator in the chunks. The default is `FALSE`.
* **separatorPosition** : (Optional) The position of the separator. Valid values are `START` or `END`. The default is `START`. `START` means place the separator at the start of the following chunk, and `END` means place the separator at the end of the previous chunk.

Example

    -- returns ['This is the text I would like to ch', 'o chunk up. It is the example text ', 'ext for this exercise']
    SELECT ML_CHARACTER_TEXT_SPLITTER('This is the text I would like to chunk up. It is the example text for this exercise', 35, 4, '', TRUE, FALSE, TRUE, 'END');
