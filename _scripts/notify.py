#!/usr/bin/env python3
"""Notify - Send macOS system notifications.

Use for pipeline completion alerts, scheduler callbacks, or quick reminders.
"""

import argparse
import platform
import subprocess
import sys


def notify(title: str, message: str = "", sound: bool = True) -> bool:
    """Send macOS notification via osascript."""
    if platform.system() != "Darwin":
        print("Notify requires macOS.")
        return False
    msg = message.replace('"', '\\"').replace("\n", " ")
    title_esc = title.replace('"', '\\"')
    script = f'display notification "{msg}" with title "{title_esc}"'
    if sound:
        script += ' sound name "default"'
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Send macOS notification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/notify.py "Done" "Daily curation complete"
  python3 _scripts/notify.py "Reminder" "Call dentist at 3pm" --no-sound
""",
    )
    parser.add_argument("title", help="Notification title")
    parser.add_argument("message", nargs="*", help="Notification body (optional)")
    parser.add_argument("--no-sound", action="store_true", help="Silent notification")
    args = parser.parse_args()

    msg = " ".join(args.message) if args.message else ""
    if notify(args.title, msg, sound=not args.no_sound):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
