# Workshop Testing Suite

This directory contains automated End-to-End tests for the Confluent Streaming Agents workshop, specifically for Lab 3 (Agentic Fleet Management).

> **Note:** This testing infrastructure is for developers validating workshop functionality. Regular workshop participants don't need to interact with this directory.

## Overview

The test suite automatically:
1. Creates AWS/Azure workshop credentials
2. Deploys all workshop labs using Terraform
3. Generates test data for Lab 3
4. Executes Flink SQL statements (anomaly detection, RAG enrichment, agent execution)
5. Validates results meet expected criteria
6. Tears down all infrastructure

**Runtime:** ~70-80 minutes per cloud provider
**Cost:** ~$5-8 per run (Kafka cluster + Flink compute + LLM inference)

## Prerequisites

### Required Software
- **Confluent CLI**: Install from [docs.confluent.io/confluent-cli](https://docs.confluent.io/confluent-cli/current/install.html)
- **Terraform**: Version >= 1.0.0
- **Python**: 3.10 or higher with `uv` package manager

### Required Credentials

You'll need the following credentials for testing:

**For All Tests:**
- Confluent Cloud API key with OrganizationAdmin role
- Zapier token (see [Zapier Setup Guide](../assets/pre-setup/Zapier-Setup.md))

**For AWS Tests:**
- AWS Bedrock access key and secret with Claude Sonnet 4.5 model access
- See [Workshop Mode Setup Guide](../assets/pre-setup/Workshop-Mode-Setup.md) for credential creation

**For Azure Tests:**
- Azure OpenAI endpoint URL and API key
- See [Workshop Mode Setup Guide](../assets/pre-setup/Workshop-Mode-Setup.md) for credential creation

## One-Time Setup

### 1. Install Development Dependencies

```bash
# From project root
uv sync --extra dev
```

This installs test-specific dependencies (pytest, pytest-timeout, pytest-order) that regular workshop users don't need.

### 2. Configure Test Credentials

```bash
# From project root
cp credentials.template.json testing/credentials.json
```

Edit `testing/credentials.json` and fill in your credentials:

```json
{
    "cloud": "aws",
    "region": "us-east-1",
    "confluent_cloud_api_key": "YOUR_CONFLUENT_API_KEY",
    "confluent_cloud_api_secret": "YOUR_CONFLUENT_API_SECRET",
    "aws_bedrock_access_key": "YOUR_AWS_KEY",
    "aws_bedrock_secret_key": "YOUR_AWS_SECRET",
    "azure_openai_endpoint": "YOUR_AZURE_ENDPOINT",
    "azure_openai_api_key": "YOUR_AZURE_KEY",
    "zapier_token": "YOUR_ZAPIER_TOKEN",
    "owner_email": "test@example.com"
}
```

> **Security:** `testing/credentials.json` is gitignored. Never commit credentials to the repository.

### 3. Ensure Confluent CLI is Authenticated

```bash
confluent login --save
```

The test suite will attempt auto-login using your Confluent API key if not already authenticated.

## Running Tests

### Run Lab 3 E2E Test (AWS)

```bash
# From project root
uv run pytest testing/e2e/test_lab3_workflow.py -k aws -v --timeout=5400
```

**Expected runtime:** ~70-80 minutes
**What it tests:**
- Workshop key creation (validates API keys work)
- Terraform deployment (all 4 environments)
- Data generation (verifies >= 28,000 ride_requests)
- Anomaly detection (verifies 1-2 anomalies detected)
- RAG enrichment (verifies no NULLs in summary/chunk columns)
- Agent execution (verifies successful boat dispatch)
- Complete teardown (verifies cleanup)

### Run Lab 3 E2E Test (Azure)

```bash
# From project root
uv run pytest testing/e2e/test_lab3_workflow.py -k azure -v --timeout=5400
```

**Expected runtime:** ~70-80 minutes

### Run Both Cloud Providers (Sequential)

```bash
# From project root
uv run pytest testing/e2e/test_lab3_workflow.py -v --timeout=5400
```

> **Warning:** Running both tests sequentially takes ~140-160 minutes. Do NOT run them in parallel — they share Terraform state files.

## Test Validation Criteria

| Test Step | Pass Criteria | Fail Criteria |
|-----------|--------------|---------------|
| Workshop Keys | `API-KEYS-<CLOUD>.md` created, no validation warnings | File missing or "cannot validate" warning |
| Deploy | `uv run deploy --testing` exits 0 | Non-zero exit code or terraform error |
| Data Generation | `ride_requests` >= 28,000 records | < 28,000 after 10 min timeout |
| Anomaly Detection | `anomalies_per_zone` produces 1-2 records | 0 records or > 2 records |
| RAG Enrichment | No NULLs in `anomaly_reason`, `top_chunk_*` | Any NULL or empty string |
| Agent Execution | 1-2 records in `completed_actions` | 0 records or > 2 records |
| Agent Success | `dispatch_summary` without failure phrases | Contains "unable to dispatch", "failed to", etc. |
| Agent API Call | `api_response` non-NULL, non-empty | NULL or empty (agent didn't execute) |
| Teardown | `uv run destroy --testing` exits 0 | Non-zero exit or cleanup failure |

## Troubleshooting

### Test Fails During Deployment

```bash
# Emergency cleanup if test fails mid-deployment
cd testing
cp credentials.json ../credentials.json
cd ..
uv run destroy --testing
uv run workshop-keys destroy aws  # or azure
rm credentials.json
```

### Confluent CLI Not Authenticated

```bash
confluent login --save
# Or the test will attempt auto-login using credentials.json
```

### Missing Terraform State

If terraform state is corrupted or missing, manually clean up:

```bash
# Remove all terraform state files
find terraform -name "terraform.tfstate*" -delete
find terraform -name ".terraform" -type d -exec rm -rf {} +
```

### Cost Control

Each test run costs ~$5-8 per cloud provider. To minimize costs:
- Run tests only before releases or after significant changes
- Set a 90-minute hard timeout (already configured via `pytest-timeout`)
- Verify teardown completed successfully

## Test Infrastructure Details

### Directory Structure

```
testing/
├── README.md              # This file
├── .gitignore             # Ignores credentials and test artifacts
├── conftest.py            # Pytest fixtures (credentials, deploy/teardown)
├── credentials.json       # Your test credentials (gitignored)
├── helpers/
│   ├── flink_sql_helper.py    # Flink SQL execution via confluent CLI
│   ├── polling_helper.py      # Retry/polling utilities
│   └── terraform_helper.py    # Terraform state extraction
├── e2e/
│   └── test_lab3_workflow.py  # Main E2E test
└── reports/               # Test artifacts (gitignored)
```

### How Tests Work

1. **Setup (deploy_and_teardown fixture):**
   - Loads `testing/credentials.json`
   - Copies to `credentials.json` in project root (where `deploy.py --testing` expects it)
   - Ensures Confluent CLI is authenticated
   - Creates workshop keys (`uv run workshop-keys create <cloud>`)
   - Deploys infrastructure (`uv run deploy --testing`)
   - Extracts SQL from `LAB3-Walkthrough.md`
   - Initializes Flink SQL helper

2. **Test Execution (4 ordered tests):**
   - Each test executes Flink SQL via `confluent flink statement create`
   - Polls for results with configurable timeouts
   - Validates results meet expected criteria

3. **Teardown (runs even on failure):**
   - Cleans up Flink statements
   - Destroys infrastructure (`uv run destroy --testing`)
   - Destroys workshop keys
   - Removes `credentials.json` from project root

### SQL Extraction

Tests extract SQL statements directly from `LAB3-Walkthrough.md` using the existing `extract_sql_from_lab_walkthroughs()` function. This ensures tests always use the same SQL that workshop participants run.

## Regular Workshop Users

If you're a workshop participant (not a developer), you **don't need this directory**. Your workflow is:

```bash
# Regular workshop workflow (unchanged)
uv sync
uv run deploy
```

The testing infrastructure has zero impact on regular users — test dependencies are only installed when explicitly requested with `uv sync --extra dev`.

## Questions or Issues

For questions about the testing infrastructure, see the main `TESTS_PLAN.md` in the project root or open an issue on GitHub.
