---
name: random-walk
description: Explore your Obsidian vault through serendipitous discovery. Randomly selects notes, traces connection paths, and suggests research directions. Use when you want to discover forgotten insights, find unexpected connections, or need inspiration for research topics.
---

# Random Walk Skill (/random-walk)

Explore your Obsidian vault through serendipitous discovery. The random walk skill helps you find forgotten insights, discover unexpected connections, and get inspired by exploring your knowledge base in a non-linear way.

## Quick Start

```bash
python3 _scripts/random_walk.py --save
```

## Features

1. **Random Note Selection** - Picks random notes from your vault, skipping very short ones
2. **Connection Path Tracing** - Follows [[wikilinks]] to discover connected notes
3. **AI-Powered Analysis** - Analyzes discoveries and suggests research directions
4. **Topic Focus** - Optionally focus random walks on specific topics
5. **Research Output** - Saves structured exploration notes with insights and next steps

## Options

- `--count N`: Number of random notes to select (default: 5)
- `--topic TEXT`: Focus random walk on a specific topic
- `--save`: Save research exploration note to vault

## Examples

```bash
# Basic random walk
python3 _scripts/random_walk.py

# Explore more notes
python3 _scripts/random_walk.py --count 10

# Focus on AI topics
python3 _scripts/random_walk.py --topic "AI"

# Save the exploration
python3 _scripts/random_walk.py --save
```

## Output

- **Terminal**: Detailed research exploration with insights and suggestions
- **Saved note**: `Sources/Random Walk - YYYY-MM-DD.md`

## Output Format

The skill generates a structured research exploration including:

- **Today's Discovery Path** - The path traced through your notes
- **Key Insights Found** - Interesting insights from the random notes
- **Unexpected Connections** - Non-obvious connections between notes
- **Research Questions** - Curious questions raised by the exploration
- **Forgotten Gems** - Notes or ideas you might have forgotten
- **Suggested Next Steps** - Concrete actions to continue exploring

## When to Use

- When you're feeling stuck and need inspiration
- When you want to rediscover forgotten notes
- When you're curious about unexpected connections in your knowledge base
- When you need research topic ideas
- When you want to explore your vault without a specific goal

## Tips

- Use `--topic` to explore specific themes you're interested in
- Increase `--count` for deeper exploration sessions
- Always use `--save` to keep a record of your discoveries
- Try multiple random walks - each one is unique!
