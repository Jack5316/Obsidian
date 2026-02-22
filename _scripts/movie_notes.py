"""Create structured movie notes for the Obsidian vault."""

import argparse
import os
import re
from typing import Optional

import requests

from config import summarize, save_note

SUMMARY_PROMPT = """You are a film scholar. Create a comprehensive movie note in markdown. Include:

1. **Metadata** (at top, concise)
   - Runtime (e.g., 2h 26m)
   - Release year
   - Director
   - Cast (main actors with roles)
   - Genre(s)

2. **Plot**
   - Brief summary without major spoilers
   - Key narrative beats or structure if notable

3. **Quotes**
   - 3–6 memorable lines, attributed to character when known
   - Format: > "Quote" — Character

4. **Interesting Points**
   - Themes, craft (cinematography, editing, music), cultural impact
   - Connections to other films, directors, or ideas as [[wikilinks]] when relevant

5. **Personal Notes** — only if the user provided observations below. Integrate their thoughts, reactions, or review. If no user notes were provided, omit this section entirely.

Be thorough but readable. Use [[wikilinks]] for Obsidian links to related concepts, films, or people.
Do NOT include YAML frontmatter or a top-level # title — start directly with the Metadata section.
If the user provided personal notes, weave them into the relevant sections rather than a separate block."""


def fetch_omdb(title: str, year: Optional[str] = None) -> Optional[dict]:
    """Fetch movie metadata from OMDb API if key is configured."""
    api_key = os.getenv("OMDB_API_KEY", "")
    if not api_key:
        return None

    params = {"apikey": api_key, "t": title}
    if year:
        params["y"] = year

    try:
        r = requests.get("https://www.omdbapi.com/", params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("Response") == "True":
            return data
    except Exception:
        pass
    return None


def build_context(title: str, year: Optional[str], omdb: Optional[dict], user_notes: Optional[str]) -> str:
    """Build context string for AI."""
    parts = [f"Movie: {title}"]
    if year:
        parts.append(f"Year: {year}")

    if omdb:
        meta = []
        if omdb.get("Runtime") and omdb["Runtime"] != "N/A":
            meta.append(f"Runtime: {omdb['Runtime']}")
        if omdb.get("Year"):
            meta.append(f"Year: {omdb['Year']}")
        if omdb.get("Director") and omdb["Director"] != "N/A":
            meta.append(f"Director: {omdb['Director']}")
        if omdb.get("Actors") and omdb["Actors"] != "N/A":
            meta.append(f"Cast: {omdb['Actors']}")
        if omdb.get("Genre") and omdb["Genre"] != "N/A":
            meta.append(f"Genre: {omdb['Genre']}")
        if omdb.get("Plot") and omdb["Plot"] != "N/A":
            meta.append(f"Plot (from API): {omdb['Plot']}")
        if meta:
            parts.append("\nVerified metadata:\n" + "\n".join(meta))

    if user_notes:
        parts.append(f"\nUser's personal notes/observations:\n{user_notes}")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Create movie notes for Obsidian")
    parser.add_argument("title", help="Movie title")
    parser.add_argument("--year", help="Release year (disambiguation)")
    parser.add_argument("--notes", help="Your personal observations or review")
    args = parser.parse_args()

    title = args.title.strip()
    year = args.year.strip() if args.year else None
    user_notes = args.notes.strip() if args.notes else None

    print(f"Processing: {title}" + (f" ({year})" if year else ""))

    omdb = fetch_omdb(title, year)
    if omdb:
        print("  Fetched metadata from OMDb")
    else:
        print("  Using AI knowledge (add OMDB_API_KEY to .env for verified metadata)")

    context = build_context(title, year, omdb, user_notes)
    print("Generating note with AI...")
    body = summarize(context, SUMMARY_PROMPT)

    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[:80].strip()
    filename = f"Sources/Movie - {safe_title}.md"

    note = f"# {title}\n\n{body}"
    save_note(filename, note)
    print("Done!")


if __name__ == "__main__":
    main()
