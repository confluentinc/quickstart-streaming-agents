---
document_id: flink_installation_versions-interoperability_chunk_1
source_file: flink_installation_versions-interoperability.md
source_url: https://docs.confluent.io/platform/current/flink/installation/versions-interoperability.html
title: Version and Interoperability for Confluent Manager for Apache Flink
chunk_index: 1
total_chunks: 1
---

# Versions and Interoperability for Confluent Manager for Apache Flink¶

The following tables list Confluent Platform for Apache Flink® compatibility and requirements.

Confluent Platform | Confluent Manager for Apache Flink® | Apache Flink® | Apache Flink® Kubernetes Operator | Release Date | Standard End of Support | Platinum End of Support
---|---|---|---|---|---|---
8.0.x | 2.0.X | 1.18.x, 1.19.x, 1.20.x | 1.12.x | June 24, 2025 | June 24, 2027 | June 24, 2028
7.9.x | 1.1.x | 1.18.x, 1.19.x, 1.20.x | 1.10.x | February 19, 2025 | February 19, 2027 | February 19, 2028
7.8.x | 1.0.x | 1.18.x, 1.19.x, 1.20.x | 1.10.x | December 2, 2024 | December 2, 2026 | December 2, 2027
7.7.x | N/A | 1.18.x, 1.19.x | 1.8.x | July 26, 2024 | N/A | July 26, 2027 for select customers only

Note the following:

* Standard support means any support level below Platinum support. For example, if you have Gold support, you have Standard support.
* The end of support date applies to minor versions and any maintenance versions that come after the minor version. This means that maintenance versions follow the same lifecycle of the minor version.

Confluent Platform for Apache Flink has the following operational requirements:

Apache Flink® version | Confluent Platform versions | Java versions | Kubernetes version | OpenShift version
---|---|---|---|---
1.20 | 7.8.x - 7.9.x | 11, 17 | 1.26+ | 4.12 and 4.14+
1.19 | 7.7.x - 7.9.x | 11, 17 | 1.26+ | 4.12 and 4.14+
1.18 | 7.7.x - 7.9.x | 11, 17 | 1.26+ | 4.12 and 4.14+
