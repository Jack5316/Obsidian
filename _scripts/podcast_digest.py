#!/usr/bin/env python3
"""Fetch and curate podcast episodes from RSS feeds.

Monitors podcast RSS feeds and creates a digest of recent episodes.
"""

import argparse
import datetime
import feedparser
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from config import summarize, save_note, VAULT_PATH, TRACKER

# Podcast configuration
PODCAST_FEEDS_FILE = VAULT_PATH / "_scripts" / "podcast_feeds.txt"

# Default podcasts if no file exists
DEFAULT_PODCASTS = [
    {"name": "Lex Fridman Podcast", "url": "https://lexfridman.com/feed/podcast/"},
    {"name": "The Joe Rogan Experience", "url": "https://feeds.feedburner.com/TheJoeRoganExperience"},
]

REQUEST_DELAY = 1  # Be nice to RSS servers
TIMEOUT = 30

ANALYSIS_PROMPT = """You are a podcast curator. Given recent podcast episodes, create a digest highlighting
the most interesting episodes. For each podcast:

1. Recent episodes with titles and descriptions
2. Interesting guests or topics
3. Key themes across episodes

Also include:
- Top 3-5 episodes you'd recommend
- Emerging themes or trends
- Suggested [[wikilinks]] for topics/concepts

Focus on what's interesting and worth listening to.
Do NOT include YAML frontmatter - start directly with the overview."""


def load_podcast_feeds() -> List[Dict[str, str]]:
    """Load podcast feeds from file or use defaults."""
    if PODCAST_FEEDS_FILE.exists():
        lines = PODCAST_FEEDS_FILE.read_text().splitlines()
        podcasts = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                if "|" in line:
                    name, url = line.split("|", 1)
                    podcasts.append({"name": name.strip(), "url": url.strip()})
        if podcasts:
            return podcasts
    return DEFAULT_PODCASTS


def fetch_podcast_feed(podcast: Dict[str, str], days: int = 14) -> Optional[Dict[str, Any]]:
    """Fetch and parse a podcast RSS feed."""
    try:
        time.sleep(REQUEST_DELAY)
        feed = feedparser.parse(podcast["url"])
        
        if not feed.entries:
            return None
        
        # Filter recent episodes
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        recent_episodes = []
        
        for entry in feed.entries[:20]:  # Check last 20 episodes
            try:
                published = datetime.datetime(*entry.published_parsed[:6])
                if published >= cutoff:
                    recent_episodes.append({
                        "title": entry.get("title", "N/A"),
                        "description": entry.get("summary", "N/A")[:500],
                        "published": published.strftime("%Y-%m-%d"),
                        "link": entry.get("link", ""),
                    })
            except Exception:
                continue
        
        if not recent_episodes:
            return None
        
        return {
            "name": podcast["name"],
            "url": podcast["url"],
            "episodes": recent_episodes,
        }
        
    except Exception as e:
        print(f"  Error fetching {podcast['name']}: {e}")
        return None


def format_podcast_data(podcast: Dict[str, Any]) -> str:
    """Format podcast data for AI analysis."""
    lines = [f"**Podcast: {podcast['name']}**"]
    
    for ep in podcast["episodes"]:
        lines.append(f"\nEpisode: {ep['title']} ({ep['published']})")
        lines.append(f"Description: {ep['description']}")
        if ep["link"]:
            lines.append(f"Link: {ep['link']}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch podcast episodes from RSS feeds",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-d", "--days", type=int, default=14,
        help="Days of episodes to fetch (default: 14)"
    )
    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="podcast_digest.py",
            operation_type="fetch_podcasts",
            status="in_progress",
            metrics={"days": args.days}
        )

    try:
        podcasts = load_podcast_feeds()
        print(f"Fetching {len(podcasts)} podcasts (last {args.days} days)...")
        
        all_podcasts = []
        for podcast in podcasts:
            print(f"  Fetching {podcast['name']}...")
            data = fetch_podcast_feed(podcast, args.days)
            if data:
                all_podcasts.append(data)
        
        if not all_podcasts:
            raise Exception("No recent podcast episodes found")
        
        print(f"Found episodes from {len(all_podcasts)} podcasts")
        
        # Format data for AI
        podcast_text = "\n\n---\n\n".join(format_podcast_data(p) for p in all_podcasts)
        
        print(f"Generating digest with AI...")
        digest_body = summarize(podcast_text, ANALYSIS_PROMPT)
        
        # Save to Obsidian
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"Podcast Digest - {today}.md"
        
        # Build table
        table_rows = []
        for podcast in all_podcasts:
            for ep in podcast["episodes"][:3]:
                table_rows.append(
                    f"| {podcast['name']} | {ep['title'][:50]}... | {ep['published']} |"
                )
        table = "\n".join(table_rows)
        
        note = f"""---
type: podcast-digest
date: {today}
podcasts: [{', '.join(p['name'] for p in all_podcasts)}]
tags:
  - source/podcast
  - audio
  - learning
---

# Podcast Digest - {today}

> [!info] Recent episodes from {len(all_podcasts)} podcasts (last {args.days} days)

## Recent Episodes

| Podcast | Episode | Date |
|---------|---------|------|
{table}

---

## AI Curated Highlights

{digest_body}

---

*Configure your own podcasts in _scripts/podcast_feeds.txt (format: Name | URL)*
"""
        
        save_note(f"Sources/{filename}", note)
        print(f"Digest saved to Sources/{filename}")
        
        # Create default podcast feeds file if it doesn't exist
        if not PODCAST_FEEDS_FILE.exists():
            default_content = "# Podcast Feeds - format: Name | RSS URL\n"
            default_content += "Lex Fridman Podcast | https://lexfridman.com/feed/podcast/\n"
            PODCAST_FEEDS_FILE.write_text(default_content)
            print(f"Created default podcast feeds file: {PODCAST_FEEDS_FILE}")
        
        # Track operation completion
        if TRACKER:
            TRACKER.record_operation(
                script_name="podcast_digest.py",
                operation_type="fetch_podcasts",
                status="success",
                metrics={
                    "podcasts": len(all_podcasts),
                    "output_file": f"Sources/{filename}"
                }
            )
        
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="podcast_digest.py",
                operation_type="fetch_podcasts",
                status="failed",
                metrics={"error": str(e)}
            )
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
