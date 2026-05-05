#!/usr/bin/env python3
"""
Publishes insurance claims to IBM MQ (IBM Cloud) via the MQ REST messaging API.
No native MQ client libraries required — uses HTTP PUT to the mqweb REST endpoint.

Messages are published as flat JSON matching the `claims` Flink table schema,
so the Flink INSERT from claim_mq → claims can use simple JSON_VALUE paths.

Usage:
    uv run scripts/publish_claims_to_ibmmq.py
    uv run scripts/publish_claims_to_ibmmq.py --dry-run
    uv run scripts/publish_claims_to_ibmmq.py --limit 50
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

try:
    from dotenv import load_dotenv, set_key as _set_key
    _CREDS_FILE = Path(__file__).parents[1] / "credentials.env"
    if _CREDS_FILE.exists():
        load_dotenv(_CREDS_FILE)
except ImportError:
    _CREDS_FILE = None

def _get_or_prompt(env_key: str, prompt_text: str, secret: bool = False) -> str:
    val = os.environ.get(env_key, "").strip()
    if val:
        return val
    import getpass
    val = (getpass.getpass if secret else input)(f"{prompt_text}: ").strip()
    if val and _CREDS_FILE and _CREDS_FILE.exists():
        _set_key(str(_CREDS_FILE), env_key, val)
    return val


# IBM MQ on IBM Cloud — CLAIMSQM queue manager
MQ_HOST = "web-claimsqm-3254.qm.us-south.mq.appdomain.cloud"
MQ_QM = "CLAIMSQM"
MQ_QUEUE = "DEV.CLAIMS.1"
MQ_USER = "app"
MQ_PASS = _get_or_prompt("TF_VAR_ibmmq_password", "IBM MQ app password (CLAIMSQM)", secret=True)

# REST messaging API endpoint
MQ_REST_URL = f"https://{MQ_HOST}/ibmmq/rest/v2/messaging/qmgr/{MQ_QM}/queue/{MQ_QUEUE}/message"

# FLAT_JSON_SWITCH: This publisher sends FLAT JSON (no Avro union envelope).
# After switching to this publisher, update the Flink INSERT in
# terraform/lab5-insurance-fraud-watson/main.tf (search for FLAT_JSON_SWITCH)
# to use simplified JSON paths: $.claim_id instead of $.value.claim_id, etc.


def load_claims(csv_file: Path, limit: int | None = None) -> list[dict]:
    """Load claims from the synthetic FEMA claims CSV."""
    claims = []
    with open(csv_file, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if limit and i >= limit:
                break
            # Build a flat JSON object matching the claims Flink table schema.
            # claim_timestamp is epoch millis — keep as integer for Flink
            # TO_TIMESTAMP_LTZ conversion.
            claims.append({
                "claim_id": row["claim_id"],
                "applicant_name": row.get("applicant_name", ""),
                "city": row.get("city", ""),
                "is_primary_residence": row.get("is_primary_residence", ""),
                "damage_assessed": row.get("damage_assessed", ""),
                "claim_amount": row.get("claim_amount", ""),
                "has_insurance": row.get("has_insurance", ""),
                "insurance_amount": row.get("insurance_amount", ""),
                "claim_narrative": row.get("claim_narrative", ""),
                "assessment_date": row.get("assessment_date", ""),
                "disaster_date": row.get("disaster_date", ""),
                "previous_claims_count": row.get("previous_claims_count", ""),
                "last_claim_date": row.get("last_claim_date", ""),
                "assessment_source": row.get("assessment_source", ""),
                "shared_account": row.get("shared_account", ""),
                "shared_phone": row.get("shared_phone", ""),
                "claim_timestamp": int(row["claim_timestamp"]),
            })
    return claims


def publish_to_mq(claims: list[dict], dry_run: bool = False) -> dict:
    """Publish claims to IBM MQ via REST API."""
    results = {"total": len(claims), "success": 0, "failed": 0}

    if dry_run:
        print(f"DRY RUN: would publish {len(claims)} claims to {MQ_QM}/{MQ_QUEUE}")
        print(f"REST URL: {MQ_REST_URL}")
        print(f"Sample message:\n{json.dumps(claims[0], indent=2)}")
        return results

    auth = HTTPBasicAuth(MQ_USER, MQ_PASS)
    headers = {
        "Content-Type": "text/plain;charset=utf-8",
        "ibm-mq-rest-csrf-token": "",  # required by MQ REST API
    }

    for i, claim in enumerate(claims, 1):
        try:
            resp = requests.post(
                MQ_REST_URL,
                data=json.dumps(claim),
                headers=headers,
                auth=auth,
                timeout=30,
            )
            resp.raise_for_status()
            results["success"] += 1

            if i % 100 == 0:
                print(f"  Progress: {i}/{results['total']}")

        except requests.RequestException as e:
            results["failed"] += 1
            print(f"  ERROR publishing claim {i} ({claim['claim_id']}): {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"    Response: {e.response.text[:300]}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Publish insurance claims to IBM MQ (CLAIMSQM) via REST API"
    )
    parser.add_argument(
        "--data-file", type=Path,
        help="Path to CSV (default: assets/lab4/data/fema_claims_synthetic.csv)"
    )
    parser.add_argument("--limit", type=int, help="Max claims to publish")
    parser.add_argument("--dry-run", action="store_true", help="Print without publishing")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    data_file = args.data_file or (project_root / "assets" / "lab4" / "data" / "fema_claims_synthetic.csv")

    if not data_file.exists():
        print(f"ERROR: Data file not found: {data_file}")
        sys.exit(1)

    print(f"Loading claims from {data_file}...")
    claims = load_claims(data_file, limit=args.limit)
    print(f"Loaded {len(claims)} claims")

    print(f"Publishing to {MQ_QM}/{MQ_QUEUE}...")
    results = publish_to_mq(claims, dry_run=args.dry_run)

    print(f"\n{'='*50}")
    print(f"Total: {results['total']}  Success: {results['success']}  Failed: {results['failed']}")
    print(f"{'='*50}")

    if results["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
