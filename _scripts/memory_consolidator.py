"""Memory Consolidator - Persist information to LLM/Agent memory in Obsidian.

This skill helps you capture and persist important information to your LLM Context
folder, creating persistent memory for Kilo Code and other AI assistants.

Features:
- Add preferences, facts, and patterns to memory
- Categorize information (preferences, facts, workflows, etc.)
- Update existing memory entries
- Search and review current memory
- Generate memory summaries
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


class MemoryConsolidator:
    """Engine for managing LLM/Agent memory."""
    
    def __init__(self):
        self.llm_context_path = VAULT_PATH / "LLM Context"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all memory directories exist."""
        directories = [
            "Preferences",
            "Personal Profile",
            "Writing Style",
            "Basic Rules",
            "Dynamic Activities",
            "Facts & Knowledge",
            "Workflows & Processes",
            "Project Context",
            "Patterns & Learnings"
        ]
        
        for dir_name in directories:
            dir_path = self.llm_context_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def add_memory(self, category: str, title: str, content: str,
                   tags: Optional[List[str]] = None) -> Path:
        """Add a new memory entry."""
        
        # Sanitize title for filename
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
        safe_title = safe_title.replace(' ', '_')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.md"
        
        category_path = self.llm_context_path / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        file_path = category_path / filename
        
        # Build frontmatter
        frontmatter = {
            "type": "memory",
            "category": category,
            "title": title,
            "created": datetime.now().isoformat(),
            "tags": ["llm-context", "memory"] + (tags or [])
        }
        
        # Build content
        md_content = self._format_frontmatter(frontmatter)
        md_content += f"\n# {title}\n\n"
        md_content += f"{content}\n\n"
        md_content += "---\n*This memory is automatically loaded by AI assistants.*"
        
        file_path.write_text(md_content, encoding="utf-8")
        print(f"✓ Memory added: {file_path}")
        
        return file_path
    
    def _format_frontmatter(self, data: Dict[str, Any]) -> str:
        """Format YAML frontmatter."""
        fm = "---\n"
        for key, value in data.items():
            if isinstance(value, list):
                fm += f"{key}:\n"
                for item in value:
                    fm += f"  - {item}\n"
            else:
                fm += f"{key}: {value}\n"
        fm += "---\n"
        return fm
    
    def add_preference(self, preference: str, description: str = "") -> Path:
        """Add a preference to memory."""
        content = f"**Preference**: {preference}\n\n"
        if description:
            content += f"**Description**: {description}\n\n"
        content += "This preference should be respected in all interactions."
        
        return self.add_memory(
            category="Preferences",
            title=f"Preference: {preference[:50]}",
            content=content,
            tags=["preference"]
        )
    
    def add_fact(self, fact: str, source: str = "") -> Path:
        """Add a factual piece of information."""
        content = f"**Fact**: {fact}\n\n"
        if source:
            content += f"**Source**: {source}\n\n"
        
        return self.add_memory(
            category="Facts & Knowledge",
            title=f"Fact: {fact[:50]}",
            content=content,
            tags=["fact", "knowledge"]
        )
    
    def add_workflow(self, name: str, steps: List[str]) -> Path:
        """Add a workflow or process."""
        content = f"## {name}\n\n**Steps:**\n\n"
        for i, step in enumerate(steps, 1):
            content += f"{i}. {step}\n"
        
        return self.add_memory(
            category="Workflows & Processes",
            title=f"Workflow: {name}",
            content=content,
            tags=["workflow", "process"]
        )
    
    def add_pattern(self, pattern: str, observation: str = "") -> Path:
        """Add an observed pattern or learning."""
        content = f"**Pattern**: {pattern}\n\n"
        if observation:
            content += f"**Observation**: {observation}\n\n"
        
        return self.add_memory(
            category="Patterns & Learnings",
            title=f"Pattern: {pattern[:50]}",
            content=content,
            tags=["pattern", "learning"]
        )
    
    def list_memories(self, category: Optional[str] = None) -> List[Path]:
        """List all memory files, optionally filtered by category."""
        memories = []
        
        if category:
            category_path = self.llm_context_path / category
            if category_path.exists():
                memories = list(category_path.glob("*.md"))
        else:
            memories = list(self.llm_context_path.rglob("*.md"))
        
        return sorted(memories)
    
    def search_memories(self, query: str) -> List[Path]:
        """Search memories containing query text."""
        results = []
        query_lower = query.lower()
        
        for md_file in self.llm_context_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8").lower()
                if query_lower in content:
                    results.append(md_file)
            except:
                continue
        
        return results
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of all memory."""
        categories = [
            "Preferences",
            "Personal Profile",
            "Writing Style",
            "Basic Rules",
            "Dynamic Activities",
            "Facts & Knowledge",
            "Workflows & Processes",
            "Project Context",
            "Patterns & Learnings"
        ]
        
        summary = {
            "total_memories": 0,
            "by_category": {},
            "recent_memories": []
        }
        
        all_memories = []
        
        for category in categories:
            cat_path = self.llm_context_path / category
            if cat_path.exists():
                mem_files = list(cat_path.glob("*.md"))
                summary["by_category"][category] = len(mem_files)
                summary["total_memories"] += len(mem_files)
                all_memories.extend(mem_files)
        
        # Get recent memories (last 10)
        all_memories.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        summary["recent_memories"] = [str(m.relative_to(self.llm_context_path)) for m in all_memories[:10]]
        
        return summary


def format_summary_report(summary: Dict[str, Any]) -> str:
    """Format memory summary as markdown."""
    
    md = f"# LLM Memory Summary\n\n"
    md += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md += f"**Total Memories**: {summary['total_memories']}\n\n"
    
    md += "## By Category\n\n"
    md += "| Category | Count |\n"
    md += "|----------|-------|\n"
    
    for category, count in sorted(summary["by_category"].items()):
        md += f"| {category} | {count} |\n"
    
    md += "\n## Recent Memories\n\n"
    for i, memory in enumerate(summary["recent_memories"], 1):
        md += f"{i}. {memory}\n"
    
    md += "\n---\n*Summary generated by Memory Consolidator*"
    
    return md


def main():
    """Main function for memory consolidation."""
    parser = argparse.ArgumentParser(
        description="Memory Consolidator - Persist information to LLM memory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill memory --summary                              # Show memory summary
  /skill memory --preference "I like concise answers"  # Add preference
  /skill memory --fact "Python 3.11 is latest"        # Add fact
  /skill memory --list                                  # List all memories
  /skill memory --search "workflow"                     # Search memories
"""
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show memory summary"
    )
    
    parser.add_argument(
        "--preference",
        type=str,
        help="Add a preference (use --desc for description)"
    )
    
    parser.add_argument(
        "--fact",
        type=str,
        help="Add a fact (use --source for source)"
    )
    
    parser.add_argument(
        "--pattern",
        type=str,
        help="Add an observed pattern"
    )
    
    parser.add_argument(
        "--workflow",
        type=str,
        help="Add a workflow (comma-separated steps)"
    )
    
    parser.add_argument(
        "--desc",
        type=str,
        default="",
        help="Description for preference"
    )
    
    parser.add_argument(
        "--source",
        type=str,
        default="",
        help="Source for fact"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all memories"
    )
    
    parser.add_argument(
        "--category",
        type=str,
        help="Filter by category when listing"
    )
    
    parser.add_argument(
        "--search",
        type=str,
        help="Search memories containing text"
    )
    
    args = parser.parse_args()
    
    consolidator = MemoryConsolidator()
    
    # Handle different operations
    if args.summary:
        summary = consolidator.get_memory_summary()
        print(format_summary_report(summary))
        return
    
    if args.preference:
        consolidator.add_preference(args.preference, args.desc)
        return
    
    if args.fact:
        consolidator.add_fact(args.fact, args.source)
        return
    
    if args.pattern:
        consolidator.add_pattern(args.pattern, args.desc)
        return
    
    if args.workflow:
        name = args.workflow.split(",")[0].strip()
        steps = [s.strip() for s in args.workflow.split(",")[1:]]
        if steps:
            consolidator.add_workflow(name, steps)
        else:
            print("Please provide workflow name followed by comma-separated steps")
        return
    
    if args.list:
        memories = consolidator.list_memories(args.category)
        print(f"# Memory Files ({len(memories)})\n")
        for mem in memories:
            rel_path = mem.relative_to(VAULT_PATH)
            print(f"- {rel_path}")
        return
    
    if args.search:
        results = consolidator.search_memories(args.search)
        print(f"# Search Results for '{args.search}' ({len(results)})\n")
        for result in results:
            rel_path = result.relative_to(VAULT_PATH)
            print(f"- {rel_path}")
        return
    
    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
