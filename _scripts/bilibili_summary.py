#!/usr/bin/env python3
"""Summarize a Bilibili video into an Obsidian note.

Fetches video metadata and subtitles using Bilibili API and creates
structured notes with AI-generated summaries.
"""

import argparse
import re
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from urllib.parse import quote, urlparse, parse_qs

from config import summarize, save_note, VAULT_PATH, TRACKER


# Rate limiter to avoid API rate limiting
class RateLimiter:
    """Simple rate limiter to control API calls."""
    def __init__(self, requests_per_minute=30):
        self.requests = []
        self.rpm = requests_per_minute

    def acquire(self):
        """Acquire a rate limit token with proper waiting."""
        now = time.time()
        # Remove old requests
        self.requests = [t for t in self.requests if now - t < 60]
        if len(self.requests) >= self.rpm:
            sleep_time = 60 - (now - self.requests[0])
            time.sleep(sleep_time + 0.1)
        self.requests.append(time.time())


rate_limiter = RateLimiter()


def extract_bvid(url_or_id: str) -> str:
    """Extract BV ID from Bilibili URL or input string.

    Handles various Bilibili URL patterns and direct BV ID inputs.
    """
    # If already looks like a BV ID
    if re.match(r'^BV[a-zA-Z0-9]{10,}$', url_or_id):
        return url_or_id

    # Extract from various URL patterns
    patterns = [
        r'(?:BV|bv)[a-zA-Z0-9]{10,}',
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group().upper()

    raise ValueError(f"Cannot extract BV ID from: {url_or_id}")


def get_video_info(bvid: str) -> Dict:
    """Fetch video metadata from Bilibili API."""
    rate_limiter.acquire()

    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 0:
            raise Exception(f"Bilibili API error: {data.get('message', 'Unknown error')}")

        return data.get("data", {})

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch video info: {e}")


def get_subtitles(bvid: str, cid: int) -> Optional[str]:
    """Fetch and parse video subtitles."""
    rate_limiter.acquire()

    url = f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 0:
            return None

        page_data = data.get("data", {})
        subtitle_info = page_data.get("subtitle", {})
        subtitles = subtitle_info.get("subtitles", [])

        if not subtitles:
            return None

        # Try to find Chinese subtitles first, then any other language
        subtitle = None
        for sub in subtitles:
            if sub.get("lan") == "zh-CN" or sub.get("lan") == "zh":
                subtitle = sub
                break
        if not subtitle:
            subtitle = subtitles[0]

        subtitle_url = subtitle.get("subtitle_url")
        if not subtitle_url:
            return None

        # Fetch subtitle content
        rate_limiter.acquire()
        sub_response = requests.get(subtitle_url, headers=headers, timeout=30)
        sub_response.raise_for_status()
        sub_data = sub_response.json()

        return format_subtitles(sub_data.get("body", []))

    except Exception as e:
        print(f"Warning: Failed to get subtitles: {e}")
        return None


def format_subtitles(subtitle_data: List) -> str:
    """Format subtitles with timestamps."""
    if not subtitle_data:
        return ""

    formatted = []
    for item in subtitle_data:
        start_time = item.get("from", 0)
        content = item.get("content", "")
        time_str = format_duration(start_time)
        formatted.append(f"[{time_str}] {content}")

    return "\n".join(formatted)


def format_duration(seconds: float) -> str:
    """Format duration from seconds to MM:SS or HH:MM:SS."""
    seconds = int(seconds)
    if seconds < 3600:
        return time.strftime("%M:%S", time.gmtime(seconds))
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


def format_subtitles_for_summary(subtitles: str) -> str:
    """Format subtitles for AI summary prompt."""
    if not subtitles:
        return "No subtitles available."

    # Truncate if too long (avoid exceeding token limits)
    max_lines = 200
    lines = subtitles.split("\n")
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines.append("... (subtitles truncated)")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Summarize a Bilibili video into Obsidian note.")
    parser.add_argument("url_or_id", help="Bilibili video URL or BV ID")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output")

    args = parser.parse_args()

    try:
        # Record operation start
        TRACKER.record_operation(
            script_name="bilibili_summary.py",
            operation_type="summarize_video",
            status="in_progress",
            metrics={"url_or_id": args.url_or_id}
        )

        if args.verbose:
            print(f"Processing: {args.url_or_id}")

        # Extract BV ID
        bvid = extract_bvid(args.url_or_id)
        if args.verbose:
            print(f"Extracted BV ID: {bvid}")

        # Fetch video info
        video_info = get_video_info(bvid)

        # Extract metadata
        title = video_info.get("title", "Unknown Title")
        description = video_info.get("desc", "")
        pubdate = datetime.fromtimestamp(video_info.get("pubdate", 0))
        duration = video_info.get("duration", 0)
        view_count = video_info.get("stat", {}).get("view", 0)
        danmaku_count = video_info.get("stat", {}).get("danmaku", 0)
        favorite_count = video_info.get("stat", {}).get("favorite", 0)
        coin_count = video_info.get("stat", {}).get("coin", 0)
        like_count = video_info.get("stat", {}).get("like", 0)
        share_count = video_info.get("stat", {}).get("share", 0)
        reply_count = video_info.get("stat", {}).get("reply", 0)
        uploader = video_info.get("owner", {}).get("name", "Unknown Uploader")
        uploader_mid = video_info.get("owner", {}).get("mid", "")
        tid = video_info.get("tid", 0)
        tname = video_info.get("tname", "")
        typename = video_info.get("typename", "")
        tags = [t.get("tag_name", "") for t in video_info.get("tags", [])]
        pic_url = video_info.get("pic", "")

        # Get first cid
        pages = video_info.get("pages", [])
        cid = pages[0].get("cid") if pages else 0

        if args.verbose:
            print(f"Video title: {title}")
            print(f"Uploader: {uploader}")
            print(f"Duration: {format_duration(duration)}")
            print(f"Views: {view_count:,}")

        # Get subtitles
        subtitles = get_subtitles(bvid, cid)

        # Prepare prompt for summary
        prompt = (
            f"You are a research assistant analyzing a Bilibili video. Given the video "
            f"transcript and metadata, create a comprehensive summary in markdown. Include:\n\n"
            f"1. **Video Overview** - Brief description of what the video covers\n"
            f"2. **Key Takeaways** - 3-5 bullet points of the most important ideas\n"
            f"3. **Detailed Summary** - A thorough summary organized by topic or timeline\n"
            f"4. **Notable Moments** - Any standout sections with approximate timestamps\n"
            f"5. **Memorable Quotes** - Impactful statements worth remembering (with timestamps if available)\n"
            f"6. **Context & Background** - Relevant context for understanding the content\n"
            f"7. **Related Concepts** - Suggest related topics as [[wikilinks]] for Obsidian\n"
            f"8. **Questions & Reflection** - Thought-provoking questions raised by the video\n\n"
            f"Be thorough but concise. If the video is in Chinese, maintain Chinese terminology "
            f"where appropriate but explain key concepts clearly.\n\n"
            f"**Video Metadata:**\n"
            f"- Title: {title}\n"
            f"- Uploader: {uploader}\n"
            f"- Duration: {format_duration(duration)}\n"
            f"- Views: {view_count:,}\n"
            f"- Description: {description[:200]}...\n"
            f"- Tags: {', '.join(tags[:5])}\n\n"
            f"**Subtitles:**\n"
            f"{format_subtitles_for_summary(subtitles or 'No subtitles available.')}\n"
        )

        # Generate summary
        if args.verbose:
            print("Generating summary...")

        # We need to pass an empty text since all the content is in the prompt
        summary = summarize("", prompt)

        # Prepare note content
        note_content = generate_note_content(
            title=title,
            uploader=uploader,
            uploader_mid=uploader_mid,
            url=f"https://www.bilibili.com/video/{bvid}",
            bvid=bvid,
            duration=duration,
            date_published=pubdate,
            date_summarized=datetime.now(),
            views=view_count,
            likes=like_count,
            coins=coin_count,
            favorites=favorite_count,
            danmaku=danmaku_count,
            shares=share_count,
            replies=reply_count,
            tid=tid,
            tname=tname,
            typename=typename,
            tags=tags,
            pic_url=pic_url,
            summary=summary,
            subtitles=subtitles,
            description=description
        )

        # Save to Obsidian
        # Clean filename first
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
        clean_title = clean_title.replace(' ', '-')
        file_name = f"Bilibili - {clean_title}.md"

        file_path = Path(VAULT_PATH) / "Sources" / file_name

        save_note(str(file_path), note_content)

        if args.verbose:
            print(f"Note saved to: {file_path}")

        # Record operation success
        TRACKER.record_operation(
            script_name="bilibili_summary.py",
            operation_type="summarize_video",
            status="success",
            metrics={
                "url_or_id": args.url_or_id,
                "bvid": bvid,
                "title": title,
                "uploader": uploader,
                "duration": duration,
                "views": view_count,
                "likes": like_count,
                "has_subtitles": subtitles is not None,
                "subtitle_length": len(subtitles) if subtitles else 0,
                "note_path": str(file_path)
            }
        )

        print(f"Successfully processed video: {title}")
        print(f"Note saved to: {file_path}")

    except Exception as e:
        print(f"Error: {e}")
        TRACKER.record_operation(
            script_name="bilibili_summary.py",
            operation_type="summarize_video",
            status="failed",
            metrics={"url_or_id": args.url_or_id},
            error=str(e)
        )


def generate_note_content(
    title: str,
    uploader: str,
    uploader_mid: str,
    url: str,
    bvid: str,
    duration: int,
    date_published: datetime,
    date_summarized: datetime,
    views: int,
    likes: int,
    coins: int,
    favorites: int,
    danmaku: int,
    shares: int,
    replies: int,
    tid: int,
    tname: str,
    typename: str,
    tags: List,
    pic_url: str,
    summary: str,
    subtitles: Optional[str],
    description: str
) -> str:
    """Generate Obsidian note content for Bilibili video."""

    frontmatter = (
        "---\n"
        f"type: bilibili-summary\n"
        f"title: \"{title}\"\n"
        f"uploader: \"{uploader}\"\n"
        f"url: {url}\n"
        f"bvid: {bvid}\n"
        f"duration: {format_duration(duration)}\n"
        f"date_published: {date_published.strftime('%Y-%m-%d')}\n"
        f"date_summarized: {date_summarized.strftime('%Y-%m-%d')}\n"
        f"views: {views:,}\n"
        f"likes: {likes:,}\n"
        f"coins: {coins:,}\n"
        f"favorites: {favorites:,}\n"
        f"danmaku: {danmaku:,}\n"
        f"shares: {shares:,}\n"
        f"replies: {replies:,}\n"
        f"tid: {tid}\n"
        f"tname: \"{tname}\"\n"
        f"typename: \"{typename}\"\n"
        f"tags:\n"
        f"  - source/bilibili\n"
        f"  - video\n"
    )

    for tag in tags:
        if tag:
            frontmatter += f"  - {tag}\n"

    frontmatter += "---\n\n"

    content = (
        f"# {title}\n\n"
        f"> [!info] 📺 [{uploader}](https://space.bilibili.com/{uploader_mid}) | {format_duration(duration)} | {views:,} views\n"
        f">\n"
        f"> **Stats**: 👍 {likes:,} | 🪙 {coins:,} | ⭐ {favorites:,} | 💬 {danmaku:,} danmaku\n\n"
        f"## AI Summary\n"
        f"{summary}\n"
        f"\n---\n\n"
        f"## Key Metadata\n"
        f"- **Video URL**: {url}\n"
        f"- **Upload Date**: {date_published.strftime('%Y-%m-%d')}\n"
        f"- **Video Type**: {typename}\n"
        f"- **Partition**: {tname}\n"
        f"- **BV ID**: {bvid}\n"
        f"- **Duration**: {format_duration(duration)}\n\n"
        f"## Tags\n"
    )

    for tag in tags:
        if tag:
            content += f"- {tag}\n"

    if description:
        content += f"\n## Video Description\n"
        content += f"{description}\n"

    if subtitles:
        content += f"\n---\n\n"
        content += f"## Subtitles\n\n"
        content += f"> [!abstract]- Full Subtitle Transcript\n"
        content += "\n".join(f"> {line}" for line in subtitles.split("\n"))

    return frontmatter + content


if __name__ == "__main__":
    main()
