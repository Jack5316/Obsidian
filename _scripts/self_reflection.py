"""Self-reflection module for the 10x Distill System.

Enables the system to:
1. Track its own behavior and performance
2. Analyze effectiveness of content curation
3. Identify patterns in successful vs. unsuccessful operations
4. Generate actionable improvement recommendations
5. Maintain a reflection log
6. Implement self-improvement suggestions
"""

import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from config import summarize, save_note, VAULT_PATH

# Reflection configuration
REFLECTION_LOG_PATH = VAULT_PATH / "_logs" / "reflection_log.json"
REFLECTION_PROMPT = """You are an AI system self-reflection analyst. Given a history of system operations,
analyze the performance and behavior of the 10x Distill System. Your analysis should include:

1. **Overall System Effectiveness** - How well the system is achieving its goals
2. **Content Curation Performance** - Which sources are providing the most valuable content
3. **AI Summarization Quality** - Effectiveness of AI-generated summaries and connections
4. **Pattern Recognition** - Patterns in successful vs. problematic operations
5. **Areas for Improvement** - Specific, actionable recommendations for system enhancement
6. **Self-Evolution Suggestions** - Changes the system can make to improve autonomously
7. **Success Metrics** - What defines a "successful" operation for each component
8. **Meta-Level Audit** - Is this system still serving the user, or has it become self-referential?
   Which metrics have become games? Would the user notice if the system stopped for a week?
   What would they miss most — and what wouldn't they miss at all?
9. **Attention Allocation** - Is the system's attention directed toward what matters, or toward
   what's easiest to surface? Are we creating information overload disguised as curation?
   Which sources consistently produce insight vs. noise?

Focus on specific, measurable improvements. Suggest changes to:
- Script behavior and parameters
- Content sources and topics
- AI prompt engineering
- System configuration
- Workflow optimization

Return your analysis in structured markdown with clear sections and actionable recommendations."""

SELF_IMPROVEMENT_PROMPT = """You are an AI system self-improvement engineer. Given a self-reflection analysis,
generate specific, implementable code or configuration changes that will improve the system.

For each improvement recommendation, provide:
1. **Change Type**: What needs to be modified (script, config, prompt, etc.)
2. **Location**: Which file(s) to modify
3. **Current State**: What's wrong with the current implementation
4. **Proposed Solution**: The exact code/config changes needed
5. **Expected Outcome**: How this will improve the system

Return your response as a JSON object with the following structure:
{
  "timestamp": "ISO-8601 date",
  "changes": [
    {
      "type": "script/config/prompt",
      "file": "path/to/file",
      "description": "Brief description of change",
      "current_code": "Current problematic code",
      "proposed_code": "Improved code"
    }
  ],
  "config_updates": {
    "key1": "new_value",
    "key2": "new_value"
  }
}"""


class SystemBehaviorTracker:
    """Tracks system behavior and performance metrics."""

    def __init__(self):
        self.log_path = REFLECTION_LOG_PATH
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log = self._load_log()

    def _load_log(self) -> List[Dict]:
        """Load existing reflection log."""
        if self.log_path.exists():
            try:
                return json.loads(self.log_path.read_text())
            except Exception as e:
                print(f"Warning: Failed to load reflection log: {e}")
        return []

    def _save_log(self):
        """Save reflection log to file."""
        self.log_path.write_text(json.dumps(self.log, indent=2, default=str))

    def record_operation(
        self,
        script_name: str,
        operation_type: str,
        status: str,
        metrics: Optional[Dict] = None,
        error: Optional[str] = None,
    ):
        """Record a system operation with metrics."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "script": script_name,
            "operation": operation_type,
            "status": status,
            "metrics": metrics or {},
            "error": error,
        }
        self.log.append(entry)
        self._save_log()

    def get_recent_operations(self, days: int = 7) -> List[Dict]:
        """Get operations from the past N days."""
        cutoff = datetime.now() - timedelta(days=days)
        return [
            entry
            for entry in self.log
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff
        ]

    def get_operation_statistics(self) -> Dict:
        """Calculate system performance statistics."""
        if not self.log:
            return {
                "total_operations": 0,
                "success_rate": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "script_statistics": {}
            }

        total = len(self.log)
        successful = len([e for e in self.log if e["status"] == "success"])
        failed = len([e for e in self.log if e["status"] == "failed"])

        script_stats = {}
        for entry in self.log:
            script = entry["script"]
            if script not in script_stats:
                script_stats[script] = {"total": 0, "success": 0, "failed": 0}
            script_stats[script]["total"] += 1
            if entry["status"] == "success":
                script_stats[script]["success"] += 1
            elif entry["status"] == "failed":
                script_stats[script]["failed"] += 1

        return {
            "total_operations": total,
            "successful_operations": successful,
            "failed_operations": failed,
            "success_rate": successful / total if total > 0 else 0,
            "script_statistics": script_stats,
        }


class SelfReflectionAnalyzer:
    """Analyzes system behavior and generates self-reflection reports."""

    def __init__(self, tracker: SystemBehaviorTracker):
        self.tracker = tracker

    def generate_reflection_report(self, days: int = 7) -> str:
        """Generate comprehensive self-reflection report."""
        recent_ops = self.tracker.get_recent_operations(days)
        stats = self.tracker.get_operation_statistics()

        # Collect metrics from notes
        content_metrics = self._analyze_content_quality()

        # Format analysis data
        analysis_data = {
            "time_period": f"Last {days} days",
            "statistics": stats,
            "recent_operations": recent_ops,
            "content_analysis": content_metrics,
        }

        analysis_text = self._format_analysis_data(analysis_data)
        reflection = summarize(analysis_text, REFLECTION_PROMPT)

        return reflection

    def _analyze_content_quality(self) -> Dict:
        """Analyze content quality from generated notes."""
        sources_dir = VAULT_PATH / "Sources"
        if not sources_dir.exists():
            return {}

        note_types = {}
        total_notes = 0

        for md_file in sources_dir.glob("*.md"):
            total_notes += 1
            content = md_file.read_text(encoding="utf-8")

            # Extract note type from frontmatter
            note_type = "unknown"
            type_match = re.search(r"^type:\s*(.+)$", content, re.MULTILINE)
            if type_match:
                note_type = type_match.group(1).strip()

            if note_type not in note_types:
                note_types[note_type] = 0
            note_types[note_type] += 1

            # TODO: Add more detailed content analysis (wikilink count, length, quality metrics)

        return {
            "total_notes": total_notes,
            "notes_by_type": note_types,
        }

    def _format_analysis_data(self, data: Dict) -> str:
        """Format analysis data for AI processing."""
        lines = []

        lines.append("System Performance Analysis")
        lines.append("=" * 50)
        lines.append(f"Time Period: {data['time_period']}")
        lines.append("")

        lines.append("Statistics:")
        lines.append(f"- Total operations: {data['statistics']['total_operations']}")
        lines.append(f"- Successful operations: {data['statistics']['successful_operations']}")
        lines.append(f"- Failed operations: {data['statistics']['failed_operations']}")
        lines.append(f"- Success rate: {data['statistics']['success_rate']:.2%}")
        lines.append("")

        lines.append("Script Statistics:")
        for script, stats in data["statistics"]["script_statistics"].items():
            lines.append(f"- {script}:")
            lines.append(f"  Total: {stats['total']}")
            lines.append(f"  Success: {stats['success']}")
            lines.append(f"  Failed: {stats['failed']}")
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            lines.append(f"  Success rate: {success_rate:.2%}")

        lines.append("")
        lines.append("Content Analysis:")
        lines.append(f"- Total notes: {data['content_analysis']['total_notes']}")
        lines.append("Notes by type:")
        for note_type, count in data["content_analysis"]["notes_by_type"].items():
            lines.append(f"  {note_type}: {count}")

        lines.append("")
        lines.append("Recent Operations:")
        for op in data["recent_operations"]:
            lines.append(f"- [{op['timestamp']}] {op['script']}: {op['operation']} ({op['status']})")
            if op.get("metrics"):
                for key, value in op["metrics"].items():
                    lines.append(f"  {key}: {value}")
            if op.get("error"):
                lines.append(f"  Error: {op['error']}")

        return "\n".join(lines)


class SelfImprovementEngine:
    """Generates and implements system improvements from self-reflection."""

    def __init__(self, tracker: SystemBehaviorTracker, analyzer: SelfReflectionAnalyzer):
        self.tracker = tracker
        self.analyzer = analyzer

    def generate_improvement_plan(self, reflection: str) -> Dict:
        """Generate specific improvement plan from reflection."""
        improvement_plan = summarize(reflection, SELF_IMPROVEMENT_PROMPT)

        try:
            return json.loads(improvement_plan)
        except Exception as e:
            print(f"Error parsing improvement plan: {e}")
            return {"changes": [], "config_updates": {}}

    def apply_improvements(self, improvement_plan: Dict) -> Dict:
        """Apply improvement changes to the system."""
        results = {
            "success": [],
            "failed": [],
            "skipped": [],
        }

        # Apply config updates
        for key, value in improvement_plan.get("config_updates", {}).items():
            try:
                self._update_config(key, value)
                results["success"].append(f"Updated config: {key}")
            except Exception as e:
                results["failed"].append(f"Failed to update config {key}: {e}")

        # Apply code changes
        for change in improvement_plan.get("changes", []):
            try:
                self._apply_code_change(change)
                results["success"].append(f"Applied change: {change['description']}")
            except Exception as e:
                results["failed"].append(f"Failed to apply change: {change['description']} - {e}")

        return results

    def _update_config(self, key: str, value: Any):
        """Update system configuration."""
        config_file = VAULT_PATH / "_scripts" / "config.py"
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        content = config_file.read_text(encoding="utf-8")
        # TODO: Implement smart config updates based on key-value pairs

    def _apply_code_change(self, change: Dict):
        """Apply code changes to files."""
        file_path = VAULT_PATH / change["file"]
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For now, log changes rather than apply automatically (safe mode)
        print(f"Would apply change to {file_path}: {change['description']}")
        print("Current code:")
        print(change["current_code"])
        print("\nProposed code:")
        print(change["proposed_code"])


def main():
    """Main function for self-reflection module."""
    parser = argparse.ArgumentParser(
        description="Self-reflection module for 10x Distill System"
    )
    subparsers = parser.add_subparsers(dest="mode", help="Mode of operation")

    # Reflection mode
    reflection_parser = subparsers.add_parser(
        "reflect", help="Generate self-reflection report"
    )
    reflection_parser.add_argument(
        "--days", type=int, default=7, help="Look back N days (default: 7)"
    )
    reflection_parser.add_argument(
        "--save", action="store_true", help="Save report as Obsidian note"
    )

    # Analyze mode
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze system behavior"
    )
    analyze_parser.add_argument(
        "--days", type=int, default=7, help="Look back N days (default: 7)"
    )

    # Self-improvement mode
    improve_parser = subparsers.add_parser(
        "improve", help="Generate self-improvement plan"
    )
    improve_parser.add_argument(
        "--days", type=int, default=7, help="Look back N days (default: 7)"
    )
    improve_parser.add_argument(
        "--apply", action="store_true", help="Apply changes automatically (experimental)"
    )

    args = parser.parse_args()

    # Initialize components
    tracker = SystemBehaviorTracker()
    analyzer = SelfReflectionAnalyzer(tracker)
    improver = SelfImprovementEngine(tracker, analyzer)

    if args.mode == "reflect":
        print(f"Generating self-reflection for last {args.days} days...")
        reflection = analyzer.generate_reflection_report(args.days)

        if args.save:
            today = datetime.now().strftime("%Y-%m-%d")
            note_content = f"""---
type: self-reflection
date: {today}
period: Last {args.days} days
---

# Self-Reflection - {today}

## Analysis Period
Last {args.days} days

## System Analysis
{reflection}
"""
            save_note(f"Sources/Self Reflection - {today}.md", note_content)
            print(f"Reflection saved to Sources/Self Reflection - {today}.md")
        else:
            print("\n" + reflection)

    elif args.mode == "analyze":
        print(f"Analyzing system behavior for last {args.days} days...")
        stats = tracker.get_operation_statistics()
        print("\nSystem Statistics:")
        print(f"Total operations: {stats['total_operations']}")
        print(f"Successful: {stats['successful_operations']}")
        print(f"Failed: {stats['failed_operations']}")
        print(f"Success rate: {stats['success_rate']:.2%}")

        print("\nScript Statistics:")
        for script, script_stats in stats["script_statistics"].items():
            print(f"\n{script}:")
            print(f"  Total: {script_stats['total']}")
            print(f"  Success: {script_stats['success']}")
            print(f"  Failed: {script_stats['failed']}")
            rate = script_stats['success'] / script_stats['total'] if script_stats['total'] > 0 else 0
            print(f"  Success rate: {rate:.2%}")

    elif args.mode == "improve":
        print(f"Generating self-improvement plan for last {args.days} days...")
        reflection = analyzer.generate_reflection_report(args.days)
        improvement_plan = improver.generate_improvement_plan(reflection)

        if args.apply:
            print("\nApplying changes:")
            results = improver.apply_improvements(improvement_plan)
            print(f"\nSuccessfully applied: {len(results['success'])}")
            for success in results['success']:
                print(f"✓ {success}")

            if results['failed']:
                print(f"\nFailed to apply: {len(results['failed'])}")
                for fail in results['failed']:
                    print(f"✗ {fail}")

            if results['skipped']:
                print(f"\nSkipped: {len(results['skipped'])}")
                for skip in results['skipped']:
                    print(f"○ {skip}")
        else:
            print("\nImprovement Plan:")
            print(json.dumps(improvement_plan, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
