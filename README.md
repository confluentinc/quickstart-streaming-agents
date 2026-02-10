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
<td><b>*NEW!*</b> Now using new Agent Definition (CREATE AGENT) syntax. Price matching agent that scrapes competitor websites and adjusts prices in real-time<br><br><img src="./assets/lab1/lab1-architecture.png" alt="Lab1 architecture diagram"></td>
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
- **Lab1:** Zapier remote MCP server ([Setup guide](./assets/pre-setup/Zapier-Setup.md))
- **Lab2:** MongoDB Atlas vector database ([Setup guide](./assets/pre-setup/MongoDB-Setup.md))
- **Lab3:** Zapier ([Setup guide](./assets/pre-setup/Zapier-Setup.md)) + MongoDB ([Setup guide](./assets/pre-setup/MongoDB-Setup.md))

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

**Clone the repository and navigate to the Quickstart directory:**

```bash
git clone https://github.com/confluentinc/quickstart-streaming-agents.git
cd quickstart-streaming-agents
```
**One command deployment:**

```bash
uv run deploy
```

That's it! The script will prompt you to choose a cloud provider (AWS or Azure) and guide you through setup, automatically create API keys, and deploy your chosen lab(s).

> [!NOTE]
>
> Workshop participants only need: Confluent Cloud API keys + LLM API keys (Bedrock access key/secret for AWS, or Azure OpenAI endpoint/key for Azure). No AWS account or Azure subscription is needed.
>
> Instructors can create shared LLM credentials with `uv run workshop-keys create {aws|azure}`. See the [Workshop Mode Setup Guide](./assets/pre-setup/Workshop-Mode-Setup.md) for more details.


## Directory Structure

```
quickstart-streaming-agents/
├── terraform/                          
│   ├── core/                           # Shared Confluent Cloud infra for all labs
│   ├── lab1-tool-calling/              # Lab-specific infra
│   ├── lab2-vector-search/             # Lab-specific infra
│   └── lab3-agentic-fleet-management/  # Lab-specific infra
├── deploy.py                           # Start here
└── scripts/                            # Python utilities
```

## Cleanup

```bash
# Automated
uv run destroy
```

## Sign up for early access to Flink AI features

For early access to exciting new Flink AI features, [fill out this form and we'll add you to our early access previews.](https://events.confluent.io/early-access-flink-features)