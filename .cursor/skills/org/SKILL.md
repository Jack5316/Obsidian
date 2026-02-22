---
name: org
description: Run all automation scripts in this Obsidian vault. Use when the user asks to organize the vault, run scripts, execute automation, or run /org.
---

# Organization Skill

Runs all automation scripts in parallel and reflects on the process. Use sub-skills for daily/weekly subsets.

## Quick Start

Execute from vault root:

```bash
python3 _scripts/org_skill.py
```

## Sub-Commands

| Command | Purpose |
|---------|---------|
| `--list` | List all available scripts |
| `--daily` | ArXiv, HN, Reddit, news, Twitter |
| `--weekly` | Weekly synthesis |
| `--status` | Check execution status and recent runs |
| `--logs` | View most recent execution log |
| `--skip s1,s2` | Skip specific scripts |
| `-v, --verbose` | Stream output (runs sequentially) |

## Scripts Executed (default)

- arxiv_digest.py, hn_newsletter.py, reddit_digest.py, tophub_news_simple.py, twitter_capture.py
- weekly_synthesis.py

## Output

- Log: `_logs/org_skill_YYYYMMDD_HHMMSS.log`
- Notes: `Sources/[Type] - YYYY-MM-DD.md`
