# Streaming Agents on Confluent Cloud Quickstart

![Streaming Agents Intro Slide](./assets/streaming-agents-intro-slide.png)

Build real-time AI agents with [Confluent Cloud Streaming Agents](https://docs.confluent.io/cloud/current/ai/streaming-agents/overview.html). This quickstart includes two hands-on labs:

| Lab | Description | Requirements |
|-----|-------------|--------------|
| [**Lab1 - MCP Tool Calling**](./LAB1-Walkthrough.md) | Price matching agent that scrapes competitor websites and adjusts prices in real-time | Zapier MCP server |
| [**Lab2 - Vector Search - RAG**](./LAB2-Walkthrough.md) | Vector search pipeline with optional retrieval augmented generation (RAG) for intelligent document retrieval | MongoDB Atlas (free M0 tier) |

## Demo Video

[![Watch on YouTube](https://img.youtube.com/vi/F4bUUsVDBVE/hqdefault.jpg)](https://www.youtube.com/watch?v=F4bUUsVDBVE "Watch on YouTube")

## 🚀 Quick Start

**One command deployment:**

```bash
uv run deploy
```

That's it! The script will guide you through setup, automatically create API keys, and deploy your chosen lab(s).

## Prerequisites

**Required accounts & credentials:**

- [![Sign up for Confluent Cloud](https://img.shields.io/badge/Sign%20up%20for%20Confluent%20Cloud-007BFF?style=for-the-badge&logo=apachekafka&logoColor=white)](https://confluent.cloud/signup)
- **Lab1:** Zapier account + SSE endpoint URL → [Setup guide](./LAB1-Walkthrough.md#zapier-mcp-server-setup)
- **Lab2:** MongoDB Atlas + connection string, database-specific user credentials → [Setup guide](./LAB2-Walkthrough.md#mongodb-atlas-setup)

**Required tools:**

- **uv** - `brew install uv` (Mac) or `winget install astral-sh.uv` (Windows)
- **Docker** - for data generation
- **Terraform** - infrastructure deployment
- **Confluent CLI** - cloud resource management
- **AWS CLI** or **Azure CLI** - choose your cloud provider
  - ***\*⚠️ AWS users:\**** [Enable Claude Sonnet 3.7 in Bedrock](https://console.aws.amazon.com/bedrock/home#/modelaccess) in your specific region before deploying.


<details>
<summary>📦 Platform-specific installation commands</summary>

**Mac:**
```bash
brew install uv git && brew tap hashicorp/tap && brew install hashicorp/tap/terraform && brew install --cask confluent-cli docker-desktop  && brew install awscli  # or azure-cli
```

**Windows:**
```powershell
winget install astral-sh.uv Git.Git Docker.DockerDesktop Hashicorp.Terraform ConfluentInc.Confluent-CLI Amazon.AWSCLI  # or Microsoft.AzureCLI
```

**Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Install other tools via your package manager
```

</details>


## Directory Structure

```
quickstart-streaming-agents/
├── aws|azure/               # Choose a cloud
│   ├── core/                # Shared infrastructure
│   ├── lab1-tool-calling/  
│   └── lab2-vector-search/ 
├── deploy.py                # 🚀 Start here
└── scripts/                 # Python utilities
```

<details>
<summary>🔄 Alternative deployment methods</summary>

**Traditional Python:**
```bash
pip install -r requirements.txt
python deploy.py
```

</details>

<details>
<summary>🔧 Manual terraform deployment</summary>

### Prerequisites
- All tools installed and authenticated
- Confluent Cloud account with API keys

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
prefix = "streaming-agents"
cloud_provider = "aws"  # or "azure"
cloud_region = "your-region"
confluent_cloud_api_key = "your-key"
confluent_cloud_api_secret = "your-secret"
ZAPIER_SSE_ENDPOINT = "https://mcp.zapier.com/api/mcp/s/your-key/sse"  # Lab1
MONGODB_CONNECTION_STRING = "mongodb+srv://cluster0.abc.mongodb.net"  # Lab2
mongodb_username = "your-db-user"  # Lab2
mongodb_password = "your-db-pass"  # Lab2  # pragma: allowlist secret
```

</details>

## Cleanup

```bash
# Automated
uv run deploy  # Choose cleanup option

# Manual
cd aws/lab1-tool-calling && terraform destroy --auto-approve
cd ../core && terraform destroy --auto-approve
```