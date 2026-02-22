"""Publish an Obsidian note to Bear Blog using browser automation."""

import argparse
import re
from pathlib import Path

import mechanicalsoup

from config import BEARBLOG_USER, BEARBLOG_PASSWORD, VAULT_PATH

BEAR_BLOG_URL = "https://bearblog.dev"



# All recognized BearBlog header fields
BEAR_FIELDS = [
    "title", "link", "alias", "canonical_url", "published_date",
    "is_page", "meta_description", "meta_image", "lang", "tags",
    "make_discoverable",
]


def parse_note(filepath: Path) -> dict:
    """Read an Obsidian note and extract frontmatter + body."""
    content = filepath.read_text(encoding="utf-8")

    # Extract YAML frontmatter
    frontmatter = {}
    body = content
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                frontmatter[key.strip()] = val.strip().strip('"').strip("'")
        body = content[fm_match.end():]

    # Extract title from frontmatter or first heading
    title = frontmatter.get("title", "")
    if not title:
        heading_match = re.match(r"^#\s+(.+)$", body, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1)
            body = body[:heading_match.start()] + body[heading_match.end():]

    # Convert Obsidian wikilinks to standard markdown links
    body = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"[\2](\1)", body)
    body = re.sub(r"\[\[([^\]]+)\]\]", r"\1", body)

    # Strip Obsidian callouts to blockquotes
    body = re.sub(r"> \[!(\w+)\][+-]?\s*", "> ", body)

    tags = frontmatter.get("tags", "").replace("[", "").replace("]", "")

    # Collect all BearBlog header fields from frontmatter
    header = {"title": title or filepath.stem}
    if tags:
        header["tags"] = tags
    for field in BEAR_FIELDS:
        if field in ("title", "tags"):
            continue
        if field in frontmatter:
            header[field] = frontmatter[field]

    return {
        "title": header["title"],
        "body": body.strip(),
        "header": header,
    }


def get_blog_slug(browser: mechanicalsoup.StatefulBrowser) -> str:
    """Extract the blog slug from the dashboard page."""
    page = browser.page
    posts_link = page.find("a", string="Posts")
    if posts_link and posts_link.get("href"):
        return posts_link["href"].split("/dashboard/")[0].lstrip("/")
    raise SystemExit("Error: Could not determine blog slug from dashboard.")


def login(browser: mechanicalsoup.StatefulBrowser) -> str:
    """Log into Bear Blog. Returns blog slug."""
    if not BEARBLOG_USER or not BEARBLOG_PASSWORD:
        raise SystemExit("Error: Set BEARBLOG_USER and BEARBLOG_PASSWORD in .env")

    browser.open("{}/accounts/login/".format(BEAR_BLOG_URL))
    browser.select_form('form[action="/accounts/login/"]')
    browser["login"] = BEARBLOG_USER
    browser["password"] = BEARBLOG_PASSWORD
    browser.submit_selected()

    if "dashboard" not in browser.url:
        raise SystemExit("Error: Login failed. Check your Bear Blog credentials.")
    print("Logged into Bear Blog.")

    slug = get_blog_slug(browser)
    print("  Blog slug: {}".format(slug))
    return slug


def build_header_content(header: dict) -> str:
    """Build BearBlog header_content string from a dict of fields."""
    lines = []
    # title first, then the rest in stable order
    if "title" in header:
        lines.append("title: {}".format(header["title"]))
    for field in BEAR_FIELDS:
        if field == "title" or field not in header:
            continue
        lines.append("{}: {}".format(field, header[field]))
    return "\n".join(lines)


def create_post(browser: mechanicalsoup.StatefulBrowser, slug: str,
                header: dict, body: str, is_draft: bool) -> str:
    """Create a new post on Bear Blog.

    Bear Blog form fields:
      - publish: hidden, "true" to publish / "false" for draft
      - header_content: Bear Blog frontmatter (title, tags, etc.)
      - body_content: markdown body
    """
    new_post_url = "{}/{}/dashboard/posts/new/".format(BEAR_BLOG_URL, slug)
    browser.open(new_post_url)
    browser.select_form('form[method="POST"]')

    browser["header_content"] = build_header_content(header)
    browser["body_content"] = body
    browser["publish"] = "false" if is_draft else "true"

    browser.submit_selected()
    post_url = browser.url
    return post_url


def main():
    parser = argparse.ArgumentParser(description="Publish an Obsidian note to Bear Blog")
    parser.add_argument("note", help="Path to the Obsidian note (relative to vault or absolute)")
    parser.add_argument("--draft", action="store_true", help="Save as draft (don't publish)")
    parser.add_argument("--title", help="Override post title")
    parser.add_argument("--link", help="Custom URL slug (e.g. my-cool-post)")
    parser.add_argument("--tags", help="Comma-separated tags (e.g. AI, books)")
    parser.add_argument("--discoverable", action="store_true", default=None,
                        help="Make post discoverable on BearBlog feed")
    parser.add_argument("--no-discoverable", dest="discoverable", action="store_false",
                        help="Hide from BearBlog feed")
    parser.add_argument("--lang", help="Post language (e.g. en, zh)")
    args = parser.parse_args()

    # Resolve note path
    note_path = Path(args.note)
    if not note_path.is_absolute():
        note_path = VAULT_PATH / note_path
    if not note_path.exists():
        raise SystemExit("Error: Note not found: {}".format(note_path))

    print("Reading note: {}".format(note_path))
    note = parse_note(note_path)
    header = note["header"]

    # Apply CLI overrides
    if args.title:
        header["title"] = args.title
    if args.link:
        header["link"] = args.link
    if args.tags:
        header["tags"] = args.tags
    if args.discoverable is not None:
        header["make_discoverable"] = str(args.discoverable).lower()
    if args.lang:
        header["lang"] = args.lang

    print("  Title: {}".format(header["title"]))
    print("  Header: {}".format(
        ", ".join("{}: {}".format(k, v) for k, v in header.items())))
    print("  Body length: {} chars".format(len(note["body"])))

    browser = mechanicalsoup.StatefulBrowser()
    slug = login(browser)

    status = "draft" if args.draft else "published"
    print("Creating post ({})...".format(status))

    post_url = create_post(browser, slug, header, note["body"], args.draft)
    print("Done! Post URL: {}".format(post_url))


if __name__ == "__main__":
    main()
