# The Personal AI Infrastructure: A Skills System Manifesto

**Date:** 2026-02-19

## TL;DR

This is not a collection of scripts. This is a Personal AI Infrastructure (PAI) — a loosely coupled, self-evolving system designed for one person's information sovereignty. The Obsidian vault is the data substrate; Python scripts are the skills; Claude Code is the CLI orchestrator.

---

## The 5-Layer Pyramid: Building Your Personal Jarvis

Inspired by Fan Bing's framework, this system follows a clear 5-layer architecture:

| Layer | Role | Implementation |
|-------|------|----------------|
| **L1 Dev Tools** | CLI-first interface | Claude Code + skills system |
| **L2 Data** | Local-first knowledge substrate | Obsidian vault (markdown, bidirectional links) |
| **L3 Skills** | Reusable workflow units | `_scripts/*.py` + `.claude/skills/` |
| **L4 Scenarios** | Automated daily tasks | Content curation, summarization, publishing |
| **L5 Review** | System watches itself | Daily/weekly/monthly reflection + self-evolution |

## Design Principles: The Philosophy Behind the Code

### Scripts Before Prompts

If a task can be codified as Python, don't burn tokens on it. Use AI only for judgment, creativity, and ambiguity. Every script follows the dual strategy pattern:
- **Python**: Fetch and filter data (API calls, scraping, parsing)
- **AI**: Process through `summarize()` — only for judgment/synthesis

### Small File Philosophy

Each script does one thing well (single responsibility), is simple to understand, and gains power through composition. A script that tries to do everything does nothing well.

### Loose Coupling

Each layer is independently optimizable and swappable. The skills layer doesn't care if the data layer moves from Obsidian to Logseq. Change is inevitable; architecture should embrace it.

### Context is the Moat

Accumulated personal context (writing style, preferences, information diet) transforms a generic LLM into a personal assistant. Accumulate gradually. The system remembers what you like, what you don't, and how you think.

### Extract Skills from Repetition

Every time you solve a problem with AI twice, extract it into a reusable skill. Repetition is signal — turn it into infrastructure.

## Philosophical Grounding: The Personal Panopticon

This isn't about surveillance for control — it's about self-surveillance for empowerment.

### The Tower Belongs to You

Every piece of tracked data serves your agency. No ads, no data sales, no external incentives. This system works for you, and only you.

### Cross-Domain Synthesis is the Superpower

The highest-value insights come from noticing patterns across domains kept stubbornly separate. Daily scripts whisper cross-domain connections; weekly synthesis shouts them.

### Productive Illegibility

Not everything should be tracked. The system must periodically question its own metrics (Goodhart resistance). A metric that can be gamed will be — even by the system itself.

### Activation Energy, Not Ability

The bottleneck is never capability but the friction to start. Every unnecessary step is a design failure. Make the right thing the easy thing.

### Thought Traces as Recursive Fuel

All outputs (digests, syntheses, reflections) are inputs to future synthesis. The system's memory is its compounding advantage. Yesterday's insights become tomorrow's context.

## The Skills: Your AI Toolbelt

This system includes **100+ skills** organized by purpose:

### Orchestration
- `/skill org` - Run all automation + reflect
- `/skill org-daily` - Daily: ArXiv, HN, Reddit, news, Twitter
- `/skill org-weekly` - Weekly: synthesis + self-reflection

### Content Curation
- `/skill ai-brief` - Morning brew of AI news
- `/skill arxiv` - ArXiv papers by topic
- `/skill hn` - Hacker News digest
- `/skill reddit` - Reddit digest
- `/skill news` - Chinese news from tophub.today
- And dozens more for books, movies, podcasts, and personal tracking

### Self-Improvement
- `/skill reflect` - Self-reflection report
- `/skill evolve` - Self-evolution improvement cycle
- `/skill insights` - Iterative insight enhancement
- `/skill review` - Monthly/quarterly system review

### Obsidian Integration
- `/skill obsidian-vault` - Vault analytics & health monitoring
- `/skill obsidian-tasks` - Task management & tracking
- `/skill obsidian-links` - Knowledge graph & link analysis

### And So Much More
- Memory consolidation, random walks, deep research, steelman debates, flashcards, thread creation, publishing, backups, thinking tools, and on and on...

## Building Your Own: How to Create a Skill

When you notice yourself solving the same problem twice, extract it:

1. **Create the Python Script** in `_scripts/` - follow the dual strategy pattern
2. **Create the Skill Definition** in `.claude/skills/<name>/SKILL.md` - document what it does and how to use it
3. **Register in skills.json** - make it discoverable
4. **Test it** - make sure it works without errors
5. **Use it** - turn repetition into infrastructure

## The Review Layer: The System That Improves Itself

Three scripts form the self-improvement feedback loop:

- **self_reflection.py** - analyzes system behavior and effectiveness
- **self_evolution.py** - generates and tracks improvement suggestions with rollback plans
- **insight_enhancement.py** - manages an insight repository with lifecycle: discovered → planned → implemented → verified

**Review cadence:**
- **Daily** - aggregate summaries, check health
- **Weekly** - adjust sources, filter noise, Goodhart check
- **Monthly** - optimize system, upgrade skills

The weekly synthesis includes a **Goodhart resistance audit** — the system explicitly questions whether its own metrics still serve curiosity rather than habit.

## Information Sovereignty in the Age of AI

This isn't just about productivity. This is about:

- **Owning your data** - everything lives in your Obsidian vault, on your filesystem
- **Controlling your tools** - no vendor lock-in, no API dependencies you can't replace
- **Building for yourself** - this system evolves with you, not the other way around
- **Thinking in public** - but only for yourself, in your own private second brain

## The Vision: Your Digital Extension

This system is more than code. It's a cognitive prosthesis. It remembers what you forget, connects what you miss, synthesizes what you consume, and evolves with you over time.

It doesn't replace your thinking — it augments it. It doesn't make decisions for you — it gives you better information to make decisions with. It doesn't own your data — you do.

This is Personal AI Infrastructure. This is your Jarvis. This is information sovereignty.

---

*Built with intention, used with care, evolved with reflection.*
