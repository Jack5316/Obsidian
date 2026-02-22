"""Curate top Hacker News stories into an Obsidian newsletter note."""

import argparse
from datetime import datetime

import requests

from config import summarize, save_note

HN_API = "https://hacker-news.firebaseio.com/v0"

NEWSLETTER_PROMPT = """You are a tech newsletter curator. Given a list of top Hacker News stories with their
details, create an engaging newsletter digest in markdown. Organize stories into categories like:
- 🔬 Research & Science
- 💻 Programming & Dev Tools
- 🚀 Startups & Business
- 🔒 Security & Privacy
- 🤖 AI & Machine Learning
- 📱 Products & Launches
- 💬 Culture & Discussion

For each story, write a 1-2 sentence summary explaining why it's interesting.
Include the HN discussion link for each. Use Obsidian [[wikilinks]] for related topics.
If any stories connect to recent academic research (LLMs, chip design, philosophy of mind) or would be surprising when viewed from a different domain, flag them briefly as "Cross-Domain Signals."
Do NOT include any YAML frontmatter or title heading - start directly with the first category."""


def fetch_top_stories(n: int = 15) -> list[int]:
    """Fetch top N story IDs from HN."""
    resp = requests.get(f"{HN_API}/topstories.json", timeout=10)
    resp.raise_for_status()
    return resp.json()[:n]


def fetch_story(story_id: int) -> dict:
    """Fetch a single story's details."""
    resp = requests.get(f"{HN_API}/item/{story_id}.json", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return {
        "id": story_id,
        "title": data.get("title", ""),
        "url": data.get("url", ""),
        "score": data.get("score", 0),
        "author": data.get("by", ""),
        "comments": data.get("descendants", 0),
        "time": data.get("time", 0),
        "hn_url": f"https://news.ycombinator.com/item?id={story_id}",
    }


def fetch_article_text(url: str) -> str:
    """Try to fetch article text for AI context. Returns empty string on failure."""
    if not url:
        return ""
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        # Simple text extraction - strip HTML tags
        import re
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:3000]  # Limit to 3000 chars per article
    except Exception:
        return ""


def main():
    parser = argparse.ArgumentParser(description="Curate HN top stories into an Obsidian newsletter")
    parser.add_argument("--top", type=int, default=15, help="Number of top stories (default: 15)")
    parser.add_argument("--fetch-articles", action="store_true", help="Fetch article content for better summaries")
    args = parser.parse_args()

    print(f"Fetching top {args.top} Hacker News stories...")
    story_ids = fetch_top_stories(args.top)

    stories = []
    for sid in story_ids:
        story = fetch_story(sid)
        stories.append(story)
        print(f"  [{story['score']:>4}⬆] {story['title']}")

    # Optionally fetch article content
    if args.fetch_articles:
        print("Fetching article content...")
        for story in stories:
            story["article_text"] = fetch_article_text(story["url"])

    # Format stories for AI
    stories_text = "\n\n".join(
        f"**{s['title']}**\n"
        f"URL: {s['url']}\n"
        f"Score: {s['score']} | Comments: {s['comments']} | By: {s['author']}\n"
        f"HN: {s['hn_url']}"
        + (f"\nArticle excerpt: {s.get('article_text', '')[:500]}" if s.get("article_text") else "")
        for s in stories
    )

    print("Generating newsletter with AI...")
    newsletter_body = summarize(stories_text, NEWSLETTER_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")

    # Build stories table
    table_rows = "\n".join(
        f"| [{s['title'][:60]}{'...' if len(s['title']) > 60 else ''}]({s['url'] or s['hn_url']}) "
        f"| {s['score']} | {s['comments']} | [discuss]({s['hn_url']}) |"
        for s in stories
    )

    note = f"""---
type: hn-newsletter
date: {today}
story_count: {len(stories)}
top_score: {max(s['score'] for s in stories)}
tags:
  - source/hackernews
  - newsletter
---

# Hacker News Digest - {today}

> [!info] Top {len(stories)} stories from Hacker News

## Top Stories

| Story | Score | Comments | Discussion |
|-------|------:|--------:|------------|
{table_rows}

---

## Curated Digest

{newsletter_body}

---

*Generated from [Hacker News](https://news.ycombinator.com) top stories*
"""

    save_note(f"Sources/HN Newsletter - {today}.md", note)
    print("Done!")


if __name__ == "__main__":
    main()
