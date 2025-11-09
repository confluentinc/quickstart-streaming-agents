---
document_id: flink_installation_upgrade-cmf_chunk_1
source_file: flink_installation_upgrade-cmf.md
source_url: https://docs.confluent.io/platform/current/flink/installation/upgrade-cmf.html
title: Upgrade Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Upgrade Confluent Manager for Apache Flink¶

Use these instructions to upgrade earlier versions of Confluent Manager for Apache Flink® (CMF) to a later version. To install CMF, see [Install Confluent Manager for Apache Flink with Helm](helm.html#install-cmf-helm).

Follow these steps to upgrade CMF:

  1. Scale down CMF to zero (0) pods and wait for the pod to be deleted. The following command shows an example of how to scale down CMF:

         kubectl scale deployment confluent-manager-for-apache-flink --replicas=0 -n <namespace>
         kubectl wait --for=delete pod -l app=confluent-manager-for-apache-flink --timeout=60s -n <namespace>

  2. Uninstall the existing Flink Kubernetes Operator:

         helm uninstall cp-flink-kubernetes-operator -n <namespace>

  3. Ensure certificate manager is installed, or use the following command to install it:

         kubectl create -f https://github.com/jetstack/cert-manager/releases/download/v1.18.2/cert-manager.yaml
         kubectl wait --for=condition=Available deployment -n cert-manager cert-manager-webhook --timeout=180s

  4. Find the version Confluent Platform for Apache Flink Kubernetes operator you want to install. For a list of available versions, see the [Versions and Interoperability for Confluent Manager for Apache Flink](versions-interoperability.html#cmf-interop).

         helm repo add confluentinc https://packages.confluent.io/helm
         helm repo update confluentinc
         helm upgrade --install --version "<desired_version>" cp-flink-kubernetes-operator confluentinc/flink-kubernetes-operator

  5. Upgrade CMF to the desired version using the Helm command:

         helm upgrade --install cmf charts/confluent-manager-for-apache-flink/ --namespace <namespace> ...

Important

If the CMF database is file system based, using `helm uninstall cmf` will lead to the loss of the database because the Persistent Volume Claim (PVC) is managed by CMF.
