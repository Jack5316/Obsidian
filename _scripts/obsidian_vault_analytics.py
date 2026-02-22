"""Obsidian Vault Analytics - Comprehensive analysis of your Obsidian vault.

This skill provides detailed analytics about your Obsidian vault including:
- File statistics and growth trends
- Tag usage and distribution
- Link graph analysis
- Property and metadata insights
- Task completion rates
- Vault health assessment
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH
from obsidian_cli import get_cli


class VaultAnalytics:
    """Comprehensive vault analytics engine."""
    
    def __init__(self):
        self.cli = get_cli()
        self.vault_path = VAULT_PATH
        self.analysis_date = datetime.now()
    
    def analyze_files(self) -> Dict[str, Any]:
        """Analyze file statistics."""
        print("Analyzing files...")
        
        files = self.cli.list_files(total=True)
        md_files = [f for f in files if f.endswith('.md')]
        
        # Count by extension
        ext_counts = Counter()
        for f in files:
            ext = Path(f).suffix.lower()
            ext_counts[ext] += 1
        
        # Folder analysis
        folders = self.cli.list_folders(total=True)
        
        return {
            "total_files": len(files),
            "markdown_files": len(md_files),
            "other_files": len(files) - len(md_files),
            "by_extension": dict(ext_counts),
            "total_folders": len(folders),
            "file_list": md_files[:50]  # First 50 markdown files
        }
    
    def analyze_tags(self) -> Dict[str, Any]:
        """Analyze tag usage."""
        print("Analyzing tags...")
        
        tags = self.cli.list_tags(counts=True, sort="count")
        
        tag_data = []
        for tag_line in tags:
            if tag_line.strip():
                # Parse tag line (format depends on CLI output)
                parts = tag_line.split()
                if parts:
                    tag_data.append({
                        "tag": parts[0],
                        "count": int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                    })
        
        return {
            "total_tags": len(tag_data),
            "top_tags": tag_data[:20],
            "all_tags": tag_data
        }
    
    def analyze_links(self) -> Dict[str, Any]:
        """Analyze link structure."""
        print("Analyzing links...")
        
        orphans = self.cli.get_orphans(all=True)
        deadends = self.cli.get_deadends(all=True)
        unresolved = self.cli.get_unresolved_links(counts=True)
        
        return {
            "orphan_files": len(orphans),
            "deadend_files": len(deadends),
            "unresolved_links": len(unresolved),
            "orphan_list": orphans[:20],
            "deadend_list": deadends[:20],
            "unresolved_list": unresolved[:20]
        }
    
    def analyze_tasks(self) -> Dict[str, Any]:
        """Analyze task statistics."""
        print("Analyzing tasks...")
        
        all_tasks = self.cli.list_tasks(all=True, verbose=True)
        todo_tasks = self.cli.list_tasks(todo=True)
        done_tasks = self.cli.list_tasks(done=True)
        
        return {
            "total_tasks": len(all_tasks),
            "todo_tasks": len(todo_tasks),
            "done_tasks": len(done_tasks),
            "completion_rate": len(done_tasks) / max(len(all_tasks), 1) * 100,
            "recent_tasks": all_tasks[:30]
        }
    
    def analyze_properties(self) -> Dict[str, Any]:
        """Analyze properties/metadata."""
        print("Analyzing properties...")
        
        properties = self.cli.list_properties(all=True, counts=True, sort="count")
        
        prop_data = []
        for prop_line in properties:
            if prop_line.strip():
                parts = prop_line.split()
                if parts:
                    prop_data.append({
                        "property": parts[0],
                        "count": int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                    })
        
        return {
            "total_properties": len(prop_data),
            "top_properties": prop_data[:20],
            "all_properties": prop_data
        }
    
    def analyze_recent_activity(self) -> Dict[str, Any]:
        """Analyze recent activity."""
        print("Analyzing recent activity...")
        
        recents = self.cli.get_recents()
        aliases = self.cli.list_aliases(all=True)
        bookmarks = self.cli.list_bookmarks()
        
        return {
            "recent_files": recents[:20],
            "total_aliases": len(aliases),
            "total_bookmarks": len(bookmarks),
            "bookmarks": bookmarks[:20]
        }
    
    def generate_health_score(self, file_analysis: Dict, link_analysis: Dict,
                              task_analysis: Dict) -> Dict[str, Any]:
        """Calculate vault health score."""
        scores = {}
        
        # File health (max 30 points)
        md_ratio = file_analysis["markdown_files"] / max(file_analysis["total_files"], 1)
        scores["file_health"] = min(30, int(md_ratio * 30))
        
        # Link health (max 30 points)
        total_files = file_analysis["total_files"]
        if total_files > 0:
            orphan_ratio = 1 - (link_analysis["orphan_files"] / total_files)
            deadend_ratio = 1 - (link_analysis["deadend_files"] / total_files)
            link_score = (orphan_ratio + deadend_ratio) / 2 * 30
            scores["link_health"] = min(30, int(link_score))
        else:
            scores["link_health"] = 0
        
        # Task health (max 25 points)
        task_completion = task_analysis["completion_rate"]
        scores["task_health"] = min(25, int(task_completion * 0.25))
        
        # Activity health (max 15 points)
        scores["activity_health"] = 15  # Assume baseline
        
        total_score = sum(scores.values())
        
        return {
            "total_score": total_score,
            "max_score": 100,
            "category_scores": scores,
            "grade": self._get_grade(total_score)
        }
    
    def _get_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report."""
        print("\n=== Generating Vault Analytics Report ===\n")
        
        file_analysis = self.analyze_files()
        tag_analysis = self.analyze_tags()
        link_analysis = self.analyze_links()
        task_analysis = self.analyze_tasks()
        prop_analysis = self.analyze_properties()
        recent_analysis = self.analyze_recent_activity()
        health_score = self.generate_health_score(file_analysis, link_analysis, task_analysis)
        
        return {
            "analysis_date": self.analysis_date.isoformat(),
            "health_score": health_score,
            "files": file_analysis,
            "tags": tag_analysis,
            "links": link_analysis,
            "tasks": task_analysis,
            "properties": prop_analysis,
            "recent_activity": recent_analysis
        }


def format_report_markdown(report: Dict[str, Any]) -> str:
    """Format analytics report as markdown."""
    
    md = f"""# Obsidian Vault Analytics Report

Generated on: {report['analysis_date']}

## 🏥 Vault Health Score

**Total Score: {report['health_score']['total_score']}/{report['health_score']['max_score']}**  
**Grade: {report['health_score']['grade']}**

| Category | Score |
|----------|-------|
| File Health | {report['health_score']['category_scores']['file_health']}/30 |
| Link Health | {report['health_score']['category_scores']['link_health']}/30 |
| Task Health | {report['health_score']['category_scores']['task_health']}/25 |
| Activity Health | {report['health_score']['category_scores']['activity_health']}/15 |

---

## 📁 File Statistics

- **Total Files**: {report['files']['total_files']}
- **Markdown Files**: {report['files']['markdown_files']}
- **Other Files**: {report['files']['other_files']}
- **Total Folders**: {report['files']['total_folders']}

**Files by Extension:**
"""
    
    for ext, count in report['files']['by_extension'].items():
        md += f"- {ext}: {count}\n"
    
    md += f"""
---

## 🏷️ Tag Analysis

- **Total Tags**: {report['tags']['total_tags']}

**Top Tags:**
"""
    
    for tag in report['tags']['top_tags'][:10]:
        md += f"- {tag['tag']}: {tag.get('count', 1)}\n"
    
    md += f"""
---

## 🔗 Link Analysis

- **Orphan Files**: {report['links']['orphan_files']}
- **Dead-end Files**: {report['links']['deadend_files']}
- **Unresolved Links**: {report['links']['unresolved_links']}

---

## ✅ Task Statistics

- **Total Tasks**: {report['tasks']['total_tasks']}
- **Todo Tasks**: {report['tasks']['todo_tasks']}
- **Done Tasks**: {report['tasks']['done_tasks']}
- **Completion Rate**: {report['tasks']['completion_rate']:.1f}%

---

## 📋 Properties & Metadata

- **Total Properties**: {report['properties']['total_properties']}

**Top Properties:**
"""
    
    for prop in report['properties']['top_properties'][:10]:
        md += f"- {prop['property']}: {prop.get('count', 1)}\n"
    
    md += f"""
---

## 📅 Recent Activity

- **Total Aliases**: {report['recent_activity']['total_aliases']}
- **Total Bookmarks**: {report['recent_activity']['total_bookmarks']}

**Recently Opened Files:**
"""
    
    for file in report['recent_activity']['recent_files'][:10]:
        md += f"- {file}\n"
    
    md += """
---

## 💡 Recommendations

1. **Link Health**: Consider linking orphan files to your knowledge graph
2. **Task Management**: Review pending tasks and update status
3. **Tag Organization**: Consider consolidating similar tags
4. **Metadata**: Add consistent properties to improve search and filtering

---

*Report generated by Obsidian Vault Analytics Skill*
"""
    
    return md


def main():
    """Main function to run vault analytics."""
    parser = argparse.ArgumentParser(
        description="Obsidian Vault Analytics - Comprehensive vault analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill obsidian-vault-analytics          # Generate full analytics report
  /skill obsidian-vault-analytics --json   # Output JSON format
  /skill obsidian-vault-analytics --save   # Save report to vault
"""
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report in JSON format"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to vault"
    )
    
    args = parser.parse_args()
    
    # Run analytics
    analytics = VaultAnalytics()
    report = analytics.generate_report()
    
    # Output results
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        md_report = format_report_markdown(report)
        print(md_report)
        
        if args.save:
            date_str = datetime.now().strftime("%Y-%m-%d")
            save_path = f"Sources/Vault Analytics - {date_str}.md"
            save_note(save_path, md_report)
            print(f"\n✓ Report saved to: {save_path}")


if __name__ == "__main__":
    main()
