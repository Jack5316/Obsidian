"""Skill wrapper for tophub news scraper."""

import argparse
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from tophub_news import main as run_tophub_scraper


def main():
    """Skill entry point for tophub news scraper."""
    parser = argparse.ArgumentParser(
        description="TopHub News Scraper Skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This skill scrapes news from tophub.today and saves it as Obsidian notes.

Examples:
  /skill tophub-news                    # Comprehensive news digest
  /skill tophub-news --section tech     # Tech news only
  /skill tophub-news --count 25         # Limit to 25 news items
  /skill tophub-news --section ai --count 30  # AI news, 30 items
"""
    )

    parser.add_argument(
        "-s", "--section",
        help="Specific news section to scrape (comprehensive, tech, ai, entertainment, sports, finance, military, international, society, culture)"
    )
    parser.add_argument(
        "-c", "--count",
        type=int,
        default=50,
        help="Maximum number of news items to scrape (default: 50)"
    )

    args = parser.parse_args()

    try:
        # Call the main scraper function
        sys.argv = [sys.argv[0],]
        if args.section:
            sys.argv.extend(["--section", args.section])
        if args.count != 50:
            sys.argv.extend(["--count", str(args.count)])

        run_tophub_scraper()

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
