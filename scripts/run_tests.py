#!/usr/bin/env python3
"""
Run workshop E2E tests with convenient shortcuts.

Usage:
    uv run tests                    # Run all tests (fresh deployment)
    uv run tests --resume           # Resume with existing infrastructure
    uv run tests --quick            # Run smoke tests only (< 1 min)
    uv run tests -k lab3            # Run specific test pattern
    uv run tests --no-teardown      # Keep infrastructure after tests

Infrastructure Management:
    - On test FAILURE: Infrastructure is kept automatically (for debugging)
    - On test SUCCESS: Infrastructure is destroyed (unless --no-teardown)
    - To force destroy on failure: PYTEST_DESTROY_ON_FAILURE=true uv run tests
"""

import argparse
import os
import subprocess
import sys


def main():
    """Run tests with configurable options."""
    parser = argparse.ArgumentParser(
        description="Run workshop E2E tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Full E2E test (~25-35 min)
  %(prog)s --resume           # Resume with deployed infra (~5-10 min)
  %(prog)s --quick            # Smoke tests only (~1 min)
  %(prog)s -k lab3 -v         # Run Lab 3 tests verbosely
  %(prog)s --no-teardown      # Keep infrastructure after tests

Environment Variables:
  PYTEST_RESUME=true              # Same as --resume
  PYTEST_SKIP_TEARDOWN=true       # Same as --no-teardown
  PYTEST_DESTROY_ON_FAILURE=true  # Force destroy even on test failure

Infrastructure Management:
  By default, infrastructure is KEPT on test failure (for debugging).
  Use --resume to rerun tests after fixing issues.
"""
    )

    parser.add_argument("--resume", action="store_true",
                       help="Resume from existing deployment (skip deploy/teardown)")
    parser.add_argument("--quick", action="store_true",
                       help="Run smoke tests only (fast validation)")
    parser.add_argument("--no-teardown", action="store_true",
                       help="Keep infrastructure after tests (for debugging)")
    parser.add_argument("-k", type=str, default=None,
                       help="Only run tests matching pattern")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                       help="Increase verbosity (-v, -vv, -vvv)")
    parser.add_argument("--timeout", type=int, default=5400,
                       help="Test timeout in seconds (default: 5400 = 90 min)")
    parser.add_argument("path", nargs="?", default="testing/e2e",
                       help="Test path (default: testing/e2e)")

    args = parser.parse_args()

    # Set environment variables based on flags
    env = os.environ.copy()

    if args.resume:
        env["PYTEST_RESUME"] = "true"
        print("🔄 Resume mode: Using existing infrastructure")

    if args.no_teardown:
        env["PYTEST_SKIP_TEARDOWN"] = "true"
        print("🚫 Teardown disabled: Infrastructure will be kept")

    # Build pytest command
    cmd = ["pytest"]

    # Determine test path
    if args.quick:
        cmd.append("testing/e2e/test_smoke.py")
        cmd.append("testing/e2e/test_sql_extraction.py")
        cmd.append("testing/e2e/test_workshop_keys.py")
        print("⚡ Quick mode: Running smoke tests only")
    else:
        cmd.append(args.path)

    # Add verbosity
    if args.verbose > 0:
        cmd.append("-" + "v" * args.verbose)

    # Add pattern filter
    if args.k:
        cmd.extend(["-k", args.k])

    # Add timeout
    cmd.append(f"--timeout={args.timeout}")

    # Always show output (-s is now default in pytest.ini)
    # But add it explicitly for clarity
    if "-s" not in cmd:
        cmd.append("-s")

    print(f"\n{'='*70}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*70}\n")

    # Execute pytest
    result = subprocess.run(cmd, env=env)

    # Print summary
    if result.returncode == 0:
        print(f"\n{'='*70}")
        print("✅ Tests passed!")
        print(f"{'='*70}\n")

        if args.resume or args.no_teardown:
            print("💡 Reminder: Infrastructure is still deployed")
            print("   To clean up: uv run destroy --testing")
            print("   To rerun tests: uv run tests --resume")
    else:
        print(f"\n{'='*70}")
        print("❌ Tests failed")
        print(f"{'='*70}\n")

        if not args.resume and not args.no_teardown:
            print("💡 Infrastructure kept automatically for debugging")
            print("   After fixing, rerun with: uv run tests --resume")
            print("   To clean up: uv run destroy --testing")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
