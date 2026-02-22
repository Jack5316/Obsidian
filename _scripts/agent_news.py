#!/usr/bin/env python3
"""Fetch, parse, and summarize news from machine-readable sources for AI agents.

Supports RSS/Atom feeds, JSON APIs (NewsAPI, GNews), and llms.txt endpoints.
Prioritizes structured, non-scraped sources per the agent-news specification.
"""

import argparse
import datetime
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))

import feedparser
import requests

from config import (
    summarize,
    save_note,
    VAULT_PATH,
    TRACKER,
    NEWS_API_KEY,
    GNEWS_API_KEY,
)

# =============================================================================
# Configuration
# =============================================================================

# Tier 2: RSS/Atom Feeds (no API key required)
RSS_FEEDS = {
    "BBC": "https://feeds.bbci.co.uk/news/rss.xml",
    "NY Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "Reuters": "https://feeds.reuters.com/reuters/topNews",
    "TechCrunch": "https://techcrunch.com/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "Wired": "https://www.wired.com/feed/rss",
    "BAIR Blog": "https://bair.berkeley.edu/blog/feed.xml",
    "OpenAI News": "https://openai.com/news/rss.xml",
    "Anthropic News": "https://www.anthropic.com/news/rss",
}

# Tier 1: JSON API endpoints (requires keys)
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
GNEWS_API_URL = "https://gnews.io/api/v4/search"

REQUEST_TIMEOUT = 30
REQUEST_DELAY = 0.5  # seconds between requests

SUMMARY_PROMPT = """You are a news editor. Given a list of news headlines and links from various sources,
create a concise, well-organized summary of each news item. For each item:

1. One-sentence summary of the headline in clear English
2. Context about why this might be relevant or significant
3. Suggest related Obsidian [[wikilinks]] for key concepts

Format the response with each news item clearly separated by source. Focus on clarity and accessibility.

Do NOT include any YAML frontmatter or title heading - start directly with the first news item."""


# =============================================================================
# RSS/Atom Feed Parsing (Tier 2)
# =============================================================================

def fetch_rss_feed(name: str, url: str, limit: int = 5) -> List[Dict]:
    """Fetch and parse an RSS/Atom feed."""
    print(f"Fetching RSS: {name}")
    try:
        time.sleep(REQUEST_DELAY)
        feed = feedparser.parse(url)
        if not feed.entries:
            print(f"  No entries found for {name}")
            return []
        
        items = []
        for entry in feed.entries[:limit]:
            items.append({
                "title": entry.get("title", "").strip(),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", "").strip(),
                "link": entry.get("link", ""),
                "source": name,
                "source_type": "rss",
            })
        print(f"  Found {len(items)} items from {name}")
        return items
    except Exception as e:
        print(f"  Error fetching {name}: {e}")
        return []


# =============================================================================
# JSON API Fetching (Tier 1)
# =============================================================================

def fetch_newsapi(topic: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """Fetch news from NewsAPI (requires API key)."""
    if not NEWS_API_KEY:
        print("NewsAPI key not configured, skipping...")
        return []
    
    print("Fetching from NewsAPI...")
    try:
        params = {
            "apiKey": NEWS_API_KEY,
            "pageSize": limit,
            "language": "en",
        }
        if topic:
            params["q"] = topic
        else:
            params["sources"] = "bbc-news,techcrunch,ars-technica,wired"
        
        response = requests.get(NEWS_API_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        items = []
        for article in data.get("articles", []):
            items.append({
                "title": article.get("title", ""),
                "published": article.get("publishedAt", ""),
                "summary": article.get("description", ""),
                "link": article.get("url", ""),
                "source": article.get("source", {}).get("name", "NewsAPI"),
                "source_type": "newsapi",
            })
        print(f"  Found {len(items)} items from NewsAPI")
        return items
    except Exception as e:
        print(f"  Error fetching from NewsAPI: {e}")
        return []


def fetch_gnews(topic: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """Fetch news from GNews (requires API key)."""
    if not GNEWS_API_KEY:
        print("GNews key not configured, skipping...")
        return []
    
    print("Fetching from GNews...")
    try:
        params = {
            "token": GNEWS_API_KEY,
            "max": limit,
            "lang": "en",
        }
        if topic:
            params["q"] = topic
        else:
            params["topic"] = "breaking-news"
        
        response = requests.get(GNEWS_API_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        items = []
        for article in data.get("articles", []):
            items.append({
                "title": article.get("title", ""),
                "published": article.get("publishedAt", ""),
                "summary": article.get("description", ""),
                "link": article.get("url", ""),
                "source": article.get("source", {}).get("name", "GNews"),
                "source_type": "gnews",
            })
        print(f"  Found {len(items)} items from GNews")
        return items
    except Exception as e:
        print(f"  Error fetching from GNews: {e}")
        return []


# =============================================================================
# llms.txt Parsing (Tier 3)
# =============================================================================

def fetch_llms_txt(domain: str) -> Optional[str]:
    """Fetch llms.txt from a domain if it exists."""
    url = f"https://{domain}/llms.txt"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, follow_redirects=True)
        if response.status_code == 200 and len(response.text) > 50:
            return response.text
    except Exception:
        pass
    return None


# =============================================================================
# Aggregation & Deduplication
# =============================================================================

def aggregate_news(
    use_api: bool = False,
    sources_filter: Optional[List[str]] = None,
    topic: Optional[str] = None,
    limit_per_source: int = 5,
) -> List[Dict]:
    """Aggregate news from multiple sources with hierarchy."""
    all_items = []
    
    # Tier 1: JSON APIs (if enabled and keys available)
    if use_api:
        all_items.extend(fetch_newsapi(topic, limit_per_source))
        all_items.extend(fetch_gnews(topic, limit_per_source))
    
    # Tier 2: RSS feeds
    feeds_to_fetch = RSS_FEEDS
    if sources_filter:
        feeds_to_fetch = {
            name: url for name, url in RSS_FEEDS.items()
            if name.lower() in [s.lower() for s in sources_filter]
        }
    
    for name, url in feeds_to_fetch.items():
        all_items.extend(fetch_rss_feed(name, url, limit_per_source))
    
    # Deduplicate by title and link
    seen_titles: Set[str] = set()
    seen_links: Set[str] = set()
    unique_items = []
    
    for item in all_items:
        title_key = item["title"].lower()[:100]
        link_key = item["link"]
        
        if title_key not in seen_titles and link_key not in seen_links:
            seen_titles.add(title_key)
            seen_links.add(link_key)
            unique_items.append(item)
    
    print(f"\nTotal: {len(all_items)} items, {len(unique_items)} unique after deduplication")
    return unique_items


# =============================================================================
# Output Generation
# =============================================================================

def generate_news_digest(news_items: List[Dict], topic: Optional[str] = None) -> str:
    """Generate AI summary of news items."""
    if not news_items:
        return "No news items found."
    
    # Format for AI
    items_text = "\n\n".join(
        f"**{item['title']}**\nSource: {item['source']}\nPublished: {item['published']}\nLink: {item['link']}\nSummary: {item['summary'][:200]}..."
        for item in news_items
    )
    
    print(f"\nGenerating AI digest for {len(news_items)} items...")
    digest_body = summarize(items_text, SUMMARY_PROMPT)
    return digest_body


def save_news_digest(
    news_items: List[Dict],
    digest: str,
    topic: Optional[str] = None,
    use_api: bool = False,
):
    """Save news digest to Obsidian vault."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    topic_suffix = f" - {topic}" if topic else ""
    api_suffix = " (API)" if use_api else ""
    filename = f"Agent News Digest{topic_suffix}{api_suffix} - {today}.md"
    
    # Build table
    table_rows = "\n".join(
        "| [{title}]({link}) | {source} | {published} |".format(
            title=item["title"][:80] + ("..." if len(item["title"]) > 80 else ""),
            link=item["link"],
            source=item["source"],
            published=item["published"][:16] if item["published"] else "N/A",
        )
        for item in news_items
    )
    
    note = """---
type: agent-news-digest
date: {today}
source: agent-news
topic: {topic}
use_api: {use_api}
article_count: {count}
tags:
  - source/news
  - source/agent-news
---

# {title}

> [!info] {count} news items from structured sources ({today})
> Sources: {sources_list}

## News Items

| Title | Source | Published |
|-------|--------|-----------|
{table}

---

## AI Summary

{digest}

---

*Generated by agent-news skill on {today}*
""".format(
        today=today,
        topic=topic or "General",
        use_api=str(use_api).lower(),
        count=len(news_items),
        title=filename.replace(".md", ""),
        sources_list=", ".join(sorted(set(item["source"] for item in news_items))),
        table=table_rows,
        digest=digest,
    )
    
    save_note(f"Sources/{filename}", note)
    print(f"\nDigest saved to Sources/{filename}")


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Fetch news from structured sources for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/agent_news.py                          # RSS only, general news
  python3 _scripts/agent_news.py --topic "AI"            # Filter by topic
  python3 _scripts/agent_news.py --sources "BBC,TechCrunch"  # Specific sources
  python3 _scripts/agent_news.py --use-api                # Use NewsAPI/GNews if keys set
  python3 _scripts/agent_news.py --limit 20               # More results
""",
    )
    parser.add_argument(
        "--topic",
        help="Filter news by topic/keyword",
    )
    parser.add_argument(
        "--sources",
        help="Comma-separated list of specific sources to use (e.g., 'BBC,TechCrunch')",
    )
    parser.add_argument(
        "--use-api",
        action="store_true",
        help="Use NewsAPI/GNews if keys are configured",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum items per source (default: 5)",
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="List available RSS sources and exit",
    )
    
    args = parser.parse_args()
    
    if args.list_sources:
        print("Available RSS sources:")
        for name in sorted(RSS_FEEDS.keys()):
            print(f"  - {name}")
        return
    
    # Track operation
    if TRACKER:
        TRACKER.record_operation(
            script_name="agent_news.py",
            operation_type="fetch_agent_news",
            status="in_progress",
            metrics={
                "topic": args.topic,
                "use_api": args.use_api,
                "limit": args.limit,
            },
        )
    
    try:
        # Parse sources filter
        sources_filter = None
        if args.sources:
            sources_filter = [s.strip() for s in args.sources.split(",")]
        
        # Aggregate news
        news_items = aggregate_news(
            use_api=args.use_api,
            sources_filter=sources_filter,
            topic=args.topic,
            limit_per_source=args.limit,
        )
        
        if not news_items:
            print("No news items found.")
            if TRACKER:
                TRACKER.record_operation(
                    script_name="agent_news.py",
                    operation_type="fetch_agent_news",
                    status="success",
                    metrics={"count": 0},
                )
            return
        
        # Generate digest
        digest = generate_news_digest(news_items, args.topic)
        
        # Save
        save_news_digest(news_items, digest, args.topic, args.use_api)
        
        # Track completion
        if TRACKER:
            TRACKER.record_operation(
                script_name="agent_news.py",
                operation_type="fetch_agent_news",
                status="success",
                metrics={
                    "count": len(news_items),
                    "sources": len(set(item["source"] for item in news_items)),
                },
            )
        
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="agent_news.py",
                operation_type="fetch_agent_news",
                status="failed",
                metrics={"error": str(e)},
            )
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
