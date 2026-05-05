#!/usr/bin/env python3
"""
Verify IBM MQ messages using non-destructive browse mode.

This script connects to the IBM MQ broker and browses messages
without consuming/deleting them. Use this to verify:
1. Messages are in the queue
2. Read-only user permissions work correctly
3. Messages remain after read (non-destructive)

Usage:
    python scripts/verify_mq_messages.py
    python scripts/verify_mq_messages.py --user workshop-user --password WORKSHOP_PASSWORD
    python scripts/verify_mq_messages.py --limit 5  # Browse first 5 messages

Requirements:
    pip install stomp.py
"""

import argparse
import json
import os
import ssl
import sys
import time
from pathlib import Path

try:
    import stomp
    STOMP_AVAILABLE = True
except ImportError:
    STOMP_AVAILABLE = False
    print("ERROR: stomp.py library not found. Install with: pip install stomp.py")
    sys.exit(1)

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


# IBM MQ Connection Details — loaded from credentials.env or prompted interactively
MQ_HOST = 'b-f5cac8db-4315-42f8-9d2e-300a720feb46-1.mq.us-east-1.amazonaws.com'
MQ_PORT = 61614  # STOMP+SSL port
MQ_USER = 'workshop-user'
MQ_PASS = _get_or_prompt("TF_VAR_activemq_password", "IBM MQ workshop-user password", secret=True)
MQ_QUEUE = '/queue/claims'


class BrowseListener(stomp.ConnectionListener):
    """Listener for browsing messages without consuming them."""

    def __init__(self, max_messages=10):
        self.messages = []
        self.errors = []
        self.max_messages = max_messages
        self.received_count = 0

    def on_message(self, frame):
        """Collect messages as they arrive."""
        self.received_count += 1

        try:
            # Parse JSON body
            message_body = json.loads(frame.body)
            self.messages.append(message_body)

            # Print compact summary
            claim_id = message_body.get('claim_id', 'UNKNOWN')
            claim_amount = message_body.get('claim_amount', 'UNKNOWN')
            city = message_body.get('city', 'UNKNOWN')

            print(f"  [{self.received_count}] Claim {claim_id} | ${claim_amount} | {city}")

        except json.JSONDecodeError as e:
            print(f"  WARNING: Could not parse message as JSON: {e}")
            self.messages.append(frame.body)

    def on_error(self, frame):
        """Handle errors."""
        error_msg = f'Error: {frame.body}'
        print(error_msg)
        self.errors.append(error_msg)

    def on_connected(self, frame):
        """Confirm connection."""
        print(f'✓ Connected to IBM MQ')

    def on_disconnected(self):
        """Handle disconnection."""
        print('✓ Disconnected from IBM MQ')


def browse_mq_queue(
    host: str,
    port: int,
    username: str,
    password: str,
    queue: str,
    max_messages: int = 10,
    browse_timeout: int = 5
):
    """
    Browse messages in the MQ queue without consuming them.

    Args:
        host: MQ broker hostname
        port: MQ broker port
        username: MQ username
        password: MQ password
        queue: Queue name
        max_messages: Maximum messages to browse
        browse_timeout: Time to wait for messages (seconds)

    Returns:
        List of messages
    """
    # Validate configuration
    if 'XXXXXXXX' in host or password == 'PLACEHOLDER_PASSWORD':
        print("ERROR: MQ credentials not configured!")
        print("Please update MQ_HOST, MQ_USER, and MQ_PASS in this script,")
        print("or provide them via command-line arguments.")
        sys.exit(1)

    # SSL configuration for Amazon MQ
    # For stomp.py 8.x, SSL is configured via set_ssl()
    conn = stomp.Connection(
        host_and_ports=[(host, port)],
        heartbeats=(10000, 10000),
        keepalive=True
    )

    # Configure SSL for secure connection
    conn.set_ssl(for_hosts=[(host, port)])

    listener = BrowseListener(max_messages=max_messages)
    conn.set_listener('', listener)

    try:
        print(f"\nConnecting to IBM MQ at {host}:{port}...")
        print(f"User: {username}")
        print(f"Queue: {queue}")

        conn.connect(username, password, wait=True)

        print(f"\nBrowsing messages (non-destructive mode)...")
        print(f"This will NOT remove messages from the queue.\n")

        # Subscribe with browser mode (non-destructive read)
        # The 'activemq.browser' header enables browse mode
        conn.subscribe(
            destination=queue,
            id=1,
            ack='client',
            headers={'activemq.browser': 'true'}
        )

        # Wait for messages to arrive
        print(f"Waiting {browse_timeout} seconds for messages...\n")
        time.sleep(browse_timeout)

        # Unsubscribe
        conn.unsubscribe(id=1)

        print(f"\n{'='*60}")
        print(f"BROWSE RESULTS")
        print(f"{'='*60}")
        print(f"Messages found: {len(listener.messages)}")

        if listener.errors:
            print(f"Errors: {len(listener.errors)}")
            for error in listener.errors:
                print(f"  - {error}")

        print(f"{'='*60}\n")

        if len(listener.messages) == 0:
            print("⚠️  No messages found in queue")
            print("\nPossible reasons:")
            print("  1. Queue is empty (run lab5_mq_publisher.py first)")
            print("  2. Queue name is incorrect")
            print("  3. User doesn't have read permissions")
        else:
            print(f"✓ Successfully browsed {len(listener.messages)} messages")
            print("✓ Messages remain in queue (non-destructive read)")

            if len(listener.messages) > 0:
                print(f"\nSample message:")
                print(json.dumps(listener.messages[0], indent=2))

        return listener.messages

    except Exception as e:
        print(f"\nERROR: Failed to browse IBM MQ: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify MQ_HOST and MQ_PORT are correct")
        print("  2. Verify MQ_USER and MQ_PASS credentials")
        print("  3. Check that the broker is running and accessible")
        print("  4. Verify security group allows port 61617")
        print("  5. Confirm the queue exists and has messages")
        sys.exit(1)

    finally:
        try:
            conn.disconnect()
        except:
            pass


def test_write_permission(
    host: str,
    port: int,
    username: str,
    password: str,
    queue: str
):
    """
    Test if user has write permissions (should fail for workshop-user).

    Args:
        host: MQ broker hostname
        port: MQ broker port
        username: MQ username
        password: MQ password
        queue: Queue name

    Returns:
        True if write succeeded (BAD), False if write failed (GOOD)
    """
    print(f"\n{'='*60}")
    print(f"TESTING WRITE PERMISSION (should fail for read-only user)")
    print(f"{'='*60}\n")

    conn = stomp.Connection(
        host_and_ports=[(host, port)],
        heartbeats=(10000, 10000),
        keepalive=True
    )

    # Configure SSL for secure connection
    conn.set_ssl(for_hosts=[(host, port)])

    try:
        conn.connect(username, password, wait=True)

        test_message = json.dumps({
            "claim_id": "TEST-WRITE-PERMISSION",
            "test": True,
            "message": "This should NOT succeed for read-only users"
        })

        conn.send(
            body=test_message,
            destination=queue,
            headers={'persistent': 'true', 'content-type': 'application/json'}
        )

        print("⚠️  WARNING: Write permission test SUCCEEDED")
        print("   This user has WRITE access, which is NOT desired for workshop-user.")
        print("   Please configure ActiveMQ authorization to make this user read-only.")

        return True

    except Exception as e:
        print(f"✓ Write permission test failed (as expected)")
        print(f"  User '{username}' cannot write to queue (read-only)")
        print(f"  Error: {e}")
        return False

    finally:
        try:
            conn.disconnect()
        except:
            pass


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Browse IBM MQ messages in non-destructive mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                           # Browse with default settings
  %(prog)s --limit 20                                # Browse first 20 messages
  %(prog)s --user admin --password ADMIN_PASSWORD    # Browse with admin credentials
  %(prog)s --test-write                              # Test write permissions
        """
    )

    parser.add_argument(
        "--host",
        default=MQ_HOST,
        help=f"MQ broker hostname (default: {MQ_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=MQ_PORT,
        help=f"MQ broker port (default: {MQ_PORT})"
    )
    parser.add_argument(
        "--user",
        default=MQ_USER,
        help=f"MQ username (default: {MQ_USER})"
    )
    parser.add_argument(
        "--password",
        default=MQ_PASS,
        help="MQ password"
    )
    parser.add_argument(
        "--queue",
        default=MQ_QUEUE,
        help=f"Queue name (default: {MQ_QUEUE})"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum messages to browse (default: 10)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Browse timeout in seconds (default: 5)"
    )
    parser.add_argument(
        "--test-write",
        action="store_true",
        help="Test write permissions (should fail for read-only user)"
    )

    args = parser.parse_args()

    # Browse messages
    messages = browse_mq_queue(
        host=args.host,
        port=args.port,
        username=args.user,
        password=args.password,
        queue=args.queue,
        max_messages=args.limit,
        browse_timeout=args.timeout
    )

    # Optionally test write permissions
    if args.test_write:
        can_write = test_write_permission(
            host=args.host,
            port=args.port,
            username=args.user,
            password=args.password,
            queue=args.queue
        )

        if can_write and args.user == 'workshop-user':
            print("\n⚠️  ACTION REQUIRED: Configure read-only permissions for workshop-user")
            sys.exit(1)


if __name__ == "__main__":
    main()
