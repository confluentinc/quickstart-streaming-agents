#!/usr/bin/env bash
# ============================================================================
# import.sh - Import the Fraud Investigation Agent and tools into
#             watsonx Orchestrate.
#
# Prerequisites:
#   - orchestrate CLI installed and authenticated
#   - Active env set (local or remote)
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ORCHESTRATE="$(which orchestrate 2>/dev/null || echo "orchestrate")"

echo "=== Importing tools into watsonx Orchestrate ==="

# Step 1: Import Python tool
echo "[1/2] Importing get_claim_investigation tool..."
$ORCHESTRATE tools import --kind python --file "${SCRIPT_DIR}/tools/get_claim_investigation.py"

# Step 2: Import agent
echo "[2/2] Importing fraud_investigation_agent..."
$ORCHESTRATE agents import --file "${SCRIPT_DIR}/agent/fraud_investigation_agent.yaml"

echo ""
echo "=== Import complete ==="
echo ""
$ORCHESTRATE agents list
