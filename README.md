# Streaming Agents on Confluent Cloud Quickstart

![Streaming Agents Intro Slide](./assets/streaming-agents-intro-slide.png)

Build real-time AI agents with [Confluent Cloud Streaming Agents](https://docs.confluent.io/cloud/current/ai/streaming-agents/overview.html). This quickstart includes two hands-on labs:

| Lab | Description | Requirements |
|-----|-------------|--------------|
| **Lab1** | Price matching agent that scrapes competitor websites and adjusts prices in real-time | Zapier MCP server |
| **Lab2** | RAG pipeline with vector search for intelligent document retrieval | MongoDB Atlas (free M0 tier) |

![Architecture Diagram](./assets/arch.png)

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
- Generate Confluent Cloud API keys
- Deploy Core infrastructure
- Deploy your chosen lab(s)

Then generate sample data and start the labs!

## 📖 Lab Walkthroughs

Choose your lab and follow the complete tutorial:

### [Lab1: Tool Calling Agent →](./LAB1-Walkthrough.md)

Real-time price matching using web scraping and email notifications. Includes Zapier MCP server setup and step-by-step agent creation.

### [Lab2: Vector Search RAG →](./LAB2-Walkthrough.md)

Document embedding, vector search, and AI-powered responses. Includes MongoDB Atlas setup and complete RAG pipeline implementation.

## Directory Structure

```
quickstart-streaming-agents/
├── aws/                    # AWS-specific deployments
│   ├── core/              # Shared infrastructure (deploy first)
│   ├── lab1-tool-calling/
│   └── lab2-vector-search/
├── azure/                 # Azure-specific deployments
│   ├── core/              # Shared infrastructure (deploy first)
│   ├── lab1-tool-calling/
│   └── lab2-vector-search/
└── setup.py              # Automated setup script
```

## Data Generation

Each lab includes sample data and generation scripts:

**Lab1**: Uses Flink SQL to create sample orders, customers, and products tables directly in the workspace

**Lab2**:

```bash
cd aws/lab2-vector-search   # or azure/lab2-vector-search
python publish_documents.py
python publish_queries.py
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

### 2. Deploy Core Infrastructure

```bash
cd core/
# Configure terraform.tfvars with your credentials
terraform init
terraform apply
```

### 3. Deploy Lab(s)

```bash
cd ../lab1-tool-calling/  # or lab2-vector-search
# Configure terraform.tfvars
terraform init
terraform apply
```

### Required terraform.tfvars variables

**Core**:

```hcl
prefix = "streaming-agents"
cloud_provider = "aws"  # or "azure"
cloud_region = "us-east-1"
confluent_cloud_api_key = "your-key"
confluent_cloud_api_secret = "your-secret"
```

**Lab1 additional**:

```hcl
ZAPIER_SSE_ENDPOINT = "https://mcp.zapier.com/api/mcp/s/your-key/sse"
```

**Lab2 additional**:

```hcl
MONGODB_CONNECTION_STRING = "mongodb+srv://cluster0.abc.mongodb.net"
mongodb_username = "confluent-user"
mongodb_password = "your-password"
```

</details>

## Prerequisites

- `terraform`, `confluent` CLI installed (or use automated setup script)
- Cloud provider CLI (`aws` or `az`) configured
- Confluent Cloud account

## Next Steps

1. **AWS users**: [Enable Claude Sonnet in Bedrock](https://console.aws.amazon.com/bedrock/home#/modelaccess)
2. **Start with Lab1**: [Tool Calling Walkthrough](./LAB1-Walkthrough.md)
3. **Try Lab2**: [Vector Search Walkthrough](./LAB2-Walkthrough.md)

## Cleanup

Remove all resources:

```bash
# From your chosen lab directory
terraform destroy

# From core directory
cd ../core/
terraform destroy
```
