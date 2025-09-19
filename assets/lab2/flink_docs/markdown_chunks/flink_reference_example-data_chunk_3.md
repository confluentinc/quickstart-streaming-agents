---
document_id: flink_reference_example-data_chunk_3
source_file: flink_reference_example-data.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/example-data.html
title: Example Data Streams in Confluent Cloud for Apache Flink
chunk_index: 3
total_chunks: 3
---

Your output should resemble:

    customer_name       product_name              price
    Mr. Lexie Collins   Fantastic Rubber Car      32.76
    Lyle Spencer        Synergistic Leather Clock 21.28
    Mrs. Candida Howe   Lightweight Silk Hat      35.38
    Colette Ebert       Sleek Steel Keyboard      92.22

### products table¶

To access the `products` example stream, use the fully qualified string, `examples.marketplace.products` in your queries.

    CREATE TABLE products (
      product_id INT, -- range between 1000 and 1500
      name STRING, -- set by the datafaker Commerce class
      brand STRING, -- set by the datafaker Commerce class
      vendor STRING, -- set by the datafaker Commerce class
      department STRING, -- set by the datafaker Commerce class
      PRIMARY KEY (product_id) NOT ENFORCED
     );

The product fields are assigned by the [datafaker Commerce class](https://javadoc.io/static/net.datafaker/datafaker/2.1.0/net.datafaker/net/datafaker/providers/base/Commerce.html).

Run the following statement to inspect the `products` data stream:

    SELECT * FROM examples.marketplace.products;

Your output should resemble:

    product_id name                        brand   vendor         department
    1440       Enormous Aluminum Keyboard  LG      Dollar General Garden & Movies
    1404       Practical Plastic Computer  Adidas  Target         Outdoors
    1132       Gorgeous Paper Watch        Samsung Amazon         Home, Kids & Movies
    ...
