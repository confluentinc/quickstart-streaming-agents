---
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/ml-preprocessing-functions.html
title: Machine-Learning Preprocessing Functions in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'functions', 'ml-preprocessing-functions.html']
scraped_date: 2025-09-05T13:50:29.990477
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
    * `C`
    * `CPP`
    * `CSHARP`
    * `ELIXIR`
    * `GO`
    * `HTML`
    * `JAVA`
    * `JAVASCRIPT`
    * `JSON`
    * `KOTLIN`
    * `LATEX`
    * `MARKDOWN`
    * `PHP`
    * `PYTHON`
    * `RUBY`
    * `RUST`
    * `SCALA`
    * `SQL`
    * `SWIFT`
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
