#!/usr/bin/env python3
"""Gateway - Skill map and integration guide.

Tracks existing skills, their relationships, and how to integrate new skills.
For each skill clarifies: Functions, Connections, Limitations, Guidance (FCLG).
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from config import summarize, save_note, VAULT_PATH

VAULT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_JSON = VAULT_ROOT / ".claude" / "skills.json"
SKILLS_DIR = VAULT_ROOT / ".claude" / "skills"
PIPELINES_JSON = VAULT_ROOT / "_config" / "pipelines.json"


def load_skills() -> Dict[str, dict]:
    """Load skills from skills.json."""
    if not SKILLS_JSON.exists():
        return {}
    data = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    return data.get("skills", {})


def load_pipelines() -> Dict[str, List[str]]:
    """Load named pipelines."""
    if not PIPELINES_JSON.exists():
        return {}
    try:
        return json.loads(PIPELINES_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_skill_md(skill_name: str) -> str:
    """Load SKILL.md content for a skill (first 800 chars)."""
    for pattern in [skill_name, skill_name.replace("_", "-")]:
        path = SKILLS_DIR / pattern / "SKILL.md"
        if path.exists():
            return path.read_text(encoding="utf-8")[:800]
    return ""


def build_pipeline_graph(pipelines: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Build skill -> [skills it connects to in pipelines]."""
    graph = {}
    for pipe_name, steps in pipelines.items():
        for i, skill in enumerate(steps):
            if skill not in graph:
                graph[skill] = []
            # Connect to next in pipeline
            if i + 1 < len(steps):
                if steps[i + 1] not in graph[skill]:
                    graph[skill].append(steps[i + 1])
            # Connect to pipeline name
            graph[skill].append(f"[pipeline:{pipe_name}]")
    return graph


def build_skill_registry(skills: Dict, pipelines: Dict) -> str:
    """Build a compact registry for AI context."""
    graph = build_pipeline_graph(pipelines)
    lines = []
    for name, meta in sorted(skills.items()):
        desc = (meta.get("description") or "")[:200]
        cmds = meta.get("commands") or []
        has_script = any("python3" in c for c in cmds) if cmds else False
        connections = list(set(graph.get(name, [])))
        skill_md = load_skill_md(name)[:300]
        lines.append(f"## {name}")
        lines.append(f"Description: {desc}")
        lines.append(f"Has script: {has_script}")
        lines.append(f"Connections: {', '.join(connections) if connections else 'none'}")
        lines.append(f"SKILL excerpt: {skill_md[:200]}...")
        lines.append("")
    return "\n".join(lines)


MAP_PROMPT = """You are the Gateway for a Personal AI Infrastructure (PAI) skill system. The user has many skills (Python scripts + AI) organized in an Obsidian vault.

Given the skill registry below, produce a **Skill Gateway Map** — a navigable document that helps the user understand and use their skills effectively.

For EACH skill, provide exactly these four sections in this format:

### [[skill-name]]
- **Functions**: What it does (1-3 bullet points)
- **Connections**: Which skills it connects to, pipelines it's in, workflows (comma-separated or list)
- **Limitations**: What it cannot do, constraints, when NOT to use it (1-2 points)
- **Guidance**: How to use it, when to use it, best practices, shortcuts (1-2 points)

Organize skills into logical categories (e.g., Orchestration, Content Curation, Knowledge Retrieval, Thinking & Reasoning, Self-Improvement, Obsidian & Vault, Publishing, Discovery, Capture, etc.). Use your judgment.

Start with:
1. **Overview** — 2-3 paragraphs on the skill ecosystem and how to navigate it
2. **Quick Reference** — Table: Skill | Category | One-line function
3. **Full Map** — Categories with each skill's FCLG (Functions, Connections, Limitations, Guidance)
4. **Common Workflows** — 3-5 suggested pipelines or skill combinations

Use [[wikilinks]] for skill names so they link in Obsidian. No YAML frontmatter. Be concise but actionable."""


SKILL_PROMPT = """You are the Gateway for a Personal AI Infrastructure. Analyze this single skill in depth.

For the skill "{skill_name}", provide:

1. **Functions** — What it does (3-5 bullet points, specific and actionable)
2. **Connections** — Which other skills it connects to, why, and how (pipelines, workflows, data flow)
3. **Limitations** — What it cannot do, constraints, edge cases, when NOT to use it
4. **Guidance** — How to use it effectively: when to use it, best practices, common pitfalls, shortcuts

Be specific. Reference actual skill names with [[wikilinks]]. No YAML frontmatter."""


INTEGRATE_PROMPT = """You are the Gateway for a Personal AI Infrastructure. The user is creating or has created a NEW skill and wants to understand how it integrates with existing skills.

**New skill**: {skill_name}
**Description**: {description}

**Existing skills** (excerpt): {registry_excerpt}

Produce an **Integration Guide** for this new skill:

1. **Placement** — Which category does it belong in? What existing skills is it most related to?
2. **Functions** — What it does (clear, specific)
3. **Connections** — Which existing skills it should connect to (and why), suggested pipelines, data flow
4. **Limitations** — What it cannot do, constraints
5. **Guidance** — How to use it, when to use it, how it fits into workflows
6. **Suggested Pipelines** — 1-3 pipeline ideas that include this skill (e.g., "content-to-insight" style)
7. **Registration Checklist** — Reminders: add to skills.json, create SKILL.md, consider adding to org-daily/weekly or a pipeline

Use [[wikilinks]] for skill names. No YAML frontmatter. Be actionable."""


def run_map(skills: Dict, pipelines: Dict, save: bool) -> str:
    """Generate full skill gateway map."""
    registry = build_skill_registry(skills, pipelines)
    # Truncate if too long (keep first ~6000 chars of unique content)
    registry_trimmed = registry[:6000] if len(registry) > 6000 else registry
    if len(registry) > 6000:
        registry_trimmed += "\n\n[Registry truncated for context...]"

    print("Generating Skill Gateway Map...")
    result = summarize(registry_trimmed, MAP_PROMPT)

    today = datetime.now().strftime("%Y-%m-%d")
    doc = f"""# Skill Gateway Map

*Generated {today} · Navigate your PAI skills*

---

{result}

---
*Gateway — Functions, Connections, Limitations, Guidance*
"""
    return doc


def run_skill_deep(skill_name: str, skills: Dict, pipelines: Dict, save: bool) -> str:
    """Deep FCLG analysis for one skill."""
    meta = skills.get(skill_name, {})
    desc = meta.get("description", "")
    skill_md = load_skill_md(skill_name)
    graph = build_pipeline_graph(pipelines)
    connections = graph.get(skill_name, [])

    context = f"""Skill: {skill_name}
Description: {desc}
Connections (from pipelines): {', '.join(connections)}
SKILL.md excerpt:
{skill_md}
"""
    prompt = SKILL_PROMPT.format(skill_name=skill_name)
    print(f"Analyzing {skill_name}...")
    result = summarize(context, prompt)

    doc = f"""# Gateway: {skill_name}

*Deep analysis — Functions, Connections, Limitations, Guidance*

---

{result}

---
*Gateway skill analysis*
"""
    return doc


def run_integrate(skill_name: str, description: str, skills: Dict, pipelines: Dict, save: bool) -> str:
    """Integration analysis for a new skill."""
    registry = build_skill_registry(skills, pipelines)
    registry_excerpt = registry[:4000]

    system_prompt = INTEGRATE_PROMPT.format(
        skill_name=skill_name,
        description=description or "(No description provided)",
        registry_excerpt=registry_excerpt,
    )
    print(f"Analyzing integration for {skill_name}...")
    result = summarize(
        f"Produce the Integration Guide for new skill: {skill_name}",
        system_prompt,
    )

    doc = f"""# Gateway: Integration — {skill_name}

*How this new skill fits into your PAI*

---

{result}

---
*Gateway integration analysis*
"""
    return doc


def main():
    parser = argparse.ArgumentParser(
        description="Gateway — Skill map and integration guide",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/gateway.py                    # Full skill map
  python3 _scripts/gateway.py --skill rag       # Deep dive on one skill
  python3 _scripts/gateway.py --integrate my-skill "Description"  # New skill integration
  python3 _scripts/gateway.py --save            # Save map to Maps/
""",
    )
    parser.add_argument(
        "--skill", "-s",
        type=str,
        metavar="NAME",
        help="Deep FCLG analysis for one skill",
    )
    parser.add_argument(
        "--integrate", "-i",
        type=str,
        nargs="+",
        metavar=("NAME", "DESCRIPTION..."),
        help="Integration analysis for a new skill (description can be multiple words)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to vault (Maps/Skill Gateway.md or Maps/Gateway - SKILL.md)",
    )
    args = parser.parse_args()

    skills = load_skills()
    pipelines = load_pipelines()

    if not skills:
        print("No skills found in skills.json.")
        return 1

    doc = ""
    if args.integrate:
        skill_name = args.integrate[0]
        desc = " ".join(args.integrate[1:]) if len(args.integrate) > 1 else ""
        doc = run_integrate(skill_name, desc, skills, pipelines, args.save)
        save_path = f"Maps/Gateway - Integration - {skill_name}.md"
    elif args.skill:
        doc = run_skill_deep(args.skill, skills, pipelines, args.save)
        save_path = f"Maps/Gateway - {args.skill}.md"
    else:
        doc = run_map(skills, pipelines, args.save)
        save_path = "Maps/Skill Gateway.md"

    print()
    print("—" * 50)
    print(doc[:2000])
    if len(doc) > 2000:
        print("...")
        print(f"[Full output: {len(doc)} chars]")
    print("—" * 50)

    if args.save:
        save_note(save_path, doc)
        print(f"\nSaved: {save_path}")

    return 0


if __name__ == "__main__":
    exit(main())
