# Workshop Mode IAM Setup Guide

This guide explains how to create AWS credentials for workshop participants to use the Real-Time Context Engine in **workshop mode** without requiring full AWS infrastructure permissions.

## Overview

Workshop mode allows participants to use pre-deployed infrastructure with their own AWS Bedrock credentials. The workflow is designed for ephemeral, time-limited access:

1. **Day Before Workshop**: Generate fresh AWS access keys
2. **During Workshop**: Participants use keys to invoke Bedrock models via Confluent Flink
3. **After Workshop**: Revoke/delete keys immediately

## Frequently Asked Questions

### Can I reuse the same IAM User for multiple workshops?

**Yes!** This is the recommended approach:
- Create one IAM user (e.g., `workshop-bedrock-user`) and keep it
- Generate new access keys before each workshop
- Revoke old keys after each workshop
- AWS allows up to 2 active access keys per user, so you can create new ones before deleting old ones for zero-downtime transitions

### Do participants need to fill out the Bedrock model access form?

**No!** Bedrock model access is granted at the **AWS account level**, not per IAM user:
- If anyone in your organization has already requested and been approved for Claude model access in your AWS account, all IAM users in that account can use it (with proper permissions)
- Participants only need the `bedrock:InvokeModel` permission
- No need to fill out use case forms for each workshop or participant

## What Permissions Are Needed?

Workshop mode credentials are **only used for Bedrock model invocation**. No other AWS services are accessed:
- ✅ AWS Bedrock Runtime (invoke models)
- ❌ NO IAM operations
- ❌ NO Lambda, API Gateway, DynamoDB, or other services

### Models Used
- **Claude 3.7 Sonnet** (text generation)
- **Amazon Titan Embeddings** (embeddings)

---

## IAM Policy Options

Choose one of these policies based on your security requirements:

### Option 1: Simple Wildcard Policy (Recommended for Workshops)

Allows invocation of all Bedrock models:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

### Option 2: Restrictive Policy (Specific Models Only)

Limits access to only Claude 3.7 Sonnet and Titan Embeddings:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "arn:aws:bedrock:*::foundation-model/eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "arn:aws:bedrock:*::foundation-model/apac.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v1"
      ]
    }
  ]
}
```

---

## Setup Instructions (AWS CLI)

Use these commands if you're already authenticated to AWS CLI.

### First-Time Setup (Create IAM User)

```bash
# 1. Create IAM user (one-time, reuse for future workshops)
aws iam create-user --user-name workshop-bedrock-user

# 2. Create the IAM policy file
cat > workshop-bedrock-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# 3. Attach the inline policy to the user
aws iam put-user-policy \
  --user-name workshop-bedrock-user \
  --policy-name BedrockInvokeOnly \
  --policy-document file://workshop-bedrock-policy.json

# 4. Verify the policy was attached
aws iam get-user-policy \
  --user-name workshop-bedrock-user \
  --policy-name BedrockInvokeOnly
```

### Before Each Workshop (Generate Keys)

```bash
# Generate new access keys for the workshop
aws iam create-access-key --user-name workshop-bedrock-user

# Save the output - you'll need both AccessKeyId and SecretAccessKey
# Output looks like:
# {
#     "AccessKey": {
#         "UserName": "workshop-bedrock-user",
#         "AccessKeyId": "AKIA...",
#         "SecretAccessKey": "wJalrXUtnFEMI...",
#         "Status": "Active",
#         "CreateDate": "2025-11-12T..."
#     }
# }
```

**Important**: Save both the `AccessKeyId` and `SecretAccessKey` - the secret is only shown once!

### After Each Workshop (Revoke Keys)

```bash
# 1. List all access keys for the user
aws iam list-access-keys --user-name workshop-bedrock-user

# 2. Delete the access key (replace ACCESS_KEY_ID with actual key)
aws iam delete-access-key \
  --user-name workshop-bedrock-user \
  --access-key-id ACCESS_KEY_ID
```

### Optional: Delete User Entirely

If you no longer need the user:

```bash
# 1. Delete all access keys first
aws iam list-access-keys --user-name workshop-bedrock-user
aws iam delete-access-key --user-name workshop-bedrock-user --access-key-id <KEY_ID>

# 2. Delete inline policies
aws iam delete-user-policy --user-name workshop-bedrock-user --policy-name BedrockInvokeOnly

# 3. Delete the user
aws iam delete-user --user-name workshop-bedrock-user
```

---

## Setup Instructions (AWS Console/UI)

### First-Time Setup (Create IAM User)

1. **Open IAM Console**
   - Go to [AWS Console](https://console.aws.amazon.com/)
   - Navigate to **IAM** service (search "IAM" in top search bar)

2. **Create IAM User**
   - Click **Users** in left sidebar
   - Click **Create user** button
   - **User name**: `workshop-bedrock-user`
   - **Do NOT** select "Provide user access to AWS Management Console" (we only need programmatic access)
   - Click **Next**

3. **Set Permissions**
   - Select **Attach policies directly**
   - Click **Create policy** (opens new tab)
   - In the new tab:
     - Click **JSON** tab
     - Paste one of the IAM policies from above (Option 1 or 2)
     - Click **Next**
     - **Policy name**: `BedrockInvokeOnlyPolicy`
     - Click **Create policy**
   - Return to previous tab, click refresh button
   - Search for `BedrockInvokeOnlyPolicy` and check the box
   - Click **Next**

4. **Review and Create**
   - Review settings
   - Click **Create user**

### Before Each Workshop (Generate Keys)

1. **Navigate to User**
   - Go to **IAM** → **Users**
   - Click on `workshop-bedrock-user`

2. **Create Access Keys**
   - Click **Security credentials** tab
   - Scroll to **Access keys** section
   - Click **Create access key**
   - Select **Third-party service** as use case
   - Check confirmation box
   - Click **Next**
   - (Optional) Add description tag: `Workshop-2025-11-12`
   - Click **Create access key**

3. **Download/Save Keys**
   - **Important**: Copy both **Access key ID** and **Secret access key**
   - Click **Download .csv file** (backup)
   - **The secret key is only shown once!**
   - Click **Done**

### After Each Workshop (Revoke Keys)

1. **Navigate to User**
   - Go to **IAM** → **Users**
   - Click on `workshop-bedrock-user`

2. **Delete Access Keys**
   - Click **Security credentials** tab
   - Scroll to **Access keys** section
   - Find the key you want to delete
   - Click **Actions** → **Deactivate** (makes key immediately unusable)
   - Click **Actions** → **Delete**
   - Confirm deletion

### Optional: Delete User Entirely

1. **Navigate to User**
   - Go to **IAM** → **Users**
   - Check box next to `workshop-bedrock-user`
   - Click **Delete** button

2. **Confirm Deletion**
   - Type the username to confirm
   - Click **Delete**

---

## Workshop Workflow Timeline

### Day Before Workshop

1. Generate fresh access keys (CLI or Console instructions above)
2. Test the keys work:
   ```bash
   export AWS_ACCESS_KEY_ID="AKIA..."
   export AWS_SECRET_ACCESS_KEY="wJalrXUt..."
   export AWS_DEFAULT_REGION="us-east-1"  # or your region

   # Test with AWS CLI
   aws bedrock-runtime invoke-model \
     --model-id us.anthropic.claude-3-7-sonnet-20250219-v1:0 \
     --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":15000,"messages":[{"role":"user","content":"Hello"}]}' \
     --region us-east-1 \
     output.json
   ```
3. Save keys securely for distribution to participants

### During Workshop

1. Provide participants with:
   - AWS Access Key ID
   - AWS Secret Access Key
   - AWS Region (e.g., `us-east-1`)
2. Participants run: `python deploy.py --workshop`
3. Script will prompt for the three values above

### After Workshop

1. **Immediately revoke keys** (within 24 hours)
2. Delete access keys via CLI or Console (see instructions above)
3. (Optional) Keep IAM user for next workshop

---

## Security Best Practices

### For Workshop Organizers

1. **Time-Limited Keys**: Generate keys close to workshop time, revoke immediately after
2. **Unique Keys Per Workshop**: Don't reuse the same keys across multiple workshops
3. **Monitor Usage**: Check CloudTrail logs for unexpected Bedrock API calls
4. **Key Distribution**: Use secure channels (password-protected docs, encrypted messages)
5. **Cost Monitoring**: Set up billing alerts for Bedrock usage
6. **Regional Deployment**: Deploy in regions where Bedrock costs are lowest

### For Participants

1. **Don't Commit Keys**: Never commit AWS keys to Git repositories
2. **Local Storage Only**: Keep keys in local config files, not shared drives
3. **Delete After Workshop**: Remove keys from your machine after the workshop
4. **Don't Share**: Each participant should use the same shared keys (provided by organizer)

---

## Troubleshooting

### Error: "User already exists"

**Cause**: IAM user was created previously
**Solution**: Skip user creation, go directly to key generation step

### Error: "ResourceNotFoundException: Could not find a model"

**Cause**: Bedrock model access not enabled in your AWS account
**Solution**: Someone with admin access needs to:
1. Go to AWS Bedrock Console → Model access
2. Request access to Claude 3.7 Sonnet and Titan Embeddings
3. Wait for approval (usually instant for Titan, may take time for Claude)

### Error: "AccessDeniedException"

**Cause**: IAM policy not attached or incorrect permissions
**Solution**:
1. Verify policy is attached: `aws iam get-user-policy --user-name workshop-bedrock-user --policy-name BedrockInvokeOnly`
2. Check policy includes `bedrock:InvokeModel` action
3. Ensure model access is enabled (see above)

### Error: "The security token included in the request is invalid"

**Cause**: Keys are revoked, deleted, or incorrectly copied
**Solution**:
1. Verify keys are still active in IAM Console
2. Re-copy keys carefully (no extra spaces/newlines)
3. Generate new keys if needed

### Keys Work in AWS CLI but Not in Workshop

**Cause**: Regional differences or Confluent Flink connection issues
**Solution**:
1. Ensure you're using the same region in both tests
2. Verify Bedrock is available in your region
3. Check Confluent Flink connection configuration

---

## Additional Resources

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Bedrock Model Access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)
- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [Main README](README.md) - Full project documentation
