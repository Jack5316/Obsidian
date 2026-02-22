"""Steelman opposing views on topics you're exploring.

Takes a topic or position and generates the strongest possible versions of
opposing arguments (steelmanning — the opposite of strawmanning). Optionally
uses vault notes as context for your current view.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

from config import summarize, save_note, VAULT_PATH, TRACKER

STEELMAN_PROMPT = """You are an expert at steelmanning — presenting the strongest possible version of an opposing argument. Steelmanning is the opposite of strawmanning: you argue *for* the other side as persuasively as a skilled advocate would, without caricature or weak interpretations.

Your task: Given a topic or position the user is exploring, identify the 2–4 most substantive opposing views and present each in its strongest form.

**Requirements:**
1. **Charitable interpretation** — Assume the smartest, most informed version of each opposing view. Give them the benefit of the doubt.
2. **Substantive** — Each steelman should be 2–4 paragraphs. Include the best evidence, reasoning, and nuance a real advocate would use.
3. **Distinct** — Each opposing view should be meaningfully different (not overlapping arguments).
4. **Honest** — If the steelman reveals a genuine weakness in the user's position, say so. The goal is intellectual honesty, not comfort.
5. **Wikilinks** — Use [[note title]] to reference any source notes when relevant.

**Output format:**
- Start with a one-paragraph summary of the user's position (as you understand it).
- For each opposing view: a ## heading with the view name, then the steelmanned argument.
- End with a brief "Key tensions" section: 1–3 sentences on what the user should sit with.

Do NOT include YAML frontmatter. Start directly with a # heading for the topic."""


def load_note_content(path: str) -> str:
    """Load content from a vault-relative path."""
    full_path = VAULT_PATH / path
    if not full_path.exists():
        raise FileNotFoundError(f"Note not found: {path}")
    content = full_path.read_text(encoding="utf-8")
    # Strip frontmatter for context
    fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    if fm_match:
        content = content[fm_match.end():]
    return content.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Steelman opposing views on topics you're exploring"
    )
    parser.add_argument(
        "topic",
        type=str,
        help="The topic or position you're exploring (e.g., 'inverse problems in life decisions', 'AI will replace most knowledge work')",
    )
    parser.add_argument(
        "--from-path",
        type=str,
        default=None,
        help="Path to a note containing your current view (e.g., Atlas/Essay - inverse problems.md)",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Custom output filename (default: derived from topic)",
    )
    args = parser.parse_args()

    if TRACKER:
        TRACKER.record_operation(
            script_name="debate_steelman.py",
            operation_type="debate",
            status="in_progress",
            metrics={"topic": args.topic},
        )

    # Build input for AI
    if args.from_path:
        try:
            context = load_note_content(args.from_path)
            user_input = f"""TOPIC: {args.topic}

CONTEXT — The user's current view (from [[{Path(args.from_path).stem}]]):

{context}

---
Generate steelmanned opposing views to this position."""
        except FileNotFoundError as e:
            print(f"Error: {e}")
            if TRACKER:
                TRACKER.record_operation(
                    script_name="debate_steelman.py",
                    operation_type="debate",
                    status="failed",
                    metrics={"error": str(e)},
                )
            return 1
    else:
        user_input = f"""TOPIC: {args.topic}

The user is exploring this topic/position. Generate steelmanned opposing views. You may infer the implied position from the topic alone."""

    print("Generating steelmanned opposing views...")
    result = summarize(user_input, STEELMAN_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")

    # Output filename
    if args.title:
        safe_title = re.sub(r"[^\w\s-]", "", args.title).strip().replace(" ", " ")
    else:
        safe_title = re.sub(r"[^\w\s-]", "", args.topic)[:50].strip().replace(" ", " ")
    if not safe_title:
        safe_title = today

    source_note = f"- [[{Path(args.from_path).stem}]]" if args.from_path else "(topic only, no vault context)"

    note = f"""---
type: debate
date: {today}
topic: {args.topic}
tags:
  - debate
  - steelman
---

{result}

---
## Sources

{source_note}
"""

    out_path = f"Atlas/Debate - {safe_title}.md"
    save_note(out_path, note)
    print(f"Done! Steelmanned views saved to {out_path}.")

    if TRACKER:
        TRACKER.record_operation(
            script_name="debate_steelman.py",
            operation_type="debate",
            status="success",
            metrics={"topic": args.topic, "output_file": out_path},
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="debate_steelman.py",
                operation_type="debate",
                status="failed",
                metrics={"error": str(e)},
            )
        import sys

        sys.exit(1)
