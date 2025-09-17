---
source_url: https://docs.confluent.io/platform/current/flink/changelog.html
title: What's New for Confluent Platform for Apache Flink
hierarchy: ['platform', 'changelog.html']
scraped_date: 2025-09-05T13:51:19.732540
---

# What’s New¶

This topic contains details about each Confluent Platform for Apache Flink® release.

## July 2025¶

This release introduces new Apache Flink packages:

  * Flink 1.20.2-cp1
  * Flink 1.19.3-cp1

## June 2025¶

This release introduces new Apache Flink packages based on the RHEL UBI 9 image:

  * Flink 1.20.1-cp3
  * Flink 1.19.2-cp3
  * Flink 1.18.1-cp4

## April 2025¶

This release includes the following vulnerability fixes for Flink:

**Flink 1.20.1-cp2**

CVE | CVSS | Upgraded Package  
---|---|---  
CVE-2025-30065 | 10.0 | org.apache.parquet:parquet*:1.15.1  
  
**Flink 1.19.2-cp2**

CVE | CVSS | Upgraded Package  
---|---|---  
CVE-2025-30065 | 10.0 | org.apache.parquet:parquet*:1.15.1  
  
**Flink 1.18.1-cp3**

CVE | CVSS | Upgraded Package  
---|---|---  
CVE-2025-30065 | 10.0 | org.apache.parquet:parquet*:1.15.1  
  
## March 2025¶

Confluent Platform 7.9 release adds support for OAuth authentication for CMF REST APIs.

Note

OAuth is available starting with Confluent Platform version 7.9, but only with REST APIs. It is NOT available with the Confluent CLI or the Confluent for Kubernetes operator.

The new Flink patch versions are now officially available.

**Flink 1.20.1-cp1**

**Flink 1.19.2-cp1**

## February 2025 - 1.0.3¶

Confluent Manager for Apache Flink® version 1.0.3 is now available with Confluent Platform 7.8 as a regular maintenance release addressing a number of small issues and updating dependencies.

This release does not include new features.

### Fixed issues¶

The following issues were fixed in this release.

  * Improved validation and error messages of FlinkApplication payloads on the REST API
  * Removed unneeded Netty 3.10.6 dependency with vulnerabilities

## February 2025 - 1.0.2¶

Confluent Manager for Apache Flink® version 1.0.3 is now available with Confluent Platform 7.8 as a regular maintenance release addressing a number of small issues and updating dependencies.

This release does not include new features.

### Fixed issues¶

The following issues were fixed in this release.

  * The Helm chart included a default `imagePullSecretRef`, which is not set anymore by default.
  * YAML payloads were not properly supported by Confluent Manager for Apache Flink®.

This release includes the following vulnerability fixes for Confluent Manager for Apache Flink®.

**Confluent Manager for Apache Flink® 1.0.2**

  * Updated Spring Boot to version 3.3.8.

CVE | CVSS | Upgraded Package  
---|---|---  
CVE-2024-52046 |  | Upgraded org.apache.mina:mina-core.  
  
## December 2024¶

Confluent Platform 7.8 release introduces Confluent Manager for Apache Flink® version 1.0.1 and adds support for Confluent Platform for Apache Flink version 1.20. This release moves Confluent Platform for Apache Flink from limited availability to general availability.

Flink versions 1.18 and 1.19 continue to be supported.

This release also includes the following vulnerability fixes for Flink:

**Flink 1.19.1-cp2**

CVE | CVSS | Upgraded Package  
---|---|---  
CVE-2021-21409 | 5.9 | org.wildfly.openssl==1.0.10.Final  
CVE-2019-14887 | 9.1 | org.apache.pekko:pekko-actor_2.12==1.1.2  
  
**Flink 1.18.1-cp2**

CVE | CVSS | Upgraded Package  
---|---|---  
CVE-2021-21409 | 5.9 | org.wildfly.openssl==1.0.10.Final  
CVE-2019-14887 | 9.1 | org.apache.pekko:pekko-actor_2.12==1.1.2  
  
## July 2024¶

Confluent Platform 7.7 release introduces Confluent Platform for Apache Flink in limited availability with support for Flink versions 1.18 and 1.19.
