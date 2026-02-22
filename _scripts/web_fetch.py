#!/usr/bin/env python3
"""Web Fetch - Fetch URL and extract content as markdown.

Generic URL-to-markdown extraction. Use for any web page; combine with article for AI summary.
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config import save_note, VAULT_PATH

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def fetch_html(url: str) -> str:
    """Fetch HTML from URL."""
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def html_to_markdown(soup: BeautifulSoup) -> str:
    """Convert HTML to readable markdown (headings, paragraphs, lists)."""
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()

    container = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_=re.compile(r"post|article|content|entry", re.I))
        or soup.body
    )
    if container is None:
        return ""

    lines = []
    for el in container.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "blockquote", "pre"]):
        if el.name and el.name.startswith("h"):
            level = int(el.name[1])
            lines.append(f"\n{'#' * level} {el.get_text(strip=True)}\n")
        elif el.name == "p":
            t = el.get_text(strip=True)
            if t:
                lines.append(t)
        elif el.name in ("ul", "ol"):
            for li in el.find_all("li"):
                lines.append(f"- {li.get_text(strip=True)}")
        elif el.name == "blockquote":
            for p in el.find_all("p") or [el]:
                lines.append(f"> {p.get_text(strip=True)}")
        elif el.name == "pre":
            lines.append(f"```\n{el.get_text()}\n```")

    text = "\n\n".join(lines)
    if not text:
        text = container.get_text(separator="\n", strip=True)
    return text.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Fetch URL and extract content as markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/web_fetch.py https://example.com/article
  python3 _scripts/web_fetch.py https://example.com --save
""",
    )
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--save", "-s", action="store_true", help="Save to vault")
    parser.add_argument("--max-chars", "-m", type=int, default=100000, help="Max chars (default 100000)")
    args = parser.parse_args()

    print(f"Fetching: {args.url}")
    html = fetch_html(args.url)
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else urlparse(args.url).path or "Untitled"
    meta = soup.find("meta", {"property": "og:title"})
    if meta and meta.get("content"):
        title = meta["content"].strip()

    print("Extracting content...")
    md = html_to_markdown(soup)
    if not md:
        print("Error: Could not extract content.")
        return 1

    if len(md) > args.max_chars:
        md = md[: args.max_chars] + "\n\n[Content truncated...]"

    print(f"Extracted {len(md)} chars")

    out = f"""# {title}

*Source: [{args.url}]({args.url})*

---

{md}

---
*Fetched {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    print(out[:500] + "..." if len(out) > 500 else out)

    if args.save:
        safe = re.sub(r'[\\/*?:"<>|]', "", title)[:60] + ".md"
        save_note(f"Sources/Web Fetch - {safe}", out)

    return 0


if __name__ == "__main__":
    exit(main())
