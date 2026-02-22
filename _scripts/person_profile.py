"""Create structured person profiles for the Obsidian vault."""

import argparse
import re
from typing import Optional

from config import summarize, save_note

SUMMARY_PROMPT = """You are building a profile for someone the user follows or studies. Create a comprehensive person note in markdown. Include:

1. **Metadata** (at top, concise)
   - Primary role(s)
   - Domain / field
   - Affiliation(s) (company, institution, etc.) when known

2. **Background**
   - Brief bio, career, education
   - How they became notable

3. **Key Ideas / Contributions**
   - What they're known for
   - Their thinking, frameworks, or philosophy
   - Distinctive perspectives

4. **Notable Quotes**
   - 3–6 memorable statements attributed to them
   - Format: > "Quote" — Source (book, interview, etc.) when known

5. **Works / Projects**
   - Books, articles, companies, products, talks
   - Key outputs worth following

6. **Personal Notes** — only if the user provided observations below. Integrate their thoughts, why they follow this person, or excerpts. If no user notes were provided, omit this section entirely.

7. **Connections**
   - Related people, concepts, or ideas as [[wikilinks]] when relevant

Be thorough but readable. Use [[wikilinks]] for Obsidian links to related concepts, people, or ideas.
Do NOT include YAML frontmatter or a top-level # title — start directly with the Metadata section.
If the user provided personal notes, weave them into the relevant sections rather than a separate block."""


def build_context(name: str, role: Optional[str], user_notes: Optional[str]) -> str:
    """Build context string for AI."""
    parts = [f"Person: {name}"]
    if role:
        parts.append(f"Role/context: {role}")
    if user_notes:
        parts.append(f"\nUser's observations / why they follow / excerpts:\n{user_notes}")
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Create person profiles for Obsidian")
    parser.add_argument("name", help="Person's full name")
    parser.add_argument("--role", help="Role hint (author, researcher, entrepreneur, founder, artist, etc.)")
    parser.add_argument("--notes", help="Your observations, why you follow them, or excerpts to incorporate")
    args = parser.parse_args()

    name = args.name.strip()
    role = args.role.strip() if args.role else None
    user_notes = args.notes.strip() if args.notes else None

    print(f"Building profile: {name}" + (f" ({role})" if role else ""))

    context = build_context(name, role, user_notes)
    print("Generating profile with AI...")
    body = summarize(context, SUMMARY_PROMPT)

    safe_name = re.sub(r'[\\/*?:"<>|]', "", name)[:80].strip()
    filename = f"Sources/Person - {safe_name}.md"

    note = f"# {name}\n\n{body}"
    save_note(filename, note)
    print("Done!")


if __name__ == "__main__":
    main()
