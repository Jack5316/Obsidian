"""Track goals and review them against daily/weekly synthesis logs."""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

from config import summarize, save_note, VAULT_PATH

GOAL_PROMPT = """You are helping define a personal goal. Given a brief description, create a structured goal note. Output ONLY the following sections in markdown (no YAML, no top-level # title):

## Desired Outcome
> What does success look like? Be specific and measurable if possible.

## Why This Matters
- Personal motivation or connection to larger purpose

## Target
- Timeframe (e.g., this quarter, by end of year)
- Key milestones if relevant

## Success Criteria
- [ ] (1–3 concrete checkpoints to know you're on track)

Use [[wikilinks]] for related concepts when relevant.
Be concise. The user can expand later."""

REVIEW_PROMPT = """You are a goal-alignment reviewer. Given:
1. The user's active goals (what they want to achieve)
2. Their recent daily and weekly synthesis notes (what they actually did, learned, and engaged with)

Assess:

1. **Alignment** — Which goals are being served by recent activity? Cite specific synthesis content.
2. **Gaps** — Which goals have no visible traction in the logs? What's missing?
3. **Surprises** — Did the logs reveal activity that could support a goal but isn't yet connected?
4. **Recommendations** — 1–3 concrete next actions to better align activity with goals. Be specific.

Be honest. If logs are sparse or goals are vague, say so. Use [[wikilinks]] to reference notes.
Keep it actionable. No fluff."""

GOALS_DIR = "Goals"


def safe_filename(name: str, max_len: int = 60) -> str:
    """Sanitize string for use as filename."""
    return re.sub(r'[\\/*?:"<>|]', "", name)[:max_len].strip()


def create_goal(name: str, description: str, target: str = "") -> Path:
    """Create a new goal note from a brief description."""
    today = datetime.now().strftime("%Y-%m-%d")
    context = f"Goal: {name}\n\nDescription: {description}"
    if target:
        context += f"\n\nTarget: {target}"

    print("Generating goal structure with AI...")
    body = summarize(context, GOAL_PROMPT)

    safe_name = safe_filename(name)
    filename = f"{GOALS_DIR}/{safe_name}.md"

    frontmatter = f"""---
created: "{today}"
tags:
  - type/goal
  - status/active
status: active
target: "{target}"
---

# {name}

{body}

## Log

### {today}
- Goal set

## Related

- Projects:
- Synthesis reviews:
"""

    path = save_note(filename, frontmatter)
    print(f"Goal created: {path}")
    return path


def list_goals() -> list[Path]:
    """List goal notes in the Goals folder."""
    goals_path = VAULT_PATH / GOALS_DIR
    if not goals_path.exists():
        return []
    return sorted(
        p for p in goals_path.glob("*.md")
        if not p.name.startswith(".")
    )


def show_list(active_only: bool = True) -> None:
    """Print list of goals."""
    goals = list_goals()
    if not goals:
        print(f"No goals found in {GOALS_DIR}/")
        return

    print(f"\nGoals ({len(goals)}):")
    print("-" * 50)
    for p in goals:
        content = p.read_text(encoding="utf-8")
        status = "active"
        if "status:" in content:
            for line in content.split("\n"):
                if line.strip().startswith("status:"):
                    status = line.split(":", 1)[1].strip().strip('"')
                    break
        if active_only and status != "active":
            continue
        print(f"  • {p.stem} ({status})")


def log_to_goal(goal_name: str, log_entry: str) -> bool:
    """Append a log entry to an existing goal."""
    goals_path = VAULT_PATH / GOALS_DIR
    if not goals_path.exists():
        print(f"Goals folder not found: {GOALS_DIR}")
        return False

    safe_name = safe_filename(goal_name)
    candidates = list(goals_path.glob(f"*{safe_name}*.md"))
    if not candidates:
        print(f"Goal not found: {goal_name}")
        return False

    path = candidates[0]
    content = path.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    log_section = f"\n### {today}\n- {log_entry}\n"
    if "## Log" in content:
        content = content.replace("## Log\n", f"## Log\n{log_section}")
    else:
        content += f"\n## Log\n{log_section}"

    path.write_text(content, encoding="utf-8")
    print(f"Logged to {path.name}")
    return True


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


def collect_goals_content(active_only: bool = True) -> str:
    """Collect content of all (active) goals."""
    goals = list_goals()
    if not goals:
        return ""

    parts = []
    for p in goals:
        content = p.read_text(encoding="utf-8")
        status = "active"
        if "status:" in content:
            for line in content.split("\n"):
                if line.strip().startswith("status:"):
                    status = line.split(":", 1)[1].strip().strip('"')
                    break
        if active_only and status != "active":
            continue

        body = content
        fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if fm_match:
            body = content[fm_match.end():]

        parts.append(f"GOAL: [[{p.stem}]]\n\n{body[:2000]}")

    return "\n\n---\n\n".join(parts)


def review_goals(days: int = 7, save: bool = True) -> None:
    """Review goals against daily/weekly synthesis and generate report."""
    goals_text = collect_goals_content()
    if not goals_text:
        print("No active goals found. Create goals first with: goal_track.py create \"Goal name\"")
        return

    synthesis_notes = collect_synthesis_notes(days)
    if not synthesis_notes:
        print(f"No Daily or Weekly Synthesis notes found in Sources/ from the last {days} days.")
        print("Run daily_synthesis.py and weekly_synthesis.py to generate logs.")
        return

    synthesis_text = "\n\n---\n\n".join(
        f"NOTE: [[{n['filename']}]] (date: {n['date']})\n\n{n['content']}"
        for n in synthesis_notes
    )

    combined = f"""## Active Goals

{goals_text}

---

## Recent Synthesis (What I Actually Did/Learned)

{synthesis_text}
"""

    if len(combined) > 50000:
        combined = combined[:50000] + "\n\n[Truncated...]"

    print("Generating goal review with AI...")
    review_body = summarize(combined, REVIEW_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")
    goals_count = len([g for g in goals_text.split("GOAL:") if g.strip()])
    note = f"""---
type: goal-review
date: {today}
goals_reviewed: {goals_count}
synthesis_notes: {len(synthesis_notes)}
tags:
  - review/goal
  - alignment
---

# Goal Review - {today}

> [!info] Alignment of goals vs. daily/weekly synthesis

{review_body}

---

## Synthesis Notes Used

{chr(10).join('- [[' + n['filename'] + ']] (' + n['date'] + ')' for n in synthesis_notes)}
"""

    if save:
        save_note(f"Sources/Goal Review - {today}.md", note)
        print(f"Goal review saved: Sources/Goal Review - {today}.md")
    else:
        print("\n" + "=" * 60 + "\n")
        print(review_body)


def main():
    parser = argparse.ArgumentParser(
        description="Track goals and review against daily/weekly logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 goal_track.py create "Read 12 books this year" --desc "Focus on philosophy and AI"
  python3 goal_track.py create "Ship faster" --target "Q2 2026"
  python3 goal_track.py list
  python3 goal_track.py log "Read 12 books" "Finished Meditations"
  python3 goal_track.py review --days 7
  python3 goal_track.py review --days 14 --no-save
"""
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    create_parser = subparsers.add_parser("create", help="Create a new goal")
    create_parser.add_argument("name", help="Goal name")
    create_parser.add_argument(
        "--desc", "--description",
        dest="description",
        default="",
        help="Brief description of the goal",
    )
    create_parser.add_argument("--target", default="", help="Target timeframe (e.g., Q2 2026)")

    # list
    list_parser = subparsers.add_parser("list", help="List active goals")
    list_parser.add_argument(
        "--all",
        action="store_true",
        help="Show all goals including inactive",
    )

    # log
    log_parser = subparsers.add_parser("log", help="Add log entry to a goal")
    log_parser.add_argument("goal", help="Goal name (partial match)")
    log_parser.add_argument("entry", help="Log entry text")

    # review
    review_parser = subparsers.add_parser("review", help="Review goals against daily/weekly synthesis")
    review_parser.add_argument("--days", type=int, default=7, help="Look back N days for synthesis (default: 7)")
    review_parser.add_argument("--no-save", action="store_true", help="Print to terminal instead of saving")

    args = parser.parse_args()

    if args.command == "create":
        desc = (args.description or args.name).strip()
        create_goal(args.name, desc, getattr(args, "target", ""))

    elif args.command == "list":
        show_list(active_only=not getattr(args, "all", False))

    elif args.command == "log":
        log_to_goal(args.goal, args.entry)

    elif args.command == "review":
        review_goals(
            days=getattr(args, "days", 7),
            save=not getattr(args, "no_save", False),
        )

    return 0


if __name__ == "__main__":
    exit(main())
