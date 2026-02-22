# AI Vault Automation - Atomic Design System

A modular automation system for your Obsidian vault using atomic design principles.

**Both systems work together!** You can use the new atomic design system or continue using your existing legacy skill scripts.

## Architecture

```
_org/
├── atoms/          # Core utilities (smallest building blocks)
│   ├── config.py       # Vault configuration management
│   ├── logger.py       # Execution logging and result tracking
│   ├── script_runner.py # Individual script execution
│   └── validators.py   # Input validation utilities
├── molecules/      # Composite components
│   ├── script_registry.py # Script metadata and categorization
│   └── execution_engine.py # Multi-script orchestration
├── organisms/      # Complete functional modules
│   ├── content_digester.py  # Content ingestion workflows
│   ├── analysis_tools.py    # Analysis and reflection tools
│   └── enhancement_tools.py # Note enhancement tools
├── templates/      # Workflow orchestrators
│   ├── daily_workflow.py    # Daily automation workflow
│   ├── weekly_workflow.py   # Weekly automation workflow
│   └── custom_workflow.py   # Build custom workflows
└── pages/          # CLI interfaces
    └── cli.py            # Main command-line interface
```

## Quick Start

### Choose Your System

**Option 1: New Atomic Design System (Recommended)**
```bash
python _org/run.py help
```

**Option 2: Legacy Skill System (Existing)**
```bash
python _scripts/org_skill.py --list
python _org/compatibility.py org_skill.py
```

### List Available Commands (Atomic System)
```bash
python _org/run.py help
```

### Run Legacy Skills
```bash
# List legacy skills
python _org/compatibility.py

# Run original org_skill
python _org/compatibility.py org_skill.py --list

# Run other skills
python _org/compatibility.py tophub_news_simple_skill.py
```

### List Available Scripts
```bash
python _org/run.py list
python _org/run.py list-categories
```

### Run Daily Workflow
```bash
# Full daily workflow
python _org/run.py daily

# Quick daily (news only)
python _org/run.py daily-quick

# Skip specific scripts
python _org/run.py daily --skip twitter_capture.py,reddit_digest.py
```

### Run Weekly Workflow
```bash
# Full weekly workflow
python _org/run.py weekly

# Weekly synthesis only
python _org/run.py weekly-synth
```

## Using as a Library

You can also use the system programmatically:

```python
from _org import DailyWorkflow, WeeklyWorkflow, CustomWorkflow
from _org import VaultConfig, ScriptRegistry

# Run daily workflow
workflow = DailyWorkflow()
results = workflow.run()

# Build custom workflow
custom = CustomWorkflow()
custom.add_phase_by_category("News", "content_digest")
custom.add_phase_by_tags("Analysis", ["reflection"])
results = custom.run("My Custom Workflow")
```

## Script Categories

- **content_digest**: Content ingestion (news, papers, social media)
- **analysis**: Analysis and reflection tools
- **enhancement**: Note enhancement and AI insights
- **publishing**: Publishing and export tools
- **system**: System maintenance tools

## Benefits of Atomic Design

1. **Modularity**: Each component can be used independently
2. **Reusability**: Atoms and molecules can be combined in new ways
3. **Maintainability**: Changes to one component don't break others
4. **Extensibility**: Easy to add new scripts and workflows
5. **Testability**: Each component can be tested in isolation

## Extending the System

### Adding a New Script
1. Create your script in `_scripts/`
2. Register it in `_org/molecules/script_registry.py`
3. It will automatically be available in all workflows

### Creating a Custom Workflow
```python
from _org import CustomWorkflow

workflow = CustomWorkflow()

# Add phases by category, tags, or specific scripts
workflow.add_phase_by_category("Content", "content_digest")
workflow.add_phase_by_tags("Analysis", ["weekly", "synthesis"])

workflow.run("My Custom Workflow")
```

## Logs

All execution logs are saved to `_logs/org_session_YYYYMMDD_HHMMSS.log` in JSON format.
