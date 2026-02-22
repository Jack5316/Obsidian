"""Open Question — capture questions for future research into Obsidian."""

import argparse
from datetime import datetime
from pathlib import Path

from config import save_note, VAULT_PATH


def capture(question: str, as_note: bool = False) -> Path:
    """Capture a question. Appends to daily file by default; use as_note=True for standalone note."""
    today = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M")

    if as_note:
        # Standalone note: Sources/Question - {slug}.md
        slug = question[:50].replace(" ", "-").replace("/", "-").replace("?", "")
        slug = "".join(c for c in slug if c.isalnum() or c == "-").strip("-") or "question"
        path = f"Sources/Question - {slug}.md"
        content = f"# {question}\n\n*Captured {today} {time_str}*\n\n## Context\n\n## Research directions\n\n"
        return save_note(path, content)

    # Append to daily file
    path = f"Sources/Question - {today}.md"
    full_path = VAULT_PATH / path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    entry = f"- **{time_str}** — {question}\n"
    if full_path.exists():
        content = full_path.read_text(encoding="utf-8") + entry
    else:
        content = f"# Open Questions — {today}\n\n{entry}"

    full_path.write_text(content, encoding="utf-8")
    print(f"Saved: {full_path}")
    return full_path


def main():
    parser = argparse.ArgumentParser(
        description="Open Question — capture questions for future research",
        epilog='Examples:\n  question "How does regularization affect inverse problems?"\n  question "What is the optimal batch size for RL?" --note',
    )
    parser.add_argument("question", nargs="+", help="The question to capture (words as arguments)")
    parser.add_argument("-n", "--note", action="store_true", help="Create standalone note instead of appending to daily")
    args = parser.parse_args()

    question = " ".join(args.question).strip()
    if not question:
        parser.error("Provide a question")
        return

    capture(question, as_note=args.note)


if __name__ == "__main__":
    main()
