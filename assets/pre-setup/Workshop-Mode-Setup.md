# Workshop Mode Setup Guide

Workshop mode allows participants to deploy the Real-Time Context Engine using shared cloud AI credentials without requiring full infrastructure permissions or cloud accounts.

**Workflow:**
1. **Before Workshop**: Organizer creates cloud AI credentials with `uv run workshop-keys create`
2. **During Workshop**: Participants run `uv run deploy --workshop` and enter Bedrock API key and secret
3. **After Workshop**: Organizer immediately revokes credentials with  `uv run workshop-keys destroy`

> [!NOTE]
>
> Workshop Mode for Azure is not ready yet, and will fail if you attempt to run it.

---

# AWS Bedrock Setup

## Required Models

Bedrock model access must be enabled at the AWS account level:
- **Claude Sonnet 4.5** (`us.anthropic.claude-sonnet-4-5-20250929-v1:0`)
- **Amazon Titan Embeddings** (`amazon.titan-embed-text-v1`)

⚠️To access Claude Sonnet 4.5 you must request access to the model by filling out an **Anthropic use case form** (or someone in your org must have previously done so) for your cloud region (`us-east-1`). To do so, visit the [Model Catalog](https://console.aws.amazon.com/bedrock/home#/model-catalog), select **Claude Sonnet 4.5** and open it it in the **Playground**, then send a message in the chat - the form will appear automatically. ⚠️

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
- `WORKSHOP_CREDENTIALS.md` file with keys and participant instructions, saved automatically in the root directory

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
   uv run deploy --workshop
   ```
   
3. **Enter credentials when prompted**
   - Cloud provider: Select **aws**
   - AWS Access Key ID: `<provided-by-organizer>`
   - AWS Secret Access Key: `<provided-by-organizer>`
   - AWS Region: `us-east-1` (the *only* region supported in Workshop Mode)

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
- Share your SSE endpoint directly with attendees rather than having them sign up individually
- This saves significant workshop time and reduces friction
- Attendees can still enter their own email in the query to receive notifications
- Free trial offers ~500 tool calls in first 2 weeks; each order uses 2 tool calls
- ⚠️ Don't use this approach for groups larger than 10-15 until confirming Zapier rate limits

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
