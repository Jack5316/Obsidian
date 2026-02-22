"""Inverse thinking — compute reversely for problems, decisions, actions, and confusions.

Inspired by linear algebra's inverse matrix (A⁻¹ undoes A) and Charlie Munger's
"invert, always invert." Many situations become clearer when viewed from the
opposite direction.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

from config import summarize, save_note, VAULT_PATH, TRACKER

INVERSE_PROMPT = """You are an expert at inverse thinking — applying the concept of the inverse from linear algebra to life situations. In linear algebra, A⁻¹ applied to A·x returns x: the inverse "undoes" a transformation. Similarly, inverting a problem, decision, action, or confusion reveals what would reverse or undo it.

**Charlie Munger's principle:** "Invert, always invert." Many problems are easier to solve when you flip them.

Your task: Given the user's input and the type (problem, decision, action, or confusion), compute the inverse — what would reverse, undo, or oppose it.

**For each type, apply this lens:**

1. **Problem** — What would the inverse of this problem look like? What would NOT having this problem mean? What conditions would "undo" it? What would the opposite problem be? What would you need to do to make the problem disappear?

2. **Decision** — What would the inverse of this decision be? What would NOT deciding (or choosing the opposite) mean? What would reversing the decision look like? What would you need to believe to choose the opposite? What does the inverse reveal about the stakes?

3. **Action** — What would the inverse of this action be? What would undo it? What would it mean to reverse this action? What would the opposite action look like? What does the inverse reveal about what the action is actually doing?

4. **Confusion** — What would the inverse of this confusion be? What would clarity look like? What would it take to "undo" the confusion? What is the inverse question that, if answered, would dissolve the confusion? What would NOT being confused about this mean?

**Requirements:**
1. **Concrete** — Give specific, actionable inverse formulations, not vague abstractions
2. **Illuminating** — The inverse should reveal something the forward view obscures
3. **Honest** — If the inverse exposes a flaw or blind spot, say so
4. **Wikilinks** — Use [[note title]] to reference relevant vault notes when appropriate

**Output format:**
- Start with a one-paragraph summary of the user's input (as you understand it)
- ## The Inverse — present the inverted formulation clearly
- ## What This Reveals — 2–4 insights the inverse perspective illuminates
- ## Inverse Actions — concrete steps or questions that follow from the inverse view
- Do NOT include YAML frontmatter in the main content

Your analysis should be thoughtful, practical, and designed to shift perspective."""


def load_note_content(path: str) -> str:
    """Load content from a vault-relative path."""
    full_path = VAULT_PATH / path
    if not full_path.exists():
        raise FileNotFoundError(f"Note not found: {path}")
    content = full_path.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    if fm_match:
        content = content[fm_match.end():]
    return content.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Inverse thinking — compute reversely for problems, decisions, actions, and confusions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/inverse.py problem "I can't find time to exercise"
  python3 _scripts/inverse.py decision "Should I quit my job?"
  python3 _scripts/inverse.py action "I'm going to start a side project"
  python3 _scripts/inverse.py confusion "I don't know what career path to take"
  python3 _scripts/inverse.py problem "Procrastination" --from-path "Atlas/Note.md" --save
""",
    )
    parser.add_argument(
        "type",
        type=str,
        choices=["problem", "decision", "action", "confusion"],
        help="Type of input: problem, decision, action, or confusion",
    )
    parser.add_argument(
        "input_text",
        type=str,
        help="The problem, decision, action, or confusion to invert",
    )
    parser.add_argument(
        "--from-path",
        type=str,
        default=None,
        help="Path to a note containing additional context",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Custom output filename (default: derived from input)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to vault (default: prints to terminal only)",
    )
    args = parser.parse_args()

    if TRACKER:
        TRACKER.record_operation(
            script_name="inverse.py",
            operation_type="inverse",
            status="in_progress",
            metrics={"type": args.type, "input": args.input_text[:50]},
        )

    user_input = f"""TYPE: {args.type}
INPUT: {args.input_text}
"""

    if args.from_path:
        try:
            context = load_note_content(args.from_path)
            user_input += f"""
CONTEXT — Additional background from [[{Path(args.from_path).stem}]]:

{context}

---
Apply inverse thinking to the input above, taking the context into account."""
        except FileNotFoundError as e:
            print(f"Error: {e}")
            if TRACKER:
                TRACKER.record_operation(
                    script_name="inverse.py",
                    operation_type="inverse",
                    status="failed",
                    metrics={"error": str(e)},
                )
            return 1
    else:
        user_input += "\nApply inverse thinking to the input above."

    print(f"Computing inverse for {args.type}...")
    result = summarize(user_input, INVERSE_PROMPT)

    if args.save:
        today = datetime.now().strftime("%Y-%m-%d")
        if args.title:
            safe_title = re.sub(r"[^\w\s-]", "", args.title).strip().replace(" ", " ")
        else:
            safe_title = re.sub(r"[^\w\s-]", "", args.input_text)[:50].strip().replace(" ", " ")
        if not safe_title:
            safe_title = today

        source_note = f"- [[{Path(args.from_path).stem}]]" if args.from_path else "(input only, no vault context)"

        note = f"""---
type: inverse
date: {today}
inverse_type: {args.type}
input: {args.input_text}
tags:
  - inverse-thinking
  - invert
  - mental-model
---

{result}

---
## Sources

{source_note}
"""

        out_path = f"Atlas/Inverse - {safe_title}.md"
        save_note(out_path, note)
        print(f"Done! Inverse analysis saved to {out_path}.")
    else:
        print("\n" + "=" * 80 + "\n")
        print(result)
        print("\n" + "=" * 80 + "\n")
        print("Note: Use --save to save this to your vault.")

    if TRACKER:
        TRACKER.record_operation(
            script_name="inverse.py",
            operation_type="inverse",
            status="success",
            metrics={"type": args.type, "saved": args.save},
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="inverse.py",
                operation_type="inverse",
                status="failed",
                metrics={"error": str(e)},
            )
        import sys
        sys.exit(1)
