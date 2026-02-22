#!/usr/bin/env python3
"""Detailed TopHub news scraper that follows section links for real news."""

import argparse
import datetime
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from config import summarize, save_note, VAULT_PATH, TRACKER

TOPHUB_URL = "https://tophub.today"
import random

REQUEST_DELAY = 5  # Longer delay
TIMEOUT = 20
MAX_RETRIES = 5

# Rotating user agents to avoid detection
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.2; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0"
]

def get_random_headers():
    """Get random headers to avoid detection"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": random.choice(["same-origin", "none"]),
        "Sec-Fetch-User": "?1",
        "Cache-Control": random.choice(["max-age=0", "no-cache"]),
        "TE": "trailers"
    }
    return headers

# Main news sections to scrape
NEWS_SECTIONS = {
    "微博热搜榜": "Weibo Hot Search",
    "微信24h热文榜": "WeChat 24h Hot Articles",
    "百度实时热点": "Baidu Real-Time Hotspots",
    "哔哩哔哩全站日榜": "Bilibili Site-Wide Daily",
    "36氪24小时热榜": "36Kr 24h Hot News"
}

SUMMARY_PROMPT = """You are a news editor. Given a list of Chinese news headlines from popular Chinese platforms,
create a concise English summary of each news item. For each item:

1. One-sentence summary of the headline in English
2. Translation of any important Chinese terms
3. Context about why this might be relevant or significant
4. Suggest related Obsidian [[wikilinks]] for key concepts

Format the response with each news item clearly separated. Focus on clarity and accessibility for English readers.

Do NOT include any YAML frontmatter or title heading - start directly with the first news item."""


def get_page_content(url: str) -> str:
    """Fetch page content from tophub.today with retry logic and better error handling."""
    time.sleep(REQUEST_DELAY + random.uniform(0, 2))
    try:
        for attempt in range(MAX_RETRIES):
            try:
                headers = get_random_headers()
                headers["Cookie"] = f"session={hash(time.time() + attempt)}"
                headers["Referer"] = TOPHUB_URL if url != TOPHUB_URL else None

                response = requests.get(url, headers=headers, timeout=TIMEOUT)

                if response.status_code == 200:
                    response.encoding = "utf-8"
                    return response.text
                elif response.status_code == 403:
                    print(f"Attempt {attempt + 1}: Forbidden. Trying again...")
                    time.sleep(3 + attempt * 2)
                else:
                    response.raise_for_status()
            except Exception as e:
                print(f"Attempt {attempt + 1}: Error - {e}")
                time.sleep(3 + attempt * 2)

        return ""
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


def parse_section_page(html: str, section_name: str) -> list:
    """Parse news items from a specific section page."""
    soup = BeautifulSoup(html, "html.parser")
    news_items = []

    # Find news containers
    # Try different selector strategies
    news_elements = soup.find_all("div", class_="I-w")
    if not news_elements:
        news_elements = soup.find_all("div", class_="s-I")
    if not news_elements:
        news_elements = soup.find_all("div", class_="c-I")
    if not news_elements:
        news_elements = soup.find_all("div", class_=re.compile(r"news|item"))

    if not news_elements:
        print(f"No news elements found for section {section_name}")
        return []

    for element in news_elements:
        try:
            # Extract title and link
            if element.name == "a":
                title = element.get_text(strip=True)
                link = element["href"]
            else:
                title_tag = element.find("a", href=True)
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                link = title_tag["href"]

            # Skip ads and invalid content
            if len(title) < 5 or len(title) > 200:
                continue

            # Skip duplicate titles
            seen_titles = set()
            if title in seen_titles:
                continue
            seen_titles.add(title)

            # Make relative links absolute
            if not link.startswith("http"):
                link = TOPHUB_URL + link

            # Skip non-news links
            if any(keyword in link.lower() for keyword in ["login", "register", "help", "manage"]):
                continue

            # Skip ads
            if any(keyword in title.lower() for keyword in ["广告", "推广", "AI总结", "让阅读更高效", "即时写作", "今日简报"]):
                continue

            news_items.append({
                "title": title,
                "link": link,
                "section": section_name,
                "source": "tophub.today",
            })

        except Exception as e:
            continue

    return news_items


def scrape_tophub() -> list:
    """Main scraping function for all sections."""
    all_news = []

    print(f"Fetching main page from {TOPHUB_URL}")
    html = get_page_content(TOPHUB_URL)
    if not html:
        print("Failed to fetch main page")
        return []

    soup = BeautifulSoup(html, "html.parser")

    # Find links to news sections
    all_links = soup.find_all("a", href=True)
    for chinese_name, english_name in NEWS_SECTIONS.items():
        print(f"Looking for section: {chinese_name} ({english_name})")

        found = False
        for link in all_links:
            if chinese_name in link.get_text(strip=True):
                section_url = link.get("href")
                if not section_url.startswith("http"):
                    section_url = TOPHUB_URL + section_url

                print(f"Scraping section: {english_name} - {section_url}")
                section_html = get_page_content(section_url)
                if not section_html:
                    print(f"Failed to scrape section: {english_name}")
                    continue

                section_news = parse_section_page(section_html, english_name)
                print(f"Found {len(section_news)} news items in {english_name}")
                all_news.extend(section_news)
                found = True
                break

        if not found:
            print(f"Section {chinese_name} not found")

    return all_news


def main():
    parser = argparse.ArgumentParser(
        description="TopHub News Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This scraper extracts real news headlines from popular Chinese news sections on tophub.today:
- Weibo Hot Search
- WeChat 24h Hot Articles
- Baidu Real-Time Hotspots
- Bilibili Site-Wide Daily Rankings
- 36Kr 24h Hot News
"""
    )
    parser.add_argument(
        "-c", "--count", type=int, default=30,
        help="Maximum number of news items to scrape per section"
    )

    args = parser.parse_args()

    if TRACKER:
        TRACKER.record_operation(
            script_name="tophub_news_detailed.py",
            operation_type="scrape_news",
            status="in_progress",
            metrics={"count": args.count}
        )

    try:
        print("Starting TopHub news scraping...")
        all_news = scrape_tophub()

        # Limit per section
        limited_news = []
        section_counts = {}
        for item in all_news:
            section = item["section"]
            if section not in section_counts:
                section_counts[section] = 0
            if section_counts[section] < args.count:
                section_counts[section] += 1
                limited_news.append(item)

        print(f"Total news items: {len(limited_news)}")

        if not limited_news:
            raise Exception("Failed to extract any news items")

        items_text = "\n\n".join(
            f"**{item['title']}**\nSource: {item['source']}\nSection: {item['section']}\nLink: {item['link']}"
            for item in limited_news
        )

        print(f"Generating AI summary for {len(limited_news)} items...")
        digest_body = summarize(items_text, SUMMARY_PROMPT)

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"News Digest - Comprehensive - {today}.md"

        table_rows = "\n".join(
            "| [{title}]({link}) | {section} | {source} |".format(
                title=item["title"][:60] + ("..." if len(item["title"]) > 60 else ""),
                link=item["link"],
                section=item["section"],
                source=item["source"]
            )
            for item in limited_news
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

> [!info] {count} news items from popular Chinese platforms

## News Items

| Title | Section | Source |
|-------|---------|--------|
{table}

---

## AI Summary

{digest}

---

*Generated from TopHub Chinese news aggregator*
""".format(
            today=today,
            count=len(limited_news),
            table=table_rows,
            digest=digest_body
        )

        save_note(f"Sources/{filename}", note)
        print(f"Digest saved to Sources/{filename}")

        if TRACKER:
            TRACKER.record_operation(
                script_name="tophub_news_detailed.py",
                operation_type="scrape_news",
                status="success",
                metrics={
                    "count": len(limited_news),
                    "sections": len(set(item["section"] for item in limited_news)),
                    "output_file": filename
                }
            )

    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="tophub_news_detailed.py",
                operation_type="scrape_news",
                status="failed",
                metrics={"error": str(e)}
            )
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
