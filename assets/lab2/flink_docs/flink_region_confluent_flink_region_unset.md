---
source_url: https://docs.confluent.io/confluent-cli/current/command-reference/flink/region/confluent_flink_region_unset.html
title: confluent flink region unset
hierarchy: ['confluent-cli', 'command-reference', 'region', 'confluent_flink_region_unset.html']
scraped_date: 2025-09-05T13:52:17.823988
---

# confluent flink region unset¶

## Description¶

Unset the current Flink cloud and region that was set with the `use` command.

    confluent flink region unset [flags]

## Global Flags¶

    -h, --help            Show help for this command.
        --unsafe-trace    Equivalent to -vvvv, but also log HTTP requests and responses which might contain plaintext secrets.
    -v, --verbose count   Increase verbosity (-v for warn, -vv for info, -vvv for debug, -vvvv for trace).

## Examples¶

Unset the current Flink region us-west-1 with cloud provider = AWS.

    confluent flink region unset

## See Also¶

  * [confluent flink region](index.html#confluent-flink-region) \- Manage Flink regions.
