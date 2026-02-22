# Obsidian CLI Integration Guide

This document describes the new Obsidian CLI integration skills and how to use them to enhance your personal AI infrastructure.

## 📋 Overview

We've created a powerful integration with Obsidian CLI that provides:

1. **Obsidian CLI Integration Module** - A Python wrapper for the Obsidian CLI
2. **Vault Analytics Skill** - Comprehensive vault statistics and health monitoring
3. **Task Manager Skill** - Advanced task management and tracking
4. **Link Analyzer Skill** - Knowledge graph and link structure analysis

---

## 🔧 Core Module: `obsidian_cli.py`

The integration module provides a Pythonic interface to Obsidian CLI commands.

### Key Features

- File operations (create, read, update, delete)
- Vault information and statistics
- Search and query capabilities
- Link and relationship analysis
- Tag and property management
- Task management
- Daily note integration
- Plugin and theme management

### Usage Example

```python
from _scripts.obsidian_cli import get_cli

# Get CLI instance
cli = get_cli()

# List files
files = cli.list_files(ext="md")

# Read a file
content = cli.read_file(path="Home.md")

# Get tasks
tasks = cli.list_tasks(todo=True)

# Get backlinks
backlinks = cli.get_backlinks(path="Some Note.md")
```

---

## 📊 Skill 1: Vault Analytics (`obsidian_vault_analytics.py`)

Comprehensive analysis of your Obsidian vault.

### Features

- **File Statistics**: Count, types, folder structure
- **Tag Analysis**: Usage patterns and distributions
- **Link Health**: Orphan files, dead-ends, unresolved links
- **Task Statistics**: Completion rates and trends
- **Property Analysis**: Metadata usage
- **Health Score**: Overall vault health assessment

### Usage

```bash
# Full analytics report
/skill obsidian-vault-analytics

# Output in JSON
/skill obsidian-vault-analytics --json

# Save report to vault
/skill obsidian-vault-analytics --save
```

### What It Measures

- **File Health**: Markdown ratio and organization
- **Link Health**: Connectivity and graph structure
- **Task Health**: Completion rates
- **Activity Health**: Recent usage patterns

---

## ✅ Skill 2: Task Manager (`obsidian_task_manager.py`)

Advanced task management using Obsidian's native task system.

### Features

- **Task Listing**: Filter by status (todo, done, in-progress)
- **Priority Tracking**: 🔴 High, 🟡 Medium, 🟢 Low priority
- **Tag Analysis**: Tasks organized by tags
- **Daily Integration**: Add tasks directly to daily notes
- **Search**: Find tasks by keywords
- **Statistics**: Completion rates and trends

### Usage

```bash
# Full task report
/skill obsidian-task-manager

# Show only todo tasks
/skill obsidian-task-manager --todo

# Show completed tasks
/skill obsidian-task-manager --done

# Show daily tasks
/skill obsidian-task-manager --daily

# Show high-priority tasks
/skill obsidian-task-manager --priority

# Search tasks
/skill obsidian-task-manager --search "project"

# Add task to daily note
/skill obsidian-task-manager --add "Finish the project"

# Save report
/skill obsidian-task-manager --save
```

### Task Formatting

The task manager recognizes:

- Priority markers: 🔴 P1, 🟡 P2, 🟢 P3
- Status: `- [ ]` todo, `- [x]` done, `- [/]` in-progress
- Tags: #tagname within task content

---

## 🔗 Skill 3: Link Analyzer (`obsidian_link_analyzer.py`)

Comprehensive knowledge graph and link structure analysis.

### Features

- **Orphan Detection**: Files with no incoming links
- **Dead-end Identification**: Files with no outgoing links
- **Unresolved Links**: Broken links to non-existent files
- **Central Hubs**: Most connected files (MOCs)
- **Connectivity Score**: Overall graph health
- **Recommendations**: Actionable improvements

### Usage

```bash
# Full link health report
/skill obsidian-link-analyzer

# Show only orphan files
/skill obsidian-link-analyzer --orphans

# Show only dead-end files
/skill obsidian-link-analyzer --deadends

# Show central hub files
/skill obsidian-link-analyzer --hubs

# Analyze specific file
/skill obsidian-link-analyzer --file "Note.md"

# Save report
/skill obsidian-link-analyzer --save
```

### Health Score Calculation

The link health score (0-100) is calculated based on:

- -50% penalty per percentage of orphan files
- -30% penalty per percentage of dead-end files
- -2 points per unresolved link (max 20 points)

---

## 🚀 Integration with Existing Skills

These new skills complement your existing automation:

### Workflow Example

```bash
# 1. Morning: Check tasks and add new ones
/skill obsidian-task-manager --todo
/skill obsidian-task-manager --add "Review yesterday's notes"

# 2. Mid-day: Check vault health
/skill obsidian-vault-analytics --save

# 3. End of day: Review links and knowledge graph
/skill obsidian-link-analyzer --orphans

# 4. Weekly: Full analysis with org_skill
/skill org
```

### Combining with `org_skill.py`

Add the new skills to your organization workflow by modifying `_scripts/org_skill.py` to include:

- `obsidian_vault_analytics.py`
- `obsidian_task_manager.py`
- `obsidian_link_analyzer.py`

---

## 📁 File Structure

```
_scripts/
├── obsidian_cli.py              # Core integration module
├── obsidian_vault_analytics.py  # Vault analytics skill
├── obsidian_task_manager.py     # Task management skill
└── obsidian_link_analyzer.py    # Link analysis skill

Sources/
└── (Reports will be saved here with timestamps)
```

---

## 💡 Best Practices

### For Task Management

1. **Use consistent priorities**: 🔴 P1 (urgent), 🟡 P2 (important), 🟢 P3 (sometime)
2. **Tag tasks**: Use #project, #personal, #work for filtering
3. **Daily review**: Check and update tasks daily
4. **Weekly summary**: Generate task manager report weekly

### For Link Health

1. **Create MOCs**: Build Maps of Content for topic hubs
2. **Link orphans**: Connect isolated notes to your graph
3. **Fix dead-ends**: Add outgoing links from terminal notes
4. **Resolve links**: Fix or remove unresolved links

### For Vault Analytics

1. **Monthly checkups**: Generate full analytics monthly
2. **Track trends**: Compare reports over time
3. **Act on insights**: Use recommendations to improve
4. **Save reports**: Keep historical reports for comparison

---

## 🔧 Advanced: Using the CLI Module Directly

The `obsidian_cli.py` module can be used in your custom scripts:

```python
from _scripts.obsidian_cli import get_cli

cli = get_cli()

# Create a new file
cli.create_file(
    name="New Note.md",
    content="# New Note\n\nContent here...",
    template="Project Note"
)

# Append to daily note
cli.append_to_daily("- [ ] New task from script")

# Search vault
results = cli.search(query="AI", format="json")

# Manage properties
cli.set_property(
    name="status",
    value="active",
    prop_type="text",
    path="Project.md"
)
```

---

## 🎯 Next Steps

1. **Try the skills**: Run each skill to see your current state
2. **Review reports**: Check the generated reports for insights
3. **Act on recommendations**: Start with the most critical issues
4. **Integrate into workflow**: Add these skills to your daily/weekly routine
5. **Customize**: Modify the skills to fit your specific needs

---

## 📚 Additional Resources

- [Obsidian CLI Documentation](obsidian://help)
- Your existing `Script Usage Guide.md`
- `_scripts/README.md` for existing skill documentation

---

*Integration created on 2026-02-18*
