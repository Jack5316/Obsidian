"""Generate a weekly synthesis note by reading all recent Source notes.

Cross-references Twitter, YouTube, HN, ArXiv, Reddit, Book, and PDF notes
to find themes, connections, and insights across all sources.
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

from config import summarize, save_note, VAULT_PATH, TRACKER

SYNTHESIS_PROMPT = """You are an intellectual synthesizer. Given notes from multiple sources
(Twitter, YouTube, Hacker News, ArXiv, Reddit, books, PDFs) collected over the past week,
create a Weekly Synthesis that:

1. **Top Themes This Week** - 3-5 major themes that appeared across multiple sources
2. **Cross-Source Connections** - Interesting links between different sources
   (e.g., a Reddit discussion relates to an ArXiv paper, or a YouTube video expands on a tweet)
3. **Key Insights** - The most valuable ideas encountered this week
4. **Emerging Patterns** - Trends or patterns you notice developing
5. **Surprising Connections** - Ideas that seem unrelated but share deeper structure. Prioritize
   cross-domain connections (e.g., a chip design concept that illuminates an LLM architecture choice,
   or a philosophy paper that reframes an engineering tradeoff). These are the system's highest-value output.
6. **Goodhart Check** - A meta-audit of the system itself:
   - Are current sources still serving genuine curiosity, or just habit?
   - Are any metrics being gamed (e.g., always flagging "cross-domain" to satisfy the prompt)?
   - What should we STOP tracking or reading?
   - Is this synthesis itself becoming formulaic? If so, how should it change?
7. **Questions to Explore** - Open questions worth investigating further
8. **Recommended Deep Dives** - Which sources deserve a second, closer look
9. **Productive Illegibility** - What resisted easy categorization this week? What was confusing
   or contradictory in a way that might be generative? Not everything needs to resolve into a theme.

Use [[wikilinks]] liberally to connect to existing notes and concepts.
Reference specific sources by their note titles using [[note title]] format.
Do NOT include any YAML frontmatter or title heading - start directly with Top Themes."""


def collect_recent_notes(days: int = 7) -> list:
    """Find all Source notes from the past N days."""
    sources_dir = VAULT_PATH / "Sources"
    if not sources_dir.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days)
    notes = []

    for md_file in sources_dir.glob("*.md"):
        # Check file modification time
        mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
        if mtime < cutoff:
            continue

        content = md_file.read_text(encoding="utf-8")

        # Extract type from frontmatter
        note_type = "unknown"
        type_match = re.search(r"^type:\s*(.+)$", content, re.MULTILINE)
        if type_match:
            note_type = type_match.group(1).strip()

        # Extract the body (skip frontmatter)
        body = content
        fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if fm_match:
            body = content[fm_match.end():]

        notes.append({
            "filename": md_file.stem,
            "type": note_type,
            "date": mtime.strftime("%Y-%m-%d"),
            "content": body[:3000],  # Cap per note to manage token usage
        })

    # Sort by date
    notes.sort(key=lambda n: n["date"], reverse=True)
    return notes


def main():
    parser = argparse.ArgumentParser(description="Generate weekly synthesis from all source notes")
    parser.add_argument("--days", type=int, default=7, help="Look back N days (default: 7)")
    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="weekly_synthesis.py",
            operation_type="generate_synthesis",
            status="in_progress",
            metrics={"days": args.days}
        )

    print("Collecting notes from the last {} days...".format(args.days))
    notes = collect_recent_notes(args.days)

    if not notes:
        print("No recent notes found in Sources/.")
        return

    # Group by type
    by_type = {}
    for note in notes:
        t = note["type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(note)

    print("Found {} notes:".format(len(notes)))
    for note_type, type_notes in by_type.items():
        print("  {}: {}".format(note_type, len(type_notes)))

    # Format all notes for AI
    notes_text = "\n\n---\n\n".join(
        "SOURCE: [[{filename}]] (type: {type}, date: {date})\n\n{content}".format(**n)
        for n in notes
    )

    # Truncate if too long
    if len(notes_text) > 80000:
        notes_text = notes_text[:80000] + "\n\n[Additional notes truncated...]"

    print("Generating weekly synthesis with AI...")
    synthesis_body = summarize(notes_text, SYNTHESIS_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")
    week_start = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    # Build source index
    source_index = "\n".join(
        "- [[{}]] ({})".format(n["filename"], n["type"]) for n in notes
    )

    note = """---
type: weekly-synthesis
date: {today}
period: {start} to {today}
note_count: {count}
source_types: [{types}]
tags:
  - review/weekly
  - synthesis
---

# Weekly Synthesis - {today}

> [!info] {count} notes synthesized from {start} to {today}

{synthesis}

---

## Sources Referenced

{index}
""".format(
        today=today,
        start=week_start,
        count=len(notes),
        types=", ".join(by_type.keys()),
        synthesis=synthesis_body,
        index=source_index,
    )

    save_note("Sources/Weekly Synthesis - {}.md".format(today), note)
    print("Done! {} notes synthesized.".format(len(notes)))

    # Track operation completion
    if TRACKER:
        TRACKER.record_operation(
            script_name="weekly_synthesis.py",
            operation_type="generate_synthesis",
            status="success",
            metrics={
                "days": args.days,
                "notes_processed": len(notes),
                "note_types": list(by_type.keys()),
                "output_file": "Sources/Weekly Synthesis - {}.md".format(today)
            }
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="weekly_synthesis.py",
                operation_type="generate_synthesis",
                status="failed",
                metrics={"error": str(e)}
            )
        import sys
        sys.exit(1)
