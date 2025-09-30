---
document_id: flink_how-to-guides_enable-udf-logging_chunk_2
source_file: flink_how-to-guides_enable-udf-logging.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/enable-udf-logging.html
title: Enable Logging in a User Defined Function with Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

that receives the log output

## Step 1: Enable the UDF log for an environment and region¶

UDF logging requires a Kafka topic in the environment and region where your UDF runs. This topic hosts all custom code logs for UDFs in this region and environment. You must have an existing topic to export UDF logs.

For the following example, the topic name is saved in the UDF_LOG_TOPIC_NAME environment variable.

Creating a UDF log requires the following inputs:

    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export KAFKA_CLUSTER_ID="<kafka-cluster-id>" # example: "lkc-12a3b4"
    export UDF_LOG_TOPIC_NAME="<udf-log-topic-name>" # example: "udf_log"

  1. Log in to Confluent Cloud.

         confluent login --organization-id ${ORG_ID} --prompt

The `--environment` option is an optional parameter. If not provided, the default environment is used.

  2. Run the following command to set up UDF logging for a region and environment by specifying a Kafka topic for logging. This command doesn’t create the Kafka topic. Instead, it enables logging per region and per environment to use the existing UDF_LOG_TOPIC_NAME topic as the log.

         confluent custom-code-logging create \
           --cloud ${CLOUD_PROVIDER} \
           --region ${CLOUD_REGION} \
           --topic ${UDF_LOG_TOPIC_NAME} \
           --cluster ${KAFKA_CLUSTER_ID} \
           --environment ${ENV_ID}

Your output should resemble:

         +-------------+------------+
         | Id          | ccl-4l5klo |
         | Cloud       | aws        |
         | Region      | us-west-2  |
         | Environment | env-xmzdkk |
         +-------------+------------+

Note the identifier of the UDF log, which in the current example is `ccl-4l5klo`. For convenience, save it in an environment variable:

         export UDF_LOG_ID="<udf-log-id>" # for example, ccl-4l5klo

## Step 2: Implement logging code¶

In your UDF project, import the `org.apache.logging.log4j.LogManager` and `org.apache.logging.log4j.Logger` namespaces. Get the `Logger` instance by calling the `LogManager.getLogger()` method.

    package your.package.namespace;

    import org.apache.flink.table.functions.ScalarFunction;
    import org.apache.logging.log4j.LogManager;
    import org.apache.logging.log4j.Logger;
    import java.util.Date;

    /* This class is a SumScalar function that logs messages at different levels */
    public class LogSumScalarFunction extends ScalarFunction {

       private static final Logger LOGGER = LogManager.getLogger();

       public int eval(int a, int b) {
         String value = String.format("SumScalar of %d and %d", a, b);
          Date now = new java.util.Date();

          // You can choose the logging level for log messages.
          LOGGER.info(value + " info log messages by log4j logger --- " + now);
          LOGGER.error(value + " error log messages by log4j logger --- " + now);
          LOGGER.warn(value + " warn log messages by log4j logger --- " + now);
          LOGGER.debug(value + " debug log messages by log4j logger --- " + now);
          return a + b;
       }
    }

## View logged events¶

After the instrumented UDF statements run, you can view logged events in the UDF_LOG_TOPIC_NAME topic.

Any user who has permission to access the Kafka cluster and Kafka topic that was specified in the `confluent custom-code-logging create` command can see the logged events.
