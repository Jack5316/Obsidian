---
name: converge
description: Convergent thinking skill - synthesis, prioritization, decision making, and actionable next steps. Use when you need to narrow down options, make decisions, prioritize, find patterns, or identify concrete next steps.
---

# Converge Skill (/converge)

Facilitates convergent thinking - synthesizing multiple ideas into coherent wholes, prioritizing options, making decisions, and narrowing down possibilities to actionable next steps. Inspired by neuroscience concepts of cognitive control and decision making, combined with Tiago Forte's Second Brain principles.

## Quick Start

```bash
python3 _scripts/converge.py "future projects" --ideas "idea1" "idea2" "idea3"
```

## What It Does

1. **Synthesis** - Find patterns and common themes across ideas
2. **Prioritization** - Rank options using multiple frameworks
3. **Decision Making** - Make clear decisions with justification
4. **Next Steps** - Generate concrete, actionable plans
5. **Tradeoff Analysis** - Evaluate pros and cons systematically
6. **Distillation** - Extract essence from noisy content

## Features

### Core Modes

- **Synthesis** - Find patterns and connections in chaos
- **Prioritization** - Rank options using frameworks like impact-effort matrix
- **Decision** - Make clear decisions with pros/cons and second-order thinking
- **Next Steps** - Generate concrete, actionable plans with timelines
- **Tradeoffs** - Analyze what you gain and lose with each option
- **Distillation** - Condense content to its essential core
- **Full Session** - Complete convergence from synthesis to action

### Decision Frameworks

- **impact-effort** - High impact, low effort first
- **urgent-important** - Eisenhower matrix
- **cost-benefit** - ROI analysis
- **risk-reward** - Risk assessment
- **value-complexity** - Value vs implementation cost
- **pros-cons** - Classic balance sheet
- **decision-matrix** - Multi-criteria scoring
- **SWOT** - Strengths, Weaknesses, Opportunities, Threats

### Cognitive Principles Applied

- **Pattern recognition** - Extract signal from noise
- **Cognitive control** - Focus on what matters
- **Decision theory** - Systematic choices under uncertainty
- **Opportunity cost** - What you give up matters
- **Second-order thinking** - Consider downstream consequences

## Options

- `topic`: Topic or question to converge on (required)
- `--ideas LIST`: List of ideas/options to process
- `--synthesize`: Synthesize ideas into patterns
- `--prioritize`: Prioritize options
- `--decide`: Make a decision
- `--nextsteps`: Generate actionable next steps
- `--tradeoffs`: Analyze tradeoffs
- `--distill FILE`: Distill a file to its essence
- `--framework NAME`: Framework to use (default: impact-effort)
- `--ratio FLOAT`: Distillation ratio 0.1-0.9 (default: 0.3)
- `--full`: Full convergence session
- `--save`: Save output to Sources folder

## Examples

```bash
# Synthesize ideas
python3 _scripts/converge.py "AI projects" --ideas "chatbot" "summarizer" "analyzer" --synthesize

# Prioritize options with framework
python3 _scripts/converge.py "which project" --prioritize --ideas "project1" "project2" "project3" --framework impact-effort

# Make a decision
python3 _scripts/converge.py "which tool to build?" --decide --ideas "Tool A" "Tool B" --framework pros-cons

# Generate next steps
python3 _scripts/converge.py "launch product" --nextsteps

# Analyze tradeoffs
python3 _scripts/converge.py "technology choice" --tradeoffs --ideas "React" "Vue" "Svelte"

# Distill a file to 30% length
python3 _scripts/converge.py --distill long_article.md --ratio 0.3

# Full convergence session
python3 _scripts/converge.py "q4 goals" --ideas "goal1" "goal2" "goal3" --full

# Save output to Sources
python3 _scripts/converge.py "topic" --ideas "i1" "i2" --save
```

## How It Works

### The Convergence Process

1. **Input Gathering** - Collect all options, ideas, or content
2. **Pattern Recognition** - Find common themes and connections
3. **Framework Application** - Apply structured decision models
4. **Clear Prioritization** - Create ordered rankings with rationale
5. **Decision Making** - Make clear, justifiable choices
6. **Action Generation** - Translate decisions into concrete steps

### Neuroscience Inspiration

- **Prefrontal Cortex** - Cognitive control and decision making
- **Basal Ganglia** - Action selection and prioritization
- **Dopamine System** - Reward prediction and risk assessment
- **Conflict Monitoring** - Evaluating tradeoffs and resolving dilemmas

## Output

- **Terminal**: Formatted markdown with your convergence session
- **Saved note**: `Sources/Converge - [topic] - YYYY-MM-DD.md`

## When to Use

Use /converge when:
- You have many options and need to prioritize
- You need to make a clear decision with justification
- You need to synthesize chaotic information into patterns
- You want to identify concrete, actionable next steps
- You need to analyze tradeoffs systematically
- You need to distill long content to its essence
- You've just used /diverge and need to narrow down

## Pairing with Other Skills

- **/diverge** - Use before /converge to expand possibilities
- **/gradient** - Use after /converge to iteratively refine decisions
- **/curl** - Gather information to feed into convergence
- **/memory** - Save decisions and priorities for future reference
- **/obsidian-tasks** - Turn next steps into actionable tasks
