"""Thinking Pattern - Decode the cognitive structure underlying your writing.

Analyzes a piece of writing to reveal the thinking patterns embedded in it:
- Reasoning style (deductive, inductive, abductive)
- Argument structure and logical flow
- Cognitive frameworks and mental models in use
- Assumptions and implicit beliefs
- Decision-making patterns
- Blind spots and unexamined premises

Use when you want to understand how you think by examining what you write.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


THINKING_PATTERN_PROMPT = """You are an expert in cognitive analysis and writing-as-thinking. Your task is to decode the thinking pattern underlying a piece of writing — to infer how the author thinks from how they write.

**Principle:** Writing is thought made visible. Structure, word choice, argument flow, and rhetorical moves reveal cognitive patterns.

## Analysis Dimensions

### 1. Reasoning Style
- **Deductive** (general → specific): Do they state principles first, then apply?
- **Inductive** (specific → general): Do they accumulate examples, then conclude?
- **Abductive** (inference to best explanation): Do they propose hypotheses and test?
- **Dialectical** (thesis → antithesis → synthesis): Do they hold tensions, then resolve?
- **Associative** (connection by analogy/metaphor): Do they think in parallels and leaps?

### 2. Argument Structure
- How do claims relate to evidence? (claim-first vs evidence-first)
- What logical connectors dominate? (therefore, because, however, if-then)
- Is the structure linear, branching, or recursive?
- Where does the writer place their strongest point? (primacy, recency, buried)

### 3. Cognitive Frameworks in Use
- What mental models appear? (e.g., first principles, inversion, opportunity cost)
- What frameworks from philosophy, economics, or psychology are implicit?
- How do they handle uncertainty? (probabilistic, binary, deferred)
- What counts as "proof" or "good enough" for them?

### 4. Assumptions and Implicit Beliefs
- What does the writer take for granted?
- What goes unsaid but shapes the argument?
- What would they need to believe for this to make sense?
- Where might their priors be limiting?

### 5. Decision-Making Patterns
- How do they weigh options? (explicit criteria vs intuition)
- What tradeoffs do they acknowledge vs ignore?
- How do they handle conflicting values?
- What triggers certainty vs doubt?

### 6. Blind Spots and Unexamined Premises
- What might they be unable to see from within their frame?
- What would an outsider notice that they miss?
- What questions does the writing avoid?
- Where does the reasoning feel forced or defensive?

## Output Format

- Use markdown with clear ## and ### headings
- Be specific: cite phrases or structural features from the text as evidence
- Be constructive: aim to illuminate, not judge
- If a dimension has insufficient signal, say so
- End with a brief "Thinking Pattern Summary" — 2–3 sentences capturing the core cognitive fingerprint
- No YAML frontmatter — start directly with # Thinking Pattern Analysis
"""


def decode_thinking_pattern(text: str, focus: Optional[str] = None) -> str:
    """Send writing to AI for thinking pattern analysis."""
    user_content = f"""Analyze the following writing and decode the thinking pattern underlying it.

{f'**Focus:** Pay special attention to: {focus}' if focus else ''}

---
Writing to analyze:
---
{text}
"""
    return summarize(user_content, THINKING_PATTERN_PROMPT)


def main():
    parser = argparse.ArgumentParser(
        description="Thinking Pattern - Decode the cognitive structure underlying your writing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/thinking_pattern.py path/to/note.md
  python3 _scripts/thinking_pattern.py path/to/note.md --focus "reasoning style"
  python3 _scripts/thinking_pattern.py path/to/note.md --save
  echo "Your text here" | python3 _scripts/thinking_pattern.py -
""",
    )
    parser.add_argument(
        "input",
        type=str,
        nargs="?",
        default="-",
        help="Path to markdown/text file, or '-' for stdin",
    )
    parser.add_argument(
        "--focus",
        type=str,
        default=None,
        help="Focus on one dimension: reasoning, structure, frameworks, assumptions, decisions, blindspots",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to Sources folder",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom output path (overrides --save default)",
    )
    args = parser.parse_args()

    # Read input
    if args.input == "-":
        text = sys.stdin.read()
        source_name = "stdin"
    else:
        path = Path(args.input)
        if not path.is_absolute():
            path = VAULT_PATH / args.input
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        text = path.read_text(encoding="utf-8")
        source_name = path.stem

    if not text.strip():
        print("Error: No content to analyze.", file=sys.stderr)
        sys.exit(1)

    # Limit input size for token efficiency (keep ~8k chars)
    if len(text) > 12000:
        text = text[:12000] + "\n\n[... truncated for analysis ...]"

    result = decode_thinking_pattern(text, args.focus)

    # Add source attribution
    header = f"# Thinking Pattern Analysis\n\n**Source:** {source_name}\n**Analyzed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n"
    full_output = header + result

    print(full_output)

    if args.save or args.output:
        if args.output:
            out_path = args.output
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
            out_path = f"Sources/Thinking Pattern - {source_name} - {date_str}.md"
        save_note(out_path, full_output)


if __name__ == "__main__":
    main()
