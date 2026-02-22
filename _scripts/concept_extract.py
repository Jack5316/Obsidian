"""Extract and define recurring concepts across vault reading.

Scans Sources, Atlas, Maps, and Inbox to identify concepts that appear
in multiple notes, then produces concise definitions with source links.
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from config import summarize, save_note, VAULT_PATH, TRACKER

PRIORITY_TYPES = {"weekly-synthesis", "daily-synthesis", "self-reflection", "self-evolution"}


def collect_notes(
    days: int = 30,
    include_atlas: bool = True,
    include_maps: bool = True,
    include_inbox: bool = True,
    topic_keywords: Optional[List[str]] = None,
) -> List[dict]:
    """Collect notes from Sources, Atlas, Maps, and Inbox."""
    notes = []

    # Sources
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

    # Atlas
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

    # Maps
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

    # Inbox
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


def build_concept_prompt(topic: Optional[str], notes_text: str) -> str:
    """Build the system prompt for concept extraction."""
    base = """You are analyzing a personal knowledge base to extract and define recurring concepts. Your task is to identify ideas, terms, or frameworks that appear across multiple notes — concepts the user is repeatedly encountering.

**Output format:**

For each recurring concept, provide:

1. **Concept name** (as ## heading)
2. **Definition** — 2–4 sentences that capture the essence. Write in the user's voice where possible; draw from how they use the concept across notes.
3. **Appears in** — List of [[note title]] links to source notes (use the exact filename without .md)

**Selection criteria:**
- A concept must appear in at least 2 different notes to be "recurring"
- Prioritize: domain-specific terms, frameworks, mental models, metaphors that cross domains
- Skip trivial or overly broad terms (e.g., "AI", "learning" unless used in a specific, recurring sense)
- Merge related concepts (e.g., "inverse problem" and "inverse problems" → one concept)
- Limit to 5–12 concepts; quality over quantity

**Output structure:**
- No YAML frontmatter
- Start with # Concept Digest
- Each concept as ## Concept Name, then definition paragraph, then "Appears in: [[note1]], [[note2]]"
- Use [[wikilinks]] for all note references

"""
    if topic:
        base += f"""**Topic focus:** The user requested concepts related to: "{topic}". Only include concepts that fit this theme.\n\n"""
    else:
        base += """**Topic:** No filter. Identify the most salient recurring concepts across all notes.\n\n"""

    base += """Do NOT include YAML frontmatter. Start directly with # Concept Digest."""
    return base


def main():
    parser = argparse.ArgumentParser(
        description="Extract and define recurring concepts across vault reading"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Focus on concepts related to this topic (e.g., 'inverse problems', 'AI')",
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
        "--output",
        type=str,
        default=None,
        help="Custom output path (default: Sources/Concept Digest - YYYY-MM-DD.md)",
    )
    args = parser.parse_args()

    topic_keywords = None
    if args.topic:
        topic_keywords = [w.strip() for w in args.topic.split(",")]

    if TRACKER:
        TRACKER.record_operation(
            script_name="concept_extract.py",
            operation_type="concept",
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

    prompt = build_concept_prompt(args.topic, notes_text)
    print("Extracting concepts with AI...")
    digest_body = summarize(notes_text, prompt)

    today = datetime.now().strftime("%Y-%m-%d")

    if args.output:
        out_path = args.output
    else:
        out_path = f"Sources/Concept Digest - {today}.md"

    source_index = "\n".join(
        "- [[{}]] ({})".format(n["filename"], n["source"]) for n in notes[:30]
    )
    if len(notes) > 30:
        source_index += f"\n- ... and {len(notes) - 30} more"

    note = f"""---
type: concept-digest
date: {today}
topic: {args.topic or "all"}
note_count: {len(notes)}
tags:
  - concept
  - extraction
---

{digest_body}

---

## Notes Scanned

{source_index}
"""

    save_note(out_path, note)
    print(f"Done! Concept digest saved to {out_path}.")

    if TRACKER:
        TRACKER.record_operation(
            script_name="concept_extract.py",
            operation_type="concept",
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
                script_name="concept_extract.py",
                operation_type="concept",
                status="failed",
                metrics={"error": str(e)},
            )
        import sys
        sys.exit(1)
