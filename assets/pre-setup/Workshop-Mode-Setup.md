# Workshop Mode Setup Guide

Workshop mode allows participants to deploy the Streaming Agents quickstart using shared cloud AI credentials without requiring an AWS account or Azure subscription.

**Workflow:**
1. **Before Workshop**: Organizer creates cloud AI credentials with `uv run workshop-keys create`
2. **During Workshop**: Participants run `uv run deploy`, select their cloud provider, and enter LLM credentials
3. **After Workshop**: Organizer immediately revokes credentials with `uv run workshop-keys destroy`

---

# AWS Bedrock Setup

## Required Models

Bedrock model access must be enabled at the AWS account level:
- **Claude Sonnet 4.5** (`us.anthropic.claude-sonnet-4-5-20250929-v1:0`)
- **Amazon Titan Embeddings** (`amazon.titan-embed-text-v1`)

> [!WARNING]
>
> To access Claude Sonnet 4.5 you must request access to the model by filling out an **Anthropic use case form** (or someone in your org must have previously done so) for your cloud region (`us-east-1`). To do so, visit the [Model Catalog](https://console.aws.amazon.com/bedrock/home#/model-catalog), select **Claude Sonnet 4.5** and open it it in the **Playground**, then send a message in the chat - the form will appear automatically.

## For Organizers

### Option 1: Automated (Recommended)

Use the workshop key manager tool:

```bash
# Create credentials
uv run workshop-keys create

# After workshop - revoke credentials
uv run workshop-keys destroy
```

This creates:
- IAM user `workshop-bedrock-user` with Bedrock-only permissions
- Bedrock API keys
- `API-KEYS-AWS.md` file with API keys and participant instructions, saved automatically in the root directory and auto-populated in `credentials.env`

### Option 2: Manual (AWS Console)

1. **Create IAM User**
   - AWS Console → IAM → Users → Create user
   - Username: `workshop-bedrock-user`
   - No console access needed

2. **Attach Policy**
   - Attach policies directly → Create policy → JSON:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
       "Resource": "*"
     }]
   }
   ```

3. **Create Access Keys**
   - User → Security credentials → Create access key
   - Use case: Third-party service
   - Save both Access Key ID and Secret Access Key

4. **After Workshop - Revoke**
   - User → Security credentials → Access keys → Delete

## For Participants

1. **Clone repository**
   ```bash
   git clone https://github.com/confluentinc/quickstart-streaming-agents
   cd quickstart-streaming-agents
   ```

2. **Run deployment**

   ```bash
   uv run deploy
   ```

3. **Enter credentials when prompted**
   - Cloud provider: Select **aws**
   - Region: `us-east-1` (by default)
   - Confluent Cloud API key and secret (auto-generated if desired)
   - AWS Access Key ID: `<auto-filled if generated with uv run workshop-keys create>`
   - AWS Secret Access Key: `<auto-filled if generated with uv run workshop-keys create>`

---

# Azure OpenAI Setup

## Required Models

Azure OpenAI deployments must be created in the organizer's Azure subscription:
- **gpt-5-mini** (Chat completions, version: 2025-08-07)
- **text-embedding-ada-002** (Embeddings, version: 2)

> [!WARNING]
>
> Azure workshop is auto-deployed in **eastus2** region because the hardcoded MongoDB clusters for Lab2 and Lab3 are located in eastus2. Using any other region will cause MongoDB connection failures.

## For Organizers

### Option 1: Automated (Recommended)

Use the workshop key manager tool:

```bash
# Create credentials
uv run workshop-keys create

# After workshop - revoke credentials
uv run workshop-keys destroy
```

This creates:
- Resource group with unique ID (e.g., `rg-workshop-openai-abc123`)
- Azure Cognitive Services account for OpenAI
- Model deployments for `gpt-5-mini` and `text-embedding-ada-002`
- `API-KEYS-AZURE.md` file with endpoint, API key, and participant instructions, saved automatically in the root directory and auto-populated in `credentials.env`

**Prerequisites:**

- Azure CLI installed and authenticated (`az login`)
- Active Azure subscription with OpenAI service enabled
- Permissions to create resource groups and Cognitive Services

### Option 2: Manual (Azure Portal)

1. **Create Resource Group**
   - Azure Portal → Resource Groups → Create
   - Name: `rg-workshop-openai-<unique-id>`
   - Region: **eastus2** (required for workshop mode)

2. **Create Cognitive Services Account**
   - Azure Portal → Create a resource → Azure OpenAI
   - Resource group: Use the one created above
   - Region: **eastus2**
   - Name: `workshop-openai-<unique-id>`
   - Pricing tier: Standard S0

3. **Create Model Deployments**
   - Navigate to Azure OpenAI Studio
   - Deployments → Create new deployment:
     - **Deployment 1:**
       - Model: gpt-5-mini
       - Version: 2025-08-07
       - Deployment name: `gpt-5-mini`
       - Capacity: 50 TPM (adjust based on workshop size)
     - **Deployment 2:**
       - Model: text-embedding-ada-002
       - Version: 2
       - Deployment name: `text-embedding-ada-002`
       - Capacity: 120 TPM

4. **Get Credentials**
   - Keys and Endpoint → Copy Key 1 and Endpoint URL

5. **After Workshop - Revoke**
   - Delete the model deployments
   - Optionally delete the entire resource group

## For Participants

1. **Clone repository**
   ```bash
   git clone https://github.com/confluentinc/quickstart-streaming-agents
   cd quickstart-streaming-agents
   ```

2. **Run deployment**
   ```bash
   uv run deploy
   ```

3. **Enter credentials when prompted**
   - Cloud provider: Select **azure**
   - Region: **eastus2** (auto-selected for workshop mode)
   - Confluent Cloud API key and secret (auto-generated if desired)
   - Azure OpenAI Endpoint: `<auto-filled if generated with uv run workshop-keys create>`
   - Azure OpenAI API Key: `<auto-filled if generated with uv run workshop-keys create>`

---

## Presenter Tips

### Before the Workshop

**Enable Bedrock Models**

- Ensure Claude models are properly activated in your AWS account beforehand
- If models aren't activated, all calls will fail with a 403 error (not immediately obvious what the issue is)
- Request model access well in advance to avoid delays

**Create Dedicated IAM Credentials**
- Create your own IAM role and temporary API keys specifically for the demo
- For proper scoping and security setup, consult with your security team (e.g., David Marsh has created properly scoped credentials for previous demos)
- Generate credentials the day before the workshop

**Zapier Setup (For Small Groups)**
- For groups of 10-15 people or fewer, create a free Zapier account 1-2 days beforehand
- Share your Streamable HTTP token directly with attendees rather than having them sign up individually
- This saves significant workshop time and reduces friction
- Attendees can still enter their own email in the query to receive notifications
- Free trial offers ~500 tool calls in first 2 weeks; each order uses 2 tool calls
- ⚠️ Don't use this approach for groups larger than 10-15 until confirming Zapier rate limits
- Note: SSE endpoints are now deprecated by Zapier - use Streamable HTTP connections instead

### During the Workshop

**Test Queries**

- Use the test queries in Lab 1 to isolate issues if LLMs aren't responding as expected
- These queries help verify each component is working correctly

**Don't Forget Email Addresses**
- Remind participants (and yourself!) to add their email address to the big query in Lab 1
- Easy to forget as everyone naturally wants to copy/paste the query quickly

### Troubleshooting

**Restarting Data Generation**
- If you need to restart data generation for any reason, drop all tables first before restarting
- Restarting without dropping tables can cause duplicate customer IDs for different customers
- This leads to duplicate emails and other downstream issues

---

## Security Notes

**For Organizers:**
- Generate credentials the day before the workshop, revoke immediately after
- Don't reuse the same keys across workshops
- Distribute credentials via secure channels

**For Participants:**

- Never commit credentials to Git
- Delete credentials from your machine after workshop (tear down resources with `uv run destroy`, then run`rm credentials.env`)

---

## Common Issues

**AWS: "ResourceNotFoundException: Could not find a model"**

- Bedrock model access not enabled in AWS account
- ⚠️To access Claude Sonnet 4.5 you must request access to the model by filling out an **Anthropic use case form** (or someone in your org must have previously done so) for your cloud region. To do so, visit the [Model Catalog](https://console.aws.amazon.com/bedrock/home#/model-catalog), select **Claude Sonnet 4.5** and open it it in the **Playground**, then send a message in the chat - the form will appear automatically. ⚠️

**AWS: "AccessDeniedException"**

- IAM policy not attached correctly
- Verify with: `aws iam get-user-policy --user-name workshop-bedrock-user --policy-name BedrockInvokeOnly`

**AWS: "The security token included in the request is invalid"**
- Keys revoked or copied incorrectly
- Generate new keys and re-copy carefully (no spaces/newlines)
