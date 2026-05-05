#!/bin/bash
# ==============================================================================
# Lab 5: IBM MQ Broker Setup Script
# ==============================================================================
# This script creates and configures an Amazon MQ (ActiveMQ) broker in AWS
# us-east-1 for Lab 5 insurance claims fraud detection demo.
#
# Prerequisites:
#   - AWS CLI installed and configured
#   - AWS credentials with permissions to create Amazon MQ resources
#   - jq installed (for JSON parsing)
#
# Usage:
#   ./scripts/setup_ibm_mq_broker.sh
#
# What this script does:
#   1. Creates Amazon MQ broker (ActiveMQ)
#   2. Waits for broker to be running
#   3. Creates read-only workshop user
#   4. Outputs connection details for Terraform
# ==============================================================================

set -e  # Exit on error

# Configuration
BROKER_NAME="lab5-insurance-claims-mq"
REGION="us-east-1"
ENGINE_TYPE="ACTIVEMQ"
ENGINE_VERSION="5.18"
INSTANCE_TYPE="mq.t3.micro"
DEPLOYMENT_MODE="SINGLE_INSTANCE"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Generate secure passwords
ADMIN_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
WORKSHOP_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

echo "========================================================================"
echo "Lab 5: IBM MQ Broker Setup"
echo "========================================================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo -e "${RED}ERROR: AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}WARNING: jq not found. Install it for better JSON parsing.${NC}"
fi

# Verify AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}ERROR: AWS credentials not configured or invalid.${NC}"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓${NC} AWS account: $ACCOUNT_ID"
echo ""

# Step 1: Create Amazon MQ Broker
echo "========================================================================"
echo "Step 1: Creating Amazon MQ Broker"
echo "========================================================================"
echo "Broker name: $BROKER_NAME"
echo "Region: $REGION"
echo "Instance type: $INSTANCE_TYPE"
echo "Engine: $ENGINE_TYPE $ENGINE_VERSION"
echo ""

# Check if broker already exists
EXISTING_BROKER=$(aws mq list-brokers --region $REGION --query "BrokerSummaries[?BrokerName=='$BROKER_NAME'].BrokerId" --output text)

if [ -n "$EXISTING_BROKER" ]; then
    echo -e "${YELLOW}Broker '$BROKER_NAME' already exists (ID: $EXISTING_BROKER)${NC}"
    BROKER_ID=$EXISTING_BROKER
else
    echo "Creating broker (this may take 5-10 minutes)..."

    BROKER_RESPONSE=$(aws mq create-broker \
        --broker-name "$BROKER_NAME" \
        --engine-type "$ENGINE_TYPE" \
        --engine-version "$ENGINE_VERSION" \
        --host-instance-type "$INSTANCE_TYPE" \
        --deployment-mode "$DEPLOYMENT_MODE" \
        --publicly-accessible \
        --auto-minor-version-upgrade \
        --users "Username=admin,Password=$ADMIN_PASSWORD,ConsoleAccess=true" \
        --region "$REGION" \
        --output json)

    BROKER_ID=$(echo $BROKER_RESPONSE | jq -r '.BrokerId')

    if [ -z "$BROKER_ID" ] || [ "$BROKER_ID" = "null" ]; then
        echo -e "${RED}ERROR: Failed to create broker${NC}"
        echo $BROKER_RESPONSE
        exit 1
    fi

    echo -e "${GREEN}✓${NC} Broker created with ID: $BROKER_ID"
fi

echo ""

# Step 2: Wait for broker to be running
echo "========================================================================"
echo "Step 2: Waiting for Broker to be Running"
echo "========================================================================"

echo "Checking broker status..."

MAX_ATTEMPTS=60  # 30 minutes (30 sec intervals)
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    BROKER_STATE=$(aws mq describe-broker --broker-id "$BROKER_ID" --region "$REGION" --query 'BrokerState' --output text)

    if [ "$BROKER_STATE" = "RUNNING" ]; then
        echo -e "${GREEN}✓${NC} Broker is RUNNING"
        break
    elif [ "$BROKER_STATE" = "CREATION_FAILED" ]; then
        echo -e "${RED}ERROR: Broker creation failed${NC}"
        exit 1
    else
        echo "  Status: $BROKER_STATE (attempt $((ATTEMPT+1))/$MAX_ATTEMPTS)"
        sleep 30
        ATTEMPT=$((ATTEMPT+1))
    fi
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo -e "${RED}ERROR: Broker did not reach RUNNING state after 30 minutes${NC}"
    exit 1
fi

echo ""

# Step 3: Get broker connection details
echo "========================================================================"
echo "Step 3: Getting Broker Connection Details"
echo "========================================================================"

BROKER_INFO=$(aws mq describe-broker --broker-id "$BROKER_ID" --region "$REGION" --output json)

# Extract OpenWire endpoint (for IBM MQ/JMS connectivity)
OPENWIRE_ENDPOINT=$(echo $BROKER_INFO | jq -r '.BrokerInstances[0].Endpoints[] | select(startswith("ssl://")) | select(contains(":61617"))')

if [ -z "$OPENWIRE_ENDPOINT" ]; then
    echo -e "${RED}ERROR: Could not find OpenWire SSL endpoint${NC}"
    exit 1
fi

# Remove ssl:// prefix for cleaner output
OPENWIRE_HOST=$(echo $OPENWIRE_ENDPOINT | sed 's/ssl:\/\///')

echo "OpenWire Endpoint: $OPENWIRE_ENDPOINT"
echo "Console URL: https://console.aws.amazon.com/amazon-mq/home?region=$REGION#/brokers/$BROKER_ID"
echo ""

# Step 4: Create read-only workshop user
echo "========================================================================"
echo "Step 4: Creating Read-Only Workshop User"
echo "========================================================================"

echo "Creating workshop-user with read-only permissions..."

# Note: Amazon MQ user creation via CLI
aws mq create-user \
    --broker-id "$BROKER_ID" \
    --username workshop-user \
    --password "$WORKSHOP_PASSWORD" \
    --console-access false \
    --region "$REGION" || echo -e "${YELLOW}User may already exist${NC}"

echo -e "${GREEN}✓${NC} Workshop user created"
echo ""
echo -e "${YELLOW}IMPORTANT: You must manually configure read-only permissions in ActiveMQ${NC}"
echo "Steps:"
echo "  1. Open ActiveMQ Web Console: $OPENWIRE_ENDPOINT:8162"
echo "  2. Login with admin credentials"
echo "  3. Navigate to Configuration > activemq.xml"
echo "  4. Add authorization entry for workshop-user (see LAB5-MANUAL-SETUP.md)"
echo ""

# Step 5: Output credentials and Terraform config
echo "========================================================================"
echo "SETUP COMPLETE"
echo "========================================================================"
echo ""
echo "Save these credentials securely (they are only shown once):"
echo ""
echo "--- Admin Credentials (for broker management) ---"
echo "Username: admin"
echo "Password: $ADMIN_PASSWORD"
echo ""
echo "--- Workshop User Credentials (read-only, for workshop attendees) ---"
echo "Username: workshop-user"
echo "Password: $WORKSHOP_PASSWORD"
echo ""
echo "--- Broker Connection Details ---"
echo "Broker ID: $BROKER_ID"
echo "OpenWire Endpoint: $OPENWIRE_ENDPOINT"
echo "Host (without protocol): $OPENWIRE_HOST"
echo "Region: $REGION"
echo ""

# Create Terraform locals snippet
echo "========================================================================"
echo "Terraform Configuration Snippet"
echo "========================================================================"
echo ""
echo "Add these values to terraform/lab5-insurance-fraud-watson/main.tf:"
echo ""
cat <<EOF
locals {
  # IBM MQ credentials (read-only workshop access)
  ibm_mq_endpoint = "$OPENWIRE_HOST"
  ibm_mq_username = "workshop-user"
  ibm_mq_password = "$WORKSHOP_PASSWORD"
  ibm_mq_queue    = "claims"
}
EOF
echo ""

# Create credentials file
CREDS_FILE="terraform/lab5-insurance-fraud-watson/mq-credentials.txt"
echo "Saving credentials to $CREDS_FILE..."

cat > "$CREDS_FILE" <<EOF
# Lab 5 IBM MQ Credentials
# Generated: $(date)
# DO NOT COMMIT THIS FILE TO GIT

Broker ID: $BROKER_ID
Region: $REGION
OpenWire Endpoint: $OPENWIRE_ENDPOINT

Admin Username: admin
Admin Password: $ADMIN_PASSWORD

Workshop Username: workshop-user
Workshop Password: $WORKSHOP_PASSWORD

Terraform locals:
  ibm_mq_endpoint = "$OPENWIRE_HOST"
  ibm_mq_username = "workshop-user"
  ibm_mq_password = "$WORKSHOP_PASSWORD"
  ibm_mq_queue    = "claims"
EOF

echo -e "${GREEN}✓${NC} Credentials saved to $CREDS_FILE"
echo ""

# Next steps
echo "========================================================================"
echo "Next Steps"
echo "========================================================================"
echo ""
echo "1. Configure read-only permissions in ActiveMQ (see above)"
echo ""
echo "2. Update Terraform configuration:"
echo "   Edit terraform/lab5-insurance-fraud-watson/main.tf"
echo "   Replace placeholders in 'locals' block with values above"
echo ""
echo "3. Populate IBM MQ with claims data:"
echo "   Update MQ_HOST, MQ_PASS in scripts/lab5_mq_publisher.py"
echo "   Run: python scripts/lab5_mq_publisher.py"
echo ""
echo "4. Verify non-destructive read:"
echo "   Update credentials in scripts/verify_mq_messages.py"
echo "   Run: python scripts/verify_mq_messages.py"
echo ""
echo "5. Test write permissions:"
echo "   Run: python scripts/verify_mq_messages.py --test-write"
echo "   Should fail for workshop-user (confirming read-only)"
echo ""
echo "========================================================================"
