
"""Knowledge Graph - Comprehensive visual and structural overview of your Obsidian vault.

This skill provides a holistic view of your knowledge graph including:
- Complete vault structure and directory organization
- Knowledge graph connectivity and hub analysis
- Topical clusters and thematic groups
- File categories and content types
- Overall knowledge architecture visualization
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict, Counter

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import save_note, VAULT_PATH
from obsidian_cli import get_cli


class KnowledgeGraph:
    """Knowledge graph visualization and analysis engine."""

    def __init__(self):
        self.cli = get_cli()
        self.vault_path = VAULT_PATH

    def get_directory_structure(self) -> Dict[str, Any]:
        """Get comprehensive directory structure."""
        print("Analyzing directory structure...")

        folders = self.cli.list_folders(total=True)
        files = self.cli.list_files(total=True)

        # Count files by folder
        folder_files = defaultdict(list)
        for file in files:
            parts = Path(file).parts
            if len(parts) > 1:
                folder = parts[0]
                folder_files[folder].append(file)
            else:
                folder_files["root"].append(file)

        return {
            "total_folders": len(folders),
            "total_files": len(files),
            "folders": sorted(folders),
            "files_by_folder": dict(folder_files),
            "folder_counts": {k: len(v) for k, v in folder_files.items()}
        }

    def get_file_categories(self) -> Dict[str, Any]:
        """Categorize files by type and purpose."""
        print("Categorizing files...")

        all_files = self.cli.list_files(ext="md", total=True)

        categories = {
            "Sources": [],
            "Atlas": [],
            "Maps": [],
            "Inbox": [],
            "Projects": [],
            "Areas": [],
            "Resources": [],
            "Archive": [],
            "Habits": [],
            "Extras": [],
            "Other": []
        }

        for file in all_files:
            if file.startswith("Sources/"):
                categories["Sources"].append(file)
            elif file.startswith("Atlas/"):
                categories["Atlas"].append(file)
            elif file.startswith("Maps/"):
                categories["Maps"].append(file)
            elif file.startswith("00 - Inbox/"):
                categories["Inbox"].append(file)
            elif file.startswith("01 - Projects/"):
                categories["Projects"].append(file)
            elif file.startswith("02 - Areas/"):
                categories["Areas"].append(file)
            elif file.startswith("03 - Resources/"):
                categories["Resources"].append(file)
            elif file.startswith("04 - Archive/"):
                categories["Archive"].append(file)
            elif file.startswith("Habits/"):
                categories["Habits"].append(file)
            elif file.startswith("Extras/"):
                categories["Extras"].append(file)
            else:
                categories["Other"].append(file)

        return {
            "categories": categories,
            "category_counts": {k: len(v) for k, v in categories.items()}
        }

    def get_hub_analysis(self) -> Dict[str, Any]:
        """Get detailed hub and connectivity analysis."""
        print("Analyzing knowledge hubs...")

        all_files = self.cli.list_files(ext="md", total=True)
        orphans = self.cli.get_orphans(all=True)
        deadends = self.cli.get_deadends(all=True)

        # Find most connected files (hubs)
        hub_files = []
        for file in all_files[:150]:  # Analyze first 150 files
            try:
                backlinks = self.cli.get_backlinks(path=file)
                outgoing = self.cli.get_outgoing_links(path=file)
                if len(backlinks) > 0 or len(outgoing) > 3:
                    hub_files.append({
                        "file": file,
                        "backlink_count": len(backlinks),
                        "outgoing_count": len(outgoing),
                        "total_connections": len(backlinks) + len(outgoing)
                    })
            except:
                continue

        # Sort by total connections
        hub_files.sort(key=lambda x: -x["total_connections"])

        return {
            "top_hubs": hub_files[:25],
            "total_files_analyzed": len(all_files),
            "orphan_count": len(orphans),
            "deadend_count": len(deadends),
            "connected_count": len(all_files) - len(orphans)
        }

    def get_tag_themes(self) -> Dict[str, Any]:
        """Get tag-based thematic analysis."""
        print("Analyzing thematic tags...")

        tags = self.cli.list_tags(counts=True, sort="count")

        tag_data = []
        for tag_line in tags:
            if tag_line.strip():
                parts = tag_line.split()
                if parts:
                    tag_data.append({
                        "tag": parts[0],
                        "count": int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                    })

        # Group tags by prefix
        tag_groups = defaultdict(list)
        for tag in tag_data:
            tag_name = tag["tag"]
            if "/" in tag_name:
                prefix = tag_name.split("/")[0]
                tag_groups[prefix].append(tag)
            else:
                tag_groups["general"].append(tag)

        return {
            "total_tags": len(tag_data),
            "top_tags": tag_data[:30],
            "tag_groups": dict(tag_groups)
        }

    def generate_graph_report(self) -> Dict[str, Any]:
        """Generate comprehensive knowledge graph report."""
        print("\n=== Generating Knowledge Graph Report ===\n")

        directory = self.get_directory_structure()
        categories = self.get_file_categories()
        hubs = self.get_hub_analysis()
        themes = self.get_tag_themes()

        return {
            "analysis_date": datetime.now().isoformat(),
            "directory_structure": directory,
            "file_categories": categories,
            "hub_analysis": hubs,
            "thematic_analysis": themes
        }


def format_graph_report(report: Dict[str, Any]) -> str:
    """Format knowledge graph report as markdown."""

    dir_struct = report["directory_structure"]
    categories = report["file_categories"]
    hubs = report["hub_analysis"]
    themes = report["thematic_analysis"]

    md = f"""# Knowledge Graph - Vault Overview

Generated on: {report['analysis_date']}

## 🌐 Vault Architecture at a Glance

| Metric | Count |
|--------|-------|
| Total Files | {dir_struct['total_files']} |
| Total Folders | {dir_struct['total_folders']} |
| Connected Files | {hubs['connected_count']} |
| Knowledge Hubs | {len(hubs['top_hubs'])} |
| Total Tags | {themes['total_tags']} |

---

## 📁 Directory Structure

**Files by Folder:**
"""

    for folder, count in sorted(dir_struct["folder_counts"].items(), key=lambda x: -x[1]):
        md += f"- **{folder}**: {count} files\n"

    md += """
---

## 📂 Content Categories

"""

    for category, files in categories["categories"].items():
        if files:
            md += f"### {category}\n"
            md += f"- **Count**: {len(files)}\n"
            if len(files) <= 10:
                for file in files:
                    md += f"  - {file}\n"
            else:
                for file in files[:8]:
                    md += f"  - {file}\n"
                md += f"  ... and {len(files) - 8} more\n"
            md += "\n"

    md += """
---

## 🏗️ Knowledge Hubs (Most Connected Files)

Top 25 hub files by total connections:

| Rank | File | Backlinks | Outgoing | Total |
|------|------|-----------|----------|-------|
"""

    for i, hub in enumerate(hubs["top_hubs"][:25], 1):
        md += f"| {i} | {hub['file']} | {hub['backlink_count']} | {hub['outgoing_count']} | {hub['total_connections']} |\n"

    md += f"""
---

## 🏷️ Thematic Tags

**Top 30 Tags:**

"""

    for i, tag in enumerate(themes["top_tags"][:30], 1):
        md += f"{i}. {tag['tag']}: {tag['count']}\n"

    md += """

**Tag Groups:**
"""

    for group, tags in sorted(themes["tag_groups"].items(), key=lambda x: -len(x[1])):
        md += f"\n### {group.capitalize()}\n"
        for tag in tags[:10]:
            md += f"- {tag['tag']}: {tag['count']}\n"
        if len(tags) > 10:
            md += f"... and {len(tags) - 10} more\n"

    md += """
---

## 📊 Connectivity Health

- **Orphan Files**: {} (no incoming links)
- **Dead-end Files**: {} (no outgoing links)
- **Connected Files**: {}

---

## 💡 Knowledge Graph Insights

1. **Central Hubs**: Identify key files that anchor your knowledge graph
2. **Content Distribution**: See how your knowledge is organized across categories
3. **Thematic Areas**: Understand the main topics and themes in your vault
4. **Connectivity**: Assess how well your knowledge is interconnected

---

*Report generated by Knowledge Graph Skill*
""".format(
        hubs["orphan_count"],
        hubs["deadend_count"],
        hubs["connected_count"]
    )

    return md


def main():
    """Main function for knowledge graph generation."""
    parser = argparse.ArgumentParser(
        description="Knowledge Graph - Comprehensive vault overview",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/knowledge_graph.py              # Generate knowledge graph report
  python3 _scripts/knowledge_graph.py --save       # Save report to vault
"""
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to vault"
    )

    args = parser.parse_args()

    # Generate knowledge graph
    kg = KnowledgeGraph()
    report = kg.generate_graph_report()
    md_report = format_graph_report(report)
    print(md_report)

    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_path = f"Sources/Knowledge Graph - {date_str}.md"
        save_note(save_path, md_report)
        print(f"\n✓ Report saved to: {save_path}")


if __name__ == "__main__":
    main()
