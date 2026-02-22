---
name: memory
description: Memory Consolidator - Persist information to LLM/Agent memory. Add preferences, facts, patterns, and workflows to your LLM Context folder for Kilo Code and AI assistants to remember permanently. Use when asked to remember something, save a preference, or store information for later.
---

# Memory Consolidator Skill (/memory)

Persist important information to your LLM Context folder, creating persistent memory for Kilo Code and other AI assistants.

## Quick Start

```bash
python3 _scripts/memory_consolidator.py --summary
```

## What It Does

1. **Preferences** - Store likes, dislikes, and interaction preferences
2. **Facts & Knowledge** - Persist factual information
3. **Patterns & Learnings** - Capture observed patterns
4. **Workflows** - Document processes and procedures
5. **Organization** - Everything stored in structured LLM Context/ folder

## Memory Categories

- **Preferences** - Likes, dislikes, interaction preferences
- **Facts & Knowledge** - Factual information
- **Workflows & Processes** - Step-by-step procedures
- **Patterns & Learnings** - Observed patterns
- **Project Context** - Project-specific information
- **Personal Profile** - About you
- **Writing Style** - Your voice and tone
- **Basic Rules** - Ground rules
- **Dynamic Activities** - Recent activities

## Options

- `--summary`: Show memory summary and statistics
- `--preference TEXT`: Add a preference (use with --desc)
- `--fact TEXT`: Add a fact (use with --source)
- `--pattern TEXT`: Add an observed pattern
- `--workflow TEXT`: Add a workflow (name,step1,step2,...)
- `--desc TEXT`: Description for preference/pattern
- `--source TEXT`: Source for fact
- `--list`: List all memory files
- `--category TEXT`: Filter by category when listing
- `--search TEXT`: Search memories containing text

## Examples

```bash
# Show memory summary
python3 _scripts/memory_consolidator.py --summary

# Add a preference
python3 _scripts/memory_consolidator.py --preference "I like concise answers" --desc "Prefer brevity over verbosity"

# Add a fact
python3 _scripts/memory_consolidator.py --fact "Python 3.11 is the latest stable version" --source "python.org"

# Add a pattern
python3 _scripts/memory_consolidator.py --pattern "I usually code in the morning" --desc "Most productive 9-12 AM"

# Add a workflow
python3 _scripts/memory_consolidator.py --workflow "Daily Review,Check email,Review tasks,Plan day"

# List all memories
python3 _scripts/memory_consolidator.py --list

# List only preferences
python3 _scripts/memory_consolidator.py --list --category "Preferences"

# Search memories
python3 _scripts/memory_consolidator.py --search "workflow"
```

## File Structure

```
LLM Context/
├── Preferences/          # User preferences
├── Facts & Knowledge/    # Factual information
├── Workflows & Processes/ # Step-by-step workflows
├── Patterns & Learnings/ # Observed patterns
├── Project Context/      # Project-specific info
├── Personal Profile/     # About you
├── Writing Style/        # Voice and tone
├── Basic Rules/          # Ground rules
└── Dynamic Activities/   # Recent activities
```

## Memory Format

Each memory file includes:
- YAML frontmatter with type, category, tags
- Title and content
- Creation timestamp
- Automatic tagging for discovery

## Why This Matters

- **Persistent Memory**: AI remembers across sessions
- **Consistent Interactions**: Preferences are always respected
- **Knowledge Base**: Build a personal knowledge graph
- **Context Awareness**: AI has better context about you
