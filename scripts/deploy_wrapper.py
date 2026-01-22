#!/usr/bin/env python3
"""
Wrapper script for GKO workshop deployment.
Always runs deploy.py with --workshop flag.
"""
import sys
from deploy import main as deploy_main


def main():
    """
    Entry point that ensures --workshop flag is always set.
    """
    # Force --workshop flag for GKO workshop branch
    if "--workshop" not in sys.argv:
        sys.argv.append("--workshop")

    # Call the original deploy main function
    deploy_main()


if __name__ == "__main__":
    main()
