"""Generate long-form essays from accumulated insights across the vault.

Pulls from Sources (syntheses, digests), Atlas, Maps, and Inbox to produce
coherent narrative essays — not bullet-point synthesis, but actual prose.
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from config import summarize, save_note, VAULT_PATH, TRACKER

# Note types to prioritize (highest insight density)
PRIORITY_TYPES = {"weekly-synthesis", "daily-synthesis", "self-reflection", "self-evolution"}

# Note types to skip
SKIP_TYPES = set()  # None for essay — we want synthesis notes


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

            # Topic filter
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

    # Sort: priority first, then by date
    notes.sort(key=lambda n: (-n["priority"], n["date"] or "0000-00-00"), reverse=True)
    return notes


def build_essay_prompt(topic: Optional[str], notes_text: str) -> str:
    """Build the system prompt for essay generation."""
    base = """You are a thoughtful essayist. Your task is to write a long-form essay — coherent narrative prose, not bullet points or lists — that synthesizes the accumulated insights from the provided notes.

The notes come from the user's personal knowledge base: digests (ArXiv, HN, Reddit, news, Twitter), weekly/daily syntheses, self-reflection, Atlas permanent notes, Maps of Content, and Inbox captures.

**Essay requirements:**
1. **Prose only** — Write in flowing paragraphs. No bullet lists, no "Key Points:" sections. This is an essay, not a summary.
2. **Thesis-driven** — Have a clear central argument or theme that threads through the piece.
3. **Synthesize, don't summarize** — Connect ideas across sources. Find the through-line. Surprise the reader with non-obvious connections.
4. **Voice** — Write in first person where natural. This is personal knowledge made legible.
5. **Length** — Aim for 800–1500 words. Substantial enough to develop an argument.
6. **Structure** — Introduction that hooks, body that develops, conclusion that lands. Use section headers (##) sparingly, only for major turns.
7. **Wikilinks** — Use [[note title]] to reference source notes where relevant. Be generous with connections.

"""
    if topic:
        base += f"""**Topic focus:** The user requested an essay on: "{topic}". Center the essay on this theme. Pull only the most relevant insights from the notes; ignore tangents.\n\n"""
    else:
        base += """**Topic:** No specific topic given. Identify the single most compelling theme or question that emerges from the notes and build the essay around it. The essay should feel like the natural culmination of what the user has been thinking about.\n\n"""

    base += """Do NOT include YAML frontmatter. Start directly with the essay title as a single # heading, then the opening paragraph."""
    return base


def main():
    parser = argparse.ArgumentParser(
        description="Generate long-form essays from accumulated vault insights"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Focus the essay on this topic (e.g., 'inverse problems', 'AI agents')",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Look back N days for Sources/Inbox (default: 30)",
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
            script_name="essay.py",
            operation_type="essay",
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
        "SOURCE: [[{filename}]] ({source}, type: {type}, date: {date})\n\n{content}".format(
            **n
        )
        for n in notes
    )

    if len(notes_text) > 100000:
        notes_text = notes_text[:100000] + "\n\n[Additional notes truncated for length...]"

    prompt = build_essay_prompt(args.topic, notes_text)
    print("Generating essay with AI...")
    essay_body = summarize(notes_text, prompt)

    today = datetime.now().strftime("%Y-%m-%d")

    # Determine output filename
    if args.title:
        safe_title = re.sub(r'[^\w\s-]', '', args.title).strip().replace(" ", " ")
        if not safe_title:
            safe_title = today
    elif args.topic:
        safe_title = re.sub(r'[^\w\s-]', '', args.topic)[:50].strip().replace(" ", " ")
        if not safe_title:
            safe_title = today
    else:
        safe_title = today

    # Build source index
    source_index = "\n".join(
        "- [[{}]] ({})".format(n["filename"], n["source"]) for n in notes[:30]
    )
    if len(notes) > 30:
        source_index += f"\n- ... and {len(notes) - 30} more"

    note = f"""---
type: essay
date: {today}
topic: {args.topic or "open synthesis"}
note_count: {len(notes)}
tags:
  - essay
  - synthesis
---

{essay_body}

---

## Sources Referenced

{source_index}
"""

    out_path = f"Atlas/Essay - {safe_title}.md"
    save_note(out_path, note)
    print(f"Done! Essay saved to {out_path}.")

    if TRACKER:
        TRACKER.record_operation(
            script_name="essay.py",
            operation_type="essay",
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
                script_name="essay.py",
                operation_type="essay",
                status="failed",
                metrics={"error": str(e)},
            )
        import sys
        sys.exit(1)
