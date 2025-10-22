# Streaming Agents on Confluent Cloud Quickstart

[![Sign up for Confluent Cloud](https://img.shields.io/badge/Sign%20up%20for%20Confluent%20Cloud-007BFF?style=for-the-badge&logo=apachekafka&logoColor=white)](https://www.confluent.io/get-started/?utm_campaign=tm.pmm_cd.q4fy25-quickstart-streaming-agents&utm_source=github&utm_medium=demo)

![Streaming Agents Intro Slide](./assets/streaming-agents-intro-slide.png)




Build real-time AI agents with [Confluent Cloud Streaming Agents](https://docs.confluent.io/cloud/current/ai/streaming-agents/overview.html). This quickstart includes two hands-on labs:

<table>
<tr>
<th width="25%">Lab</th>
<th width="75%">Description</th>
</tr>
<tr>
<td><a href="./LAB1-Walkthrough.md"><strong>Lab1 - MCP Tool Calling</strong></a></td>
<td>Price matching agent that scrapes competitor websites and adjusts prices in real-time<br><br><img src="./assets/lab1/lab1-architecture.png" alt="Lab1 Architecture"></td>
</tr>
<tr>
<td><a href="./LAB2-Walkthrough.md"><strong>Lab2 - Vector Search - RAG</strong></a></td>
<td>Vector search pipeline with optional retrieval augmented generation (RAG) for intelligent document retrieval<br><br><img src="./assets/lab2/mongodb/00_lab2_architecture.png" alt="Lab2 Architecture"></td>
</tr>
</table>

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

- [![Sign up for Confluent Cloud](https://img.shields.io/badge/Sign%20up%20for%20Confluent%20Cloud-007BFF?style=for-the-badge&logo=apachekafka&logoColor=white)](https://www.confluent.io/get-started/?utm_campaign=tm.pmm_cd.q4fy25-quickstart-streaming-agents&utm_source=github&utm_medium=demo)
- **Lab1:** Zapier account + SSE endpoint URL → [Setup guide](./LAB1-Walkthrough.md#zapier-mcp-server-setup)
- **Lab2:** MongoDB Atlas + connection string, database-specific user credentials → [Setup guide](./LAB2-Walkthrough.md#mongodb-atlas-setup)

**Required tools:**

- **[uv](https://github.com/astral-sh/uv)**
- **[Python 3.8+](https://github.com/python/cpython)**
- **[Terraform](https://github.com/hashicorp/terraform)** - infrastructure deployment
- **[AWS CLI](https://github.com/aws/aws-cli)** or **[Azure CLI](https://github.com/Azure/azure-cli)**
- **[Confluent CLI](https://docs.confluent.io/confluent-cli/current/overview.html)** - cloud resource management
- **[Docker](https://github.com/docker)** - for Lab1 data generation
- **[librdkafka](https://github.com/confluentinc/librdkafka)**

<details>
<summary>📦 Platform-specific installation commands</summary>

**Mac:**
```bash
brew install uv git && brew tap hashicorp/tap && brew install hashicorp/tap/terraform && brew install --cask confluent-cli docker-desktop && brew install librdkafka && brew install awscli  # or azure-cli
```

**Windows:**
```powershell
winget install astral-sh.uv Git.Git Docker.DockerDesktop Hashicorp.Terraform ConfluentInc.Confluent-CLI Amazon.AWSCLI  # or Microsoft.AzureCLI
```
> **Note:** librdkafka is bundled with confluent-kafka Python wheels on Windows - no separate installation needed.

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
prefix = "streaming-agents"
cloud_provider = "aws"  # or "azure"
cloud_region = "your-region"  # must be a region supported by MongoDB free tier, otherwise Lab2 deployment will not succeed
confluent_cloud_api_key = "your-key"
confluent_cloud_api_secret = "your-secret"
ZAPIER_SSE_ENDPOINT = "https://mcp.zapier.com/api/mcp/s/your-key/sse"  # Lab1
MONGODB_CONNECTION_STRING = "mongodb+srv://cluster0.abc.mongodb.net"  # Lab2
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