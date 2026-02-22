#!/usr/bin/env python3
"""Web Search - Search the web via Brave or Tavily API.

Providers:
  brave  - BRAVE_API_KEY in .env. Free tier: 2000 queries/month.
  tavily - TAVILY_API_KEY in .env. Free tier: 1000 credits/month.
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path

import requests

from config import save_note, VAULT_PATH

BRAVE_API = "https://api.search.brave.com/res/v1/web/search"
TAVILY_API = "https://api.tavily.com/search"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def _load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        pass


def get_brave_key() -> str:
    """Get Brave API key from env."""
    _load_env()
    return os.environ.get("BRAVE_API_KEY", "").strip()


def get_tavily_key() -> str:
    """Get Tavily API key from env."""
    _load_env()
    return os.environ.get("TAVILY_API_KEY", "").strip()


def search_brave(query: str, count: int = 10) -> list:
    """Search web via Brave API. Returns list of {title, url, description}."""
    key = get_brave_key()
    if not key:
        raise ValueError("BRAVE_API_KEY required. Add to .env. Get key: https://api.search.brave.com/app/dashboard")
    resp = requests.get(
        BRAVE_API,
        params={"q": query, "count": min(count, 20)},
        headers={"Accept": "application/json", "X-Subscription-Token": key},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    raw = data.get("web", {}).get("results", [])
    return [{"title": r.get("title", ""), "url": r.get("url", ""), "description": r.get("description", "")} for r in raw]


def search_tavily(query: str, count: int = 10) -> list:
    """Search web via Tavily API. Returns list of {title, url, description}."""
    key = get_tavily_key()
    if not key:
        raise ValueError("TAVILY_API_KEY required. Add to .env. Get key: https://tavily.com")
    resp = requests.post(
        TAVILY_API,
        json={"query": query, "max_results": min(count, 20), "search_depth": "basic"},
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    raw = data.get("results", [])
    return [{"title": r.get("title", ""), "url": r.get("url", ""), "description": r.get("content", "")} for r in raw]


def search(query: str, count: int = 10, provider: str = "brave") -> list:
    """Search web via specified provider (brave or tavily)."""
    if provider == "tavily":
        return search_tavily(query, count)
    return search_brave(query, count)


def main():
    parser = argparse.ArgumentParser(
        description="Search the web via Brave or Tavily API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/web_search.py "Python asyncio tutorial"
  python3 _scripts/web_search.py "Claude API" --count 5 --save
  python3 _scripts/web_search.py "AI news" --provider tavily
""",
    )
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--count", "-n", type=int, default=10, help="Number of results (default 10)")
    parser.add_argument("--provider", "-p", choices=["brave", "tavily"], default="brave",
                        help="Search provider: brave (default) or tavily")
    parser.add_argument("--save", "-s", action="store_true", help="Save results to vault")
    args = parser.parse_args()

    q = " ".join(args.query)
    if not q:
        print("Provide a search query.")
        return 1

    print(f"Searching ({args.provider}): {q}")
    try:
        results = search(q, args.count, args.provider)
    except ValueError as e:
        print(str(e))
        return 1
    except requests.RequestException as e:
        print(f"Search failed: {e}")
        return 1

    if not results:
        print("No results.")
        return 0

    lines = [f"# Web Search: {q}", "", f"*{datetime.now().strftime('%Y-%m-%d %H:%M')}*", "", "---", ""]
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        url = r.get("url", "")
        desc = r.get("description", "")
        lines.append(f"## {i}. [{title}]({url})")
        lines.append("")
        if desc:
            lines.append(desc)
        lines.append("")

    out = "\n".join(lines)
    print(out)

    if args.save:
        safe = re.sub(r'[\\/*?:"<>|]', "", q)[:50] + ".md"
        save_note(f"Sources/Web Search - {safe}", out)

    return 0


if __name__ == "__main__":
    exit(main())
