---
source_url: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/flink-rest-api.html
title: Flink REST API in Confluent Cloud for Apache Flink
hierarchy: ['operate-and-deploy', 'flink-rest-api.html']
scraped_date: 2025-09-05T13:46:55.792425
---

# Flink SQL REST API for Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides a REST API for managing your Flink SQL statements, compute pools, and connections programmatically.

Use the REST API to manage these features:

  * Artifacts (user-defined functions)
  * Compute pools
  * Connections
  * List available regions
  * Statements

For the complete Flink REST API reference, see:

  * [Artifacts (user-defined functions)](/cloud/current/api.html#tag/Flink-Artifacts-\(artifactv1\))
  * [Compute Pools](/cloud/current/api.html#tag/Compute-Pools-\(fcpmv2\))
  * [Connections](/cloud/current/api.html#tag/Connections-\(sqlv1\))
  * [Regions](/cloud/current/api.html##tag/Regions-\(fcpmv2\))
  * [Statements](/cloud/current/api.html#tag/Statements-\(sqlv1\))

In addition to the REST API, you can manage Flink resources by using these Confluent tools:

  * [Cloud Console](../get-started/quick-start-cloud-console.html#flink-sql-quick-start-run-sql-statement)
  * [Confluent CLI](../reference/flink-sql-cli.html#flink-sql-confluent-cli)
  * [SQL shell](../get-started/quick-start-shell.html#flink-sql-quick-start-shell)
  * [Confluent Terraform Provider](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs)

## Prerequisites¶

To manage Flink resources by using the REST API, you must generate an API key that’s specific to the Flink environment. Also, you need Confluent Cloud account details, like your organization and environment identifiers.

  * **Flink API Key:** Follow the steps in Generate a Flink API key.
  * **Organization ID:** The identifier your organization, for example, “b0b421724-4586-4a07-b787-d0bb5aacbf87”.
  * **Environment ID:** The identifier of the environment where your Flink SQL statements run, for example, “env-z3y2x1”.
  * **Cloud provider name:** The name of the cloud provider where your cluster runs, for example, “AWS”. To see the available providers, run the `confluent flink region list` command.
  * **Cloud region:** The name of the region where your cluster runs, for example, “us-east-1”. To see the available regions, run the `confluent flink region list` command.

Depending on the request, you may need these details:

  * **Cloud API key:** Some requests require a Confluent Cloud API key and secret, which are distinct from a Flink API key and secret. Follow the instructions [here](../../security/authenticate/workload-identities/service-accounts/api-keys/manage-api-keys.html#cloud-cloud-api-keys) to create a new API key for Confluent Cloud, and on the <https://confluent.cloud/settings/api-keys> page, select the **Cloud resource management** tile for the API key’s resource scope.
  * **Principal ID:** The identifier of your user account or a service account, for example, “u-aq1dr2” for a user account or “sa-23kgz4” for a service account.
  * **Compute pool ID:** The identifier of the compute pool that runs your Flink SQL statements, for example, “lfcp-8m03rm”.
  * **Statement name:** A unique name for a Flink SQL statement.
  * **SQL code:** The code for a Flink SQL statement.

## Rate limits¶

Requests to the Flink REST API are rate-limited per IP address.

  * Concurrent connections: 100
  * Requests per minute: 1000
  * Requests per second: 50

## Private networking endpoints¶

If you have enabled Flink [private networking](../concepts/flink-private-networking.html#flink-sql-private-networking), the REST endpoints are different.

    <!-- Without private network -->
    https://flink.${CLOUD_REGION}.${CLOUD_PROVIDER}.confluent.cloud/
    
    <!-- With private network -->
    https://flink.${CLOUD_REGION}.${CLOUD_PROVIDER}.private.confluent.cloud/

For example, if you send a request to the `us-east-1` AWS region without a private network, the host is:

    <!-- Without private network -->
    https://flink.us-east-1.aws.confluent.cloud

With a private network, the host is:

    <!-- With private network -->
    https://flink.us-east-1.aws.private.confluent.cloud

## Generate a Flink API key¶

To access the REST API, you need an API key specifically for Flink. This key is distinct from the Confluent Cloud API key.

Before you create an API key for Flink access, decide whether you want to create long-running Flink SQL statements. If you need long-running Flink SQL statements, Confluent recommends using a service account and creating an API key for it. If you want to run only interactive queries or statements for a short time while developing queries, you can create an API key for your user account.

  * Follow the steps in [Generate an API Key for Access](generate-api-key-for-flink.html#flink-generate-api-key).

Run the following commands to save your API key and secret in environment variables.

    export FLINK_API_KEY="<flink-api-key>"
    export FLINK_API_SECRET="<flink-api-secret>"

The REST API uses basic authentication, which means that you provide a base64-encoded string made from your Flink API key and secret in the request header.

You can use the `base64` command to encode the “key:secret” string. Be sure to use the `-n` option of the `echo` command to prevent newlines from being embedded in the encoded string. If you’re on Linux, be sure to use the `-w 0` option of the `base64` command, to prevent the string from being line-wrapped.

For convenience, save the encoded string in an environment variable:

    export BASE64_FLINK_KEY_AND_SECRET=$(echo -n "${FLINK_API_KEY}:${FLINK_API_SECRET}" | base64 -w 0)

## Manage statements¶

Using requests to the Flink REST API, you can perform these actions:

  * Submit a statement
  * Get a statement
  * List statements
  * Update metadata for a statement
  * Delete a statement

### Flink SQL statement schema¶

A statement has the following schema:

    api_version: "sql/v1"
    kind: "Statement"
    organization_id: "" # Identifier of your Confluent Cloud organization
    environment_id: "" # Identifier of your Confluent Cloud environment
    name: "" # Primary identifier of the statement, must be unique within the environment, 100 max length, [a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*
    metadata:
      created_at: "" # Creation timestamp of this resource
      updated_at: "" # Last updated timestamp of this resource
      resource_version: "" # Generated by the system and updated whenever the statement is updated (including by the system). Opaque and should not be parsed.
      self: "" # An absolute URL to this resource
      uid: "" # uid is unique in time and space (i.e., even if the name is re-used)
    spec:
      compute_pool_id: "" # The ID of the compute pool the statement should run in. DNS Subdomain (RFC 1123) – 255 max len, [a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*
      principal: "" # user or service account ID
      properties: map[string]string # Optional. request/client properties
      statement: "SELECT * from Orders;" # The raw SQL text
      stopped: false # Boolean, specifying if the statement should be stopped
    status:
      phase: PENDING | RUNNING | COMPLETED | DELETING | FAILING | FAILED
      detail: "" # Optional. Human-readable description of phase.
      result_schema: "" # Optional. JSON object in TableSchema format; describes the data returned by the results serving API.

The statement name has a maximum length of 100 characters and must satisfy the following regular expression:

    [a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*

The underscore character (`_`) and period character (`.`) are not supported.

### Submit a statement¶

You can submit a Flink SQL statement by sending a POST request to the [Statements endpoint](/cloud/current/api.html#tag/Statements-\(sqlv1\)/operation/createSqlv1Statement).

Submitting a Flink SQL statement requires the following inputs:

    export FLINK_API_KEY="<flink-api-key>"
    export FLINK_API_SECRET="<flink-api-secret>"
    export BASE64_FLINK_KEY_AND_SECRET=$(echo -n "${FLINK_API_KEY}:${FLINK_API_SECRET}" | base64 -w 0)
    export STATEMENT_NAME="<statement-name>" # example: "user-filter"
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export PRINCIPAL_ID="<principal-id>" # (optional) example: "sa-23kgz4" for a service account, or "u-aq1dr2" for a user account
    export SQL_CODE="<sql-statement-text>" # example: "SELECT * FROM USERS;"
    export JSON_DATA="<payload-string>"

The PRINCIPAL_ID parameter is optional. Confluent Cloud infers the principal from the provided Flink API key.

The following JSON shows an example payload:

    {
      "name": "${STATEMENT_NAME}",
      "organization_id": "${ORG_ID}",
      "environment_id": "${ENV_ID}",
      "spec": {
        "statement": "${SQL_CODE}",
        "properties": {
          "key1": "value1",
          "key2": "value2"
        },
        "compute_pool_id": "${COMPUTE_POOL_ID}",
        "principal": "${PRINCIPAL_ID}",
        "stopped": false
      }
    }

Quotation mark characters in the JSON string must be escaped, so the payload string to send resembles the following:

    export JSON_DATA="{
      \"name\": \"${STATEMENT_NAME}\",
      \"organization_id\": \"${ORG_ID}\",
      \"environment_id\": \"${ENV_ID}\",
      \"spec\": {
        \"statement\": \"${SQL_CODE}\",
        \"properties\": {
          \"key1\": \"value1\",
          \"key2\": \"value2\"
        },
        \"compute_pool_id\": \"${COMPUTE_POOL_ID}\",
        \"principal\": \"${PRINCIPAL_ID}\",
        \"stopped\": false
      }
    }"

The following command sends a POST request that submits a Flink SQL statement.

    curl --request POST \
      --url "https://flink.${CLOUD_REGION}.${CLOUD_PROVIDER}.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/statements" \
      --header "Authorization: Basic ${BASE64_FLINK_KEY_AND_SECRET}" \
      --header 'content-type: application/json' \
      --data "${JSON_DATA}"

Your output should resemble:

Response from a request to submit a SQL statement 

    {
      "api_version": "sql/v1",
      "environment_id": "env-z3y2x1",
      "kind": "Statement",
      "metadata": {
        "created_at": "2023-12-16T17:12:08.914198Z",
        "resource_version": "1",
        "self": "https://flink.us-east-1.aws.confluent.cloud/sql/v1/organizations/b0b21724-4586-4a07-b787-d0bb5aacbf87/environments/env-z3y2x1/statements/demo-statement-1",
        "uid": "0005dd7b-8a7e-4274-b97e-c21b134d98f0",
        "updated_at": "2023-12-16T17:12:08.914198Z"
      },
      "name": "demo-statement-1",
      "organization_id": "b0b21724-4586-4a07-b787-d0bb5aacbf87",
      "spec": {
        "compute_pool_id": "lfcp-8m03rm",
        "principal": "u-aq1dr2",
        "properties": null,
        "statement": "select 1;",
        "stopped": false
      },
      "status": {
        "detail": "",
        "phase": "PENDING"
      }
    }

### Get a statement¶

Get the details about a Flink SQL statement by sending a GET request to the [Statements endpoint](/cloud/current/api.html#tag/Statements-\(sqlv1\)/operation/getSqlv1Statement).

Getting a Flink SQL statement requires the following inputs:

    export FLINK_API_KEY="<flink-api-key>"
    export FLINK_API_SECRET="<flink-api-secret>"
    export BASE64_FLINK_KEY_AND_SECRET=$(echo -n "${FLINK_API_KEY}:${FLINK_API_SECRET}" | base64 -w 0)
    export STATEMENT_NAME="<statement-name>" # example: "user-filter"
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"

The following command gets a Flink SQL statement’s details by its name. Attempting to get a deleted statement returns `404`.

    curl --request GET \
     --url "https://flink.${CLOUD_REGION}.${CLOUD_PROVIDER}.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/statements/${STATEMENT_NAME}" \
     --header "Authorization: Basic ${BASE64_FLINK_KEY_AND_SECRET}"

Your output should resemble:

Response from a request to get a SQL statement 

    {
      "api_version": "sql/v1",
      "environment_id": "env-z3y2x1",
      "kind": "Statement",
      "metadata": {
        "created_at": "2023-12-16T16:08:36.650591Z",
        "resource_version": "13",
        "self": "https://flink.us-east-1.aws.confluent.cloud/sql/v1/organizations/b0b21724-4586-4a07-b787-d0bb5aacbf87/environments/env-z3y2x1/statements/demo-statement-1",
        "uid": "5387a4a4-02dd-4375-8db1-80bdd82ede96",
        "updated_at": "2023-12-16T16:10:05.353298Z"
      },
      "name": "demo-statement-1",
      "organization_id": "b0b21724-4586-4a07-b787-d0bb5aacbf87",
      "spec": {
        "compute_pool_id": "lfcp-8m03rm",
        "principal": "u-aq1dr2",
        "properties": null,
        "statement": "select 1;",
        "stopped": false
      },
      "status": {
        "detail": "",
        "phase": "COMPLETED",
        "result_schema": {
          "columns": [
            {
              "name": "EXPR$0",
              "type": {
                "nullable": false,
                "type": "INTEGER"
              }
            }
          ]
        }
      }
    }

Tip

Pipe the result through `jq` to extract the code for the Flink SQL statement:

    curl --request GET \
      --url "https://flink.${CLOUD_REGION}.${CLOUD_PROVIDER}.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/statements/${STATEMENT_NAME}" \
      --header "Authorization: Basic ${BASE64_FLINK_KEY_AND_SECRET}" \
      | jq -r '.spec.statement'

Your output should resemble:

    select 1;

### List statements¶

List the statements in an environment by sending a GET request to the [Statements endpoint](/cloud/current/api.html#tag/Statements-\(sqlv1\)/operation/listSqlv1Statements).

Request Query Parameters

  * `spec.compute_pool_id` (optional): Fetch only the statements under this compute pool ID.
  * `page_token` (optional): Retrieve a page based on a previously received token (via the `metadata.next` field of `StatementList`).
  * `page_size` (optional): Maximum number of items to return in a page.

Listing all Flink SQL statements requires the following inputs:

    export FLINK_API_KEY="<flink-api-key>"
    export FLINK_API_SECRET="<flink-api-secret>"
    export BASE64_FLINK_KEY_AND_SECRET=$(echo -n "${FLINK_API_KEY}:${FLINK_API_SECRET}" | base64 -w 0)
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="environment-id" # example: "env-z3y2x1"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"

The following command returns details for all non-deleted Flink SQL statements under the scope of the environment (one or more compute pools) where you have permission to do a GET request.

    curl --request GET \
      --url "https://flink.${CLOUD_REGION}.${CLOUD_PROVIDER}.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/statements" \
      --header "Authorization: Basic ${BASE64_FLINK_KEY_AND_SECRET}"

Your output should resemble:

Response from a request to list the statements in an environment 

    {
      "api_version": "sql/v1",
      "data": [
        {
          "api_version": "sql/v1",
          "environment_id": "env-z3y2x1",
          "kind": "Statement",
          "metadata": {
            "created_at": "2023-12-16T16:08:36.650591Z",
            "resource_version": "13",
            "self": "https://flink.us-east-1.aws.confluent.cloud/sql/v1/organizations/b0b21724-4586-4a07-b787-d0bb5aacbf87/environments/env-z3y2x1/statements/demo-statement-1",
            "uid": "5387a4a4-02dd-4375-8db1-80bdd82ede96",
            "updated_at": "2023-12-16T16:10:05.353298Z"
          },
          "name": "demo-statement-1",
          "organization_id": "b0b21724-4586-4a07-b787-d0bb5aacbf87",
          "spec": {
            "compute_pool_id": "lfcp-8m03rm",
            "principal": "u-aq1dr2",
            "properties": null,
            "statement": "select 1;",
            "stopped": false
          },
          "status": {
            "detail": "",
            "phase": "COMPLETED",
            "result_schema": {
              "columns": [
                {
                  "name": "EXPR$0",
                  "type": {
                    "nullable": false,
                    "type": "INTEGER"
                  }
                }
              ]
            }
          }
        }

### Update metadata for a statement¶

Update the metadata for a statement by sending a PUT request to the [Statements endpoint](/cloud/current/api.html#tag/Statements-\(sqlv1\)/operation/updateSqlv1Statement).

You can stop and resume a statement by setting `stopped` in the `spec` to `true` to stop the statement and `false` to resume the statement.

  * You can update the statement’s name, compute pool, and security principal. To update the compute pool or principal, you must stop the statement, send the update request, then restart the statement.
  * The statement’s code is immutable.
  * You must specify a resource version in the payload metadata.

Updating metadata for an existing Flink SQL statement requires the following inputs:

    export FLINK_API_KEY="<flink-api-key>"
    export FLINK_API_SECRET="<flink-api-secret>"
    export BASE64_FLINK_KEY_AND_SECRET=$(echo -n "${FLINK_API_KEY}:${FLINK_API_SECRET}" | base64 -w 0)
    export STATEMENT_NAME="<statement-name>" # example: "user-filter"
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export PRINCIPAL_ID="<principal-id>" # (optional) example: "sa-23kgz4" for a service account, or "u-aq1dr2" for a user account
    export SQL_CODE="<sql-statement-text>" # example: "SELECT * FROM USERS;"
    export RESOURCE_VERSION="<version>" # example: "a3e", must be fetched from the latest version of the statement
    export JSON_DATA="<payload-string>"

The PRINCIPAL_ID parameter is optional. Confluent Cloud infers the principal from the provided Flink API key.

The following JSON shows an example payload:

    {
      "name": "${STATEMENT_NAME}",
      "organization_id": "${ORG_ID}",
      "environment_id": "${ENV_ID}",
      "spec": {
        "statement": "${SQL_CODE}",
        "properties": {
          "key1": "value1",
          "key2": "value2"
        },
        "compute_pool_id": "${COMPUTE_POOL_ID}",
        "principal": "${PRINCIPAL_ID}",
        "stopped": false
      },
      "metadata": {
         "resource_version": "${RESOURCE_VERSION}"
      }
    }

Quotation mark characters in the JSON string must be escaped, so the payload string to send resembles the following:

    export JSON_DATA="{
      \"name\": \"${STATEMENT_NAME}\",
      \"organization_id\": \"${ORG_ID}\",
      \"environment_id\": \"${ENV_ID}\",
      \"spec\": {
        \"statement\": \"${SQL_CODE}\",
        \"properties\": {
          \"key1\": \"value1\",
          \"key2\": \"value2\"
        },
        \"compute_pool_id\": \"${COMPUTE_POOL_ID}\",
        \"principal\": \"${PRINCIPAL_ID}\",
        \"stopped\": false
      },
      \"metadata\": {
        \"resource_version\": \"${RESOURCE_VERSION}\"
      }
    }"

The following command sends a PUT request that updates metadata for an existing Flink SQL statement.

    curl --request PUT \
      --url "https://flink.${CLOUD_REGION}.${CLOUD_PROVIDER}.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/statements/${STATEMENT_NAME}" \
      --header "Authorization: Basic ${BASE64_FLINK_KEY_AND_SECRET}" \
      --header 'content-type: application/json' \
      --data "${JSON_DATA}"

Resource version is required in the PUT request and changes every time the statement is updated, by the system or by the user. It’s not possible to calculate the resource version ahead of time, so if the statement has changed since it was fetched, you must submit a GET request, reapply the modifications, and try the update again.

This means you must loop and retry on 409 errors. The following pseudo code shows the loop.

    while true:
      statement = getStatement()
      # make modifications to the current statement
      statement.spec.stopped = True
      # send the update
      response = updateStatement(statement)
      # if a conflict, retry
      if response.code == 409:
        continue
      elif response.code == 200:
        return "success"
      else:
        return response.error()

### Delete a statement¶

Delete a statement from the compute pool by sending a DELETE request to the [Statements endpoint](/cloud/current/api.html#tag/Statements-\(sqlv1\)/operation/deleteSqlv1Statement).

  * Once a statement deleted, it can’t be undone.
  * State is cleaned up by Confluent Cloud.
  * When deletion is complete, the statement is no longer accessible.

Deleting a statement requires the following inputs:

    export FLINK_API_KEY="<flink-api-key>"
    export FLINK_API_SECRET="<flink-api-secret>"
    export BASE64_FLINK_KEY_AND_SECRET=$(echo -n "${FLINK_API_KEY}:${FLINK_API_SECRET}" | base64 -w 0)
    export STATEMENT_NAME="<statement-name>" # example: "user-filter"
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"

The following command deletes a statement in the specified organization and environment.

    curl --request DELETE \
      --url "https://flink.${CLOUD_REGION}.${CLOUD_PROVIDER}.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/statements/${STATEMENT_NAME}" \
      --header "Authorization: Basic ${BASE64_FLINK_KEY_AND_SECRET}"

## Manage compute pools¶

Using requests to the Flink REST API, you can perform these actions:

  * List Flink compute pools
  * Create a Flink compute pool
  * Read a Flink compute pool
  * Update a Flink compute pool
  * Delete a Flink compute pool

You must be authorized to create, update, delete (`FlinkAdmin`) or use (`FlinkDeveloper`) a compute pool. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](flink-rbac.html#flink-rbac).

### List Flink compute pools¶

List the compute pools in your environment by sending a GET request to the [Compute Pools endpoint](/cloud/current/api.html#tag/Compute-Pools-\(fcpmv2\)/operation/listFcpmV2ComputePools).

  * This request uses your Cloud API key instead of the Flink API key.

Listing the compute pools in your environment requires the following inputs:

    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following command to list the compute pools in your environment.

    curl --request GET \
         --url "https://confluent.cloud/api/fcpm/v2/compute-pools?environment=${ENV_ID}&page_size=100" \
         --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
         | jq -r '.data[] | .spec.display_name, {id}'

Your output should resemble:

    compute_pool_0
    {
      "id": "lfcp-j123kl"
    }
    compute_pool_2
    {
      "id": "lfcp-abc1de"
    }
    my-lfcp-01
    {
      "id": "lfcp-l2mn3o"
    }
    ...

Find your compute pool in the list and save its ID in an environment variable.

    export COMPUTE_POOL_ID="<your-compute-pool-id>"

### Create a Flink compute pool¶

Create a compute pool in your environment by sending a POST request to the [Compute Pools endpoint](/cloud/current/api.html#tag/Compute-Pools-\(fcpmv2\)/operation/createFcpmV2ComputePool).

  * This request uses your Cloud API key instead of the Flink API key.

Creating a compute pool requires the following inputs:

    export COMPUTE_POOL_NAME="<compute-pool-name>" # human readable name, for example: "my-compute-pool"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export MAX_CFU="<max-cfu>" # example: 5
    export JSON_DATA="<payload-string>"

The following JSON shows an example payload. The `network` key is optional.

    {
      "spec": {
        "display_name": "${COMPUTE_POOL_NAME}",
        "cloud": "${CLOUD_PROVIDER}",
        "region": "${CLOUD_REGION}",
        "max_cfu": ${MAX_CFU},
        "environment": {
          "id": "${ENV_ID}"
        },
        "network": {
          "id": "n-00000",
          "environment": "string"
        }
      }
    }

Quotation mark characters in the JSON string must be escaped, so the payload string to send resembles the following:

    export JSON_DATA="{
      \"spec\": {
        \"display_name\": \"${COMPUTE_POOL_NAME}\",
        \"cloud\": \"${CLOUD_PROVIDER}\",
        \"region\": \"${CLOUD_REGION}\",
        \"max_cfu\": ${MAX_CFU},
        \"environment\": {
          \"id\": \"${ENV_ID}\"
        }
      }
    }"

The following command sends a POST request to create a compute pool.

    curl --request POST \
      --url https://api.confluent.cloud/fcpm/v2/compute-pools \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
      --header 'content-type: application/json' \
      --data "${JSON_DATA}"

Your output should resemble:

Response from a request to create a compute pool 

    {
        "api_version": "fcpm/v2",
        "id": "lfcp-6g7h8i",
        "kind": "ComputePool",
        "metadata": {
            "created_at": "2024-02-27T22:44:27.18964Z",
            "resource_name": "crn://confluent.cloud/organization=b0b21724-4586-4a07-b787-d0bb5aacbf87/environment=env-z3y2x1/flink-region=aws.us-east-1/compute-pool=lfcp-6g7h8i",
            "self": "https://api.confluent.cloud/fcpm/v2/compute-pools/lfcp-6g7h8i",
            "updated_at": "2024-02-27T22:44:27.18964Z"
        },
        "spec": {
            "cloud": "AWS",
            "display_name": "my-compute-pool",
            "environment": {
                "id": "env-z3y2x1",
                "related": "https://api.confluent.cloud/fcpm/v2/compute-pools/lfcp-6g7h8i",
                "resource_name": "crn://confluent.cloud/organization=b0b21724-4586-4a07-b787-d0bb5aacbf87/environment=env-z3y2x1"
            },
            "http_endpoint": "https://flink.us-east-1.aws.confluent.cloud/sql/v1/organizations/b0b21724-4586-4a07-b787-d0bb5aacbf87/environments/env-z3y2x1",
            "max_cfu": 5,
            "region": "us-east-1"
        },
        "status": {
            "current_cfu": 0,
            "phase": "PROVISIONING"
        }
    }

### Read a Flink compute pool¶

Get the details about a compute pool in your environment by sending a GET request to the [Compute Pools endpoint](/cloud/current/api.html#tag/Compute-Pools-\(fcpmv2\)/operation/getFcpmV2ComputePool).

  * This request uses your Cloud API key instead of the Flink API key.

Getting details about a compute pool requires the following inputs:

    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following command to get details about the compute pool specified in the COMPUTE_POOL_ID environment variable.

    curl --request GET \
      --url "https://api.confluent.cloud/fcpm/v2/compute-pools/${COMPUTE_POOL_ID}?environment=${ENV_ID}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

Your output should resemble:

Response from a request to read a compute pool 

    {
        "api_version": "fcpm/v2",
        "id": "lfcp-6g7h8i",
        "kind": "ComputePool",
        "metadata": {
            "created_at": "2024-02-27T22:44:27.18964Z",
            "resource_name": "crn://confluent.cloud/organization=b0b21724-4586-4a07-b787-d0bb5aacbf87/environment=env-z3y2x1/flink-region=aws.us-east-1/compute-pool=lfcp-6g7h8i",
            "self": "https://api.confluent.cloud/fcpm/v2/compute-pools/lfcp-6g7h8i",
            "updated_at": "2024-02-27T22:44:27.18964Z"
        },
        "spec": {
            "cloud": "AWS",
            "display_name": "my-compute-pool",
            "environment": {
                "id": "env-z3y2x1",
                "related": "https://api.confluent.cloud/fcpm/v2/compute-pools/lfcp-6g7h8i",
                "resource_name": "crn://confluent.cloud/organization=b0b21724-4586-4a07-b787-d0bb5aacbf87/environment=env-z3y2x1"
            },
            "http_endpoint": "https://flink.us-east-1.aws.confluent.cloud/sql/v1/organizations/b0b21724-4586-4a07-b787-d0bb5aacbf87/environments/env-z3y2x1",
            "max_cfu": 5,
            "region": "us-east-1"
        },
        "status": {
            "current_cfu": 0,
            "phase": "PROVISIONED"
        }
    }

### Update a Flink compute pool¶

Update a compute pool in your environment by sending a PATCH request to the [Compute Pools endpoint](/cloud/current/api.html#tag/Compute-Pools-\(fcpmv2\)/operation/updateFcpmV2ComputePool).

  * This request uses your Cloud API key instead of the Flink API key.

Updating a compute pool requires the following inputs:

    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"
    export MAX_CFU="<max-cfu>" # example: 5
    export JSON_DATA="<payload-string>"

The following JSON shows an example payload. The `network` key is optional.

    {
      "spec": {
        "display_name": "${COMPUTE_POOL_NAME}",
        "max_cfu": ${MAX_CFU},
        "environment": {
          "id": "${ENV_ID}"
        }
      }
    }

Quotation mark characters in the JSON string must be escaped, so the payload string to send resembles the following:

    export JSON_DATA="{
      \"spec\": {
        \"display_name\": \"${COMPUTE_POOL_NAME}\",
        \"max_cfu\": ${MAX_CFU},
        \"environment\": {
          \"id\": \"${ENV_ID}\"
        }
      }
    }"

Run the following command to update the compute pool specified in the COMPUTE_POOL_ID environment variable.

    curl --request PATCH \
      --url "https://api.confluent.cloud/fcpm/v2/compute-pools/${COMPUTE_POOL_ID}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
      --header 'content-type: application/json' \
      --data "${JSON_DATA}"

### Delete a Flink compute pool¶

Delete a compute pool in your environment by sending a DELETE request to the [Compute Pools endpoint](/cloud/current/api.html#tag/Compute-Pools-\(fcpmv2\)/operation/deleteFcpmV2ComputePool).

  * This request uses your Cloud API key instead of the Flink API key.

Deleting a compute pool requires the following inputs:

    export COMPUTE_POOL_ID="<compute-pool-id>" # example: "lfcp-8m03rm"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following command to delete the compute pool specified in the COMPUTE_POOL_ID environment variable.

    curl --request DELETE \
      --url "https://api.confluent.cloud/fcpm/v2/compute-pools/${COMPUTE_POOL_ID}?environment=${ENV_ID}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

## List Flink regions¶

List the regions where Flink is available by sending a GET request to the [Regions endpoint](/cloud/current/api.html#tag/Regions-\(fcpmv2\)/operation/listFcpmV2Regions).

  * This request uses your Cloud API key instead of the Flink API key.

Getting details about a compute pool requires the following inputs:

    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)

Run the following command to list the available Flink regions.

    curl --request GET \
      --url "https://api.confluent.cloud/fcpm/v2/regions" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
      | jq -r '.data[].id'

Your output should resemble:

    aws.eu-central-1
    aws.us-east-1
    aws.eu-west-1
    aws.us-east-2
    ...

## Manage Flink artifacts¶

Using requests to the Flink REST API, you can perform these actions:

  * List Flink artifacts
  * Create a Flink artifact
  * Read an artifact
  * Update an artifact
  * Delete an artifact

An artifact has the following schema:

    api_version: artifact/v1
    kind: FlinkArtifact
    id: dlz-f3a90de
    metadata:
      self: 'https://api.confluent.cloud/artifact/v1/flink-artifacts/fa-12345'
      resource_name: crn://confluent.cloud/organization=<org-id>/flink-artifact=fa-12345
      created_at: '2006-01-02T15:04:05-07:00'
      updated_at: '2006-01-02T15:04:05-07:00'
      deleted_at: '2006-01-02T15:04:05-07:00'
    cloud: AWS
    region: us-east-1
    environment: env-00000
    display_name: string
    class: io.confluent.example.SumScalarFunction
    content_format: JAR
    description: string
    documentation_link: '^$|^(http://|https://).'
    runtime_language: JAVA
    versions:
      - version: cfa-ver-001
        release_notes: string
        is_beta: true
        artifact_id: {}
        upload_source:
          api_version: artifact.v1/UploadSource
          kind: PresignedUrl
          id: dlz-f3a90de
          metadata:
            self: https://api.confluent.cloud/artifact.v1/UploadSource/presigned-urls/pu-12345
            resource_name: crn://confluent.cloud/organization=<org-id>/presigned-url=pu-12345
            created_at: '2006-01-02T15:04:05-07:00'
            updated_at: '2006-01-02T15:04:05-07:00'
            deleted_at: '2006-01-02T15:04:05-07:00'
          location: PRESIGNED_URL_LOCATION
          upload_id: <guid>

### List Flink artifacts¶

List the artifacts, like user-defined functions (UDFs), in your environment by sending a GET request to the [List Artifacts endpoint](/cloud/current/api.html#tag/Flink-Artifacts-\(artifactv1\)/operation/listArtifactV1FlinkArtifacts).

  * This request uses your Cloud API key instead of the Flink API key.

Listing the artifacts in your environment requires the following inputs:

    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following command to list the artifacts in your environment.

    curl --request GET \
         --url "https://api.confluent.cloud/artifact/v1/flink-artifacts?cloud=${CLOUD_PROVIDER}&region=${CLOUD_REGION}&environment=${ENV_ID}" \
         --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
         | jq -r '.data[] | .spec.display_name, {id}'

Your output should resemble:

    {
      "id": "cfa-e8rzq7"
    }

### Create a Flink artifact¶

Creating an artifact, like a user-defined function (UDF), requires these steps:

  1. Request a presigned upload URL for a new Flink Artifact by sending a POST request to the [Presigned URLs endpoint](/cloud/current/api.html#tag/Presigned-Urls-\(artifactv1\)/The-Presigned-Urls-Model).
  2. Upload your JAR file to the object storage provider by using the results from the presigned URL request.
  3. Create the artifact in your environment by sending a POST request to the [Create Artifact endpoint](/cloud/current/api.html#tag/Flink-Artifacts-\(artifactv1\)/operation/createArtifactV1FlinkArtifact).

  * These requests use your Cloud API key instead of the Flink API key.

Creating an artifact in your environment requires the following inputs:

    export ARTIFACT_DISPLAY_NAME="<human-readable-name>" # example: "my-udf"
    export ARTIFACT_DESCRIPTION="<description>" # example: "This is a demo UDF."
    export ARTIFACT_DOC_LINK="<url-to-documentation>" # example: "https://docs.example.com/my-udf"
    export CLASS_NAME="<java-class-name>" # example: "io.confluent.example.SumScalarFunction"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

The following JSON shows an example payload.

    {
      "content_format": "JAR",
      "cloud": "${CLOUD_PROVIDER}",
      "environment": "${ENV_ID}",
      "region": "${CLOUD_REGION}"
    }

Quotation mark characters in the JSON string must be escaped, so the payload string to send resembles the following:

    export JSON_DATA="{
      \"content_format\": \"JAR\",
      \"cloud\": \"${CLOUD_PROVIDER}\",
      \"environment\": \"${ENV_ID}\",
      \"region\": \"${CLOUD_REGION}\"
    }"

Run the following command to request the upload identifier and the presigned upload URL for your artifact.

    curl --request POST \
         --url https://api.confluent.cloud/artifact/v1/presigned-upload-url \
         --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
         --header 'content-type: application/json' \
         --data "${JSON_DATA}"

Your output should resemble:

    {
      "api_version": "artifact/v1",
      "cloud": "AWS",
      "content_format": "JAR",
      "kind": "PresignedUrl",
      "region": "us-east-1",
      "upload_form_data": {
        "bucket": "confluent-custom-connectors-prod-us-east-1",
        "key": "staging/ccp/v1/<your-org-id>/custom-plugins/<guid>/plugin.jar",
        "policy": "ey…",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "AS…/20241121/us-east-1/s3/aws4_request",
        "x-amz-date": "20241121T212232Z",
        "x-amz-security-token": "IQ…",
        "x-amz-signature": "52…"
      },
      "upload_id": "<upload-id-guid>",
      "upload_url": "https://confluent-custom-connectors-prod-us-east-1.s3.dualstack.us-east-1.amazonaws.com/"
    }

For convenience, save the security details in environment variables:

    export UPLOAD_ID="<upload-id-guid>"
    export UPLOAD_URL="<upload_url>"
    export UPLOAD_BUCKET="<bucket>"
    export UPLOAD_KEY="<key>"
    export UPLOAD_POLICY="<policy>"
    export UPLOAD_KEY="<key>"
    export X_AMZ_ALGORITHM="<x-amz-algorithm>"
    export X_AMZ_CREDENTIAL="<x-amz-credential>"
    export X_AMZ_DATE="<x-amz-date>"
    export X_AMZ_SECURITY_TOKEN="<x-amz-security-token>"
    export X_AMZ_SIGNATURE="<x-amz-signature>"

Once you have the presigned URL, ID, bucket policy, and other security details, upload your JAR to the bucket. The following example provides a curl command you can use to upload your JAR file.

Note

When specifying the JAR file to upload, you must use the `@` symbol at the start of the file path. For example, `-F file=@</path/to/upload/file>`. If the `@` symbol is not used, you may see an error stating that `Your proposed upload is smaller than the minimum allowed size.`

    curl -X POST "${UPLOAD_URL}" \
      -F "bucket=${UPLOAD_BUCKET}" \
      -F "key=${UPLOAD_KEY}" \
      -F "policy=${UPLOAD_POLICY}" \
      -F "x-amz-algorithm=${X_AMZ_ALGORITHM}" \
      -F "x-amz-credential=${X_AMZ_CREDENTIAL}" \
      -F "x-amz-date=${X_AMZ_DATE}" \
      -F "x-amz-security-token=${X_AMZ_SECURITY_TOKEN}" \
      -F "x-amz-signature=${X_AMZ_SIGNATURE}" \
      -F file=@/path/to/udf_file.jar

When your JAR file is uploaded to the object score, you can create the UDF in Confluent Cloud for Apache Flink by sending a POST request to the [Create Artifact endpoint](/cloud/current/api.html#tag/Flink-Artifacts-\(artifactv1\)/operation/createArtifactV1FlinkArtifact).

The following JSON shows an example payload.

    {
      "cloud": "${CLOUD_PROVIDER}",
      "region": "${CLOUD_REGION}",
      "environment": "${ENV_ID}",
      "display_name": "${ARTIFACT_DISPLAY_NAME}",
      "class": "${CLASS_NAME}",
      "content_format": "JAR",
      "description": "${ARTIFACT_DESCRIPTION}",
      "documentation_link": "${ARTIFACT_DOC_LINK}",
      "runtime_language": "JAVA",
      "upload_source": {
        "location": "PRESIGNED_URL_LOCATION",
        "upload_id": "${UPLOAD_ID}"
      }
    }

Quotation mark characters in the JSON string must be escaped, so the payload string resembles the following:

    export JSON_DATA="{
      \"cloud\": \"${CLOUD_PROVIDER}\",
      \"region\": \"${CLOUD_REGION}\",
      \"environment\": \"${ENV_ID}\",
      \"display_name\": \"${ARTIFACT_DISPLAY_NAME}\",
      \"class\": \"${CLASS_NAME}\",
      \"content_format\": \"JAR\",
      \"description\": \"${ARTIFACT_DESCRIPTION}\",
      \"documentation_link\": \"${ARTIFACT_DOC_LINK}\",
      \"runtime_language\": \"JAVA\",
      \"upload_source\": {
        \"location\": \"PRESIGNED_URL_LOCATION\",
        \"upload_id\": \"${UPLOAD_ID}\"
      }
    }"

Run the following command to create the artifact in your environment.

    curl --request POST \
         --url "https://api.confluent.cloud/artifact/v1/flink-artifacts?cloud=${CLOUD_REGION}&region=${CLOUD_REGION}&environment=${ENV_ID}" \
         --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
         --header 'content-type: application/json' \
         --data "${JSON_DATA}"

### Read an artifact¶

Get the details about an artifact in your environment by sending a GET request to the [Read Artifact endpoint](/cloud/current/api.html#tag/Flink-Artifacts-\(artifactv1\)/operation/getArtifactV1FlinkArtifact).

  * This request uses your Cloud API key instead of the Flink API key.

Getting details about an artifact requires the following inputs:

    export ARTIFACT_ID="<artifact-id>" # example: cfa-e8rzq7
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following command to get details about the artifact specified by the ARTIFACT_ID environment variable.

    curl --request GET \
      --url "https://api.confluent.cloud/artifact/v1/flink-artifacts/${ARTIFACT_ID}?cloud=${CLOUD_PROVIDER}&region=${CLOUD_REGION}&environment=${ENV_ID}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

Your output should resemble:

Response from a request to get details about an artifact 

    {
      "api_version": "artifact/v1",
      "class": "default",
      "cloud": "AWS",
      "content_format": "JAR",
      "description": "",
      "display_name": "udf_example",
      "documentation_link": "",
      "environment": "env-z3q9rd",
      "id": "cfa-e8rzq7",
      "kind": "FlinkArtifact",
      "metadata": {
        "created_at": "2024-11-21T21:52:43.788042Z",
        "resource_name": "crn://confluent.cloud/organization=<org-id>/flink-artifact=cfa-e8rzq7",
        "self": "https://api.confluent.cloud/artifact/v1/flink-artifacts/cfa-e8rzq7",
        "updated_at": "2024-11-21T21:52:44.625318Z"
      },
      "region": "us-east-1",
      "runtime_language": "JAVA",
      "versions": [
        {
          "artifact_id": {},
          "is_beta": false,
          "release_notes": "",
          "upload_source": {
            "location": "PRESIGNED_URL_LOCATION",
            "upload_id": ""
          },
          "version": "ver-xq72dk"
        }
      ]
    }

### Update an artifact¶

Update an artifact in your environment by sending a PATCH request to the [Update Artifact endpoint](/cloud/current/api.html#tag/Flink-Artifacts-\(artifactv1\)/operation/updateArtifactV1FlinkArtifact).

  * This request uses your Cloud API key instead of the Flink API key.

Updating an artifact in your environment requires the following inputs:

    export ARTIFACT_ID="<artifact-id>" # example: cfa-e8rzq7
    export ARTIFACT_DISPLAY_NAME="<human-readable-name>" # example: "my-udf"
    export ARTIFACT_DESCRIPTION="<description>" # example: "This is a demo UDF."
    export ARTIFACT_DOC_LINK="<url-to-documentation>" # example: "https://docs.example.com/my-udf", "^$|^(http://|https://)."
    export CLASS_NAME="<java-class-name>" # example: "io.confluent.example.SumScalarFunction"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

The following JSON shows an example payload.

Response from a request to update an artifact 

    {
      "cloud": "${CLOUD_PROVIDER}",
      "region": "${CLOUD_REGION}",
      "environment": "${ENV_ID}",
      "display_name": "${ARTIFACT_DISPLAY_NAME}",
      "content_format": "JAR",
      "description": "${ARTIFACT_DESCRIPTION}",
      "documentation_link": "${ARTIFACT_DOC_LINK}",
      "runtime_language": "JAVA",
      "versions": [
        {
          "version": "cfa-ver-001",
          "release_notes": "string",
          "is_beta": true,
          "artifact_id": {
            "cloud": "${CLOUD_PROVIDER}",
            "region": "${CLOUD_REGION}",
            "environment": "${ENV_ID}",
            "display_name": "${ARTIFACT_DISPLAY_NAME}",
            "class": "${CLASS_NAME}",
            "content_format": "JAR",
            "description": "${ARTIFACT_DESCRIPTION}",
            "documentation_link": "${ARTIFACT_DOC_LINK}",
            "runtime_language": "JAVA",
            "versions": [
              {}
            ]
          },
          "upload_source": {
            "location": "PRESIGNED_URL_LOCATION",
            "upload_id": "${UPLOAD_ID}"
          }
        }
      ]
    }

Quotation mark characters in the JSON string must be escaped, so the payload string resembles the following:

    export JSON_DATA="{
      \"cloud\": \"${CLOUD_PROVIDER}\",
      \"region\": \"${CLOUD_REGION}\",
      \"environment\": \"${ENV_ID}\",
      \"display_name\": \"${ARTIFACT_DISPLAY_NAME}\",
      \"content_format\": \"JAR\",
      \"description\": \"${ARTIFACT_DESCRIPTION}\",
      \"documentation_link\": \"${ARTIFACT_DOC_LINK}\",
      \"runtime_language\": \"JAVA\",
      \"versions\": [
        {
          \"version\": \"cfa-ver-001\",
          \"release_notes\": \"string\",
          \"is_beta\": true,
          \"artifact_id\": {
            \"cloud\": \"${CLOUD_PROVIDER}\",
            \"region\": \"${CLOUD_REGION}\",
            \"environment\": \"${ENV_ID}\",
            \"display_name\": \"${ARTIFACT_DISPLAY_NAME}\",
            \"class\": \"${CLASS_NAME}\",
            \"content_format\": \"JAR\",
            \"description\": \"${ARTIFACT_DESCRIPTION}\",
            \"documentation_link\": \"${ARTIFACT_DOC_LINK}\",
            \"runtime_language\": \"JAVA\",
            \"versions\": [
              {}
            ]
          },
          \"upload_source\": {
            \"location\": \"PRESIGNED_URL_LOCATION\",
            \"upload_id\": \"${UPLOAD_ID}\"
          }
        }
      ]
    }"

Run the following command to update the artifact specified by the ARTIFACT_ID environment variable.

    curl --request PATCH \
         --url "https://api.confluent.cloud/artifact/v1/flink-artifacts/${ARTIFACT_ID}?cloud=${CLOUD_PROVIDER}&region=${CLOUD_REGION}&environment=${ENV_ID}" \
         --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
         --header 'content-type: application/json' \
         --data "${JSON_DATA}"

### Delete an artifact¶

Delete an artifact in your environment by sending a DELETE request to the [Delete Artifact endpoint](/cloud/current/api.html#tag/Flink-Artifacts-\(artifactv1\)/operation/deleteArtifactV1FlinkArtifact).

  * This request uses your Cloud API key instead of the Flink API key.

Deleting an artifact in your environment requires the following inputs:

    export ARTIFACT_ID="<artifact-id>" # example: cfa-e8rzq7
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

Run the following command to delete an artifact specified by the ARTIFACT_ID environment variable.

    curl --request DELETE \
      --url "https://api.confluent.cloud/artifact/v1/flink-artifacts/${ARTIFACT_ID}?cloud=${CLOUD_PROVIDER}&region=${CLOUD_REGION}&environment=${ENV_ID}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

## Manage UDF logging¶

When you create a user defined function (UDF) with Confluent Cloud for Apache Flink®, you have the option of enabling logging to a Kafka topic to help with monitoring and debugging. For more information, see [Enable Logging in a User Defined Function](../how-to-guides/enable-udf-logging.html#flink-sql-enable-udf-logging).

Using requests to the Flink REST API, you can perform these actions:

  * Enable logging
  * List UDF logs
  * Disable a UDF log
  * View log details
  * Update the logging level for a UDF log

Managing UDF logs requires the following inputs:

    export UDF_LOG_ID="<udf-log-id>" # example: "ccl-4l5klo"
    export UDF_LOG_TOPIC_NAME="<topic-name>" # example: "udf_log"
    export KAFKA_CLUSTER_ID="<kafka-cluster-id>" # example: "lkc-12345"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export ENV_ID="<environment-id>" # example: "env-z3y2x1"

### Enable logging¶

Run the following command to enable UDF logging.

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

### List UDF logs¶

To list the active UDF logs, run the following commands.

    curl --silent -X GET \
      -u ${CLOUD_API_KEY}:${CLOUD_API_SECRET} \
      https://api.confluent.cloud/ccl/v1/custom-code-loggings?environment=${ENV_ID}

### Disable a UDF log¶

Run the following command to disable UDF logging.

    curl --silent -X DELETE \
      -u ${CLOUD_API_KEY}:${CLOUD_API_SECRET} \
      https://api.confluent.cloud/ccl/v1/custom-code-loggings/${UDF_LOG_ID}?environment=${ENV_ID}

### View log details¶

Run the following command to view the details of a UDF log.

    curl --silent -X GET \
      -u ${CLOUD_API_KEY}:${CLOUD_API_SECRET} \
      https://api.confluent.cloud/ccl/v1/custom-code-loggings/${UDF_LOG_ID}?environment=${ENV_ID}

### Update the logging level for a UDF log¶

Run the following command to change the logging level for an active UDF log.

    cat <<EOF | curl --silent -X PATCH \
      -u ${CLOUD_API_KEY}:${CLOUD_API_SECRET} \
      -d @- https://api.confluent.cloud/ccl/v1/custom-code-loggings/${UDF_LOG_ID}
      {
        "region":"asddf",
        "destination_settings":{
          "kind":"Kafka"
        }
      }
      EOF

## Manage connections¶

To manage connections, you can use the following endpoints:

  * [Create Connection](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/createConnectionV1Connection)
  * [Delete Connection](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/deleteConnectionV1Connection)
  * [Describe Connection](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/describeConnectionV1Connection)
  * [List Connections](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/listConnectionsV1Connection)
  * [Update Connection](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/updateConnectionV1Connection)

You must be authorized to create, update, delete (`FlinkAdmin`) or use (`FlinkDeveloper`) a connection. For more information, see [Grant Role-Based Access in Confluent Cloud for Apache Flink](flink-rbac.html#flink-rbac).

### Create a connection¶

Create a connection in your environment by sending a POST request to the [Connections](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/createSqlv1Connection) endpoint.

Creating a connection requires the following inputs. Credentials vary by service.

    export CONNECTION_NAME="<connection-name>" # example: "my-openai-connection"
    export CONNECTION_TYPE="<connection-type>" # example: "OPENAI"
    export ENDPOINT="<endpoint>" # example: "https://api.openai.com/v1/chat/completions"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export JSON_DATA="<payload-string>"

The following JSON shows an example payload. The `auth_data` key varies by service.

    {
      "name": "${CONNECTION_NAME}",
      "spec": {
        "connection_type": "${CONNECTION_TYPE}",
        "endpoint": "${ENDPOINT}",
        "auth_data": {
          "kind": "PlaintextProvider",
          "data": "string"
        }
      },
      "metadata": {}
    }

Quotation mark characters in the JSON string must be escaped, so the payload string to send resembles the following:

    export JSON_DATA="{
      \"name\": \"${CONNECTION_NAME}\",
      \"spec\": {
        \"connection_type\": \"${CONNECTION_TYPE}\",
        \"endpoint\": \"${ENDPOINT}\",
        \"auth_data\": {
          \"kind\": \"PlaintextProvider\",
          \"data\": \"string\"
        }
      },
      \"metadata\": {}
    }"

The following command sends a POST request to create a connection.

    curl --request POST \
      --url "https://flink.region.provider.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/connections" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
      --header 'content-type: application/json' \
      --data "${JSON_DATA}"

Your output should resemble:

Response from a request to create a connection 

    {
      "api_version": "sql/v1",
      "kind": "Connection",
      "metadata": {
        "self": "https://flink.us-west1.aws.confluent.cloud/sql/v1/organizations/org-abc/environments/env-a1b2c3/connections/my-openai-connection",
        "resource_name": "",
        "created_at": "2006-01-02T15:04:05-07:00",
        "updated_at": "2006-01-02T15:04:05-07:00",
        "deleted_at": "2006-01-02T15:04:05-07:00",
        "uid": "12345678-1234-1234-1234-123456789012",
        "resource_version": "a23av"
      },
      "name": "my-openai-connection",
      "spec": {
        "connection_type": "OPENAI",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "auth_data": {
          "kind": "PlaintextProvider",
          "data": "string"
        }
      },
      "status": {
        "phase": "READY",
        "detail": "Lookup failed: ai.openai.com"
         }
       }
    }

### Delete a connection¶

Delete a connection in your environment by sending a DELETE request to the [Connections endpoint](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/deleteSqlv1Connection).

  * This request uses your Cloud API key instead of the Flink API key.

Deleting a connection requires the following inputs:

    export CONNECTION_NAME="<connection-name>" # example: "my-openai-connection"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"

Run the following command to delete the connection specified in the CONNECTION_NAME environment variable.

    curl --request DELETE \
      --url "https://flink.region.provider.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/connections/${CONNECTION_NAME}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

Describe a connection

Get the details about a connection in your environment by sending a GET request to the [Connections endpoint](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/getSqlv1Connection).

  * This request uses your Cloud API key instead of the Flink API key.

Getting details about a connection requires the following inputs:

    export CONNECTION_NAME="<connection-name>" # example: "my-openai-connection"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"

Run the following command to get details about the connection specified in the CONNECTION_NAME environment variable.

    curl --request GET \
      --url "https://flink.region.provider.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/connections/${CONNECTION_NAME}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

Your output should resemble:

Response from a request to read a connection 

    {
      "api_version": "sql/v1",
      "kind": "Connection",
      "metadata": {
        "self": "https://flink.us-west1.aws.confluent.cloud/sql/v1/organizations/org-abc/environments/env-123/connections/my-openai-connection",
        "resource_name": "",
        "created_at": "2006-01-02T15:04:05-07:00",
        "updated_at": "2006-01-02T15:04:05-07:00",
        "deleted_at": "2006-01-02T15:04:05-07:00",
        "uid": "12345678-1234-1234-1234-123456789012",
        "resource_version": "a23av"
      },
      "name": "my-openai-connection",
      "spec": {
        "connection_type": "OPENAI",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "auth_data": {
          "kind": "PlaintextProvider",
          "data": "string"
        }
      },
      "status": {
        "phase": "READY",
        "detail": "Lookup failed: ai.openai.com"
      }
    }

### List connections¶

List the connections in your environment by sending a GET request to the [Connections endpoint](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/listSqlv1Connections).

  * This request uses your Cloud API key instead of the Flink API key.

Listing the connections in your environment requires the following inputs:

    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"

Run the following command to list the connections in your environment.

    curl --request GET \
      --url "https://flink.region.provider.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/connections" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}"

Your output should resemble:

Response from a request to list connections 

    {
      "api_version": "sql/v1",
      "kind": "ConnectionList",
      "metadata": {
        "first": "https://flink.us-west1.aws.confluent.cloud/sql/v1/environments/env-abc123/connections",
        "last": "",
        "prev": "",
        "next": "https://flink.us-west1.aws.confluent.cloud/sql/v1/environments/env-abc123/connections?page_token=UvmDWOB1iwfAIBPj6EYb",
        "total_size": 123,
        "self": "https://flink.us-west1.aws.confluent.cloud/sql/v1/environments/env-123/connections"
      },
      "data": [
        {
          "api_version": "sql/v1",
          "kind": "Connection",
          "metadata": {
            "self": "https://flink.us-west1.aws.confluent.cloud/sql/v1/organizations/org-abc/environments/env-123/connections/my-openai-connection",
            "resource_name": "",
            "created_at": "2006-01-02T15:04:05-07:00",
            "updated_at": "2006-01-02T15:04:05-07:00",
            "deleted_at": "2006-01-02T15:04:05-07:00",
            "uid": "12345678-1234-1234-1234-123456789012",
            "resource_version": "a23av"
          },
          "name": "my-openai-connection",
          "spec": {
            "connection_type": "OPENAI",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "auth_data": {
              "kind": "PlaintextProvider",
              "data": "string"
            }
         }
       },
       "status": {
         "phase": "READY",
         "detail": "Lookup failed: ai.openai.com"
          }
        }
      ]
    }

Update a connection

Update a connection in your environment by sending a PATCH request to the [Connections endpoint](/cloud/current/api.html#tag/Connections-\(sqlv1\)/operation/updateSqlv1Connection).

  * This request uses your Cloud API key instead of the Flink API key.

Updating a connection requires the following inputs:

    export CONNECTION_NAME="<connection-name>" # example: "my-openai-connection"
    export CONNECTION_TYPE="<connection-type>" # example: "OPENAI"
    export ENDPOINT="<endpoint>" # example: "https://api.openai.com/v1/chat/completions"
    export CLOUD_API_KEY="<cloud-api-key>"
    export CLOUD_API_SECRET="<cloud-api-secret>"
    export BASE64_CLOUD_KEY_AND_SECRET=$(echo -n "${CLOUD_API_KEY}:${CLOUD_API_SECRET}" | base64 -w 0)
    export ORG_ID="<organization-id>" # example: "b0b21724-4586-4a07-b787-d0bb5aacbf87"
    export ENV_ID="<environment-id>" # example: "env-a1b2c3"
    export CLOUD_PROVIDER="<cloud-provider>" # example: "aws"
    export CLOUD_REGION="<cloud-region>" # example: "us-east-1"
    export JSON_DATA="<payload-string>"

The following JSON shows an example payload. The `auth_data` key varies by service.

    {
      "name": "${CONNECTION_NAME}",
      "spec": {
        "connection_type": "${CONNECTION_TYPE}",
        "endpoint": "${ENDPOINT}",
        "auth_data": {
          "kind": "PlaintextProvider",
          "data": "string"
        }
      },
      "metadata": {}
    }

Quotation mark characters in the JSON string must be escaped, so the payload string to send resembles the following:

    export JSON_DATA="{
      \"name\": \"${CONNECTION_NAME}\",
      \"spec\": {
        \"connection_type\": \"${CONNECTION_TYPE}\",
        \"endpoint\": \"${ENDPOINT}\",
        \"auth_data\": {
          \"kind\": \"PlaintextProvider\",
          \"data\": \"string\"
        }
      },
      \"metadata\": {}
    }"

The following command sends a PUT request to update a connection.

    curl --request PUT \
      --url "https://flink.region.provider.confluent.cloud/sql/v1/organizations/${ORG_ID}/environments/${ENV_ID}/connections/${CONNECTION_NAME}" \
      --header "Authorization: Basic ${BASE64_CLOUD_KEY_AND_SECRET}" \
      --header 'content-type: application/json' \
      --data "${JSON_DATA}"

Your output should resemble:

Response from a request to update a connection 

    {
      "api_version": "sql/v1",
      "kind": "Connection",
      "metadata": {
        "self": "https://flink.us-west1.aws.confluent.cloud/sql/v1/organizations/org-abc/environments/env-a1b2c3/connections/my-openai-connection",
        "resource_name": "",
        "created_at": "2006-01-02T15:04:05-07:00",
        "updated_at": "2006-01-02T15:04:05-07:00",
        "deleted_at": "2006-01-02T15:04:05-07:00",
        "uid": "12345678-1234-1234-1234-123456789012",
        "resource_version": "a23av"
      },
      "name": "my-openai-connection",
      "spec": {
        "connection_type": "OPENAI",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "auth_data": {
          "kind": "PlaintextProvider",
          "data": "string"
        }
      },
      "status": {
        "phase": "READY",
        "detail": "Lookup failed: ai.openai.com"
         }
       }
    }

## Related content¶

  * [Cloud Console](../get-started/quick-start-cloud-console.html#flink-sql-quick-start-run-sql-statement)
  * [Confluent CLI](../reference/flink-sql-cli.html#flink-sql-confluent-cli)
  * [SQL shell](../get-started/quick-start-shell.html#flink-sql-quick-start-shell)
  * [Confluent Terraform Provider](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs)

Note

This website includes content developed at the [Apache Software Foundation](https://www.apache.org/) under the terms of the [Apache License v2](https://www.apache.org/licenses/LICENSE-2.0.html).
