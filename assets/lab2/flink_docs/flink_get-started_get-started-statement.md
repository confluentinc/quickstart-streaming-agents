---
source_url: https://docs.confluent.io/platform/current/flink/get-started/get-started-statement.html
title: Submit Flink SQL Statement with Confluent Manager for Apache Flink
hierarchy: ['platform', 'get-started', 'get-started-statement.html']
scraped_date: 2025-09-05T13:52:20.056838
---

# Submit Flink SQL Statement with Confluent Manager for Apache Flink¶

This guide provides a quick introduction submitting a Flink SQL statement with Confluent Manager for Apache Flink® (CMF). It provides the prerequisites, how to set up an environment and compute pool, and how to run SQL statements.

This guide provides steps using the Confluent CLI, but you can also use the [REST APIs for Confluent Manager for Apache Flink](../clients-api/rest.html#af-rest-api) to perform the same tasks.

## Prerequisites¶

* CMF installed. Follow step 1 of [Get Started with Applications in Confluent Manager for Apache Flink](get-started-application.html#cpf-get-started) to install the Flink Kubernetes operator.
* The latest version of the Confluent CLI installed. For more information, see [Install the Confluent CLI](/confluent-cli/current/install.html).
* Example tables configured. Run the following command to configure example tables that are immediately usable.

    helm upgrade --install cmf --version "~2.0.0" \
    confluentinc/confluent-manager-for-apache-flink \
    --namespace default \
    --set cmf.sql.examples-catalog.enabled=true \
    --set cmf.sql.production=false

Configure the SQL shell to connect to your CMF instance.

    export CONFLUENT_CMF_URL=http://<host>:<port>

## Set up an Environment and a Compute Pool¶

This topic uses the Confluent CLI, but all functionality is also supported through the [REST APIs](../clients-api/rest.html#af-rest-api).

  1. Create Flink environment pointing to the default namespace.

         confluent flink environment create test --kubernetes-namespace default

  2. Create a compute pool to run the SQL statement with.

         {
           "apiVersion": "cmf.confluent.io/v1",
           "kind": "ComputePool",
           "metadata": {
             "name": "pool"
           },
           "spec": {
             "type": "DEDICATED",
             "clusterSpec": {
               "flinkVersion": "v1_19",
               "image": "confluentinc/cp-flink-sql:1.19-cp1",
               "flinkConfiguration": {
                 "pipeline.operator-chaining.enabled": "false",
                 "execution.checkpointing.interval": "10s"
               },
               "taskManager": {
                 "resource": {
                   "cpu": 1.0,
                   "memory": "1024m"
                 }
               },
               "jobManager": {
                 "resource": {
                   "cpu": 0.5,
                   "memory": "1024m"
                 }
               }
             }
           }
         }

         confluent --environment test flink compute-pool create /path/to/compute-pool.json

## Run Statements¶

The next steps use the SQL shell feature of the Confluent CLI to run some example statements.

Run the following command to start the SQL shell.

    confluent --environment test --compute-pool pool flink shell

You should see the following output and a prompt waiting for your statements.

    Welcome!
    To exit, press Ctrl-Q or type "exit".

    [Ctrl-Q] Quit [Ctrl-S] Toggle Completions
    >

Next, you can execute some SQL statements. The following command lists the tables of the examples marketplace database.

    > SHOW TABLES IN examples.marketplace;
    Statement name: cli-2025-07-02-120056-c98ff916-15df-4160-ba89
    Submitting statement...
    Statement successfully submitted.
    Details: Statement execution completed.
    Finished statement execution. Statement phase: COMPLETED.
    Details: Statement execution completed.
    +------------+
    | table name |
    +------------+
    | blackhole  |
    | clicks     |
    | orders     |
    +------------+

The response shows a list of three tables: `blackhole`, `clicks`, and `orders`. The `clicks` and the `orders` tables provide randomly generated data. The `blackhole` table consumes data and does not persist it.

The following command shows the details of the `clicks` table.

    > DESCRIBE examples.marketplace.clicks;
    Statement name: cli-2025-07-02-120412-70574d7b-9fc1-49e6-8e97
    Submitting statement...
    Statement successfully submitted.
    Details: Statement execution completed.
    Finished statement execution. Statement phase: COMPLETED.
    Details: Statement execution completed.
    +------------+--------+-------+------+--------+-----------+
    |    name    |  type  | null  | key  | extras | watermark |
    +------------+--------+-------+------+--------+-----------+
    | click_id   | STRING | false | null | null   | null      |
    | user_id    | INT    | false | null | null   | null      |
    | url        | STRING | false | null | null   | null      |
    | user_agent | STRING | false | null | null   | null      |
    | view_time  | INT    | false | null | null   | null      |
    +------------+--------+-------+------+--------+-----------+

The previous queries are metadata queries and did not execute on a Flink cluster. The following query processes some real data.

    > SELECT * FROM examples.marketplace.clicks WHERE view_time > 100;
    Statement name: cli-2025-07-02-121205-99174ab6-619f-46a2-9a60
    Submitting statement...
    Statement successfully submitted.
    Waiting for statement to be ready. Statement phase: PENDING.
    Details: Statement execution pending.
    Waiting for statement to be ready. Statement phase is PENDING. (Timeout 6s/600s)
    Waiting for statement to be ready. Statement phase is PENDING. (Timeout 13s/600s)

This statement is executed on an Flink cluster. It takes some time until the cluster is deployed on Kubernetes and the statement job is started. Depending on your setup, this might take a while. Once the job is running, the SQL shell starts printing its results.

    ╔══════════════════════════════════════ Table mode (cli-2025-07-02-121205-99174ab6-619f-46a2-9a60) ═══════════════════════════════════════╗
    ║click_id                             user_id url                                                              user_agent       view_time ║
    ║37ff930579bf010eeb67441baff9e7267496 4169    726cb48b60576e9032263a936557d6549ff2dd99b695c88811a2b35e4043a5ad df4bca5dc6b68fa9 101       ║
    ║2ddd4aa4369e6d6b926df041f8292b7be2ec 4687    a83b52665f8b076edc01e1ff65ae85a96ae9cf0b199418f184b128ba8dd489d6 def647e82e093d17 103       ║
    ║54c46cc1327c47a3f54795357bbf49b97cfc 4735    a7726bb2b8b894f45b9034b64fb3bc81593d2fbadf4d9bc5a379814e8bc54fa1 7385df86e130b205 108       ║
    ║105e58ea2eab2751356df0c5ad6f033fbcb7 3814    81085625216dc8493736a0e7c6ff7a78774fe0d74beb3c2003878e12a4da2ffd 90e7f895e7810e60 119       ║
    ║4f58683d2fa404c0186e42b3cfe15ad519c3 3240    a069f6050a1de39b879bfe08a8c50903cb707f8c3025ff6c9d0566a07bc5065f d914681c38e8b111 112       ║
    ║1aa038f7d3de609ec66066aaa8c7103a7766 3684    7c4d62b393330c1d25daf8252b5e02dec5a181f44a31855f594ab296f17ddc7e e78baae6a6b8c636 104       ║
    ║                                                                                                                                         ║
    ╚═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
    Refresh: Paused                                             Row: 6766 of 6785                                    Last refresh: 12:14:59.837
    [Q] Quit  [M] Show changelog  [P] Play  [U/D] Jump up/down

As mentioned before, the data of the `clicks` table is randomly generated. You can leave the result view by pressing the `Q` key.

Finally, the following example deploys a statement that writes data from the `clicks` table into the `blackhole` table.

    > INSERT INTO examples.marketplace.blackhole SELECT click_id AS data FROM examples.marketplace.clicks;
    Statement name: cli-2025-07-02-123224-beb9370d-3041-4ade-9dda
    Submitting statement...
    Statement successfully submitted.
    Waiting for statement to be ready. Statement phase: PENDING.
    Details: Statement execution pending.
    Waiting for statement to be ready. Statement phase is PENDING. (Timeout 6s/600s)
    Waiting for statement to be ready. Statement phase is PENDING. (Timeout 13s/600s)

Again, it takes a few moments until the Flink cluster is deployed and the query is running. Now you can inspect the running statement job using the webUI of the Flink cluster. Close the SQL shell by pressing `CTRL-Q` and run the following command to forward the webUI of the Flink cluster.

    confluent --environment test flink statement web-ui-forward <stmt-name> --port 9090

`<stmt-name>` needs to be replaced by the name of the statement, which is `cli-2025-07-02-121205-99174ab6-619f-46a2-9a60` in the previous example.

The Confluent CLI forwards the Flink webUI through CMF to your local machine. Open <http://localhost:9090> in your browser to see the `INSERT INTO` statement running in the Flink webUI.

Once you are done, you should stop the `INSERT INTO` statement and tear down the Flink cluster. For this, cancel the forwarding of the webUI by pressing `CTRL-C`, run the following command, and confirm the deletion of the statement.

    confluent --environment test flink statement delete <stmt-name>
