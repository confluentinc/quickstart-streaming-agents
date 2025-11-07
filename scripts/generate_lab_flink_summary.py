#!/usr/bin/env python3
"""
Generate Flink SQL command summary markdown files for labs.

This script is invoked by Terraform during lab deployment to create a
comprehensive Flink SQL command reference for each lab.

Usage:
    python scripts/generate_lab_flink_summary.py <lab-name> <cloud-provider> <terraform-dir>

Examples:
    python scripts/generate_lab_flink_summary.py lab1 aws aws/lab1-tool-calling
    python scripts/generate_lab_flink_summary.py lab2 azure azure/lab2-vector-search
"""

import json
import subprocess
import sys
from pathlib import Path

# Add scripts/common to the path so we can import from it
sys.path.insert(0, str(Path(__file__).parent / "common"))

from generate_deployment_summary import generate_flink_sql_summary


def get_lab_commands(lab_name: str, cloud_provider: str):
    """
    Get the automated and manual SQL commands for each lab.

    Returns:
        tuple: (automated_commands, manual_commands)
    """
    # Determine provider-specific details
    if cloud_provider == "azure":
        provider = "azureopenai"
        llm_connection = "llm-textgen-connection"
    else:  # AWS
        provider = "bedrock"
        llm_connection = "llm-textgen-connection"

    if lab_name == "lab1":
        automated = [
            {
                "title": "Create Zapier MCP Connection",
                "sql": """CREATE CONNECTION `zapier-mcp-connection`
WITH (
  'type' = 'MCP_SERVER',
  'endpoint' = '<your-zapier-sse-endpoint>',
  'api-key' = 'api_key'
);"""
            },
            {
                "title": "Create Zapier MCP Model",
                "sql": f"""CREATE MODEL zapier_mcp_model
INPUT (prompt STRING)
OUTPUT (response STRING)
WITH (
  'provider' = '{provider}',
  'task' = 'text_generation',
  '{provider}.connection' = '{llm_connection}',
  '{provider}.params.max_tokens' = '50000',
  'mcp.connection' = 'zapier-mcp-connection'
);"""
            },
            {
                "title": "Create Orders Table",
                "sql": """CREATE TABLE orders (
  order_id VARCHAR(2147483647) NOT NULL,
  customer_id VARCHAR(2147483647) NOT NULL,
  product_id VARCHAR(2147483647) NOT NULL,
  price DOUBLE NOT NULL,
  order_ts TIMESTAMP(3) WITH LOCAL TIME ZONE NOT NULL
) WITH (
  'changelog.mode' = 'append',
  'connector' = 'confluent',
  'kafka.cleanup-policy' = 'delete',
  'kafka.max-message-size' = '2097164 bytes',
  'kafka.retention.size' = '0 bytes',
  'kafka.retention.time' = '7 d',
  'key.format' = 'raw',
  'value.format' = 'json-registry'
);"""
            },
            {
                "title": "Create Customers Table",
                "sql": """CREATE TABLE customers (
  customer_id VARCHAR(2147483647) NOT NULL,
  customer_name VARCHAR(2147483647),
  customer_email VARCHAR(2147483647),
  address VARCHAR(2147483647),
  state VARCHAR(2147483647),
  PRIMARY KEY (customer_id) NOT ENFORCED
) WITH (
  'changelog.mode' = 'upsert',
  'connector' = 'confluent',
  'kafka.cleanup-policy' = 'compact',
  'kafka.max-message-size' = '2097164 bytes',
  'kafka.retention.size' = '0 bytes',
  'kafka.retention.time' = '7 d',
  'key.format' = 'raw',
  'value.format' = 'json-registry'
);"""
            },
            {
                "title": "Create Products Table",
                "sql": """CREATE TABLE products (
  product_id VARCHAR(2147483647) NOT NULL,
  product_name VARCHAR(2147483647),
  category VARCHAR(2147483647),
  base_price DOUBLE,
  PRIMARY KEY (product_id) NOT ENFORCED
) WITH (
  'changelog.mode' = 'upsert',
  'connector' = 'confluent',
  'kafka.cleanup-policy' = 'compact',
  'kafka.max-message-size' = '2097164 bytes',
  'kafka.retention.size' = '0 bytes',
  'kafka.retention.time' = '7 d',
  'key.format' = 'raw',
  'value.format' = 'json-registry'
);"""
            }
        ]

        manual = [
            {
                "title": "Create Zapier Tool",
                "sql": """CREATE TOOL zapier
USING CONNECTION `zapier-mcp-connection`
WITH (
  'type' = 'mcp',
  'allowed_tools' = 'webhooks_by_zapier_get, gmail_send_email',
  'request_timeout' = '30'
);"""
            },
            {
                "title": "Create Price Match Agent",
                "sql": """CREATE AGENT price_match_agent
USING MODEL llm_textgen_model
USING PROMPT 'You are a price matching assistant that performs the following steps:

1. SCRAPE COMPETITOR PRICE: Use the webhooks_by_zapier_get tool to extract page contents from the competitor URL provided in the prompt.

2. EXTRACT PRICE: Analyze the scraped page content to find the product that most closely matches the product name. Extract only the price in format: XX.XX

3. COMPARE AND NOTIFY: Compare the extracted competitor price with our order price. If the competitor price is lower than our price, use the gmail_send_email tool to send a price match notification email.

Return a summary of actions taken and results.'
USING TOOLS zapier
COMMENT 'Agent for scraping competitor prices and sending price match notifications'
WITH (
  'max_consecutive_failures' = '2',
  'MAX_ITERATIONS' = '5'
);"""
            },
            {
                "title": "Create Price Match Input Table",
                "sql": """SET 'sql.state-ttl' = '1 HOURS';

CREATE TABLE price_match_input AS
SELECT
    o.order_id,
    p.product_name,
    c.customer_email,
    o.price AS order_price,
    CONCAT(
        'COMPETITOR URL: https://www.walmart.com/search?q="', p.product_name, '"',
        ' PRODUCT NAME: ', p.product_name,
        ' OUR ORDER PRICE: $', CAST(CAST(o.price AS DECIMAL(10, 2)) AS STRING),
        ' EMAIL RECIPIENT: <your-email>',
        ' EMAIL SUBJECT: Price Match Applied - Order #', o.order_id,
        ' [email body template...]'
    ) AS agent_prompt
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id;"""
            },
            {
                "title": "Run the Agent and Create Results Table",
                "sql": """CREATE TABLE price_match_results AS
SELECT
    pmi.order_id,
    pmi.product_name,
    pmi.customer_email,
    CAST(CAST(pmi.order_price AS DECIMAL(10, 2)) AS STRING) as order_price,
    agent_result.status as agent_status,
    agent_result.response as agent_response
FROM price_match_input pmi,
LATERAL TABLE(
    AI_RUN_AGENT(
        'price_match_agent',
        pmi.agent_prompt,
        pmi.order_id,
        MAP['debug', 'true']
    )
) as agent_result(status, response);"""
            }
        ]

    elif lab_name == "lab2":
        automated = [
            {
                "title": "Create MongoDB Connection",
                "sql": """CREATE CONNECTION `mongodb-connection`
WITH (
  'type' = 'MONGODB',
  'endpoint' = '<your-mongodb-connection-string>',
  'username' = '<your-mongodb-username>',
  'password' = '<your-mongodb-password>'
);"""
            },
            {
                "title": "Create Documents Table",
                "sql": """CREATE TABLE documents (
  document_id STRING,
  document_text STRING
);"""
            },
            {
                "title": "Create Documents Embed Table",
                "sql": """CREATE TABLE documents_embed (
  document_id STRING,
  chunk STRING,
  embedding ARRAY<FLOAT>
);"""
            },
            {
                "title": "Create Queries Table",
                "sql": """CREATE TABLE queries (
  query STRING NOT NULL
);"""
            },
            {
                "title": "Create Queries Embed Table",
                "sql": """CREATE TABLE queries_embed (
  query STRING,
  embedding ARRAY<FLOAT>
);"""
            },
            {
                "title": "Create Search Results Table",
                "sql": """CREATE TABLE search_results (
  query STRING,
  document_id STRING,
  chunk STRING,
  similarity_score DOUBLE
);"""
            },
            {
                "title": "Create Search Results Response Table",
                "sql": """CREATE TABLE search_results_response (
  query STRING,
  response STRING
);"""
            }
        ]

        manual = [
            {
                "title": "Monitoring Query - Check Document Count",
                "sql": """SELECT COUNT(*) FROM documents;"""
            },
            {
                "title": "Monitoring Query - Check Embeddings",
                "sql": """SELECT COUNT(*) FROM documents_embed;"""
            },
            {
                "title": "Monitoring Query - Check Queries",
                "sql": """SELECT COUNT(*) FROM queries;"""
            },
            {
                "title": "Monitoring Query - View Search Results",
                "sql": """SELECT * FROM search_results LIMIT 5;"""
            },
            {
                "title": "Monitoring Query - View RAG Responses",
                "sql": """SELECT query, response FROM search_results_response LIMIT 5;"""
            }
        ]

    elif lab_name == "lab3":
        automated = [
            {
                "title": "Create Ride Requests Table",
                "sql": """CREATE TABLE ride_requests (
  request_id VARCHAR(2147483647) NOT NULL,
  customer_email VARCHAR(2147483647) NOT NULL,
  pickup_zone VARCHAR(2147483647) NOT NULL,
  drop_off_zone VARCHAR(2147483647) NOT NULL,
  price DOUBLE NOT NULL,
  number_of_passengers INT NOT NULL,
  request_ts TIMESTAMP(3) WITH LOCAL TIME ZONE NOT NULL,
  WATERMARK FOR request_ts AS request_ts - INTERVAL '5' SECOND
);"""
            },
            {
                "title": "Create Vessel Catalog Table",
                "sql": """CREATE TABLE vessel_catalog (
  vessel_id VARCHAR(2147483647) NOT NULL,
  vessel_name VARCHAR(2147483647) NOT NULL,
  base_zone VARCHAR(2147483647) NOT NULL,
  availability VARCHAR(2147483647) NOT NULL,
  capacity INT NOT NULL
);"""
            }
        ]

        manual = [
            {
                "title": "Modify Watermark on Ride Requests",
                "sql": """ALTER TABLE ride_requests
MODIFY (WATERMARK FOR request_ts AS request_ts - INTERVAL '5' SECOND);"""
            },
            {
                "title": "Create Anomalies Detection Table",
                "sql": """CREATE TABLE anomalies_detected_per_zone AS
WITH windowed_traffic AS (
    SELECT
        window_start,
        window_end,
        window_time,
        pickup_zone,
        COUNT(*) AS request_count,
        SUM(number_of_passengers) AS total_passengers,
        SUM(CAST(price AS DECIMAL(10, 2))) AS total_revenue
    FROM TABLE(
        TUMBLE(TABLE ride_requests, DESCRIPTOR(request_ts), INTERVAL '5' MINUTE)
    )
    GROUP BY window_start, window_end, window_time, pickup_zone
),
anomaly_detection AS (
    SELECT
        pickup_zone,
        window_time,
        request_count,
        total_passengers,
        total_revenue,
        ML_DETECT_ANOMALIES(
            CAST(request_count AS DOUBLE),
            window_time,
            JSON_OBJECT(
                'minTrainingSize' VALUE 287,
                'maxTrainingSize' VALUE 7000,
                'confidencePercentage' VALUE 99.999,
                'enableStl' VALUE FALSE
            )
        ) OVER (
            PARTITION BY pickup_zone
            ORDER BY window_time
            RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS anomaly_result
    FROM windowed_traffic
)
SELECT
    pickup_zone,
    window_time,
    request_count,
    total_passengers,
    total_revenue,
    CAST(ROUND(anomaly_result.forecast_value) AS BIGINT) AS expected_requests,
    anomaly_result.upper_bound AS upper_bound,
    anomaly_result.lower_bound AS lower_bound,
    anomaly_result.is_anomaly AS is_surge
FROM anomaly_detection
WHERE anomaly_result.is_anomaly = true
  AND request_count > anomaly_result.upper_bound;"""
            },
            {
                "title": "Query Detected Anomalies",
                "sql": """SELECT * FROM anomalies_detected_per_zone;"""
            }
        ]

    else:
        print(f"Warning: Unknown lab '{lab_name}', no SQL commands configured")
        return [], []

    return automated, manual


def main():
    """Main entry point."""
    if len(sys.argv) != 4:
        print("Usage: python scripts/generate_lab_flink_summary.py <lab-name> <cloud-provider> <terraform-dir>")
        print("Example: python scripts/generate_lab_flink_summary.py lab1 aws aws/lab1-tool-calling")
        sys.exit(1)

    lab_name = sys.argv[1]  # e.g., "lab1"
    cloud_provider = sys.argv[2]  # e.g., "aws"
    terraform_dir = Path(sys.argv[3])  # e.g., "aws/lab1-tool-calling"

    # Validate inputs
    if cloud_provider not in ["aws", "azure"]:
        print(f"Error: Invalid cloud provider '{cloud_provider}'. Must be 'aws' or 'azure'")
        sys.exit(1)

    if not terraform_dir.exists():
        print(f"Error: Terraform directory not found: {terraform_dir}")
        sys.exit(1)

    # Get terraform outputs from CORE (not lab-specific)
    core_terraform_dir = terraform_dir.parent / "core"
    if not core_terraform_dir.exists():
        print(f"Warning: Core terraform directory not found: {core_terraform_dir}")
        print("Generating summary without terraform outputs...")
        tf_outputs = {}
    else:
        try:
            print(f"Reading Terraform outputs from {core_terraform_dir}...")
            result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd=core_terraform_dir,
                capture_output=True,
                text=True,
                check=True
            )
            tf_outputs = json.loads(result.stdout)
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Failed to read terraform outputs: {e}")
            print("Generating summary without terraform outputs...")
            tf_outputs = {}

    # Get lab-specific commands
    automated_commands, manual_commands = get_lab_commands(lab_name, cloud_provider)

    # Generate the summary
    output_file = terraform_dir / "FLINK_SQL_COMMANDS.md"
    lab_full_name = f"{lab_name}-tool-calling" if lab_name == "lab1" else f"{lab_name}-vector-search" if lab_name == "lab2" else f"{lab_name}-anomaly-detection"

    generate_flink_sql_summary(
        lab_name=lab_full_name,
        cloud_provider=cloud_provider,
        tf_outputs=tf_outputs,
        output_path=output_file,
        automated_commands=automated_commands,
        manual_commands=manual_commands
    )

    print(f"\nSuccess! Flink SQL summary generated at: {output_file}")


if __name__ == "__main__":
    main()
