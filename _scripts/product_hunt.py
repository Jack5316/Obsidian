"""Product Hunt Digest - Find the best shiny new tools from Product Hunt.

Fetches the Product Hunt feed (RSS/Atom), parses top products, and uses AI
to curate the best shiny new tools worth your attention. Saves to Sources/.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from xml.etree import ElementTree as ET

import requests

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH

PH_FEED = "https://www.producthunt.com/feed"
NS = {"atom": "http://www.w3.org/2005/Atom"}

CURATE_PROMPT = """You are curating the best shiny new tools from Product Hunt for a developer and knowledge worker.

Given a list of recently launched products (name, tagline, maker, URL), produce a concise digest note:

1. **Top Picks** — Select 5–10 tools most valuable for: dev tools, AI/LLM workflows, productivity, Obsidian/knowledge work, and creative tools. Briefly explain why each stands out.
2. **Honorable Mentions** — 3–5 more worth a look, one-line each.
3. **Theme of the Day** — One sentence on what's trending (e.g., "AI agents and observability" or "design tools").

Use [[wikilinks]] for key concepts. No YAML frontmatter. Start directly with content.
Output in clean Markdown suitable for Obsidian. Be selective — quality over quantity."""


def fetch_feed(url: str = PH_FEED, max_items: int = 30) -> List[Dict]:
    """Fetch and parse Product Hunt Atom feed."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    root = ET.fromstring(resp.content)
    products = []
    for entry in root.findall(".//atom:entry", NS)[:max_items]:
        title_el = entry.find("atom:title", NS)
        link_el = entry.find("atom:link[@rel='alternate']", NS) or entry.find("atom:link", NS)
        content_el = entry.find("atom:content", NS)
        author_el = entry.find("atom:author/atom:name", NS)

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        url_val = link_el.get("href", "") if link_el is not None else ""
        author = author_el.text.strip() if author_el is not None and author_el.text else ""

        tagline = ""
        if content_el is not None and content_el.text:
            # Extract first <p> content (tagline); handle both raw and entity-encoded HTML
            text = content_el.text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            match = re.search(r"<p>\s*(.+?)\s*</p>", text, re.DOTALL)
            if match:
                tagline = re.sub(r"<[^>]+>", "", match.group(1)).strip()

        if title:
            products.append({
                "name": title,
                "tagline": tagline,
                "maker": author,
                "url": url_val,
            })

    return products


def build_raw_markdown(products: List[Dict]) -> str:
    """Build raw markdown list without AI curation."""
    lines = [
        "# Product Hunt Digest",
        "",
        f"*Fetched {datetime.now().strftime('%Y-%m-%d %H:%M')} from [Product Hunt](https://www.producthunt.com)*",
        "",
        "## Top Products",
        "",
    ]
    for p in products:
        lines.append(f"- **{p['name']}** — {p['tagline']}")
        lines.append(f"  - By {p['maker']} | [View]({p['url']})")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Find the best shiny new tools from Product Hunt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/product_hunt.py
  python3 _scripts/product_hunt.py --count 20 --no-ai
  python3 _scripts/product_hunt.py --print
""",
    )
    parser.add_argument(
        "-c", "--count",
        type=int,
        default=25,
        help="Max products to fetch (default: 25)",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip AI curation; output raw list only",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print to stdout instead of saving",
    )
    args = parser.parse_args()

    print(f"Fetching Product Hunt feed...")
    products = fetch_feed(max_items=args.count)
    if not products:
        print("No products found.")
        return 1

    print(f"Found {len(products)} products.")

    if args.no_ai:
        content = build_raw_markdown(products)
    else:
        raw_list = "\n\n".join(
            f"**{p['name']}** — {p['tagline']}\nBy {p['maker']} | {p['url']}"
            for p in products
        )
        print("Curating with AI...")
        content = summarize(raw_list, CURATE_PROMPT)

    if args.print:
        print(content)
        return 0

    date_str = datetime.now().strftime("%Y-%m-%d")
    path = f"Sources/Product Hunt Digest - {date_str}.md"
    save_note(path, content)
    print(f"Saved: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
