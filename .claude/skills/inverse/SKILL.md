---
name: inverse
description: Inverse thinking — compute reversely for problems, decisions, actions, and confusions. Inspired by linear algebra's inverse matrix and Charlie Munger's "invert, always invert." Use when you want to flip a problem, reverse a decision, undo an action, or dissolve confusion.
---

# Inverse Skill (/inverse)

Apply inverse thinking to problems, decisions, actions, and confusions. Inspired by the inverse matrix in linear algebra (A⁻¹ undoes A) and Charlie Munger's principle: "Invert, always invert."

## Quick Start

```bash
python3 _scripts/inverse.py problem "I can't find time to exercise"
python3 _scripts/inverse.py decision "Should I quit my job?"
python3 _scripts/inverse.py action "I'm going to start a side project"
python3 _scripts/inverse.py confusion "I don't know what career path to take"
```

## What It Does

The inverse skill computes the **reverse** of your input across four types:

| Type | Inverse Lens |
|------|--------------|
| **problem** | What would NOT having this problem mean? What would undo it? |
| **decision** | What would the opposite choice mean? What would reversing the decision look like? |
| **action** | What would undo this action? What would the opposite action be? |
| **confusion** | What would clarity look like? What would dissolve the confusion? |

## The Inverse Matrix Analogy

In linear algebra: A · A⁻¹ = I. The inverse "undoes" a transformation. Similarly:

- **Problem** → Inverse reveals what conditions would make the problem disappear
- **Decision** → Inverse reveals what the opposite choice implies
- **Action** → Inverse reveals what reversing the action would mean
- **Confusion** → Inverse reveals what clarity would look like

## Options

- `type`: One of `problem`, `decision`, `action`, `confusion` (required)
- `input_text`: The problem, decision, action, or confusion to invert (required)
- `--from-path PATH`: Path to a note containing additional context
- `--title TEXT`: Custom output filename
- `--save`: Save output to vault (default: prints to terminal only)

## Examples

```bash
# Invert a problem
python3 _scripts/inverse.py problem "Procrastination on important projects"

# Invert a decision
python3 _scripts/inverse.py decision "Should I move to a new city?"

# Invert an action
python3 _scripts/inverse.py action "I'm cutting back on social media"

# Invert confusion
python3 _scripts/inverse.py confusion "I'm unsure about my relationship"

# With vault context and save
python3 _scripts/inverse.py problem "Career stagnation" --from-path "Atlas/Career Notes.md" --save
```

## Output

- **Terminal**: Markdown-formatted inverse analysis with "The Inverse," "What This Reveals," and "Inverse Actions"
- **Saved note**: `Atlas/Inverse - [Topic].md` with YAML frontmatter

## Why This Matters

- **Shifts perspective** — The inverse view often reveals what the forward view obscures
- **Easier to solve** — Many problems are simpler when inverted (Munger's insight)
- **Exposes blind spots** — The inverse can reveal flaws or assumptions
- **Concrete clarity** — Inverse formulations lead to actionable next steps
