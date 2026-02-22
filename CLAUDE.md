# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Personal AI Infrastructure (PAI)** — an implementation of Fan Bing's 5-Layer Pyramid framework for building a personal "Jarvis." It is not a collection of scripts; it is a loosely coupled, self-evolving system designed for one person's information sovereignty. The Obsidian vault is the data substrate; Python scripts are the skills; Claude Code is the CLI orchestrator.

## The 5-Layer Architecture

This vault maps directly to the PAI pyramid. Understanding this structure explains every design decision:

| Layer | Role | Implementation |
|-------|------|----------------|
| **L1 Dev Tools** | CLI-first interface | Claude Code + skills system |
| **L2 Data** | Local-first knowledge substrate | Obsidian vault (markdown, bidirectional links) |
| **L3 Skills** | Reusable workflow units | `_scripts/*.py` + `.claude/skills/` |
| **L4 Scenarios** | Automated daily tasks | Content curation, summarization, publishing |
| **L5 Review** | System watches itself | Daily/weekly/monthly reflection + self-evolution |

**Design principles from the framework:**
- **Scripts before prompts** — if a task can be codified as Python, don't burn tokens on it. Use AI only for judgment, creativity, and ambiguity.
- **Small File Philosophy** — each script does one thing well (single responsibility), is simple to understand, and gains power through composition.
- **Loose coupling** — each layer is independently optimizable and swappable. The skills layer doesn't care if the data layer moves from Obsidian to Logseq.
- **Context is the moat** — accumulated personal context (writing style, preferences, information diet) transforms a generic LLM into a personal assistant. Accumulate gradually.
- **Extract skills from repetition** — every time you solve a problem with AI twice, extract it into a reusable skill.

**Philosophical grounding (Miessler's Personal Panopticon):**
- **The tower belongs to you** — self-surveillance for empowerment, not control. Every piece of tracked data serves the user's agency.
- **Cross-domain synthesis is the superpower** — the highest-value insights come from noticing patterns across domains kept stubbornly separate. Daily scripts whisper cross-domain connections; weekly synthesis shouts them.
- **Productive illegibility** — not everything should be tracked. The system must periodically question its own metrics (Goodhart resistance). A metric that can be gamed will be — even by the system itself.
- **Activation energy, not ability** — the bottleneck is never capability but the friction to start. Every unnecessary step is a design failure.
- **Thought traces as recursive fuel** — all outputs (digests, syntheses, reflections) are inputs to future synthesis. The system's memory is its compounding advantage.

## Prerequisites

- **Python 3.8+** with dependencies: `pip install -r _scripts/requirements.txt`
- **ARK_API_KEY** in `.env` file (Volcengine Ark API — the sole AI backend)

## Skills (Claude Code Slash Commands)

```bash
# Orchestration
/skill org          # Run all automation + reflect
/skill org-daily    # Daily: ArXiv, HN, Reddit, news, Twitter
/skill org-weekly   # Weekly: synthesis + self-reflection
/skill org-list     # List available scripts
/skill org-status   # Check recent execution status
/skill org-logs     # View recent execution logs

# Content curation (L4 Scenarios)
/skill ai-brief     # Morning brew of AI news (ArXiv, HN, Reddit, skills.sh)
/skill arxiv        # ArXiv papers by topic
/skill hn           # Hacker News digest
/skill reddit       # Reddit digest
/skill news         # Chinese news from tophub.today
/skill twitter      # Twitter content
/skill bookmark     # Process saved URLs into structured notes
/skill cubox-rss    # Auto-sync RSS feeds to Cubox
/skill book         # Book notes (AI or Kindle clippings)
/skill movie        # Movie notes (review, quotes, cast, plot)
/skill person       # Person profiles (people you follow/study)
/skill project      # Track ongoing personal projects
/skill goal         # Track and review goals against daily/weekly logs
/skill habit        # Log and analyze behavioral patterns
/skill meeting      # Structure notes/action items from meeting conversations
/skill weekly       # Weekly cross-source synthesis
/skill daily-synthesis  # Daily cross-domain synthesis
/skill essay        # Long-form essay from accumulated insights
/skill concept      # Extract and define recurring concepts across reading
/skill connect      # Find relationships between notes, ideas, and concepts
/skill rag          # RAG query over vault (LightRAG-inspired: keyword + graph retrieval)
/skill filter       # Precision RAG search — exact, relevant passages only (reranking + chunk extraction)
/skill deep-research # Multi-step deep research (OpenAI/HKUDS inspired: vault + sources + steelman → report)
/skill debate       # Steelman opposing views on topics you're exploring
/skill flashcard    # Generate spaced repetition cards from content
/skill thread       # Convert insights into Twitter/X threads
/skill official-wechat-publisher  # Publish to 微信公众号 (format + clipboard/API)
/skill md2wechat  # Markdown → WeChat HTML with themes (bytedance, chinese, apple, etc.)
/skill skill-grab   # Collect latest best skills from skills.sh
/skill product-hunt # Best shiny new tools from Product Hunt
/skill api          # Find best databases and APIs for a subject
/skill til          # Today I Learned quick capture
/skill question     # Open questions for future research
/skill job-seeking  # Job digest from V2EX, RemoteOK (China job search)
/skill dictionary  # Longman Dictionary lookup (meaning, etymology, corpus)
/skill wiki        # Feynman-style wiki tutorial (learn anything)
/skill quotes      # Inspirational quotes by subject, author, or movie lines
/skill prompt      # Generate well-structured prompts, apply templates, orchestrate workflows
/skill alignment   # Update skills (strategic, reflective, purposeful, systematic)
/skill gateway     # Skill map + integration guide (FCLG: Functions, Connections, Limitations, Guidance)
/skill scheduler   # Automate & schedule tasks (launchd on macOS)
/skill things      # Add to-dos and projects to Things (macOS)
/skill notify      # macOS system notifications
/skill web-fetch   # Fetch URL → markdown
/skill web-search  # Web search (Brave API)
/skill nanobot     # Leverage nanobot — chat, status, gateway (HKUDS ultra-lightweight agent)

 # Self-improvement (L5 Review)
 /skill zen          # Grounding, presence, intentional focus
 /skill reflect      # Self-reflection report
 /skill evolve       # Self-evolution improvement cycle
 /skill insights     # Iterative insight enhancement
 /skill review       # Monthly/quarterly system review
 
 # Obsidian Integration (NEW)
 /skill obsidian-vault   # Vault analytics & health monitoring
 /skill obsidian-tasks   # Task management & tracking
 /skill obsidian-links   # Knowledge graph & link analysis
 /skill second-brain-audit  # Vault health + PARA check (full audit)
 /skill clean            # Find and remove redundant notes (with permission)
 /skill memory           # Memory consolidation for LLM/Agent
 ```

## Scripts Reference

### Orchestration
```bash
python3 _scripts/org_skill.py              # Run all daily scripts in parallel
python3 _scripts/org_skill.py --daily      # ArXiv, HN, Reddit, news, Twitter
python3 _scripts/org_skill.py --weekly     # Weekly synthesis + self-reflection
python3 _scripts/org_skill.py --list       # List available scripts
python3 _scripts/org_skill.py --status     # Check recent execution status
python3 _scripts/org_skill.py --logs       # View recent logs
```

### Content Curation (have skills)
```bash
python3 _scripts/arxiv_digest.py                              # ArXiv digest
python3 _scripts/hn_newsletter.py [--count N]                  # Hacker News (default 15)
python3 _scripts/reddit_digest.py                              # Reddit digest
python3 _scripts/tophub_news_simple.py                         # Chinese news (simple)
python3 _scripts/twitter_capture.py [--accounts @a @b] [--hours N]  # Twitter
python3 _scripts/bookmark_process.py [--file PATH] [--limit N] URL [URL...] # Process saved URLs
python3 _scripts/book_notes.py title "Book Title" [--author X] # Book notes from AI
python3 _scripts/book_notes.py kindle path/Clippings.txt [--book X] # From Kindle
python3 _scripts/movie_notes.py "Movie Title" [--year YYYY] [--notes "..."] # Movie notes
python3 _scripts/person_profile.py "Person Name" [--role X] [--notes "..."] # Person profiles
python3 _scripts/project_track.py create "Name" [--desc X] [--due YYYY-MM-DD] # Create project
python3 _scripts/project_track.py list [--all] # List projects
python3 _scripts/project_track.py log "Name" "entry" # Log to project
python3 _scripts/goal_track.py create "Goal" [--desc X] [--target "Q2 2026"] # Create goal
python3 _scripts/goal_track.py list [--all] # List goals
python3 _scripts/goal_track.py log "Goal" "entry" # Log to goal
python3 _scripts/goal_track.py review [--days N] [--no-save] # Review goals vs daily/weekly synthesis
python3 _scripts/habit_track.py create "Habit" [--desc X] # Create habit
python3 _scripts/habit_track.py list [--all] # List habits
python3 _scripts/habit_track.py log "Habit" [note] # Log habit check-in
python3 _scripts/habit_track.py analyze [--days N] [--no-synthesis] [--no-save] # Analyze behavioral patterns
python3 _scripts/meeting_notes.py PATH [--title X] [--output PATH] # Structure meeting notes
python3 _scripts/weekly_synthesis.py                           # Weekly synthesis
python3 _scripts/daily_synthesis.py                            # Daily cross-domain synthesis
python3 _scripts/essay.py [--topic X] [--days N]               # Long-form essay from insights
python3 _scripts/debate_steelman.py "topic" [--from-path PATH]   # Steelman opposing views
python3 _scripts/concept_extract.py [--topic X] [--days N]     # Extract recurring concepts
python3 _scripts/flashcard_generate.py [PATH] [--topic X] [--deck D] [--anki]  # Spaced repetition cards
python3 _scripts/thread_from_insights.py [--topic X] [--tweets N]  # Twitter/X thread from insights
python3 _scripts/skill_grab.py [-s trending|hot|all] [--no-ai] # Skills.sh digest
python3 _scripts/til_capture.py "learning" [--note]             # TIL quick capture
python3 _scripts/question_capture.py "question" [--note]       # Open question capture
python3 _scripts/dictionary.py WORD [--save]                    # Longman Dictionary lookup
python3 _scripts/wiki.py "TOPIC" [--save]                      # Feynman-style wiki tutorial
python3 _scripts/quotes.py "TOPIC" [--author X] [--movie-lines] [--save]  # Inspirational quotes
python3 _scripts/gateway.py [--skill X] [--integrate NAME "desc"] [--save]  # Skill map & integration
python3 _scripts/scheduler.py add|list|remove|run|install                  # Schedule tasks
python3 _scripts/things.py add|project|update|show|search                   # Things (macOS)
python3 _scripts/notify.py "Title" "Message"                                # macOS notification
python3 _scripts/web_fetch.py URL [--save]                                 # URL → markdown
python3 _scripts/web_search.py "query" [--save]                            # Web search (Brave)
```

### Standalone Scripts (no skill — run directly)
```bash
python3 _scripts/youtube_summary.py VIDEO_URL_OR_ID            # YouTube summary
python3 _scripts/bilibili_summary.py VIDEO_URL_OR_BV [-v]      # Bilibili summary
python3 _scripts/pdf_summarize.py PATH.pdf [--title X]         # PDF summary
python3 _scripts/bearblog_publish.py NOTE_PATH [--draft]       # Publish to BearBlog
python3 _scripts/wechat_official_publish.py NOTE_PATH [--save] # Publish to 微信公众号 (format + clipboard)
python3 _scripts/tophub_news_detailed.py [-c N]                # Detailed news (sections)
python3 _scripts/tophub_news.py [-s SECTION] [-n N]            # News (legacy)
```

### Self-Improvement (have skills)
```bash
python3 _scripts/self_reflection.py reflect [--days N] [--save]       # Reflect
python3 _scripts/self_reflection.py analyze [--days N]                # Analyze behavior
python3 _scripts/self_reflection.py improve [--days N] [--apply]      # Improvement plan
python3 _scripts/self_evolution.py cycle [--iteration N] [--safe]     # Single evolution
python3 _scripts/self_evolution.py continuous [--iterations N] [--safe] # Continuous
python3 _scripts/self_evolution.py analyze [--iterations N] [--report]  # History
python3 _scripts/insight_enhancement.py                               # Insight cycle
python3 _scripts/review_system.py [--monthly|--quarterly] [--save]    # Monthly/quarterly review
```

## Architecture

### AI Backend

All AI processing uses **Volcengine Ark** (OpenAI-compatible API) configured in `_scripts/config.py`:
- Endpoint: `https://ark.cn-beijing.volces.com/api/coding/v1`
- Model: `ark-code-latest`
- Client: OpenAI SDK with custom base_url

### Shared Utilities (`_scripts/config.py`)

Every script imports from `config.py`:
- `summarize(text, prompt, model)` — sends text to AI with a system prompt
- `save_note(relative_path, content)` — writes to vault with auto-directory creation
- `VAULT_PATH` — resolved vault root (parent of `_scripts/`)
- `TRACKER` — optional `SystemBehaviorTracker` instance for performance logging

### Common Script Pattern (L3 Skills)

All content scripts follow the same structure — the **dual strategy** of Python (low cost, deterministic) + AI (high quality, judgment):

1. Import `summarize`, `save_note`, `VAULT_PATH` from config
2. Define a content-specific `PROMPT` constant for AI context
3. **Python**: Fetch and filter data (API call, scrape, or parse local file)
4. **AI**: Process through `summarize(content, PROMPT)` — only for judgment/synthesis
5. Output via `save_note("Sources/[Type] - YYYY-MM-DD.md", result)`
6. CLI interface via `argparse` with `if __name__ == "__main__"`
7. **Cross-domain awareness**: each prompt includes a lightweight hint to flag connections to other domains. The AI can ignore these if nothing crosses domains — the instruction is permissive, not mandatory.

To add a new content source, follow this pattern. See `arxiv_digest.py` or `reddit_digest.py` as reference implementations.

### How to Create a New Skill (Step-by-Step)

When creating a new skill, follow this complete workflow:

#### 1. Create the Python Script (`_scripts/my_new_skill.py`)

```python
"""My New Skill - Brief description of what this skill does.

Explain the purpose and key features here.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


def main():
    """Main function for the skill."""
    parser = argparse.ArgumentParser(
        description="My New Skill - Brief description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill my-new-skill                    # Basic usage
  /skill my-new-skill --option value    # With options
  /skill my-new-skill --save            # Save output
"""
    )
    
    parser.add_argument(
        "--option",
        type=str,
        help="Description of option"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to vault"
    )
    
    args = parser.parse_args()
    
    # Your skill logic here
    result = "Skill output content..."
    
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_note(f"Sources/My New Skill - {date_str}.md", result)
    
    print(result)


if __name__ == "__main__":
    main()
```

#### 2. Create the Skill Definition (`.claude/skills/my-new-skill/SKILL.md`)

```markdown
---
name: my-new-skill
description: Brief description of what this skill does. Use when user asks for X, Y, or Z.
---

# My New Skill (/my-new-skill)

Brief description of the skill.

## Quick Start

```bash
python3 _scripts/my_new_skill.py
```

## Features

1. **Feature 1** - Description
2. **Feature 2** - Description
3. **Feature 3** - Description

## Options

- `--option TEXT`: Description of option
- `--save`: Save output to vault

## Examples

```bash
# Basic usage
python3 _scripts/my_new_skill.py

# With options
python3 _scripts/my_new_skill.py --option value

# Save output
python3 _scripts/my_new_skill.py --save
```

## Output

- **Terminal**: Markdown or text output
- **Saved note**: `Sources/My New Skill - YYYY-MM-DD.md`
```

#### 3. Register in `skills.json`

Add to `.claude/skills.json`:

```json
{
  "skills": {
    "my-new-skill": {
      "description": "Brief description of what this skill does. Use when user asks for X, Y, or Z.",
      "commands": [
        "python3 _scripts/my_new_skill.py"
      ]
    }
  }
}
```

#### 4. Follow These Conventions

✅ **Naming:**
- Skill name: hyphenated (`my-new-skill`)
- Script name: snake_case (`my_new_skill.py`)
- Folder name: hyphenated (`my-new-skill/`)

✅ **Documentation:**
- Always include docstring at top of Python file
- Always create SKILL.md with examples
- Add usage examples to argparse epilog

✅ **Output:**
- Save to `Sources/` with dated filename: `Skill Name - YYYY-MM-DD.md`
- Use `save_note()` from config.py
- Print to terminal for immediate feedback

✅ **Configuration:**
- Import from `config.py` (don't hardcode paths)
- Use `VAULT_PATH` for file operations
- Store API keys in `.env` (never commit!)

### Skill Creation Checklist

Before considering a skill complete:

- [ ] Python script created in `_scripts/`
- [ ] Script uses `argparse` with helpful examples
- [ ] Script imports from `config.py`
- [ ] SKILL.md created in `.claude/skills/<skill-name>/`
- [ ] Added to `.claude/skills.json`
- [ ] Tested (runs without errors)
- [ ] Saves output to appropriate location (`Sources/`, `Atlas/`, etc.)
- [ ] Uses YAML frontmatter if appropriate (for memory files)
- [ ] Follows "scripts before prompts" principle (Python for deterministic tasks, AI only for judgment)

### Reference Implementations

Study these existing skills as patterns:

- **Content Curation**: `arxiv_digest.py`, `reddit_digest.py`
- **Task/Management**: `project_track.py`, `goal_track.py`
- **Self-Improvement**: `self_reflection.py`, `insight_enhancement.py`
- **Obsidian Integration**: `obsidian_vault_analytics.py`, `memory_consolidator.py`

### Orchestration (`_scripts/org_skill.py`)

Runs multiple scripts in parallel using `ThreadPoolExecutor`. Individual script failures don't stop others. Generates timestamped logs in `_logs/org_skill_*.log`.

### Review Layer (L5)

Three scripts form the self-improvement feedback loop, matching the PAI review cadence:

- `self_reflection.py` — analyzes system behavior and effectiveness via `SystemBehaviorTracker`
- `self_evolution.py` — generates and tracks improvement suggestions (SEAI framework) with rollback plans
- `insight_enhancement.py` — manages an insight repository (`_logs/insights_repo.json`) with lifecycle: discovered → planned → implemented → verified

**Review cadence:** Daily (aggregate summaries, check health), Weekly (adjust sources, filter noise, Goodhart check), Monthly (optimize system, upgrade skills). The weekly synthesis includes a **Goodhart resistance** audit — the system explicitly questions whether its own metrics still serve curiosity rather than habit.

### Publishing (`_scripts/bearblog_publish.py`)

Publishes vault notes to BearBlog. Post template structure: TL;DR → Hook → Main Point → Supporting idea → Takeaway. Uses credentials from `.env` (`BEARBLOG_USER`, `BEARBLOG_PASSWORD`).

### Output Conventions

- Most generated notes go to `Sources/` with dated filenames (e.g., `Sources/ArXiv Digest - 2026-02-18.md`)
- Essays go to `Atlas/` (e.g., `Atlas/Essay - topic.md`) — long-form distillations are permanent notes
- Content organized by **theme/topic**, not by source
- Uses `[[wikilinks]]` for Obsidian interconnection
- No YAML frontmatter in generated output

### Input Configuration

- `_scripts/arxiv_topics.txt` — ArXiv search keywords (one per line)
- `_scripts/subreddits.txt` — Reddit subreddits to monitor
- `_scripts/twitter_accounts.txt` — Twitter accounts to follow

### Vault Structure (L2 Data)

Uses a modified PARA method:
- `00-04 Inbox/Projects/Areas/Resources/Archive` — knowledge management
- `Maps/` — Map of Content (MOC) semantic hubs
- `Atlas/` — permanent notes
- `Sources/` — script-generated content
- `Templates/` — 28 Obsidian note templates

## Logs and Debugging

- `_logs/org_skill_YYYYMMDD_HHMMSS.log` — script execution history
- `_logs/reflection_log.json` — self-reflection performance tracking
- `_logs/evolution_log.json` — self-evolution iteration history
- `_logs/insights_repo.json` — insight lifecycle tracking
