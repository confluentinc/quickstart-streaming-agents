# Streaming Agents on Confluent Cloud Quickstart

[![Sign up for Confluent Cloud](https://img.shields.io/badge/Sign%20up%20for%20Confluent%20Cloud-007BFF?style=for-the-badge&logo=apachekafka&logoColor=white)](https://www.confluent.io/get-started/?utm_campaign=tm.pmm_cd.q4fy25-quickstart-streaming-agents&utm_source=github&utm_medium=demo)

<div align="center">
  <a href="https://www.youtube.com/watch?v=3fWMD3qqBR8">
    <img src="https://img.youtube.com/vi/3fWMD3qqBR8/maxresdefault.jpg" alt="Watch Demo Video" style="width:100%;max-width:800px;">
  </a>
</div>

Build real-time AI agents with [Confluent Cloud Streaming Agents](https://docs.confluent.io/cloud/current/ai/streaming-agents/overview.html). This quickstart includes three hands-on labs:

<table>
<tr>
<th width="25%">Lab</th>
<th width="75%">Description</th>
</tr>
<tr>
<td><a href="./LAB1-Walkthrough.md"><strong>Lab1 - Price Matching Orders With MCP Tool Calling</strong></a></td>
<td><b>*NEW!*</b> Now using new Agent Definition (CREATE AGENT) syntax. Price matching agent that scrapes competitor websites and adjusts prices in real-time.<br><br><img src="./assets/lab1/lab1-architecture.png" alt="Lab1 architecture diagram"></td>
</tr>
<tr>
<td><a href="./LAB2-Walkthrough.md"><strong>Lab2 - Vector Search & RAG</strong></a></td>
<td>Vector search pipeline template with retrieval augmented generation (RAG). Use the included Flink documentation chunks, or bring your own documents for intelligent document retrieval.<br><br><img src="./assets/lab2/00_lab2_architecture.png" alt="Lab2 architecture diagram"></td>
</tr>
<tr>
<td><a href="./LAB3-Walkthrough.md"><strong>Lab3 - Agentic Fleet Management Using Confluent Intelligence</strong></a></td>
    <td>End-to-end boat fleet management demo showing use of Agent Definition, MCP tool calling, vector search, and <a href="https://docs.confluent.io/cloud/current/ai/builtin-functions/detect-anomalies.html">anomaly detection</a>.<br><br><img src="./assets/lab3/lab3-architecture.png" alt="Lab3 architecture diagram"></td>
</tr>
</table>

## Prerequisites

**Required accounts & credentials:**

- [![Sign up for Confluent Cloud](https://img.shields.io/badge/Sign%20up%20for%20Confluent%20Cloud-007BFF?style=for-the-badge&logo=apachekafka&logoColor=white)](https://www.confluent.io/get-started/?utm_campaign=tm.pmm_cd.q4fy25-quickstart-streaming-agents&utm_source=github&utm_medium=demo)
- **LLM Provider:** AWS Bedrock API keys **OR** Azure OpenAI keys - or BYOK
- **Lab1 & Lab3:** Zapier remote MCP server ([Setup guide](./assets/pre-setup/Zapier-Setup.md))

> **Note:** SSE endpoints are now deprecated by Zapier. If you previously created an SSE endpoint, you'll need to create a new Streamable HTTP endpoint and copy the Zapier token instead. See the [Zapier Setup guide](./assets/pre-setup/Zapier-Setup.md) for updated instructions.

**Required tools:**

- **[Confluent CLI](https://docs.confluent.io/confluent-cli/current/overview.html)** - must be logged in
- **[Docker](https://github.com/docker)** - for Lab1 & Lab3 data generation only
- **[Git](https://github.com/git/git)**
- **[Terraform](https://github.com/hashicorp/terraform)**
- **[uv](https://github.com/astral-sh/uv)**

<details>
<summary> Installation commands (Mac/Windows)</summary>
**Mac:**

```bash
brew install uv git python && brew tap hashicorp/tap && brew install hashicorp/tap/terraform && brew install --cask confluent-cli docker-desktop
```

**Windows:**

```powershell
winget install astral-sh.uv Git.Git Docker.DockerDesktop Hashicorp.Terraform ConfluentInc.Confluent-CLI Python.Python
```
</details>

## 🚀 Quick Start

**1. Clone the repository and navigate to the Quickstart directory:**

```bash
git clone https://github.com/confluentinc/quickstart-streaming-agents.git
cd quickstart-streaming-agents
```
**2. Auto-generate AWS Bedrock or Azure OpenAI keys:**

```bash
# Creates API-KEYS-[AWS|AZURE].md and auto-populates them in next step
uv run workshop-keys create
```

3. **One command deployment:**

```bash
uv run deploy
```

That's it! The script will autofill generated credentials and guide you through setup and deployment of your chosen lab(s).
> [!NOTE]
>
> See the [Workshop Mode Setup Guide](./assets/pre-setup/Workshop-Mode-Setup.md) for details about auto-generating API keys and tips for running demo workshops.

## Directory Structure

```
quickstart-streaming-agents/
├── terraform/                          
│   ├── core/                           # Shared Confluent Cloud infra for all labs
│   ├── lab1-tool-calling/              # Lab1-specific infra
│   ├── lab2-vector-search/             # Lab2-specific infra
│   └── lab3-agentic-fleet-management/  # Lab3-specific infra
├── deploy.py                           # Start here with uv run deploy
└── scripts/                            # Python utilities invoked with uv
```

**[NEW!] Streamlined architecture:**

- No heavyweight AWS/Azure Terraform providers needed - just LLM API keys generated with one command
- **MongoDB is now pre-configured:** No need to set up your own MongoDB Atlas cluster anymore - we provide MongoDB endpoints with read-only credentials, pre-populated with vectorized documents so you can get started faster

## Cleanup

```bash
# Automated
uv run destroy
```

## Sign up for early access to Flink AI features

For early access to exciting new Flink AI features, [fill out this form and we'll add you to our early access previews.](https://events.confluent.io/early-access-flink-features)