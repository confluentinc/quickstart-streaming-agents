---
source_url: https://docs.confluent.io/platform/current/flink/installation/helm.html
title: How to Install Confluent Manager for Apache Flink with Helm
hierarchy: ['platform', 'installation', 'helm.html']
scraped_date: 2025-09-05T13:51:26.133802
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
         create: true
         dataVolumeCapacity: 10Gi
         ##  storageClassName: # Without the storage class, the default storage class is used.

         ## Volumes to mount for the CMF pod.
         ##
         ## Example with a PVC.
         ## mountedVolumes:
         ##   volumes:
         ##   - name: custom-volume
         ##     persistentVolumeClaim:
         ##       claimName: pvc-test
         ##   volumeMounts:
         ##   - name: custom-volume
         ##     mountPath: /mnt/<path_of_your_choice>
         ##
         mountedVolumes:
         volumes:
         volumeMounts:

         ## Configure the CMF service for example Authn/Authz
         cmf:
         #  authentication:
         #    type: mtls

         ## Enable Kubernetes RBAC
         # When set to true, it will create a proper role/rolebinding or cluster/clusterrolebinding based on namespaced field.
         # If a user doesn't have permission to create role/rolebinding then they can disable rbac field and
         # create required resources out of band to be used by the Operator. In this case, follow the
         # templates/clusterrole.yaml and templates/clusterrolebiding.yaml to create proper required resources.
         rbac: true
         ## Creates a default service account for the CMF pod if service.account.create is set to true.
         # In order to use a custom service account, set the name field to the desired service account name and set create to false.
         # Also note that the new service account must have the necessary permissions to run the CMF pod, i.e cluster wide permissions.
         # The custom service account must have:
         #
         # rules:
         #  - apiGroups: ["flink.apache.org"]
         #    resources: ["flinkdeployments", "flinkdeployments/status"] # Needed to manage FlinkDeployments CRs
         #    verbs: ["*"]
         #  - apiGroups: [""]
         #    resources: ["services"] # Read-only permissions needed for the flink UI
         #    verbs: ["get", "list", "watch"]
         serviceAccount:
         create: true
         name: ""
         # The jvmArgs parameter allows you to specify custom Java Virtual Machine (JVM) arguments that will be passed to the application container.
         # This can be useful for tuning memory settings, garbage collection, and other JVM-specific options.
         # Example :
         # jvmArgs: "-Xms512m -Xmx1024m -XX:+UseG1GC"

Note the following about CMF default values:

     * CMF uses SQLite to store metadata about your deployments. The data is persisted on a persistent volume that is created during the installation via a `PersistentVolumeClaim` created by Helm.

     * The persistent volume is created with your Kubernetes cluster’s default storage class. Depending on your storage class, your metadata might not be retained if you uninstall CMF. For example, if your reclaim policy is `Delete`, data is not retained. **Make sure to backup the data in the persistent volume regularly**.

     * If you want to set your storage class, you can overwrite `persistence.storageClassName` during the installation.

     * By default, the chart uses the image hosted by [Confluent on DockerHub](https://hub.docker.com/r/confluentinc/cp-cmf). To specify your own registry, set the following configuration values:

           image:
             repository: <image-registry>
             name: cp-cmf
             pullPolicy: IfNotPresent
             tag: <tag>

     * By default, the chart creates a cluster role and [service account](https://kubernetes.io/docs/concepts/security/service-accounts/) that CMF can use to create and monitor Flink applications in all namespaces. If you want to keep your service account, you set the `serviceAccount.name` property during installation to the preferred service account.

     * To change the log level, for example to show debug logs, set `cmf.logging.level.root=debug`.

## Step 4: Cleanup¶

For cleanup instructions, see the [cleanup section in the quickstart guide](../get-started/get-started-application.html#cpf-get-started-cleanup).
