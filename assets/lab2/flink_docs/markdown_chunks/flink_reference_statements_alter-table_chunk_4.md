---
document_id: flink_reference_statements_alter-table_chunk_4
source_file: flink_reference_statements_alter-table.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/statements/alter-table.html
title: SQL ALTER TABLE Statement in Confluent Cloud for Apache Flink
chunk_index: 4
total_chunks: 7
---

If one partition does not emit a watermark, it can affect the entire pipeline.

The following statements may be helpful for debugging issues related to watermarks.

    -- example table
    CREATE TABLE t_watermark_debugging (k INT, s STRING)
      DISTRIBUTED BY (k) INTO 4 BUCKETS;

    -- Each value lands in a separate Kafka partition (out of 4).
    -- Leave out values to see missing watermarks.
    INSERT INTO t_watermark_debugging
      VALUES (1, 'Bob'), (2, 'Alice'), (8, 'John'), (15, 'David');

    -- If ROW_NUMBER doesn't show results, it's clearly a watermark issue.
    SELECT ROW_NUMBER() OVER (ORDER BY $rowtime ASC) AS `number`, *
      FROM t_watermark_debugging;

    -- Add partition information as metadata column
    ALTER TABLE t_watermark_debugging ADD part INT METADATA FROM 'partition' VIRTUAL;

    -- Use the CURRENT_WATERMARK() function to check which watermark is calculated
    SELECT
      *,
      part AS `Row Partition`,
      $rowtime AS `Row Timestamp`,
      CURRENT_WATERMARK($rowtime) AS `Operator Watermark`
    FROM t_watermark_debugging;

    -- Visualize the highest timestamp per Kafka partition
    -- Due to the table declaration (with 4 buckets), this query should show 4 rows.
    -- If not, the missing partitions might be the cause for watermark issues.
    SELECT part AS `Partition`, MAX($rowtime) AS `Max Timestamp in Partition`
      FROM t_watermark_debugging
      GROUP BY part;

    -- A workaround could be to not use the system watermark:
    ALTER TABLE t_watermark_debugging
      MODIFY WATERMARK FOR $rowtime AS $rowtime - INTERVAL '2' SECOND;
    -- Or for perfect input data:
    ALTER TABLE t_watermark_debugging
      MODIFY WATERMARK FOR $rowtime AS $rowtime - INTERVAL '0.001' SECOND;

    -- Add "fresh" data while the above statements with
    -- ROW_NUMBER() or CURRENT_WATERMARK() are running.
    INSERT INTO t_watermark_debugging VALUES
      (1, 'Fresh Bob'),
      (2, 'Fresh Alice'),
      (8, 'Fresh John'),
      (15, 'Fresh David');

The debugging examples above won’t solve everything but may help in finding the root cause.

The system watermark strategy is smart and excludes idle Kafka partitions from the watermark calculation after some time, but at least one partition must produce new data for the “logical clock” with watermarks.

Typically, root causes are:

* Idle Kafka partitions
* No data in Kafka partitions
* Not enough data in Kafka partitions
* Watermark strategy is too conservative
* No fresh data after warm up with historical data for progressing the logical clock

### Handle idle partitions for missing watermarks¶

Idle partitions often cause missing watermarks. Also, no data in a partition or infrequent data can be a root cause.

    -- Create a topic with 4 partitions.
    CREATE TABLE t_watermark_idle (k INT, s STRING)
      DISTRIBUTED BY (k) INTO 4 BUCKETS;

    -- Avoid the "not enough data" problem by using a custom watermark.
    -- The watermark strategy is still coarse-grained enough for this example.
    ALTER TABLE t_watermark_idle
      MODIFY WATERMARK FOR $rowtime AS $rowtime - INTERVAL '2' SECONDS;

    -- Each value lands in a separate Kafka partition, and partition 1 is empty.
    INSERT INTO t_watermark_idle
      VALUES
        (1, 'Bob in partition 0'),
        (2, 'Alice in partition 3'),
        (8, 'John in partition 2');

    -- Thread 1: Start a streaming job.
    SELECT ROW_NUMBER() OVER (ORDER BY $rowtime ASC) AS `number`, *
      FROM t_watermark_idle;

    -- Thread 2: Insert some data immediately -> Thread 1 still without results.
    INSERT INTO t_watermark_idle
      VALUES (1, 'Another Bob in partition 0 shortly after');

    -- Thread 2: Insert some data after 15s -> Thread 1 should show results.
    INSERT INTO t_watermark_idle
      VALUES (1, 'Another Bob in partition 0 after 15s')

Within the first 15 seconds, all partitions contribute to the watermark calculation, so the first INSERT INTO has no effect because partition 1 is still empty.

After 15 seconds, all partitions are marked as idle. No partition contributes to the watermark calculation. But when the second INSERT INTO is executed, it becomes the main driving partition for the logical clock.

The global watermark jumps to “second INSERT INTO - 2 seconds”.

In the following code, the `sql.tables.scan.idle-timeout` configuration overrides the default idle-detection algorithm, so even an immediate INSERT INTO can be the main driving partition for the logical clock, because all other partitions are marked as idle after 1 second.

    -- Thread 1: Start a streaming job.
    -- Lower the idle timeout further.
    SET 'sql.tables.scan.idle-timeout' = '1s';
    SELECT ROW_NUMBER() OVER (ORDER BY $rowtime ASC) AS `number`, *
      FROM t_watermark_idle;

    -- Thread 2: Insert some data immediately -> Thread 1 should show results.
    INSERT INTO t_watermark_idle
      VALUES (1, 'Another Bob in partition 0 shortly after');
