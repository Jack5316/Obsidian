#!/usr/bin/env python3
"""Quotes - Find inspirational quotes by subject or from famous people.

Uses Quotable.io API for famous quotes, plus AI for movie lines and thematic enrichment.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import requests

from config import summarize, save_note, VAULT_PATH

QUOTABLE_API = "https://api.quotable.io"
TIMEOUT = 15

QUOTES_PROMPT = """You are a curator of memorable quotes for inspiration. The user wants quotes on a topic or from a person.

Given the context below, generate 5-8 inspiring quotes. For each quote:
1. The exact quote text
2. Attribution (author, film, book, or source)
3. Brief note on why it resonates (one line)

Format as markdown:
> "Quote text here."
> — Author/Source (Film/Book if applicable)
> *Why it matters: one line*

If the user asked for movie lines, include 2-3 iconic film quotes that fit the theme.
If they asked for a specific person, prioritize their actual words; add 1-2 from similar thinkers if needed.
Be diverse: mix philosophy, literature, film, business, science.
Use [[wikilinks]] for key concepts where natural (Obsidian).
No YAML frontmatter. Start with a brief intro line, then the quotes."""

MOVIE_LINES_PROMPT = """You are a film buff who knows iconic movie lines. The user wants memorable film quotes for inspiration on a theme.

Generate 5-7 iconic movie quotes that fit the theme. For each:
1. The exact quote as spoken (or close)
2. Film title and year
3. Character who said it
4. Brief note on why it's memorable or inspiring

Format as markdown:
> "Quote text."
> — Character, *Film* (Year)
> *Why it resonates*

Choose from classic and modern films across genres. Be accurate with the quotes.
No YAML frontmatter."""


def fetch_quotable_quotes(query: str, limit: int = 8) -> List[dict]:
    """Fetch quotes from Quotable.io API by search query."""
    try:
        resp = requests.get(
            f"{QUOTABLE_API}/search/quotes",
            params={"query": query, "limit": limit},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        out = []
        for q in results:
            author = q.get("author", "Unknown")
            if isinstance(author, dict):
                author = author.get("name", "Unknown")
            out.append({
                "content": q.get("content", ""),
                "author": author,
                "tags": q.get("tags", []),
            })
        return out
    except Exception as e:
        print(f"  (Quotable API unavailable: {e})")
        return []


import json
import random
import pickle
from pathlib import Path

# 文件路径用于存储已显示过的引用
USED_QUOTES_FILE = Path("/Users/jack/Documents/Obsidian/AI_Vault/_scripts/used_quotes.pkl")

def load_local_quotes() -> List[dict]:
    """Load quotes from local database."""
    try:
        with open("/Users/jack/Documents/Obsidian/AI_Vault/_scripts/local_quotes.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"  (Failed to load local quotes: {e})")
        return []

def load_used_quotes() -> set:
    """Load used quotes from file."""
    if USED_QUOTES_FILE.exists():
        try:
            with open(USED_QUOTES_FILE, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"  (Failed to load used quotes: {e})")
    return set()

def save_used_quotes(used_quotes: set):
    """Save used quotes to file."""
    try:
        with open(USED_QUOTES_FILE, "wb") as f:
            pickle.dump(used_quotes, f)
    except Exception as e:
        print(f"  (Failed to save used quotes: {e})")

def fetch_random_quote(quote_type: Optional[str] = None) -> Optional[dict]:
    """Fetch a random quote from Quotable.io API or local database if API fails.
    Ensures no repeated quotes by tracking used ones.
    
    Args:
        quote_type: Type of quote to fetch (e.g., "诗词" for poems only, None for all types)
    """
    used_quotes = load_used_quotes()
    local_quotes = load_local_quotes()
    
    # 过滤引用类型
    if quote_type:
        available_local_quotes = [q for q in local_quotes if q.get("type", "") == quote_type]
        if not available_local_quotes:
            print(f"  (No quotes of type '{quote_type}' available in local database)")
            available_local_quotes = local_quotes  # fallback to all quotes
    else:
        available_local_quotes = local_quotes
    
    # 过滤已显示过的引用
    available_quotes = [q for q in available_local_quotes if q["content"] not in used_quotes]
    
    # 如果所有引用都已显示，重置已用引用集合
    if not available_quotes:
        print(f"  (All quotes of type '{quote_type}' shown, resetting used quotes list)")
        used_quotes = set()
        available_quotes = available_local_quotes
    
    # 随机选择一个引用
    selected_quote = random.choice(available_quotes)
    
    try:
        resp = requests.get(
            f"{QUOTABLE_API}/random",
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        q = resp.json()
        author = q.get("author", "Unknown")
        if isinstance(author, dict):
            author = author.get("name", "Unknown")
        api_quote = {
            "content": q.get("content", ""),
            "author": author,
            "tags": q.get("tags", []),
        }
        # 检查API返回的引用是否符合类型要求和是否已使用
        if (not quote_type or any(tag in ["poetry", "poem", "literature"] for tag in api_quote["tags"])) and api_quote["content"] not in used_quotes:
            used_quotes.add(api_quote["content"])
            save_used_quotes(used_quotes)
            return api_quote
        else:
            if quote_type:
                print(f"  (API returned a quote not matching type '{quote_type}', using local quote)")
            else:
                print("  (API returned a repeated quote, using local quote)")
            return selected_quote
    except Exception as e:
        print(f"  (Quotable API unavailable: {e})")
        print("  (Using local quote database)")
        return selected_quote


def fetch_quotable_by_author(author: str, limit: int = 8) -> List[dict]:
    """Fetch quotes from Quotable.io by author (search authors first, then quotes)."""
    try:
        # Search for author slug
        auth_resp = requests.get(
            f"{QUOTABLE_API}/search/authors",
            params={"query": author, "limit": 5},
            timeout=TIMEOUT,
        )
        auth_resp.raise_for_status()
        authors = auth_resp.json().get("results", [])
        if not authors:
            return []

        # Get quotes by first matching author slug
        slug = authors[0].get("slug", "")
        if not slug:
            return []

        quotes_resp = requests.get(
            f"{QUOTABLE_API}/quotes",
            params={"author": slug, "limit": limit},
            timeout=TIMEOUT,
        )
        quotes_resp.raise_for_status()
        data = quotes_resp.json()
        results = data.get("results", data) if isinstance(data, dict) else data
        if not isinstance(results, list):
            results = []

        out = []
        for q in results:
            a = q.get("author", author)
            if isinstance(a, dict):
                a = a.get("name", author)
            out.append({
                "content": q.get("content", ""),
                "author": a,
                "tags": q.get("tags", []),
            })
        return out
    except Exception as e:
        print(f"  (Quotable API unavailable: {e})")
        return []


def format_api_quotes(quotes: List[dict]) -> str:
    """Format API quotes as markdown."""
    if not quotes:
        return ""
    lines = ["## From Quotable.io", ""]
    for q in quotes:
        content = q.get("content", "").strip()
        author_name = q.get("author", "Unknown")
        if isinstance(author_name, dict):
            author_name = author_name.get("name", "Unknown")
        author_name = str(author_name)
        lines.append(f'> "{content}"')
        lines.append(f"> — {author_name}")
        lines.append("")
    return "\n".join(lines)


def sanitize_filename(s: str) -> str:
    """Make a safe filename from query string."""
    s = re.sub(r'[<>:"/\\|?*]', "", s)
    s = s.strip() or "quotes"
    return s[:60]


def main():
    parser = argparse.ArgumentParser(
        description="Find inspirational quotes by subject or from famous people",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/quotes.py "courage"
  python3 _scripts/quotes.py --author "Einstein"
  python3 _scripts/quotes.py "perseverance" --movie-lines
  python3 _scripts/quotes.py "success" --limit 10 --save
  python3 _scripts/quotes.py --random  # Get a random quote
  python3 _scripts/quotes.py --poem  # Get a random poem (for daily poetry)
""",
    )
    parser.add_argument(
        "--random", "-r",
        action="store_true",
        help="Get a random inspirational quote (ignores other arguments)",
    )
    parser.add_argument(
        "--poem", "-p",
        action="store_true",
        help="Get a random poem (Chinese classic poems)",
    )
    parser.add_argument(
        "topic",
        nargs="?",
        default=None,
        help="Subject or theme (e.g., courage, success, creativity)",
    )
    parser.add_argument(
        "--author", "-a",
        type=str,
        help="Famous person (e.g., Einstein, Churchill, Steve Jobs)",
    )
    parser.add_argument(
        "--movie-lines", "-m",
        action="store_true",
        help="Include iconic movie lines on the theme",
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=8,
        help="Max quotes to fetch from API (default: 8)",
    )
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="Save to vault (Sources/Quotes - TOPIC - YYYY-MM-DD.md)",
    )
    parser.add_argument(
        "--ai-only",
        action="store_true",
        help="Skip API, use AI only (curated quotes + movie lines)",
    )
    args = parser.parse_args()

    # Handle random quote request
    if args.random:
        print("Getting a random quote...")
        quote = fetch_random_quote()
        if quote:
            content = quote.get("content", "").strip()
            author_name = quote.get("author", "Unknown")
            print(f'"{content}" — {author_name}')
        else:
            print("Failed to fetch a random quote.")
        return
    
    # Handle poem request
    if args.poem:
        print("Getting a random poem...")
        quote = fetch_random_quote(quote_type="诗词")
        if quote:
            content = quote.get("content", "").strip()
            author_name = quote.get("author", "Unknown")
            print(f'"{content}" — {author_name}')
        else:
            print("Failed to fetch a random poem.")
        return

    query = args.author or args.topic or "inspiration"
    if not query.strip():
        query = "inspiration"

    print(f"Finding quotes for: {query}...")
    if args.movie_lines:
        print("  (Including movie lines)")

    # 1. Fetch from Quotable API (unless ai-only)
    api_quotes: List[dict] = []
    if not args.ai_only:
        if args.author:
            api_quotes = fetch_quotable_by_author(args.author, limit=args.limit)
        else:
            api_quotes = fetch_quotable_quotes(query, limit=args.limit)

    # 2. Build context for AI
    api_section = format_api_quotes(api_quotes) if api_quotes else ""
    if args.movie_lines:
        user_context = f"Topic: {query}\n\nInclude 2-3 iconic movie lines that fit this theme.\n\n{api_section}"
        prompt = QUOTES_PROMPT
    elif args.ai_only or not api_quotes:
        user_context = f"Topic/Person: {query}\n\nGenerate inspiring quotes. Include movie lines if they fit."
        prompt = QUOTES_PROMPT
    else:
        # We have API quotes; AI can add movie lines or enrich
        user_context = f"Topic/Person: {query}\n\nHere are quotes from the API:\n\n{api_section}\n\nAdd 2-3 iconic movie lines on the same theme, and optionally 1-2 more from thinkers/films. Format everything consistently."
        prompt = QUOTES_PROMPT

    # 3. AI enrichment
    print("  Curating with AI...")
    ai_content = summarize(user_context, prompt)

    # 4. Assemble output
    today = datetime.now().strftime("%Y-%m-%d")
    title = f"Quotes — {query}"
    note = f"""# {title}

*{today} · {query}*

---

{ai_content}

---
*Generated by /skill quotes*
"""

    print()
    print("—" * 40)
    print(note)
    print("—" * 40)

    if args.save:
        safe = sanitize_filename(query)
        path = f"Sources/Quotes - {safe} - {today}.md"
        save_note(path, note)


if __name__ == "__main__":
    main()
