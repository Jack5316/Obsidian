# AI Vault Automation Scripts

## Overview

This directory contains Python scripts for automating various tasks in your AI-powered Obsidian vault.

## Script List

| Script | Description |
|--------|-------------|
| `arxiv_digest.py` | Summarizes arXiv papers based on topics in `arxiv_topics.txt` |
| `bearblog_publish.py` | Publishes notes to your BearBlog |
| `bilibili_summary.py` | Summarizes Bilibili videos |
| `book_notes.py` | Processes and organizes book notes |
| `config.py` | Configuration file for scripts |
| `hn_newsletter.py` | Creates a newsletter from Hacker News |
| `insight_enhancement.py` | Enhances notes with AI-generated insights |
| `pdf_summarize.py` | Summarizes PDF documents |
| `reddit_digest.py` | Creates Reddit summaries from subreddits in `subreddits.txt` |
| `self_evolution.py` | Analyzes and improves your note system |
| `self_reflection.py` | Generates self-reflection prompts and analysis |
| `tophub_news_simple.py` | Simple and reliable scraper for tophub.today's main page with AI English summaries |
| `tophub_news_simple_skill.py` | Skill wrapper for tophub_news_simple.py |
| `tophub_news_detailed.py` | Detailed scraper that follows links to specific news sections on tophub.today |
| `tophub_news_detailed_skill.py` | Skill wrapper for tophub_news_detailed.py
| `twitter_capture.py` | Captures and summarizes Twitter content from accounts in `twitter_accounts.txt` |
| `weekly_synthesis.py` | Synthesizes weekly notes and insights |
| `youtube_summary.py` | Summarizes YouTube videos |

## Prerequisites

1. Python 3.8+
2. Required packages: `pip install -r requirements.txt`
3. API key: ARK_API_KEY in `.env` file

## Usage

### Running Scripts

```bash
# Basic usage
python3 script_name.py

# With parameters
python3 arxiv_digest.py --days 14 --max 15
python3 book_notes.py title "The Lean Startup" --author "Eric Ries"
python3 youtube_summary.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Configuration Files

- **arxiv_topics.txt**: List of arXiv topic keywords
- **subreddits.txt**: List of Reddit subreddits to monitor
- **twitter_accounts.txt**: List of Twitter accounts to follow
- **config.py**: General script configuration

## Output Directories

- **Sources/**: External content (ArXiv, books, videos, etc.)
- **_logs/**: Script execution logs

## Advanced Usage

### Batch Execution

Create a bash script for daily automation:

```bash
#!/bin/bash
cd /Users/jack/Documents/Obsidian/AI_Vault

python3 _scripts/arxiv_digest.py
python3 _scripts/hn_newsletter.py
python3 _scripts/reddit_digest.py

if [ "$(date +%u)" -eq 5 ]; then
    python3 _scripts/weekly_synthesis.py
    python3 _scripts/self_reflection.py
fi

echo "Automation complete!"
```

### Customization

1. **Add new topics**: Edit `arxiv_topics.txt`
2. **Add new subreddits**: Edit `subreddits.txt`
3. **Add new Twitter accounts**: Edit `twitter_accounts.txt`
4. **Modify learning parameters**: Edit `config.py`

## Troubleshooting

- **Permissions**: `chmod +x *.py`
- **Dependencies**: `pip install -r requirements.txt`
- **Logs**: Check `_logs/` directory for errors

---

*For detailed documentation, see the [Script Usage Guide](../Script%20Usage%20Guide.md)*
