#!/usr/bin/env python3
"""
Publishes insurance claims data to IBM MQ (Amazon MQ ActiveMQ).
Uses the same data schema as Lab 4 datagen.
Messages are published with persistence enabled.

Usage:
    python scripts/lab5_mq_publisher.py
    python scripts/lab5_mq_publisher.py --dry-run
    python scripts/lab5_mq_publisher.py --limit 100

Requirements:
    pip install stomp.py
"""

import argparse
import csv
import json
import os
import random
import ssl
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import stomp
    STOMP_AVAILABLE = True
except ImportError:
    STOMP_AVAILABLE = False
    print("ERROR: stomp.py library not found. Install with: pip install stomp.py")
    sys.exit(1)

try:
    from dotenv import load_dotenv, set_key
    _CREDS_FILE = Path(__file__).parents[1] / "credentials.env"
    if _CREDS_FILE.exists():
        load_dotenv(_CREDS_FILE)
except ImportError:
    pass


def _get_or_prompt(env_key: str, prompt_text: str, secret: bool = False) -> str:
    val = os.environ.get(env_key, "").strip()
    if val:
        return val
    import getpass
    val = (getpass.getpass if secret else input)(f"{prompt_text}: ").strip()
    if val and "_CREDS_FILE" in globals() and _CREDS_FILE.exists():
        set_key(str(_CREDS_FILE), env_key, val)
    return val


# IBM MQ Connection Details — loaded from credentials.env or prompted interactively
MQ_HOST = 'b-f5cac8db-4315-42f8-9d2e-300a720feb46-1.mq.us-east-1.amazonaws.com'
MQ_PORT = 61614  # STOMP+SSL port
MQ_USER = 'admin'
MQ_QUEUE = '/queue/claims'
MQ_PASS = _get_or_prompt("IBM_MQ_PUBLISHER_PASS", "IBM MQ admin password", secret=True)


class MQListener(stomp.ConnectionListener):
    """Listener for MQ connection events."""

    def __init__(self):
        self.errors = []
        self.messages = []

    def on_error(self, frame):
        """Handle connection errors."""
        error_msg = f'MQ Error: {frame.body}'
        print(error_msg)
        self.errors.append(error_msg)

    def on_message(self, frame):
        """Handle incoming messages."""
        self.messages.append(frame.body)
        print(f'Received message: {frame.body[:100]}...')

    def on_connected(self, frame):
        """Confirm connection established."""
        print(f'Successfully connected to IBM MQ')

    def on_disconnected(self):
        """Handle disconnection."""
        print('Disconnected from IBM MQ')


def transform_claim(claim: dict) -> dict:
    """
    Apply field transformations before publishing:
    - Rename 'has_insurance' -> 'has_current_policy'
    - Replace 'Contractor' assessment_source with insurance adjuster types
    """
    transformed = {}
    for key, value in claim.items():
        if key == 'has_insurance':
            transformed['has_current_policy'] = value
        else:
            transformed[key] = value

    if transformed.get('assessment_source') == 'Contractor':
        transformed['assessment_source'] = random.choice([
            'Insurance adjuster (in-house)',
            'Insurance adjuster (3rd party)',
        ])

    return transformed


def load_claims_data(csv_file: Path, limit: int = None) -> list:
    """
    Load claims data from CSV file.

    Args:
        csv_file: Path to CSV file
        limit: Optional limit on number of claims to load

    Returns:
        List of claim dictionaries
    """
    claims = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, claim in enumerate(reader):
                if limit and idx >= limit:
                    break
                claims.append(transform_claim(claim))
    except Exception as e:
        print(f"ERROR: Failed to read CSV file {csv_file}: {e}")
        sys.exit(1)

    return claims


def publish_claims_to_mq(
    claims_data: list,
    dry_run: bool = False,
    simulate_streaming: bool = False,
    speed_multiplier: float = 1.0
):
    """
    Publish claims to IBM MQ with persistent delivery.

    Args:
        claims_data: List of claim dictionaries
        dry_run: If True, don't actually publish
        simulate_streaming: If True, publish based on timestamps
        speed_multiplier: Speed up factor for streaming simulation

    Returns:
        Dictionary with success/failure counts
    """
    results = {"success": 0, "failed": 0, "total": len(claims_data)}

    if dry_run:
        print(f"DRY RUN: Would publish {len(claims_data)} claims to {MQ_HOST}:{MQ_PORT}")
        print(f"Queue: {MQ_QUEUE}")
        print(f"Sample claim: {json.dumps(claims_data[0], indent=2)}")
        return results

    # Validate configuration
    if not MQ_PASS:
        print("ERROR: IBM MQ password not configured.")
        sys.exit(1)

    # SSL configuration for Amazon MQ
    # For stomp.py 8.x, SSL is configured via set_ssl()
    conn = stomp.Connection(
        host_and_ports=[(MQ_HOST, MQ_PORT)],
        heartbeats=(10000, 10000),
        keepalive=True
    )

    # Configure SSL for secure connection
    conn.set_ssl(for_hosts=[(MQ_HOST, MQ_PORT)])

    listener = MQListener()
    conn.set_listener('', listener)

    try:
        print(f"Connecting to IBM MQ at {MQ_HOST}:{MQ_PORT}...")
        conn.connect(MQ_USER, MQ_PASS, wait=True)
        print(f"Connected successfully!")

        # Sort by timestamp if simulating streaming
        if simulate_streaming:
            claims_data.sort(key=lambda c: c['claim_timestamp'])
            print(f"Simulating streaming at {speed_multiplier}x speed")

        # Publish each claim as a persistent message
        for idx, claim in enumerate(claims_data, 1):
            # Simulate streaming timing
            if simulate_streaming and idx > 1:
                current_time = datetime.fromisoformat(claim['claim_timestamp'])
                prev_time = datetime.fromisoformat(claims_data[idx - 2]['claim_timestamp'])
                time_diff = (current_time - prev_time).total_seconds() / speed_multiplier

                if time_diff > 0:
                    time.sleep(time_diff)

            try:
                message_body = json.dumps(claim)

                conn.send(
                    body=message_body,
                    destination=MQ_QUEUE,
                    headers={
                        'persistent': 'true',  # Enable message persistence
                        'content-type': 'application/json',
                        'correlation-id': claim.get('claim_id', f'claim-{idx}'),
                        'amq-msg-type': 'text',
                    }
                )

                results["success"] += 1

                # Progress update
                if idx % 100 == 0:
                    print(f"Progress: {idx}/{results['total']} claims published")

            except Exception as e:
                print(f"ERROR publishing claim {idx}: {e}")
                results["failed"] += 1

        print(f"\nSuccessfully published {results['success']} claims to MQ queue '{MQ_QUEUE}'")
        print("Messages are persistent and will remain in queue after consumption.")

        if results["failed"] > 0:
            print(f"WARNING: {results['failed']} claims failed to publish")

    except Exception as e:
        print(f"ERROR: Failed to connect to IBM MQ: {e}")
        print("\nTroubleshooting:")
        print("1. Verify MQ_HOST and MQ_PORT are correct")
        print("2. Verify MQ_USER and MQ_PASS credentials")
        print("3. Check that the broker is running and publicly accessible")
        print("4. Verify security group allows port 61617")
        sys.exit(1)

    finally:
        try:
            conn.disconnect()
        except:
            pass

    return results


def main():
    """Main entry point for the Lab5 MQ publisher CLI."""
    parser = argparse.ArgumentParser(
        description="Publish Lab5 insurance claims data to IBM MQ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                  # Publish all claims
  %(prog)s --dry-run                        # Test without publishing
  %(prog)s --limit 100                      # Publish first 100 claims
  %(prog)s --simulate-streaming --speed 10  # Stream at 10x speed
        """
    )

    parser.add_argument(
        "--data-file",
        type=Path,
        help="Path to CSV data file (default: assets/lab4/data/fema_claims_synthetic.csv)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of claims to publish"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test without actually publishing to MQ"
    )
    parser.add_argument(
        "--simulate-streaming",
        action="store_true",
        help="Publish claims based on timestamps (simulates real-time streaming)"
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speed multiplier for streaming simulation (default: 1.0)"
    )

    args = parser.parse_args()

    # Determine data file path
    if args.data_file:
        data_file = args.data_file
    else:
        # Default to Lab 4 data file
        project_root = Path(__file__).parent.parent
        data_file = project_root / "assets" / "lab4" / "data" / "fema_claims_synthetic.csv"

    if not data_file.exists():
        print(f"ERROR: Data file not found: {data_file}")
        sys.exit(1)

    print(f"Loading claims data from {data_file}...")
    claims = load_claims_data(data_file, limit=args.limit)
    print(f"Loaded {len(claims)} claims")

    # Publish to IBM MQ
    results = publish_claims_to_mq(
        claims,
        dry_run=args.dry_run,
        simulate_streaming=args.simulate_streaming,
        speed_multiplier=args.speed
    )

    # Print summary
    print("\n" + "="*60)
    print("PUBLICATION SUMMARY")
    print("="*60)
    print(f"Total claims:      {results['total']}")
    print(f"Successfully sent: {results['success']}")
    print(f"Failed:            {results['failed']}")
    print("="*60)

    if results['failed'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
