# Required: Your project name (used for resource naming)
prefix = "streaming-agents"

# Required: Choose your cloud provider
cloud_provider = "AWS"  # or "azure"

# Required: Choose your region (see supported regions below)
cloud_region = "us-east-1"

# Required: Confluent Cloud credentials (or use environment variables)
confluent_cloud_api_key = "your-confluent-api-key"
confluent_cloud_api_secret = "your-confluent-api-secret"

# Required: Zapier MCP SSE Endpoint required for tool calling. Get from Zapier UI and should look like this
ZAPIER_SSE_ENDPOINT="https://mcp.zapier.com/api/mcp/s/<<long-API-key>>/sse"