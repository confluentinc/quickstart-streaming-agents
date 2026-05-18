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
import logging
import os
import random
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List

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

# Total time window: 24 hours of data
TOTAL_WINDOW_HOURS = 24
# Spike window: last 1 hour
SPIKE_WINDOW_HOURS = 1
# Steady-state rate: ~25-30 claims per hour (we use 27 for ~23 hours = 621 claims)
STEADY_STATE_PER_HOUR = 27
# Extra non-narrative claims mixed into the spike hour alongside the 47 narrative claims
SPIKE_EXTRA_NORMAL = 47


def rebase_timestamps(
    claims: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Rebase claim timestamps so data ends at 'now'.

    - A small number of non-narrative claims (~27/hr) fill the first 23 hours
      (steady state).
    - The last 1 hour contains all 47 narrative claims plus 47 additional
      non-narrative claims (94 total) — the spike.
    - Remaining claims from the CSV are discarded.

    All claims are returned sorted by their new timestamp.
    """
    logger = logging.getLogger(__name__)

    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=TOTAL_WINDOW_HOURS)
    spike_start = now - timedelta(hours=SPIKE_WINDOW_HOURS)

    # Separate claims by whether they have a narrative
    narrative_claims = [c for c in claims if c.get("claim_narrative", "").strip()]
    normal_claims = [c for c in claims if not c.get("claim_narrative", "").strip()]

    # Select subsets
    steady_state_hours = TOTAL_WINDOW_HOURS - SPIKE_WINDOW_HOURS
    steady_state_count = STEADY_STATE_PER_HOUR * steady_state_hours
    total_normal_needed = steady_state_count + SPIKE_EXTRA_NORMAL

    if len(normal_claims) < total_normal_needed:
        logger.warning(
            f"Only {len(normal_claims)} non-narrative claims available, "
            f"need {total_normal_needed}"
        )
        total_normal_needed = len(normal_claims)
        steady_state_count = total_normal_needed - SPIKE_EXTRA_NORMAL

    steady_state_claims = normal_claims[:steady_state_count]
    spike_normal_claims = normal_claims[steady_state_count:steady_state_count + SPIKE_EXTRA_NORMAL]

    total_emitted = len(steady_state_claims) + len(spike_normal_claims) + len(narrative_claims)
    logger.info(f"Steady state: {len(steady_state_claims)} claims over {steady_state_hours}h (~{STEADY_STATE_PER_HOUR}/hr)")
    logger.info(f"Spike hour: {len(narrative_claims)} narrative + {len(spike_normal_claims)} normal = {len(narrative_claims) + len(spike_normal_claims)} claims")
    logger.info(f"Total to publish: {total_emitted} (discarding {len(claims) - total_emitted} from CSV)")

    rebased = []

    # Spread steady-state claims over the first 23 hours with jitter.
    # Generate random offsets within the window, then sort them to maintain
    # chronological order while producing natural per-hour count variation.
    if steady_state_claims:
        total_seconds = steady_state_hours * 3600
        offsets = sorted(random.uniform(0, total_seconds) for _ in steady_state_claims)
        for claim, offset in zip(steady_state_claims, offsets):
            new_ts = window_start + timedelta(seconds=offset)
            claim = claim.copy()
            claim["claim_timestamp"] = new_ts.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            rebased.append(claim)

    # Combine narrative + extra normal claims for the spike hour
    spike_claims = narrative_claims + spike_normal_claims
    if spike_claims:
        spike_seconds = SPIKE_WINDOW_HOURS * 3600
        interval = spike_seconds / (len(spike_claims) + 1)
        for i, claim in enumerate(spike_claims):
            new_ts = spike_start + timedelta(seconds=(i + 1) * interval)
            claim = claim.copy()
            claim["claim_timestamp"] = new_ts.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            rebased.append(claim)

    # Sort ALL claims by rebased timestamp for chronological publishing
    rebased.sort(key=lambda c: c["claim_timestamp"])

    logger.info(
        f"Rebased time window: "
        f"{window_start.strftime('%Y-%m-%d %H:%M')} to "
        f"{now.strftime('%Y-%m-%d %H:%M')} UTC"
    )
    logger.info(
        f"Spike window: "
        f"{spike_start.strftime('%Y-%m-%d %H:%M')} to "
        f"{now.strftime('%Y-%m-%d %H:%M')} UTC"
    )

    return rebased


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
                "claim_timestamp": row["claim_timestamp"],
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
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

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

    claims = rebase_timestamps(claims)
    for claim in claims:
        dt = datetime.fromisoformat(claim["claim_timestamp"])
        claim["claim_timestamp"] = int(dt.timestamp() * 1000)

    print(f"Publishing to {MQ_QM}/{MQ_QUEUE}...")
    results = publish_to_mq(claims, dry_run=args.dry_run)

    print(f"\n{'='*50}")
    print(f"Total: {results['total']}  Success: {results['success']}  Failed: {results['failed']}")
    print(f"{'='*50}")

    if results["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
