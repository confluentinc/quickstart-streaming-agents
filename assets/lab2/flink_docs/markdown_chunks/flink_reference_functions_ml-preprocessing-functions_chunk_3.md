---
document_id: flink_reference_functions_ml-preprocessing-functions_chunk_3
source_file: flink_reference_functions_ml-preprocessing-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/ml-preprocessing-functions.html
title: Machine-Learning Preprocessing Functions in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 4
---

returns 0.2 SELECT ML_MAX_ABS_SCALER(1, 5);

## ML_MIN_MAX_SCALER¶

Scales numerical values to a specified range using min-max normalization.

Syntax

    ML_MIN_MAX_SCALER(value, min, max)

Description
    The `ML_MIN_MAX_SCALER` function scales numerical values to a specified range using min-max normalization. The function transforms values to the range `[0, 1]` by default, or to a custom range if `min` and `max` are specified.
Arguments

* **value** : Numerical expression to be scaled. If the input value is `NULL`, `NaN`, or `Infinity`, it is returned as is.
  * If `value > max`, it is set to `1.0`.
  * If `value < min`, it is set to `0.0`.
  * If `max == min`, the range is set to `1.0` to avoid division by zero.
* **min** : Minimum value of the feature data seen in the dataset. If `min` is `NULL`, `NaN`, or `Infinity`, an exception is thrown.
* **max** : Maximum value of the feature data seen in the dataset.
  * If `max` is `NULL`, `NaN`, or `Infinity`, an exception is thrown.
  * If `max < min`, an exception is thrown.

Example

    -- returns 0.25
    SELECT ML_MIN_MAX_SCALER(2, 1, 5);

## ML_NGRAMS¶

Generates n-grams from an array of strings.

Syntax

    ML_NGRAMS(input [, nValue] [, separator])

Description

The `ML_NGRAMS` function generates n-grams from an array of strings. N-grams are contiguous sequences of n items from a given sample of text.

The ordering of the returned output is the same as the `input` array.

Arguments

* **input** : Array of CHAR or VARCHAR to return n-gram for.
  * If the `input` array has `NULL`, it is ignored while forming N-GRAMS.
  * If the `input` array is `NULL` or empty, an empty N-GRAMS array is returned.
  * Empty strings in the `input` array are treated as is.
  * Strings with only whitespace are treated as empty strings.
* **nValue** : (Optional) N value of n-gram function. The default is `2`.
  * If `nValue < 1`, an exception is thrown.
  * If `nValue > input.size()`, an empty N-GRAMS array is returned.
* **separator** : (Optional) Characters to join n-gram values with. The default is whitespace.

Example

    -- returns ['ab', 'cd', 'de', 'pwe']
    SELECT ML_NGRAMS(ARRAY['ab', 'cd', 'de', 'pwe'], 1, '#');

    -- returns ['ab#cd', 'cd#de']
    SELECT ML_NGRAMS(ARRAY['ab','cd','de', NULL], 2, '#');

## ML_NORMALIZER¶

Normalizes numerical values using p-norm normalization.

Syntax

    ML_NORMALIZER(value, normValue)

Description
    The `ML_NORMALIZER` function normalizes numerical values using p-norm normalization. This scales each sample to have unit norm.
Arguments

* **value** : Numerical expression to be scaled. If the input value is `NULL`, `NaN`, or `Infinity`, it is returned as is.
* **normValue** : Calculated norm value of the feature data using p-norm.
  * If `normValue` is `NULL` or `NaN`, an exception is thrown.
  * If `normValue` is `Infinity`, `0` is returned.
  * If `normValue` is `0`, which is only possible when all the values are `0`, the input value is returned as is.

Example

    -- returns 0.6
    SELECT ML_NORMALIZER(3.0, 5.0);

## ML_ONE_HOT_ENCODER¶

Encodes categorical variables into a binary vector representation.

Syntax

    ML_ONE_HOT_ENCODER(input, categories [, dropLast] [, handleUnknown])

Description
    The `ML_ONE_HOT_ENCODER` function encodes categorical variables into a binary vector representation. Each category is represented by a binary vector where only one element is 1 and the rest are 0.
Arguments

* **input** : Input value to encode. If the input value is `NULL`, it is considered to be in the unknown category.
* **categories** : Array of category values to encode input value to. The `input` argument must be of same type as the `categories` array.
  * If the `categories` array is empty, an exception is thrown.
  * The `categories` array can’t be `NULL`, or an exception is thrown.
  * The `categories` array can’t have `NULL` or duplicate values, or an exception is thrown.
* **dropLast** : (Optional) Whether to drop the last category. The default is `TRUE`. By default, the last category is dropped, to prevent perfectly collinear features.
* **handleUnknown** : (Optional) `ERROR`, `IGNORE`, `KEEP` options to indicate how to handle unknown values. The default is `IGNORE`.
  * If `handleUnknown` is `ERROR`, an exception is thrown when the input is an unknown value.
  * If `handleUnknown` is `IGNORE`, unknown values are ignored and values of all the columns are 0.
  * If `handleUnknown` is `KEEP`, the unknown category column has value 1.
  * If `handleUnknown` is `KEEP`, the last column is for the unknown category.

Example

    -- returns [1, 0, 0, 0]
    SELECT ML_ONE_HOT_ENCODER('abc', ARRAY['abc', 'def', 'efg', 'hikj']);

    -- returns [0, 0, 0, 0, 1]
    SELECT ML_ONE_HOT_ENCODER('abcd', ARRAY['abc', 'def', 'efg', 'hik'], TRUE, 'KEEP' );
