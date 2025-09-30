---
document_id: flink_how-to-guides_profile-query_chunk_1
source_file: flink_how-to-guides_profile-query.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/profile-query.html
title: Profile a Query with Confluent Cloud for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Profile a Query with Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® enables you to profile the performance of your queries.

The Query Profiler provides enhanced visibility into how a Flink statement is processing data, which enables rapid identification of bottlenecks, data skew issues, and other performance issues.

The profiler updates metrics in near real-time, enabling you to monitor query performance as data flows through your pipeline.

For more information about the Query Profiler, see [Flink SQL Query Profiler](../operate-and-deploy/query-profiler.html#flink-sql-query-profiler).

[](../../_images/flink-query-profiler.gif)

## Prerequisites¶

* Access to Confluent Cloud.
* The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, contact your OrganizationAdmin or EnvironmentAdmin. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](../operate-and-deploy/flink-rbac.html#flink-rbac).
* A provisioned Flink compute pool.

## Step 1: Analyze and run a statement¶

In this step, you use the [EXPLAIN](../reference/statements/explain.html#flink-sql-explain) statement to perform a static analysis on a query and then start the query. The query is a [temporal join](../reference/queries/joins.html#flink-sql-temporal-joins) between the `orders` and `customers` tables.

  1. Log in to Confluent Cloud and navigate to your Flink workspace.

  2. Run the following EXPLAIN statement to view a static analysis of a query.

         EXPLAIN
         SELECT
           o.order_id,
           o.`$rowtime`,
           c.customer_id,
           c.name,
           o.price
         FROM examples.marketplace.orders o
         JOIN examples.marketplace.customers FOR SYSTEM_TIME AS OF o.`$rowtime` c
         ON o.customer_id = c.customer_id
         WHERE o.`$rowtime` >= CURRENT_TIMESTAMP - INTERVAL '1' HOUR;

Your output should resemble:

         == Physical Plan ==

         StreamSink [12]
           +- StreamCalc [11]
             +- StreamTemporalJoin [10]
               +- StreamExchange [3]
               :  +- StreamCalc [2]
               :    +- StreamTableSourceScan [1]
               +- StreamExchange [9]
                 +- StreamCalc [8]
                   +- StreamChangelogNormalize [7]
                     +- StreamExchange [6]
                       +- StreamCalc [5]
                         +- StreamTableSourceScan [4]
         ...

  3. Run the statement.

         SELECT
           o.order_id,
           o.`$rowtime`,
           c.customer_id,
           c.name,
           o.price
         FROM examples.marketplace.orders o
         JOIN examples.marketplace.customers FOR SYSTEM_TIME AS OF o.`$rowtime` c
         ON o.customer_id = c.customer_id
         WHERE o.`$rowtime` >= CURRENT_TIMESTAMP - INTERVAL '1' HOUR;

## Step 2: Profile the query¶

In this step, you use the Query Profiler to monitor the performance of the query. The Query Profiler helps identify performance bottlenecks by showing where records are flowing slowly or backing up in the pipeline.

  1. Navigate to your environment’s overview page.

  2. In the navigation menu, click **Flink** , and in the overview page, click **Flink statements**.

  3. In the statement list, click your statement to open the statement details page.

  4. Click **Query profiler** to view the profiler graph.

The Query Profiler opens and shows a graph of the Flink tasks that are running. The graph shows the physical execution plan of your query, with each operator represented as a node. The nodes are connected by arrows showing the flow of data between operators. For each operator node, you can see:

     * The operator name and ID
     * Metrics like Idleness and Backpressure
     * Resource utilization like CPU and memory usage

Key operators in the current temporal join query include:

     * StreamTableSourceScan nodes [1] and [4] reading from the orders and customers tables
     * StreamCalc nodes [2], [5], [8], [11] performing filtering and projection
     * StreamExchange nodes [3], [6], [9] handling data redistribution between tasks
     * StreamChangelogNormalize [7] processing changelog records from the versioned customers table
     * StreamTemporalJoin [10] joining the orders with customer versions based on event time
     * StreamSink [12] writing results to the output
  5. Click the title bar of the **TemporalJoin** node to open the operator details pane.

  6. Click **Operator** to view details about the operators in the task.

  7. Expand **State Size** to view the amount of data currently stored by the task.

  8. In the graph, click on other operator nodes to see metrics about their performance.
