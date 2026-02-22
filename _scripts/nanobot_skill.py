#!/usr/bin/env python3
"""Leverage nanobot — ultra-lightweight personal AI assistant from HKUDS.

nanobot (https://github.com/HKUDS/nanobot) is ~4K lines of core agent code,
inspired by OpenClaw. This skill wraps the nanobot CLI to chat, check status,
and integrate with your PAI vault.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import save_note, VAULT_PATH


def run_nanobot(args: list[str], timeout: int = 120) -> tuple[int, str]:
    """Run nanobot CLI and return (exit_code, output)."""
    try:
        result = subprocess.run(
            ["nanobot"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(VAULT_PATH),
        )
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        combined = f"{out}\n{err}".strip() if err else out
        return result.returncode, combined
    except FileNotFoundError:
        return 1, (
            "nanobot not found. Install with:\n"
            "  uv tool install nanobot-ai   # or: pip install nanobot-ai\n"
            "Then run: nanobot onboard"
        )
    except subprocess.TimeoutExpired:
        return 1, f"nanobot timed out after {timeout}s"


def cmd_chat(message: str, save: bool = False) -> str:
    """Send a message to nanobot agent and return the response."""
    code, out = run_nanobot(["agent", "-m", message])
    if code != 0:
        return f"Error (exit {code}):\n{out}"
    if save and out:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_note(f"Sources/Nanobot Chat - {date_str}.md", f"# Nanobot Chat\n\n**Q:** {message}\n\n**A:**\n\n{out}")
    return out


def cmd_status() -> str:
    """Show nanobot status (providers, config, workspace)."""
    code, out = run_nanobot(["status"])
    if code != 0:
        return f"Error (exit {code}):\n{out}"
    return out


def cmd_gateway() -> str:
    """Start nanobot gateway (Telegram, Discord, etc.). Runs in foreground."""
    return (
        "To start the gateway (connects Telegram, Discord, etc.), run in a separate terminal:\n\n"
        "  nanobot gateway\n\n"
        "Or run in background:\n  nohup nanobot gateway > _logs/nanobot_gateway.log 2>&1 &\n\n"
        "Check channel status: nanobot channels status"
    )


def cmd_info() -> str:
    """Show nanobot setup and integration info."""
    return """# nanobot — Ultra-Lightweight Personal AI Assistant

**Repo:** https://github.com/HKUDS/nanobot (~4K lines, 99% smaller than Clawdbot)

## Install

```bash
uv tool install nanobot-ai   # or: pip install nanobot-ai
nanobot onboard
```

## Config

- **Config:** `~/.nanobot/config.json`
- **Workspace:** Set to your vault path for PAI skill indexing
- **Tools:** `restrictToWorkspace: true` sandboxes file access to vault

## Commands

| Command | Description |
|---------|-------------|
| `nanobot agent` | Interactive chat |
| `nanobot agent -m "msg"` | Single message |
| `nanobot status` | Show status |
| `nanobot gateway` | Start chat channels (Telegram, Discord, etc.) |
| `nanobot channels status` | Channel status |
| `nanobot cron add --name X --message "Y" --cron "0 9 * * *"` | Scheduled tasks |

## PAI Integration

This vault's `.claude/skills/` are indexed by nanobot when workspace = vault path.
nanobot can run PAI skills via exec (e.g. org-list, dictionary, TIL).

See `_scripts/nanobot_setup.md` for full setup.
"""


def cmd_list_skills() -> str:
    """List PAI skills (via org_skill.py — nanobot uses same skills)."""
    script = VAULT_PATH / "_scripts" / "org_skill.py"
    if not script.exists():
        return "org_skill.py not found"
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--list"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(VAULT_PATH),
        )
        return (result.stdout or result.stderr or "").strip() or "No output"
    except subprocess.TimeoutExpired:
        return "Timed out"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Leverage nanobot — ultra-lightweight personal AI assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/nanobot_skill.py chat "Summarize today's notes"
  python3 _scripts/nanobot_skill.py chat "Run org-list" --save
  python3 _scripts/nanobot_skill.py status
  python3 _scripts/nanobot_skill.py gateway
  python3 _scripts/nanobot_skill.py info
  python3 _scripts/nanobot_skill.py list-skills
""",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # chat
    p_chat = sub.add_parser("chat", help="Send message to nanobot agent")
    p_chat.add_argument("message", nargs="+", help="Message to send")
    p_chat.add_argument("--save", action="store_true", help="Save response to Sources/")

    # status
    sub.add_parser("status", help="Show nanobot status")

    # gateway
    sub.add_parser("gateway", help="Instructions to start nanobot gateway")

    # info
    sub.add_parser("info", help="Setup and integration info")

    # list-skills
    sub.add_parser("list-skills", help="List PAI skills (same as org-list)")

    args = parser.parse_args()

    if args.cmd == "chat":
        msg = " ".join(args.message)
        out = cmd_chat(msg, save=args.save)
    elif args.cmd == "status":
        out = cmd_status()
    elif args.cmd == "gateway":
        out = cmd_gateway()
    elif args.cmd == "info":
        out = cmd_info()
    elif args.cmd == "list-skills":
        out = cmd_list_skills()
    else:
        out = "Unknown command"

    print(out)


if __name__ == "__main__":
    main()
