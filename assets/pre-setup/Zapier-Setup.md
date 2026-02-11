## Zapier Remote MCP Server Setup

> **Note:** SSE endpoints are now deprecated by Zapier. If you previously created an SSE endpoint, you'll need to create a new Streamable HTTP endpoint and copy the token instead.

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

- **`Webhooks by Zapier: GET`** 

- **`Webhooks by Zapier: Custom Request`** 

- **`Gmail: Send Email`** tool (authenticate via SSO). This tool is needed for Lab1 only.

    <img src="./zapier-screenshots/4.png" alt="Add Tools" width="50%" />

<a id="step-4"></a>

### 4. Get Zapier Token

> **Note:** SSE endpoints are now deprecated. Use Streamable HTTP instead.

* Click **Connect** Tab to open the connection credentials dialog.

* Select **Rotate token**. Rotating the token will invalidate the existing connection token, so any clients using the old token must be updated. Confirm by clicking **Rotate token** again.

* Choose **Option 1 (Authorization header — Recommended)** and **copy the token** from the **Token** field. This value is the `zapier_token` parameter required when deploying the lab using `uv run deploy`.

    <img src="./zapier-screenshots/7.png" alt="Streamable HTTP Token" width="50%" />

The endpoint `https://mcp.zapier.com/api/v1/connect` is the same for all Zapier MCP servers - you only need to copy the token. You will enter this value as the `zapier_token` when deploying labs with `uv run deploy` later.

## :white_check_mark: Checklist

- [ ] Created MCP server and chose "Other" as the MCP client ([step 2](#step-2))
- [ ] Added  **`Webhooks by Zapier: GET`** , **`Webhooks by Zapier: Custom Request`** , and **`Gmail: Send Email`** tools ([step 3](#step-3))
- [ ] Copied the **Streamable HTTP token** from the connection credentials dialog ([step 4](#step-4))
- [ ] Saved the token somewhere safe, to enter it later during deployment ([step 4](#step-4))

## Navigation

- **← Back to Overview**: [Main README](../../README.md)
- **→ Lab1**: [Price Matching Orders With MCP Tool Calling](../../LAB1-Walkthrough.md)
- **→ Lab3**: [Agentic Fleet Management](../../LAB3-Walkthrough.md)
- **→ MongoDB Setup**: [MongoDB Atlas Setup Guide](./MongoDB-Setup.md)
