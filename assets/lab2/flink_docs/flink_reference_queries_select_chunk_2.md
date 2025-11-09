---
document_id: flink_reference_queries_select_chunk_2
source_file: flink_reference_queries_select.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/queries/select.html
title: SQL SELECT statement in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

SELECT DISTINCT id FROM orders;

## Usage¶

In the Flink SQL shell or in a Cloud Console workspace, run the following commands to see examples of the SELECT statement.

  1. Create a table for web page click events.

         -- Create a table for web page click events.
         CREATE TABLE clicks (
           ip_address VARCHAR,
           url VARCHAR,
           click_ts_raw BIGINT
         );

  2. Populate the table with mock clickstream data.

         -- Populate the table with mock clickstream data.
         INSERT INTO clicks
         VALUES( '10.0.0.1',  'https://acme.com/index.html',     1692812175),
               ( '10.0.0.12', 'https://apache.org/index.html',   1692826575),
               ( '10.0.0.13', 'https://confluent.io/index.html', 1692826575),
               ( '10.0.0.1',  'https://acme.com/index.html',     1692812175),
               ( '10.0.0.12', 'https://apache.org/index.html',   1692819375),
               ( '10.0.0.13', 'https://confluent.io/index.html', 1692826575);

Press ENTER to return to the SQL shell. Because INSERT INTO VALUES is a point-in-time statement, it exits after it completes inserting records.

  3. View all rows in the `clicks` table by using a SELECT statement.

         SELECT * FROM clicks;

Your output should resemble:

         ip_address url                             click_ts_raw
         10.0.0.1   https://acme.com/index.html     1692812175
         10.0.0.12  https://apache.org/index.html   1692826575
         10.0.0.13  https://confluent.io/index.html 1692826575
         10.0.0.1   https://acme.com/index.html     1692812175
         10.0.0.12  https://apache.org/index.html   1692819375
         10.0.0.13  https://confluent.io/index.html 1692826575

  4. View only unique rows in the `clicks` table by using a SELECT DISTINCT statement.

         SELECT DISTINCT * FROM clicks;

Your output should resemble:

         ip_address url                             click_ts_raw
         10.0.0.1   https://acme.com/index.html     1692812175
         10.0.0.12  https://apache.org/index.html   1692826575
         10.0.0.13  https://confluent.io/index.html 1692826575
         10.0.0.12  https://apache.org/index.html   1692819375

  5. View only records that have the ip_address of `10.0.0.1` by using a SELECT WHERE statement.

         SELECT * FROM clicks WHERE ip_address='10.0.0.1';

Your output should resemble:

         ip_address url                         click_ts_raw
         10.0.0.1   https://acme.com/index.html 1692812175
         10.0.0.1   https://acme.com/index.html 1692812175
