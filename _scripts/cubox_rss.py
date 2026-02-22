#!/usr/bin/env python3
"""Automate RSS subscription to Cubox.

Fetches RSS feeds and saves each item to Cubox via the open API.
Tracks sent URLs to avoid duplicates. Requires Cubox Premium (API extension).
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import feedparser
import requests

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import VAULT_PATH, CUBOX_API_URL

# Configuration
CUBOX_RSS_FEEDS = VAULT_PATH / "_scripts" / "cubox_rss_feeds.txt"
SENT_LOG_PATH = VAULT_PATH / "_logs" / "cubox_rss_sent.json"
REQUEST_DELAY = 1.5  # Be nice to Cubox API (500 calls/day limit for premium)
TIMEOUT = 30


def load_feeds() -> List[dict]:
    """Load RSS feeds from config file. Format: Name | URL | Folder (optional)."""
    if not CUBOX_RSS_FEEDS.exists():
        return []
    lines = CUBOX_RSS_FEEDS.read_text(encoding="utf-8").splitlines()
    feeds = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 2:
            feeds.append({
                "name": parts[0],
                "url": parts[1],
                "folder": parts[2] if len(parts) > 2 else "RSS",
            })
    return feeds


def load_sent_log() -> dict:
    """Load set of already-sent URLs."""
    if SENT_LOG_PATH.exists():
        try:
            return json.loads(SENT_LOG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_sent_log(data: dict) -> None:
    """Persist sent URLs log."""
    SENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    SENT_LOG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def save_to_cubox(
    url: str,
    title: str = "",
    description: str = "",
    tags: Optional[List[str]] = None,
    folder: str = "",
) -> bool:
    """POST a URL to Cubox API. Returns True on success."""
    if not CUBOX_API_URL or not CUBOX_API_URL.strip():
        print("Error: CUBOX_API_URL not set. Add your Cubox API link to .env")
        return False

    payload = {
        "type": "url",
        "content": url,
        "title": title or "",
        "description": (description or "")[:500],
        "tags": tags or [],
        "folder": folder or "",
    }

    try:
        r = requests.post(
            CUBOX_API_URL.strip(),
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            data = r.json()
            # Cubox returns code 200 for success
            if data.get("code") in (0, 200) or data.get("code") is None:
                return True
            print(f"  Cubox API error: {data.get('message', r.text)}")
            return False
        print(f"  HTTP {r.status_code}: {r.text[:200]}")
        return False
    except requests.RequestException as e:
        print(f"  Request failed: {e}")
        return False


def fetch_and_sync(feeds: List[dict], days: int, dry_run: bool) -> tuple:
    """Fetch RSS feeds and sync new items to Cubox. Returns (sent, skipped)."""
    sent_log = load_sent_log()
    cutoff = datetime.now() - timedelta(days=days)
    total_sent = 0
    total_skipped = 0

    for feed in feeds:
        print(f"\nFetching: {feed['name']}")
        try:
            time.sleep(REQUEST_DELAY)
            parsed = feedparser.parse(feed["url"])
        except Exception as e:
            print(f"  Error: {e}")
            continue

        if not parsed.entries:
            print("  No entries")
            continue

        for entry in parsed.entries[:50]:
            link = entry.get("link", "").strip()
            if not link or not link.startswith("http"):
                continue

            if link in sent_log:
                total_skipped += 1
                continue

            try:
                pub = entry.get("published_parsed")
                if pub:
                    pub_dt = datetime(*pub[:6])
                    if pub_dt < cutoff:
                        total_skipped += 1
                        continue
            except (TypeError, ValueError):
                pass

            title = (entry.get("title") or "").strip()
            desc = (entry.get("summary", "") or "").strip()
            if desc and len(desc) > 500:
                desc = desc[:497] + "..."

            if dry_run:
                print(f"  [DRY] Would save: {title[:50]}... -> {feed['folder']}")
                total_sent += 1
                sent_log[link] = datetime.now().isoformat()
                continue

            ok = save_to_cubox(
                url=link,
                title=title,
                description=desc,
                folder=feed["folder"],
            )
            if ok:
                print(f"  Saved: {title[:50]}...")
                total_sent += 1
                sent_log[link] = datetime.now().isoformat()
            time.sleep(REQUEST_DELAY)

    if not dry_run and total_sent > 0:
        save_sent_log(sent_log)

    return total_sent, total_skipped


def main():
    parser = argparse.ArgumentParser(
        description="Sync RSS feeds to Cubox",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/cubox_rss.py              # Sync all feeds (last 7 days)
  python3 _scripts/cubox_rss.py --days 3      # Only last 3 days
  python3 _scripts/cubox_rss.py --dry-run     # Preview without saving
  python3 _scripts/cubox_rss.py --list        # List configured feeds

Config: _scripts/cubox_rss_feeds.txt
Format: Feed Name | RSS URL | Folder (optional, default: RSS)
""",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Only sync items from last N days (default: 7)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be saved without calling API",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List configured feeds and exit",
    )
    args = parser.parse_args()

    feeds = load_feeds()

    if args.list:
        if not feeds:
            print("No feeds configured. Add entries to _scripts/cubox_rss_feeds.txt")
            print("Format: Feed Name | RSS URL | Folder (optional)")
            return
        for f in feeds:
            print(f"  {f['name']} -> {f['folder']}")
            print(f"    {f['url']}")
        return

    if not feeds:
        print("No feeds configured. Create _scripts/cubox_rss_feeds.txt")
        print("Format: Feed Name | RSS URL | Folder (optional)")
        print("Example: Hacker News | https://hnrss.org/frontpage | HN")
        sys.exit(1)

    if not args.dry_run and (not CUBOX_API_URL or not CUBOX_API_URL.strip()):
        print("Error: CUBOX_API_URL not set.")
        print("Add to .env: CUBOX_API_URL=https://cubox.pro/c/api/save/YOUR_KEY")
        print("Get your API link: Cubox 偏好设置 > 扩展中心和自动化 > API 扩展")
        sys.exit(1)

    sent, skipped = fetch_and_sync(feeds, args.days, args.dry_run)
    print(f"\nDone: {sent} saved, {skipped} skipped (already sent or too old)")


if __name__ == "__main__":
    main()
