# Quick Reference Guide

## Script Usage

### Content Acquisition Scripts

```bash
# TopHub news scraping (simple, reliable)
python3 _scripts/tophub_news_simple.py         # Comprehensive news (30 items)
python3 _scripts/tophub_news_simple.py --count 5  # Limit to 5 items

# TopHub news scraping (detailed, section-specific)
python3 _scripts/tophub_news_detailed.py       # 5 news items per section (default)
python3 _scripts/tophub_news_detailed.py --count 3  # 3 news items per section

# Summarize arXiv papers
python3 _scripts/arxiv_digest.py

# Publish to BearBlog
python3 _scripts/bearblog_publish.py

# Summarize Bilibili videos
python3 _scripts/bilibili_summary.py

# Process book notes
python3 _scripts/book_notes.py

# Create Hacker News newsletter
python3 _scripts/hn_newsletter.py

# Enhance notes with insights
python3 _scripts/insight_enhancement.py

# Summarize PDF documents
python3 _scripts/pdf_summarize.py

# Reddit summary digest
python3 _scripts/reddit_digest.py

# Analyze and improve note system
python3 _scripts/self_evolution.py

# Self-reflection prompts
python3 _scripts/self_reflection.py

# Twitter content capture
python3 _scripts/twitter_capture.py

# Weekly content synthesis
python3 _scripts/weekly_synthesis.py

# YouTube video summaries
python3 _scripts/youtube_summary.py
```

## Core Dependencies

```bash
pip install -r _scripts/requirements.txt
```

## Claude Code Commands

### Slash Commands

```bash
/agent [agent_type]      # Launch specialized agent
/fast                    # Toggle fast mode
/help                    # Display help
/clear                   # Clear conversation history
```

### TopHub News Scraper Skills

```bash
# Simple scraper (main page only)
/skill tophub-news-simple              # Comprehensive news digest (30 items)
/skill tophub-news-simple --count 15   # Scrape 15 news items

# Detailed scraper (section-specific)
/skill tophub-news-detailed              # 5 news items per section (default)
/skill tophub-news-detailed --count 10   # Scrape 10 news items per section
```

### Ralph Loop Plugin

```bash
/ralph-loop              # Start Ralph Loop
/rl                      # Start Ralph Loop (shorthand)
/cancel-ralph            # Cancel active loop
/ralph-loop:help         # Show help
```

## Dataview Queries

### Basic Query

```dataview
TABLE file.ctime AS "Created", file.mtime AS "Modified"
FROM "01 - Projects"
WHERE contains(tags, "#urgent")
SORT file.mtime DESC
```

### List Links

```dataview
LIST
WHERE contains(file.outlinks, [[]])
```

### Metadata Summary

```dataview
TABLE status AS "Status", priority AS "Priority"
FROM "02 - Areas"
WHERE typeof(status) = "string"
```

## Templater Quick Tips

### Date & Time Variables

```markdown
<% tp.date.now("YYYY-MM-DD") %>          <!-- Current date -->
<% tp.date.now("HH:mm:ss") %>          <!-- Current time -->
<% tp.file.creation_date() %>          <!-- File creation date -->
<% tp.file.last_modified_date() %>     <!-- Last modified date -->
```

### File Properties

```markdown
<% tp.file.title %>                    <!-- Current file title -->
<% tp.file.folder() %>                 <!-- File directory -->
<% tp.file.filename() %>               <!-- Full filename -->
```

### System Information

```markdown
<% tp.system.user %>                   <!-- Current user -->
<% tp.system.hostname %>               <!-- Computer name -->
```

## Daily Workflow Checklist

- [ ] Check Home.md dashboard
- [ ] Process Inbox items
- [ ] Run daily scripts
- [ ] Create new notes from Templates
- [ ] Review and connect related notes
- [ ] Update project statuses
- [ ] Run weekly synthesis (Fridays)
- [ ] Archive completed items

## Keyboard Shortcuts

**Note**: Customize in Obsidian settings → Hotkeys

```
Cmd/Ctrl + N          New note
Cmd/Ctrl + O          Open quick switcher
Cmd/Ctrl + P          Command palette
Cmd/Ctrl + E          Edit mode
Cmd/Ctrl + Shift + E  Read mode
Cmd/Ctrl + B          Toggle sidebar
```

## Troubleshooting Quick Fixes

1. **Scripts won't run**: Check Python version (3.8+) and dependencies
2. **API errors**: Verify ARK_API_KEY in .env
3. **Plugin issues**: Reinstall plugins or restart Obsidian
4. **Sync issues**: Check Obsidian sync settings
5. **Performance**: Disable unused plugins, reduce backlinks

## Links to Manual Sections

- [Full Manual](Obsidian%20Vault%20Usage%20Manual.md)
- [Vault Structure](Obsidian%20Vault%20Usage%20Manual.md#vault-structure)
- [Automated Scripts](Obsidian%20Vault%20Usage%20Manual.md#automated-scripts)
- [MCP Configuration](Obsidian%20Vault%20Usage%20Manual.md#mcp-configuration)
- [Skills & Agents](Obsidian%20Vault%20Usage%20Manual.md#skills--agent-system)
- [Ralph Loop](Obsidian%20Vault%20Usage%20Manual.md#ralph-loop-plugin)
