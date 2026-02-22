"""Structure meeting notes/conversations into Obsidian meeting note format."""

import argparse
import re
from datetime import datetime
from pathlib import Path

from config import summarize, save_note, VAULT_PATH

MEETING_PROMPT = """You are a meeting note synthesizer. Given raw meeting notes or a conversation transcript, extract and structure the content into this exact format:

## Attendees
- List each participant identified (use "-" if none identifiable)

## Agenda
- Topics or items discussed (infer from content if not explicit)

## Notes
- Key discussion points, summarized concisely
- Preserve important context and nuance
- Use bullet points

## Decisions Made
- Explicit decisions, outcomes, or agreements
- Use "-" if none

## Action Items
- [ ] Task description — assignee (if identifiable)
- Each action item as a checkbox. Include owner when you can infer from context.
- Use "- [ ]" format for Obsidian compatibility

## Follow Up
- [ ] Process into relevant project/area notes
- [ ] Any other suggested next steps

Use [[wikilinks]] to link to projects, people, or concepts when relevant.
Do NOT include YAML frontmatter or a top-level # title — start directly with ## Attendees.
Be thorough but concise. Extract every actionable item and decision from the transcript."""


def resolve_path(path_str: str) -> Path:
    """Resolve path relative to vault or as absolute."""
    p = Path(path_str)
    if not p.is_absolute():
        p = VAULT_PATH / path_str
    return p.resolve()


def main():
    parser = argparse.ArgumentParser(
        description="Structure meeting notes into Obsidian format"
    )
    parser.add_argument(
        "path",
        help="Path to meeting notes file (relative to vault or absolute)",
    )
    parser.add_argument(
        "--title",
        help="Meeting name for output note",
    )
    parser.add_argument(
        "--output",
        help="Custom output path (relative to vault)",
    )
    args = parser.parse_args()

    input_path = resolve_path(args.path)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return 1

    content = input_path.read_text(encoding="utf-8")
    if not content.strip():
        print("Error: File is empty")
        return 1

    title = args.title
    if not title:
        title = input_path.stem.replace("-", " ").replace("_", " ").title()

    print(f"Processing: {input_path.name}")
    print("Structuring with AI...")

    body = summarize(content, MEETING_PROMPT)

    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[:80].strip()

    if args.output:
        out_path = args.output
    else:
        out_path = f"Sources/Meeting - {safe_title} - {date_str}.md"

    note = f"# {safe_title} - {date_str}\n\n{body}"
    save_note(out_path, note)
    print("Done!")
    return 0


if __name__ == "__main__":
    exit(main())
