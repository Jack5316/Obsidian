"""Log and analyze behavioral patterns (habits) in the Obsidian vault."""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

from config import summarize, save_note, VAULT_PATH

HABIT_PROMPT = """You are helping define a habit to track. Given a brief description, create a structured habit note. Output ONLY the following sections in markdown (no YAML, no top-level # title):

## What It Is
> One sentence: what is this habit?

## Why Track It
- Personal motivation or connection to goals

## When / How
- Best time of day or trigger (e.g., "after morning coffee", "before bed")
- Any specific criteria (e.g., "at least 10 min")

Use [[wikilinks]] for related concepts when relevant.
Be concise."""

ANALYZE_PROMPT = """You are a behavioral pattern analyst. Given:
1. Habit definitions and their check-in history (dates when each habit was done)
2. Optional: Daily/Weekly Synthesis notes (what the user actually did, learned, engaged with)

Produce an analysis:

1. **Streaks & Consistency** — Current streak, longest streak, compliance rate (% of days) for each habit
2. **Trends** — Is the habit improving, declining, or stable over the period?
3. **Patterns** — What days/times tend to have compliance? What correlates with misses?
4. **Synthesis Cross-Reference** (if synthesis notes provided) — On high-compliance days, what was different? On miss days, what was going on? Any cross-domain insights?

Be honest. If data is sparse, say so. Use [[wikilinks]] to reference notes.
Keep it actionable. No fluff."""

HABITS_DIR = "Habits"


def safe_filename(name: str, max_len: int = 60) -> str:
    """Sanitize string for use as filename."""
    return re.sub(r'[\\/*?:"<>|]', "", name)[:max_len].strip()


def create_habit(name: str, description: str = "") -> Path:
    """Create a new habit note from a brief description."""
    today = datetime.now().strftime("%Y-%m-%d")
    context = f"Habit: {name}\n\nDescription: {description or name}"

    print("Generating habit structure with AI...")
    body = summarize(context, HABIT_PROMPT)

    safe_name = safe_filename(name)
    filename = f"{HABITS_DIR}/{safe_name}.md"

    frontmatter = f"""---
created: "{today}"
tags:
  - type/habit
  - status/active
status: active
---

# {name}

{body}

## Check-ins

### {today}
- Logged
"""

    path = save_note(filename, frontmatter)
    print(f"Habit created: {path}")
    return path


def list_habits() -> list[Path]:
    """List habit notes in the Habits folder."""
    habits_path = VAULT_PATH / HABITS_DIR
    if not habits_path.exists():
        return []
    return sorted(
        p for p in habits_path.glob("*.md")
        if not p.name.startswith(".")
    )


def show_list(active_only: bool = True) -> None:
    """Print list of habits."""
    habits = list_habits()
    if not habits:
        print(f"No habits found in {HABITS_DIR}/")
        return

    print(f"\nHabits ({len(habits)}):")
    print("-" * 50)
    for p in habits:
        content = p.read_text(encoding="utf-8")
        status = "active"
        if "status:" in content:
            for line in content.split("\n"):
                if line.strip().startswith("status:"):
                    status = line.split(":", 1)[1].strip().strip('"')
                    break
        if active_only and status != "active":
            continue

        # Count check-ins
        check_count = len(re.findall(r"^### \d{4}-\d{2}-\d{2}", content, re.MULTILINE))
        print(f"  • {p.stem} ({status}) — {check_count} check-ins")


def log_habit(habit_name: str, note: str = "") -> bool:
    """Log a check-in for a habit (today)."""
    habits_path = VAULT_PATH / HABITS_DIR
    if not habits_path.exists():
        print(f"Habits folder not found: {HABITS_DIR}")
        return False

    safe_name = safe_filename(habit_name)
    candidates = list(habits_path.glob(f"*{safe_name}*.md"))
    if not candidates:
        print(f"Habit not found: {habit_name}")
        return False

    path = candidates[0]
    content = path.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if already logged today
    if f"### {today}" in content:
        entry = f"- {note}" if note else "- (updated)"
        # Replace first line under ### today
        old_block = re.search(rf"(### {today}\s*\n)(- [^\n]*)", content)
        if old_block:
            content = content.replace(old_block.group(0), f"### {today}\n{entry}")
    else:
        entry = f"- {note}" if note else "- Done"
        check_section = f"\n### {today}\n{entry}\n"
        if "## Check-ins" in content:
            content = content.replace("## Check-ins\n", f"## Check-ins\n{check_section}")
        else:
            content += f"\n## Check-ins\n{check_section}"

    path.write_text(content, encoding="utf-8")
    print(f"Logged to {path.name}")
    return True


def parse_check_in_dates(content: str) -> list[str]:
    """Extract dates from ## Check-ins section."""
    dates = []
    in_checkins = False
    for line in content.split("\n"):
        if line.strip() == "## Check-ins":
            in_checkins = True
            continue
        if in_checkins and line.strip().startswith("## "):
            break
        m = re.match(r"^### (\d{4}-\d{2}-\d{2})$", line.strip())
        if m:
            dates.append(m.group(1))
    return sorted(dates, reverse=True)


def collect_habits_content(active_only: bool = True) -> str:
    """Collect habit definitions and check-in history."""
    habits = list_habits()
    if not habits:
        return ""

    parts = []
    for p in habits:
        content = p.read_text(encoding="utf-8")
        status = "active"
        if "status:" in content:
            for line in content.split("\n"):
                if line.strip().startswith("status:"):
                    status = line.split(":", 1)[1].strip().strip('"')
                    break
        if active_only and status != "active":
            continue

        dates = parse_check_in_dates(content)
        body = content
        fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if fm_match:
            body = content[fm_match.end():]

        # Truncate body to definition (before Check-ins)
        if "## Check-ins" in body:
            body = body.split("## Check-ins")[0].strip()

        date_list = ", ".join(dates[:30])  # Last 30 check-ins
        if len(dates) > 30:
            date_list += f" ... (+{len(dates) - 30} more)"

        parts.append(f"HABIT: [[{p.stem}]]\n\n{body[:1500]}\n\nCheck-in dates: {date_list}")

    return "\n\n---\n\n".join(parts)


def collect_synthesis_notes(days: int = 7) -> list[dict]:
    """Collect Daily and Weekly Synthesis notes from Sources/."""
    sources_dir = VAULT_PATH / "Sources"
    if not sources_dir.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days)
    notes = []

    for pattern in ["Daily Synthesis - *.md", "Weekly Synthesis - *.md"]:
        for md_file in sources_dir.glob(pattern):
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
            if mtime < cutoff:
                continue

            content = md_file.read_text(encoding="utf-8")
            body = content
            fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
            if fm_match:
                body = content[fm_match.end():]

            notes.append({
                "filename": md_file.stem,
                "date": mtime.strftime("%Y-%m-%d"),
                "content": body[:4000],
            })

    notes.sort(key=lambda n: n["date"], reverse=True)
    return notes


def analyze_habits(days: int = 30, include_synthesis: bool = True, save: bool = True) -> None:
    """Analyze habit patterns and generate report."""
    habits_text = collect_habits_content()
    if not habits_text:
        print("No active habits found. Create habits first with: habit_track.py create \"Habit name\"")
        return

    synthesis_text = ""
    if include_synthesis:
        synthesis_notes = collect_synthesis_notes(days)
        if synthesis_notes:
            synthesis_text = "\n\n---\n\n## Recent Synthesis (What I Actually Did/Learned)\n\n"
            synthesis_text += "\n\n---\n\n".join(
                f"NOTE: [[{n['filename']}]] (date: {n['date']})\n\n{n['content']}"
                for n in synthesis_notes
            )

    combined = f"""## Habits & Check-in History

{habits_text}
{synthesis_text}
"""

    if len(combined) > 50000:
        combined = combined[:50000] + "\n\n[Truncated...]"

    print("Generating habit analysis with AI...")
    analysis_body = summarize(combined, ANALYZE_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")
    habits_count = len([h for h in habits_text.split("HABIT:") if h.strip()])
    note = f"""---
type: habit-analysis
date: {today}
habits_analyzed: {habits_count}
days: {days}
tags:
  - review/habit
  - behavior
---

# Habit Analysis - {today}

> [!info] Behavioral pattern analysis

{analysis_body}
"""

    if save:
        save_note(f"Sources/Habit Analysis - {today}.md", note)
        print(f"Habit analysis saved: Sources/Habit Analysis - {today}.md")
    else:
        print("\n" + "=" * 60 + "\n")
        print(analysis_body)


def main():
    parser = argparse.ArgumentParser(
        description="Log and analyze behavioral patterns (habits)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 habit_track.py create "Morning meditation"
  python3 habit_track.py create "Read 30 min" --desc "Daily reading habit"
  python3 habit_track.py list
  python3 habit_track.py log "Morning meditation"
  python3 habit_track.py log "Read 30 min" "Finished chapter 3"
  python3 habit_track.py analyze --days 30
  python3 habit_track.py analyze --days 14 --no-synthesis --no-save
""",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    create_parser = subparsers.add_parser("create", help="Create a new habit")
    create_parser.add_argument("name", help="Habit name")
    create_parser.add_argument(
        "--desc", "--description",
        dest="description",
        default="",
        help="Brief description of the habit",
    )

    # list
    list_parser = subparsers.add_parser("list", help="List active habits")
    list_parser.add_argument(
        "--all",
        action="store_true",
        help="Show all habits including inactive",
    )

    # log
    log_parser = subparsers.add_parser("log", help="Log a check-in for today")
    log_parser.add_argument("habit", help="Habit name (partial match)")
    log_parser.add_argument("note", nargs="*", default=[], help="Optional note for the check-in")

    # analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze habit patterns")
    analyze_parser.add_argument("--days", type=int, default=30, help="Look back N days (default: 30)")
    analyze_parser.add_argument("--no-synthesis", action="store_true", help="Skip cross-reference with Daily/Weekly Synthesis")
    analyze_parser.add_argument("--no-save", action="store_true", help="Print to terminal instead of saving")

    args = parser.parse_args()

    if args.command == "create":
        create_habit(args.name, getattr(args, "description", ""))

    elif args.command == "list":
        show_list(active_only=not getattr(args, "all", False))

    elif args.command == "log":
        note = " ".join(getattr(args, "note", []) or []).strip() or None
        log_habit(args.habit, note)

    elif args.command == "analyze":
        analyze_habits(
            days=getattr(args, "days", 30),
            include_synthesis=not getattr(args, "no_synthesis", False),
            save=not getattr(args, "no_save", False),
        )

    return 0


if __name__ == "__main__":
    exit(main())
