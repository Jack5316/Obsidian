"""Lightweight daily cross-domain synthesis from today's Source notes.

Runs after daily curation scripts to find cross-domain sparks,
contradictions, and the single most important signal of the day.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

from config import summarize, save_note, VAULT_PATH, TRACKER

SYNTHESIS_PROMPT = """You are a cross-domain pattern detector. Given today's curated notes from
multiple sources (ArXiv, Hacker News, Reddit, news, Twitter), find ONLY:

1. **Cross-Domain Sparks** (2-3 max, or zero if nothing genuinely crosses domains) -
   Ideas from one domain that illuminate another. E.g., a chip design constraint that
   mirrors an LLM architecture choice, or a philosophy concept that reframes an engineering
   tradeoff. Be honest — if nothing crosses domains today, say so. Do not force connections.

2. **Tension or Contradiction** (0-1) - Contradictory signals across sources. E.g., one source
   celebrates a technology while another flags its risks. Only include if genuinely contradictory.

3. **One-Line Verdict** - A single sentence capturing today's most important cross-domain signal.
   If there is none, say "No cross-domain signal today — and that's fine."

Use [[wikilinks]] to connect to existing notes and concepts.
Keep it SHORT. This is a daily scan, not a weekly essay.
Do NOT include any YAML frontmatter or title heading - start directly with Cross-Domain Sparks."""

# Note types to skip (avoid self-referential loops)
SKIP_TYPES = {"weekly-synthesis", "self-reflection", "daily-synthesis"}


def collect_today_notes() -> list:
    """Find all Source notes from today, excluding synthesis/reflection notes."""
    sources_dir = VAULT_PATH / "Sources"
    if not sources_dir.exists():
        return []

    today_str = datetime.now().strftime("%Y-%m-%d")
    notes = []

    for md_file in sources_dir.glob("*.md"):
        # Only include files with today's date in the name
        if today_str not in md_file.name:
            continue

        content = md_file.read_text(encoding="utf-8")

        # Extract type from frontmatter
        note_type = "unknown"
        type_match = re.search(r"^type:\s*(.+)$", content, re.MULTILINE)
        if type_match:
            note_type = type_match.group(1).strip()

        # Skip synthesis/reflection notes to avoid self-referential loops
        if note_type in SKIP_TYPES:
            continue

        # Extract the body (skip frontmatter)
        body = content
        fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if fm_match:
            body = content[fm_match.end():]

        notes.append({
            "filename": md_file.stem,
            "type": note_type,
            "content": body[:2000],  # 2000 char cap (lighter than weekly's 3000)
        })

    return notes


def main():
    parser = argparse.ArgumentParser(description="Generate daily cross-domain synthesis")
    parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="daily_synthesis.py",
            operation_type="daily_synthesis",
            status="in_progress",
        )

    print("Collecting today's source notes...")
    notes = collect_today_notes()

    if len(notes) < 2:
        print("Need at least 2 source notes for cross-domain synthesis (found {}).".format(len(notes)))
        return

    print("Found {} notes:".format(len(notes)))
    for n in notes:
        print("  {} ({})".format(n["filename"], n["type"]))

    # Format all notes for AI
    notes_text = "\n\n---\n\n".join(
        "SOURCE: [[{filename}]] (type: {type})\n\n{content}".format(**n)
        for n in notes
    )

    # Truncate if too long
    if len(notes_text) > 40000:
        notes_text = notes_text[:40000] + "\n\n[Additional notes truncated...]"

    print("Generating daily synthesis with AI...")
    synthesis_body = summarize(notes_text, SYNTHESIS_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")

    # Build source index
    source_index = "\n".join(
        "- [[{}]] ({})".format(n["filename"], n["type"]) for n in notes
    )

    note = """---
type: daily-synthesis
date: {today}
note_count: {count}
source_types: [{types}]
tags:
  - review/daily
  - synthesis
---

# Daily Synthesis - {today}

> [!info] Cross-domain scan of {count} source notes

{synthesis}

---

## Sources Scanned

{index}
""".format(
        today=today,
        count=len(notes),
        types=", ".join(sorted(set(n["type"] for n in notes))),
        synthesis=synthesis_body,
        index=source_index,
    )

    save_note("Sources/Daily Synthesis - {}.md".format(today), note)
    print("Done! {} notes scanned for cross-domain signals.".format(len(notes)))

    # Track operation completion
    if TRACKER:
        TRACKER.record_operation(
            script_name="daily_synthesis.py",
            operation_type="daily_synthesis",
            status="success",
            metrics={
                "notes_processed": len(notes),
                "note_types": list(set(n["type"] for n in notes)),
                "output_file": "Sources/Daily Synthesis - {}.md".format(today),
            },
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error: {}".format(e))
        if TRACKER:
            TRACKER.record_operation(
                script_name="daily_synthesis.py",
                operation_type="daily_synthesis",
                status="failed",
                metrics={"error": str(e)},
            )
        import sys
        sys.exit(1)
