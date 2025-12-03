## Zapier Remote MCP Server Setup

Create a Zapier MCP server for tool calling:

<a id="step-1"></a>
### 1. Create free Zapier Account

Sign up for a free account at [zapier.com](https://zapier.com/sign-up) and verify your email.

<a id="step-2"></a>
### 2. Create MCP Server

Visit [mcp.zapier.com](https://mcp.zapier.com/mcp/servers), choose **"Other"** as MCP Client, and create your server.

<img src="./zapier-screenshots/3.png" alt="Create MCP Server" width="50%" />

<a id="step-3"></a>
### 3. Add Tools

Add these tools to your MCP server:

- **`Webhooks by Zapier: GET`** and **`Webhooks by Zapier: Custom Request`** tools
- **`Gmail: Send Email`** tool (authenticate via SSO). This tool is needed for Lab1 only.

<img src="./zapier-screenshots/4.png" alt="Add Tools" width="50%" />

<a id="step-4"></a>
### 4. Get SSE Endpoint URL

Click **"Connect",** choose **"Other"** for your client, then change transport to **"SSE Endpoint"**, and **copy the URL.** This is the `zapier_sse_endpoint` you will need to enter when deploying the lab with `uv run deploy`.

<img src="./zapier-screenshots/7.png" alt="SSE Endpoint" width="50%" />
Make sure the endpoint URL you have ends with `/sse`, and copy it somewhere safe. You will enter this value as the `zapier_sse_endpoint` when deploying labs with `uv run deploy` later.

## :white_check_mark: Checklist

- [ ] Created MCP server and chose "Other" as the MCP client ([step 2](#step-2))
- [ ] Added  **`Webhooks by Zapier: GET`** , **`Webhooks by Zapier: Custom Request`** , and **`Gmail: Send Email`** tools ([step 3](#step-3))
- [ ] Server URL ends in `/sse` ([step 4](#step-4))
- [ ] Copied the URL somewhere safe, to enter it later during deployment ([step 4](#step-4))

## Navigation

- **← Back to Overview**: [Main README](../../README.md)
- **→ Lab1**: [Price Matching Orders With MCP Tool Calling](../../LAB1-Walkthrough.md)
- **→ Lab3**: [Agentic Fleet Management](../../LAB3-Walkthrough.md)
- **→ MongoDB Setup**: [MongoDB Atlas Setup Guide](./MongoDB-Setup.md)
