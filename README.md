# Streaming Agents on Confluent Cloud Quickstart

[![Sign up for Confluent Cloud](https://img.shields.io/badge/Sign%20up%20for%20Confluent%20Cloud-007BFF?style=for-the-badge&logo=apachekafka&logoColor=white)](https://www.confluent.io/get-started/?utm_campaign=tm.pmm_cd.q4fy25-quickstart-streaming-agents&utm_source=github&utm_medium=demo)

<div align="center">
  <a href="https://www.youtube.com/watch?v=3fWMD3qqBR8">
    <img src="https://img.youtube.com/vi/3fWMD3qqBR8/maxresdefault.jpg" alt="Watch Demo Video" style="width:100%;max-width:800px;">
  </a>
</div>


Build real-time AI agents with [Confluent Cloud Streaming Agents](https://docs.confluent.io/cloud/current/ai/streaming-agents/overview.html). This quickstart includes two hands-on labs:

<table>
<tr>
<th width="25%">Lab</th>
<th width="75%">Description</th>
</tr>
<tr>
<td><a href="./LAB1-Walkthrough.md"><strong>Lab1 - MCP Tool Calling</strong></a></td>
<td><b>*NEW!*</b> Now using new Agent Definition (CREATE AGENT) syntax. Price matching agent that scrapes competitor websites and adjusts prices in real-time<br><br><img src="./assets/lab1/lab1-architecture.png" alt="Lab1 architecture diagram"></td>
</tr>
<tr>
<td><a href="./LAB2-Walkthrough.md"><strong>Lab2 - Vector Search & RAG</strong></a></td>
<td>Vector search pipeline template with retrieval augmented generation (RAG). Use the included Flink documentation chunks, or bring your own documents for intelligent document retrieval.<br><br><img src="./assets/lab2/mongodb/00_lab2_architecture.png" alt="Lab2 architecture diagram"></td>
</tr>
<tr>
<td><a href="./LAB3-Agentic-Fleet-Management.md"><strong>Lab3 - Agentic Fleet Management</strong></a></td>
    <td>End-to-end boat fleet management demo showing use of Agent Definition, MCP tool calling, vector search, and <a href="https://docs.confluent.io/cloud/current/ai/builtin-functions/detect-anomalies.html">anomaly detection</a>.<br><br><img src="./assets/lab3/lab3_architecture.png" alt="Lab3 architecture diagram"></td>
</tr>
</table>

## Prerequisites

**Required accounts & credentials:**

- [![Sign up for Confluent Cloud](https://img.shields.io/badge/Sign%20up%20for%20Confluent%20Cloud-007BFF?style=for-the-badge&logo=apachekafka&logoColor=white)](https://www.confluent.io/get-started/?utm_campaign=tm.pmm_cd.q4fy25-quickstart-streaming-agents&utm_source=github&utm_medium=demo)
- **Lab1:** Zapier account + SSE endpoint URL → [Setup guide](./LAB1-Walkthrough.md#zapier-mcp-server-setup)
- **Lab2:** MongoDB Atlas + connection string, database-specific user credentials → [Setup guide](./LAB2-Walkthrough.md#mongodb-atlas-setup)

**Required tools:**

- **[AWS CLI](https://github.com/aws/aws-cli)** or **[Azure CLI](https://github.com/Azure/azure-cli)** - must be logged in
- **[Confluent CLI](https://docs.confluent.io/confluent-cli/current/overview.html)** - must be logged in
- **[Docker](https://github.com/docker)** - for Lab1 data generation only
- **[Git](https://github.com/git/git)**
- **[Python 3.8+](https://github.com/python/cpython)**
- **[Terraform](https://github.com/hashicorp/terraform)** - infrastructure deployment
- **[uv](https://github.com/astral-sh/uv)**

<details>
<summary> Installation commands (Mac/Windows/Linux)</summary>
**Mac:**

```bash
brew install uv git python && brew tap hashicorp/tap && brew install hashicorp/tap/terraform && brew install --cask confluent-cli docker-desktop && brew install awscli  # or azure-cli
```

**Windows:**
```powershell
winget install astral-sh.uv Git.Git Docker.DockerDesktop Hashicorp.Terraform ConfluentInc.Confluent-CLI Python.Python Amazon.AWSCLI # or Microsoft.AzureCLI
```

**Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Install other tools via your package manager
```

</details>

## 🚀 Quick Start

**Clone the repository and navigate to the Quickstart directory:**

```bash
git clone https://github.com/confluentinc/quickstart-streaming-agents.git
cd quickstart-streaming-agents
```
**One command deployment:**

```bash
uv run deploy
```

That's it! The script will guide you through setup, automatically create API keys, and deploy your chosen lab(s).


## Directory Structure

```
quickstart-streaming-agents/
├── aws|azure/               # Choose a cloud
│   ├── core/                # Shared Terraform infrastructure
│   ├── lab1-tool-calling/   # Lab-specific infra
│   └── lab2-vector-search/  # Lab-specific infra
├── deploy.py                # 🚀 Start here
└── scripts/                 # Python utilities
```

<details>
<summary>🔄 Alternative deployment methods</summary>

**Traditional Python:**
```bash
pip install -e . && python deploy.py
```

</details>

<details>
<summary>🔧 Manual terraform deployment</summary>

### Prerequisites
- All tools installed and authenticated
- Confluent Cloud API keys (Cloud Resource Management keys with EnvironmentAdmin role)

### Deploy
```bash
cd aws/  # or azure/
cd core/
terraform init && terraform apply --auto-approve
cd ../lab1-tool-calling/  # or lab2-vector-search
terraform init && terraform apply --auto-approve
```

### Required terraform.tfvars

```hcl
cloud_provider = "aws"  # or "azure"
cloud_region = "your-region"  # must be a region supported by MongoDB free tier, otherwise Lab2 deployment will not succeed
confluent_cloud_api_key = "your-key"
confluent_cloud_api_secret = "your-secret"
zapier_sse_endpoint = "https://mcp.zapier.com/api/mcp/s/your-key/sse"  # Lab1
mongodb_connection_string = "mongodb+srv://cluster0.abc.mongodb.net"  # Lab2
mongodb_username = "your-db-user"  # Lab2
mongodb_password = "your-db-pass"  # Lab2
```

### Tear down
```bash
cd aws/lab1-tool-calling && terraform destroy --auto-approve
cd ../core && terraform destroy --auto-approve
```
</details>

## Cleanup
```bash
# Automated
uv run destroy
```

## Sign up for early access to Flink AI features

For early access to exciting new Flink AI features, [fill out this form and we'll add you to our early access previews.](https://events.confluent.io/early-access-flink-features)