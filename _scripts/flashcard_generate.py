"""Generate spaced repetition flashcards from vault content or a single note.

Extracts key facts, concepts, and definitions suitable for memory retention.
Outputs Obsidian Spaced Repetition plugin format (question::answer).
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from config import summarize, save_note, VAULT_PATH, TRACKER

FLASHCARD_PROMPT = """You are generating spaced repetition flashcards from content. Extract key facts, concepts, definitions, and relationships that are worth memorizing.

**Output format (Obsidian Spaced Repetition plugin):**
- Each card: `question::answer` on a single line
- Use `::` exactly as the separator (no spaces around it)
- Keep questions concise (one concept per card)
- Answers should be brief but complete enough to verify recall
- Avoid trivial or obvious facts; prioritize testable knowledge
- Include [[wikilinks]] in answers when referencing specific notes

**Card quality guidelines:**
- One atomic fact per card — not compound questions
- Questions should be answerable without looking at the source
- Prefer "What is X?" / "Why does Y?" / "How does Z work?" style
- Limit to 5–15 cards; quality over quantity

**Output structure:**
- No YAML frontmatter
- Start with `#flashcards` or `#flashcards/deck-name` (use deck name from context if provided)
- One card per line, no numbering
- Example:
  What is an inverse problem?::A problem where you infer causes from observed effects, common in imaging and life decisions. See [[Inverse Problems]].
  Why does regularization help inverse problems?::It constrains the solution space when multiple answers fit the data.
"""


def collect_notes(
    days: int = 30,
    include_atlas: bool = True,
    include_maps: bool = True,
    include_inbox: bool = True,
    topic_keywords: Optional[List[str]] = None,
) -> List[dict]:
    """Collect notes from Sources, Atlas, Maps, and Inbox."""
    notes = []

    def add_note(md_file: Path, body: str, source: str, note_type: str, date: str, content_limit: int = 3000):
        if topic_keywords:
            combined = (md_file.stem + " " + body).lower()
            if not any(kw.lower() in combined for kw in topic_keywords):
                return
        notes.append({
            "filename": md_file.stem,
            "type": note_type,
            "source": source,
            "date": date,
            "content": body[:content_limit],
        })

    def strip_frontmatter(content: str) -> str:
        fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        return content[fm_match.end():] if fm_match else content

    # Sources
    sources_dir = VAULT_PATH / "Sources"
    if sources_dir.exists():
        cutoff = datetime.now() - timedelta(days=days)
        for md_file in sources_dir.glob("*.md"):
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
            if mtime < cutoff:
                continue
            content = md_file.read_text(encoding="utf-8")
            add_note(md_file, strip_frontmatter(content), "Sources", "source", mtime.strftime("%Y-%m-%d"), 4000)

    # Atlas
    if include_atlas:
        atlas_dir = VAULT_PATH / "Atlas"
        if atlas_dir.exists():
            for md_file in atlas_dir.glob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                add_note(md_file, strip_frontmatter(content), "Atlas", "atlas", "")

    # Maps
    if include_maps:
        maps_dir = VAULT_PATH / "Maps"
        if maps_dir.exists():
            for md_file in maps_dir.glob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                add_note(md_file, strip_frontmatter(content), "Maps", "moc", "", 2000)

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
                add_note(md_file, strip_frontmatter(content), "Inbox", "inbox", mtime.strftime("%Y-%m-%d"))

    return notes


def read_file_content(path: Path) -> str:
    """Read and strip frontmatter from a single file."""
    content = path.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    return content[fm_match.end():] if fm_match else content


def main():
    parser = argparse.ArgumentParser(
        description="Generate spaced repetition flashcards from vault content or a single note"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Path to a single note (e.g., Atlas/Essay - topic.md). If omitted, uses --topic/--days to collect from vault.",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Focus on notes related to this topic (used when no path given)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Look back N days for Sources/Inbox when collecting from vault (default: 30)",
    )
    parser.add_argument(
        "--deck",
        type=str,
        default=None,
        help="Deck name for Obsidian (e.g., 'concepts' -> #flashcards/concepts)",
    )
    parser.add_argument(
        "--no-atlas",
        action="store_true",
        help="Exclude Atlas when collecting from vault",
    )
    parser.add_argument(
        "--no-maps",
        action="store_true",
        help="Exclude Maps when collecting from vault",
    )
    parser.add_argument(
        "--no-inbox",
        action="store_true",
        help="Exclude Inbox when collecting from vault",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom output path",
    )
    parser.add_argument(
        "--anki",
        action="store_true",
        help="Also output Anki-compatible .txt (tab-separated front\\tback)",
    )
    args = parser.parse_args()

    if TRACKER:
        TRACKER.record_operation(
            script_name="flashcard_generate.py",
            operation_type="flashcard",
            status="in_progress",
            metrics={"path": args.path, "topic": args.topic},
        )

    if args.path:
        # Single file mode
        note_path = Path(args.path)
        if not note_path.is_absolute():
            note_path = VAULT_PATH / note_path
        if not note_path.exists():
            print(f"Error: File not found: {note_path}")
            return
        content = read_file_content(note_path)
        notes_text = f"SOURCE: [[{note_path.stem}]]\n\n{content}"
        deck_hint = args.deck or note_path.stem.replace(" - ", "-").replace(" ", "-")[:30]
    else:
        # Vault collection mode
        topic_keywords = [w.strip() for w in args.topic.split(",")] if args.topic else None
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
        notes_text = "\n\n---\n\n".join(
            f"SOURCE: [[{n['filename']}]] ({n['source']})\n\n{n['content']}" for n in notes
        )
        if len(notes_text) > 80000:
            notes_text = notes_text[:80000] + "\n\n[Truncated...]"
        deck_hint = args.deck or (
            args.topic.replace(",", "-").replace(" ", "-")[:30] if args.topic else "vault"
        )

    prompt = FLASHCARD_PROMPT + f"\n\n**Deck suggestion:** Use #flashcards/{deck_hint} or #flashcards as the deck tag.\n\n"
    print("Generating flashcards with AI...")
    cards_body = summarize(notes_text, prompt)

    # Ensure deck tag is present
    if "#flashcards" not in cards_body and "#flashcards/" not in cards_body:
        deck_tag = f"#flashcards/{deck_hint}" if deck_hint else "#flashcards"
        cards_body = deck_tag + "\n\n" + cards_body.lstrip()

    today = datetime.now().strftime("%Y-%m-%d")

    if args.output:
        out_path = args.output
    elif args.path:
        base = Path(args.path).stem
        out_path = f"Sources/Flashcards - {base}.md"
    else:
        out_path = f"Sources/Flashcards - {today}.md"

    note = f"""---
type: flashcard-deck
date: {today}
deck: {deck_hint}
tags:
  - flashcard
  - spaced-repetition
---

{cards_body}
"""
    save_note(out_path, note)
    print(f"Saved: {out_path}")

    if args.anki:
        # Parse question::answer lines and output tab-separated
        anki_path = out_path.replace(".md", "_anki.txt")
        lines = []
        for line in cards_body.split("\n"):
            line = line.strip()
            if "::" in line and not line.startswith("#"):
                parts = line.split("::", 1)
                if len(parts) == 2:
                    front = parts[0].strip()
                    back = parts[1].strip()
                    lines.append(f"{front}\t{back}")
        if lines:
            anki_content = "\n".join(lines)
            save_note(anki_path, anki_content)
            print(f"Anki export: {anki_path}")

    if TRACKER:
        TRACKER.record_operation(
            script_name="flashcard_generate.py",
            operation_type="flashcard",
            status="success",
            metrics={"output": out_path},
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="flashcard_generate.py",
                operation_type="flashcard",
                status="failed",
                metrics={"error": str(e)},
            )
        raise
