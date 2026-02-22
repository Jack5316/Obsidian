#!/usr/bin/env python3
"""
Skill wrapper for the atomic design organization system.
Use with /skill atomic-org command in Claude Code.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _org.templates import DailyWorkflow, WeeklyWorkflow


def main():
    """Skill entry point for atomic design organization system."""
    parser = argparse.ArgumentParser(
        description="Atomic Design Organization Skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This skill runs automation workflows using the atomic design system.

Workflows:
  --daily          - Run daily workflow (default)
  --daily-quick    - Run quick daily (news only)
  --weekly         - Run weekly workflow
  --weekly-synth   - Run weekly synthesis only

Examples:
  /skill atomic-org                    # Run daily workflow
  /skill atomic-org --daily            # Run daily workflow
  /skill atomic-org --daily-quick      # Quick news check
  /skill atomic-org --weekly           # Full weekly workflow
  /skill atomic-org --weekly-synth     # Weekly synthesis only
  /skill atomic-org --skip twitter_capture.py,reddit_digest.py
""",
    )

    workflow_group = parser.add_mutually_exclusive_group()
    workflow_group.add_argument(
        "--daily",
        action="store_true",
        help="Run daily workflow (default)",
    )
    workflow_group.add_argument(
        "--daily-quick",
        action="store_true",
        help="Run quick daily workflow (news only)",
    )
    workflow_group.add_argument(
        "--weekly",
        action="store_true",
        help="Run weekly workflow",
    )
    workflow_group.add_argument(
        "--weekly-synth",
        action="store_true",
        help="Run weekly synthesis only",
    )
    workflow_group.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available scripts",
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

    # List scripts if requested
    if args.list:
        from _org.pages.cli import list_scripts

        list_scripts()
        return 0

    # Determine which workflow to run
    if args.weekly:
        print("Running WEEKLY workflow...")
        workflow = WeeklyWorkflow()
        workflow.run(skip_scripts=skip_list)
        return 0

    elif args.weekly_synth:
        print("Running WEEKLY SYNTHESIS only...")
        workflow = WeeklyWorkflow()
        workflow.run_synthesis_only(skip_scripts=skip_list)
        return 0

    elif args.daily_quick:
        print("Running DAILY QUICK workflow...")
        workflow = DailyWorkflow()
        workflow.run_quick(skip_scripts=skip_list)
        return 0

    else:
        # Default: daily workflow
        print("Running DAILY workflow...")
        workflow = DailyWorkflow()
        workflow.run(skip_scripts=skip_list)
        return 0


if __name__ == "__main__":
    sys.exit(main())
