## Workshop MCP Server Setup

The workshop uses a shared MCP server hosted by the instructor. You do **not** need to create any external accounts.

Your instructor will provide you with:

- **MCP Server URL** — the SSE endpoint for the workshop MCP server (e.g. `https://52-7-123-45.sslip.io/mcp/sse`)
- **MCP Token** — the bearer token for authenticating with the server

Enter both values when prompted by `uv run deploy`.

### Tools Available

The workshop MCP server exposes the following tools:

- **`http_get`** — Fetches the contents of a URL via HTTP GET
- **`http_request`** — Makes a custom HTTP request (any method, headers, body)
- **`send_email`** — Sends an email via Gmail

## :white_check_mark: Checklist

- [ ] Received MCP Server URL from instructor
- [ ] Received MCP Token from instructor
- [ ] Ready to enter both when `uv run deploy` prompts for them

## Navigation

- **← Back to Overview**: [Main README](../../README.md)
- **→ Lab1**: [Price Matching Orders With MCP Tool Calling](../../LAB1-Walkthrough.md)
- **→ Lab3**: [Agentic Fleet Management](../../LAB3-Walkthrough.md)
- **→ MongoDB Setup**: [MongoDB Atlas Setup Guide](./MongoDB-Setup.md)
