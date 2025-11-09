---
document_id: flink_reference_functions_collection-functions_chunk_2
source_file: flink_reference_functions_collection-functions.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/functions/collection-functions.html
title: SQL Collection Functions in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

'Rust',], ARRAY['Python', 'Rust', 'Haskell', 'C#']);

## ARRAY_JOIN¶

Syntax

    ARRAY_JOIN(array, delimiter [, nullReplacement])

Description

Returns a string that represents the concatenation of the elements in `array`. Elements are cast to their string representation.

The `delimiter` is a string that separates each pair of consecutive elements of the array.

The optional `nullReplacement` is a string that replaces null elements in the array. If `nullReplacement` is not specified, null elements in the array are omitted from the resulting string.

Returns NULL if any of the inputs is NULL.

Example

    -- returns "Java, SQL, Python, not specified"
    SELECT ARRAY_JOIN(ARRAY['Java', 'SQL', 'Python', NULL], ', ', 'not specified');

## ARRAY_MAX¶

Syntax

    ARRAY_MAX(array)

Description
    Returns the maximum value from `array`, or NULL if `array` is NULL.
Example

    -- returns 4
    SELECT ARRAY_MAX(ARRAY[1, 2, 3, 4]);

## ARRAY_MIN¶

Syntax

    ARRAY_MIN(array)

Description
    Returns the minimum value from `array`, or NULL if `array` is NULL.
Example

    -- returns 1
    SELECT ARRAY_MIN(ARRAY[1, 2, 3, 4]);

## ARRAY_POSITION¶

Syntax

    ARRAY_POSITION(array, element)

Description

Returns the position of the first occurrence of `element` in `array` as an integer. The index is 1-based, so the first element in the array has index 1.

Returns 0 if `element` is not found in `array`.

Returns NULL if either of the arguments is NULL.

Example

    -- returns 2
    SELECT ARRAY_POSITION(ARRAY['Java', 'SQL', 'Python'], 'SQL');

## ARRAY_PREPEND¶

Syntax

    ARRAY_PREPEND(array, element)

Description

Prepends an element to the beginning of the array and returns the result.

If `array` is NULL, the function returns NULL.

If `element` is NULL, the NULL element is prepended to the beginning of the array.

Example

    -- returns [SQL,Java,Python]
    SELECT ARRAY_PREPEND(ARRAY['Java', 'Python'], 'SQL');

## ARRAY_REMOVE¶

Syntax

    ARRAY_REMOVE(array, element)

Description

Removes from `array` all elements that are equal to `element`. Order of elements is retained.

If `array` is NULL, the function returns NULL.

Example

    -- returns [Java,Python]
    SELECT ARRAY_REMOVE(ARRAY['Java', 'SQL', 'Python'], 'SQL');

## ARRAY_REVERSE¶

Syntax

    ARRAY_REVERSE(array)

Description

Returns an array that has elements in the reverse order of the elements in `array`.

If `array` is NULL, the function returns NULL.

Example

    -- returns [Python,SQL,Java]
    SELECT ARRAY_REVERSE(ARRAY['Java', 'SQL', 'Python']);

## ARRAY_SLICE¶

Syntax

    ARRAY_SLICE(array, start_offset [, end_offset])

Description

Returns a subarray of the input array between `start_offset` and `end_offset`, inclusive. The offsets are 1-based, but 0 is also treated as the beginning of the array.

Elements of the subarray are returned in the order they appear in `array`.

Positive values are counted from the beginning of the array. Negative values are counted from the end.

If `end_offset` is omitted, this offset is treated as the length of the array.

If `start_offset` is after `end_offset`, or both are out of array bounds, an empty array is returned.

Returns NULL if any input value is NULL.

Example

    -- returns [SQL,Python,C#,JavaScript]
    SELECT ARRAY_SLICE(ARRAY['Java', 'SQL', 'Python', 'C#', 'JavaScript', 'Go'], 2, 5);

## ARRAY_SORT¶

Syntax

    ARRAY_SORT(array [, ascending_order [, null_first]])

Description

Returns an array that has the elements of `array` in sorted order.

When only `array` is specified, the function defaults to ascending order with NULLs at the start.

Specifying `ascending_order` as `TRUE` orders the array in ascending order, with NULLs first. Setting `ascending_order` to `FALSE` orders the array in descending order, with NULLs last.

Independently, specifying `null_first` as TRUE moves NULLs to the beginning. specifying `null_first` as FALSE moves NULLs to the end, irrespective of the sorting order.

The function returns NULL if any input is NULL.

Example

    -- returns [1,2,3,4,5]
    SELECT ARRAY_SORT(ARRAY[5,4,3,2,1]);

    -- returns [NULL,SQL,Python,Java,Go,C#]
    SELECT ARRAY_SORT(ARRAY['Java', 'SQL', 'Python', NULL, 'Go', 'C#'], FALSE, TRUE);

## ARRAY_UNION¶

Syntax

    ARRAY_UNION(array1, array2)

Description

Returns an array that has the elements from the union of `array1` and `array2`. Duplicate elements are removed.

If `array1` or `array2` is NULL, the function returns NULL.

Example

    -- returns [Java,SQL,Python,C#,Go]
    SELECT ARRAY_UNION(ARRAY['Java', 'SQL', 'Python'], ARRAY['C#', 'SQL', 'Go']);

## CARDINALITY(array)¶

Syntax

    CARDINALITY(array)

Description
    Returns the number of elements in the specified array.
Example

    -- returns 5
    SELECT CARDINALITY(ARRAY['Java', 'SQL', 'Python', 'Rust', 'C++']);
