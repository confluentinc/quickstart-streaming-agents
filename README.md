# Streaming Agents on Confluent Cloud Quickstart

![Streaming Agents Intro Slide](./assets/streaming-agents-intro-slide.png)

Build real-time AI agents with [Confluent Cloud Streaming Agents](https://docs.confluent.io/cloud/current/ai/streaming-agents/overview.html). This quickstart includes two hands-on labs:

| Lab | Description | Requirements |
|-----|-------------|--------------|
| [**Lab1 - MCP Tool Calling**](./LAB1-Walkthrough.md) | Price matching agent that scrapes competitor websites and adjusts prices in real-time | Zapier MCP server |
| [**Lab2 - Vector Search - RAG**](./LAB2-Walkthrough.md) | RAG pipeline with vector search for intelligent document retrieval | MongoDB Atlas (free M0 tier) |

## Demo Video

[![Watch on YouTube](https://img.youtube.com/vi/F4bUUsVDBVE/hqdefault.jpg)](https://www.youtube.com/watch?v=F4bUUsVDBVE "Watch on YouTube")

## 🚀 Quick Start

**Fastest path**: Run the automated setup script

```bash
python setup.py
```

The script will:

- Install missing prerequisites (terraform, confluent CLI, etc.)
- Configure cloud provider (AWS or Azure)
- Generate Confluent Cloud API keys (Cloud Resource Management Scope with OrganizationAdmin role)
- Deploy Core infrastructure (Confluent Cloud environment where all labs run)
- Deploy your chosen lab(s)

## 📖 Lab Walkthroughs

Choose your lab and follow the complete tutorial:

### [Lab1: Tool Calling Agent →](./LAB1-Walkthrough.md)

Real-time price matching using web scraping and email notifications. Includes Zapier MCP server setup and step-by-step agent creation.

### [Lab2: Vector Search RAG →](./LAB2-Walkthrough.md)

Document embedding, vector search, and AI-powered responses. Includes MongoDB Atlas setup and complete RAG pipeline implementation.

## Directory Structure

```sh
quickstart-streaming-agents/
├── aws/                   # AWS-specific deployments
│   ├── core/              # Shared infrastructure (deploy first)
│   ├── lab1-tool-calling/
│   └── lab2-vector-search/
├── azure/                 # Azure-specific deployments
│   ├── core/              # Shared infrastructure (deploy first)
│   ├── lab1-tool-calling/
│   └── lab2-vector-search/
└── setup.py               # Automated setup script
```

## Manual Setup (Advanced)

<details>
<summary>Manual terraform deployment steps</summary>

### Prerequisites

- `terraform`, `confluent` CLI installed (or use automated setup script)
- Cloud provider CLI (`aws` or `az`) configured
- Confluent Cloud account

### 1. Choose Cloud Provider

```bash
cd aws/    # or cd azure/
```

⚠️ **IMPORTANT: For AWS Users: [Request access to Claude Sonnet 3.7 in Bedrock for your cloud region](https://console.aws.amazon.com/bedrock/home#/modelaccess)**. If you do not activate it, the LLM connections automatically created by Terraform will not work.

### 2. Deploy Core Infrastructure

```bash
cd core/
# Configure terraform.tfvars with your credentials
terraform init
terraform apply --auto-approve
```

### 3. Deploy Lab(s)

```bash
cd ../lab1-tool-calling/  # or lab2-vector-search
# Configure terraform.tfvars with your credentials
terraform init
terraform apply --auto-approve
```

### Required terraform.tfvars variables

**Core**:

```hcl
prefix = "streaming-agents"
cloud_provider = "aws"  # or "azure"
cloud_region = "your-cloud-region"
confluent_cloud_api_key = "your-key"
confluent_cloud_api_secret = "your-secret"
```

**Lab1 additional**:

```hcl
ZAPIER_SSE_ENDPOINT = "https://mcp.zapier.com/api/mcp/s/your-key/sse"
```

**Lab2 additional**:

```hcl
MONGODB_CONNECTION_STRING = "mongodb+srv://cluster0.abc.mongodb.net"  # yours should look just like this
# Note: the username and password below correspond to a "Database User" role in MongoDB that can access your Atlas vector database. You create this username and password separately from your MongoDB login.
mongodb_username = "your-database-username"
mongodb_password = "your-database-password"
```

</details>

## Next Steps

1. **AWS users**: [Enable Claude Sonnet 3.7 in Bedrock for your cloud region](https://console.aws.amazon.com/bedrock/home#/modelaccess)
2. **Start with Lab1**: [Tool Calling Walkthrough](./LAB1-Walkthrough.md)
3. **Try Lab2**: [Vector Search Walkthrough](./LAB2-Walkthrough.md)

## Cleanup

Remove all resources:

```bash
# From your chosen lab directory
terraform destroy --auto-approve

# From core directory
cd ../core/
terraform destroy --auto-approve
```
