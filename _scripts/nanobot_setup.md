# Nanobot Setup

[nanobot](https://github.com/HKUDS/nanobot) — Ultra-lightweight personal AI assistant (~4K lines of core code) inspired by OpenClaw.

## Setup

Configured for your PAI vault:

- **Installed**: `uv tool install nanobot-ai`
- **Config**: `~/.nanobot/config.json`
- **Workspace**: `/Users/jack/Documents/Obsidian/AI_Vault` (your vault)
- **Tools**: Sandboxed to vault (`restrictToWorkspace: true`)
- **MCP**: Filesystem server for vault access
- **Provider**: Volcengine Ark Coding Plan (`api/coding/v3`)

## Usage

```bash
# Terminal chat
nanobot agent

# Single message
nanobot agent -m "Summarize today's notes"

# Show status
nanobot status
```

## Chat Channels

Enable Telegram, Discord, Feishu, etc. in `~/.nanobot/config.json` under `channels`. After editing, run:

```bash
nanobot gateway   # Start gateway
nanobot channels status   # Check channel status
```

### Supported Channels

| Channel | Config key | Required fields | Notes |
|---------|------------|-----------------|-------|
| **Telegram** | `telegram` | `token` (from @BotFather) | Easiest for personal use |
| **Discord** | `discord` | `token` (Bot token + MESSAGE CONTENT intent) | DMs and server channels |
| **WhatsApp** | `whatsapp` | `bridgeUrl`, `bridgeToken` | Needs local Node.js bridge |
| **Feishu** | `feishu` | `appId`, `appSecret`, `encryptKey`, `verificationToken` | WebSocket long connection |
| **Slack** | `slack` | `botToken`, `appToken` | Socket Mode |
| **DingTalk** | `dingtalk` | `clientId`, `clientSecret` | Stream mode |
| **Email** | `email` | IMAP + SMTP credentials | IMAP poll + SMTP reply |
| **QQ** | `qq` | `appId`, `secret` | Private message (C2C) |

### Telegram (recommended for personal use)

1. Open @BotFather in Telegram → `/newbot` → copy token
2. (Optional) Get your user ID via @userinfobot for access control
3. Edit `~/.nanobot/config.json`:

```json
"channels": {
  "telegram": {
    "enabled": true,
    "token": "YOUR_BOT_TOKEN",
    "allowFrom": []   // empty = allow all; or ["123456789"] for your user ID
  }
}
```

### Discord

1. [discord.com/developers/applications](https://discord.com/developers/applications) → New Application → Bot → Add Bot
2. Enable **MESSAGE CONTENT INTENT** in Bot settings
3. Copy bot token
4. Edit config:

```json
"channels": {
  "discord": {
    "enabled": true,
    "token": "YOUR_BOT_TOKEN",
    "allowFrom": []   // or ["YOUR_DISCORD_USER_ID"]
  }
}
```

### Access Control (`allowFrom`)

- **Empty `[]`**: Allow everyone (use only for local/testing)
- **Non-empty list**: Only listed user IDs/usernames can interact

## Ark Coding Plan Models

Current default: `doubao-seed-code`. To switch model, edit `agents.defaults.model` in `~/.nanobot/config.json`:

| Model | Config value |
|-------|--------------|
| doubao-seed-code | `openai/doubao-seed-code` |
| kimi-k2.5 | `openai/kimi-k2.5` |
| glm-4.7 | `openai/glm-4.7` |
| deepseek-v3.2 | `openai/deepseek-v3.2` |
| doubao-seed-2.0-code | `openai/doubao-seed-2.0-code` |

## Optional: Web Search

Add `BRAVE_API_KEY` to `tools.web.search.apiKey` in config for web search.

## PAI Skills Indexing

nanobot loads skills from `workspace/skills/`. This vault uses `.claude/skills/` (Claude Code format). A symlink connects them:

```bash
# Already done — vault/skills -> .claude/skills
# nanobot indexes all 97 PAI skills when workspace = vault path
```

If the symlink is missing: `ln -s .claude/skills skills` from vault root.

## List Skills — Direct Workaround

The agent tends to summarize instead of pasting raw output. For the full skill list, run directly:

```bash
python3 _scripts/org_skill.py --list
# or
bash _scripts/nanobot_list_skills.sh
```
