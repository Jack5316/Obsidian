"""Today I Learned — quick capture of learnings into Obsidian."""

import argparse
from datetime import datetime
from pathlib import Path

from config import save_note, VAULT_PATH


def capture(learning: str, as_note: bool = False) -> Path:
    """Capture a TIL. Appends to daily file by default; use as_note=True for standalone note."""
    today = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M")

    if as_note:
        # Standalone note: Sources/TIL - {slug}.md
        slug = learning[:50].replace(" ", "-").replace("/", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-").strip("-") or "learning"
        path = f"Sources/TIL - {slug}.md"
        content = f"# {learning}\n\n*Captured {today} {time_str}*\n"
        return save_note(path, content)

    # Append to daily file
    path = f"Sources/TIL - {today}.md"
    full_path = VAULT_PATH / path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    entry = f"- **{time_str}** — {learning}\n"
    if full_path.exists():
        content = full_path.read_text(encoding="utf-8") + entry
    else:
        content = f"# TIL — {today}\n\n{entry}"

    full_path.write_text(content, encoding="utf-8")
    print(f"Saved: {full_path}")
    return full_path


def main():
    parser = argparse.ArgumentParser(
        description="Today I Learned — quick capture",
        epilog='Examples:\n  til "Python walrus operator := assigns and returns"\n  til "Git rebase -i rewrites history" --note',
    )
    parser.add_argument("learning", nargs="+", help="What you learned (words as arguments)")
    parser.add_argument("-n", "--note", action="store_true", help="Create standalone note instead of appending to daily")
    args = parser.parse_args()

    learning = " ".join(args.learning).strip()
    if not learning:
        parser.error("Provide what you learned")
        return

    capture(learning, as_note=args.note)


if __name__ == "__main__":
    main()
