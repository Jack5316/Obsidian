---
name: evolve
description: Run system self-evolution and improvement cycle. Use when user asks for self-evolution, SEAI, or /evolve.
---

# Self-Evolution Skill

SEAI framework: analyzes performance, generates improvements with rollback plans, tracks iterations.

## Usage

```bash
python3 _scripts/self_evolution.py cycle [--iteration N] [--safe]
python3 _scripts/self_evolution.py continuous [--iterations N] [--safe]
python3 _scripts/self_evolution.py analyze [--iterations N] [--report]
```

- `cycle`: Single evolution iteration
- `continuous`: Multiple iterations
- `analyze`: View history and generate report
- `--safe`: Require confirmation before applying changes

## Output

`_logs/evolution_log.json` — iteration history
