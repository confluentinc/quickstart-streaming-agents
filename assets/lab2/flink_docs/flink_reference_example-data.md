---
source_url: https://docs.confluent.io/cloud/current/flink/reference/example-data.html
title: Example Data Streams in Confluent Cloud for Apache Flink
hierarchy: ['reference', 'example-data.html']
scraped_date: 2025-09-05T13:47:15.567086
---

# Example Data Streams in Confluent Cloud for Apache Flink¶

Confluent Cloud for Apache Flink® provides an Examples catalog that has mock data streams you can use for experimenting with Flink SQL queries.

* The `examples` catalog is available in all environments.
* All example tables have `$rowtime` available as a system column. The `SOURCE_WATERMARK()` strategy for example tables is different than the `SOURCE_WATERMARK()` strategy Kafka-based tables. For the example tables, the `SOURCE_WATAERMARK()` corresponds to the maximum timestamp seen to this point.
* You can use example data in Flink workspaces, Flink shell, Terraform, and all other clients.
* Example data is read-only, so you can’t use INSERT INTO/ALTER/DROP/CREATE statements on these tables, the database, or the catalog.
* SHOW statements work for the database, catalog, and tables.
* SHOW CREATE TABLE works for the example tables.

## Publish to a Kafka topic¶

You can publish any of the example streams to a Kafka topic by creating a Flink table and populating it with the [INSERT INTO FROM SELECT](queries/insert-into-from-select.html#flink-sql-insert-into-from-select-statement) statement. Confluent Cloud for Apache Flink creates a Kafka topic automatically for the table.

  1. Run the following statements to create and populate a `customers_source` table with the `examples.marketplace.customers` stream.

         CREATE TABLE customers_source (
           customer_id INT,
           name STRING,
           address STRING,
           postcode STRING,
           city STRING,
           email STRING,
           PRIMARY KEY (customer_id) NOT ENFORCED
         );

         INSERT INTO customers_source(
           customer_id,
           name,
           address,
           postcode,
           city,
           email
         )
         SELECT * FROM examples.marketplace.customers;

  2. Run the following statement to inspect the `customers_source` table:

         SELECT * FROM customers_source;

Your output should resemble:

         customer_id name                  address                postcode city               email
         3172        Roseanna Bode         6744 Kacy Bypass       22635    Margarettborough   rico.zboncak@yahoo.com
         3055        Josiah Morissette PhD 61799 Friesen Islands  14194    North Abbybury     thomas.dach@gmail.com
         3177        Buddy Hill            6836 Graham Street     72767    South Earnest      enoch.turcotte@hotmail.com
         ...

  3. Navigate to the [Environments](https://confluent.cloud/environments) page, and in the navigation menu, click **Data portal**.

  4. In the **Data portal** page, click the dropdown menu and select the environment for your workspace.

  5. In the **Recently created** section, find your **customers_source** topic and click it to open the details pane.

  6. Click **View all messages** to open the **Message viewer** on the `customers_source` topic.

  7. Observe the example data from the `examples.marketplace.customers` flowing into the Kafka topic.

Important

The INSERT INTO statement runs continuously until you stop it manually. Free resources in your compute pool by deleting the long-running statement when you’re done.

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
