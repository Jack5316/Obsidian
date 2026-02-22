"""Socratic questioning method to explore and deepen understanding of a question or topic.

Uses the SOCRATES questioning framework to systematically explore a topic through
thought-provoking questions, helping to uncover assumptions, clarify concepts,
and reveal implications.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

from config import summarize, save_note, VAULT_PATH, TRACKER

SOCRATES_PROMPT = """You are an expert at Socratic questioning — a method of guided inquiry that helps deepen understanding through thoughtful, probing questions. Your role is not to provide answers, but to ask questions that illuminate the topic.

**SOCRATES Framework:**
S - Clarification Questions (What do you mean by...?)
O - Origin Questions (Where did this idea come from?)
C - Consequence Questions (What follows from this?)
R - Role Reversal Questions (What if the opposite were true?)
A - Assumption Questions (What are we taking for granted?)
T - Truth/Evidence Questions (How do we know this is true?)
E - Example/Counterexample Questions (Can you think of an example?)
S - Synthesis Questions (How does this relate to...?)

Your task: Given a question or topic the user wants to explore, apply the SOCRATES framework to generate a comprehensive set of questions that deepen understanding.

**Requirements:**
1. **Framework Application** - For each letter in SOCRATES, generate 2-3 thoughtful questions
2. **Depth, Not Trivia** - Questions should challenge assumptions and reveal deeper insights
3. **Progressive Inquiry** - Questions should build on each other, moving from basic to more complex
4. **Wikilinks** - Use [[note title]] to reference any relevant vault notes when appropriate
5. **Context Awareness** - If vault context is provided, tailor questions to that specific content

**Output format:**
- Start with a brief introduction explaining the purpose of Socratic questioning for this topic
- For each SOCRATES category: a ## heading with the category name and letter, then 2-3 questions
- End with a "Synthesis & Next Steps" section that suggests how to pursue these questions
- Do NOT include YAML frontmatter in the main content

Your questions should be open-ended, thought-provoking, and designed to stimulate deeper reflection."""


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
        description="Apply Socratic questioning method to explore a question or topic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/socrates.py "What is consciousness?"
  python3 _scripts/socrates.py "AI safety" --from-path "Atlas/Essay - AI Ethics.md"
  python3 _scripts/socrates.py "Meaning of life" --save
"""
    )
    parser.add_argument(
        "question",
        type=str,
        help="The question or topic to explore using Socratic method",
    )
    parser.add_argument(
        "--from-path",
        type=str,
        default=None,
        help="Path to a note containing context (e.g., Atlas/Essay - topic.md)",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Custom output filename (default: derived from question)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to vault (default: prints to terminal only)",
    )
    args = parser.parse_args()

    if TRACKER:
        TRACKER.record_operation(
            script_name="socrates.py",
            operation_type="socratic_inquiry",
            status="in_progress",
            metrics={"question": args.question},
        )

    # Build input for AI
    if args.from_path:
        try:
            context = load_note_content(args.from_path)
            user_input = f"""QUESTION/TOPIC: {args.question}

CONTEXT — The user has provided this note as background context (from [[{Path(args.from_path).stem}]]):

{context}

---
Apply the SOCRATES questioning framework to explore this question/topic, taking into account the provided context."""
        except FileNotFoundError as e:
            print(f"Error: {e}")
            if TRACKER:
                TRACKER.record_operation(
                    script_name="socrates.py",
                    operation_type="socratic_inquiry",
                    status="failed",
                    metrics={"error": str(e)},
                )
            return 1
    else:
        user_input = f"""QUESTION/TOPIC: {args.question}

The user wants to explore this question/topic using the Socratic method. Apply the SOCRATES framework to generate deep, thought-provoking questions."""

    print("Generating Socratic questions...")
    result = summarize(user_input, SOCRATES_PROMPT)

    if args.save:
        today = datetime.now().strftime("%Y-%m-%d")

        # Output filename
        if args.title:
            safe_title = re.sub(r"[^\w\s-]", "", args.title).strip().replace(" ", " ")
        else:
            safe_title = re.sub(r"[^\w\s-]", "", args.question)[:50].strip().replace(" ", " ")
        if not safe_title:
            safe_title = today

        source_note = f"- [[{Path(args.from_path).stem}]]" if args.from_path else "(topic only, no vault context)"

        note = f"""---
type: socratic-inquiry
date: {today}
topic: {args.question}
tags:
  - socratic-method
  - inquiry
  - questioning
---

{result}

---
## Sources

{source_note}
"""

        out_path = f"Atlas/Socratic Inquiry - {safe_title}.md"
        save_note(out_path, note)
        print(f"Done! Socratic inquiry saved to {out_path}.")
    else:
        print("\n" + "="*80 + "\n")
        print(result)
        print("\n" + "="*80 + "\n")
        print("Note: Use --save to save this to your vault.")

    if TRACKER:
        TRACKER.record_operation(
            script_name="socrates.py",
            operation_type="socratic_inquiry",
            status="success",
            metrics={"question": args.question, "saved": args.save},
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="socrates.py",
                operation_type="socratic_inquiry",
                status="failed",
                metrics={"error": str(e)},
            )
        import sys
        sys.exit(1)
