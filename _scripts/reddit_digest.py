"""Curate top Reddit posts from specified subreddits into an Obsidian digest.

Uses Reddit's public JSON API (no auth needed - just append .json to any URL).
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List

import requests

from config import summarize, save_note, VAULT_PATH

SUBREDDITS_FILE = VAULT_PATH / "_scripts" / "subreddits.txt"

# Default subreddits matching user interests
DEFAULT_SUBREDDITS = [
    "MachineLearning",
    "philosophy",
    "chipdesign",
    "LocalLLaMA",
]

DIGEST_PROMPT = """You are a Reddit curator. Given top posts from various subreddits,
create an engaging digest organized by theme/topic. For each notable post:
1. Brief summary of the discussion or content
2. Why it's interesting or significant
3. Suggest related [[wikilinks]] for Obsidian

Group by theme rather than by subreddit. Highlight the most valuable discussions.
If posts from different subreddits (e.g., MachineLearning + chipdesign, philosophy + LocalLLaMA) touch the same underlying idea, highlight these cross-domain connections explicitly.
Do NOT include any YAML frontmatter or title heading - start directly with the first theme."""

HEADERS = {"User-Agent": "ObsidianVaultBot/1.0"}


def load_subreddits(override: List[str] = None) -> List[str]:
    """Load subreddit list from file or CLI args."""
    if override:
        return [s.lstrip("r/") for s in override]
    if SUBREDDITS_FILE.exists():
        lines = SUBREDDITS_FILE.read_text().splitlines()
        return [line.strip().lstrip("r/") for line in lines if line.strip() and not line.startswith("#")]
    return DEFAULT_SUBREDDITS


def fetch_subreddit(subreddit: str, sort: str = "hot", limit: int = 10) -> List[dict]:
    """Fetch top posts from a subreddit."""
    url = "https://www.reddit.com/r/{}/{}.json".format(subreddit, sort)
    params = {"limit": limit, "t": "week"}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("  Warning: Could not fetch r/{}: {}".format(subreddit, e))
        return []

    posts = []
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})
        if post.get("stickied"):
            continue

        posts.append({
            "title": post.get("title", ""),
            "subreddit": post.get("subreddit", subreddit),
            "score": post.get("score", 0),
            "comments": post.get("num_comments", 0),
            "author": post.get("author", ""),
            "url": post.get("url", ""),
            "selftext": (post.get("selftext", "") or "")[:500],
            "permalink": "https://reddit.com{}".format(post.get("permalink", "")),
            "created": datetime.fromtimestamp(post.get("created_utc", 0)).strftime("%Y-%m-%d"),
        })

    return posts


def main():
    parser = argparse.ArgumentParser(description="Curate Reddit posts into an Obsidian digest")
    parser.add_argument("--subreddits", nargs="+", help="Subreddits to fetch (overrides config)")
    parser.add_argument("--sort", default="hot", choices=["hot", "top", "new"], help="Sort method")
    parser.add_argument("--limit", type=int, default=10, help="Posts per subreddit (default: 10)")
    args = parser.parse_args()

    subreddits = load_subreddits(args.subreddits)
    print("Fetching from {} subreddits...".format(len(subreddits)))

    all_posts = []
    for sub in subreddits:
        posts = fetch_subreddit(sub, sort=args.sort, limit=args.limit)
        all_posts.extend(posts)
        print("  r/{}: {} posts".format(sub, len(posts)))

    if not all_posts:
        print("No posts found.")
        return

    # Sort by score
    all_posts.sort(key=lambda p: p["score"], reverse=True)

    # Format for AI
    posts_text = "\n\n".join(
        "**{title}** (r/{subreddit})\nScore: {score} | Comments: {comments} | By: u/{author}\n{permalink}\n{selftext}".format(**p)
        for p in all_posts
    )

    print("Generating digest with AI ({} posts)...".format(len(all_posts)))
    digest_body = summarize(posts_text, DIGEST_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")
    subs_str = ", ".join("r/{}".format(s) for s in subreddits)

    # Build posts table
    table_rows = "\n".join(
        "| [{title}]({permalink}) | r/{subreddit} | {score} | {comments} |".format(
            title=p["title"][:55] + ("..." if len(p["title"]) > 55 else ""),
            permalink=p["permalink"],
            subreddit=p["subreddit"],
            score=p["score"],
            comments=p["comments"],
        )
        for p in all_posts[:30]  # Cap table at 30 rows
    )

    note = """---
type: reddit-digest
date: {today}
subreddits: [{subs}]
post_count: {count}
tags:
  - source/reddit
---

# Reddit Digest - {today}

> [!info] {count} posts from {sub_count} subreddits

## Top Posts

| Post | Subreddit | Score | Comments |
|------|-----------|------:|---------:|
{table}

---

## Curated Digest

{digest}

---

*Sources: {subs}*
""".format(
        today=today,
        subs=subs_str,
        count=len(all_posts),
        sub_count=len(subreddits),
        table=table_rows,
        digest=digest_body,
    )

    save_note("Sources/Reddit Digest - {}.md".format(today), note)
    print("Done! {} posts digested.".format(len(all_posts)))


if __name__ == "__main__":
    main()
