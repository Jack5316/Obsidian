#!/usr/bin/env python3
"""Alignment Skill - Update skills in a strategic, reflective, purposeful, and systematic way.

This skill analyzes existing skills through the ALIGNMENT framework:
- **Strategic**: Purpose alignment, PAI framework fit, layer coherence, integration
- **Reflective**: Effectiveness, gaps, what works, improvement opportunities
- **Purposeful**: Clear intent, user value, outcomes, success criteria
- **Systematic**: Completeness, consistency, conventions, documentation

Produces actionable recommendations for skill improvement.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


ALIGNMENT_PROMPT = """You are a skill architect for a Personal AI Infrastructure (PAI) system. Analyze the following skill through the ALIGNMENT framework and produce a structured update plan.

## ALIGNMENT Framework

1. **STRATEGIC** — Purpose and fit
   - Does the skill align with its stated purpose?
   - How does it fit the PAI 5-layer pyramid (L1 Dev Tools, L2 Data, L3 Skills, L4 Scenarios, L5 Review)?
   - Does it integrate well with related skills?
   - Is "scripts before prompts" followed (Python for deterministic tasks, AI only for judgment)?

2. **REFLECTIVE** — Effectiveness and gaps
   - What is working well?
   - What gaps or inconsistencies exist?
   - What edge cases or failure modes are unhandled?
   - What would make this skill more valuable?

3. **PURPOSEFUL** — Intent and outcomes
   - Is the skill's purpose clear to users?
   - What concrete outcomes does it deliver?
   - Are success criteria implicit or explicit?
   - Does the description match actual behavior?

4. **SYSTEMATIC** — Completeness and consistency
   - Does it follow PAI conventions (argparse, config.py, save_note, VAULT_PATH)?
   - Is documentation (SKILL.md) complete and accurate?
   - Are options, examples, and output format documented?
   - Is error handling adequate?

## Output Format

Provide your analysis as structured markdown:

# Alignment Report: [Skill Name]

## Executive Summary
2-3 sentences on overall alignment and top priority.

## Strategic Assessment
- Purpose alignment
- PAI layer fit
- Integration points
- Scripts vs prompts balance

## Reflective Assessment
- Strengths
- Gaps and inconsistencies
- Improvement opportunities

## Purposeful Assessment
- Clarity of intent
- Outcome delivery
- Success criteria

## Systematic Assessment
- Convention compliance
- Documentation completeness
- Error handling

## Recommended Updates (Prioritized)
1. [High] — Specific change with rationale
2. [Medium] — ...
3. [Low] — ...

## Suggested SKILL.md Updates
Concrete edits for the description, features, options, or examples.

## Suggested Script Updates
Concrete code or logic improvements (if applicable).

Be specific and actionable. Reference line numbers or sections when suggesting changes."""


def load_skills_json() -> Dict:
    """Load skills.json."""
    path = VAULT_PATH / ".claude" / "skills.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def skill_name_to_paths(skill_name: str) -> Tuple[Optional[Path], Optional[Path]]:
    """Resolve skill name to script path and SKILL.md path."""
    skill_dir = VAULT_PATH / ".claude" / "skills" / skill_name
    skill_md = skill_dir / "SKILL.md"
    # Infer script name: hyphenated -> snake_case
    script_name = skill_name.replace("-", "_") + ".py"
    script_path = VAULT_PATH / "_scripts" / script_name
    return script_path, skill_md


def get_script_from_skills_json(skill_name: str) -> Optional[str]:
    """Extract script path from skills.json command."""
    skills = load_skills_json()
    skill_data = skills.get("skills", {}).get(skill_name)
    if not skill_data or not skill_data.get("commands"):
        return None
    cmd = skill_data["commands"][0]
    # "python3 _scripts/foo.py" -> _scripts/foo.py
    if "_scripts/" in cmd:
        return cmd.split("_scripts/")[-1].split()[0]
    return None


def load_skill_artifacts(skill_name: str) -> str:
    """Load all artifacts for a skill into a single context string."""
    parts = []
    skills = load_skills_json()
    skill_data = skills.get("skills", {}).get(skill_name, {})

    # skills.json entry
    parts.append("## skills.json entry")
    parts.append(f"```json\n{json.dumps({skill_name: skill_data}, indent=2)}\n```")
    parts.append("")

    # SKILL.md
    script_path, skill_md_path = skill_name_to_paths(skill_name)
    if skill_md_path and skill_md_path.exists():
        parts.append("## SKILL.md")
        parts.append(skill_md_path.read_text(encoding="utf-8"))
        parts.append("")
    else:
        parts.append("## SKILL.md")
        parts.append("(Not found)")
        parts.append("")

    # Python script
    # Prefer path from skills.json if available
    script_from_json = get_script_from_skills_json(skill_name)
    if script_from_json:
        script_path = VAULT_PATH / "_scripts" / script_from_json
    elif not script_path or not script_path.exists():
        script_path = VAULT_PATH / "_scripts" / (skill_name.replace("-", "_") + ".py")

    if script_path and script_path.exists():
        parts.append("## Python script (_scripts/" + script_path.name + ")")
        parts.append("```python")
        parts.append(script_path.read_text(encoding="utf-8"))
        parts.append("```")
    else:
        parts.append("## Python script")
        parts.append("(Not found or no script — skill may be prompt-only)")

    return "\n".join(parts)


def list_available_skills() -> List[str]:
    """List skill names from skills.json."""
    skills = load_skills_json()
    return sorted(skills.get("skills", {}).keys())


def main():
    parser = argparse.ArgumentParser(
        description="Align a skill — strategic, reflective, purposeful, systematic update analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/alignment_skill.py rag              # Analyze RAG skill
  python3 _scripts/alignment_skill.py ai-brief --save  # Analyze and save report
  python3 _scripts/alignment_skill.py --list           # List available skills
""",
    )
    parser.add_argument(
        "skill",
        nargs="?",
        help="Skill name to align (e.g., rag, ai-brief, clean)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available skills",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save alignment report to Sources/Alignment - Skill - YYYY-MM-DD.md",
    )
    parser.add_argument(
        "--context",
        type=str,
        default="",
        help="Additional context for the analysis (e.g., 'User reports slow performance')",
    )

    args = parser.parse_args()

    if args.list:
        skills = list_available_skills()
        print("Available skills:")
        for s in skills:
            print(f"  - {s}")
        return

    if not args.skill:
        parser.error("Skill name required (or use --list to see options)")

    skill_name = args.skill.strip().lower()
    skills = list_available_skills()
    if skill_name not in skills:
        print(f"Skill '{skill_name}' not found in skills.json.")
        print("Available:", ", ".join(skills[:15]) + ("..." if len(skills) > 15 else ""))
        sys.exit(1)

    print(f"Loading artifacts for skill: {skill_name}")
    context = load_skill_artifacts(skill_name)
    if args.context:
        context += f"\n\n## Additional Context\n{args.context}"

    print("Running ALIGNMENT analysis...")
    report = summarize(context, ALIGNMENT_PROMPT)
    print(report)

    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_name = skill_name.replace(" ", "-")
        save_note(f"Sources/Alignment - {safe_name.title()} - {date_str}.md", report)
        print(f"\nSaved: Sources/Alignment - {safe_name.title()} - {date_str}.md")


if __name__ == "__main__":
    main()
