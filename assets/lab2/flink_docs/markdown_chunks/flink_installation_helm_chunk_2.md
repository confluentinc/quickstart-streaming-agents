---
document_id: flink_installation_helm_chunk_2
source_file: flink_installation_helm.md
source_url: https://docs.confluent.io/platform/current/flink/installation/helm.html
title: How to Install Confluent Manager for Apache Flink with Helm
chunk_index: 2
total_chunks: 3
---

\ confluentinc/flink-kubernetes-operator \ --set watchNamespaces="{namespace1,namespace2,...}"

## Step 3: Deploy CMF from the Confluent Helm repository¶

Next you will install CMF using the Confluent-provided Helm chart. This Helm chart is the only supported way to install and update CMF. Out-of-band updates to the resources that the Helm chart creates are not supported.

Warning

If you do not specify a license, CMF will generate a trial license.

  1. (Optional) Store your Confluent license in a Kubernetes secret.

         kubectl create secret generic <license-secret-name> --from-file=license.txt

  2. (Optional) Create a CMF database encryption key into a Kubernetes secret

CMF is storing sensitive data such as secrets in its internal database. Below instructions are for setting up the encryption key for the CMF database. CMF has a `cmf.sql.production` property. When the property is set to `false`, encryption is disabled. Otherwise, an encryption key is required.

         # Generate a 256-bit key (recommended for production)
         openssl rand -out cmf.key 32
         # Create a Kubernetes secret with the encryption key
         kubectl create secret generic <secret-name> \
           --from-file=<property-name>=cmf.key
           -n <your-cmf-namespace>

During the CMF installation, pass the following Helm parameter to use the encryption key:

         --set encryption.key.kubernetesSecretName=<secret-name> \
         --set encryption.key.kubernetesSecretProperty=<property-name>

**Example**

         openssl rand -out cmf.key 32
         kubectl create secret generic cmf-encryption-key \
           --from-file=encryption-key=cmf.key \
           -n confluent
         helm upgrade --install cmf --version "~2.0.0" \
                 confluentinc/confluent-manager-for-apache-flink \
                 --namespace confluent \
                 --set encryption.key.kubernetesSecretName=cmf-encryption-key \
                 --set encryption.key.kubernetesSecretProperty=encryption-key

Warning

You must backup the encryption key, CMF does not keep a backup of it. If the key is lost, you will no longer be able to access the encrypted data stored in the database.

  3. Install CMF using the default configuration:

For deployment on OpenShift, you must also pass `--set podSecurity.securityContext.fsGroup=null --set podSecurity.securityContext.runAsUser=null` to below Helm command.

         helm upgrade --install cmf --version "~2.0.0" \
           confluentinc/confluent-manager-for-apache-flink \
           --namespace <namespace> \
           --set license.secretRef=<license-secret-name> \
           --set cmf.sql.production=false # or pass --set encryption.key.kubernetesSecretName ...

Note

CMF will create a `PersistentVolumeClaim` (PVC) in Kubernetes. If the PVC remains in status `Pending`, check your Kubernetes cluster configuration and make sure a Container Storage Interface (CSI) driver is installed and configured correctly. Alternatively, if you want to run CMF without persistent storage, you can disable the PVC by setting the `persistence.create` property to `false`. Note that in this case, a restart of the CMF pod will lead to a data loss.

  4. Configure the Chart. Helm provides [several options](https://helm.sh/docs/intro/using_helm/#customizing-the-chart-before-installing) for setting and overriding values in a chart. For CMF, you should customize the chart by passing a values file with the `--values` flag.

First, use Helm to show the default `values.yaml` file for CMF.

         helm inspect values confluentinc/confluent-manager-for-apache-flink --version "~2.0.0"

You should see output similar to the following:

         ## Image pull secret
         imagePullSecretRef:

         ## confluent-manager-for-apache-flink image
         image:
         repository: confluentinc
         name: cp-cmf
         pullPolicy: IfNotPresent
         tag: 1.0.1

         ## CMF Pod Resources
         resources:
         limits:
            cpu: 2
            memory: 1024Mi
         requests:
            cpu: 1
            memory: 1024Mi

         ## Load license either from K8s secret
         license:
         ##
         ## The license secret reference name is injected through
         ## CONFLUENT_LICENSE environment variable.
         ## The expected key: license.txt. license.txt contains raw license data.
         ## Example:
            ##   secretRef: confluent-license-for-cmf
         secretRef: ""

         ## Pod Security Context
         podSecurity:
         enabled: true
         securityContext:
            fsGroup: 1001
            runAsUser: 1001
            runAsNonRoot: true

         ## Persistence for CMF
         persistence:
         # if set to false, the database will be on the pod ephemeral storage, e.g. gone when the pod stops
