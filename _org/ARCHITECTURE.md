# Atomic Design Architecture

## Visual Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          PAGES (CLI)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  cli.py      │  │  run.py      │  │  examples.py     │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       TEMPLATES (Workflows)                      │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐ │
│  │ DailyWorkflow  │  │ WeeklyWorkflow │  │ CustomWorkflow   │ │
│  └────────────────┘  └────────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ORGANISMS (Modules)                         │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐│
│  │ ContentDigester  │ │ AnalysisTools    │ │EnhancementTools ││
│  └──────────────────┘ └──────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MOLECULES (Composite)                         │
│  ┌──────────────────┐      ┌──────────────────┐                 │
│  │ ScriptRegistry   │      │ ExecutionEngine  │                 │
│  └──────────────────┘      └──────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ATOMS (Core)                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │  Config  │ │  Logger  │ │ScriptRunner  │ │  Validators  │ │
│  └──────────┘ └──────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Atoms (Smallest Building Blocks)
- **config.py**: Vault path management, environment loading, API config
- **logger.py**: Execution tracking, result formatting, log persistence
- **script_runner.py**: Single script execution, output capture, timeout handling
- **validators.py**: Input validation, path checking, script validation

### Molecules (Composite Components)
- **script_registry.py**: Script metadata, categorization, discovery
- **execution_engine.py**: Multi-script orchestration, callbacks, progress tracking

### Organisms (Functional Modules)
- **content_digester.py**: News, papers, social media ingestion
- **analysis_tools.py**: Reflection, evolution, synthesis
- **enhancement_tools.py**: AI insights, note enhancement

### Templates (Workflow Orchestrators)
- **daily_workflow.py**: Daily automation (digestion + light analysis)
- **weekly_workflow.py**: Weekly full automation
- **custom_workflow.py**: Build your own workflows

### Pages (User Interfaces)
- **cli.py**: Command-line interface
- **run.py**: Convenient entry point
- **examples.py**: Usage examples

## Data Flow

```
User Command
    │
    ▼
CLI (Pages)
    │
    ▼
Workflow (Templates)
    │
    ├─→ Organism 1
    │      │
    │      ├─→ Molecule (Registry)
    │      └─→ Molecule (Execution Engine)
    │              │
    │              ├─→ Atom (Config)
    │              ├─→ Atom (ScriptRunner)
    │              └─→ Atom (Logger)
    │
    ├─→ Organism 2
    │      └─→ (same as above)
    │
    └─→ Organism 3
           └─→ (same as above)
    │
    ▼
Results & Logs
```
