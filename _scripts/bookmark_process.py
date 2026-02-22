"""Process saved URLs into structured Obsidian notes."""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from article_summary import fetch_html, extract_metadata, extract_text
from bs4 import BeautifulSoup
from config import summarize, save_note

SUMMARY_PROMPT = """You are a research assistant. Given a web article, create a comprehensive
summary in markdown. Include:
1. **Key Takeaways** - 3-5 bullet points of the most important ideas
2. **Summary** - A detailed summary organized by topic
3. **Notable Quotes** - Any standout quotes worth remembering
4. **Related Topics** - Suggest related topics as [[wikilinks]] for Obsidian

If you notice connections to other domains (AI, science, philosophy, business, etc.),
briefly note them — but only if genuinely interesting.

Be thorough but concise. Do NOT include any YAML frontmatter or title heading —
start directly with the Key Takeaways section."""


def parse_url_file(path: Path) -> List[Tuple[str, Optional[str]]]:
    """Parse file: one URL per line, optional title after tab or pipe."""
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = re.split(r"\t|\|", line, maxsplit=1)
            url = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else None
            if url.startswith("http://") or url.startswith("https://"):
                items.append((url, title))
    return items


def process_url(url: str, title_override: Optional[str] = None) -> bool:
    """Fetch, extract, summarize one URL and save as note. Returns True on success."""
    try:
        print(f"Fetching: {url}")
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        meta = extract_metadata(soup, url)
        if title_override:
            meta["title"] = title_override
        print(f"  Title: {meta['title']}")

        text = extract_text(soup)
        if not text:
            print("  Error: Could not extract any text.")
            return False

        if len(text) > 60000:
            text = text[:60000] + "\n\n[Content truncated...]"

        print("  Generating summary...")
        author_line = f" by {meta['author']}" if meta["author"] else ""
        context = f"Article: {meta['title']}{author_line} ({meta['site_name']})\n\nContent:\n{text}"
        summary_body = summarize(context, SUMMARY_PROMPT)

        safe_title = re.sub(r'[\\/*?:"<>|]', "", meta["title"])[:80].strip()

        text_lines = text.split("\n")
        quoted_lines = "\n".join("> " + line for line in text_lines[:200])
        if len(text_lines) > 200:
            quoted_lines += f"\n> \n> [Content truncated — {len(text_lines)} total lines]"

        info_parts = [f"[{meta['site_name']}]({meta['url']})"]
        if meta["author"]:
            info_parts.append(meta["author"])
        if meta["date"]:
            info_parts.append(meta["date"])
        info_line = " | ".join(info_parts)

        fm_lines = [
            "---",
            "type: bookmark",
            f'title: "{meta["title"]}"',
        ]
        if meta["author"]:
            fm_lines.append(f'author: "{meta["author"]}"')
        fm_lines += [
            f"url: {meta['url']}",
            f'site: "{meta["site_name"]}"',
        ]
        if meta["date"]:
            fm_lines.append(f"date_published: {meta['date']}")
        fm_lines += [
            "tags:",
            "  - source/bookmark",
            "---",
        ]
        frontmatter = "\n".join(fm_lines)

        note = f"""{frontmatter}

# {meta['title']}

> [!info] {info_line}

{summary_body}

---

## Original Text

> [!abstract]- Full Article Text
{quoted_lines}
"""

        save_note(f"Sources/Bookmark - {safe_title}.md", note)
        print("  Done!")
        return True

    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Process saved URLs into structured Obsidian notes"
    )
    parser.add_argument("urls", nargs="*", help="URL(s) to process")
    parser.add_argument("--file", "-f", help="File with URLs (one per line)")
    parser.add_argument("--limit", "-n", type=int, help="Max URLs to process (file mode)")
    parser.add_argument("--title", "-t", help="Override title (single-URL mode only)")
    args = parser.parse_args()

    items: List[Tuple[str, Optional[str]]] = []

    if args.file:
        path = Path(args.file)
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.exists():
            print(f"Error: File not found: {path}")
            sys.exit(1)
        items = parse_url_file(path)
        if args.limit:
            items = items[: args.limit]
    elif args.urls:
        title = args.title if len(args.urls) == 1 else None
        items = [(u, title) for u in args.urls]
    else:
        parser.print_help()
        sys.exit(1)

    if not items:
        print("No URLs to process.")
        sys.exit(0)

    success = 0
    failed = 0
    for url, title in items:
        if process_url(url, title):
            success += 1
        else:
            failed += 1

    print(f"\nProcessed: {success} succeeded, {failed} failed")


if __name__ == "__main__":
    main()
