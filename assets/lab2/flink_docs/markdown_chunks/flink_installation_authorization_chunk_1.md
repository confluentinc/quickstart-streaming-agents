---
document_id: flink_installation_authorization_chunk_1
source_file: flink_installation_authorization.md
source_url: https://docs.confluent.io/platform/current/flink/installation/authorization.html
title: Configure Authorization for Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Configure Authorization for Confluent Manager for Apache Flink¶

Authorization for Confluent Manager for Apache Flink relies on Confluent Platform `role-based access control (RBAC) <rbac-overview>` through the Confluent Metadata Service (MDS). Authorization assumes authentication is already enabled. Confluent Manager for Apache Flink communicates with the MDS to validate whether the principal of the incoming request is allowed to perform a specific action. Confluent Manager for Apache Flink supports all available RBAC [authentication options](../../security/authorization/rbac/overview.html#rbac-authentication-options).

The following image illustrates the authentication and authorization process for Confluent Manager for Apache Flink.

[](../../_images/cmf-security.png)

## Confluent Manager for Apache Flink service principal¶

Confluent Manager for Apache Flink requires its own service principal to authorize user principals.

All the three following roles have sufficient privileges for the CMF service principal, however, you should choose the role with the least privileges to meet your needs, to interact with CMF. For a full list of RBAC roles, see [Use Predefined RBAC Roles in Confluent Platform](../../security/authorization/rbac/rbac-predefined-roles.html#rbac-predefined-roles).

  * SystemAdmin
  * UserAdmin
  * SecurityAdmin

Before enabling the authorization feature for Confluent Manager for Apache Flink you must assign the cluster identifiers for CMF. For more information on the cluster identifiers, see [Cluster identifiers](../configure/access-control.html#af-ac-cluster-id).

    confluent iam rbac role-binding create \
      --principal User:<user-name> \
      --role UserAdmin #example \
      --cmf CMF-id

## Role binding¶

You also need to create a role binding for every environment you create, including the name of the environment. The following example code shows how you might do that.

    confluent iam rbac role-binding create \
      --principal User:<user-name> \
      --role UserAdmin #example \
      --cmf CMF-id \
      --flink-environment <flink-environment-name>

## Configure Confluent Manager for Apache Flink for RBAC¶

Confluent Manager for Apache Flink supports all available RBAC authentication options to authenticate with the Confluent Platform metadata service. The following examples cover some authentication methods for the metadata service.

### OAuth example¶

The following YAML file shows how you might configure CMF with OAuth.

    # authorization-values.yaml
     cmf:
       authorization:
         mdsRestConfig:
           endpoint: #Mandatory: replace with the endpoint for the Metadata Service
           authentication:
             type: oauth
             config:
               confluent.metadata.http.auth.credentials.provider: OAUTHBEARER
               confluent.metadata.oauthbearer.token.endpoint.url: #URL of your configured IDP used to store the users
               confluent.metadata.oauthbearer.login.client.id: #Client id for the user talking to MDS, needs to be a user that can request permissions for all users
               confluent.metadata.oauthbearer.login.client.secret: #Client secret for the user talking to MDS

When you make the `helm install` call, use the `-f` flag to pass the YAML file with the security information like the following:

    helm upgrade --install cmf confluent/confluent-manager-for-apache-flink \
      -f oauth-values.yaml \
      -f authorization-values.yaml

### mTLS example¶

The following example shows how you configure mTLS for CMF.

    # authorization-values.yaml
    cmf:
      authorization:
        mdsRestConfig:
          endpoint: #Mandatory: replace with the endpoint for the Metadata Service
          authentication:
            type: mtls
            config:
              confluent.metadata.ssl.truststore.location: #truststore path containing certificates needed to talk to metadata service
              confluent.metadata.ssl.truststore.password: #optional password if truststore is encrypted
              confluent.metadata.ssl.keystore.location: #keystore path containing keys/certificates needed to talk to metadata service
              confluent.metadata.ssl.keystore.password: #optional password if keystore is encrypted
              confluent.metadata.ssl.key.password:

When you make the `helm install` call, use the `-f` flag to pass the YAML file with the security information like the following:

    helm upgrade --install cmf confluent/confluent-manager-for-apache-flink \
      -f mtls-values.yaml \
      -f authorization-values.yaml
