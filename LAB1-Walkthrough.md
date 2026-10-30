# Lab 1: Price Matching Orders with MCP Tool Calling

Build a price-matching pipeline in Confluent Cloud for Apache Flink. Flink joins orders with customer and product data, then runs an agent that fetches competitor prices and emails your configured test address when it finds a lower price. The demo does not process refunds.

![Architecture Diagram](./assets/lab1/lab1-architecture.png)

> [!TIP]
> **Already deployed Lab 1?** Skip to [Getting Started](#getting-started). If its data generator is already running, do not start another copy.

## Prerequisites

### Payment method or promo code

Confluent Cloud requires a payment method or promo code before Terraform can create a cluster. Free credits are applied first.

1. Open **[Billing & payment](https://confluent.cloud/settings/billing/payment)** and select **Payment details and contacts**.
2. Add a credit card or bank account, or scroll to **Promos**, choose **+ Promo code**, and apply the code from your workshop host.

<img src="./assets/lab1/billing-promo-code.png" alt="Billing and payment: add a promo code" width="500">

### Local dependencies

**macOS:**

```bash
brew install uv git python && brew tap hashicorp/tap && brew install hashicorp/tap/terraform && brew install --cask confluent-cli
```

**Windows:**

```powershell
winget install astral-sh.uv Git.Git Hashicorp.Terraform ConfluentInc.Confluent-CLI Python.Python
```

### Models and MCP access

- **Default models:** `uv run deploy` uses Confluent-hosted inference (Claude Sonnet 4.6 on AWS, GPT-5.4 mini on Azure). No separate cloud account or LLM API key is needed.
- **Optional model credentials:** Use `uv run deploy --bedrock` or `uv run deploy --azure-openai` to use your own model credentials. See the [Workshop Mode Setup Guide](./assets/pre-setup/Workshop-Mode-Setup.md); `uv run api-keys create` can generate workshop credentials.
- **Remote MCP server:** Choose **Confluent-hosted remote MCP server (Recommended)** and enter the token from your presenter. Confluent staff can see `go/mcp-keys` or `#help-tmm`. [Zapier](./assets/pre-setup/Zapier-Setup.md) is an alternative backend.

> [!NOTE]
> **Bedrock only:** Complete the Anthropic use-case form for Claude Sonnet 4.5 in the [AWS Model Catalog](https://console.aws.amazon.com/bedrock/home#/model-catalog). Open the model in the Playground and send a test message to display the form.

## Deploy the Demo

If needed, clone the repository:

```bash
git clone https://github.com/confluentinc/quickstart-streaming-agents.git
cd quickstart-streaming-agents
```

Run the deployer and select **Lab 1: Price matching**:

```bash
uv run deploy
```

Use your Confluent Cloud login, accept generated API keys, and select the recommended MCP backend. For SSO, first run `confluent login --no-browser`. Native hosted models skip the AWS/Azure model-key prompts.

Enter an email address you can check during the workshop. Deployment fills it into both SQL prompts below. If asked to start data generation in the background, choose **n**; step 2 starts it manually. Allow about ten minutes for deployment.

## Getting Started

### Workspace setup

Open the [SQL Workspace](https://confluent.cloud/environments/env-2kz1g1/flink) and select the **environment/catalog**, **Kafka cluster/database**, and **compute pool** shown in your deployment summary. Deployment updates this link for your environment. If you copied it from another attendee, open [Flink](https://confluent.cloud/go/flink) and select your own resources.

Confirm `customers`, `products`, and `orders` appear in the catalog. Run each SQL block in its own cell. Keep `SET` and its following query together when shown in the same block.

**Already created a table, tool, or agent?** Inspect the existing object and statement before rerunning `CREATE`. Resume a stopped writer instead of starting a second copy. Do not drop the Terraform-managed input tables.

## 1. Test the LLM models before continuing

#### Test Query 1: Base LLM model

Run this bounded query and confirm a nonempty response appears. Stop the reader if it remains open.

```sql
SELECT
  question,
  response
FROM (SELECT 'How was the state of Colorado founded?' as question) t,
LATERAL TABLE(ML_PREDICT('llm_textgen_model', question, MAP['debug', 'true'])) as r(response);
```

#### Test Query 2: LLM Tool Calling Model

This test sends one email to your configured workshop address. Confirm the `send_email` result reports success, then check your inbox and spam folder. A successful tool response does not independently confirm inbox receipt.

> [!NOTE]
> Deployment fills in your notification address. If you still see `<<YOUR-EMAIL-ADDRESS-HERE>>`, replace it without adding extra quotes or brackets. The synthetic `customer_email` values in the input are not the notification recipients.

```sql
SELECT
      AI_TOOL_INVOKE(
          'remote_mcp_model',
          'Use the send_email tool to send an email. 
           The "to" parameter must be a single string value: bheintz+test@confluent.io
           The "subject" parameter is: Direct Query Test
           The "body" parameter is: This email was sent directly from Confluent Cloud!
           Important: pass the to address as a string, not an array.',
          MAP[],
          MAP['send_email', 'Send an email via Gmail SMTP'],
          MAP['debug', 'true']
      ) as response;
```

## 2. Generate Data

If the generator is not already running, start it in your terminal:

```bash
uv run lab1_datagen --local
```

Leave the terminal open and continue. The replay publishes 50 `customers`, 17 `products` priced from $5 to $365, and 10 `orders` at two-minute intervals, then exits. The full replay takes about 20 minutes, and you can inspect partial results as they arrive.

> [!IMPORTANT]
> Starting this command again purges the three input topics and reuses the same record IDs. It does not clear existing Flink join state or downstream results. Do not restart it while the price-match job is active; doing so can repeat evaluations and emails. See [Restarting safely](#restarting-safely).

## 3. Create `enriched_orders` table for the agent to use

Join orders with customer and product details. The one-hour state TTL bounds retained join state; the one-time customer/product snapshot supports this workshop replay, not indefinite new-order processing.

```sql
SET 'sql.state-ttl' = '1 HOURS';

CREATE TABLE enriched_orders AS
SELECT
    o.order_id,
    p.product_name,
    c.customer_email,
    o.price AS order_price
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id;
```

**Leave this writer running.** A `CREATE TABLE ... AS SELECT` statement continues to populate its output table as records arrive.

## 4. Run `CREATE TOOL` and `CREATE AGENT`

Register the MCP tool. It exposes only `http_get` and `send_email`; no payment or refund tool is available.

```sql
CREATE TOOL lab1_remote_mcp
USING CONNECTION `remote-mcp-connection`
WITH (
  'type' = 'mcp',
  'allowed_tools' = 'http_get, send_email',
  'request_timeout' = '30'
);
```

Create the agent with its comparison rules and output format. See the [tool-calling guide](https://docs.confluent.io/cloud/current/ai/builtin-functions/invoke-tool-ai-workflow.html) for the underlying feature.

```sql
CREATE AGENT price_match_agent
USING MODEL remote_mcp_model
USING PROMPT 'You are a price matching assistant that performs the following steps:

1. SCRAPE COMPETITOR PRICE: Use the http_get tool to extract page contents from the competitor URL provided in the prompt.

2. EXTRACT PRICE: Analyze the scraped page content to find the product that most closely matches the product name. Extract only the price in format: XX.XX (for example: 29.95). If you cannot find a valid price, stop here.

3. COMPARE AND NOTIFY: Compare the extracted competitor price with our order price. If the competitor price is lower than our price, use the send_email tool to send a price match notification email. Use the exact format provided in the prompt for the email subject and body.

Return your results in this exact format, as plain text with no markdown, bold, or emoji:

Competitor Price:
[price as XX.XX, or "Not found"]

Decision:
[PRICE_MATCH or NO_MATCH]

Summary:
[One sentence describing what you found and what action you took]'
USING TOOLS lab1_remote_mcp
COMMENT 'Consolidated agent for scraping competitor prices and sending price match notifications'
WITH (
  'max_consecutive_failures' = '2',
  'MAX_ITERATIONS' = '10'
);
```

## 5. Run the Agent

This writer reads `enriched_orders`, supplies the product and order price to `AI_RUN_AGENT`, and parses the result into `price_match_results`. The short email template describes the simulated price match without claiming a refund.

Keep the `EMAIL RECIPIENT:` address as plain text inside the prompt. Deployment fills it in for you.

```sql
CREATE TABLE price_match_results AS
SELECT
    pmi.order_id,
    pmi.product_name,
    pmi.customer_email,
    CAST(CAST(pmi.order_price AS DECIMAL(10, 2)) AS STRING) as order_price,
    agent_result.status as agent_status,
    TRIM(REGEXP_EXTRACT(CAST(agent_result.response AS STRING), '\*{0,2}Competitor Price:\*{0,2}\s*\**([\s\S]+?)\**\s*(?=\n\*{0,2}(?:Decision|Summary):|$)', 1)) AS competitor_price,
    TRIM(REGEXP_EXTRACT(CAST(agent_result.response AS STRING), '\*{0,2}Decision:\*{0,2}\s*\**([A-Z_]+)', 1)) AS decision,
    TRIM(REGEXP_EXTRACT(CAST(agent_result.response AS STRING), '\*{0,2}Summary:\*{0,2}\s*\n?([\s\S]+?)$', 1)) AS summary,
    CAST(agent_result.response AS STRING) AS raw_response
FROM enriched_orders pmi,
LATERAL TABLE(
    AI_RUN_AGENT(
        'price_match_agent',
         CONCAT(
          'COMPETITOR URL: http://river-retail-resellers.s3-website-us-east-1.amazonaws.com/',
          '
          PRODUCT NAME: ', pmi.product_name, '
          
          OUR ORDER PRICE: $', CAST(CAST(pmi.order_price AS DECIMAL(10, 2)) AS STRING), '
          
          EMAIL RECIPIENT: bheintz+test@confluent.io
          
          EMAIL SUBJECT: Price match found - Order #', pmi.order_id, '
          
          EMAIL BODY TEMPLATE:
          We found a lower price for your order #', pmi.order_id, '.
          Product: ', pmi.product_name, '
          Our price: $', CAST(CAST(pmi.order_price AS DECIMAL(10, 2)) AS STRING), '
          Competitor price: $[INSERT_COMPETITOR_PRICE]
          Potential savings: $[INSERT_SAVINGS]
          
          This workshop demonstrates a price comparison and notification only.
          No refund or payment adjustment has been processed.'
        ),
        pmi.order_id,
        MAP['debug', 'true']
    )
) as agent_result(status, response);
```

**Leave this writer running until you finish Lab 1.** In a new cell, inspect the decisions:

```sql
SELECT order_id, product_name, order_price, agent_status,
       competitor_price, decision, summary
FROM price_match_results;
```

In the supplied fixture, all 10 orders match lower competitor prices: expect `SUCCESS`, `PRICE_MATCH`, and populated price and summary fields. The fixture does not include equal/higher prices or missing products. If a parsed field is empty, inspect `raw_response` in `price_match_results` before assuming the agent failed.


*Example from the workshop audit, not a console screenshot. Product prices and generated wording can change.*

**Stop this SELECT reader after inspecting it.** Keep the two writer jobs running while orders arrive. Agent summaries report notification actions; check the configured inbox to confirm delivery.

<details>
<summary>Example notification email</summary>

<img src="./assets/lab1/email.png" alt="Illustrative price-match notification email" width="700">

*This older screenshot illustrates email delivery. The current template explicitly says that no refund is processed.*

</details>

## Troubleshooting

- **No results yet:** Check that both writer jobs are `RUNNING`. Orders arrive every two minutes and model/tool calls take additional time. If the generator has exited, inspect retained input records before restarting it.
- **`PENDING` / `POOL_EXHAUSTED`:** Stop preview SELECT cells and completed-lab writers you no longer need. A queued reader is not evidence of an empty table.
- **Model errors:** Open the failed statement's exceptions. For native hosted inference, confirm the selected catalog contains the models and check the reported model-access or quota error. For `--bedrock`, check Claude access; for `--azure-openai`, check the configured deployment and quota. External-provider key fixes do not apply to native hosted models.
- **No email:** Check the configured recipient in both prompts, run Test Query 2 once, and inspect spam filtering. `MCP error -32602` can mean `to` was supplied as an array instead of a plain string.
- **Missing MCP connection:** Run `SHOW CONNECTIONS;` in the correct database. If `remote-mcp-connection` is absent, inspect deployment output before rerunning deployment.

### Restarting safely

For a paused run, **resume the existing writers and use retained input**, rather than rerunning the data generator. A fresh replay reuses IDs and requires a deliberate reset of the workshop-created outputs and state. Stop the price-match writer first; ask the workshop host to coordinate that reset. Do not drop `orders`, `customers`, or `products`, and do not use global destroy to restart this one lab.

### Moving to the next lab

Stop the two Lab 1 writer statements and any remaining preview SELECTs when you finish. The tables and results remain available. `uv run destroy` removes **all deployed labs and shared core resources**; reserve it for the end of all chosen labs.

## Navigation

- [Back to overview](./README.md)
- [Next: Lab 2 — Vector Search / RAG](./LAB2-Walkthrough.md)
- [Full quickstart cleanup](./README.md#cleanup)
