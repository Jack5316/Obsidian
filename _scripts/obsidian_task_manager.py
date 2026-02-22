"""Obsidian Task Manager - Comprehensive task management using Obsidian CLI.

This skill provides powerful task management capabilities including:
- Listing and filtering tasks by status
- Task statistics and completion rates
- Daily task management integration
- Prioritization and organization
- Task summaries and reports
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH
from obsidian_cli import get_cli


class TaskManager:
    """Task management engine using Obsidian CLI."""
    
    def __init__(self):
        self.cli = get_cli()
    
    def get_all_tasks(self, verbose: bool = True) -> List[Dict[str, Any]]:
        """Get all tasks with parsing."""
        if verbose:
            print("Fetching all tasks...")
        
        task_lines = self.cli.list_tasks(all=True, verbose=True)
        return self._parse_tasks(task_lines)
    
    def get_todo_tasks(self) -> List[Dict[str, Any]]:
        """Get pending tasks."""
        print("Fetching todo tasks...")
        task_lines = self.cli.list_tasks(todo=True)
        return self._parse_tasks(task_lines)
    
    def get_done_tasks(self) -> List[Dict[str, Any]]:
        """Get completed tasks."""
        print("Fetching done tasks...")
        task_lines = self.cli.list_tasks(done=True)
        return self._parse_tasks(task_lines)
    
    def get_daily_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks from daily notes."""
        print("Fetching daily tasks...")
        task_lines = self.cli.list_tasks(daily=True)
        return self._parse_tasks(task_lines)
    
    def _parse_tasks(self, task_lines: List[str]) -> List[Dict[str, Any]]:
        """Parse raw task lines into structured data."""
        tasks = []
        
        for line in task_lines:
            if not line.strip():
                continue
            
            task = {
                "raw": line,
                "status": "unknown",
                "content": line.strip(),
                "priority": 0,
                "tags": [],
                "due_date": None,
                "file": None,
                "line": None
            }
            
            # Check for task status markers
            if line.strip().startswith("- [ ]"):
                task["status"] = "todo"
                task["content"] = line.replace("- [ ]", "", 1).strip()
            elif line.strip().startswith("- [x]") or line.strip().startswith("- [X]"):
                task["status"] = "done"
                task["content"] = line.replace("- [x]", "", 1).replace("- [X]", "", 1).strip()
            elif line.strip().startswith("- [/]"):
                task["status"] = "in_progress"
                task["content"] = line.replace("- [/]", "", 1).strip()
            
            # Extract tags
            import re
            tags = re.findall(r'#(\w+)', task["content"])
            task["tags"] = tags
            
            # Check for priority markers
            if "🔴" in task["content"] or "P1" in task["content"]:
                task["priority"] = 3
            elif "🟡" in task["content"] or "P2" in task["content"]:
                task["priority"] = 2
            elif "🟢" in task["content"] or "P3" in task["content"]:
                task["priority"] = 1
            
            # Try to extract file path if present
            if ":" in line and not line.startswith("-"):
                parts = line.split(":", 2)
                if len(parts) >= 2:
                    task["file"] = parts[0].strip()
                    if parts[1].strip().isdigit():
                        task["line"] = int(parts[1].strip())
                        if len(parts) > 2:
                            task["content"] = parts[2].strip()
            
            tasks.append(task)
        
        return tasks
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get comprehensive task statistics."""
        print("Calculating task statistics...")
        
        all_tasks = self.get_all_tasks(verbose=False)
        todo_tasks = [t for t in all_tasks if t["status"] == "todo"]
        done_tasks = [t for t in all_tasks if t["status"] == "done"]
        in_progress = [t for t in all_tasks if t["status"] == "in_progress"]
        
        # Tag analysis
        tag_counts = defaultdict(int)
        for task in all_tasks:
            for tag in task["tags"]:
                tag_counts[tag] += 1
        
        # Priority analysis
        priority_counts = defaultdict(int)
        for task in all_tasks:
            priority_counts[task["priority"]] += 1
        
        return {
            "total": len(all_tasks),
            "todo": len(todo_tasks),
            "done": len(done_tasks),
            "in_progress": len(in_progress),
            "completion_rate": len(done_tasks) / max(len(all_tasks), 1) * 100,
            "by_tag": dict(tag_counts),
            "by_priority": dict(priority_counts),
            "all_tasks": all_tasks,
            "todo_tasks": todo_tasks,
            "done_tasks": done_tasks
        }
    
    def append_to_daily_note(self, content: str, inline: bool = False) -> bool:
        """Append task or content to daily note."""
        return self.cli.append_to_daily(content, inline=inline)
    
    def prepend_to_daily_note(self, content: str, inline: bool = False) -> bool:
        """Prepend task or content to daily note."""
        return self.cli.prepend_to_daily(content, inline=inline)
    
    def get_daily_note_content(self) -> Optional[str]:
        """Get current daily note content."""
        return self.cli.read_daily_note()
    
    def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        """Search for tasks containing specific text."""
        print(f"Searching tasks for: {query}")
        all_tasks = self.get_all_tasks(verbose=False)
        return [t for t in all_tasks if query.lower() in t["content"].lower()]
    
    def get_high_priority_tasks(self) -> List[Dict[str, Any]]:
        """Get high priority tasks."""
        all_tasks = self.get_all_tasks(verbose=False)
        high_priority = [t for t in all_tasks if t["priority"] >= 2 and t["status"] == "todo"]
        return sorted(high_priority, key=lambda x: -x["priority"])


def format_task_report(stats: Dict[str, Any]) -> str:
    """Format task statistics as a markdown report."""
    
    md = f"""# Obsidian Task Manager Report

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Task Overview

| Metric | Count |
|--------|-------|
| Total Tasks | {stats['total']} |
| ✅ Done | {stats['done']} |
| 🔄 In Progress | {stats['in_progress']} |
| ⏳ Todo | {stats['todo']} |
| **Completion Rate** | **{stats['completion_rate']:.1f}%** |

---

## 🎯 Todo Tasks (Priority Sorted)
"""
    
    # Sort todo tasks by priority
    sorted_todos = sorted(stats['todo_tasks'], key=lambda x: (-x['priority'], x['content']))
    
    for i, task in enumerate(sorted_todos[:20], 1):
        priority_icon = "🔴" if task['priority'] >= 3 else "🟡" if task['priority'] >= 2 else "🟢" if task['priority'] >= 1 else ""
        md += f"{i}. {priority_icon} {task['content']}\n"
    
    if len(sorted_todos) > 20:
        md += f"\n... and {len(sorted_todos) - 20} more todo tasks\n"
    
    md += """
---

## 🏷️ Tasks by Tag
"""
    
    for tag, count in sorted(stats['by_tag'].items(), key=lambda x: -x[1])[:10]:
        md += f"- #{tag}: {count} tasks\n"
    
    md += """
---

## 📈 Recently Completed
"""
    
    for i, task in enumerate(stats['done_tasks'][-15:], 1):
        md += f"{i}. ✅ {task['content']}\n"
    
    md += """
---

## 💡 Task Management Tips

1. **Prioritize**: Focus on high-priority (🔴) tasks first
2. **Daily Review**: Check your daily note for upcoming tasks
3. **Tag Organization**: Use consistent tags for better filtering
4. **Status Updates**: Mark tasks as in-progress or completed regularly

---

*Report generated by Obsidian Task Manager Skill*
"""
    
    return md


def format_task_list(tasks: List[Dict[str, Any]], title: str = "Tasks") -> str:
    """Format a simple task list."""
    output = f"# {title}\n\n"
    
    for i, task in enumerate(tasks, 1):
        status_icon = "✅" if task["status"] == "done" else "🔄" if task["status"] == "in_progress" else "⏳"
        priority_icon = "🔴" if task['priority'] >= 3 else "🟡" if task['priority'] >= 2 else "🟢" if task['priority'] >= 1 else ""
        output += f"{i}. {status_icon} {priority_icon} {task['content']}\n"
    
    return output


def main():
    """Main function for task management."""
    parser = argparse.ArgumentParser(
        description="Obsidian Task Manager - Comprehensive task management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill obsidian-task-manager                    # Show full task report
  /skill obsidian-task-manager --todo             # Show only todo tasks
  /skill obsidian-task-manager --done             # Show completed tasks
  /skill obsidian-task-manager --daily            # Show daily tasks
  /skill obsidian-task-manager --priority         # Show high-priority tasks
  /skill obsidian-task-manager --search "project" # Search tasks
  /skill obsidian-task-manager --add "New task"   # Add task to daily note
  /skill obsidian-task-manager --save             # Save report to vault
"""
    )
    
    parser.add_argument(
        "--todo",
        action="store_true",
        help="Show only todo tasks"
    )
    
    parser.add_argument(
        "--done",
        action="store_true",
        help="Show only done tasks"
    )
    
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Show daily tasks"
    )
    
    parser.add_argument(
        "--priority",
        action="store_true",
        help="Show high-priority tasks"
    )
    
    parser.add_argument(
        "--search",
        type=str,
        help="Search tasks containing text"
    )
    
    parser.add_argument(
        "--add",
        type=str,
        help="Add task to daily note"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to vault"
    )
    
    args = parser.parse_args()
    
    manager = TaskManager()
    
    # Handle different modes
    if args.add:
        # Add task to daily note
        task_content = f"- [ ] {args.add}"
        success = manager.append_to_daily_note(task_content)
        if success:
            print(f"✓ Task added to daily note: {args.add}")
        else:
            print("✗ Failed to add task")
        return
    
    if args.todo:
        tasks = manager.get_todo_tasks()
        print(format_task_list(tasks, "Todo Tasks"))
        return
    
    if args.done:
        tasks = manager.get_done_tasks()
        print(format_task_list(tasks, "Completed Tasks"))
        return
    
    if args.daily:
        tasks = manager.get_daily_tasks()
        print(format_task_list(tasks, "Daily Tasks"))
        return
    
    if args.priority:
        tasks = manager.get_high_priority_tasks()
        print(format_task_list(tasks, "High Priority Tasks"))
        return
    
    if args.search:
        tasks = manager.search_tasks(args.search)
        print(format_task_list(tasks, f"Tasks containing: {args.search}"))
        return
    
    # Default: show full report
    stats = manager.get_task_statistics()
    report = format_task_report(stats)
    print(report)
    
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_path = f"Sources/Task Manager Report - {date_str}.md"
        save_note(save_path, report)
        print(f"\n✓ Report saved to: {save_path}")


if __name__ == "__main__":
    main()
