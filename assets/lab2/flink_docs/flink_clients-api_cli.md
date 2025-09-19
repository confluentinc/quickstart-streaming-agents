---
source_url: https://docs.confluent.io/platform/current/flink/clients-api/cli.html
title: CLI Operations for Confluent Manager for Apache Flink
hierarchy: ['platform', 'clients-api', 'cli.html']
scraped_date: 2025-09-05T13:52:39.647088
---

# CLI Operations for Confluent Manager for Apache Flink¶

Manage Flink environments and applications in Confluent Manager for Apache Flink® (CMF) by using Flink commands provided by the Confluent CLI.

Important

You must be using Confluent CLI version 4.7.0 or later to use these commands. Confluent Platform 7.8.0 provides this version of the Confluent CLI. For more information, see [Confluent CLI](../../installation/versions-interoperability.html#confluent-cli-cp-compatibility).

You can use the Confluent CLI to manage the following CMF resources:

  * [Environments](../configure/environments.html#cmf-environments)
  * [Applications](../jobs/applications/overview.html#cmf-applications)

## Configure the CLI¶

To use the Confluent CLI to manage Flink Applications and Environments, the CLI needs to be connected to the CMF server. There are two ways of configuring the CLI.

  * Setting an environment variable
  * Using a `--url` flag when you make a call

Note

You can only access the Flink on-premises commands when you are logged out of Confluent Cloud or any other Confluent login.

To set the environment variable, specify the URL globally like the following:

    export CONFLUENT_CMF_URL=<URL-of-CMF-server>

Or each time you invoke the CLI, like the following:

    confluent flink environment list --url <cmf-url>

The following authentication and authorization parameters are available:

  * Client Key path
  * Client Certificate path
  * Certificate Authority path

You can set them globally like the following:

    export CONFLUENT_CMF_CLIENT_KEY_PATH=<path/to/client/key/file>
    export CONFLUENT_CMF_CLIENT_CERT_PATH=<path/to/client/cert/file>
    export CONFLUENT_CMF_CERTIFICATE_AUTHORITY_PATH=<path/to/certificate/authority/file>

Or pass them as flags each time you invoke the CLI.

    confluent flink environment list --url <cmf-url> --client-key-path <path/to/client/key/file>
    confluent flink environment list --url <cmf-url> --client-cert-path <path/to/client/cert/file>
    confluent flink environment list --url <cmf-url> --certificate-authority-path <path/to/certificate/authority/file>

## View available commands¶

You can see all of the commands available by using the `--help` option. To view the commands, you must be logged out of Confluent Cloud or any other Confluent resource. For example:

    flink environment --help
    flink application --help

You can also see a list of the available options on the [/confluent-cli/current/](/confluent-cli/current/). Make sure to choose the **On-Premises** tab.

## Manage Environments¶

Using the Confluent CLI, you can perform these actions:

  * Create a new environment
  * Update an existing environment
  * Describe an environment
  * Delete an environment
  * List all available environments

### Create a new environment¶

In CMF, one Flink environment is attached to one Kubernetes namespace. To learn more about environments, see [Environments](../configure/environments.html#cmf-environments).

There are two ways of specifying Flink application defaults in an environment. You can pass a JSON string, or pass a path to a JSON or YAML file.

For example, to pass a JSON string, use the following command:

    confluent flink environment create <environment-name> --kubernetes-namespace <k8s-namespace> --defaults <json-defaults-string>

Example:

    confluent flink environment create dev-environment --kubernetes-namespace devops --defaults "{\"metadata\":{\"annotations\":{\"prometheus.io/scrape\":\"true\"},\"labels\":{\"billing/origin\":\"sales-team-apac\"}},\"spec\":{\"flinkConfiguration\":{\"taskmanager.numberOfTaskSlots\":\"4\"}}}"

To pass a path to a JSON or YAML file, use the following command:

    confluent flink environment create <environment-name> --kubernetes-namespace <k8s-namespace> --defaults <path/to/file>

Example:

    confluent flink environment create dev-environment --kubernetes-namespace devops --defaults ~/input/flink/environment/create-success-with-defaults.json

Example JSON input `(create-success-with-defaults.json` in the previous example):

    {
        "metadata": {
            "annotations": {
                "prometheus.io/scrape": "true"
            },
            "labels": {
                "billing/origin": "sales-team-apac"
            }
        },
        "spec": {
            "flinkConfiguration": {
                "taskmanager.numberOfTaskSlots": "4"
            }
        }
    }

Note that the JSON specified is the JSON for the `flinkApplicationDefaults` key and not the environment JSON.

Your output should resemble:

    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    || Name                 || dev-environment                                                                                                                                                                |
    || Kubernetes Namespace || devops                                                                                                                                                                         |
    || Created Time         || 2024-11-08 06:28:00.251622876                                                                                                                                                  |
    ||                      || +0000 UTC                                                                                                                                                                      |
    || Updated Time         || 2024-11-08 06:28:00.251623376                                                                                                                                                  |
    ||                      || +0000 UTC                                                                                                                                                                      |
    || Application Defaults || {"metadata":{"annotations":{"prometheus.io/scrape":"true"},"labels":{"billing/origin":"sales-team-apac"}},"spec":{"flinkConfiguration":{"taskmanager.numberOfTaskSlots":"4"}}} |
    +-----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

### Update an existing environment¶

You can update the defaults for Flink application in Flink environment similar to how you create an environment.

Important

You cannot update the Kubernetes namespace for an existing environment. Also, if use the `update` command with no defaults, you will erase of the existing defaults.

To update an environment, you can either pass a JSON string or pass the path to a JSON or YAML file.

To pass a JSON string, use the following command.

    confluent flink environment update <environment-name> --defaults <json-defaults-string>

For example:

    confluent flink environment update dev-environment --defaults "{\"metadata\":{\"labels\":{\"billing/origin\":\"sales-team-emea\"}}}"

Or to pass the path to a JSON or YAML file, use the following command.

    confluent flink environment update <environment-name> --defaults <path/to/json/file>

For example:

    confluent flink environment update dev-environment--defaults ~/input/flink/environment/create-success-with-defaults.json

A JSON file passed to this command might look like the following:

    {
        "metadata": {
            "labels": {
                "billing/origin": "sales-team-emea"
            }
        }
    }

Your output should resemble the following, regardless of whether you pass a string or a file path:

    +-----------------------+---------------------------------------------------------------+
    || Name                 || dev-environment                                              |
    || Kubernetes Namespace || devops                                                       |
    || Created Time         || 2024-11-05 11:01:52.497 +0000                                |
    ||                      || UTC                                                          |
    || Updated Time         || 2024-11-05 11:32:30.458160877                                |
    ||                      || +0000 UTC                                                    |
    || Application Defaults || {"metadata":{"labels":{"billing/origin":"sales-team-emea"}}} |
    +-----------------------+---------------------------------------------------------------+

    confluent flink environment update dev-environment

Your output should resemble:

    +----------------------------+--------------------------------+
    | Name                       | dev-environment                |
    | Kubernetes Namespace       | devops                         |
    | Created Time               | 2024-11-05 11:01:52.497 +0000  |
    |                            | UTC                            |
    | Updated Time               | 2024-11-05 11:34:36.823979088  |
    |                            | +0000 UTC                      |
    | Flink Application Defaults | null                           |
    +----------------------------+--------------------------------+

### Describe an environment¶

Use the following command to get details of an existing Flink environment:

    confluent flink environment describe <environment-name>

Example command

    confluent flink environment describe dev-environment

Your output should resemble:

    +----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Name                       | dev-environment                                                                                                                                                                |
    | Kubernetes Namespace       | devops                                                                                                                                                                         |
    | Created Time               | 2024-11-08 06:28:00.251 +0000                                                                                                                                                  |
    |                            | UTC                                                                                                                                                                            |
    | Updated Time               | 2024-11-08 06:28:00.251 +0000                                                                                                                                                  |
    |                            | UTC                                                                                                                                                                            |
    | Flink Application Defaults | {"metadata":{"annotations":{"prometheus.io/scrape":"true"},"labels":{"billing/origin":"sales-team-apac"}},"spec":{"flinkConfiguration":{"taskmanager.numberOfTaskSlots":"4"}}} |
    +----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

### Delete an existing environment¶

Run the following command to delete an environment

    confluent flink environment delete <environment-name>

The optional `--force` flag skips the confirmation prompt.

    confluent flink environment delete <environment-name> --force

Your output should resemble:

    Deleted Flink environment "<environment-name>".

### List all available environments¶

You can use the following command to list environments:

    confluent flink environment list

Your output should resemble:

    Name           | Kubernetes Namespace |          Created Time          |          Updated Time
    ------------------+----------------------+--------------------------------+---------------------------------
    dev-environment| devops               | 2024-11-05 11:01:52.497 +0000  | 2024-11-05 11:35:13.216 +0000
                   |                      | UTC                            | UTC
    staging        | billing              | 2024-11-05 11:38:46.969 +0000  | 2024-11-05 11:38:46.969 +0000
                   |                      | UTC                            | UTC

The default output format for this command is human-readable. You can get the output in JSON and YAML format too by passing the optional `--output` flag.

## Manage Applications¶

Using the Confluent CLI, you can perform these actions:

  * Create a new application
  * Update an existing application
  * Describe an application
  * Delete an application
  * List all applications in a given environment
  * Access the Flink Web UI for the application

The output format for these commands is either JSON or YAML. Human-readable output is not an option.

### Create a new application¶

Use the following command to create an application in an environment by passing the path to the JSON or YAML file.

    confluent flink application create --environment <environment-name> <path/to/file>

Example command:

    confluent flink application create ~/resources/app_payload.json --environment dev-environment --output json

Example JSON:

    {
    "apiVersion": "cmf.confluent.io/v1",
    "kind": "FlinkApplication",
    "metadata": {
        "name": "basic-example"
    },
    "spec": {
        "image": "confluentinc/cp-flink:1.19.1-cp1",
        "flinkVersion": "v1_19",
        "flinkConfiguration": {
        "taskmanager.numberOfTaskSlots": "1",
        "metrics.reporter.prom.factory.class": "org.apache.flink.metrics.prometheus.PrometheusReporterFactory",
        "metrics.reporter.prom.port": "9249-9250"
        },
        "serviceAccount": "flink",
        "jobManager": {
        "resource": {
            "memory": "1048m",
            "cpu": 1
        }
        },
        "taskManager": {
        "resource": {
            "memory": "1048m",
            "cpu": 1
        }
        },
        "job": {
        "jarURI": "local:///opt/flink/examples/streaming/StateMachineExample.jar",
        "state": "running",
        "parallelism": 3,
        "upgradeMode": "stateless"
        }
    },
    "status": null
    }

Your output should resemble:

    {
    "apiVersion": "cmf.confluent.io/v1",
    "kind": "FlinkApplication",
    "metadata": {
        "name": "basic-example"
    },
    "spec": {
        "image": "confluentinc/cp-flink:1.19.1-cp1",
        "flinkVersion": "v1_19",
        "flinkConfiguration": {
        "taskmanager.numberOfTaskSlots": "1",
        "metrics.reporter.prom.factory.class": "org.apache.flink.metrics.prometheus.PrometheusReporterFactory",
        "metrics.reporter.prom.port": "9249-9250"
        },
        "serviceAccount": "flink",
        "jobManager": {
        "resource": {
            "memory": "1048m",
            "cpu": 1
        }
        },
        "taskManager": {
        "resource": {
            "memory": "1048m",
            "cpu": 1
        }
        },
        "job": {
        "jarURI": "local:///opt/flink/examples/streaming/StateMachineExample.jar",
        "state": "running",
        "parallelism": 3,
        "upgradeMode": "stateless"
        }
    },
    "status": null
    }

### Update an existing application¶

You can update an existing application in an environment by using this command:

    confluent flink application update --environment <environment-name> <path/to/file>

Example command

    confluent flink application update ~/resources/app_payload.json --environment dev-environment --output json

Your output should resemble your output from the create command, but with the specified properties updated.

### Describe an application¶

Use the following command to get details of an existing Flink application.

    confluent flink application describe <application-name> --environment <environment-name>

Example command

    confluent flink application describe basic-example --environment dev-environment

Your output should resemble:

    {
    "apiVersion": "cmf.confluent.io/v1",
    "kind": "FlinkApplication",
    "metadata": {
        "name": "basic-example"
    },
    "spec": {
        "flinkConfiguration": {
        "metrics.reporter.prom.factory.class": "org.apache.flink.metrics.prometheus.PrometheusReporterFactory",
        "metrics.reporter.prom.port": "9249-9250",
        "taskmanager.numberOfTaskSlots": "1"
        },
        "flinkVersion": "v1_19",
        "image": "confluentinc/cp-flink:1.19.1-cp1",
        "job": {
        "jarURI": "local:///opt/flink/examples/streaming/StateMachineExample.jar",
        "parallelism": 3,
        "state": "running",
        "upgradeMode": "stateless"
        },
        ...

### Delete an existing application in an environment¶

Run the following command to delete an application.

    confluent flink environment delete <application-name> --environment <environment-name>

The optional `--force` flag skips the confirmation prompt.

    confluent flink environment delete <application-name> --environment <environment-name> --force

Your output should resemble:

    Deleted flink application "basic-example".

### List all application in a given environment¶

You can use the following command to list all applications in a given environment:

    confluent flink application list --environment <environment-name>

Your output should resemble:

        Name      |   Environment   |     Job Name      | Job Status
    --------------+-----------------+-------------------+-------------
    basic-example | dev-environment | State machine job | RUNNING

### Access the Flink Web UI for the application¶

To access the Flink Web UI for a Flink application in an environment, use the following command:

    confluent flink application web-ui-forward <application-name> --environment <environment-name> --port <port-to-start-web-ui> --url <cmf-url>

Example command:

    confluent flink application web-ui-forward basic-example --environment dev-environment --port 9090 --url http://localhost:8080

Your output should resemble:

    Starting web UI at http://localhost:9090/ ... (Press Ctrl-C to stop)

Keep the session on and access the UI at the URL provided in the output.

Important

There is a known bug in CLI v4.7.0 which requires you to pass the URL to the CMF server explicitly for this command.

## Debugging¶

If you experience issues with the Confluent CLI, you can use the `flag --unsafe-trace` to get more insights into the command that is running. You will notice more output when you use this flag.

If you get a `not found` error response, and you are sure that the specified resource exists, verify that the CMF server is up and running and you have connectivity to the server.

