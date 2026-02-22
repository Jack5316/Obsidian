"""Skill wrapper for skill package analysis (/package skill).

This skill analyzes the status, health, completeness, and pipelines of your current skill configuration.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from skill_package_analysis import main as run_analysis


def main():
    """Skill entry point for skill package analysis (/package)."""
    parser = argparse.ArgumentParser(
        description="Package Analysis Skill (/package)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This skill analyzes your skill configuration including:
- Status monitoring (active/inactive, last execution)
- Health assessment (error rates, performance metrics)
- Completeness analysis (documentation, coverage)
- Improvement recommendations
- Pipeline optimization insights

Examples:
  /package                    # Analyze and output to terminal
  /package --save             # Save report to Sources/
  /package --json             # Output in JSON format
  /package --days 60          # Analyze last 60 days of history
""",
    )

    parser.add_argument(
        "-d", "--days",
        type=int,
        default=30,
        help="Days of history to analyze (default: 30)"
    )
    parser.add_argument(
        "-s", "--save",
        action="store_true",
        help="Save analysis report to Sources/"
    )
    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output JSON instead of Markdown"
    )

    args = parser.parse_args()

    try:
        # Call the main analysis function
        sys.argv = [sys.argv[0],]
        if args.days != 30:
            sys.argv.extend(["--days", str(args.days)])
        if args.save:
            sys.argv.append("--save")
        if args.json:
            sys.argv.append("--json")

        run_analysis()

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
