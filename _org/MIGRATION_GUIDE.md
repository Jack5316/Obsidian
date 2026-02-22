# Migration Guide: Legacy Skills → Atomic Design

Both systems work side-by-side! You don't need to migrate immediately.

## Side-by-Side Comparison

| Task | Legacy System | Atomic Design System |
|------|----------------|---------------------|
| List all scripts | `python _scripts/org_skill.py --list` | `python _org/run.py list` |
| Run all scripts | `python _scripts/org_skill.py` | `python _org/run.py daily` |
| Skip scripts | `python _scripts/org_skill.py --skip s1,s2` | `python _org/run.py daily --skip s1,s2` |
| Run daily tasks | `python _scripts/org_skill.py` | `python _org/run.py daily` |
| Run weekly tasks | (custom bash script) | `python _org/run.py weekly` |
| Quick news check | (custom) | `python _org/run.py daily-quick` |

## Features: Atomic Design Advantages

### Organization
- ✅ Scripts categorized by function
- ✅ Browse by tags and categories
- ✅ Clear separation of concerns

### Workflows
- ✅ Pre-built daily/weekly workflows
- ✅ Build custom workflows programmatically
- ✅ Phased execution with callbacks

### Extensibility
- ✅ Add new scripts without changing core code
- ✅ Compose existing components in new ways
- ✅ Full library API available

## When to Use Which

### Use Legacy System (`_scripts/`) if:
- You have existing cron jobs set up
- You prefer the original simplicity
- You need the exact org_skill.py behavior

### Use Atomic Design System (`_org/`) if:
- You want organized, categorized workflows
- You want to build custom automation
- You want better logging and tracking
- You want to extend the system

## Running Both Systems

You can run both systems without conflicts:

```bash
# Legacy system
python _scripts/org_skill.py --list

# Atomic system
python _org/run.py list

# Both work with the same scripts!
```

## Gradual Migration

1. **Try the new system** - Run `python _org/run.py daily` and see how it works
2. **Use both in parallel** - Keep your existing setup, try new workflows
3. **Migrate when ready** - Update your cron jobs to use the new system when comfortable

## Compatibility Layer

The compatibility layer lets you run legacy skills from the atomic system:

```bash
# List legacy skills
python _org/compatibility.py

# Run org_skill.py through compatibility layer
python _org/compatibility.py org_skill.py --list
```
