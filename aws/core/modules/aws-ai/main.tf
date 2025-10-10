locals {
  common_tags = {
    Owner       = var.owner_email
    Project     = "https://github.com/confluentinc/quickstart-streaming-agents"
    Environment = var.confluent_environment_id
    ManagedBy   = "Terraform"
    LocalPath   = var.project_root_path
  }
}

resource "aws_iam_user" "bedrock_user" {
  name = "bedrock-user-${var.random_id}"
  tags = local.common_tags
}

resource "aws_iam_access_key" "bedrock_user_key" {
  user = aws_iam_user.bedrock_user.name
}

resource "aws_iam_policy" "bedrock_policy" {
  name = "bedrock-policy-${var.random_id}"
  tags = local.common_tags

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

resource "aws_iam_user_policy_attachment" "bedrock_user_policy" {
  user       = aws_iam_user.bedrock_user.name
  policy_arn = aws_iam_policy.bedrock_policy.arn
}

resource "confluent_flink_connection" "bedrock_connection" {
  organization {
    id = var.confluent_organization_id
  }
  environment {
    id = var.confluent_environment_id
  }
  compute_pool {
    id = var.confluent_compute_pool_id
  }
  principal {
    id = var.confluent_service_account_id
  }
  rest_endpoint = var.confluent_flink_rest_endpoint
  credentials {
    key    = var.confluent_flink_api_key_id
    secret = var.confluent_flink_api_key_secret
  }

  display_name   = "llm-textgen-connection"
  type           = "BEDROCK"
  endpoint       = "https://bedrock-runtime.${var.cloud_region}.amazonaws.com/model/${var.model_prefix}.anthropic.claude-3-7-sonnet-20250219-v1:0/invoke"
  aws_access_key = aws_iam_access_key.bedrock_user_key.id
  aws_secret_key = aws_iam_access_key.bedrock_user_key.secret

  depends_on = [
    aws_iam_user_policy_attachment.bedrock_user_policy,
    var.confluent_flink_api_key_resource,
    var.confluent_role_binding_resource
  ]

  lifecycle {
    create_before_destroy = false
  }
}

resource "confluent_flink_connection" "bedrock_embedding_connection" {
  organization {
    id = var.confluent_organization_id
  }
  environment {
    id = var.confluent_environment_id
  }
  compute_pool {
    id = var.confluent_compute_pool_id
  }
  principal {
    id = var.confluent_service_account_id
  }
  rest_endpoint = var.confluent_flink_rest_endpoint
  credentials {
    key    = var.confluent_flink_api_key_id
    secret = var.confluent_flink_api_key_secret
  }

  display_name   = "llm-embedding-connection"
  type           = "BEDROCK"
  endpoint       = "https://bedrock-runtime.${var.cloud_region}.amazonaws.com/model/amazon.titan-embed-text-v1/invoke"
  aws_access_key = aws_iam_access_key.bedrock_user_key.id
  aws_secret_key = aws_iam_access_key.bedrock_user_key.secret

  depends_on = [
    aws_iam_user_policy_attachment.bedrock_user_policy,
    var.confluent_flink_api_key_resource,
    var.confluent_role_binding_resource
  ]

  lifecycle {
    create_before_destroy = false
  }
}
