#!/usr/bin/env python3
"""Skill wrapper for tophub_news_detailed.py"""

import argparse
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from tophub_news_detailed import main as run_detailed_tophub_scraper


def main():
    parser = argparse.ArgumentParser(
        description="TopHub Detailed News Scraper Skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This skill scrapes real news headlines from popular Chinese news sections on tophub.today:
- Weibo Hot Search
- WeChat 24h Hot Articles
- Baidu Real-Time Hotspots
- Bilibili Site-Wide Daily Rankings
- 36Kr 24h Hot News

Examples:
  /skill tophub-news-detailed              # Scrape default number of news items
  /skill tophub-news-detailed --count 5    # Scrape 5 news items per section
"""
    )

    parser.add_argument(
        "-c", "--count", type=int, default=5,
        help="Number of news items to scrape per section (default: 5)"
    )

    args = parser.parse_args()

    try:
        # Run the detailed scraper function
        sys.argv = [sys.argv[0], "--count", str(args.count)]
        run_detailed_tophub_scraper()
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    main()
