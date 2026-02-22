"""
Compatibility layer for skill scripts.
Allows running both atomic design system and legacy skill scripts.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_legacy_skill(skill_name: str, args: Optional[List[str]] = None) -> int:
    """
    Run a skill script (looks in both _scripts/ and _org/).

    Args:
        skill_name: Name of the skill script (e.g., "org_skill.py")
        args: Optional arguments to pass

    Returns:
        Exit code from the skill
    """
    vault_root = Path(__file__).parent.parent

    # Look in _scripts/ first, then _org/
    script_path = vault_root / "_scripts" / skill_name
    if not script_path.exists():
        script_path = vault_root / "_org" / skill_name

    if not script_path.exists():
        print(f"Error: Skill not found: {skill_name}")
        return 1

    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    skill_type = "atomic" if "_org" in str(script_path) else "legacy"
    print(f"\nRunning {skill_type} skill: {skill_name}")
    print("=" * 60)

    result = subprocess.run(
        cmd,
        cwd=str(vault_root),
    )

    return result.returncode


def list_legacy_skills() -> List[str]:
    """List all available skill scripts (both legacy and atomic)."""
    vault_root = Path(__file__).parent.parent

    skills = []

    # Legacy skills in _scripts/
    scripts_dir = vault_root / "_scripts"
    for file in scripts_dir.glob("*_skill.py"):
        skills.append(file.name)

    # Atomic skills in _org/
    org_dir = vault_root / "_org"
    for file in org_dir.glob("*_skill.py"):
        skills.append(file.name)

    return sorted(skills)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Skill Runner (Legacy + Atomic)")
        print("=" * 40)
        print("\nAvailable skills:")
        for skill in list_legacy_skills():
            print(f"  - {skill}")
        print("\nUsage:")
        print("  python _org/compatibility.py <skill_name> [args...]")
        sys.exit(1)

    skill_name = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else None

    sys.exit(run_legacy_skill(skill_name, args))
