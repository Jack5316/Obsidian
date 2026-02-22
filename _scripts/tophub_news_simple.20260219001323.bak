#!/usr/bin/env python3
"""Simple TopHub news scraper with better error handling."""

import argparse
import datetime
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from config import summarize, save_note, VAULT_PATH, TRACKER

TOPHUB_URL = "https://tophub.today"
REQUEST_DELAY = 2  # seconds between requests
TIMEOUT = 10  # seconds per request
MAX_RETRIES = 2  # maximum retry attempts

# Realistic browser headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

SUMMARY_PROMPT = """You are a news editor. Given a list of recent Chinese news headlines from tophub.today,
create a concise English summary of each news item. For each item:

1. One-sentence summary of the headline in English
2. Translation of any important Chinese terms
3. Context about why this might be relevant or significant
4. Suggest related Obsidian [[wikilinks]] for key concepts

Format the response with each news item clearly separated. Focus on clarity and accessibility for English readers.
If any news items relate to global AI/chip/tech trends or have implications beyond the Chinese market (e.g., semiconductor policy, AI regulation, ethics debates), note these cross-domain connections.
Do NOT include any YAML frontmatter or title heading - start directly with the first news item."""


def get_page_content(url: str) -> str:
    """Fetch page content from tophub.today with retry logic and better error handling."""
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(REQUEST_DELAY)
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            if response.status_code == 200:
                response.encoding = "utf-8"
                return response.text
            else:
                print(f"Attempt {attempt + 1}: Status code {response.status_code}")
                continue
        except Exception as e:
            print(f"Attempt {attempt + 1}: Error - {e}")
            continue
    return ""


NEWS_SOURCES = {
    "微博", "知乎", "微信", "百度", "36氪", "虎嗅网", "IT之家",
    "机器之心", "量子位", "Readhub", "腾讯新闻", "少数派",
    "第一财经", "华尔街见闻", "新浪财经新闻", "雪球",
    "GitHub", "Product Hunt", "掘金",
}


def parse_news_items(html: str) -> list:
    """Parse news items from the main page.

    tophub.today structure (2025+): each source is a div.cc-cd card containing
    div.cc-cd-lb (source name) and div.cc-cd-cb-ll items (rank + title + extra).
    Items are wrapped in <a> tags with links.
    """
    soup = BeautifulSoup(html, "html.parser")
    news_items = []
    seen_titles = set()

    for card in soup.find_all("div", class_="cc-cd"):
        try:
            lb = card.find("div", class_="cc-cd-lb")
            source_name = lb.get_text(strip=True) if lb else ""

            # Only include news-relevant sources
            if source_name not in NEWS_SOURCES:
                continue

            for a_tag in card.find_all("a", href=True):
                item_div = a_tag.find("div", class_="cc-cd-cb-ll")
                if not item_div:
                    continue

                title_span = item_div.find("span", class_="t")
                title = title_span.get_text(strip=True) if title_span else ""

                if not title or len(title) < 4 or len(title) > 200:
                    continue

                # Skip ads / promo text
                if any(kw in title for kw in ("广告", "推广", "AI总结", "让阅读更高效", "即时写作", "今日简报")):
                    continue

                if title in seen_titles:
                    continue
                seen_titles.add(title)

                link = a_tag["href"]
                if not link.startswith("http"):
                    link = TOPHUB_URL + link

                extra_span = item_div.find("span", class_="e")
                extra = extra_span.get_text(strip=True) if extra_span else ""

                news_items.append({
                    "title": title,
                    "link": link,
                    "section": "comprehensive",
                    "source": source_name,
                    "extra": extra,
                })
        except Exception:
            continue

    return news_items


def main():
    parser = argparse.ArgumentParser(
        description="Simple TopHub News Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-c", "--count", type=int, default=30, help="Maximum number of news items to scrape"
    )
    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="tophub_news_simple.py",
            operation_type="scrape_news",
            status="in_progress",
            metrics={"count": args.count}
        )

    try:
        print(f"Fetching news from {TOPHUB_URL}...")
        html = get_page_content(TOPHUB_URL)

        if not html:
            raise Exception("Failed to fetch page content after multiple attempts")

        news_items = parse_news_items(html)[:args.count]
        print(f"Found {len(news_items)} news items")

        if not news_items:
            raise Exception("Failed to extract any news items from the page")

        # Generate AI summary
        items_text = "\n\n".join(
            f"**{item['title']}**\nSource: {item['source']}\nLink: {item['link']}"
            for item in news_items
        )

        print(f"Generating AI summary for {len(news_items)} items...")
        digest_body = summarize(items_text, SUMMARY_PROMPT)

        # Save to Obsidian
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"News Digest - Comprehensive - {today}.md"

        table_rows = "\n".join(
            "| [{title}]({link}) | {source} |".format(
                title=item["title"][:60] + ("..." if len(item["title"]) > 60 else ""),
                link=item["link"],
                source=item["source"]
            )
            for item in news_items
        )

        note = """---
type: news-digest
date: {today}
source: tophub.today
section: comprehensive
article_count: {count}
tags:
  - source/news
  - source/tophub
---

# News Digest - Comprehensive - {today}

> [!info] {count} news items from tophub.today

## News Items

| Title | Source |
|-------|--------|
{table}

---

## AI Summary

{digest}

---

*Generated from TopHub Chinese news aggregator*
""".format(
            today=today,
            count=len(news_items),
            table=table_rows,
            digest=digest_body
        )

        save_note(f"Sources/{filename}", note)
        print(f"Digest saved to Sources/{filename}")

        # Track operation completion
        if TRACKER:
            TRACKER.record_operation(
                script_name="tophub_news_simple.py",
                operation_type="scrape_news",
                status="success",
                metrics={"count": len(news_items)}
            )

    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="tophub_news_simple.py",
                operation_type="scrape_news",
                status="failed",
                metrics={"error": str(e)}
            )
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
