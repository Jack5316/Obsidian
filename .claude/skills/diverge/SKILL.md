---
name: diverge
description: Divergent thinking skill - exploratory idea generation, branching exploration, cross-domain connections, and creative brainstorming. Use when you want to expand possibilities, generate many ideas, explore different directions, or make unexpected connections.
---

# Diverge Skill (/diverge)

Facilitates divergent thinking - generating multiple creative ideas, exploring possibilities, branching out from a central concept, and making unexpected connections. Inspired by neuroscience concepts of neural plasticity and associative thinking, combined with Tiago Forte's Second Brain principles.

## Quick Start

```bash
python3 _scripts/diverge.py "future of AI"
```

## What It Does

1. **Idea Generation** - Generate multiple creative ideas from a central topic
2. **Branch Exploration** - Explore multiple directions a topic could evolve into
3. **Cross-Domain Connections** - Find surprising connections between unrelated fields
4. **Question Storming** - Generate provocative questions that challenge assumptions
5. **Mind Maps** - Create structured mind map visualizations
6. **Random Walks** - Take associative journeys through idea space

## Features

### Core Modes

- **Full Session** - Complete divergent thinking exploration (default)
- **Ideas Only** - Focus on generating ideas
- **Branch Exploration** - Map possible evolutionary paths
- **Cross-Domain** - Connect to unrelated fields (biology, music, physics, etc.)
- **Question Storm** - Challenge assumptions with questions
- **Mind Map** - Create structured visualizations
- **Random Walk** - Serendipitous associative exploration

### Cognitive Principles Applied

- **Quantity over quality** - Generate many ideas first, filter later
- **Associative thinking** - Leverage neural connectivity patterns
- **Pattern breaking** - Escape cognitive fixedness
- **Concept blending** - Merge ideas from different domains
- **Provocative questioning** - Challenge fundamental assumptions

## Options

- `topic`: Central topic to explore (required)
- `--ideas N`: Generate exactly N ideas
- `--branches`: Explore branching directions from topic
- `--cross-domain`: Find connections to unrelated domains
- `--questions N`: Generate N provocative questions
- `--mindmap`: Create a mind map structure
- `--randomwalk N`: Take random associative walk of N steps
- `--save`: Save output to Sources folder

## Examples

```bash
# Full divergence session on a topic
python3 _scripts/diverge.py "future of education"

# Generate 20 ideas about AI
python3 _scripts/diverge.py "artificial intelligence" --ideas 20

# Explore branching paths of a topic
python3 _scripts/diverge.py "climate technology" --branches

# Find cross-domain connections
python3 _scripts/diverge.py "creativity" --cross-domain

# Generate 25 provocative questions
python3 _scripts/diverge.py "problem statement" --questions 25

# Create a mind map
python3 _scripts/diverge.py "complex topic" --mindmap

# Take a random walk of 8 steps
python3 _scripts/diverge.py "starting concept" --randomwalk 8

# Save output to Sources
python3 _scripts/diverge.py "topic" --save
```

## How It Works

### The Divergence Process

1. **Central Topic** - Start with a single concept or problem
2. **Multi-Directional Expansion** - Branch out in many directions simultaneously
3. **Cross-Pollination** - Mix concepts from different domains
4. **Quantity First** - Prioritize generating many ideas over perfect ideas
5. **Serendipity Engine** - Create conditions for unexpected connections to emerge

### Neuroscience Inspiration

- **Hebbian Learning** - "Neurons that fire together, wire together"
- **Neural Plasticity** - Brain's ability to form new connections
- **Default Mode Network** - Active during mind-wandering and creative thinking
- **Semantic Networks** - Concepts connected by meaning and association

## Output

- **Terminal**: Formatted markdown with your divergence session
- **Saved note**: `Sources/Diverge - [topic] - YYYY-MM-DD.md`

## When to Use

Use /diverge when:
- You need to generate many creative ideas
- You feel stuck in conventional thinking patterns
- You want to explore multiple possible futures
- You need to make unexpected connections
- You want to challenge basic assumptions
- You're starting a new project and want to explore possibilities
- You need inspiration from unrelated domains

## Pairing with Other Skills

- **/converge** - Use after /diverge to narrow down and prioritize
- **/gradient** - Use to iteratively refine promising ideas
- **/random-walk** - Complementary for serendipitous discovery
- **/memory** - Save interesting insights for future reference
