"""Convert accumulated vault insights into Twitter/X threads.

Pulls from Sources (syntheses, digests), Atlas, Maps, and Inbox to produce
thread-ready tweets — each under 280 chars, hook-first, designed for engagement.
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from config import summarize, save_note, VAULT_PATH, TRACKER

# Note types to prioritize (highest insight density)
PRIORITY_TYPES = {"weekly-synthesis", "daily-synthesis", "self-reflection", "self-evolution", "essay"}


def collect_notes(
    days: int = 30,
    include_atlas: bool = True,
    include_maps: bool = True,
    include_inbox: bool = True,
    topic_keywords: Optional[List[str]] = None,
) -> List[dict]:
    """Collect notes from Sources, Atlas, Maps, and Inbox."""
    notes = []

    # Sources — recent digests and syntheses
    sources_dir = VAULT_PATH / "Sources"
    if sources_dir.exists():
        cutoff = datetime.now() - timedelta(days=days)
        for md_file in sources_dir.glob("*.md"):
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
            if mtime < cutoff:
                continue

            content = md_file.read_text(encoding="utf-8")
            note_type = "unknown"
            type_match = re.search(r"^type:\s*(.+)$", content, re.MULTILINE)
            if type_match:
                note_type = type_match.group(1).strip()

            body = content
            fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
            if fm_match:
                body = content[fm_match.end():]

            if topic_keywords:
                combined = (md_file.stem + " " + body).lower()
                if not any(kw.lower() in combined for kw in topic_keywords):
                    continue

            priority = 1 if note_type in PRIORITY_TYPES else 0
            notes.append({
                "filename": md_file.stem,
                "type": note_type,
                "source": "Sources",
                "date": mtime.strftime("%Y-%m-%d"),
                "content": body[:4000],
                "priority": priority,
            })

    # Atlas — permanent notes
    if include_atlas:
        atlas_dir = VAULT_PATH / "Atlas"
        if atlas_dir.exists():
            for md_file in atlas_dir.glob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                body = content
                fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
                if fm_match:
                    body = content[fm_match.end():]

                if topic_keywords:
                    combined = (md_file.stem + " " + body).lower()
                    if not any(kw.lower() in combined for kw in topic_keywords):
                        continue

                notes.append({
                    "filename": md_file.stem,
                    "type": "atlas",
                    "source": "Atlas",
                    "date": "",
                    "content": body[:3000],
                    "priority": 0,
                })

    # Maps — MOCs
    if include_maps:
        maps_dir = VAULT_PATH / "Maps"
        if maps_dir.exists():
            for md_file in maps_dir.glob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                body = content
                fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
                if fm_match:
                    body = content[fm_match.end():]

                if topic_keywords:
                    combined = (md_file.stem + " " + body).lower()
                    if not any(kw.lower() in combined for kw in topic_keywords):
                        continue

                notes.append({
                    "filename": md_file.stem,
                    "type": "moc",
                    "source": "Maps",
                    "date": "",
                    "content": body[:2000],
                    "priority": 0,
                })

    # Inbox — recent captures
    if include_inbox:
        inbox_dir = VAULT_PATH / "00 - Inbox"
        if inbox_dir.exists():
            cutoff = datetime.now() - timedelta(days=days)
            for md_file in inbox_dir.glob("*.md"):
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                if mtime < cutoff:
                    continue

                content = md_file.read_text(encoding="utf-8")
                body = content
                fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
                if fm_match:
                    body = content[fm_match.end():]

                if topic_keywords:
                    combined = (md_file.stem + " " + body).lower()
                    if not any(kw.lower() in combined for kw in topic_keywords):
                        continue

                notes.append({
                    "filename": md_file.stem,
                    "type": "inbox",
                    "source": "Inbox",
                    "date": mtime.strftime("%Y-%m-%d"),
                    "content": body[:3000],
                    "priority": 0,
                })

    notes.sort(key=lambda n: (-n["priority"], n["date"] or "0000-00-00"), reverse=True)
    return notes


def build_thread_prompt(topic: Optional[str], notes_text: str, tweet_count: int) -> str:
    """Build the system prompt for thread generation."""
    base = """You are a skilled Twitter/X thread writer. Your task is to convert the provided vault insights into a thread — a series of tweets that distill one compelling idea for a broad audience.

The notes come from the user's personal knowledge base: digests (ArXiv, HN, Reddit, news), weekly/daily syntheses, self-reflection, Atlas permanent notes, Maps of Content, essays, and Inbox captures.

**Thread requirements:**
1. **280 characters max per tweet** — Strict limit. Count carefully. No exceptions.
2. **Plain text only** — No markdown, no [[wikilinks]], no asterisks or underscores for emphasis. Clean copy-paste ready for Twitter.
3. **Hook in tweet 1** — First tweet must grab attention. Contrarian take, surprising fact, or bold claim. Make readers want to tap "Show more".
4. **One idea per tweet** — Each tweet is a complete thought. No mid-sentence breaks.
5. **Flow** — Tweets build on each other. Thread reads as one coherent argument or narrative.
6. **Voice** — Conversational, confident. First person where natural. This is personal insight made public.
7. **Length** — Aim for """ + str(tweet_count) + """ tweets. Quality over quantity; 6–12 tweets is typical.
8. **Land the ending** — Last tweet should feel like a conclusion: takeaway, call to action, or resonant close.

**Output format:** Return ONLY the thread, one tweet per line. Number each line (1., 2., 3., ...). No preamble, no explanation. Example:

1. Most people think X. They're wrong. Here's why.
2. The real insight is Y. Let me explain.
3. [continues...]

"""
    if topic:
        base += f"""**Topic focus:** The user requested a thread on: "{topic}". Center the thread on this theme. Pull only the most relevant insights.\n\n"""
    else:
        base += """**Topic:** No specific topic given. Identify the single most shareable, compelling insight from the notes and build the thread around it.\n\n"""

    base += """Do NOT include YAML frontmatter. Output only the numbered tweet list."""
    return base


def main():
    parser = argparse.ArgumentParser(
        description="Convert vault insights into Twitter/X threads"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Focus the thread on this topic (e.g., 'inverse problems', 'AI agents')",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Look back N days for Sources/Inbox (default: 30)",
    )
    parser.add_argument(
        "--tweets",
        type=int,
        default=10,
        help="Target number of tweets (default: 10)",
    )
    parser.add_argument(
        "--no-atlas",
        action="store_true",
        help="Exclude Atlas notes",
    )
    parser.add_argument(
        "--no-maps",
        action="store_true",
        help="Exclude Maps (MOCs)",
    )
    parser.add_argument(
        "--no-inbox",
        action="store_true",
        help="Exclude Inbox notes",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Custom filename title (default: derived from topic or date)",
    )
    args = parser.parse_args()

    topic_keywords = None
    if args.topic:
        topic_keywords = [w.strip() for w in args.topic.split(",")]

    if TRACKER:
        TRACKER.record_operation(
            script_name="thread_from_insights.py",
            operation_type="thread",
            status="in_progress",
            metrics={"topic": args.topic, "days": args.days},
        )

    print("Collecting notes...")
    notes = collect_notes(
        days=args.days,
        include_atlas=not args.no_atlas,
        include_maps=not args.no_maps,
        include_inbox=not args.no_inbox,
        topic_keywords=topic_keywords,
    )

    if not notes:
        print("No notes found matching criteria.")
        return

    print(f"Found {len(notes)} notes:")
    by_source = {}
    for n in notes:
        by_source[n["source"]] = by_source.get(n["source"], 0) + 1
    for src, count in sorted(by_source.items()):
        print(f"  {src}: {count}")

    notes_text = "\n\n---\n\n".join(
        "SOURCE: {filename} ({source}, type: {type}, date: {date})\n\n{content}".format(
            **n
        )
        for n in notes
    )

    if len(notes_text) > 80000:
        notes_text = notes_text[:80000] + "\n\n[Additional notes truncated...]"

    prompt = build_thread_prompt(args.topic, notes_text, args.tweets)
    print("Generating thread with AI...")
    thread_body = summarize(notes_text, prompt)

    today = datetime.now().strftime("%Y-%m-%d")

    # Determine output filename
    if args.title:
        safe_title = re.sub(r"[^\w\s-]", "", args.title).strip().replace(" ", " ")
        if not safe_title:
            safe_title = today
    elif args.topic:
        safe_title = re.sub(r"[^\w\s-]", "", args.topic)[:50].strip().replace(" ", " ")
        if not safe_title:
            safe_title = today
    else:
        safe_title = today

    source_index = "\n".join(
        "- [[{}]] ({})".format(n["filename"], n["source"]) for n in notes[:30]
    )
    if len(notes) > 30:
        source_index += f"\n- ... and {len(notes) - 30} more"

    note = f"""---
type: thread
date: {today}
topic: {args.topic or "open synthesis"}
note_count: {len(notes)}
tags:
  - thread
  - twitter
  - synthesis
---

# Thread: {safe_title}

{thread_body}

---

## Sources Referenced

{source_index}
"""

    out_path = f"Sources/Thread - {safe_title}.md"
    save_note(out_path, note)
    print(f"Done! Thread saved to {out_path}.")

    if TRACKER:
        TRACKER.record_operation(
            script_name="thread_from_insights.py",
            operation_type="thread",
            status="success",
            metrics={
                "topic": args.topic,
                "days": args.days,
                "notes_processed": len(notes),
                "output_file": out_path,
            },
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="thread_from_insights.py",
                operation_type="thread",
                status="failed",
                metrics={"error": str(e)},
            )
        import sys

        sys.exit(1)
