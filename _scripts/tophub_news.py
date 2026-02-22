#!/usr/bin/env python3
"""Scrape recent news from tophub.today and save as Obsidian notes.

Supports multiple sections and customizable news categories.
"""

import argparse
import datetime
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from config import summarize, save_note, VAULT_PATH, TRACKER

# Configuration
TOPHUB_URL = "https://tophub.today"
REQUEST_DELAY = 1  # seconds between requests
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://tophub.today/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# News sections on tophub.today
NEWS_SECTIONS = {
    "comprehensive": "",
    "tech": "c/tech",
    "entertainment": "c/ent",
    "community": "c/community",
    "shopping": "c/shopping",
    "finance": "c/finance",
    "developer": "c/developer",
    "brief": "c/brief",
    "ai": "c/ai",
    "epaper": "c/epaper",
    "design": "c/design",
    "university": "c/university",
    "organization": "c/organization",
    "blog": "c/blog",
    "apple": "apple",
    "wxmp": "c/wxmp",
    "widget": "c/widget",
}

SUMMARY_PROMPT = """You are a news editor. Given a list of Chinese news headlines and links from tophub.today,
create a concise English summary of each news item. For each item:

1. One-sentence summary of the headline in English
2. Translation of any important Chinese terms
3. Context about why this might be relevant or significant
4. Suggest related Obsidian [[wikilinks]] for key concepts

Format the response with each news item clearly separated. Focus on clarity and accessibility for English readers.

Do NOT include any YAML frontmatter or title heading - start directly with the first news item."""


def get_page_content(url: str) -> str:
    """Fetch page content from tophub.today with rate limiting and retry logic."""
    time.sleep(REQUEST_DELAY)
    try:
        # Try multiple times with different headers
        for attempt in range(3):
            try:
                headers = HEADERS.copy()
                headers["Cookie"] = f"session={hash(time.time())}"
                response = requests.get(url, headers=headers, timeout=30)

                if response.status_code == 200:
                    response.encoding = "utf-8"
                    return response.text
                elif response.status_code == 403:
                    print(f"Attempt {attempt + 1}: Forbidden. Trying again...")
                    time.sleep(2 + attempt)
                else:
                    response.raise_for_status()
            except Exception as e:
                print(f"Attempt {attempt + 1}: Error - {e}")
                time.sleep(2 + attempt)

        return ""
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


def parse_news_items(html: str, section: str) -> List[Dict]:
    """Parse news items from HTML content."""
    soup = BeautifulSoup(html, "html.parser")
    news_items = []

    # Find news containers
    news_elements = soup.find_all("div", class_="I-w")
    if not news_elements:
        news_elements = soup.find_all("div", class_="s-I")

    for element in news_elements:
        # Extract title and link
        title_tag = element.find("a", class_="kb-lb-c")
        if not title_tag or not title_tag.get("href"):
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag.get("href")

        # Make relative links absolute
        if not link.startswith("http"):
            link = TOPHUB_URL + link

        # Extract metrics (views, comments, etc.)
        metrics = {}

        # Extract view count
        view_tag = element.find("span", class_="I-w-ib-c")
        if view_tag:
            view_text = view_tag.get_text(strip=True)
            # Parse view count like "100w" (1 million)
            view_text = re.sub(r"[^\d.]", "", view_text)
            if view_text:
                metrics["views"] = float(view_text)

        # Extract publish time
        time_tag = element.find("span", class_="I-w-ib-f")
        if time_tag:
            metrics["time"] = time_tag.get_text(strip=True)

        news_items.append({
            "title": title,
            "link": link,
            "section": section,
            "metrics": metrics,
            "source": "tophub.today",
        })

    return news_items


def fetch_news_by_section(section: str, section_code: str) -> List[Dict]:
    """Fetch news from a specific section."""
    print(f"Fetching news from section: {section}")

    if section_code:
        url = f"{TOPHUB_URL}/{section_code}"
    else:
        url = TOPHUB_URL

    html = get_page_content(url)
    if not html:
        if section_code:
            print(f"Falling back to main page for {section}")
            html = get_page_content(TOPHUB_URL)
        else:
            return []

    news_items = parse_news_items(html, section)
    print(f"Found {len(news_items)} news items in {section}")
    return news_items


def generate_news_digest(news_items: List[Dict], section_filter: Optional[str]) -> str:
    """Generate an AI summary of news items."""
    if not news_items:
        return "No news items found for the specified sections."

    # Format news items for AI
    items_text = "\n\n".join(
        f"**{item['title']}**\nSection: {item['section']}\nLink: {item['link']}"
        for item in news_items
    )

    print(f"Generating digest with AI ({len(news_items)} items)...")
    digest_body = summarize(items_text, SUMMARY_PROMPT)
    return digest_body


def save_news_digest(news_items: List[Dict], digest: str, section_filter: Optional[str]):
    """Save news digest to Obsidian vault."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if section_filter:
        filename = f"News Digest - {section_filter.capitalize()} - {today}.md"
    else:
        filename = f"News Digest - Comprehensive - {today}.md"

    # Build news table
    table_rows = "\n".join(
        "| [{title}]({link}) | {section} | {views} |".format(
            title=item["title"][:60] + ("..." if len(item["title"]) > 60 else ""),
            link=item["link"],
            section=item["section"],
            views=item["metrics"].get("views", "N/A"),
        )
        for item in news_items
    )

    note = """---
type: news-digest
date: {today}
source: tophub.today
section: {section}
article_count: {count}
tags:
  - source/news
  - source/tophub
---

# {title}

> [!info] {count} news items from tophub.today ({today})

## News Items

| Title | Section | Views |
|-------|---------|-------|
{table}

---

## AI Summary

{digest}

---

*Generated by AI on {today}*
""".format(
        today=today,
        section=section_filter or "Comprehensive",
        count=len(news_items),
        title=filename.replace(".md", ""),
        table=table_rows,
        digest=digest,
    )

    save_note(f"Sources/{filename}", note)
    print(f"Digest saved to Sources/{filename}")


def main():
    parser = argparse.ArgumentParser(description="Scrape news from tophub.today")
    parser.add_argument("-s", "--section", help="Specific section to scrape (comprehensive, tech, ai, etc.)")
    parser.add_argument("-o", "--output", help="Output filename")
    parser.add_argument("-n", "--count", type=int, default=50, help="Maximum number of news items per section")

    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="tophub_news.py",
            operation_type="scrape_news",
            status="in_progress",
            metrics={"section": args.section or "all", "count": args.count}
        )

    try:
        all_news = []

        if args.section:
            if args.section not in NEWS_SECTIONS:
                raise ValueError(f"Invalid section: {args.section}. Valid sections: {', '.join(NEWS_SECTIONS.keys())}")
            section_code = NEWS_SECTIONS[args.section]
            all_news.extend(fetch_news_by_section(args.section, section_code))
        else:
            # Fetch from all sections
            for section, section_code in NEWS_SECTIONS.items():
                section_news = fetch_news_by_section(section, section_code)
                all_news.extend(section_news[:args.count])

        # Remove duplicates
        seen_links = set()
        unique_news = []
        for item in all_news:
            if item["link"] not in seen_links:
                seen_links.add(item["link"])
                unique_news.append(item)

        # Apply section and count filters
        if args.section:
            unique_news = [item for item in unique_news if item["section"] == args.section]

        unique_news = unique_news[:args.count]

        print(f"Total unique news items: {len(unique_news)}")

        # Generate AI digest
        digest = generate_news_digest(unique_news, args.section)

        # Save to Obsidian
        save_news_digest(unique_news, digest, args.section)

        # Track operation completion
        if TRACKER:
            TRACKER.record_operation(
                script_name="tophub_news.py",
                operation_type="scrape_news",
                status="success",
                metrics={
                    "section": args.section or "all",
                    "count": len(unique_news),
                    "sections_fetched": len(NEWS_SECTIONS) if not args.section else 1
                }
            )

    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="tophub_news.py",
                operation_type="scrape_news",
                status="failed",
                metrics={"error": str(e)}
            )
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
