#!/bin/bash

set -e

# This script creates a dedicated service account and an API key for Terraform,
# and automatically writes them to the core terraform.tfvars file and a markdown reference file.

TFVARS_FILE="terraform/core/terraform.tfvars"
CREDENTIALS_MD_FILE="confluent_api_keys.md"

# 1. Check for or create a Service Account
echo "Checking for service account 'TerraformAdminSA'..."
SERVICE_ACCOUNT_ID=$(confluent iam service-account list | grep "TerraformAdminSA" | awk '{print $1}' || true)

if [ -n "$SERVICE_ACCOUNT_ID" ]; then
    echo "✅ Service account 'TerraformAdminSA' already exists with ID: $SERVICE_ACCOUNT_ID"
else
    echo "Service account not found. Creating a new one..."
    SA_CREATE_OUTPUT=$(confluent iam service-account create "TerraformAdminSA" --description "Service Account for Terraform automation")
    SERVICE_ACCOUNT_ID=$(echo "$SA_CREATE_OUTPUT" | grep -o 'sa-[a-zA-Z0-9]*')
    if [ -z "$SERVICE_ACCOUNT_ID" ]; then
        echo "Error: Could not create or parse the service account."
        exit 1
    fi
    echo "✅ Service Account created with ID: $SERVICE_ACCOUNT_ID"
fi

# 2. Assign the OrganizationAdmin role to the Service Account
echo "Assigning the 'OrganizationAdmin' role..."
# The role binding might already exist, so we ignore errors here.
confluent iam rbac role-binding create --principal "User:$SERVICE_ACCOUNT_ID" --role "OrganizationAdmin" || echo "Role binding may already exist. Continuing..."
echo "✅ Role assignment step completed."

# 3. Create the API Key for the Service Account
echo "Creating the API Key and Secret..."
API_KEY_OUTPUT=$(confluent api-key create --service-account "$SERVICE_ACCOUNT_ID" --resource "cloud" --description "Terraform Bootstrap Key")

API_KEY=$(echo "$API_KEY_OUTPUT" | grep "API Key" | awk '{print $5}')
API_SECRET=$(echo "$API_KEY_OUTPUT" | grep "API Secret" | awk '{print $5}')

# Basic validation
if [ ${#API_KEY} -lt 16 ] || [ ${#API_SECRET} -lt 16 ]; then
    echo "Error: Parsed API Key or Secret is too short. Could not correctly parse credentials."
    echo "Raw output was:"
    echo "$API_KEY_OUTPUT"
    exit 1
fi

# 4. Update the credentials in the terraform.tfvars file
echo "Updating credentials in $TFVARS_FILE..."

if [ ! -f "$TFVARS_FILE" ]; then
    echo "Error: $TFVARS_FILE not found. Please ensure the terraform configuration exists."
    exit 1
fi

# Create a backup
cp "$TFVARS_FILE" "$TFVARS_FILE.backup"

# Update the API key and secret in the existing file
sed -i.tmp "s/^confluent_cloud_api_key[[:space:]]*=.*$/confluent_cloud_api_key = \"$API_KEY\"/" "$TFVARS_FILE"
sed -i.tmp "s/^confluent_cloud_api_secret[[:space:]]*=.*$/confluent_cloud_api_secret = \"$API_SECRET\"/" "$TFVARS_FILE"

# Remove the temporary file created by sed
rm -f "$TFVARS_FILE.tmp"

echo "✅ Updated existing terraform.tfvars with new API credentials"

# 5. Write the credentials to the markdown file for reference
echo "Writing credentials to $CREDENTIALS_MD_FILE..."

cat > "$CREDENTIALS_MD_FILE" << EOL
# Confluent Cloud API Keys

## Service Account Information
- **Service Account ID**: $SERVICE_ACCOUNT_ID
- **Service Account Name**: TerraformAdminSA
- **Role**: OrganizationAdmin

## API Credentials
- **API Key**: $API_KEY
- **API Secret**: $API_SECRET

## Usage
These credentials have been automatically written to:
- \`$TFVARS_FILE\` (for Terraform automation)
- \`$CREDENTIALS_MD_FILE\` (for reference)

> **Security Note**: Keep these credentials secure. The API Secret provides full access to your Confluent Cloud organization.

Generated on: $(date)
EOL

echo "✅ Success! Credentials have been written to:"
echo "  - $TFVARS_FILE (for Terraform)"
echo "  - $CREDENTIALS_MD_FILE (for reference)"
echo "You are now ready to run Terraform."
