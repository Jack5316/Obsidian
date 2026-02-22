"""Summarize a PDF document into an Obsidian note.

Extracts text from PDF and generates structured summary with AI.
"""

import argparse
import re
import subprocess
from pathlib import Path

from config import summarize, save_note, VAULT_PATH

SUMMARY_PROMPT = """You are a research assistant analyzing a document. Create a comprehensive summary in markdown:

1. **Core Thesis / Main Argument** - What is the central claim or purpose?
2. **Key Points** - 5-7 bullet points of the most important ideas
3. **Arguments & Evidence** - How does the author support their claims?
4. **Key Definitions / Concepts** - Important terms introduced or used
5. **Critical Analysis** - Strengths, weaknesses, or notable perspectives
6. **Connections** - Suggest related topics as [[wikilinks]] for Obsidian

Be thorough but concise. If this is a technical paper, include key equations or results.
If philosophical, trace the logical structure of arguments.
Do NOT include any YAML frontmatter or title heading - start directly with Core Thesis."""


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF using python or command-line tools."""
    # Try pdftotext (poppler) first - best quality
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: try PyPDF2 / pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        if text.strip():
            return text
    except ImportError:
        pass

    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        if text.strip():
            return text
    except ImportError:
        pass

    raise SystemExit(
        "Error: Could not extract text from PDF. Install poppler (brew install poppler) "
        "or pypdf (pip install pypdf)."
    )


def extract_metadata(text: str, pdf_path: Path) -> dict:
    """Try to extract title and author from the PDF text."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Title is usually the first substantial line that isn't boilerplate
    title = pdf_path.stem
    skip_words = ["permission", "copyright", "license", "arxiv", "preprint", "published"]
    for line in lines[:10]:
        if len(line) > 10 and len(line) < 200 and not re.match(r"^\d", line):
            if not any(sw in line.lower() for sw in skip_words):
                title = line
                break

    # Look for author patterns
    author = ""
    for line in lines[:20]:
        if any(kw in line.lower() for kw in ["university", "institute", "department", "@"]):
            # Previous line is likely the author
            idx = lines.index(line)
            if idx > 0:
                author = lines[idx - 1]
            break

    return {"title": title, "author": author}


def main():
    parser = argparse.ArgumentParser(description="Summarize a PDF into an Obsidian note")
    parser.add_argument("pdf", help="Path to PDF file (relative to vault or absolute)")
    parser.add_argument("--title", help="Override title (otherwise extracted from PDF)")
    args = parser.parse_args()

    # Resolve path
    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = VAULT_PATH / pdf_path
    if not pdf_path.exists():
        raise SystemExit("Error: PDF not found: {}".format(pdf_path))

    print("Extracting text from: {}".format(pdf_path.name))
    text = extract_text_from_pdf(pdf_path)
    print("  Extracted {} characters".format(len(text)))

    meta = extract_metadata(text, pdf_path)
    title = args.title or meta["title"]
    author = meta["author"]
    print("  Title: {}".format(title))
    if author:
        print("  Author: {}".format(author))

    # Truncate very long documents
    if len(text) > 60000:
        text = text[:60000] + "\n\n[Document truncated...]"

    print("Generating summary with AI...")
    context = "Document: {}\n{}\n\n{}".format(
        title,
        "Author: {}".format(author) if author else "",
        text,
    )
    summary_body = summarize(context, SUMMARY_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[:80]

    note = """---
type: pdf-summary
title: "{title}"
author: "{author}"
source: "{filename}"
date_read: {today}
tags:
  - source/pdf
---

# {title}

> [!info] {author_line}Source: `{filename}` | {char_count:,} characters extracted

{summary}

---

*Summarized from [[{filename}]]*
""".format(
        title=title,
        author=author,
        filename=pdf_path.name,
        today=today,
        author_line="By {} | ".format(author) if author else "",
        char_count=len(text),
        summary=summary_body,
    )

    save_note("Sources/PDF - {}.md".format(safe_title), note)
    print("Done!")


from datetime import datetime

if __name__ == "__main__":
    main()
