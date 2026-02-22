"""Track ongoing personal projects in the Obsidian vault."""

import argparse
import re
from datetime import datetime
from pathlib import Path

from config import summarize, save_note, VAULT_PATH

PROJECT_PROMPT = """You are helping define a personal project. Given a brief description, create a structured project note. Output ONLY the following sections in markdown (no YAML, no top-level # title):

## Desired Outcome
> What does "done" look like? Be specific and measurable.

## Why This Matters
- Personal motivation, stakes, or connection to larger goals

## Next Actions
- [ ] First concrete step to take
- [ ] Second step
- [ ] Third step (optional)

## Tasks
- [ ] (Leave empty or add 1–2 high-level tasks if obvious from description)

## Resources & Links
- (Leave empty or add if user mentioned specific resources)

Use [[wikilinks]] for related concepts, areas, or people when relevant.
Be concise. The user can expand later. Do NOT invent scope beyond what the description implies."""

PROJECTS_DIR = "01 - Projects"


def safe_filename(name: str, max_len: int = 60) -> str:
    """Sanitize string for use as filename."""
    return re.sub(r'[\\/*?:"<>|]', "", name)[:max_len].strip()


def create_project(name: str, description: str, due: str = "") -> Path:
    """Create a new project note from a brief description."""
    today = datetime.now().strftime("%Y-%m-%d")
    context = f"Project: {name}\n\nDescription: {description}"
    if due:
        context += f"\n\nTarget due: {due}"

    print("Generating project structure with AI...")
    body = summarize(context, PROJECT_PROMPT)

    safe_name = safe_filename(name)
    filename = f"{PROJECTS_DIR}/{safe_name}.md"

    frontmatter = f"""---
created: "{today}"
tags:
  - type/project
  - status/active
status: active
due: "{due}"
outcome: ""
---

# {name}

{body}

## Log

### {today}
- Project started

## Related

- MOC: [[AI Projects MOC]]
- Area:
"""

    path = save_note(filename, frontmatter)
    print(f"Project created: {path}")
    return path


def list_projects() -> list[Path]:
    """List project notes in the Projects folder."""
    projects_path = VAULT_PATH / PROJECTS_DIR
    if not projects_path.exists():
        return []
    return sorted(
        p for p in projects_path.glob("*.md")
        if not p.name.startswith(".")
    )


def show_list(active_only: bool = True) -> None:
    """Print list of projects."""
    projects = list_projects()
    if not projects:
        print("No projects found in 01 - Projects/")
        return

    print(f"\nProjects ({len(projects)}):")
    print("-" * 50)
    for p in projects:
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


def log_to_project(project_name: str, log_entry: str) -> bool:
    """Append a log entry to an existing project."""
    projects_path = VAULT_PATH / PROJECTS_DIR
    if not projects_path.exists():
        print(f"Projects folder not found: {PROJECTS_DIR}")
        return False

    safe_name = safe_filename(project_name)
    candidates = list(projects_path.glob(f"*{safe_name}*.md"))
    if not candidates:
        print(f"Project not found: {project_name}")
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


def main():
    parser = argparse.ArgumentParser(
        description="Track ongoing personal projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 project_track.py create "Build habit tracker" --desc "Simple app to track daily habits"
  python3 project_track.py create "Learn Rust" --desc "Complete Rust book by Q2"
  python3 project_track.py list
  python3 project_track.py log "Build habit tracker" "Designed database schema"
"""
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument(
        "--desc", "--description",
        dest="description",
        default="",
        help="Brief description of the project",
    )
    create_parser.add_argument("--due", default="", help="Target due date (YYYY-MM-DD)")

    # list
    list_parser = subparsers.add_parser("list", help="List active projects")
    list_parser.add_argument(
        "--all",
        action="store_true",
        help="Show all projects including inactive",
    )

    # log
    log_parser = subparsers.add_parser("log", help="Add log entry to a project")
    log_parser.add_argument("project", help="Project name (partial match)")
    log_parser.add_argument("entry", help="Log entry text")

    args = parser.parse_args()

    if args.command == "create":
        desc = args.description.strip() or args.name
        create_project(args.name, desc, args.due)

    elif args.command == "list":
        show_list(active_only=not getattr(args, "all", False))

    elif args.command == "log":
        log_to_project(args.project, args.entry)

    return 0


if __name__ == "__main__":
    exit(main())
