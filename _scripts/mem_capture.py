#!/usr/bin/env python3
"""Quick memory capture skill - capture fleeting thoughts without context switching.

Creates timestamped notes in your Obsidian vault for quick idea capture.
"""

import argparse
import datetime
import sys
from pathlib import Path
from typing import Optional

from config import save_note, VAULT_PATH, TRACKER

DEFAULT_DESTINATION = "00 - Inbox"
TEMPLATE = """---
type: fleeting-memory
date: {date}
time: {time}
tags:
  - type/fleeting
  - source/mem-skill
---

# {title}

{content}

---
*Captured with /mem skill at {full_timestamp}*
"""


def main():
    parser = argparse.ArgumentParser(
        description="Quick memory capture - /mem for fleeting thoughts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/mem_capture.py "My great idea"
  python3 _scripts/mem_capture.py "Meeting note" --dest "02 - Areas/Meetings"
  python3 _scripts/mem_capture.py "Book idea" --title "New Book Concept"
        """
    )
    parser.add_argument(
        "content", nargs="*", help="Content of the memory (quoted string)"
    )
    parser.add_argument(
        "-t", "--title", help="Custom title (defaults to 'Memory - HH:MM')"
    )
    parser.add_argument(
        "-d", "--dest", default=DEFAULT_DESTINATION,
        help=f"Destination folder (default: {DEFAULT_DESTINATION})"
    )
    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="mem_capture.py",
            operation_type="capture_memory",
            status="in_progress",
            metrics={}
        )

    try:
        # Get content - from args or stdin
        content = " ".join(args.content)
        if not content:
            # Read from stdin if no args provided
            if not sys.stdin.isatty():
                content = sys.stdin.read().strip()
        
        if not content:
            print("Usage: /mem \"Your thought here\"")
            print("Error: No content provided for memory capture")
            if TRACKER:
                TRACKER.record_operation(
                    script_name="mem_capture.py",
                    operation_type="capture_memory",
                    status="failed",
                    metrics={"error": "No content provided"}
                )
            return

        # Generate timestamp
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        full_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Default title
        if not args.title:
            args.title = f"Memory - {time_str}"
        
        # Build filename
        safe_title = args.title.replace("/", "-").replace("\\", "-")
        filename = f"{safe_title} - {date_str}.md"
        dest_path = Path(args.dest) / filename
        
        # Build note content
        note = TEMPLATE.format(
            date=date_str,
            time=time_str,
            title=args.title,
            content=content,
            full_timestamp=full_timestamp
        )
        
        # Save the note
        save_note(str(dest_path), note)
        print(f"✅ Memory captured: {dest_path}")
        
        # Track operation completion
        if TRACKER:
            TRACKER.record_operation(
                script_name="mem_capture.py",
                operation_type="capture_memory",
                status="success",
                metrics={"destination": str(dest_path)}
            )
        
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="mem_capture.py",
                operation_type="capture_memory",
                status="failed",
                metrics={"error": str(e)}
            )
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
