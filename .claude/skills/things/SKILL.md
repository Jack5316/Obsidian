---
name: things
description: Add and manage actionable items in Things (macOS) via URL scheme. Add to-dos, projects, update tasks, show lists, search. Use when user asks to add tasks to Things, create to-dos, Things integration, or /things.
---

# Things Skill (/things)

Add and manage actionable items in Things 3 for Mac using the [Things URL Scheme](https://culturedcode.com/things/support/articles/2803573/).

## Quick Start

```bash
# Add a to-do (to Inbox by default)
python3 _scripts/things.py add "Buy milk"

# Add with when and tags
python3 _scripts/things.py add "Call dentist" --when tomorrow --tags Errand

# Add a project
python3 _scripts/things.py project "Vacation" --area Family --todos "Book flights" "Pack bags"

# Show Today
python3 _scripts/things.py show

# Search
python3 _scripts/things.py search "meeting"
```

## Commands

| Command | Description |
|---------|-------------|
| `add` | Add a to-do |
| `project` | Add a project with optional to-dos |
| `update` | Update existing to-do (requires auth token) |
| `show` | Show Today, Inbox, or a list |
| `search` | Search to-dos |

## Add Options

- `--when`, `-w` — today, tomorrow, evening, anytime, someday, or date (e.g. 2026-02-25, next monday)
- `--list`, `-l` — Project or area name
- `--notes`, `-n` — Notes
- `--tags`, `-t` — Comma-separated tags
- `--deadline`, `-d` — Deadline (yyyy-mm-dd or natural language)
- `--reveal` — Open and show the new to-do

## Update (requires auth token)

For `update`, you need `THINGS_AUTH_TOKEN` in `.env`. Get it from:
**Things → Settings → General → Things URLs → Manage**

```bash
# Update a to-do (get ID from Share → Copy Link)
python3 _scripts/things.py update <todo-id> --when today
python3 _scripts/things.py update <todo-id> --completed true
python3 _scripts/things.py update <todo-id> --append-notes "Done"
```

## Show List IDs

Built-in: `today`, `inbox`, `anytime`, `upcoming`, `someday`, `logbook`, `tomorrow`, `deadlines`

```bash
python3 _scripts/things.py show --id today
python3 _scripts/things.py show --query "Work"
```

## Configuration

Add to `.env`:
```
THINGS_AUTH_TOKEN=your_token
```

Required only for `update` command. Get token from Things → Settings → General → Things URLs → Manage.

## Examples

```bash
# Quick capture
python3 _scripts/things.py add "Review PR #42"

# Scheduled for evening
python3 _scripts/things.py add "Grocery run" --when evening --tags Errand

# With deadline
python3 _scripts/things.py add "Submit report" --list Work --deadline 2026-02-25

# Project with to-dos
python3 _scripts/things.py project "Q1 Planning" --area Work --todos "Set goals" "Review metrics" "Schedule review"
```

## Requirements

- macOS with Things 3 for Mac
- Things URLs enabled (Things → Settings → General)
