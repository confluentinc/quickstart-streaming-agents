---
document_id: flink_reference_example-data_chunk_2
source_file: flink_reference_example-data.md
source_url: https://docs.confluent.io/cloud/current/flink/reference/example-data.html
title: Example Data Streams in Confluent Cloud for Apache Flink
chunk_index: 2
total_chunks: 3
---

long-running statement when you’re done.

## Marketplace database¶

The `marketplace` database provides streams that simulate commerce-related data. The `marketplace` database has these tables:

  * clicks: simulates a stream of user clicks on a web page.
  * customers: simulates a stream of customers who order products.
  * orders: simulates a stream of orders.
  * products: simulates a stream of products that a customer has ordered.

### clicks table¶

To access the `clicks` example stream, use the fully qualified string, `examples.marketplace.clicks` in your queries.

The `clicks` table has the following schema:

    CREATE TABLE clicks (
      click_id STRING, -- UUID
      user_id INT, -- range between 3000 and 5000
      url STRING, -- regex https://www[.]acme[.]com/product/[a-z]{5}
      user_agent STRING, -- set by the datafaker Internet class
      view_time INT -- range between 10 and 120
     );

The `user_agent` field is assigned by the [datafaker Internet class](https://javadoc.io/doc/net.datafaker/datafaker/latest/net.datafaker/net/datafaker/providers/base/Internet.html).

Run the following statement to inspect the `clicks` data stream:

    SELECT * FROM examples.marketplace.clicks;

Your output should resemble:

    click_id                             user_id url                                user_agent                                                           view_time
    23add2ce-da47-47c1-925a-f7c1def06f0c 3278    https://www.acme.com/product/mqwpg Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like … 11
    b81dc020-5ad2-493f-8175-d3e50e40f411 4919    https://www.acme.com/product/vycnj Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)… 58
    b62ae975-0f5d-4e87-9cbe-45b7661ad327 3461    https://www.acme.com/product/pghkm Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML… 105
    ...

### customers table¶

To access the `customers` example stream, use the fully qualified string, `examples.marketplace.customers` in your queries.

The `customers` table has the following schema:

    CREATE TABLE customers (
      customer_id INT, -- range between 3000 and 3250
      name STRING, -- set by the datafaker Name class
      address STRING, -- set by the datafaker Address class
      postcode STRING, -- set by the datafaker Address class
      city STRING, -- set by the datafaker Address class
      email STRING, -- set by the datafaker Internet class
      PRIMARY KEY (customer_id) NOT ENFORCED
     );

  * The `name` field is assigned by the [datafaker Name class](https://javadoc.io/static/net.datafaker/datafaker/2.1.0/net.datafaker/net/datafaker/providers/base/Name.html)
  * The address fields are assigned by the [datafaker Address class](https://javadoc.io/static/net.datafaker/datafaker/2.1.0/net.datafaker/net/datafaker/providers/base/Address.html).
  * The `email` field is assigned by the [datafaker Internet class](https://javadoc.io/doc/net.datafaker/datafaker/latest/net.datafaker/net/datafaker/providers/base/Internet.html).

Run the following statement to inspect the `customers` data stream:

    SELECT * FROM examples.marketplace.customers;

Your output should resemble:

    customer_id name                 address                postcode city               email
    3023        Ellsworth Price      0644 Mara Drive        29407    Emilyhaven         sheldon.sipes@gmail.com
    3003        Jayme Buckridge      320 Schumm Green       38752    Schowalterchester  johnsie.hane@yahoo.com
    3010        Les Beier            7032 Gerda Road        66841    Deckowside         minnie.becker@hotmail.com
    ...

### orders table¶

To access the `orders` example stream, use the fully qualified string, `examples.marketplace.orders` in your queries.

The `customer_id` and `product_id` are suitable for joins with the `customers` and `products` streams.

    CREATE TABLE orders (
      order_id STRING, -- UUID
      customer_id INT, -- range between 3000 and 3250
      product_id INT, -- range between 1000 and 1500
      price DOUBLE -- range between 0.00 and 100.00
    );

Run the following statement to inspect the `orders` data stream:

    SELECT * FROM examples.marketplace.orders;

Your output should resemble:

    order_id                             customer_id product_id price
    36d77b21-e68f-4123-b87a-cc19ac1f36ac 3137        1305       65.71
    7fd3cd2a-392b-4f8f-b953-0bfa1d331354 3063        1327       17.75
    1a223c61-38a5-4b8c-8465-2a6b359bf05e 3064        1166       14.95
    ...

Run the following statement to join the `orders` data stream with the `customers` and `products` streams. The query shows the name of the customer, and the product name, and the price of the order.

    SELECT
      examples.marketplace.customers.name AS customer_name,
      examples.marketplace.products.name AS product_name,
      examples.marketplace.orders.price
    FROM examples.marketplace.products
    JOIN examples.marketplace.orders ON examples.marketplace.products.product_id = examples.marketplace.orders.product_id
    JOIN examples.marketplace.customers ON examples.marketplace.customers.customer_id = examples.marketplace.orders.customer_id;
