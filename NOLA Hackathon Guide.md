### 1. [Sign up for Confluent Cloud](https://www.confluent.io/get-started/?utm_campaign=tm.pmm_cd.q4fy25-quickstart-streaming-agents&utm_source=github&utm_medium=demo) and add a credit card

### 2. [Sign up for Zapier free account](https://zapier.com/sign-up), create remote MCP server, and add tools

For step-by-step instructions with screenshots, visit [LAB1-Walkthrough.md](./LAB1-Walkthrough.md#zapier-mcp-server-setup).
- Add: `Gmail` send email tool (click "Configure" then sign on with SSO), and `Zapier Webhooks: GET` tools.
- Choose `Other` as MCP client, click `Connect` at the top, change Transport to `SSE`, then copy and save the server URL - you'll enter that in the next step as `zapier_sse_endpoint`.

### 3. Run `uv run deploy`

Follow instructions in [LAB1-Walkthrough.md](./LAB1-Walkthrough.md) to deploy the lab.

------

### **7. Clean up afterward**

When you’re done, don't forget to:

```uv run destroy
uv run destroy

confluent logout
```

