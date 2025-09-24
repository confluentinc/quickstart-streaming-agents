# Lab1: Tool Calling Agent Walkthrough

![Architecture Diagram](./assets/arch.png)

In this lab, we'll use Confluent Cloud's Apache Flink tool calling feature to look up products in real-time orders. The LLM, through tool calling, uses a Zapier MCP server to retrieve competitor prices, and if a competitor offers a better price, the agent automatically applies a price match.

## Prerequisites

- ⚠️ **IMPORTANT: For AWS Users: [Request access to Claude Sonnet 3.7 in Bedrock for your cloud region](https://console.aws.amazon.com/bedrock/home#/modelaccess)**. If you do not activate it, you will get ModelRuntime errors in Flink and the LLM calls in this lab will not work. ⚠️ 
- Core infrastructure deployed via `python setup.py` or manually with Terraform (see [main README](./README.md))
- Zapier account and remote MCP server setup (instructions below)

## Zapier MCP Server Setup

Create a Zapier MCP server for tool calling:

### 1. Create Zapier Account

Sign up at [zapier.com](https://zapier.com/sign-up) and verify your email.

### 2. Create MCP Server

Visit [mcp.zapier.com](https://mcp.zapier.com/mcp/servers), choose "Other" as MCP Client, and create your server.

![Create MCP Server](./assets/lab1/zapier/3.png)

### 3. Add Tools

Add these tools to your MCP server:

- **Webhooks by Zapier: GET** tool
- **Gmail: Send Email** tool (authenticate via SSO)

![Add Tools](./assets/lab1/zapier/4.png)

### 4. Get SSE Endpoint URL

Click **"Connect",** choose **"Other"** for your client, then change transport to **"SSE Endpoint"**, and **copy the URL.** This is the `ZAPIER_SSE_ENDPOINT` you will need to enter when deploying the lab with `python setup.py` or manually with Terraform.

![SSE Endpoint](./assets/lab1/zapier/7.png)

## Lab Architecture

This lab implements a three-agent pipeline:

1. **Agent 1: URL Scraping Agent** - Enriches orders with product names and scrapes competitor websites
2. **Agent 2: Price Extractor Agent** - Extracts competitor prices from scraped page content
3. **Agent 3: Price Match Notification Agent** - Sends email notifications for price matches

## Getting Started

### Connecting to Flink

Confluent Cloud Flink Compute Pool is a managed environment that provides the resources needed to run Apache Flink jobs directly within Confluent Cloud. It eliminates the need for self-managed Flink clusters by offering a scalable, serverless compute layer for stream processing and real-time analytics on data in Confluent topics.

In [Flink UI](https://confluent.cloud/go/flink), choose the Environment.

You will see a compute pool created for you. Click on **Open SQL Workspace**

![Flink UI](./assets/lab1/flinkworkspace.png)

### Setting up the MCP connection and model

Open `mcp_commands.txt` from the `[aws|azure]/lab1-tool-calling/` directory, and run the customized `confluent flink connection create` command in the Confluent CLI, then run the Flink SQL `CREATE MODEL zapier_mcp_model...` command in the Flink SQL Workspace.

`mcp_commands.txt` is generated automatically by Terraform when deploying Lab1, and its commands are custom tailored to your environment, so that they run right out of the box.

### Test the LLM models before continuing

Run the following queries:

#### Test Query 1: Base LLM functioning

```sql
SELECT 
  question,
  response
FROM (SELECT 'What is the capital of France?' as question) t,
LATERAL TABLE(ML_PREDICT('llm_textgen_model', question, MAP['debug', true])) as r(response);
```

#### Test Query 2: LLM Tool Calling

```sql
SELECT 
    AI_TOOL_INVOKE('zapier_mcp_model', 
                   'Use the gmail_send_email tool to send an email. Instructions: send an email address to yourself, subject "Direct Query Test", body "This email was sent directly from Confluent Cloud!"', 
                   MAP[],
                   MAP['gmail_send_email', 'Create and send a new email message']) as response;
```

### Data Generation

Navigate to your lab's data-gen directory:

**AWS:**

```bash
cd aws/lab1-tool-calling/data-gen/
```

**Azure:**

```bash
cd azure/lab1-tool-calling/data-gen/
```

#### Unix/Mac Instructions

Download the ShadowTraffic license file and run the data generator:

```bash
curl -O https://raw.githubusercontent.com/ShadowTraffic/shadowtraffic-examples/master/free-trial-license-docker.env
chmod +x run.sh && ./run.sh
```

#### Windows Instructions

Download the ShadowTraffic license file and run the data generator:

```cmd
curl -O https://raw.githubusercontent.com/ShadowTraffic/shadowtraffic-examples/master/free-trial-license-docker.env
run.bat
```

#### What Data is Generated

The data generator creates three interconnected data streams:

- **Customers**: 100 customer records with realistic names, emails, addresses, and state information
- **Products**: 17 product records including electronics, games, sports equipment, and household items with prices ranging from $5-$365
- **Orders**: Continuous stream of orders linking customers to products with timestamps

🎉 **Data is now flowing through your streaming pipeline! The agents will process this data in real-time.**

### Agent 1: URL Scraping Agent

First, we need to enrich incoming Orders with product names, then search for and scrape these products from competitors' websites. We'll achieve this using Flink's Tool Calling feature, which will enable Flink to invoke the Zapier MCP server we previously created.

Run this in Flink Workspace UI to start the first agent:

```sql
-- Get recent orders, scrape competitor website for same product
SET 'sql.state-ttl' = '1 HOURS';
CREATE TABLE recent_orders_scraped AS
SELECT
    o.order_id,
    p.product_name,
    c.customer_email,
    o.price as order_price,
    (AI_TOOL_INVOKE(
        'zapier_mcp_model',
        CONCAT('Use the webhooks_by_zapier_get tool to extract page contents. ',
               'Instructions: Extract the page contents from the following URL: ',
               'https://www.walmart.com/search?q="',
               p.product_name, '"'),
        MAP[],
        MAP['webhooks_by_zapier_get', 'Fire off a single GET request with optional querystrings.'],
        MAP['debug', 'true', 'on_error', 'continue']
    ))['webhooks_by_zapier_get']['response'] as page_content
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id;
```

### Agent 2: Price Extractor Agent

Start **Agent 2** to extract the competitor's price from `page_content` and output it as a new field: `extracted_price`.

```sql
-- Extract prices from scraped webpages using AI_COMPLETE
CREATE TABLE streaming_competitor_prices AS
SELECT
    ros.order_id,
    ros.product_name,
    ros.customer_email,
    ros.order_price,
    llm.response as extracted_price
FROM recent_orders_scraped ros
CROSS JOIN LATERAL TABLE(
    AI_COMPLETE('llm_textgen_model',
        CONCAT('Analyze this search results page for the following product name: "', ros.product_name,
               '", and extract the price of the product that most closely matches the product name. ',
               'Return only the price in format: XX.XX. For example, return only: 29.95. ',
               'Page content: ', ros.page_content)
    )
) AS llm
WHERE ros.page_content IS NOT NULL
  AND ros.page_content NOT LIKE 'MCP error%'
  AND ros.page_content <> '';
```

In a new cell, check the output of `streaming_competitor_prices`

```sql
SELECT * FROM streaming_competitor_prices;
```

![Agent 2 Output Screenshot](./assets/lab1/agent2-flinkoutput.png)

Notice the new field `extracted_price`. This will be used by the next Agent.

### Agent 3: Price Match Notification Agent

In this step, we'll notify the customer when a price match has been applied.
We'll again use Confluent Cloud's tool-calling feature — this time connecting to the Zapier MCP server to trigger an email or message to the customer. For this agent, the tool is `gmail_send_email`.

Start Agent 3 by running:

```sql
-- Create and send professional email notifications for price matches
CREATE TABLE price_match_email_results AS
SELECT
    scp.order_id,
    scp.customer_email,
    scp.product_name,
    CAST(CAST(scp.order_price AS DECIMAL(10, 2)) AS STRING) as order_price,
    CAST(CAST(scp.competitor_price AS DECIMAL(10, 2)) AS STRING) as competitor_price,
    CAST(CAST((scp.order_price - scp.competitor_price) AS DECIMAL(10, 2)) AS STRING) as savings,
    AI_TOOL_INVOKE('zapier_mcp_model',
                   CONCAT('Use the gmail_send_email tool to send an email. ',
                          'Instructions: send yourself an email to your own email address, ',
                          'subject "✅ Great News! Price Match Applied - Order #', scp.order_id, '", ',
                          'body "Subject: Your Price Match Has Been Applied - Order #', scp.order_id, '

Dear Valued Customer,

We have great news! We found a better price for your recent purchase and have automatically applied a price match.

📦 ORDER DETAILS:
   • Order Number: #', scp.order_id, '
   • Product: ', scp.product_name, '

💰 PRICE MATCH DETAILS:
   • Original Price: $', CAST(CAST(scp.order_price AS DECIMAL(10, 2)) AS STRING), '
   • Competitor Price Found: $', CAST(CAST(scp.competitor_price AS DECIMAL(10, 2)) AS STRING), '
   • Your Savings: $', CAST(CAST((scp.order_price - scp.competitor_price) AS DECIMAL(10, 2)) AS STRING), '

✅ ACTION TAKEN:
We have processed a price match refund of $', CAST(CAST((scp.order_price - scp.competitor_price) AS DECIMAL(10, 2)) AS STRING),
' back to your original payment method. You should see this credit within 3-5 business days.

🛒 WHY WE DO THIS:
We are committed to offering you the best prices. Our automated price matching system continuously monitors competitor prices to ensure you always get the best deal.

Thank you for choosing River Retail. We appreciate your business!

Best regards,
River Retail Customer Success Team
📧 support@riverretail.com | 📞 1-800-RIVER-HELP

---
This is an automated message from our price matching system."'),
                   MAP[],
                   MAP['gmail_send_email', 'Create and send a new email message'],
                   MAP['debug', 'true', 'on_error', 'continue']) as email_response
FROM (
    SELECT *,
           TRY_CAST(extracted_price AS DECIMAL(10,2)) as competitor_price
    FROM streaming_competitor_prices
) scp
WHERE scp.competitor_price IS NOT NULL
  AND scp.competitor_price > 0
  AND scp.order_price > scp.competitor_price;
```

With Agent 3 running, our real-time price matching pipeline is complete—orders stream in, competitor prices are fetched and analyzed, and customers are instantly notified when they get the best deal.

Check out your email for price matched orders

![Price matched emails](./assets/lab1/email.png)

## Conclusion

By chaining these agents together, we've built a real-time data pipeline that reacts to market changes in seconds, ensures pricing competitiveness, and delivers immediate value to customers—right in their inbox.

## Navigation

- **← Back to Overview**: [Main README](./README.md)
- **→ Next Lab**: [Lab2: Vector Search RAG](./LAB2-Walkthrough.md)
- **🧹 Cleanup**: [Cleanup Instructions](./README.md#cleanup)
