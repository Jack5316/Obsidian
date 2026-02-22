#!/usr/bin/env python3
"""Skill wrapper for tophub_news_simple.py to enable use from Claude Code."""

import argparse
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from tophub_news_simple import main as run_simple_tophub_scraper


def main():
    """Entry point for the TopHub news scraper skill."""
    parser = argparse.ArgumentParser(
        description="TopHub News Scraper Skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This skill scrapes and summarizes recent Chinese news from tophub.today and saves it as an Obsidian note with AI-generated English summaries and relevant wikilinks.

Examples:
  /skill tophub-news-simple              # Scrape 30 news items (default)
  /skill tophub-news-simple --count 15   # Scrape 15 news items
"""
    )
    parser.add_argument(
        "-c", "--count",
        type=int,
        default=30,
        help="Maximum number of news items to scrape and summarize (default: 30)"
    )

    args = parser.parse_args()

    try:
        # Prepare arguments for the main scraper
        sys.argv = [sys.argv[0],]
        if args.count != 30:
            sys.argv.extend(["--count", str(args.count)])

        # Run the main scraper function
        run_simple_tophub_scraper()
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
