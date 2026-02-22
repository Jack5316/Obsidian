# Obsidian Vault Usage Manual

## Overview

This manual provides a comprehensive guide to using your AI-powered Obsidian vault effectively. The vault is equipped with automated scripts, MCP (Model Context Protocol) integration, and specialized agents to enhance productivity and knowledge management.

## Table of Contents

1. [Vault Structure](#vault-structure)
2. [Automated Scripts](#automated-scripts)
3. [MCP Configuration](#mcp-configuration)
4. [Skills & Agent System](#skills--agent-system)
5. [Ralph Loop Plugin](#ralph-loop-plugin)
6. [Daily Workflow](#daily-workflow)
7. [Troubleshooting](#troubleshooting)

## Vault Structure

Your vault follows a well-organized structure based on the PARA method:

- **00 - Inbox**: Quick capture for new ideas and unprocessed content
- **01 - Projects**: Active projects with specific goals and deadlines
- **02 - Areas**: Ongoing areas of responsibility (e.g., work, health, finance)
- **03 - Resources**: Reference materials (books, articles, templates)
- **04 - Archive**: Completed or inactive items
- **Atlas**: Maps of content and connections
- **Extras**: Additional resources
- **Home.md**: Main dashboard and entry point
- **Maps**: Visual maps and diagrams
- **Sources**: External content sources (websites, articles, videos)
- **Templates**: Obsidian templates for note creation

Special directories:
- **_scripts**: Contains automation scripts (Python-based)
- **_logs**: Log files for script execution
- **.claude**: Claude Code configuration files
- **.obsidian**: Obsidian vault settings

## Obsidian Plugins

Your vault has two key community plugins installed:

### 1. Dataview

**Purpose**: Provides advanced query capabilities for your notes using JavaScript or SQL-like syntax.

**Key Features**:
- Query notes based on metadata, tags, and content
- Create dynamic tables and lists
- Filter and sort notes programmatically
- Display related content based on connections

**Usage Example**:
```dataview
TABLE file.ctime AS "Created", file.mtime AS "Modified"
FROM "01 - Projects"
WHERE contains(tags, "#urgent")
SORT file.mtime DESC
```

### 2. Templater

**Purpose**: Automates note creation with customizable templates.

**Key Features**:
- Create templates with variables and functions
- Insert dynamic content (date, time, file names)
- Automate repetitive note structures
- Use JavaScript to enhance templates

**Sample Template**:
```markdown
---
created: <% tp.date.now("YYYY-MM-DD HH:mm:ss") %>
tags: <% tp.file.cursor() %>
---

# <% tp.file.title %>

## Summary

## Key Points

## Action Items

## References
```

**Plugins Directory**:
- **dataview**: Dataview plugin files
- **templater-obsidian**: Templater plugin files

## Templates

Your vault includes a comprehensive set of templates for various note types, located in the `Templates` directory:

| Template | Purpose |
|----------|---------|
| AI Paper Review.md | Review and summarize AI research papers |
| ArXiv Digest.md | Summarize arXiv papers |
| Bilibili Summary.md | Bilibili video summaries |
| Blog Draft.md | Blog post drafts |
| Book Notes.md | Book notes and highlights |
| Daily Note.md | Daily journaling template |
| Experiment Log.md | Experiment documentation |
| Fleeting Note.md | Quick capture for ideas |
| HN Newsletter.md | Hacker News newsletter format |
| Insight.md | AI-generated insights |
| Literature Note.md | Academic literature notes |
| Meeting Note.md | Meeting notes and action items |
| MOC Template.md | Map of Content template |
| PDF Summary.md | PDF document summaries |
| Permanent Note.md | Evergreen notes |
| Project Note.md | Project documentation |
| Prompt Template.md | AI prompt engineering |
| Reddit Digest.md | Reddit content summaries |
| Self Reflection.md | Self-reflection and journaling |
| Self-Evolution Analysis.md | System improvement analysis |
| Self-Evolution Cycle.md | Personal growth cycle tracking |
| Tool Review.md | Tool and software reviews |
| Twitter Digest.md | Twitter content summaries |
| Weekly Review.md | Weekly planning and review |
| Weekly Synthesis.md | Weekly content synthesis |
| YouTube Summary.md | YouTube video summaries |

**Usage**: Templates are used by both manual note creation and automated scripts to maintain consistency.

## Automated Scripts

The `_scripts` directory contains Python scripts for automating various tasks:

### Script Overview

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
| `twitter_capture.py` | Captures and summarizes Twitter content from accounts in `twitter_accounts.txt` |
| `weekly_synthesis.py` | Synthesizes weekly notes and insights |
| `youtube_summary.py` | Summarizes YouTube videos |

### Running Scripts

To run a script:

1. Open a terminal in `/Users/jack/Documents/Obsidian/AI_Vault`
2. Run: `python3 _scripts/[script_name.py]`

**Example**: `python3 _scripts/arxiv_digest.py`

### Dependencies

All scripts require Python 3. Dependencies are listed in `_scripts/requirements.txt`.

To install dependencies:
```bash
pip install -r _scripts/requirements.txt
```

### Configuration Files

- **arxiv_topics.txt**: List of arXiv topic keywords
- **subreddits.txt**: List of Reddit subreddits to monitor
- **twitter_accounts.txt**: List of Twitter accounts to follow
- **config.py**: General script configuration

## MCP Configuration

Your vault uses MCP (Model Context Protocol) to integrate with Claude Code. Configuration is stored in:

### Settings File

`.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch(domain:docs.bearblog.dev)",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:grizzlygazette.bearblog.dev)",
      "Bash(pip install:*)",
      "Bash(python3 -m pip install:*)",
      "Bash(python3:*)",
      "WebFetch(domain:www.volcengine.com)",
      "Bash(chmod:*)"
    ]
  }
}
```

This configuration:
- Allows web search functionality
- Permits web fetching from specific domains
- Allows Python package installation and execution
- Permits file permission changes

### Environment Variables

`.env` file contains:
- `ARK_API_KEY`: API key for Claude Code
- `BEARBLOG_USER`: BearBlog username
- `BEARBLOG_PASSWORD`: BearBlog password

## Skills & Agent System

The vault supports two types of agents:

### Specialized Agents

1. **Bash**: Command execution specialist
2. **general-purpose**: Research and multi-step task handling
3. **statusline-setup**: Status line configuration
4. **Explore**: Codebase exploration
5. **Plan**: Software architecture design
6. **claude-code-guide**: Claude Code usage guidance

### Agent Usage

To launch an agent, use the `/agent` slash command in Claude Code with the appropriate subagent type.

Examples:
- `/agent Explore quick` to explore the vault structure
- `/agent Plan` to design implementation plans

## Ralph Loop Plugin

The Ralph Loop plugin is an AI-powered task automation tool.

### Available Commands

- `/ralph-loop` or `/rl`: Start Ralph Loop
- `/cancel-ralph`: Cancel active Ralph Loop
- `/ralph-loop:help`: Show Ralph Loop help

### Starting Ralph Loop

1. Open Claude Code in your vault
2. Type `/ralph-loop` and press Enter
3. Follow the prompts to define your loop parameters
4. The AI will automatically process tasks based on your instructions

### Example Use Cases

- Summarize all new articles in your Sources folder
- Process and organize book notes
- Generate weekly synthesis reports
- Analyze and improve your note system

## Daily Workflow

### Morning Routine

1. Open Obsidian and check the Home.md dashboard
2. Review Inbox for unprocessed items
3. Run relevant scripts:
   - `arxiv_digest.py` to get latest research
   - `hn_newsletter.py` for tech news
   - `reddit_digest.py` for community updates
4. Process new content and organize into appropriate folders

### During the Day

1. Use quick capture for ideas in Inbox
2. Take notes in relevant project/area folders
3. Use agents to enhance notes:
   - `/agent Explore` to find related content
   - `/agent Plan` to structure complex notes

### Evening Routine

1. Run `self_reflection.py` to review the day
2. Process any remaining Inbox items
3. Run `weekly_synthesis.py` if it's Friday
4. Archive completed items

## Troubleshooting

### Script Execution Issues

1. **Dependencies not installed**: Run `pip install -r _scripts/requirements.txt`
2. **API key errors**: Check ARK_API_KEY in `.env`
3. **Permission errors**: Ensure scripts are executable (`chmod +x _scripts/*.py`)
4. **Python version issues**: Use Python 3.8+

### Agent Problems

1. **Agent won't start**: Ensure Claude Code is properly configured
2. **Permission errors**: Check `.claude/settings.local.json`
3. **API rate limiting**: Reduce script execution frequency

### Ralph Loop Issues

1. **Loop won't start**: Check if another loop is active
2. **Execution errors**: Review log files in `_logs` directory
3. **Performance issues**: Reduce loop scope or frequency

## Tips for Effective Use

1. **Regular Maintenance**: Run scripts daily to keep content fresh
2. **Batch Processing**: Use Ralph Loop to automate repetitive tasks
3. **Template Usage**: Leverage Obsidian templates for consistent note creation
4. **Link Building**: Create connections between related notes
5. **Backup**: Regularly back up your vault to prevent data loss
6. **Review**: Periodically review and update your PARA structure

## Resources

- [Obsidian Documentation](https://help.obsidian.md)
- [Claude Code Documentation](https://claude.ai/help/code)
- [Ralph Loop Plugin GitHub](https://github.com/your-repo/ralph-loop)

## Version History

- **v1.0**: Initial manual creation (2026-02-16)

---

*This manual is dynamically generated. Check back for updates as your vault evolves.*
