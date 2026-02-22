"""Obsidian Link Analyzer - Comprehensive link and knowledge graph analysis.

This skill provides powerful link analysis capabilities including:
- Backlink and outgoing link analysis
- Orphan and dead-end file detection
- Unresolved link identification
- Knowledge graph connectivity analysis
- Link health assessment and recommendations
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH
from obsidian_cli import get_cli


class LinkAnalyzer:
    """Link analysis engine using Obsidian CLI."""
    
    def __init__(self):
        self.cli = get_cli()
    
    def get_orphan_files(self) -> List[str]:
        """Get files with no incoming links."""
        print("Finding orphan files...")
        return self.cli.get_orphans(all=True)
    
    def get_deadend_files(self) -> List[str]:
        """Get files with no outgoing links."""
        print("Finding dead-end files...")
        return self.cli.get_deadends(all=True)
    
    def get_unresolved_links(self) -> List[str]:
        """Get unresolved links."""
        print("Finding unresolved links...")
        return self.cli.get_unresolved_links(verbose=True)
    
    def get_all_files(self) -> List[str]:
        """Get all markdown files."""
        all_files = self.cli.list_files(ext="md", total=True)
        return [f for f in all_files if f.endswith('.md')]
    
    def analyze_file_links(self, file_path: str) -> Dict[str, Any]:
        """Analyze links for a specific file."""
        print(f"Analyzing links for: {file_path}")
        
        backlinks = self.cli.get_backlinks(path=file_path)
        outgoing = self.cli.get_outgoing_links(path=file_path)
        
        return {
            "file": file_path,
            "backlinks": backlinks,
            "backlink_count": len(backlinks),
            "outgoing_links": outgoing,
            "outgoing_count": len(outgoing),
            "is_isolated": len(backlinks) == 0 and len(outgoing) == 0,
            "is_orphan": len(backlinks) == 0,
            "is_deadend": len(outgoing) == 0
        }
    
    def build_link_graph(self) -> Dict[str, Any]:
        """Build comprehensive link graph analysis."""
        print("Building link graph...")
        
        all_files = self.get_all_files()
        orphans = self.get_orphan_files()
        deadends = self.get_deadend_files()
        unresolved = self.get_unresolved_links()
        
        # Analyze connectivity
        connected_files = [f for f in all_files if f not in orphans]
        files_with_outgoing = [f for f in all_files if f not in deadends]
        
        # Calculate metrics
        total_files = len(all_files)
        
        return {
            "total_files": total_files,
            "orphans": orphans,
            "orphan_count": len(orphans),
            "orphan_percentage": (len(orphans) / max(total_files, 1)) * 100,
            "deadends": deadends,
            "deadend_count": len(deadends),
            "deadend_percentage": (len(deadends) / max(total_files, 1)) * 100,
            "unresolved_links": unresolved,
            "unresolved_count": len(unresolved),
            "connected_files": connected_files,
            "connected_count": len(connected_files),
            "files_with_outgoing": files_with_outgoing,
            "files_with_outgoing_count": len(files_with_outgoing),
            "connectivity_score": self._calculate_connectivity_score(total_files, len(orphans)),
            "all_files": all_files
        }
    
    def _calculate_connectivity_score(self, total_files: int, orphan_count: int) -> float:
        """Calculate connectivity health score."""
        if total_files == 0:
            return 0.0
        connected_ratio = 1 - (orphan_count / total_files)
        return connected_ratio * 100
    
    def find_most_connected_files(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Find files with most backlinks."""
        print("Finding most connected files...")
        
        all_files = self.get_all_files()
        file_link_counts = []
        
        # Sample a subset for performance
        sample_files = all_files[:100]  # Analyze first 100 files
        
        for file_path in sample_files:
            try:
                backlinks = self.cli.get_backlinks(path=file_path)
                file_link_counts.append({
                    "file": file_path,
                    "backlink_count": len(backlinks),
                    "backlinks": backlinks
                })
            except:
                continue
        
        # Sort by backlink count
        return sorted(file_link_counts, key=lambda x: -x["backlink_count"])[:limit]
    
    def analyze_central_hubs(self) -> Dict[str, Any]:
        """Identify central hub files in the knowledge graph."""
        print("Identifying central hubs...")
        
        most_connected = self.find_most_connected_files(limit=15)
        
        return {
            "hub_files": most_connected,
            "recommendations": self._generate_hub_recommendations(most_connected)
        }
    
    def _generate_hub_recommendations(self, hubs: List[Dict]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if not hubs:
            recommendations.append("Consider creating some index or MOC (Map of Content) files")
        
        if len(hubs) > 0 and len(hubs) < 5:
            recommendations.append("You have very few hub files - consider creating more MOCs")
        
        recommendations.append("Use hub files to organize your knowledge graph")
        
        return recommendations
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive link health report."""
        print("\n=== Generating Link Health Report ===\n")
        
        graph = self.build_link_graph()
        hubs = self.analyze_central_hubs()
        
        health_score = 100.0
        
        # Penalty for orphans
        health_score -= graph["orphan_percentage"] * 0.5
        
        # Penalty for deadends
        health_score -= graph["deadend_percentage"] * 0.3
        
        # Penalty for unresolved links
        health_score -= min(graph["unresolved_count"] * 2, 20)
        
        health_score = max(0, min(100, health_score))
        
        return {
            "analysis_date": datetime.now().isoformat(),
            "link_health_score": health_score,
            "link_graph": graph,
            "central_hubs": hubs,
            "recommendations": self._generate_comprehensive_recommendations(graph, health_score)
        }
    
    def _generate_comprehensive_recommendations(self, graph: Dict, score: float) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if score >= 80:
            recommendations.append("✅ Excellent link health! Your knowledge graph is well-connected!")
        elif score >= 60:
            recommendations.append("⚠️ Good link health, but there's room for improvement")
        else:
            recommendations.append("🔴 Link health needs attention - your knowledge graph could be better connected")
        
        # Orphan recommendations
        if graph["orphan_count"] > 0:
            recommendations.append(f"📌 You have {graph['orphan_count']} orphan files - consider linking them to your knowledge graph")
            if graph["orphan_count"] <= 10:
                for orphan in graph["orphans"][:5]:
                    recommendations.append(f"   - {orphan}")
        
        # Deadend recommendations
        if graph["deadend_count"] > 0:
            recommendations.append(f"📌 You have {graph['deadend_count']} dead-end files - consider adding outgoing links")
        
        # Unresolved recommendations
        if graph["unresolved_count"] > 0:
            recommendations.append(f"📌 You have {graph['unresolved_count']} unresolved links - consider fixing or removing them")
        
        # General recommendations
        recommendations.append("💡 Create MOC (Map of Content) files to organize topics")
        recommendations.append("💡 Use tags and properties to enhance discoverability")
        recommendations.append("💡 Regularly review and update your link structure")
        
        return recommendations


def format_link_report(report: Dict[str, Any]) -> str:
    """Format link analysis report as markdown."""
    
    graph = report["link_graph"]
    hubs = report["central_hubs"]
    
    md = f"""# Obsidian Link Analyzer Report

Generated on: {report['analysis_date']}

## 🏥 Link Health Score

**Score: {report['link_health_score']:.1f}/100

---

## 📊 Link Graph Overview

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Files | {graph['total_files']} | 100% |
| 🔗 Connected Files | {graph['connected_count']} | {100 - graph['orphan_percentage']:.1f}% |
| 📭 Orphan Files | {graph['orphan_count']} | {graph['orphan_percentage']:.1f}% |
| 🚧 Dead-end Files | {graph['deadend_count']} | {graph['deadend_percentage']:.1f}% |
| ❓ Unresolved Links | {graph['unresolved_count']} | - |

---

## 🏗️ Central Hub Files

Files with the most backlinks (hubs):
"""
    
    for i, hub in enumerate(hubs["hub_files"][:10], 1):
        md += f"{i}. **{hub['file']}** - {hub['backlink_count']} backlinks\n"
    
    md += """
---

## 📭 Orphan Files (No Incoming Links)
"""
    
    if graph["orphan_count"] > 0:
        for orphan in graph["orphans"][:15]:
            md += f"- {orphan}\n"
        if graph["orphan_count"] > 15:
            md += f"\n... and {graph['orphan_count'] - 15} more\n"
    else:
        md += "✅ No orphan files! Great job!\n"
    
    md += """
---

## 🚧 Dead-end Files (No Outgoing Links)
"""
    
    if graph["deadend_count"] > 0:
        for deadend in graph["deadends"][:15]:
            md += f"- {deadend}\n"
        if graph["deadend_count"] > 15:
            md += f"\n... and {graph['deadend_count'] - 15} more\n"
    else:
        md += "✅ No dead-end files! Excellent connectivity!\n"
    
    md += """
---

## ❓ Unresolved Links
"""
    
    if graph["unresolved_count"] > 0:
        for unresolved in graph["unresolved_links"][:20]:
            md += f"- {unresolved}\n"
        if graph["unresolved_count"] > 20:
            md += f"\n... and {graph['unresolved_count'] - 20} more\n"
    else:
        md += "✅ No unresolved links! Perfect!\n"
    
    md += """
---

## 💡 Recommendations

"""
    
    for i, rec in enumerate(report["recommendations"], 1):
        md += f"{i}. {rec}\n"
    
    md += """
---

*Report generated by Obsidian Link Analyzer Skill*
"""
    
    return md


def main():
    """Main function for link analysis."""
    parser = argparse.ArgumentParser(
        description="Obsidian Link Analyzer - Knowledge graph analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill obsidian-link-analyzer              # Full link health report
  /skill obsidian-link-analyzer --orphans   # Show only orphan files
  /skill obsidian-link-analyzer --deadends   # Show only dead-end files
  /skill obsidian-link-analyzer --hubs      # Show central hub files
  /skill obsidian-link-analyzer --file "Note.md"  # Analyze specific file
  /skill obsidian-link-analyzer --save         # Save report to vault
"""
    )
    
    parser.add_argument(
        "--orphans",
        action="store_true",
        help="Show only orphan files"
    )
    
    parser.add_argument(
        "--deadends",
        action="store_true",
        help="Show only dead-end files"
    )
    
    parser.add_argument(
        "--hubs",
        action="store_true",
        help="Show central hub files"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Analyze links for a specific file"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to vault"
    )
    
    args = parser.parse_args()
    
    analyzer = LinkAnalyzer()
    
    # Handle different modes
    if args.orphans:
        orphans = analyzer.get_orphan_files()
        print("# Orphan Files (No Incoming Links)\n")
        if orphans:
            for orphan in orphans:
                print(f"- {orphan}")
            print(f"\nTotal: {len(orphans)} orphan files")
        else:
            print("✅ No orphan files!")
        return
    
    if args.deadends:
        deadends = analyzer.get_deadend_files()
        print("# Dead-end Files (No Outgoing Links)\n")
        if deadends:
            for deadend in deadends:
                print(f"- {deadend}")
            print(f"\nTotal: {len(deadends)} dead-end files")
        else:
            print("✅ No dead-end files!")
        return
    
    if args.hubs:
        hubs = analyzer.find_most_connected_files(limit=20)
        print("# Central Hub Files (Most Backlinks)\n")
        for i, hub in enumerate(hubs, 1):
            print(f"{i}. {hub['file']} - {hub['backlink_count']} backlinks")
        return
    
    if args.file:
        analysis = analyzer.analyze_file_links(args.file)
        print(f"# Link Analysis: {analysis['file']}\n")
        print(f"Backlinks: {analysis['backlink_count']}")
        if analysis['backlinks']:
            for link in analysis['backlinks']:
                print(f"  - {link}")
        print(f"\nOutgoing Links: {analysis['outgoing_count']}")
        if analysis['outgoing_links']:
            for link in analysis['outgoing_links']:
                print(f"  - {link}")
        print(f"\nStatus: Isolated={analysis['is_isolated']}, Orphan={analysis['is_orphan']}, Dead-end={analysis['is_deadend']}")
        return
    
    # Default: full report
    report = analyzer.generate_health_report()
    md_report = format_link_report(report)
    print(md_report)
    
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_path = f"Sources/Link Analyzer Report - {date_str}.md"
        save_note(save_path, md_report)
        print(f"\n✓ Report saved to: {save_path}")


if __name__ == "__main__":
    main()
