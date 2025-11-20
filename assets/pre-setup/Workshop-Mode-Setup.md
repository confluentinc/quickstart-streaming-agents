# Workshop Mode Setup Guide

Workshop mode allows participants to deploy the Real-Time Context Engine using shared cloud AI credentials without requiring full infrastructure permissions or cloud accounts.

**Workflow:**
1. **Before Workshop**: Organizer creates cloud AI credentials
2. **During Workshop**: Participants run `python deploy.py --workshop` and enter shared credentials
3. **After Workshop**: Organizer immediately revokes credentials

---

# AWS Bedrock Setup

## Required Models

Bedrock model access must be enabled at the AWS account level:
- **Claude 3.7 Sonnet** (`us.anthropic.claude-3-7-sonnet-20250219-v1:0`)
- **Amazon Titan Embeddings** (`amazon.titan-embed-text-v1`)

Enable in AWS Console → Bedrock → Model access before creating workshop credentials.

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
- Access keys valid for workshop
- `WORKSHOP_CREDENTIALS.md` file with participant instructions

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

2. **Run in workshop mode**
   ```bash
   python deploy.py --workshop
   ```

3. **Enter credentials when prompted**
   - Cloud provider: Select **aws**
   - AWS Access Key ID: `<provided-by-organizer>`
   - AWS Secret Access Key: `<provided-by-organizer>`
   - AWS Region: `us-east-1` (the *only* region supported in Workshop Mode)

---

# Azure OpenAI Setup

## Required Model Deployments

Your Azure OpenAI resource **must** have deployments with these **exact names**:
- **`gpt-4o`** (GPT-4o model for text generation)
- **`text-embedding-3-large`** (text-embedding-3-large model for embeddings)

**Critical**: Deployment names must match exactly. If you have different names, create new deployments with these exact names (you can have multiple deployments of the same model).

### Create Model Deployments

Azure Portal → Your Azure OpenAI resource → Deployments → Create new deployment:
1. Deploy **GPT-4o**: Model = `gpt-4o`, Deployment name = **exactly** `gpt-4o`
2. Deploy **Embeddings**: Model = `text-embedding-3-large`, Deployment name = **exactly** `text-embedding-3-large`

## For Organizers

### Setup Workflow

1. **Run Regular Terraform Deployment**
   ```bash
   uv run deploy
   ```
   Select Azure as cloud provider and complete the full deployment.

2. **Get Credentials from Terraform Output**
   After deployment completes, Terraform outputs the Azure OpenAI credentials:
   - Azure OpenAI Endpoint (e.g., `https://YOUR_INSTANCE.openai.azure.com`)
   - Azure OpenAI API Key

3. **Share Credentials with Participants**
   Provide participants with:
   - Azure OpenAI Endpoint
   - Azure OpenAI API Key
   - **Do not commit to Git or share publicly**

4. **After Workshop - Regenerate Keys**, or run `uv run destroy` to destroy all resources, including keys.
   Azure Portal → Your Azure OpenAI resource → Keys and Endpoint → Regenerate Key
   
   - This **immediately invalidates** the old key
   - Workshop participants can no longer access the resource

## For Participants

1. **Clone repository**
   ```bash
   git clone https://github.com/confluentinc/quickstart-streaming-agents
   cd quickstart-streaming-agents
   ```

2. **Run in workshop mode**
   ```bash
   python deploy.py --workshop
   ```

3. **Enter credentials when prompted**
   - Cloud provider: Select **azure**
   - Azure OpenAI Endpoint: `<provided-by-organizer>`
   - Azure OpenAI API Key: `<provided-by-organizer>`
   - Confluent Cloud credentials: Your own Confluent Cloud API keys

## Troubleshooting

**Error: "Model deployment 'gpt-4o' not found"**
- Azure resource is missing deployment named exactly `gpt-4o`
- Create deployment with exact name in Azure Portal

**Error: "Model deployment 'text-embedding-3-large' not found"**

- Azure resource is missing deployment named exactly `text-embedding-3-large`
- Create deployment with exact name in Azure Portal

**Error: "Access denied" or "Invalid API key"**
- API key is incorrect or was regenerated
- Get fresh key from Azure Portal → Keys and Endpoint

**Error: "Endpoint URL format incorrect"**
- Endpoint must be: `https://YOUR_INSTANCE.openai.azure.com`
- Do NOT include paths like `/openai/deployments/...`

## Security Notes

**For Organizers:**
- Generate credentials just before workshop, revoke immediately after
- Don't reuse the same keys across workshops
- Set up billing alerts for cost monitoring
- Distribute credentials via secure channels (never email/Slack)

**For Participants:**
- Never commit credentials to Git (add `credentials.env` to `.gitignore`)
- Delete credentials from your machine after workshop
- Use only the credentials provided by organizer

---

## Common Issues

**AWS: "ResourceNotFoundException: Could not find a model"**
- Bedrock model access not enabled in AWS account
- AWS Console → Bedrock → Model access → Request access to Claude 3.7 Sonnet and Titan Embeddings

**AWS: "AccessDeniedException"**
- IAM policy not attached correctly
- Verify with: `aws iam get-user-policy --user-name workshop-bedrock-user --policy-name BedrockInvokeOnly`

**AWS: "The security token included in the request is invalid"**
- Keys revoked or copied incorrectly
- Generate new keys and re-copy carefully (no spaces/newlines)
