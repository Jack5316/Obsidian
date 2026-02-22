#!/usr/bin/env python3
"""
Skill wrapper for daily workflow.
Use with /skill daily command in Claude Code.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _org.templates import DailyWorkflow


def main():
    """Skill entry point for daily workflow."""
    parser = argparse.ArgumentParser(
        description="Daily Workflow Skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This skill runs the daily automation workflow.

Examples:
  /skill daily                    # Run daily workflow
  /skill daily --quick            # Quick news only
  /skill daily --skip twitter_capture.py
""",
    )

    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Quick mode - news digestion only",
    )

    parser.add_argument(
        "--skip",
        "-s",
        help="Comma-separated list of scripts to skip",
    )

    args = parser.parse_args()

    skip_list = []
    if args.skip:
        skip_list = [s.strip() for s in args.skip.split(",") if s.strip()]

    workflow = DailyWorkflow()

    if args.quick:
        print("Running DAILY QUICK workflow (news only)...")
        workflow.run_quick(skip_scripts=skip_list)
    else:
        print("Running DAILY workflow...")
        workflow.run(skip_scripts=skip_list)

    return 0


if __name__ == "__main__":
    sys.exit(main())
