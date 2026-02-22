---
name: curl
description: Information curation skill - gather, filter, organize, and synthesize information from multiple sources in your Obsidian vault. Use when you want to collect information on a topic, build reading lists, organize knowledge, or synthesize what you've learned.
---

# Curl Skill (/curl)

Facilitates information curation - gathering, filtering, organizing, and synthesizing information from multiple sources in your Obsidian vault. Named after the command-line tool, but for knowledge curation. Inspired by Tiago Forte's Second Brain principles of capturing and organizing information.

## Quick Start

```bash
python3 _scripts/curl.py "AI" --tags ai machine-learning
```

## What It Does

1. **Information Gathering** - Collect files from multiple vault locations
2. **Smart Filtering** - Filter by tags, dates, keywords, or content types
3. **Thematic Organization** - Group information into meaningful collections
4. **Reading Lists** - Create annotated, prioritized reading lists
5. **Synthesis** - Connect and synthesize curated information
6. **Knowledge Repositories** - Build comprehensive personal knowledge bases

## Features

### Core Modes

- **Gather** - Just collect and list relevant files
- **Organize** - Group into thematic collections
- **Reading List** - Create annotated reading lists with priorities
- **Synthesize** - Connect ideas across sources into a coherent whole
- **Repository** - Full knowledge repository (organize + reading list + synthesis)

### Search & Filter Options

- **Tags** - Search by hashtags in content
- **Keywords** - Search by keyword matches
- **Date Range** - Recent files from last N days
- **Directories** - Limit to specific folders
- **Specific Paths** - Explicitly include files
- **Directory Search** - Everything within a specific folder

### Curation Principles Applied

- **Quality over quantity** - Curate the most valuable information
- **Context preservation** - Maintain source attribution and context
- **Thematic organization** - Group by meaning and purpose
- **Progressive summarization** - Distill layers of insight
- **Connection making** - Synthesize across sources

## Options

- `topic`: Topic for curation (required)
- `--tags LIST`: Search by tags (multiple allowed)
- `--keywords LIST`: Search by keywords (multiple allowed)
- `--days N`: Search files from last N days
- `--directories LIST`: Directories to search (multiple allowed)
- `--paths LIST`: Specific file paths (multiple allowed)
- `--directory DIR`: Specific directory to search exclusively
- `--gather`: Just gather and list files
- `--organize`: Organize by theme
- `--reading-list`: Create annotated reading list
- `--synthesize`: Synthesize curated information
- `--repository`: Build full knowledge repository
- `--save`: Save output to Sources folder

## Examples

```bash
# Gather files by tags
python3 _scripts/curl.py "AI topics" --tags ai machine-learning

# Gather recent files and organize thematically
python3 _scripts/curl.py "recent learning" --days 7 --organize

# Search by keywords and synthesize
python3 _scripts/curl.py "neural networks" --keywords "neural" "network" --synthesize

# Create reading list from specific files
python3 _scripts/curl.py "reading" --paths "Sources/Article1.md" "Sources/Article2.md" --reading-list

# Build complete repository from a project folder
python3 _scripts/curl.py "My Project" --directory "01 - Projects/MyProject" --repository

# Combine multiple filters and save
python3 _scripts/curl.py "cognitive science" --tags cognition neuroscience --days 14 --synthesize --save
```

## How It Works

### The Curation Pipeline

1. **Gather** - Collect files from multiple sources using filters
2. **Filter** - Apply search criteria to find relevant content
3. **Organize** - Group by themes and emerging patterns
4. **Synthesize** - Connect ideas and extract insights
5. **Preserve** - Save curation with source context

### Second Brain Principles

- **Capture** - Collect what resonates
- **Organize** - For actionability, not just categorization
- **Distill** - Progressive summarization layers
- **Express** - Turn curated knowledge into creative output

## Output

- **Terminal**: Formatted markdown with your curation session
- **Saved note**: `Sources/Curl - [topic] - YYYY-MM-DD.md`

## When to Use

Use /curl when:
- You want to collect everything you know about a topic
- You need to organize scattered information into themes
- You want to build a reading list from your vault
- You need to synthesize what you've learned
- You're building a personal knowledge repository
- You want to see connections between different sources
- You're preparing for research or writing

## Pairing with Other Skills

- **/diverge** - Use before /curl to explore what to look for
- **/converge** - Use after /curl to prioritize curated content
- **/gradient** - Use to iteratively refine your curation
- **/random-walk** - Use to discover serendipitous content to curate
- **/memory** - Save important curation insights for future reference
