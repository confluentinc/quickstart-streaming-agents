---
document_id: flink_jobs_configure_security_chunk_1
source_file: flink_jobs_configure_security.md
source_url: https://docs.confluent.io/platform/current/flink/jobs/configure/security.html
title: How to Secure a Flink Job with Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# How to Secure a Flink Job with Confluent Manager for Apache Flink¶

The following sections provide an overview of security risks and available security controls for Flink jobs deployed with Confluent Manager for Apache Flink® (CMF).

## Risks¶

Apache Flink® is a framework for executing user code. As such, users that have permission to deploy Flink jobs have the ability to execute arbitrary code. It is therefore critical that you set up authentication/authorization and limit networked access. Unconfigured Flink clusters should **never** be deployed in an Internet-facing environment.

## TLS/SSL for authentication and encryption¶

Flink supports TLS/SSL for authentication and encryption of network traffic between Flink processes, both for internal connectivity and external connectivity.

You should follow the [SSL guidelines](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/deployment/security/security-ssl/) in the Flink documentation.

Internal connectivity in Flink includes control messages between Flink processes and the data connections between TaskManagers. All internal connections can be configured to use TLS/SSL for authentication and encryption, which is in the [SSL guidelines](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/deployment/security/security-ssl/). When configured, the connections use mutual authentication, meaning both server and client side of each connection need to present the certificate to each other. The certificate acts effectively as a shared secret when a dedicated CA is used to exclusively sign an internal certificate. The certificate for internal communication is not needed by any other party to interact with Flink, and can be simply added to the container images.

External connectivity in Flink happens with HTTP/REST endpoints. For example, these endpoints are used by the web UI and the Flink CLI. These endpoints can be configured to require TLS/SSL connections. The server will, however, accept connections from any client by default, meaning the REST endpoint does not authenticate the client. Simple mutual authentication may be enabled by configuration (as outlined in the Flink documentation mentioned previously) if authentication of connections to the REST endpoints is required. However, Confluent recommends you deploy a “side car proxy” meaning you bind the REST endpoint to the loopback interface (or the pod-local interface in Kubernetes) and start a REST proxy that authenticates and forwards the requests to Flink. Examples for proxies that Flink users have deployed are Envoy Proxy or NGINX with MOD_AUTH.

## Kubernetes-level security controls¶

CMF supports Flink deployments via Flink’s Kubernetes operator. You have tight control over who can deploy Flink applications with the security controls available in Kubernetes.

You should not provide direct access to the Kubernetes resources managed by the Flink Kubernetes operator using Kubernetes RBAC. All access should go through CMF to comply with the [authentication](../../installation/authentication.html#cmf-authenticate) and [authorization](../../installation/authorization.html#cmf-authorize) requirements.

The Flink Kubernetes operator installs two custom roles: `flink-operator` and `flink`. `flink-operator` is used to manage FlinkDeployment resources, meaning it creates and manages the JobManager deployment for each Flink job (and related resources). The `flink` role is used by the `jobManager` process of each job to create and manage the `taskManager` and `configMap` resources.

The standalone Kubernetes deployment mode is recommended when running untrusted code inside the Flink cluster, as there is no requirement for the Flink pod service account to have permissions to launch additional pods.

When you install CMF, you create the roles to create and manage FlinkDeployment resources on Kubernetes.
