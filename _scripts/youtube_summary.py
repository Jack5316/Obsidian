"""Summarize a YouTube video into an Obsidian note."""

import argparse
import re
import json

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

from config import summarize, save_note

SUMMARY_PROMPT = """You are a research assistant. Given a YouTube video transcript, create a comprehensive
summary in markdown. Include:
1. **Key Takeaways** - 3-5 bullet points of the most important ideas
2. **Summary** - A detailed summary organized by topic
3. **Notable Quotes** - Any standout quotes worth remembering (with approximate timestamps)
4. **Related Topics** - Suggest related topics as [[wikilinks]] for Obsidian

Be thorough but concise. Do NOT include any YAML frontmatter or title heading -
start directly with the Key Takeaways section."""


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from a YouTube URL or return as-is if already an ID."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def get_metadata(video_id: str) -> dict:
    """Fetch video metadata using yt-dlp."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "title": info.get("title", "Unknown"),
        "channel": info.get("channel", info.get("uploader", "Unknown")),
        "duration": info.get("duration", 0),
        "description": (info.get("description", "") or "")[:500],
        "upload_date": info.get("upload_date", ""),
        "view_count": info.get("view_count", 0),
        "url": url,
    }


def get_transcript(video_id: str) -> str:
    """Fetch video transcript."""
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    lines = []
    for entry in transcript:
        minutes = int(entry.start // 60)
        seconds = int(entry.start % 60)
        lines.append(f"[{minutes:02d}:{seconds:02d}] {entry.text}")
    return "\n".join(lines)


def format_duration(seconds: int) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def main():
    parser = argparse.ArgumentParser(description="Summarize a YouTube video into an Obsidian note")
    parser.add_argument("video", help="YouTube URL or video ID")
    args = parser.parse_args()

    video_id = extract_video_id(args.video)
    print(f"Processing video: {video_id}")

    print("Fetching metadata...")
    meta = get_metadata(video_id)
    print(f"  Title: {meta['title']}")
    print(f"  Channel: {meta['channel']}")

    print("Fetching transcript...")
    try:
        transcript = get_transcript(video_id)
    except Exception as e:
        print(f"Warning: Could not fetch transcript ({e}). Summarizing from description only.")
        transcript = f"[No transcript available]\n\nVideo description:\n{meta['description']}"

    # Truncate very long transcripts to avoid token limits
    if len(transcript) > 50000:
        transcript = transcript[:50000] + "\n\n[Transcript truncated...]"

    print("Generating summary with AI...")
    context = f"Video: {meta['title']} by {meta['channel']}\nDuration: {format_duration(meta['duration'])}\n\nTranscript:\n{transcript}"
    summary_body = summarize(context, SUMMARY_PROMPT)

    upload_date = meta["upload_date"]
    if upload_date:
        upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"

    # Clean title for filename
    safe_title = re.sub(r'[\\/*?:"<>|]', "", meta["title"])[:80]

    # Build transcript callout
    transcript_lines = transcript.split("\n")
    quoted_lines = "\n".join("> " + line for line in transcript_lines[:200])
    if len(transcript_lines) > 200:
        quoted_lines += f"\n> \n> [Transcript truncated - {len(transcript_lines)} total lines]"

    note = f"""---
type: youtube-summary
title: "{meta['title']}"
channel: "{meta['channel']}"
url: {meta['url']}
duration: {format_duration(meta['duration'])}
date_published: {upload_date}
views: {meta['view_count']:,}
tags:
  - source/youtube
---

# {meta['title']}

> [!info] 📺 [{meta['channel']}]({meta['url']}) | {format_duration(meta['duration'])} | {meta['view_count']:,} views

{summary_body}

---

## Transcript

> [!abstract]- Full Transcript
{quoted_lines}
"""

    save_note(f"Sources/YT - {safe_title}.md", note)
    print("Done!")


if __name__ == "__main__":
    main()
