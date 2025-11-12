## Zapier Remote MCP Server Setup

Create a Zapier MCP server for tool calling:

### A. Create free Zapier Account

Sign up at [zapier.com](https://zapier.com/sign-up) and verify your email.

### B. Create MCP Server

Visit [mcp.zapier.com](https://mcp.zapier.com/mcp/servers), choose "Other" as MCP Client, and create your server.



<img src="./zapier-screenshots/3.png" alt="Create MCP Server" width="100%" />


### C. Add Tools

Add these tools to your MCP server:

- **Webhooks by Zapier: GET** and **Custom Request** tools
- **[ONLY FOR LAB 1]Gmail: Send Email** tool (authenticate via SSO)


    <img src="./zapier-screenshots/4.png" alt="Add Tools" width="100%" />


### D. Get SSE Endpoint URL

Click **"Connect",** choose **"Other"** for your client, then change transport to **"SSE Endpoint"**, and **copy the URL.** This is the `zapier_sse_endpoint` you will need to enter when deploying the lab with `uv run deploy`.



<img src="./zapier-screenshots/7.png" alt="SSE Endpoint" width="100%" />



