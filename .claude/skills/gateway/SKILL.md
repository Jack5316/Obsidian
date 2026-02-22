---
name: gateway
description: Skill map and integration guide. Tracks existing skills, relationships, and how to integrate new skills. Clarifies Functions, Connections, Limitations, Guidance (FCLG) for each skill. Use when creating a new skill, navigating skills, understanding skill relationships, or /gateway.
---

# Gateway Skill (/gateway)

The Gateway keeps track of all skills and how they connect. When you create a new skill, it analyzes integration. For every skill it clarifies: **Functions**, **Connections**, **Limitations**, **Guidance** (FCLG).

## Quick Start

```bash
# Full skill map (all skills, FCLG)
python3 _scripts/gateway.py

# Deep dive on one skill
python3 _scripts/gateway.py --skill rag

# New skill integration (after creating with meta-skill)
python3 _scripts/gateway.py --integrate my-new-skill "Brief description"

# Save to vault
python3 _scripts/gateway.py --save
```

## What It Produces

### Full Map (`gateway` or `gateway --save`)
- **Overview** — Skill ecosystem and how to navigate
- **Quick Reference** — Table: Skill | Category | One-line function
- **Full Map** — Each skill with FCLG
- **Common Workflows** — Suggested pipelines and combinations

### Single Skill (`--skill NAME`)
- **Functions** — What it does (specific, actionable)
- **Connections** — Related skills, pipelines, data flow
- **Limitations** — What it can't do, when NOT to use
- **Guidance** — How to use, best practices, shortcuts

### Integration (`--integrate NAME "Description"`)
- **Placement** — Category, related skills
- **Functions, Connections, Limitations, Guidance**
- **Suggested Pipelines** — Workflows including the new skill
- **Registration Checklist** — skills.json, SKILL.md, pipelines

## Options

| Option | Description |
|--------|--------------|
| (none) | Generate full skill map |
| `--skill`, `-s` | Deep FCLG for one skill |
| `--integrate`, `-i` | Integration analysis for new skill |
| `--save` | Save to `Maps/Skill Gateway.md` or `Maps/Gateway - {name}.md` |

## Examples

```bash
# Full map, save to vault
python3 _scripts/gateway.py --save

# Understand the RAG skill
python3 _scripts/gateway.py --skill rag --save

# Just created a "read-later" skill — how does it fit?
python3 _scripts/gateway.py --integrate read-later "Process saved articles from Instapaper/Pocket" --save
```

## Workflow with Meta-Skill

1. Create skill: `python3 _scripts/meta_skill.py create read-later "Process saved articles"`
2. Implement logic in the generated script
3. Run Gateway: `python3 _scripts/gateway.py --integrate read-later "Process saved articles" --save`
4. Use the integration guide to register, add to pipelines, connect to other skills

## Output

- **Terminal**: Full output (truncated if long)
- **Saved**: `Maps/Skill Gateway.md` (full map) or `Maps/Gateway - {skill}.md` (single/integration)
