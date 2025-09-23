---
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/enable-udf-logging.html
title: Enable Logging in a User Defined Function with Confluent Cloud for Apache Flink
hierarchy: ['how-to-guides', 'enable-udf-logging.html']
scraped_date: 2025-09-05T13:47:37.358658
---

# Enable Logging in a User Defined Function for Confluent Cloud for Apache Flink¶

Note

User-Defined Function (UDF) logging support is an Early Access Program feature in Confluent Cloud. This feature should be used only for evaluation and non-production testing purposes or to provide feedback to Confluent, particularly as it becomes more widely available in follow-on preview editions. To participate in this Early Access Program, contact your Confluent account manager.

Early Access Program features are intended for evaluation use in development and testing environments only, and not for production use. Early Access Program features are provided: (a) without support; (b) “AS IS”; and (c) without indemnification, warranty, or condition of any kind. No service level commitment will apply to Early Access Program features. Early Access Program features are considered to be a Proof of Concept as defined in the Confluent Cloud Terms of Service. Confluent may discontinue providing preview releases of the Early Access Program features at any time in Confluent’s sole discretion.

When you create a user defined function (UDF) with Confluent Cloud for Apache Flink®, you have the option of enabling logging to an Apache Kafka® topic to help with monitoring and debugging.

In this topic, you perform the following steps.

  * Step 1: Enable the UDF log for an environment and region
  * Step 2: Implement logging code
  * View logged events
  * Manage your UDF logs

For more information on creating UDFs, see [Create a User Defined Function](create-udf.html#flink-sql-create-udf).

## Limitations¶

For limitations related to logs, see [UDF logging limitations](../concepts/user-defined-functions.html#flink-sql-udfs-logging-limitations).

## Prerequisites¶

You need the following prerequisites to use Confluent Cloud for Apache Flink.

  * Access to Confluent Cloud.

  * The organization ID, environment ID, and compute pool ID for your organization.

  * The OrganizationAdmin, EnvironmentAdmin, or FlinkAdmin role for creating compute pools, or the FlinkDeveloper role if you already have a compute pool. If you don’t have the appropriate role, reach out to your OrganizationAdmin or EnvironmentAdmin.

  * The Confluent CLI. To use the Flink SQL shell, update to the latest version of the Confluent CLI by running the following command:

        confluent update --yes

If you used homebrew to install the Confluent CLI, update the CLI by using the `brew upgrade` command, instead of `confluent update`.

For more information, see [Confluent CLI](https://docs.confluent.io/confluent-cli/current/overview.html).

  * A provisioned Flink compute pool in Confluent Cloud.

  * Apache Maven software project management tool (see [Installing Apache Maven](https://maven.apache.org/install.html))

  * Java 11 to Java 17

  * Sufficient permissions to upload and invoke UDFs in Confluent Cloud. For more information, see [Flink RBAC](../operate-and-deploy/flink-rbac.html#flink-rbac).

  * Sufficient permissions to enable UDF logging. For more information, see [RBAC for UDF Logging](../operate-and-deploy/flink-rbac.html#flink-rbac-udf-logging).

  * Flink versions 1.18.x and 1.19.x of `flink-table-api-java` are supported.

  * Confluent CLI version 4.13.0 or later

  * A Kafka topic that receives the log output

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

## Manage your UDF logs¶

You can manage your logging configurations by using the Confluent CLI or by using the Confluent Cloud REST API.

In addition to the previously listed inputs, the REST API requires a Cloud API key. Follow the instructions [here](../../security/authenticate/workload-identities/service-accounts/api-keys/manage-api-keys.html#cloud-cloud-api-keys) to create a new API key for Confluent Cloud.

    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"

### Enable a logging configuration¶

Run the following commands to enable the logging configuration for a region and environment.

Confluent CLIREST API

To enable UDF logging, run the following commands.

  1. Log in to Confluent Cloud.

         confluent login --organization-id ${ORG_ID} --prompt

  2. Run the following command to enable UDF logging.

         confluent custom-code-logging create \
           --cloud ${CLOUD_PROVIDER} \
           --region ${CLOUD_REGION} \
           --topic ${UDF_LOG_TOPIC_NAME} \
           --cluster ${KAFKA_CLUSTER_ID} \
           --environment ${ENV_ID}

  1. Run the following command to enable UDF logging.

         cat << EOF | curl --silent -X POST
           -u ${CLOUD_API_KEY}:${CLOUD_API_SECRET} \
           -d @- https://api.confluent.cloud/ccl/v1/custom-code-loggings
             {
                 "cloud":"${CLOUD_PROVIDER}",
                 "region":"${CLOUD_REGION}",
                 "environment": {
                 "id":"${ENV_ID}"
             },
                 "destination_settings":{
                         "kind":"Kafka",
                         "cluster_id":"${KAFKA_CLUSTER_ID}",
                         "topic":"${UDF_LOG_TOPIC_NAME}",
                 "log_level":"info"
                 }
             }
             EOF

### Delete a logging configuration¶

Deleting a logging configuration disables UDF logging for a region and environment. Deletion may disrupt debugging and troubleshooting for applicable UDFs, because logging no longer occurs.

Run the following commands to delete the logging configuration for a region and environment.

Confluent CLIREST API

To delete a logging configuration, run the following commands.

  1. Log in to Confluent Cloud.

         confluent login --organization-id ${ORG_ID} --prompt

  2. Run the following command to delete the logging configuration specified by UDF_LOG_ID.

         confluent custom-code-logging delete ${UDF_LOG_ID}

  1. Run the following command to delete the logging configuration specified by UDF_LOG_ID.

         curl --silent -X DELETE \
           -u ${CLOUD_API_KEY}:${CLOUD_API_SECRET} \
           https://api.confluent.cloud/ccl/v1/custom-code-loggings/${UDF_LOG_ID}?environment=${ENV_ID}

### View the region and environment¶

Run the following commands to view the region and environment for a logging configuration.

Confluent CLIREST API

To view the region and environment for a UDF log, run the following commands.

  1. Log in to Confluent Cloud.

         confluent login --organization-id ${ORG_ID} --prompt

  2. Run the following command to view the region and environment of a UDF log.

         confluent custom-code-logging describe ${UDF_LOG_ID}

Your output should resemble:

    +-------------+------------+
    | Id          | ccl-4l5klo |
    | Cloud       | aws        |
    | Region      | us-west-2  |
    | Environment | env-xmzdkk |
    +-------------+------------+

  1. Run the following command to view the region and environment of a UDF log.

         curl --silent -X GET \
           -u ${CLOUD_API_KEY}:${CLOUD_API_SECRET} \
           https://api.confluent.cloud/ccl/v1/custom-code-loggings/${UDF_LOG_ID}?environment=${ENV_ID}

### List logging configurations¶

Run the following commands to list the active logging configurations.

Confluent CLIREST API

To list the active UDF logs, run the following commands.

  1. Log in to Confluent Cloud.

         confluent login --organization-id ${ORG_ID} --prompt

  2. Run the following command to view the active UDF logs.

         confluent custom-code-logging list

Your output should resemble:

          Id     | Cloud |  Region   | Environment
    -------------+-------+-----------+--------------
      ccl-4l5klo | aws   | us-west-2 | env-xmzdkk

  1. Run the following command to view the active UDF logs.

         curl --silent -X GET \
           -u ${CLOUD_API_KEY}:${CLOUD_API_SECRET} \
           https://api.confluent.cloud/ccl/v1/custom-code-loggings?environment=${ENV_ID}

### Update the log level¶

Run the following commands to update the log level for a logging configuration.

The following log levels are supported.

  * OFF
  * FATAL
  * ERROR
  * WARN
  * INFO
  * DEBUG
  * TRACE
  * ALL

Confluent CLIREST API

To change the logging level for an active UDF log, run the following commands.

  1. Log in to Confluent Cloud.

         confluent login --organization-id ${ORG_ID} --prompt

  2. Run the following command to change the logging level for an active UDF log.

         confluent custom-code-logging update --log-level DEBUG

  1. Run the following command to change the logging level for an active UDF log.

         curl --silent -X PATCH \
         -u ${CLOUD_API_KEY}:${CLOUD_API_SECRET} \
         https://api.confluent.cloud/ccl/v1/custom-code-loggings/${UDF_LOG_ID}?environment=${ENV_ID}
         -d
         '{
            "destination_settings": {
              "kind": "Kafka",
              "log_level": "ERROR"
           }
         }'
