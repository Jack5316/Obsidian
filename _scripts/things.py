#!/usr/bin/env python3
"""Things - Add and manage actionable items in Things (macOS) via URL scheme.

Uses the Things URL scheme: https://culturedcode.com/things/support/articles/2803573/
Requires Things 3 for Mac. Auth token needed for update commands.
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

VAULT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = VAULT_ROOT / ".env"


def get_auth_token() -> str:
    """Get Things auth token from .env."""
    token = os.environ.get("THINGS_AUTH_TOKEN", "")
    if not token:
        try:
            from dotenv import load_dotenv
            load_dotenv(ENV_PATH)
            token = os.environ.get("THINGS_AUTH_TOKEN", "")
        except ImportError:
            pass
    return token.strip()


def open_things_url(url: str) -> bool:
    """Open a things:// URL on macOS."""
    if platform.system() != "Darwin":
        print("Things skill requires macOS (Things app).")
        return False
    try:
        subprocess.run(["open", url], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error opening Things: {e}")
        return False


def build_add_url(title: str, when: str = None, list_name: str = None, notes: str = None,
                  tags: str = None, deadline: str = None, reveal: bool = False) -> str:
    """Build things:///add URL."""
    params = [f"title={quote(title)}"]
    if when:
        params.append(f"when={quote(when)}")
    if list_name:
        params.append(f"list={quote(list_name)}")
    if notes:
        params.append(f"notes={quote(notes)}")
    if tags:
        params.append(f"tags={quote(tags)}")
    if deadline:
        params.append(f"deadline={quote(deadline)}")
    if reveal:
        params.append("reveal=true")
    return "things:///add?" + "&".join(params)


def build_add_project_url(title: str, area: str = None, to_dos: str = None,
                          when: str = None, notes: str = None, reveal: bool = False) -> str:
    """Build things:///add-project URL."""
    params = [f"title={quote(title)}"]
    if area:
        params.append(f"area={quote(area)}")
    if to_dos:
        params.append(f"to-dos={quote(to_dos)}")
    if when:
        params.append(f"when={quote(when)}")
    if notes:
        params.append(f"notes={quote(notes)}")
    if reveal:
        params.append("reveal=true")
    return "things:///add-project?" + "&".join(params)


def build_update_url(todo_id: str, auth_token: str, **kwargs) -> str:
    """Build things:///update URL. Requires auth-token."""
    params = [f"auth-token={quote(auth_token)}", f"id={quote(todo_id)}"]
    for k, v in kwargs.items():
        if v is not None:
            key = k.replace("_", "-")
            params.append(f"{key}={quote(str(v))}")
    return "things:///update?" + "&".join(params)


def build_show_url(query: str = None, list_id: str = None) -> str:
    """Build things:///show URL."""
    if list_id:
        return f"things:///show?id={quote(list_id)}"
    if query:
        return f"things:///show?query={quote(query)}"
    return "things:///show?id=today"


def build_search_url(query: str = None) -> str:
    """Build things:///search URL."""
    if query:
        return f"things:///search?query={quote(query)}"
    return "things:///search"


def cmd_add(args) -> int:
    """Add a to-do to Things."""
    title = " ".join(args.title) if args.title else ""
    if not title:
        print("Error: Provide a title. E.g. things add 'Buy milk'")
        return 1
    url = build_add_url(
        title=title,
        when=args.when,
        list_name=args.list,
        notes=args.notes,
        tags=args.tags,
        deadline=args.deadline,
        reveal=args.reveal,
    )
    if open_things_url(url):
        print(f"Added to Things: {title}")
        return 0
    return 1


def cmd_project(args) -> int:
    """Add a project to Things."""
    title = " ".join(args.title) if args.title else ""
    if not title:
        print("Error: Provide a project title.")
        return 1
    to_dos = None
    if args.todos:
        to_dos = "\n".join(args.todos)
    url = build_add_project_url(
        title=title,
        area=args.area,
        to_dos=to_dos,
        when=args.when,
        notes=args.notes,
        reveal=args.reveal,
    )
    if open_things_url(url):
        print(f"Added project to Things: {title}")
        return 0
    return 1


def cmd_update(args) -> int:
    """Update an existing to-do. Requires auth token."""
    token = get_auth_token()
    if not token:
        print("Error: THINGS_AUTH_TOKEN required for update. Add to .env:")
        print("  THINGS_AUTH_TOKEN=your_token")
        print("  Get it from Things → Settings → General → Things URLs → Manage")
        return 1
    kwargs = {}
    if args.when is not None:
        kwargs["when"] = args.when
    if args.title:
        kwargs["title"] = " ".join(args.title)
    if args.completed is not None:
        kwargs["completed"] = "true" if args.completed else "false"
    if args.notes:
        kwargs["notes"] = args.notes
    if args.append_notes:
        kwargs["append-notes"] = args.append_notes
    if not kwargs:
        print("Error: Provide at least one field to update (--when, --title, --completed, --notes)")
        return 1
    url = build_update_url(args.id, token, **kwargs)
    if open_things_url(url):
        print("Updated in Things")
        return 0
    return 1


def cmd_show(args) -> int:
    """Show a list in Things."""
    if args.id:
        url = build_show_url(list_id=args.id)
    elif args.query:
        url = build_show_url(query=args.query)
    else:
        url = build_show_url(list_id="today")
    if open_things_url(url):
        return 0
    return 1


def cmd_search(args) -> int:
    """Search in Things."""
    query = " ".join(args.query) if args.query else ""
    url = build_search_url(query)
    if open_things_url(url):
        return 0
    return 1


def main():
    parser = argparse.ArgumentParser(
        description="Things - Add actionable items to Things (macOS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  things add "Buy milk"
  things add "Call dentist" --when tomorrow --tags Errand
  things add "Submit report" --list Work --deadline 2026-02-25
  things project "Vacation" --area Family --todos "Book flights" "Pack bags"
  things update <id> --when today
  things show today
  things search "meeting"
""",
    )
    sub = parser.add_subparsers(dest="cmd", help="Command")

    # add
    p_add = sub.add_parser("add", help="Add a to-do")
    p_add.add_argument("title", nargs="*", help="To-do title")
    p_add.add_argument("--when", "-w", help="today, tomorrow, evening, anytime, someday, or date")
    p_add.add_argument("--list", "-l", help="Project or area name")
    p_add.add_argument("--notes", "-n", help="Notes")
    p_add.add_argument("--tags", "-t", help="Comma-separated tags")
    p_add.add_argument("--deadline", "-d", help="Deadline (yyyy-mm-dd or natural language)")
    p_add.add_argument("--reveal", action="store_true", help="Show the new to-do")
    p_add.set_defaults(func=cmd_add)

    # project
    p_proj = sub.add_parser("project", help="Add a project")
    p_proj.add_argument("title", nargs="*", help="Project title")
    p_proj.add_argument("--area", "-a", help="Area name")
    p_proj.add_argument("--todos", nargs="*", help="To-do titles (space-separated)")
    p_proj.add_argument("--when", "-w", help="today, tomorrow, etc.")
    p_proj.add_argument("--notes", "-n", help="Project notes")
    p_proj.add_argument("--reveal", action="store_true", help="Show the new project")
    p_proj.set_defaults(func=cmd_project)

    # update
    p_upd = sub.add_parser("update", help="Update a to-do (requires auth token)")
    p_upd.add_argument("id", help="To-do ID (from Share → Copy Link)")
    p_upd.add_argument("--when", "-w", help="today, tomorrow, etc.")
    p_upd.add_argument("--title", "-t", nargs="*", help="New title")
    p_upd.add_argument("--completed", "-c", type=lambda x: x.lower() == "true", help="true/false")
    p_upd.add_argument("--notes", "-n", help="Replace notes")
    p_upd.add_argument("--append-notes", help="Append to notes")
    p_upd.set_defaults(func=cmd_update)

    # show
    p_show = sub.add_parser("show", help="Show Today, Inbox, or a list")
    p_show.add_argument("--id", "-i", help="List ID: today, inbox, anytime, upcoming, someday, logbook")
    p_show.add_argument("--query", "-q", help="Search for list by name")
    p_show.set_defaults(func=cmd_show)

    # search
    p_search = sub.add_parser("search", help="Search to-dos")
    p_search.add_argument("query", nargs="*", help="Search query")
    p_search.set_defaults(func=cmd_search)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
