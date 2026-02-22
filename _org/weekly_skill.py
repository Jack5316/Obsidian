#!/usr/bin/env python3
"""
Skill wrapper for weekly workflow.
Use with /skill weekly command in Claude Code.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _org.templates import WeeklyWorkflow


def main():
    """Skill entry point for weekly workflow."""
    parser = argparse.ArgumentParser(
        description="Weekly Workflow Skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This skill runs the weekly automation workflow.

Examples:
  /skill weekly                    # Run full weekly workflow
  /skill weekly --synthesis        # Weekly synthesis only
  /skill weekly --skip twitter_capture.py
""",
    )

    parser.add_argument(
        "--synthesis",
        "--synth",
        action="store_true",
        help="Run weekly synthesis only",
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

    workflow = WeeklyWorkflow()

    if args.synthesis:
        print("Running WEEKLY SYNTHESIS only...")
        workflow.run_synthesis_only(skip_scripts=skip_list)
    else:
        print("Running FULL WEEKLY workflow...")
        workflow.run(skip_scripts=skip_list)

    return 0


if __name__ == "__main__":
    sys.exit(main())
