#!/usr/bin/env python3
"""Scheduler - Automate and schedule tasks (skills/pipelines) to run automatically.

Uses launchd on macOS for periodic execution. Supports daily, weekly, and cron schedules.
"""

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = VAULT_ROOT / "_config"
SCHEDULE_JSON = CONFIG_DIR / "schedule.json"
STATE_JSON = CONFIG_DIR / "schedule_state.json"
LOGS_DIR = VAULT_ROOT / "_logs"

# Default schedule config
DEFAULT_SCHEDULE = {
    "tasks": [
        {
            "id": "daily-curation",
            "target": "org-daily",
            "target_type": "skill",
            "schedule": "daily",
            "time": "09:00",
            "enabled": True,
        },
        {
            "id": "weekly-synthesis",
            "target": "org-weekly",
            "target_type": "skill",
            "schedule": "weekly",
            "day": "monday",
            "time": "10:00",
            "enabled": True,
        },
    ]
}

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def load_schedule() -> dict:
    """Load schedule config."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not SCHEDULE_JSON.exists():
        SCHEDULE_JSON.write_text(json.dumps(DEFAULT_SCHEDULE, indent=2), encoding="utf-8")
        return DEFAULT_SCHEDULE
    return json.loads(SCHEDULE_JSON.read_text(encoding="utf-8"))


def save_schedule(data: dict) -> None:
    """Save schedule config."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SCHEDULE_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_state() -> dict:
    """Load last-run state."""
    if not STATE_JSON.exists():
        return {}
    try:
        return json.loads(STATE_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state: dict) -> None:
    """Save last-run state."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(state, indent=2), encoding="utf-8")


def parse_time(s: str) -> tuple:
    """Parse HH:MM or H:MM to (hour, minute)."""
    parts = s.strip().split(":")
    h = int(parts[0]) if parts else 0
    m = int(parts[1]) if len(parts) > 1 else 0
    return (h, m)


def is_due_daily(task: dict, now: datetime, last_run: str) -> bool:
    """Check if daily task is due (run once per day at specified time)."""
    if task.get("schedule") != "daily":
        return False
    if last_run and last_run.startswith(now.strftime("%Y-%m-%d")):
        return False  # Already ran today
    h, m = parse_time(task.get("time", "09:00"))
    scheduled = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if now < scheduled:
        return False
    # Run only within 14-min window after scheduled (scheduler runs every 15 min)
    if now - scheduled > timedelta(minutes=14):
        return False
    return True


def is_due_weekly(task: dict, now: datetime, last_run: str) -> bool:
    """Check if weekly task is due."""
    if task.get("schedule") != "weekly":
        return False
    if last_run and last_run.startswith(now.strftime("%Y-%m-%d")):
        return False
    day_str = task.get("day", "monday").lower()
    try:
        target_weekday = WEEKDAYS.index(day_str)
    except ValueError:
        target_weekday = 0
    if now.weekday() != target_weekday:
        return False
    h, m = parse_time(task.get("time", "10:00"))
    scheduled = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if now < scheduled:
        return False
    if now - scheduled > timedelta(minutes=14):
        return False
    return True


def is_due_cron(task: dict, now: datetime, last_run: str) -> bool:
    """Check if cron task is due. Supports min hour day month dow (5 fields)."""
    cron = task.get("cron", "")
    if not cron or task.get("schedule") != "cron":
        return False
    parts = cron.split()
    if len(parts) != 5:
        return False
    min_p, hour_p, day_p, month_p, dow_p = parts
    # Simple matching (no * step support for now)
    if min_p != "*" and int(min_p) != now.minute:
        return False
    if hour_p != "*" and int(hour_p) != now.hour:
        return False
    if day_p != "*" and int(day_p) != now.day:
        return False
    if month_p != "*" and int(month_p) != now.month:
        return False
    if dow_p != "*":
        # 0=Sunday, 1=Monday, ... in cron
        if int(dow_p) != (now.weekday() + 1) % 7:
            return False
    # Avoid duplicate run in same minute
    if last_run and last_run >= now.strftime("%Y-%m-%d %H:%M"):
        return False
    return True


def is_task_due(task: dict, now: datetime, state: dict, wake: bool = False) -> bool:
    """Check if task is due to run. wake=True skips 14-min window (run overdue tasks)."""
    if not task.get("enabled", True):
        return False
    task_id = task.get("id", "")
    last_run = state.get(task_id, "")
    if wake:
        if task.get("schedule") == "daily":
            if last_run and last_run.startswith(now.strftime("%Y-%m-%d")):
                return False
            h, m = parse_time(task.get("time", "09:00"))
            scheduled = now.replace(hour=h, minute=m, second=0, microsecond=0)
            return now >= scheduled
        if task.get("schedule") == "weekly":
            if last_run and last_run.startswith(now.strftime("%Y-%m-%d")):
                return False
            day_str = task.get("day", "monday").lower()
            try:
                target_weekday = WEEKDAYS.index(day_str)
            except ValueError:
                target_weekday = 0
            if now.weekday() != target_weekday:
                return False
            h, m = parse_time(task.get("time", "10:00"))
            scheduled = now.replace(hour=h, minute=m, second=0, microsecond=0)
            return now >= scheduled
        if task.get("schedule") == "cron":
            return is_due_cron(task, now, last_run)
    if task.get("schedule") == "daily":
        return is_due_daily(task, now, last_run)
    if task.get("schedule") == "weekly":
        return is_due_weekly(task, now, last_run)
    if task.get("schedule") == "cron":
        return is_due_cron(task, now, last_run)
    return False


def run_task(task: dict) -> bool:
    """Execute a task. Returns True if success."""
    target = task.get("target", "")
    target_type = task.get("target_type", "skill")
    task_id = task.get("id", "unknown")

    if target_type == "pipeline":
        cmd = ["python3", str(VAULT_ROOT / "_scripts" / "pipeline.py"), "--run", target]
    else:
        skills_json = VAULT_ROOT / ".claude" / "skills.json"
        if not skills_json.exists():
            print("  Error: skills.json not found")
            return False
        skills = json.loads(skills_json.read_text(encoding="utf-8")).get("skills", {})
        if target not in skills:
            print(f"  Error: Skill '{target}' not found")
            return False
        cmds = skills[target].get("commands", [])
        if not cmds:
            print(f"  Error: Skill '{target}' has no commands")
            return False
        cmd = cmds[0].split()

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"scheduler_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    try:
        with open(log_file, "w", encoding="utf-8") as lf:
            proc = subprocess.run(
                cmd,
                cwd=str(VAULT_ROOT),
                stdout=lf,
                stderr=subprocess.STDOUT,
                text=True,
            )
        return proc.returncode == 0
    except Exception as e:
        with open(log_file, "w", encoding="utf-8") as lf:
            lf.write(str(e))
        return False


def cmd_add(args) -> int:
    """Add a scheduled task."""
    data = load_schedule()
    tasks = data.get("tasks", [])

    task_id = args.id or args.target.replace("-", "_")
    if any(t["id"] == task_id for t in tasks):
        print(f"Error: Task '{task_id}' already exists. Use --remove first.")
        return 1

    task = {
        "id": task_id,
        "target": args.target,
        "target_type": "pipeline" if args.pipeline else "skill",
        "schedule": args.schedule,
        "enabled": True,
    }
    if args.schedule == "daily":
        task["time"] = args.time or "09:00"
    elif args.schedule == "weekly":
        task["day"] = (args.day or "monday").lower()
        task["time"] = args.time or "10:00"
    elif args.schedule == "cron":
        task["cron"] = args.cron or "0 9 * * *"  # 9am daily

    tasks.append(task)
    data["tasks"] = tasks
    save_schedule(data)
    print(f"Added task: {task_id} ({args.target} @ {args.schedule})")
    return 0


def cmd_list(args) -> int:
    """List scheduled tasks."""
    data = load_schedule()
    tasks = data.get("tasks", [])
    state = load_state()

    if not tasks:
        print("No scheduled tasks. Add with: scheduler add <target> --schedule daily")
        return 0

    print("Scheduled Tasks")
    print("=" * 60)
    for t in tasks:
        en = "✓" if t.get("enabled", True) else "✗"
        sched = t.get("schedule", "?")
        if sched == "daily":
            sched_str = f"daily @ {t.get('time', '09:00')}"
        elif sched == "weekly":
            sched_str = f"{t.get('day', 'monday')} @ {t.get('time', '10:00')}"
        elif sched == "cron":
            sched_str = t.get("cron", "")
        else:
            sched_str = sched
        last = state.get(t["id"], "never")
        print(f"  {en} {t['id']:<25} {t['target']:<20} {sched_str:<25} last: {last}")
    return 0


def cmd_remove(args) -> int:
    """Remove a scheduled task."""
    data = load_schedule()
    tasks = [t for t in data.get("tasks", []) if t["id"] != args.id]
    if len(tasks) == len(data.get("tasks", [])):
        print(f"Error: Task '{args.id}' not found")
        return 1
    data["tasks"] = tasks
    save_schedule(data)
    print(f"Removed task: {args.id}")
    return 0


def run_notify(title: str, message: str) -> None:
    """Send macOS notification if available."""
    try:
        subprocess.run(
            [sys.executable, str(VAULT_ROOT / "_scripts" / "notify.py"), title, message],
            cwd=str(VAULT_ROOT),
            capture_output=True,
            timeout=5,
        )
    except Exception:
        pass


def cmd_run(args) -> int:
    """Check schedule and run due tasks."""
    data = load_schedule()
    tasks = data.get("tasks", [])
    state = load_state()
    now = datetime.now()
    wake = getattr(args, "wake", False)

    due = [t for t in tasks if is_task_due(t, now, state, wake=wake)]
    if not due:
        if args.verbose:
            print("No tasks due at this time.")
        return 0

    print(f"Running {len(due)} due task(s)...")
    success_count = 0
    for task in due:
        task_id = task["id"]
        print(f"  Running: {task_id} ({task['target']})...")
        success = run_task(task)
        state[task_id] = now.strftime("%Y-%m-%d %H:%M:%S")
        save_state(state)
        if success:
            success_count += 1
        print(f"    {'✓' if success else '✗'} Done")

    if getattr(args, "notify", False):
        run_notify("Scheduler", f"{success_count}/{len(due)} tasks completed")

    return 0


def cmd_install(args) -> int:
    """Generate launchd plist for macOS (run scheduler every 15 min)."""
    if platform.system() != "Darwin":
        print("Install only supported on macOS (launchd). Use cron on Linux.")
        return 1

    script_path = VAULT_ROOT / "_scripts" / "scheduler.py"
    logs_dir = str(LOGS_DIR)
    with_notify = not getattr(args, "no_notify", False)
    plist_array = ["/usr/bin/python3", str(script_path), "run"]
    if with_notify:
        plist_array.extend(["--notify"])
    array_lines = "\n".join(f'        <string>{a}</string>' for a in plist_array)
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.pai.scheduler</string>
    <key>ProgramArguments</key>
    <array>
{array_lines}
    </array>
    <key>StartInterval</key>
    <integer>900</integer>
    <key>WorkingDirectory</key>
    <string>{VAULT_ROOT}</string>
    <key>StandardOutPath</key>
    <string>{logs_dir}/scheduler_launchd.log</string>
    <key>StandardErrorPath</key>
    <string>{logs_dir}/scheduler_launchd_err.log</string>
</dict>
</plist>
"""

    plist_path = CONFIG_DIR / "com.pai.scheduler.plist"
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    plist_path.write_text(plist_content, encoding="utf-8")

    print(f"Generated: {plist_path}")
    print()
    print("To install and start the scheduler:")
    print("  cp _config/com.pai.scheduler.plist ~/Library/LaunchAgents/")
    print("  launchctl load ~/Library/LaunchAgents/com.pai.scheduler.plist")
    print()
    print("To stop:")
    print("  launchctl unload ~/Library/LaunchAgents/com.pai.scheduler.plist")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Scheduler - Automate and schedule tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scheduler add org-daily --schedule daily --time 09:00
  scheduler add weekly-synthesis --schedule weekly --day monday --time 10:00
  scheduler add ai-brief --schedule cron --cron "0 8 * * 1-5"
  scheduler list
  scheduler remove daily-curation
  scheduler run
  scheduler install
""",
    )
    sub = parser.add_subparsers(dest="cmd", help="Command")

    # add
    p_add = sub.add_parser("add", help="Add a scheduled task")
    p_add.add_argument("target", help="Skill or pipeline name")
    p_add.add_argument("--id", help="Task ID (default: from target)")
    p_add.add_argument("--pipeline", action="store_true", help="Target is a pipeline name")
    p_add.add_argument("--schedule", choices=["daily", "weekly", "cron"], default="daily")
    p_add.add_argument("--time", default="09:00", help="Time HH:MM (daily/weekly)")
    p_add.add_argument("--day", default="monday", help="Weekday (weekly)")
    p_add.add_argument("--cron", help="Cron expression (cron schedule)")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = sub.add_parser("list", help="List scheduled tasks")
    p_list.set_defaults(func=cmd_list)

    # remove
    p_remove = sub.add_parser("remove", help="Remove a task")
    p_remove.add_argument("id", help="Task ID")
    p_remove.set_defaults(func=cmd_remove)

    # run
    p_run = sub.add_parser("run", help="Check and run due tasks (called by launchd)")
    p_run.add_argument("-v", "--verbose", action="store_true")
    p_run.add_argument("--wake", action="store_true", help="Run overdue tasks (skip 14-min window)")
    p_run.add_argument("--notify", action="store_true", help="Send macOS notification when done")
    p_run.add_argument("--background", action="store_true", help="Run in background")
    p_run.set_defaults(func=cmd_run)

    # wake (alias for run --wake)
    p_wake = sub.add_parser("wake", help="Run overdue tasks now (same as run --wake)")
    p_wake.add_argument("-v", "--verbose", action="store_true")
    p_wake.add_argument("--notify", action="store_true", help="Send macOS notification when done")
    p_wake.set_defaults(func=cmd_run, wake=True)

    # install
    p_install = sub.add_parser("install", help="Install launchd plist (macOS)")
    p_install.add_argument("--no-notify", action="store_true", help="Don't add --notify to plist")
    p_install.set_defaults(func=cmd_install)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 0

    # Background mode: spawn and return
    if args.cmd == "run" and getattr(args, "background", False):
        import os
        cmd = [sys.executable, str(Path(__file__).resolve())]
        cmd.extend(["run", "-v"])
        if getattr(args, "wake", False):
            cmd.append("--wake")
        if getattr(args, "notify", False):
            cmd.append("--notify")
        if os.name != "nt":
            subprocess.Popen(cmd, cwd=str(VAULT_ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        else:
            subprocess.Popen(cmd, cwd=str(VAULT_ROOT), creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        print("Scheduler running in background.")
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
