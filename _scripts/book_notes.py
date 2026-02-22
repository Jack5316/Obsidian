"""Generate structured book notes from a title or Kindle clippings export.

Two modes:
  1. By title: AI generates comprehensive notes from its knowledge
  2. From Kindle: Parses My Clippings.txt and organizes highlights with AI
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List

from config import summarize, save_note, VAULT_PATH, TRACKER

BOOK_PROMPT = """You are a well-read intellectual assistant. Given a book title (and author if provided),
create comprehensive reading notes in markdown. Include:

1. **Overview** - What the book is about, its main thesis, and why it matters
2. **Key Ideas** - The 5-10 most important ideas, each with a brief explanation
3. **Chapter-by-Chapter Summary** - Brief summary of main chapters/sections
4. **Key Quotes** - Notable passages worth remembering
5. **Critical Analysis** - Strengths, weaknesses, and how it relates to other works
6. **Connections** - Related books, thinkers, and concepts as [[wikilinks]]
7. **Personal Takeaways** - Actionable insights or questions to reflect on

Be thorough, intellectually rigorous, and honest about the book's arguments.
If the book is philosophical, trace the logical structure. If technical, highlight key frameworks.
Do NOT include any YAML frontmatter or title heading - start directly with Overview."""

KINDLE_PROMPT = """You are a reading assistant. Given a collection of Kindle highlights from a book,
organize them into a structured note:

1. **Themes** - Group highlights by major theme or chapter
2. **Key Insights** - The most important highlighted passages with brief commentary
3. **Connections** - Suggest related concepts as [[wikilinks]]
4. **Questions** - Questions raised by the highlights worth exploring further

Preserve the original highlight text in blockquotes. Add your own brief commentary after each group.
Do NOT include any YAML frontmatter or title heading - start directly with the first theme."""


def parse_kindle_clippings(filepath: Path, book_filter: str = None) -> dict:
    """Parse Kindle My Clippings.txt file.

    Returns dict of {book_title: [highlights]}
    """
    content = filepath.read_text(encoding="utf-8-sig")
    entries = content.split("==========")

    books = {}
    for entry in entries:
        lines = [l.strip() for l in entry.strip().split("\n") if l.strip()]
        if len(lines) < 3:
            continue

        title_line = lines[0]
        # Extract book title (before the author in parentheses)
        title_match = re.match(r"(.+?)(?:\s*\(([^)]+)\))?\s*$", title_line)
        if not title_match:
            continue

        book_title = title_match.group(1).strip()
        author = title_match.group(2) or ""

        # The highlight text is everything after the metadata line
        highlight = "\n".join(lines[2:])
        if not highlight:
            continue

        key = book_title
        if key not in books:
            books[key] = {"author": author, "highlights": []}
        books[key]["highlights"].append(highlight)

    if book_filter:
        # Fuzzy match book title
        filter_lower = book_filter.lower()
        matched = {k: v for k, v in books.items() if filter_lower in k.lower()}
        return matched

    return books


def generate_from_title(title: str, author: str = ""):
    """Generate book notes from AI knowledge."""
    query = title
    if author:
        query = "{} by {}".format(title, author)

    print("Generating notes for: {}".format(query))
    notes_body = summarize(query, BOOK_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[:80]

    note = """---
type: book-notes
title: "{title}"
author: "{author}"
date_read: {today}
status: to-read
rating:
tags:
  - source/book
---

# {title}

> [!info] {author_line}Notes generated from AI knowledge

{body}

---

> [!warning] These notes are AI-generated from training data.
> Read the actual book for the full experience. Update with your own highlights and thoughts.
""".format(
        title=title,
        author=author,
        today=today,
        author_line="By {} | ".format(author) if author else "",
        body=notes_body,
    )

    save_note("Sources/Book - {}.md".format(safe_title), note)


def generate_from_kindle(clippings_path: Path, book_filter: str = None):
    """Generate book notes from Kindle highlights."""
    print("Parsing Kindle clippings: {}".format(clippings_path.name))
    books = parse_kindle_clippings(clippings_path, book_filter)

    if not books:
        if book_filter:
            raise SystemExit("Error: No highlights found for '{}'".format(book_filter))
        raise SystemExit("Error: No highlights found in clippings file.")

    print("Found {} books with highlights".format(len(books)))

    for book_title, data in books.items():
        author = data["author"]
        highlights = data["highlights"]
        print("\nProcessing: {} ({} highlights)".format(book_title, len(highlights)))

        highlights_text = "\n\n".join(
            "Highlight {}: {}".format(i + 1, h) for i, h in enumerate(highlights)
        )
        context = "Book: {}\nAuthor: {}\n\n{}".format(book_title, author, highlights_text)
        notes_body = summarize(context, KINDLE_PROMPT)

        today = datetime.now().strftime("%Y-%m-%d")
        safe_title = re.sub(r'[\\/*?:"<>|]', "", book_title)[:80]

        note = """---
type: book-notes
title: "{title}"
author: "{author}"
date_read: {today}
highlight_count: {count}
status: reading
rating:
tags:
  - source/book
  - source/kindle
---

# {title}

> [!info] By {author} | {count} Kindle highlights

{body}

---

## All Highlights

{highlights}
""".format(
            title=book_title,
            author=author,
            today=today,
            count=len(highlights),
            body=notes_body,
            highlights="\n\n".join("> {}".format(h) for h in highlights),
        )

        save_note("Sources/Book - {}.md".format(safe_title), note)

    print("\nDone! {} books processed.".format(len(books)))


def main():
    parser = argparse.ArgumentParser(description="Generate book notes for Obsidian")
    subparsers = parser.add_subparsers(dest="mode", help="Mode of operation")

    # Mode 1: From title
    title_parser = subparsers.add_parser("title", help="Generate notes from a book title")
    title_parser.add_argument("book_title", help="Book title")
    title_parser.add_argument("--author", default="", help="Author name")

    # Mode 2: From Kindle
    kindle_parser = subparsers.add_parser("kindle", help="Generate notes from Kindle clippings")
    kindle_parser.add_argument("clippings", help="Path to My Clippings.txt")
    kindle_parser.add_argument("--book", help="Filter to a specific book title")

    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        metrics = {}
        if args.mode == "title":
            metrics = {"book_title": args.book_title, "author": args.author}
        elif args.mode == "kindle":
            metrics = {"clippings_file": args.clippings, "book_filter": args.book or "all"}

        TRACKER.record_operation(
            script_name="book_notes.py",
            operation_type=args.mode,
            status="in_progress",
            metrics=metrics
        )

    try:
        if args.mode == "title":
            generate_from_title(args.book_title, args.author)
            if TRACKER:
                TRACKER.record_operation(
                    script_name="book_notes.py",
                    operation_type=args.mode,
                    status="success",
                    metrics={"book_title": args.book_title, "author": args.author}
                )
        elif args.mode == "kindle":
            clippings_path = Path(args.clippings)
            if not clippings_path.is_absolute():
                clippings_path = VAULT_PATH / clippings_path
            if not clippings_path.exists():
                raise SystemExit("Error: File not found: {}".format(clippings_path))
            generate_from_kindle(clippings_path, args.book)
            if TRACKER:
                TRACKER.record_operation(
                    script_name="book_notes.py",
                    operation_type=args.mode,
                    status="success",
                    metrics={"clippings_file": args.clippings, "book_filter": args.book or "all"}
                )
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="book_notes.py",
                operation_type=args.mode,
                status="failed",
                metrics={"error": str(e)}
            )
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
