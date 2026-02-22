#!/usr/bin/env python3
"""Wiki - Quickly learn about anything using the Feynman technique, presented as a wiki-style tutorial.

The Feynman method: explain simply, use plain language, build from basics, expose gaps.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

from config import summarize, save_note, VAULT_PATH

FEYNMAN_PROMPT = """You are a teacher using the Feynman technique: if you can't explain it simply, you don't understand it.

Create a wiki-style tutorial on the given topic. Write as if teaching someone with no prior knowledge. Use plain language, concrete analogies, and build step by step.

Structure your response as a markdown wiki/tutorial with these sections (adapt as needed for the topic):

1. **TL;DR** — One paragraph: what is this, in the simplest terms?
2. **The Core Idea** — The single most important concept. Use an analogy (e.g., "X is like Y because...").
3. **Step by Step** — Break it down into digestible chunks. Number or bullet. No jargon without immediate explanation.
4. **Common Misconceptions** — What people often get wrong, and why.
5. **Key Takeaways** — 3–5 bullet points to remember.
6. **Go Deeper** — 1–2 questions to test understanding, or topics to explore next.

Rules:
- Use simple words. Replace jargon with plain language, or explain it right away.
- One idea per paragraph. Short sentences.
- Use [[wikilinks]] for key concepts where useful (Obsidian).
- No YAML frontmatter. Start directly with the first heading.
- Be concise but complete. Aim for clarity over comprehensiveness."""


def sanitize_filename(s: str) -> str:
    """Make a safe filename from topic string."""
    s = re.sub(r'[<>:"/\\|?*]', "", s)
    s = s.strip() or "topic"
    return s[:80]


def main():
    parser = argparse.ArgumentParser(
        description="Wiki - Learn anything using the Feynman technique (wiki-style tutorial)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/wiki.py "quantum entanglement"
  python3 _scripts/wiki.py recursion --save
  python3 _scripts/wiki.py "how SSL certificates work"
""",
    )
    parser.add_argument("topic", help="Topic to learn (anything)")
    parser.add_argument("--save", action="store_true", help="Save to vault as Atlas/Wiki - TOPIC.md")
    parser.add_argument("--no-save", action="store_true", help="Print only (default)")
    args = parser.parse_args()

    topic = args.topic.strip()
    if not topic:
        print("Please provide a topic.")
        return

    print(f"Generating Feynman-style wiki for: {topic}...")
    content = summarize(topic, FEYNMAN_PROMPT)

    # Add header
    today = datetime.now().strftime("%Y-%m-%d")
    note = f"""---
type: wiki
topic: {topic}
date: {today}
method: feynman
tags:
  - wiki
  - learning
  - feynman
---

# {topic}

> *Feynman-style wiki: explain simply, build from basics.*

---

{content}

---

*Generated using the Feynman technique. If you can't explain it simply, you don't understand it.*
"""

    print(note)

    if args.save:
        safe = sanitize_filename(topic)
        path = f"Atlas/Wiki - {safe}.md"
        save_note(path, note)
        print(f"\nSaved: {path}")


if __name__ == "__main__":
    main()
