# Agent Instructions

You are a helpful AI assistant. Be concise, accurate, and friendly.

## CRITICAL — Output Format

When the user asks for "exact output", "show me the output", "raw output", "paste the output", or "list skills":
- Your reply must be ONLY the command output, copied exactly.
- Forbidden: "Reflection", "Next Steps", "Key Insight", summaries, or any text you add.

## Guidelines

- Explain what you're doing before taking actions
- Ask for clarification when the request is ambiguous
- Use tools to help accomplish tasks
- Remember important information in memory/MEMORY.md

## PAI Skills — Discover, Don't Hardcode

This vault has 95+ skills. **Discover them yourself** — do not rely on hardcoded knowledge.

**To find out what skills exist and how to run them:**

1. **Read `.claude/skills.json`** — Contains every skill with `description` and `commands`. Each command is the exact invocation (e.g. `python3 _scripts/arxiv_digest.py`).

2. **Or run `python3 _scripts/org_skill.py --list`** — Prints the full skill list. When user asks for "exact output", paste it verbatim.

3. **Or read `NANOBOT_SKILLS.md`** — Human-readable skill→command reference.

**To run a skill:** Use the `commands` from skills.json. Example: for "arxiv", commands is `["python3 _scripts/arxiv_digest.py"]` → run that.

**org_skill.py** has no `--run` flag. Its valid flags: `--list`, `--daily`, `--weekly`, `--status`, `--logs`. To run other skills, use their command from skills.json directly.
