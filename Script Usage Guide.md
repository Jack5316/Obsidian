# Script Usage Guide

## Overview

This guide provides detailed instructions for using each automation script in your vault's `_scripts` directory. All scripts are Python-based and designed to integrate seamlessly with Obsidian.

## Prerequisites

1. **Python 3.8+**: Ensure Python is installed (check with `python3 --version`)
2. **Dependencies**: Install required packages:
   ```bash
   pip install -r _scripts/requirements.txt
   ```
3. **API Key**: ARK_API_KEY must be configured in the `.env` file

## Script Directory Structure

```
_scripts/
├── arxiv_digest.py         # ArXiv paper curation
├── arxiv_topics.txt        # ArXiv topic configuration
├── bearblog_publish.py     # BearBlog publishing
├── bilibili_summary.py     # Bilibili video summarization
├── book_notes.py           # Book notes management
├── config.py               # Shared configuration
├── hn_newsletter.py        # Hacker News newsletter
├── insight_enhancement.py  # AI insight generation
├── pdf_summarize.py        # PDF document summarization
├── reddit_digest.py        # Reddit content digestion
├── requirements.txt        # Python dependencies
├── self_evolution.py       # System self-improvement
├── self_reflection.py      # Self-reflection system
├── subreddits.txt          # Reddit subreddit configuration
├── twitter_accounts.txt    # Twitter account configuration
├── twitter_capture.py      # Twitter content capture
├── tophub_news.py         # TopHub news scraping
├── tophub_skill.py        # TopHub news scraper skill
├── weekly_synthesis.py     # Weekly content synthesis
└── youtube_summary.py      # YouTube video summarization
```

---

## Detailed Script Documentation

### 1. arxiv_digest.py - ArXiv Paper Curation

**Purpose**: Curates and summarizes recent ArXiv papers based on topics.

**Usage**:
```bash
# Basic usage
python3 _scripts/arxiv_digest.py

# Custom parameters
python3 _scripts/arxiv_digest.py --days 14 --max 15 --topics "machine learning" "computer vision"
```

**Options**:
- `--days N`: Look back N days (default: 7)
- `--max N`: Maximum papers per topic (default: 10)
- `--topics TOPIC1 TOPIC2`: Override default topics

**Configuration**:
- Default topics in `arxiv_topics.txt`
- Output saved to: `Sources/ArXiv Digest - YYYY-MM-DD.md`

### 2. bearblog_publish.py - BearBlog Publishing

**Purpose**: Publishes notes to your BearBlog.

**Usage**:
```bash
python3 _scripts/bearblog_publish.py [note_path]
```

**Configuration**:
- BearBlog credentials in `.env`:
  - BEARBLOG_USER
  - BEARBLOG_PASSWORD

### 3. bilibili_summary.py - Bilibili Video Summarization

**Purpose**: Summarizes Bilibili videos with AI.

**Usage**:
```bash
python3 _scripts/bilibili_summary.py [bilibili_url]
```

### 4. book_notes.py - Book Notes Management

**Purpose**: Generates book notes from AI knowledge or Kindle clippings.

**Usage**:
```bash
# From book title
python3 _scripts/book_notes.py title "The Lean Startup" --author "Eric Ries"

# From Kindle clippings
python3 _scripts/book_notes.py kindle "path/to/My Clippings.txt" --book "Sapiens"
```

**Output**: Saved to `Sources/Book - [Title].md`

### 5. hn_newsletter.py - Hacker News Newsletter

**Purpose**: Creates a curated newsletter from Hacker News.

**Usage**:
```bash
python3 _scripts/hn_newsletter.py
```

### 6. insight_enhancement.py - AI Insight Generation

**Purpose**: Enhances existing notes with AI-generated insights.

**Usage**:
```bash
python3 _scripts/insight_enhancement.py [note_path]
```

### 7. pdf_summarize.py - PDF Document Summarization

**Purpose**: Summarizes PDF documents.

**Usage**:
```bash
python3 _scripts/pdf_summarize.py [pdf_path]
```

### 8. reddit_digest.py - Reddit Content Digestion

**Purpose**: Creates Reddit summaries from configured subreddits.

**Usage**:
```bash
python3 _scripts/reddit_digest.py
```

**Configuration**:
- Subreddits in `subreddits.txt`

### 9. self_evolution.py - System Self-Improvement

**Purpose**: Analyzes and improves your note system.

**Usage**:
```bash
python3 _scripts/self_evolution.py
```

### 10. self_reflection.py - Self-Reflection System

**Purpose**: Generates self-reflection prompts and analysis.

**Usage**:
```bash
python3 _scripts/self_reflection.py
```

### 11. twitter_capture.py - Twitter Content Capture

**Purpose**: Captures and summarizes Twitter content.

**Usage**:
```bash
python3 _scripts/twitter_capture.py
```

**Configuration**:
- Twitter accounts in `twitter_accounts.txt`

### 12. weekly_synthesis.py - Weekly Content Synthesis

**Purpose**: Synthesizes weekly notes and insights.

**Usage**:
```bash
python3 _scripts/weekly_synthesis.py
```

### 13. tophub_news_simple.py - Simple TopHub News Scraping

**Purpose**: Simple and reliable scraper for tophub.today's main page with AI-generated English summaries.

**Usage**:
```bash
# Basic usage - scrape 30 news items
python3 _scripts/tophub_news_simple.py

# Limit number of news items
python3 _scripts/tophub_news_simple.py --count 5
```

**Features**:
- Focuses on the main page for reliability
- Handles anti-scraping measures
- Generates AI summaries with English translations and Obsidian wikilinks
- Better error handling and retry logic

**Output**: Saved to `Sources/News Digest - Comprehensive - YYYY-MM-DD.md`

### 14. tophub_news_simple_skill.py - Simple TopHub News Scraper Skill

**Purpose**: Skill wrapper for running tophub_news_simple.py from Claude Code.

**Usage**:
```bash
/skill tophub-news-simple              # Scrape 30 news items (default)
/skill tophub-news-simple --count 15   # Scrape 15 news items
```

### 15. tophub_news_detailed.py - Detailed TopHub News Scraper

**Purpose**: Advanced scraper that follows links to specific news sections and extracts real headlines.

**Usage**:
```bash
# Basic usage - scrape 5 news items per section
python3 _scripts/tophub_news_detailed.py

# Limit number of news items per section
python3 _scripts/tophub_news_detailed.py --count 2
```

**Features**:
- Scrapes real news from popular Chinese platforms
- Follows links to specific news sections
- Extracts actual news headlines from each section
- Handles anti-scraping measures
- Generates detailed AI summaries
- Better error handling and retry logic

**Sections Scraped**:
- Weibo Hot Search (微博热搜榜)
- WeChat 24h Hot Articles (微信24h热文榜)
- Baidu Real-Time Hotspots (百度实时热点)
- Bilibili Site-Wide Daily Rankings (哔哩哔哩全站日榜)
- 36Kr 24h Hot News (36氪24小时热榜)

**Output**: Saved to `Sources/News Digest - Comprehensive - YYYY-MM-DD.md`

### 16. tophub_news_detailed_skill.py - Detailed TopHub News Scraper Skill

**Purpose**: Skill wrapper for running tophub_news_detailed.py from Claude Code.

**Usage**:
```bash
/skill tophub-news-detailed              # Scrape 5 news items per section (default)
/skill tophub-news-detailed --count 10   # Scrape 10 news items per section
```

### 15. youtube_summary.py - YouTube Video Summarization

**Purpose**: Summarizes YouTube videos with AI.

**Usage**:
```bash
python3 _scripts/youtube_summary.py [youtube_url]
```

---

## Shared Configuration (config.py)

### API Configuration

```python
# AI client (Volcengine Ark, OpenAI-compatible)
DEFAULT_MODEL = "ark-code-latest"
ARK_API_KEY = os.getenv("ARK_API_KEY")

# Save note function
def save_note(relative_path: str, content: str) -> Path:
    """Save a note to the vault. Creates parent directories as needed."""
    ...

# Summarization function
def summarize(text: str, prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Send text to AI for summarization/processing."""
    ...

# Learning configuration
LEARNING_RATE = 0.1
ADAPTATION_THRESHOLD = 0.8
MAX_EVOLUTION_ITERATIONS = 100
```

### Common Output Directories

- **Sources/**: External content (ArXiv, books, videos, etc.)
- **_logs/**: Script execution logs

---

## Advanced Usage

### Batch Script Execution

Create a bash script for daily automation:

```bash
#!/bin/bash
VAULT_PATH="/Users/jack/Documents/Obsidian/AI_Vault"
cd "$VAULT_PATH"

# Daily scripts
python3 _scripts/arxiv_digest.py
python3 _scripts/hn_newsletter.py
python3 _scripts/reddit_digest.py

# Weekly scripts (run on Fridays)
if [ "$(date +%u)" -eq 5 ]; then
    python3 _scripts/weekly_synthesis.py
    python3 _scripts/self_reflection.py
fi

echo "Automation complete!"
```

### Customizing Topics & Sources

1. **ArXiv Topics**: Edit `_scripts/arxiv_topics.txt`
2. **Reddit Subreddits**: Edit `_scripts/subreddits.txt`
3. **Twitter Accounts**: Edit `_scripts/twitter_accounts.txt`

### Adding New Scripts

All scripts follow a standard pattern:

```python
from config import summarize, save_note, VAULT_PATH

def main():
    # Script logic
    ...
    save_note("Output/Path.md", content)

if __name__ == "__main__":
    main()
```

---

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Run `pip install -r _scripts/requirements.txt`
2. **API Key Errors**: Verify ARK_API_KEY in `.env`
3. **File Not Found**: Check relative paths and ensure files exist
4. **Permission Errors**: Make scripts executable (`chmod +x _scripts/*.py`)

### Log Files

Script execution logs are saved in the `_logs` directory. Check for errors:
```bash
cat _logs/[script_name].log
```

---

## Performance Optimization

1. **Limit API Calls**: Adjust `--max` and `--days` parameters
2. **Cache Results**: Some scripts cache results locally
3. **Batch Processing**: Run scripts during off-peak hours
4. **Parallel Execution**: Run independent scripts in parallel

---

## Updates & Maintenance

1. **Dependencies**: Regularly update with `pip install -r _scripts/requirements.txt --upgrade`
2. **Configuration**: Back up `.env` and configuration files
3. **Script Updates**: Review and update scripts for API changes

---

*Last updated: 2026-02-16*
