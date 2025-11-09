---
document_id: flink_how-to-guides_enable-udf-logging_chunk_3
source_file: flink_how-to-guides_enable-udf-logging.md
source_url: https://docs.confluent.io/cloud/current/flink/how-to-guides/enable-udf-logging.html
title: Enable Logging in a User Defined Function with Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

can see the logged events.

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
