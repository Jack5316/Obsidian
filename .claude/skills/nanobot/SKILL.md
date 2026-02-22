---
name: nanobot
description: Leverage nanobot — ultra-lightweight personal AI assistant from HKUDS. Chat via nanobot agent, check status, start gateway, list skills. Use when user wants nanobot, /nanobot, or to interact with their nanobot assistant.
---

# Nanobot Skill (/nanobot)

Leverage [nanobot](https://github.com/HKUDS/nanobot) — the ultra-lightweight personal AI assistant (~4K lines of core code, 99% smaller than Clawdbot). Chat with your agent, check status, start the gateway, and integrate with your PAI vault.

## Quick Start

```bash
# Chat with nanobot
python3 _scripts/nanobot_skill.py chat "Summarize today's notes"

# Check status
python3 _scripts/nanobot_skill.py status

# Setup info
python3 _scripts/nanobot_skill.py info
```

## Features

1. **Chat** — Send messages to nanobot agent and get responses
2. **Status** — Check nanobot provider, config, and workspace
3. **Gateway** — Instructions to start Telegram/Discord/Feishu channels
4. **Info** — Setup guide and PAI integration instructions
5. **List Skills** — List PAI skills (same as org-list) that nanobot can run

## Commands

| Command | Description |
|---------|-------------|
| `chat MESSAGE` | Send message to nanobot agent |
| `status` | Show nanobot status |
| `gateway` | Start gateway (Telegram, Discord, etc.) |
| `info` | Setup and integration info |
| `list-skills` | List PAI skills |

## Options

- `--save`: Save chat response to `Sources/Nanobot Chat - YYYY-MM-DD.md`

## Examples

```bash
# Basic chat
python3 _scripts/nanobot_skill.py chat "What's in my vault? Run obsidian-vault analytics"

# Chat and save to vault
python3 _scripts/nanobot_skill.py chat "Summarize today's notes" --save

# Check nanobot status
python3 _scripts/nanobot_skill.py status

# How to start gateway
python3 _scripts/nanobot_skill.py gateway

# Setup and integration info
python3 _scripts/nanobot_skill.py info

# List PAI skills (nanobot can run these)
python3 _scripts/nanobot_skill.py list-skills
```

## Prerequisites

- **Install**: `uv tool install nanobot-ai` or `pip install nanobot-ai`
- **Config**: `~/.nanobot/config.json` (run `nanobot onboard` first)
- **Workspace**: Set to vault path for PAI skill indexing

See `_scripts/nanobot_setup.md` for full setup (Telegram, Discord, etc.).

## When to Use

- When you want to chat with nanobot from the CLI
- To check nanobot configuration and status
- To get gateway setup instructions
- When nanobot needs to run PAI skills (org-list, dictionary, etc.)

## PAI Integration

nanobot indexes all PAI skills from `.claude/skills/` when workspace = vault path. It can run skills via exec (e.g. `Run org-list`, `TIL: something`, `Look up serendipity in dictionary`).
