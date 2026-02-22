"""Summarize a web article/blog post into an Obsidian note."""

import argparse
import re
from urllib.parse import urlparse

import requests
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

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def fetch_html(url: str) -> str:
    """Fetch HTML content from a URL."""
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def extract_metadata(soup: BeautifulSoup, url: str) -> dict:
    """Extract article metadata from HTML."""

    def meta(attrs):
        tag = soup.find("meta", attrs=attrs)
        return tag["content"].strip() if tag and tag.get("content") else None

    # Title
    title = (
        meta({"property": "og:title"})
        or (soup.title.string.strip() if soup.title and soup.title.string else None)
        or (soup.find("h1").get_text(strip=True) if soup.find("h1") else None)
        or "Untitled"
    )

    # Author
    author = (
        meta({"name": "author"})
        or meta({"property": "article:author"})
        or meta({"property": "og:author"})
        or ""
    )

    # Date
    date = (
        meta({"property": "article:published_time"})
        or meta({"name": "date"})
        or meta({"name": "publish_date"})
        or ""
    )
    # Normalize to YYYY-MM-DD if it looks like ISO
    if date and len(date) >= 10:
        date = date[:10]

    # Site name
    site_name = meta({"property": "og:site_name"}) or urlparse(url).netloc

    return {
        "title": title,
        "author": author,
        "date": date,
        "site_name": site_name,
        "url": url,
    }


def extract_text(soup: BeautifulSoup) -> str:
    """Extract main article text from HTML."""
    # Remove non-content elements
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()

    # Try increasingly broad selectors
    container = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_=re.compile(r"post|article|content|entry", re.I))
        or soup.body
    )

    if container is None:
        return ""

    # Get text with paragraph breaks
    paragraphs = container.find_all(["p", "h1", "h2", "h3", "h4", "li", "blockquote", "pre"])
    if paragraphs:
        return "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    return container.get_text(separator="\n", strip=True)


def main():
    parser = argparse.ArgumentParser(description="Summarize a web article into an Obsidian note")
    parser.add_argument("url", help="Article URL")
    parser.add_argument("--title", help="Override article title")
    args = parser.parse_args()

    print(f"Fetching article: {args.url}")
    html = fetch_html(args.url)
    soup = BeautifulSoup(html, "html.parser")

    meta = extract_metadata(soup, args.url)
    if args.title:
        meta["title"] = args.title
    print(f"  Title: {meta['title']}")
    if meta["author"]:
        print(f"  Author: {meta['author']}")

    print("Extracting content...")
    text = extract_text(soup)
    if not text:
        print("Error: Could not extract any text from the page.")
        return

    # Truncate for token safety
    if len(text) > 60000:
        text = text[:60000] + "\n\n[Content truncated...]"

    print("Generating summary with AI...")
    author_line = f" by {meta['author']}" if meta["author"] else ""
    context = f"Article: {meta['title']}{author_line} ({meta['site_name']})\n\nContent:\n{text}"
    summary_body = summarize(context, SUMMARY_PROMPT)

    # Clean title for filename
    safe_title = re.sub(r'[\\/*?:"<>|]', "", meta["title"])[:80].strip()

    # Build original text callout
    text_lines = text.split("\n")
    quoted_lines = "\n".join("> " + line for line in text_lines[:200])
    if len(text_lines) > 200:
        quoted_lines += f"\n> \n> [Content truncated — {len(text_lines)} total lines]"

    # Author/date info line
    info_parts = [f"[{meta['site_name']}]({meta['url']})"]
    if meta["author"]:
        info_parts.append(meta["author"])
    if meta["date"]:
        info_parts.append(meta["date"])
    info_line = " | ".join(info_parts)

    # Frontmatter
    fm_lines = [
        "---",
        "type: article-summary",
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
        "  - source/article",
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

    save_note(f"Sources/Article - {safe_title}.md", note)
    print("Done!")


if __name__ == "__main__":
    main()
