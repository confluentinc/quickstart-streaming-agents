---
document_id: flink_installation_authentication_chunk_1
source_file: flink_installation_authentication.md
source_url: https://docs.confluent.io/platform/current/flink/installation/authentication.html
title: Configure Authentication for Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Configure Authentication for Confluent Manager for Apache Flink¶

By default, Confluent Manager for Apache Flink® (CMF) installs with authentication disabled. CMF supports [mutual TLS (mTLS) authentication](../../security/authentication/mutual-tls/overview.html#tls-authentication) and [OAuth authentication](../../security/authentication/oauth-oidc/overview.html#oauth-oidc-authentication-overview) only.

## mTLS authentication¶

mTLS provides two-way authentication to ensure that traffic between clients and the CMF node is secure, and that content from both directions can be trusted. For a review of mTLS and RBAC terminology, see [Terminology](../../kafka/configure-mds/mutual-tls-auth-rbac.html#mtls-rbac-terminolgy-review).

## Example¶

The following configuration file shows how to provision Confluent Manager for Apache Flink with a keystore and truststore to specify mTLS for all communication. It also shows how to configure a mounted volume to store certificates. You pass the configuration file to Helm when you install CMF.

    # mtls-values.yaml
      cmf:
        ssl:
          keystore: /store/my-keystore
          keystore-password: #Optional in case the key store is password protected
          trust-store: /store/my-trust-store
          trust-store-password: #Optional in case the trust store is password protected
          client-auth: need # require clients with valid certificate
        authentication:
          type: mtls
          config:
            auth.ssl.principal.mapping.rules: #Optional to extract a specific principal from the certificate https://docs.confluent.io/platform/current/security/authentication/mutual-tls/tls-principal-mapping.html
      # Example to mount the certificate stores into your installation
      mountedVolumes:
        volumes:
          - name: certificates
            azureFile:
              secretName: azure-secret
              shareName: aksshare
              readOnly: true
        volumeMounts:
          - name: certificates
            mountPath: /store

When you make the `helm install` call, use the `-f` flag to pass the YAML file with the security information like the following:

    helm upgrade --install cmf confluentinc/confluent-manager-for-apache-flink \
    -f mtls-values.yaml

## OAuth authentication¶

Note

OAuth is available starting with Confluent Platform version 7.9, but only with REST APIs. It is NOT available with the Confluent CLI or the Confluent for Kubernetes operator.

Starting with Confluent Platform version 7.9, the CMF server can be configured for Open Authentication (OAuth) to secure its services.

## Example¶

The following configuration file shows how to provision Confluent Manager for Apache Flink with OAuth authentication.

    # oauth-values.yaml
     cmf:
     authentication:
         type: oauth
         config:
             oauthbearer.jwks.endpoint.url: <jwks-endpoint-url>
             token.issuer: Confluent
             oauthbearer.expected.issuer: <idp-issuer-url>
             oauthbearer.sub.claim.name: <sub-claim-name>
             oauthbearer.groups.claim.name: <groups-claim-name>
             oauthbearer.expected.audience: <audience>
             public.key.path: /path/to/metadata-public-key
             confluent.metadata.bootstrap.server.urls: <mds-url>:<mds-port>
             confluent.metadata.http.auth.credentials.provider: OAUTHBEARER
             confluent.metadata.oauthbearer.token.endpoint.url: <idp-token-url>
             confluent.metadata.oauthbearer.login.client.id: <client-id-for-cmf>
             confluent.metadata.oauthbearer.login.client.secret: <client-secret-for-cmf>
