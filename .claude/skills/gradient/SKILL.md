---
name: gradient
description: Gradient descent inspired iterative refinement - gradually improve ideas, text, and solutions through multiple refinement cycles. Use when you want to iteratively improve something, get constructive critique, compare versions, or progressively enhance your work.
---

# Gradient Skill (/gradient)

Facilitates iterative refinement - gradually improving ideas, text, and solutions through multiple refinement cycles. Inspired by gradient descent in machine learning and the concept of progressive learning, combined with Tiago Forte's Second Brain principles of incremental improvement.

## Quick Start

```bash
python3 _scripts/gradient.py --file draft.md --refine
```

## What It Does

1. **Iterative Refinement** - Multi-round improvement cycles
2. **Constructive Critique** - Detailed feedback without rewriting
3. **Version Comparison** - A/B comparison of different versions
4. **Progressive Enhancement** - Gradual improvement toward a goal
5. **Idea Enhancement** - Focus on specific aspects (clarity, depth, etc.)
6. **Learning Rate Control** - Adjust how aggressive changes are

## Features

### Core Modes

- **Single Refine** - One iteration of improvement
- **Multi-Iteration** - Multiple refinement cycles
- **Critique Only** - Feedback without rewriting
- **A/B Compare** - Compare two versions and recommend
- **Enhance Idea** - Focus on specific quality aspects
- **Progressive** - Iterate until convergence

### Enhancement Aspects

- **clarity** - Make it easier to understand
- **depth** - Add substance and thoroughness
- **practicality** - Make it more actionable
- **originality** - Make it more unique
- **feasibility** - Make it more implementable
- **structure** - Improve organization
- **persuasion** - Make it more compelling

### Machine Learning Inspiration

- **Gradient Descent** - Small steps toward optimization
- **Learning Rate** - Control step size (aggressiveness)
- **Convergence Detection** - Know when to stop
- **Loss Function** - Implicit goal optimization
- **Version History** - Track improvement trajectory

## Options

- `--text TEXT`: Text to refine directly
- `--file FILE`: File to read content from
- `--refine`: Single refinement iteration
- `--iterations N`: Number of refinement iterations
- `--critique`: Provide critique without rewriting
- `--compare FILE`: Second file for A/B comparison
- `--enhance`: Enhance an idea
- `--aspects LIST`: Aspects to focus on (clarity, depth, etc.)
- `--progressive`: Progressive improvement until convergence
- `--goal TEXT`: Goal for the refinement
- `--save`: Save output to Sources folder

## Examples

```bash
# Single refinement of a file
python3 _scripts/gradient.py --file draft.md --refine

# Single refinement of direct text
python3 _scripts/gradient.py --text "My idea needs work" --refine

# Multiple iterations (3 rounds)
python3 _scripts/gradient.py --file draft.md --iterations 3

# Get constructive critique
python3 _scripts/gradient.py --file draft.md --critique

# Compare two versions
python3 _scripts/gradient.py --file version1.md --compare version2.md

# Enhance an idea focusing on specific aspects
python3 _scripts/gradient.py --text "My idea" --enhance --aspects clarity practicality

# Progressive improvement with goal
python3 _scripts/gradient.py --file draft.md --progressive --goal "Make this more concise"

# With goal and save
python3 _scripts/gradient.py --file draft.md --refine --goal "Add more examples" --save
```

## How It Works

### The Refinement Cycle

1. **Critique** - Analyze strengths and weaknesses
2. **Improve** - Make targeted, meaningful changes
3. **Review** - Assess progress
4. **Iterate** - Repeat until goal is reached
5. **Converge** - Stop when diminishing returns

### Progressive Learning Principles

- **Small steps** - Make meaningful but focused changes
- **Build on strengths** - Preserve what works
- **Fix weaknesses** - Address limitations systematically
- **Track trajectory** - Maintain version history
- **Goal-directed** - Always move toward a clear objective

## Output

- **Terminal**: Formatted markdown with your refinement session
- **Saved note**: `Sources/Gradient - [topic] - YYYY-MM-DD.md`

## When to Use

Use /gradient when:
- You have a draft that needs iterative improvement
- You want constructive feedback on something
- You need to compare different versions
- You want to progressively enhance an idea
- You're writing and want to refine through multiple passes
- You have a solution that can be optimized incrementally
- You want to focus on improving specific aspects (clarity, depth, etc.)

## Pairing with Other Skills

- **/diverge** - Use before /gradient to generate initial ideas
- **/converge** - Use with /gradient to decide which direction to take
- **/curl** - Gather information to feed into refinement
- **/memory** - Save refinement insights for future projects
- **/essay** - Use /gradient to iteratively improve your essays
