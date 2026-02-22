"""Curate recent ArXiv papers by topic into an Obsidian digest note.

Uses the ArXiv API (free, no auth needed).
"""

import argparse
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from urllib.parse import quote

import requests

from config import summarize, save_note, VAULT_PATH, TRACKER

ARXIV_API = "http://export.arxiv.org/api/query"
TOPICS_FILE = VAULT_PATH / "_scripts" / "arxiv_topics.txt"

# Default topics if no file exists
DEFAULT_TOPICS = [
    "large language model",
    "transformer architecture",
    "VLSI design",
    "integrated circuit",
    "philosophy of mind",
]

DIGEST_PROMPT = """You are a research assistant. Given a list of recent ArXiv papers with their titles,
authors, and abstracts, create a digest organized by research theme. For each paper:
1. One-sentence plain-English summary of what the paper does/finds
2. Why it matters (significance)
3. Suggest related Obsidian [[wikilinks]] for key concepts

Group papers by theme. Highlight the most impactful papers.
If any papers have surprising connections to chip design/VLSI, philosophy of mind, or industry trends visible on Hacker News or Reddit, note these briefly in a "Cross-Domain Signals" section at the end.
Do NOT include any YAML frontmatter or title heading - start directly with the first theme group."""

ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


def load_topics(override: List[str] = None) -> List[str]:
    """Load search topics from file or CLI args."""
    if override:
        return override
    if TOPICS_FILE.exists():
        lines = TOPICS_FILE.read_text().splitlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith("#")]
    return DEFAULT_TOPICS


def search_arxiv(query: str, max_results: int = 10, days_back: int = 7) -> List[dict]:
    """Search ArXiv for recent papers matching a query."""
    params = {
        "search_query": 'all:"{}"'.format(query),
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    try:
        resp = requests.get(ARXIV_API, params=params, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print("  Warning: ArXiv query failed for '{}': {}".format(query, e))
        return []

    root = ET.fromstring(resp.text)
    papers = []
    cutoff = datetime.now() - timedelta(days=days_back)

    for entry in root.findall("atom:entry", ARXIV_NS):
        published_str = entry.findtext("atom:published", "", ARXIV_NS)
        if published_str:
            published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            if published.replace(tzinfo=None) < cutoff:
                continue

        title = entry.findtext("atom:title", "", ARXIV_NS).strip().replace("\n", " ")
        abstract = entry.findtext("atom:summary", "", ARXIV_NS).strip().replace("\n", " ")
        link = ""
        for lnk in entry.findall("atom:link", ARXIV_NS):
            if lnk.get("type") == "text/html":
                link = lnk.get("href", "")
                break
        if not link:
            link = entry.findtext("atom:id", "", ARXIV_NS)

        authors = [a.findtext("atom:name", "", ARXIV_NS) for a in entry.findall("atom:author", ARXIV_NS)]

        categories = [c.get("term", "") for c in entry.findall("atom:category", ARXIV_NS)]

        papers.append({
            "title": title,
            "authors": authors,
            "abstract": abstract[:500],
            "url": link,
            "published": published_str[:10],
            "categories": categories,
            "query": query,
        })

    return papers


def main():
    parser = argparse.ArgumentParser(description="Curate ArXiv papers into an Obsidian digest")
    parser.add_argument("--topics", nargs="+", help="Search topics (overrides topics file)")
    parser.add_argument("--days", type=int, default=7, help="Look back N days (default: 7)")
    parser.add_argument("--max", type=int, default=10, help="Max papers per topic (default: 10)")
    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="arxiv_digest.py",
            operation_type="curate_papers",
            status="in_progress",
            metrics={"days": args.days, "topics": len(args.topics) if args.topics else "default"}
        )

    topics = load_topics(args.topics)
    print("Searching ArXiv for {} topics (last {} days)...".format(len(topics), args.days))

    all_papers = []
    seen_urls = set()
    for topic in topics:
        papers = search_arxiv(topic, max_results=args.max, days_back=args.days)
        # Deduplicate
        for p in papers:
            if p["url"] not in seen_urls:
                seen_urls.add(p["url"])
                all_papers.append(p)
        print("  '{}': {} papers".format(topic, len(papers)))

    if not all_papers:
        print("No papers found. Try increasing --days or adjusting topics.")
        return

    # Format for AI
    papers_text = "\n\n".join(
        "**{title}**\nAuthors: {authors}\nCategories: {cats}\nPublished: {published}\nURL: {url}\n\nAbstract: {abstract}".format(
            title=p["title"],
            authors=", ".join(p["authors"][:5]),
            cats=", ".join(p["categories"][:3]),
            published=p["published"],
            url=p["url"],
            abstract=p["abstract"],
        )
        for p in all_papers
    )

    print("Generating digest with AI ({} papers)...".format(len(all_papers)))
    digest_body = summarize(papers_text, DIGEST_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")
    topics_str = ", ".join(topics)

    # Build papers table
    table_rows = "\n".join(
        "| [{title}]({url}) | {authors} | {published} | {cats} |".format(
            title=p["title"][:60] + ("..." if len(p["title"]) > 60 else ""),
            url=p["url"],
            authors=", ".join(p["authors"][:2]) + (" et al." if len(p["authors"]) > 2 else ""),
            published=p["published"],
            cats=", ".join(p["categories"][:2]),
        )
        for p in all_papers
    )

    note = """---
type: arxiv-digest
date: {today}
topics: [{topics}]
paper_count: {count}
tags:
  - source/arxiv
  - research
---

# ArXiv Digest - {today}

> [!info] {count} papers across {topic_count} topics (last {days} days)

## Papers

| Title | Authors | Date | Categories |
|-------|---------|------|------------|
{table}

---

## AI Summary

{digest}

---

*Searched topics: {topics}*
""".format(
        today=today,
        topics=topics_str,
        count=len(all_papers),
        topic_count=len(topics),
        days=args.days,
        table=table_rows,
        digest=digest_body,
    )

    save_note("Sources/ArXiv Digest - {}.md".format(today), note)
    print("Done! {} papers digested.".format(len(all_papers)))

    # Track operation completion
    if TRACKER:
        TRACKER.record_operation(
            script_name="arxiv_digest.py",
            operation_type="curate_papers",
            status="success",
            metrics={
                "days": args.days,
                "topics": len(topics),
                "papers_found": len(all_papers),
                "output_file": "Sources/ArXiv Digest - {}.md".format(today)
            }
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="arxiv_digest.py",
                operation_type="curate_papers",
                status="failed",
                metrics={"error": str(e)}
            )
        import sys
        sys.exit(1)
