#!/usr/bin/env python3
"""
Example usage of the atomic design automation system.
Run this file to see various usage patterns.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from _org import DailyWorkflow, WeeklyWorkflow, CustomWorkflow
from _org import VaultConfig, ScriptRegistry


def example_1_list_scripts():
    """Example 1: List all available scripts."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: List Available Scripts")
    print("=" * 60)

    config = VaultConfig()
    registry = ScriptRegistry(config.scripts_dir)

    print("\nAll scripts:")
    for script in registry.list_scripts():
        print(f"  - {script.name}: {script.description}")

    print("\nBy category:")
    categorized = registry.get_by_category()
    for category, scripts in categorized.items():
        print(f"\n  {category.value}:")
        for script in scripts:
            print(f"    - {script.name}")


def example_2_daily_workflow():
    """Example 2: Run daily workflow (demonstration only)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Daily Workflow")
    print("=" * 60)
    print("\nTo run the actual daily workflow:")
    print("  python _org/run.py daily")
    print("\nOr for quick mode:")
    print("  python _org/run.py daily-quick")


def example_3_weekly_workflow():
    """Example 3: Run weekly workflow (demonstration only)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Weekly Workflow")
    print("=" * 60)
    print("\nTo run the actual weekly workflow:")
    print("  python _org/run.py weekly")
    print("\nOr for synthesis only:")
    print("  python _org/run.py weekly-synth")


def example_4_custom_workflow():
    """Example 4: Build a custom workflow."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Custom Workflow")
    print("=" * 60)
    print("\nCustom workflow code example:")
    print("""
from _org import CustomWorkflow

# Create custom workflow
workflow = CustomWorkflow()

# Add phases
workflow.add_phase_by_category("News Ingestion", "content_digest")
workflow.add_phase_by_tags("Analysis", ["reflection", "evolution"])
workflow.add_phase_by_tags("Enhancement", ["insights"])

# Run it
results = workflow.run("My Research Workflow")
""")


def example_5_skip_scripts():
    """Example 5: Skipping scripts."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Skipping Scripts")
    print("=" * 60)
    print("\nSkip specific scripts from command line:")
    print("  python _org/run.py daily --skip twitter_capture.py,reddit_digest.py")
    print("\nOr programmatically:")
    print("""
from _org import DailyWorkflow

workflow = DailyWorkflow()
results = workflow.run(
    skip_digestion=False,
    skip_analysis=False,
    skip_scripts=["twitter_capture.py", "reddit_digest.py"]
)
""")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("AI VAULT AUTOMATION - EXAMPLES")
    print("=" * 60)

    example_1_list_scripts()
    example_2_daily_workflow()
    example_3_weekly_workflow()
    example_4_custom_workflow()
    example_5_skip_scripts()

    print("\n" + "=" * 60)
    print("For more information, see _org/README.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
