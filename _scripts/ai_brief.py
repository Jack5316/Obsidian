"""AI Brief — Morning brew of AI news worth your time.

Runs ArXiv, HN, Reddit, and skills.sh digests, then synthesizes an AI-focused
brief. Designed for a quick morning scan.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH, TRACKER

# Scripts to run for AI-relevant content (in order)
FETCH_SCRIPTS = [
    ("arxiv_digest.py", "ArXiv papers (LLM, transformers, etc.)"),
    ("hn_newsletter.py", "Hacker News top stories"),
    ("reddit_digest.py", "Reddit (MachineLearning, LocalLLaMA, etc.)"),
    ("skill_grab.py", "Trending AI agent skills from skills.sh"),
]
# Optional: add twitter_capture.py if user has AI accounts configured

# Note patterns: (filename_contains, type_for_synthesis)
# Only these sources are AI-relevant for the brief
NOTE_PATTERNS = [
    ("ArXiv Digest", "arxiv-digest"),
    ("HN Newsletter", "hn-newsletter"),
    ("Reddit Digest", "reddit-digest"),
    ("Skills Digest", "skills-digest"),
    ("Twitter Digest", "twitter-digest"),
]
AI_BRIEF_SOURCE_TYPES = {"arxiv-digest", "hn-newsletter", "reddit-digest", "skills-digest", "twitter-digest"}

AI_BRIEF_PROMPT = """You are curating a morning AI brief for someone who cares about AI/ML but has limited time.

Given today's curated content from ArXiv, Hacker News, Reddit, and skills.sh, produce a **concise morning brew** that is WORTH THEIR TIME. Filter aggressively — only include items that matter for AI practitioners, researchers, or enthusiasts.

Format:

## ☕ Must-Read (2–4 items)
The top signals: breakthrough papers, major product launches, paradigm shifts, or genuinely surprising discussions. One sentence each + why it matters.

## 📄 Research Highlights
Key ArXiv papers worth skimming. One line per paper. Skip routine incremental work.

## 🌐 Community Buzz
Notable HN/Reddit threads: new tools, heated debates, contrarian takes. One line each.

## 🛠 Tools & Skills (if present)
Top 3–5 agent skills or tools from skills.sh that are actually useful for AI work. Include install command.

## One-Liner
A single sentence capturing today's AI signal. If nothing stands out, say so honestly.

Use [[wikilinks]] for concepts. No YAML frontmatter. Start directly with Must-Read.
Be ruthless: if a source has nothing AI-relevant today, omit it. Quality over quantity."""


def run_script(script_name: str, cwd: Path) -> bool:
    """Run a script and return success."""
    try:
        proc = subprocess.run(
            ["python3", f"_scripts/{script_name}"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=300,
        )
        if proc.returncode != 0 and proc.stderr:
            print(f"  Warning: {script_name} — {proc.stderr[:200]}")
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  Warning: {script_name} timed out")
        return False
    except Exception as e:
        print(f"  Warning: {script_name} — {e}")
        return False


def collect_today_notes(sources_dir: Path, today_str: str) -> list:
    """Collect today's digest notes for AI Brief synthesis."""
    notes = []
    for md_file in sorted(sources_dir.glob("*.md")):
        if today_str not in md_file.name:
            continue
        content = md_file.read_text(encoding="utf-8")
        # Match note type by filename
        note_type = "unknown"
        for pattern, ntype in NOTE_PATTERNS:
            if pattern in md_file.name:
                note_type = ntype
                break
        # Skip synthesis/reflection to avoid loops
        if note_type in {"daily-synthesis", "weekly-synthesis", "self-reflection", "ai-brief"}:
            continue
        # Only include AI-relevant sources
        if note_type not in AI_BRIEF_SOURCE_TYPES:
            continue
        # Extract body (skip frontmatter)
        body = content
        fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if fm_match:
            body = content[fm_match.end():]
        notes.append({
            "filename": md_file.stem,
            "type": note_type,
            "content": body[:3000],
        })
    return notes


def main():
    parser = argparse.ArgumentParser(
        description="AI Brief — Morning brew of AI news",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/ai_brief.py              # Fetch sources + synthesize
  python3 _scripts/ai_brief.py --skip-fetch # Use existing digests only
  python3 _scripts/ai_brief.py --no-save    # Print only, don't save
""",
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip fetching; use today's existing digests only",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Print brief to stdout only, don't save to vault",
    )
    args = parser.parse_args()

    vault = VAULT_PATH
    sources_dir = vault / "Sources"
    today_str = datetime.now().strftime("%Y-%m-%d")

    if TRACKER:
        TRACKER.record_operation(
            script_name="ai_brief.py",
            operation_type="ai_brief",
            status="in_progress",
        )

    # Step 1: Fetch sources (unless skipped)
    if not args.skip_fetch:
        print("Fetching AI-relevant sources...")
        for script_name, desc in FETCH_SCRIPTS:
            print(f"  Running {script_name} ({desc})...")
            run_script(script_name, vault)
        print()

    # Step 2: Collect today's notes
    if not sources_dir.exists():
        print("No Sources directory. Run with default (no --skip-fetch) first.")
        return 1

    notes = collect_today_notes(sources_dir, today_str)

    if len(notes) < 2:
        print(
            f"Need at least 2 source notes for AI Brief (found {len(notes)}). "
            "Run without --skip-fetch to fetch first."
        )
        return 1

    print(f"Found {len(notes)} notes: {[n['filename'] for n in notes]}")

    # Step 3: Format for AI
    notes_text = "\n\n---\n\n".join(
        "SOURCE: [[{filename}]] (type: {type})\n\n{content}".format(**n)
        for n in notes
    )
    if len(notes_text) > 35000:
        notes_text = notes_text[:35000] + "\n\n[Truncated...]"

    # Step 4: Synthesize
    print("Generating AI Brief...")
    brief_body = summarize(notes_text, AI_BRIEF_PROMPT)

    # Step 5: Build note
    source_index = "\n".join(
        "- [[{}]] ({})".format(n["filename"], n["type"]) for n in notes
    )

    note = f"""---
type: ai-brief
date: {today_str}
source_count: {len(notes)}
tags:
  - source/ai-brief
  - review/daily
---

# AI Brief — {today_str}

> [!info] Morning brew of AI news worth your time

{brief_body}

---

## Sources

{source_index}
"""

    if args.no_save:
        print(note)
        return 0

    save_note(f"Sources/AI Brief - {today_str}.md", note)
    print(f"Done! AI Brief saved.")

    if TRACKER:
        TRACKER.record_operation(
            script_name="ai_brief.py",
            operation_type="ai_brief",
            status="success",
            metrics={
                "notes_processed": len(notes),
                "output_file": f"Sources/AI Brief - {today_str}.md",
            },
        )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="ai_brief.py",
                operation_type="ai_brief",
                status="failed",
                metrics={"error": str(e)},
            )
        sys.exit(1)
