---
document_id: flink_installation_helm_chunk_1
source_file: flink_installation_helm.md
source_url: https://docs.confluent.io/platform/current/flink/installation/helm.html
title: How to Install Confluent Manager for Apache Flink with Helm
chunk_index: 1
total_chunks: 3
---

# Install Confluent Manager for Apache Flink with Helm¶

This topic walks you through how to install Confluent Manager for Apache Flink (CMF) with Helm.

## Step 1: Confirm prerequisites​¶

  1. Confirm you have adequate hardware.

The underlying processor architecture of your Kubernetes worker nodes must be a supported version for the Confluent Platform for Apache Flink version you plan to deploy.

Currently, Confluent Platform for Apache Flink supports x86 and ARM64 hardware architecture.

Component | Nodes | Storage | Memory | CPU
---|---|---|---|---
Confluent Manager for Apache Flink | 1 | 10 GB (persistent storage as PVC) [1] | 1 GB RAM [1] | 2 [1]
Flink Kubernetes Operator [2] | 1 | N/A | 3 GB RAM | 2
[1]| _(1, 2, 3)_ Storage, memory and CPU values are configurable through the Helm installation.
---|---
[2]| These resource requirements are calculated to support the execution of 200 Flink applications.
---|---

  2. Install the required tools.

This installation guide assumes you have already installed Helm. CMF supports Helm 3 for installation. You should have already configured Helm using the Helm documentation. To verify that your environment is prepared, the following commands should complete without error:

         kubectl get pods
         helm list

Add the Confluent Platform for Apache Flink Helm repository.

         helm repo add confluentinc https://packages.confluent.io/helm
         helm repo update

## Step 2: Install the Confluent Platform for Apache Flink Kubernetes operator¶

You must install the Confluent Platform for Apache Flink Kubernetes operator _before_ you install CMF because CMF uses the operator to manage the Flink clusters.

  1. Install the certificate manager.

         kubectl create -f https://github.com/jetstack/cert-manager/releases/download/v1.18.2/cert-manager.yaml

  2. Install the Flink Kubernetes operator.

Use the `watchNamespaces` configuration to prepare the Kubernetes namespaces you want to deploy Flink applications to. You can later upgrade the Flink Kubernetes operator to extend the list, by re-running below Helm command again, with the additional namespaces. Note that you need to manually restart the Flink Kubernetes operator after changing the `watchNamespaces` configuration, for example by deleting the operator pod. It will be automatically recreated. You must ensure that the Kubernetes operator watches the Kubernetes namespaces you want to deploy Flink applications to with CMF.

Instead of using Helm, you can also manually prepare a Kubernetes namespace for deploying Flink clusters, by creating the necessary `flink` service account, role and role binding, as documented in the Flink Kubernetes operator [documentation](https://nightlies.apache.org/flink/flink-kubernetes-operator-docs-release-1.12/docs/operations/rbac/#cluster-scoped-flink-operator-with-jobs-running-in-other-namespaces). If you omit the `watchNamespaces` flag, the operator will watch all namespaces, but the necessary `flink` service account will only by created in the namespace where the operator is installed. Additional namespaces must be setup manually.

For deployment on OpenShift, you must also pass `--set podSecurityContext.runAsUser=null --set podSecurityContext.runAsGroup=null` to below Helm command.

         helm upgrade --install cp-flink-kubernetes-operator --version "~1.120.0" \
           confluentinc/flink-kubernetes-operator \
           --set watchNamespaces="{namespace1,namespace2,...}"
