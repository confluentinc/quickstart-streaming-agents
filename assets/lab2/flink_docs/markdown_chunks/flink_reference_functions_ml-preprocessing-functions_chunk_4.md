---
document_id: flink_reference_functions_ml-preprocessing-functions_chunk_4
source_file: flink_reference_functions_ml-preprocessing-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/ml-preprocessing-functions.html
title: Machine-Learning Preprocessing Functions in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 4
---

'efg', 'hik'], TRUE, 'KEEP' );

## ML_RECURSIVE_TEXT_SPLITTER¶

Splits text into chunks using multiple separators recursively.

Syntax

    ML_RECURSIVE_TEXT_SPLITTER(text, chunkSize, chunkOverlap [, separators]
    [, isSeparatorRegex] [, trimWhitespace] [, keepSeparator]
    [, separatorPosition])

Description

The `ML_RECURSIVE_TEXT_SPLITTER` function splits text into chunks using multiple separators recursively. It starts with the first separator and recursively applies subsequent separators if chunks are still too large.

If any argument other than `text` is `NULL`, an exception is thrown.

The returned array of chunks has the same order as the input.

Arguments

  * **text** : The input text to be split. If the input text is `NULL`, it is returned as is.
  * **chunkSize** : The size of each chunk. If `chunkSize < 0` or `chunkOverlap > chunkSize`, an exception is thrown.
  * **chunkOverlap** : The number of overlapping characters between chunks. If `chunkOverlap < 0`, an exception is thrown.
  * **separators** : (Optional) The list of separators used for splitting. The default is `["\n\n", "\n", " ", ""]`
  * **isSeparatorRegex** : (Optional) Whether the separator is a regex pattern. The default is `FALSE`
  * **trimWhitespace** : (Optional) Whether to trim whitespace from chunks. The default is `TRUE`
  * **keepSeparator** : (Optional) Whether to keep the separator in the chunks. The default is `FALSE`
  * **separatorPosition** : (Optional) The position of the separator. Valid values are `START` or `END`. The default is `START`. `START` means place the separator at the start of the following chunk, and `END` means place the separator at the end of the previous chunk.

Example

    -- returns ['Hello', '. world', '!']
    SELECT ML_RECURSIVE_TEXT_SPLITTER('Hello. world!', 0, 0, ARRAY['[!]','[.]'], TRUE, TRUE, TRUE, 'START');

## ML_ROBUST_SCALER¶

Scales numerical values using statistics that are robust to outliers.

Syntax

    ML_ROBUST_SCALER(value, median, firstQuartile, thirdQuartile [,
    withCentering, withScaling)

Description
    The `ML_ROBUST_SCALER` function scales numerical values using statistics that are robust to outliers. It removes the median and scales the data according to the quantile range.
Arguments

  * **value** : Numerical expression to be scaled. If the input value is `NULL`, `NaN`, or `Infinity`, it is returned as is.
  * **median** : Median of the feature data seen in the training dataset. If `median` is `NULL`, `NaN`, or `Infinity`, an exception is thrown.
  * **firstQuartile** : First Quartile of feature data seen in the dataset. If `firstQuartile` is `NULL`, `NaN`, or `Infinity`, an exception is thrown.
  * **thirdQuartile** : Third Quartile of feature data seen in the dataset.
    * If `thirdQuartile` is `NULL`, `NaN`, or `Infinity`, an exception is thrown.
    * If `thirdQuartile - firstQuartile = 0`, the range is set to `1.0` to avoid division by zero.
  * **withCentering** : (Optional) Boolean value indicating to center the numerical value using median before scaling. The default is `TRUE`. If `withCentering` is `FALSE`, the median value is ignored.
  * **withScaling** : (Optional) Boolean value indicating to scale the numerical value using IQR after centering. The default is `TRUE`. If `withScaling` is `FALSE`, the firstQuartile and thirdQuartile values are ignored.

Example

    -- returns 0.3333333333333333
    SELECT ML_ROBUST_SCALER(2, 1, 0, 3, TRUE, TRUE);

## ML_STANDARD_SCALER¶

Standardizes numerical values by removing the mean and scaling to unit variance.

Syntax

    ML_STANDARD_SCALER(value, mean, standardDeviation [, withCentering]
    [, withScaling])

Description
    The `ML_STANDARD_SCALER` function standardizes numerical values by removing the mean and scaling to unit variance. This is useful for features that follow a normal distribution.
Arguments

  * **value** : Numerical expression to be scaled. If the input value is `NULL, NaN` or `Infinity`, it is returned as is.
  * **mean** : Mean of the feature data seen in the dataset. If `mean` is `NULL, NaN` or `Infinity`, an exception is thrown.
  * **standardDeviation** : Standard Deviation of the feature data seen in the dataset. If `standardDeviation` is `NULL` or `NaN`, an exception is thrown.
    * If `standardDeviation` is `Infinity`, `0` is returned.
    * If `standardDeviation` is `0`, the value does not need to be scaled, so it is returned as is.
  * **withCentering** : (Optional) Boolean value indicating to center the numerical value using mean before scaling. The default is `TRUE`. If `withCentering` is `FALSE`, the mean value is ignored.
  * **withScaling** : (Optional) Boolean value indicating to scale the numerical value using std after centering. The default is `TRUE`. If `withScaling` is `FALSE`, the `standardDeviation` value is ignored.

Example

    -- returns 0.2
    SELECT ML_STANDARD_SCALER(2, 1, 5, TRUE, TRUE);

ML_STANDARD_SCALER(2, 1, 5, TRUE, TRUE);

## Other built-in functions¶

  * [Aggregate Functions](aggregate-functions.html#flink-sql-aggregate-functions)
  * [Collection Functions](collection-functions.html#flink-sql-collection-functions)
  * [Comparison Functions](comparison-functions.html#flink-sql-comparison-functions)
  * [Conditional Functions](conditional-functions.html#flink-sql-conditional-functions)
  * [Datetime Functions](datetime-functions.html#flink-sql-datetime-functions)
  * [Hash Functions](hash-functions.html#flink-sql-hash-functions)
  * [JSON Functions](json-functions.html#flink-sql-json-functions)
  * ML Preprocessing Functions
  * [Model Inference Functions](model-inference-functions.html#flink-sql-model-inference-functions)
  * [Numeric Functions](numeric-functions.html#flink-sql-numeric-functions)
  * [String Functions](string-functions.html#flink-sql-string-functions)
  * [Table API Functions](table-api-functions.html#flink-table-api-functions)
