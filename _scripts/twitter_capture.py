"""Capture tweets from followed accounts into an Obsidian digest note.

Uses Twitter's public syndication endpoint (no API key or login needed).
"""

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import List, Optional

import requests

from config import VAULT_PATH, summarize, save_note

ACCOUNTS_FILE = VAULT_PATH / "_scripts" / "twitter_accounts.txt"
SYNDICATION_URL = "https://syndication.twitter.com/srv/timeline-profile/screen-name/{}"

DIGEST_PROMPT = """You are a social media curator. Given a collection of tweets from various accounts,
create a well-organized digest in markdown format. Group related tweets by topic/theme.
For each tweet, preserve the author and any key links. Highlight the most important or
interesting posts. Be concise but informative.
If any tweets connect to themes in academic research, chip design, or philosophical questions about AI, note these as potential cross-domain insights worth tracking.
Do NOT include any YAML frontmatter or title heading -
just the digest content starting with the first topic group."""


def load_accounts(override: Optional[List[str]] = None) -> List[str]:
    """Load account list from file or CLI args."""
    if override:
        return [a.lstrip("@") for a in override]
    if ACCOUNTS_FILE.exists():
        lines = ACCOUNTS_FILE.read_text().splitlines()
        return [line.strip().lstrip("@") for line in lines if line.strip() and not line.startswith("#")]
    raise SystemExit(
        "Error: No accounts specified. Create {} with one @handle per line, "
        "or use --accounts @user1 @user2".format(ACCOUNTS_FILE)
    )


def fetch_tweets(username: str, since: datetime) -> List[dict]:
    """Fetch recent tweets from a user via Twitter syndication endpoint."""
    tweets = []
    try:
        url = SYNDICATION_URL.format(username)
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()

        # Extract __NEXT_DATA__ JSON from the page
        match = re.search(
            r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', resp.text, re.DOTALL
        )
        if not match:
            print("  Warning: Could not parse syndication page for @{}".format(username))
            return tweets

        data = json.loads(match.group(1))
        entries = data["props"]["pageProps"]["timeline"]["entries"]

        for entry in entries:
            if entry.get("type") != "tweet":
                continue
            tweet = entry["content"]["tweet"]

            # Parse date
            created_str = tweet.get("created_at", "")
            if not created_str:
                continue
            try:
                created = parsedate_to_datetime(created_str)
            except Exception:
                continue

            if created < since:
                continue

            text = tweet.get("full_text", tweet.get("text", ""))
            screen_name = tweet.get("user", {}).get("screen_name", username)
            tweet_id = tweet.get("conversation_id_str", "")

            tweets.append({
                "author": "@{}".format(screen_name),
                "text": text,
                "date": created.isoformat(),
                "likes": tweet.get("favorite_count", 0) or 0,
                "retweets": tweet.get("retweet_count", 0) or 0,
                "url": "https://x.com/{}/status/{}".format(screen_name, tweet_id),
            })
    except Exception as e:
        print("  Warning: Could not fetch tweets for @{}: {}".format(username, e))
    return tweets


def main():
    parser = argparse.ArgumentParser(description="Capture tweets into an Obsidian digest")
    parser.add_argument("--accounts", nargs="+", help="@handles to fetch (overrides accounts file)")
    parser.add_argument("--hours", type=int, default=24, help="Look back N hours (default: 24)")
    args = parser.parse_args()

    accounts = load_accounts(args.accounts)
    since = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    print("Fetching tweets from {} accounts (last {}h)...".format(len(accounts), args.hours))

    all_tweets = []
    for account in accounts:
        tweets = fetch_tweets(account, since)
        all_tweets.extend(tweets)
        print("  @{}: {} tweets".format(account, len(tweets)))

    if not all_tweets:
        print("No tweets found in the time window.")
        return

    # Sort by likes descending
    all_tweets.sort(key=lambda t: t["likes"], reverse=True)

    # Format tweets for AI
    tweet_text = "\n\n".join(
        "**{author}** ({date})\n{text}\n{url} | likes: {likes} | retweets: {retweets}".format(**t)
        for t in all_tweets
    )

    print("Generating digest with AI...")
    digest_body = summarize(tweet_text, DIGEST_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")
    accounts_str = ", ".join("@{}".format(a) for a in accounts)

    note_lines = [
        "---",
        "type: twitter-digest",
        "date: {}".format(today),
        "accounts: [{}]".format(accounts_str),
        "tweet_count: {}".format(len(all_tweets)),
        "tags:",
        "  - source/twitter",
        "---",
        "",
        "# Twitter Digest - {}".format(today),
        "",
        "> [!info] Tracking {} accounts | {} tweets captured".format(len(accounts), len(all_tweets)),
        "",
        digest_body,
        "",
        "---",
        "",
        "## Raw Tweets",
        "",
    ]
    for t in all_tweets:
        text_preview = t["text"][:200] + ("..." if len(t["text"]) > 200 else "")
        note_lines.append("- **{}**: {} ([link]({}))".format(t["author"], text_preview, t["url"]))

    note = "\n".join(note_lines) + "\n"
    save_note("Sources/Twitter Digest - {}.md".format(today), note)
    print("Done! {} tweets digested.".format(len(all_tweets)))


if __name__ == "__main__":
    main()
