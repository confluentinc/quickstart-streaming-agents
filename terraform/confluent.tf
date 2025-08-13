# Random ID for unique resource names (used for both AWS and Azure)
resource "random_id" "resource_suffix" {
  byte_length = 4
} 

# ------------------------------------------------------
# REGION MAPPING
# ------------------------------------------------------
locals {
  region_mapping = {
    # AWS Regions
    "us-east-1"      = "us-east-1"
    "us-east-2"      = "us-east-2"
    "us-west-1"      = "us-west-1"
    "us-west-2"      = "us-west-2"
    "eu-west-1"      = "eu-west-1"
    "eu-west-2"      = "eu-west-2"
    "eu-central-1"   = "eu-central-1"
    "ap-southeast-1" = "ap-southeast-1"
    "ap-southeast-2" = "ap-southeast-2"
    "ap-northeast-1" = "ap-northeast-1"
    "sa-east-1"      = "sa-east-1"

    # Azure Regions: User-friendly to programmatic names (based on Microsoft list) :contentReference[oaicite:1]{index=1}
    "East US"             = "eastus"
    "East US 2"           = "eastus2"
    "Central US"          = "centralus"
    "North Central US"    = "northcentralus"
    "South Central US"    = "southcentralus"
    "West US"             = "westus"
    "West US 2"           = "westus2"
    "West US 3"           = "westus3"
    "West Central US"     = "westcentralus"
    "Canada Central"      = "canadacentral"
    "Canada East"         = "canadaeast"
    "Brazil South"        = "brazilsouth"
    "Brazil Southeast"    = "brazilsoutheast"    
    "North Europe"        = "northeurope"
    "West Europe"         = "westeurope"
    "France Central"      = "francecentral"
    "France South"        = "francesouth"
    "Germany West Central"= "germanywestcentral"
    "Germany North"       = "germanynorth"       
    "Sweden Central"      = "swedencentral"
    "UK South"            = "uksouth"
    "UK West"             = "ukwest"
    "Norway East"         = "norwayeast"
    "Norway West"         = "norwaywest"          
    "Switzerland North"   = "switzerlandnorth"
    "Switzerland West"    = "switzerlandwest"
    "UAE North"           = "uaenorth"
    "UAE Central"         = "uaecentral"         
    "South Africa North"  = "southafricanorth"
    "South Africa West"   = "southafricawest"    
    "East Asia"           = "eastasia"
    "Southeast Asia"      = "southeastasia"
    "Japan East"          = "japaneast"
    "Japan West"          = "japanwest"
    "Korea Central"       = "koreacentral"
    "Korea South"         = "koreasouth"
    "Central India"       = "centralindia"
    "South India"         = "southindia"
    "West India"          = "westindia"
    "Australia East"      = "australiaeast"
    "Australia Southeast" = "australiasoutheast"
    "Australia Central"   = "australiacentral"
    "Australia Central 2" = "australiacentral2"
    "Chile Central"       = "chilecentral"       

    # Backward-compatible: programmatic names directly
    "eastus"            = "eastus"
    "eastus2"           = "eastus2"
    "centralus"         = "centralus"
    "northcentralus"    = "northcentralus"
    "southcentralus"    = "southcentralus"
    "westus"            = "westus"
    "westus2"           = "westus2"
    "westus3"           = "westus3"
    "westcentralus"     = "westcentralus"
    "canadacentral"     = "canadacentral"
    "canadaeast"        = "canadaeast"
    "brazilsouth"       = "brazilsouth"
    "brazilsoutheast"   = "brazilsoutheast"
    "northeurope"       = "northeurope"
    "westeurope"        = "westeurope"
    "francecentral"     = "francecentral"
    "francesouth"       = "francesouth"
    "germanywestcentral"= "germanywestcentral"
    "germanynorth"      = "germanynorth"
    "swedencentral"     = "swedencentral"
    "uksouth"           = "uksouth"
    "ukwest"            = "ukwest"
    "norwayeast"        = "norwayeast"
    "norwaywest"        = "norwaywest"
    "switzerlandnorth"  = "switzerlandnorth"
    "switzerlandwest"   = "switzerlandwest"
    "uaenorth"          = "uaenorth"
    "uaecentral"        = "uaecentral"
    "southafricanorth"  = "southafricanorth"
    "southafricawest"   = "southafricawest"
    "eastasia"          = "eastasia"
    "southeastasia"     = "southeastasia"
    "japaneast"         = "japaneast"
    "japanwest"         = "japanwest"
    "koreacentral"      = "koreacentral"
    "koreasouth"        = "koreasouth"
    "centralindia"      = "centralindia"
    "southindia"        = "southindia"
    "westindia"         = "westindia"
    "australiaeast"     = "australiaeast"
    "australiasoutheast"= "australiasoutheast"
    "australiacentral"  = "australiacentral"
    "australiacentral2" = "australiacentral2"
    "chilecentral"      = "chilecentral"
  }

  confluent_region = lookup(local.region_mapping, var.cloud_region, var.cloud_region)
  
  # Determine model prefix based on region for AWS Bedrock
  model_prefix = length(regexall("^us-", var.cloud_region)) > 0 ? "us" : (length(regexall("^eu-", var.cloud_region)) > 0 ? "eu" : "apac")
}



# ------------------------------------------------------
# ENVIRONMENT
# ------------------------------------------------------


resource "confluent_environment" "staging" {
  display_name = "${var.prefix}-RIVERRETAIL-${random_id.resource_suffix.hex}"

  stream_governance {
    package = "ADVANCED"
  }
}

# ------------------------------------------------------
# KAFKA Cluster
# ------------------------------------------------------

data "confluent_schema_registry_cluster" "sr-cluster" {
  environment {
    id = confluent_environment.staging.id
  }

  depends_on = [
    confluent_kafka_cluster.standard
  ]
}

# Update the config to use a cloud provider and region of your choice.
# https://registry.terraform.io/providers/confluentinc/confluent/latest/docs/resources/confluent_kafka_cluster
resource "confluent_kafka_cluster" "standard" {
  display_name = "${var.prefix}-RIVERBANK-CLUSTER-${random_id.resource_suffix.hex}"
  availability = "SINGLE_ZONE"
  cloud        = local.cloud_provider
  region       = local.confluent_region
  standard {}
  environment {
    id = confluent_environment.staging.id
  }
}

# ------------------------------------------------------
# SERVICE ACCOUNTS
# ------------------------------------------------------

resource "confluent_service_account" "app-manager" {
  display_name = "${var.prefix}-app-manager-${random_id.resource_suffix.hex}"
  description  = "Service account to manage 'inventory' Kafka cluster"
}

resource "confluent_role_binding" "app-manager-kafka-cluster-admin" {
  principal   = "User:${confluent_service_account.app-manager.id}"
  role_name   = "EnvironmentAdmin"
  crn_pattern = confluent_environment.staging.resource_name  
}


# ------------------------------------------------------
# Flink Compute Pool
# ------------------------------------------------------

resource "confluent_flink_compute_pool" "flinkpool-main" {
  display_name     = "${var.prefix}_standard_compute_pool_${random_id.resource_suffix.hex}"
  cloud            = local.cloud_provider
  region           = local.confluent_region
  max_cfu          = 20
  environment {
    id = confluent_environment.staging.id
  }
}

# ------------------------------------------------------
# API Keys
# ------------------------------------------------------

resource "confluent_api_key" "app-manager-kafka-api-key" {
  display_name = "app-manager-kafka-api-key"
  description  = "Kafka API Key that is owned by 'app-manager' service account"
  owner {
    id          = confluent_service_account.app-manager.id
    api_version = confluent_service_account.app-manager.api_version
    kind        = confluent_service_account.app-manager.kind
  }

  managed_resource {
    id          = confluent_kafka_cluster.standard.id
    api_version = confluent_kafka_cluster.standard.api_version
    kind        = confluent_kafka_cluster.standard.kind

    environment {
      id = confluent_environment.staging.id
    }
  }

  depends_on = [
    confluent_role_binding.app-manager-kafka-cluster-admin
  ]
}


resource "confluent_api_key" "app-manager-schema-registry-api-key" {
  display_name = "env-manager-schema-registry-api-key"
  description  = "Schema Registry API Key that is owned by 'env-manager' service account"
  owner {
    id          = confluent_service_account.app-manager.id
    api_version = confluent_service_account.app-manager.api_version
    kind        = confluent_service_account.app-manager.kind
  }

  managed_resource {
    id          = data.confluent_schema_registry_cluster.sr-cluster.id
    api_version = data.confluent_schema_registry_cluster.sr-cluster.api_version
    kind        = data.confluent_schema_registry_cluster.sr-cluster.kind

    environment {
      id = confluent_environment.staging.id
    }
  }
  depends_on = [
    confluent_role_binding.app-manager-kafka-cluster-admin
  ]
}

data "confluent_flink_region" "demo_flink_region" {
  cloud   = local.cloud_provider
  region  = local.confluent_region
}



# Flink management API Keys

resource "confluent_api_key" "app-manager-flink-api-key" {
  display_name = "env-manager-flink-api-key"
  description  = "Flink API Key that is owned by 'env-manager' service account"
  owner {
    id          = confluent_service_account.app-manager.id
    api_version = confluent_service_account.app-manager.api_version
    kind        = confluent_service_account.app-manager.kind
  }

  managed_resource {
    id          = data.confluent_flink_region.demo_flink_region.id
    api_version = data.confluent_flink_region.demo_flink_region.api_version
    kind        = data.confluent_flink_region.demo_flink_region.kind

    environment {
      id = confluent_environment.staging.id
    }
  }
}


# ------------------------------------------------------
# Flink Connection
# ------------------------------------------------------

# Data sources for Flink connection
data "confluent_organization" "main" {}

# ------------------------------------------------------
# ACLS
# ------------------------------------------------------




resource "confluent_kafka_acl" "app-manager-read-on-topic" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  resource_type = "TOPIC"
  resource_name = "*"
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-manager.id}"
  host          = "*"
  operation     = "READ"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}

resource "confluent_kafka_acl" "app-manager-describe-on-cluster" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  resource_type = "CLUSTER"
  resource_name = "kafka-cluster"
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-manager.id}"
  host          = "*"
  operation     = "DESCRIBE"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}


resource "confluent_kafka_acl" "app-manager-write-on-topic" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  resource_type = "TOPIC"
  resource_name = "*"
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-manager.id}"
  host          = "*"
  operation     = "WRITE"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}

resource "confluent_kafka_acl" "app-manager-create-topic" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  resource_type = "TOPIC"
  resource_name = "*"
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-manager.id}"
  host          = "*"
  operation     = "CREATE"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}

resource "confluent_kafka_acl" "app-manager-read-on-group" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  resource_type = "GROUP"
  resource_name = "*"
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-manager.id}"
  host          = "*"
  operation     = "READ"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}



