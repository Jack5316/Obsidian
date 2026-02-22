---
name: scheduler
description: Automate and schedule tasks (skills/pipelines) to run automatically. Uses launchd on macOS. Use when user asks to schedule tasks, automate execution, run skills automatically, cron, or /scheduler.
---

# Scheduler Skill (/scheduler)

Schedule skills and pipelines to run automatically. Uses launchd on macOS (runs every 15 min to check due tasks).

## Quick Start

```bash
# List scheduled tasks
python3 _scripts/scheduler.py list

# Add a daily task (9am)
python3 _scripts/scheduler.py add org-daily --schedule daily --time 09:00

# Add a weekly task (Monday 10am)
python3 _scripts/scheduler.py add org-weekly --schedule weekly --day monday --time 10:00

# Install launchd (generate plist, then copy & load)
python3 _scripts/scheduler.py install
```

## Commands

| Command | Description |
|---------|-------------|
| `add <target>` | Add a scheduled task |
| `list` | List all scheduled tasks |
| `remove <id>` | Remove a task by ID |
| `run` | Check and run due tasks (called by launchd) |
| `wake` | Run overdue tasks now (skip 14-min window) |
| `install` | Generate launchd plist for macOS |

## Schedule Types

| Type | Options | Example |
|------|---------|---------|
| **daily** | `--time HH:MM` | 9am every day |
| **weekly** | `--day monday` `--time HH:MM` | Monday 10am |
| **cron** | `--cron "min hour day month dow"` | `0 8 * * 1-5` (8am Mon–Fri) |

## Add Options

- `--id` — Task ID (default: from target)
- `--pipeline` — Target is a pipeline name (e.g., daily-curation)
- `--schedule` — daily | weekly | cron
- `--time` — HH:MM for daily/weekly
- `--day` — Weekday for weekly (monday, tuesday, ...)
- `--cron` — Cron expression for cron schedule

## Examples

```bash
# Daily curation at 9am
python3 _scripts/scheduler.py add org-daily --schedule daily --time 09:00

# AI brief at 8am weekdays (using pipeline)
python3 _scripts/scheduler.py add ai-brief --schedule daily --time 08:00

# Weekly synthesis Monday 10am
python3 _scripts/scheduler.py add org-weekly --schedule weekly --day monday --time 10:00

# Second brain audit every Sunday 6pm
python3 _scripts/scheduler.py add second-brain-audit --schedule weekly --day sunday --time 18:00

# Cron: 8am Mon–Fri (0 8 * * 1-5)
python3 _scripts/scheduler.py add ai-brief --schedule cron --cron "0 8 * * 1-5"

# Run overdue tasks now
python3 _scripts/scheduler.py wake
python3 _scripts/scheduler.py wake --notify

# Run in background
python3 _scripts/scheduler.py run --background --notify

# Remove a task
python3 _scripts/scheduler.py remove daily-curation

# Install (macOS)
python3 _scripts/scheduler.py install
# Then: cp _config/com.pai.scheduler.plist ~/Library/LaunchAgents/
#       launchctl load ~/Library/LaunchAgents/com.pai.scheduler.plist
```

## Config & State

- **Config**: `_config/schedule.json` — Task definitions
- **State**: `_config/schedule_state.json` — Last run times
- **Logs**: `_logs/scheduler_{task_id}_{timestamp}.log`

## Default Tasks

On first run, creates:
- `daily-curation` — org-daily @ 9am
- `weekly-synthesis` — org-weekly @ Monday 10am

## Output

- **list**: Table of tasks with schedule and last run
- **install**: Generates `_config/com.pai.scheduler.plist` + copy/load instructions
