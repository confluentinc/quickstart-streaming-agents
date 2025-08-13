# AWS Bedrock Configuration (Bare minimum - no logging)
# AWS Bedrock is a fully managed service, no resources to create
# Users just need to use the Bedrock API with their AWS credentials
# Model: us.anthropic.claude-3-7-sonnet-20250219-v1:0 (Sonnet 3.7)

# Determine model prefix based on region
locals {
  model_prefix = length(regexall("^us-", var.cloud_region)) > 0 ? "us" : (length(regexall("^eu-", var.cloud_region)) > 0 ? "eu" : "apac")
}

# AWS IAM User for Bedrock access
resource "aws_iam_user" "bedrock_user" {
  count = local.cloud_provider == "AWS" ? 1 : 0
  name  = "bedrock-user-${random_id.resource_suffix.hex}"
}

# AWS IAM Access Key for Bedrock user
resource "aws_iam_access_key" "bedrock_user_key" {
  count = local.cloud_provider == "AWS" ? 1 : 0
  user  = aws_iam_user.bedrock_user[0].name
}

# AWS IAM Policy for Bedrock permissions
resource "aws_iam_policy" "bedrock_policy" {
  count = local.cloud_provider == "AWS" ? 1 : 0
  name  = "bedrock-policy-${random_id.resource_suffix.hex}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach policy to user
resource "aws_iam_user_policy_attachment" "bedrock_user_policy" {
  count      = local.cloud_provider == "AWS" ? 1 : 0
  user       = aws_iam_user.bedrock_user[0].name
  policy_arn = aws_iam_policy.bedrock_policy[0].arn
}

# Azure OpenAI Configuration
resource "azurerm_resource_group" "openai_rg" {
  count    = local.cloud_provider == "AZURE" ? 1 : 0
  name     = "rg-openai-${random_id.resource_suffix.hex}"
  location = var.cloud_region
}

resource "azurerm_cognitive_account" "openai_account" {
  count               = local.cloud_provider == "AZURE" ? 1 : 0
  name                = "openai-${random_id.resource_suffix.hex}"
  location            = azurerm_resource_group.openai_rg[0].location
  resource_group_name = azurerm_resource_group.openai_rg[0].name
  kind                = "OpenAI"
  sku_name            = "S0"
  public_network_access_enabled = true 
  custom_subdomain_name = "openai-${random_id.resource_suffix.hex}"
}

resource "azurerm_cognitive_deployment" "openai_deployment" {
  count               = local.cloud_provider == "AZURE" ? 1 : 0
  name                = "gpt4-deployment-${random_id.resource_suffix.hex}"
  cognitive_account_id = azurerm_cognitive_account.openai_account[0].id
  model {
    format  = "OpenAI"
    name    = "gpt-4.1"
  }
  scale {
    type = "GlobalStandard"
    capacity = 100
  }
}
