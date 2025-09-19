---
document_id: flink_installation_encryption_chunk_1
source_file: flink_installation_encryption.md
source_url: https://docs.confluent.io/platform/current/flink/installation/encryption.html
title: Data Encryption in Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 2
---

# Data Encryption in Confluent Manager for Apache Flink¶

Confluent Manager for Apache Flink (CMF) automatically encrypts Secrets stored in the database.

## What Gets Encrypted¶

CMF encrypts the following sensitive data:

  * **Secret data** : The `data` field provided in the [Secrets](link_to_secrets_api_or_objects_here) is stored encrypted. In the current setup, these secrets are primarily used for storing the connection config for Kafka & Schema Registry Clusters.

## How Encryption Works¶

### Encryption Algorithm¶

CMF uses AES-GCM (Galois/Counter Mode) encryption with the following strict requirements:

  * **Algorithm** : AES (Advanced Encryption Standard) with GCM mode
  * **Key Length** : Must be exactly 128 bits (16 bytes) or 256 bits (32 bytes)

No other algorithms are supported.

### Production Mode (Recommended)¶

When CMF runs in production mode, encryption is automatically enabled and required. You must provide an encryption key in a K8s secret that CMF uses to encrypt and decrypt sensitive data.

### Development Mode (Strictly not recommended)¶

For development and testing, encryption can be disabled. In this mode, sensitive data is stored in plain text and is NOT suitable for production use.

## Setting Up Encryption¶

### Step 1: Generate an AES-GCM Encryption Key of either 128 bits or 256 bits.¶

#### Using OpenSSL (Recommended)¶

    # Generate a 256-bit key (recommended for production)
    > openssl rand -out cmf.key 32
    # Or generate a 128-bit key
    > openssl rand -out cmf.key 16

The key must be exactly 128 bits (16 bytes) or 256 bits (32 bytes) when Base64-decoded. No other key lengths are supported.

### Step 2: Store the Key in Kubernetes¶

Create a Kubernetes Secret in your release namespace to store your encryption key:

    # Replace:
    # 1. secret-name: The name of the K8s secret that you want.
    # 2. property-name: The key inside the K8s secret whose value is the secret
    # 3. your-cmf-namespace: The namespace in which CMF is deployed
    > kubectl create secret generic <secret-name> \
      --from-file=<property-name>=cmf.key  -n <your-cmf-namespace>

For example, the secret `cmf-encryption-key` and the property name `encryption-key` and the release namespace is `confluent`, in that case this command becomes:

    kubectl create secret generic cmf-encryption-key \
      --from-file=encryption-key=cmf.key  -n confluent

CMF expects a base64 encoded encryption key. While using the command `kubectl create secret`, k8s by default base64 encodes the value (the actual encryption key) in this case. So do not provide an already encoded key to the command.

CMF does not create a backup of the encryption key. It is important for the user to back up the key securely somewhere.

You can make sure that the key generated and stored is 16 or 32 bytes long by using this command:

    # Replace: <secret-name>, <property-name>, and <your-cmf-namespace>
    > kubectl get secret <secret-name> -n <your-cmf-namespace> \
      -o jsonpath="{.data.<property-name>}" | base64 --decode | wc -c
    16 or 32

### Step 3: Configure CMF to Use the Key¶

Update your Helm values file (`values.yaml` or any file that you use to provide the values) to tell CMF where to find the encryption key:

    # Enable encryption
    encryption:
      key:
        kubernetesSecretName: "cmf-encryption-key"    # Name of your Kubernetes Secret, i.e <secret-name> in the example command
        kubernetesSecretProperty: "encryption-key"    # Key name within the Secret, i.e <property-name> in the example command
    # Enable production mode (required for encryption)
    cmf:
      sql:
        production: true

### Step 4: Deploy CMF¶

Deploy CMF with your updated configuration:

    helm upgrade --install cmf confluentinc/confluent-manager-for-apache-flink --version "~2.0.0" \
      --values values.yaml \
      --namespace <your-cmf-namespace>

You can also directly pass the config values in the command directly:

    helm upgrade --install cmf confluentinc/confluent-manager-for-apache-flink --version "~2.0.0" \
        --set cmf.sql.production=true \
        --set encryption.key.kubernetesSecretName=cmf-encryption-key \
        --set encryption.key.kubernetesSecretProperty=encryption-key \
        --namespace <your-cmf-namespace>
