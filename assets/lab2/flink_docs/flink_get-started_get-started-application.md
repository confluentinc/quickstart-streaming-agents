---
source_url: https://docs.confluent.io/platform/current/flink/get-started/get-started-application.html
title: Get Started with Confluent Platform for Apache Flink
hierarchy: ['platform', 'get-started', 'get-started-application.html']
scraped_date: 2025-09-05T13:48:07.922650
---

# Get Started with Applications in Confluent Manager for Apache Flink¶

Confluent Platform for Apache Flink® is compatible with open-source Apache Flink®. To submit an application you must use the Helm chart to install the Confluent Manager for Apache Flink (CMF) application and the Flink Kubernetes operator. After you have installed both, you can deploy a Flink job. The next few sections will describe necessary prerequisites and walk you through the steps to install CMF and deploy a Flink job.

For requirement and compatibility details, see [Confluent Platform for Apache Flink](../../installation/versions-interoperability.html#cp-af-compat).

## Prerequisites¶

To use Confluent Platform for Apache Flink, you must meet the following prerequisites:

### Kubernetes¶

Confluent Platform for Apache Flink® is designed for Kubernetes. Therefore, you must have access to a Kubernetes cluster to deploy the Flink Kubernetes operator and individual Flink jobs:

  * A Kubernetes cluster running a supported version. For a list of supported versions, see [Versions and Interoperability for Confluent Manager for Apache Flink](../installation/versions-interoperability.html#cmf-interop).
  * [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) installed, initialized, with the context set. You also must have the `kubeconfig` file configured for your cluster.
  * [Helm 3](https://helm.sh/docs/intro/install/) installed.

To learn more about deploying Flink on Kubernetes, see [Kubernetes deployment](https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/resource-providers/standalone/kubernetes/).

### Confluent CLI¶

If you have not installed Confluent Platform 8.0 you must install the latest version of the Confluent CLI. In either case, make sure to set the `CONFLUENT_HOME` environment variable and add the bin directory to your path. For more information, see [Install the Confluent CLI](/confluent-cli/current/install.html).

Set the `CONFLUENT_HOME` environment variable.

    export CONFLUENT_HOME=<The directory where Confluent is installed>

Add the location of the CLI (the `/bin` directory) to the PATH:

    export PATH=$CONFLUENT_HOME/bin:$PATH

### Durable storage¶

In production, Flink requires durable storage that is readable and writeable from each Flink cluster. Durable storage is used to store consistent snapshots of the state of your Flink jobs (checkpoints and savepoints).

Examples of durable storage include:

  * S3-compatible storage (S3, MinIO)
  * Microsoft Azure Blob Storage
  * Google Cloud Storage

For more information on configuring durable storage, see [Checkpoint Storage](https://nightlies.apache.org/flink/flink-docs-master/docs/ops/state/checkpoints/#checkpoint-storage) in the Flink documentation.

### Supported components¶

Check to make sure that you are using components supported by Confluent Platform for Apache Flink. See, [Confluent Platform for Apache Flink Features and Support](../jobs/applications/supported-features.html#cpflink-vs-oss).

## Step 1: Install Confluent Manager for Apache Flink¶

To install Confluent Manager for Apache Flink, you have to use Helm to add the Confluent repository, install the certificate manager and then install the Flink Kubernetes operator, and finally install CMF.

Warning

This quickstart guide assumes that everything will be installed into the same Kubernetes namespace. In this example it is `default`. You can use a different namespace, as long as it is consistent across all the commands. Please refer to the [Helm installation guide](../installation/helm.html#install-cmf-helm) for more information on how to setup Confluent Platform for Apache Flink in a multi-namespace environment, in a production environment or on OpenShift.

  1. Add the Confluent Platform repository.

         helm repo add confluentinc https://packages.confluent.io/helm
         helm repo update

  2. Install the certificate manager.

         kubectl create -f https://github.com/jetstack/cert-manager/releases/download/v1.18.2/cert-manager.yaml

  3. Install the Flink Kubernetes Operator

         helm upgrade --install --version "~1.120.0" cp-flink-kubernetes-operator confluentinc/flink-kubernetes-operator

  4. Install Confluent Manager for Apache Flink.

         helm upgrade --install cmf --version "~2.0.0" \
         confluentinc/confluent-manager-for-apache-flink \
         --namespace default --set cmf.sql.production=false

Note

The `cmf.sql.production=false` setting initializing the CMF database without encryption. You can not enable encryption later on. A new CMF installation with a new database is required to setup encryption.

  1. Check that everything deployed correctly.

         kubectl get pods

## Step 2: Deploy Flink jobs¶

To deploy Flink jobs, you should open port forwarding to CMF, and create an environment and application. You can then use the Web UI to confirm that your application has been created.

  1. Open port forwarding to CMF.

         kubectl port-forward svc/cmf-service 8080:80

  2. Create an environment using the Confluent CLI. For a list of Confluent CLI commands for Confluent Platform for Apache Flink, see [confluent flink (On-Premises tab)](/confluent-cli/current/command-reference/flink/).

         confluent flink environment create env1 --url http://localhost:8080 --kubernetes-namespace default

  3. Create the JSON application file. Following is an example.

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
            "image": "confluentinc/cp-flink:1.19.1-cp2",
            "job": {
               "jarURI": "local:///opt/flink/examples/streaming/StateMachineExample.jar",
               "parallelism": 3,
               "state": "running",
               "upgradeMode": "stateless"
            },
            "jobManager": {
               "resource": {
               "cpu": 1,
               "memory": "1024m"
               }
            },
            "serviceAccount": "flink",
            "taskManager": {
               "resource": {
               "cpu": 1,
               "memory": "1024m"
               }
            }
         }
         }

  4. Use the application command, passing the `application.json file` to create the application.

         confluent flink application create application.json --environment env1 --url http://localhost:8080

  5. Access the Flink Web UI to confirm you have successfully created the application:

         confluent flink application web-ui-forward basic-example --environment env1 --port 8090 --url http://localhost:8080

## Step 3: Cleanup¶

  1. Delete the Flink Application:

         confluent flink application delete basic-example --environment env1 --url http://localhost:8080

  2. Uninstall the Flink Kubernetes Operator and CMF:

         helm uninstall cp-flink-kubernetes-operator
         helm uninstall cmf
