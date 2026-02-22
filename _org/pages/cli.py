"""CLI interface for the atomic design automation system."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..templates import DailyWorkflow, WeeklyWorkflow, CustomWorkflow
from ..molecules import ScriptRegistry
from ..atoms import VaultConfig
from ..compatibility import run_legacy_skill, list_legacy_skills


def list_commands():
    """List all available commands."""
    print("""
AI Vault Automation - Atomic Design System
===========================================

Available Commands:
------------------

Workflows:
  daily          - Run daily workflow (digestion + light analysis)
  daily-quick    - Run quick daily (only news digestion)
  weekly         - Run weekly workflow (full)
  weekly-synth   - Run weekly synthesis only

Skills (Legacy Wrappers):
  skill list     - List all available skill wrappers
  skill org      - Run organization skill (all scripts)
  skill tophub   - Run TopHub news skill
  skill tophub-simple - Run simple TopHub skill with AI summaries

Listing & Discovery:
  list           - List all available scripts
  list-categories - List scripts by category
  list-tags      - List scripts by tags

Custom Execution:
  run <script>   - Run a specific script
  run-multiple <s1,s2,...> - Run multiple specific scripts

Examples:
  python -m _org.pages.cli daily
  python -m _org.pages.cli weekly
  python -m _org.pages.cli list
  python -m _org.pages.cli skill org
  python -m _org.pages.cli skill tophub
""")


def list_scripts():
    """List all available scripts."""
    config = VaultConfig()
    registry = ScriptRegistry(config.scripts_dir)
    scripts = registry.list_scripts()

    print("\nAvailable Scripts:")
    print("=" * 80)
    for script in scripts:
        status = "✓" if script.recommended else "○"
        requires = " (requires args)" if script.requires_args else ""
        print(f"{status} {script.name:<25} - {script.description}{requires}")
        if script.tags:
            print(f"{' ':28} Tags: {', '.join(script.tags)}")


def list_categories():
    """List scripts organized by category."""
    config = VaultConfig()
    registry = ScriptRegistry(config.scripts_dir)
    categorized = registry.get_by_category()

    print("\nScripts by Category:")
    print("=" * 80)

    for category, scripts in categorized.items():
        print(f"\n{category.value.upper()}:")
        print("-" * 40)
        for script in scripts:
            status = "✓" if script.recommended else "○"
            requires = " (requires args)" if script.requires_args else ""
            print(f"  {status} {script.name:<25} - {script.description}{requires}")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        list_commands()
        return 0

    command = sys.argv[1]
    args = sys.argv[2:]

    # Check for help
    if command == "help":
        list_commands()
        return 0

    # Skill command handling (special case - pass all args)
    if command == "skill":
        if not args:
            print("Available skills:")
            for skill in list_legacy_skills():
                print(f"  - {skill}")
            print("\nUsage: skill <skill-name> [args...]")
            print("Shortcuts: skill org, skill tophub, skill tophub-simple")
            return 0

        skill_cmd = args[0]
        skill_args = args[1:] if len(args) > 1 else []

        # Skill shortcuts
        skill_map = {
            "org": "org_skill.py",
            "atomic-org": "atomic_org_skill.py",
            "daily": "daily_skill.py",
            "weekly": "weekly_skill.py",
            "tophub": "tophub_skill.py",
            "tophub-simple": "tophub_news_simple_skill.py",
            "tophub-detailed": "tophub_news_detailed_skill.py",
        }

        if skill_cmd in skill_map:
            skill_name = skill_map[skill_cmd]
            return run_legacy_skill(skill_name, skill_args)
        elif skill_cmd == "list":
            print("Available skills:")
            for skill in list_legacy_skills():
                print(f"  - {skill}")
            return 0
        else:
            # Try direct skill name
            if skill_cmd.endswith(".py"):
                return run_legacy_skill(skill_cmd, skill_args)
            else:
                print(f"Unknown skill: {skill_cmd}")
                print("Use 'skill list' to see available skills")
                return 1

    # Parse --skip for workflow commands
    skip_list = []
    workflow_args = []
    i = 0
    while i < len(args):
        if args[i] in ("--skip", "-s") and i + 1 < len(args):
            skip_str = args[i + 1]
            skip_list = [s.strip() for s in skip_str.split(",") if s.strip()]
            i += 2
        else:
            workflow_args.append(args[i])
            i += 1

    # Execute other commands
    if command == "daily":
        workflow = DailyWorkflow()
        workflow.run(skip_scripts=skip_list)
        return 0

    elif command == "daily-quick":
        workflow = DailyWorkflow()
        workflow.run_quick(skip_scripts=skip_list)
        return 0

    elif command == "weekly":
        workflow = WeeklyWorkflow()
        workflow.run(skip_scripts=skip_list)
        return 0

    elif command == "weekly-synth":
        workflow = WeeklyWorkflow()
        workflow.run_synthesis_only(skip_scripts=skip_list)
        return 0

    elif command == "list":
        list_scripts()
        return 0

    elif command == "list-categories":
        list_categories()
        return 0

    elif command == "list-tags":
        print("Tag-based listing coming soon!")
        return 0

    elif command == "run":
        if not workflow_args:
            print("Error: Please specify a script to run")
            return 1
        script_name = workflow_args[0]
        print(f"Running single script: {script_name}")
        print("Use 'list' to see available scripts")
        return 0

    else:
        print(f"Unknown command: {command}")
        print("Use 'help' to see available commands")
        return 1


if __name__ == "__main__":
    sys.exit(main())
