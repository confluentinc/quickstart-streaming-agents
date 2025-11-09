---
document_id: flink_installation_encryption_chunk_2
source_file: flink_installation_encryption.md
source_url: https://docs.confluent.io/platform/current/flink/installation/encryption.html
title: Data Encryption in Confluent Manager for Apache Flink
chunk_index: 2
total_chunks: 2
---

--set encryption.key.kubernetesSecretProperty=encryption-key \ --namespace <your-cmf-namespace>

## Configuration Examples¶

### Production Deployment¶

    # values.yaml
    encryption:
      key:
        kubernetesSecretName: "cmf-encryption-key"
        kubernetesSecretProperty: "encryption-key"
    cmf:
      sql:
        production: true

### Development/Testing Deployment¶

    # values.yaml
    cmf:
      sql:
        production: false  # Disables encryption

Note

In the production disabled mode, even when you provide the `encryption.key.kubernetesSecretName` and `encryption.key.kubernetesSecretProperty`, it is not used.

When you setup CMF with production mode disabled, you will see a warning like this:

    Confluent Manager for Apache Flink® provides a management solution for Apache Flink clusters using Confluent Platform.
    It includes various templates and configurations to deploy and manage Flink applications.Thank you for installing confluent-manager-for-apache-flink!
    ##################################################################################
    #                              !!! WARNING !!!                                  #
    #                        NON-PRODUCTION DEPLOYMENT                              #
    ##################################################################################
    This is a NON-PRODUCTION deployment of Confluent Manager for Apache Flink®.
    This deployment is NOT suitable for production use. If 'cmf.sql.production' is set
    to 'false' sensitive data like secrets in the database are not encrypted.
    To deploy in production mode, set cmf.sql.production=true in your values.yaml and
    create an encryption key, according to the documentation.
    Note: A CMF database that has been initialized as a non-production mode deployment can not be
    turned into a production mode later on.
    #################################################################################

You are not allowed to switch between productions mode, i.e you cannot have the same CMF instance started with `cmf.sql.production: true` and move to `cmf.sql.production: false` or vice versa.

Warning

Key Rotation is Not Supported

Once you set an encryption key, you cannot change it. The same key must be used for the entire lifetime of your CMF database.
