---
document_id: flink_installation_helm_chunk_3
source_file: flink_installation_helm.md
source_url: https://docs.confluent.io/platform/current/flink/installation/helm.html
title: How to Install Confluent Manager for Apache Flink with Helm
chunk_index: 3
total_chunks: 3
---

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
