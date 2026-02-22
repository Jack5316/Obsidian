"""Curl - Information curation from multiple sources.

This skill facilitates information curation - gathering, filtering, organizing,
and synthesizing information from multiple sources in your Obsidian vault.
Named after the command-line tool, but for knowledge curation. Inspired by
Tiago Forte's Second Brain principles of capturing and organizing information.

Features:
- Gather information from multiple vault locations
- Filter by tags, dates, keywords, or content types
- Organize into thematic collections
- Synthesize curated information
- Create curated reading lists
- Build personal knowledge repositories
"""

import argparse
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


CURL_PROMPT = """You are a knowledge curation assistant. Your role is to help
gather, filter, organize, and synthesize information from multiple sources.

Key principles:
- Quality over quantity - curate the most valuable information
- Context preservation - maintain source and context
- Thematic organization - group by meaning and purpose
- Synthesis - connect ideas across sources
- Actionable insights - identify what matters most

For each curation, provide:
1. Well-organized, thematic collections
2. Key insights from each source
3. Connections between different sources
4. Actionable insights and next steps
5. Gaps identified in the collection
"""


class InformationCurator:
    """Engine for curating information from multiple sources."""
    
    def __init__(self):
        self.vault_path = VAULT_PATH
        
        # Common directories to search
        self.source_dirs = [
            "Sources",
            "Atlas",
            "00 - Inbox",
            "01 - Projects",
            "02 - Areas",
            "03 - Resources"
        ]
    
    def search_by_tags(self, tags: List[str], directories: Optional[List[str]] = None) -> List[Path]:
        """Find files containing any of the specified tags."""
        if directories is None:
            directories = self.source_dirs
        
        matching_files = []
        tag_patterns = [re.compile(rf'#\s*{re.escape(tag)}\b', re.IGNORECASE) for tag in tags]
        
        for dir_name in directories:
            dir_path = self.vault_path / dir_name
            if not dir_path.exists():
                continue
            
            for md_file in dir_path.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8")
                    if any(pattern.search(content) for pattern in tag_patterns):
                        matching_files.append(md_file)
                except:
                    continue
        
        return matching_files
    
    def search_by_keywords(self, keywords: List[str], directories: Optional[List[str]] = None) -> List[Path]:
        """Find files containing any of the specified keywords."""
        if directories is None:
            directories = self.source_dirs
        
        matching_files = []
        keyword_patterns = [re.compile(re.escape(kw), re.IGNORECASE) for kw in keywords]
        
        for dir_name in directories:
            dir_path = self.vault_path / dir_name
            if not dir_path.exists():
                continue
            
            for md_file in dir_path.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8")
                    if any(pattern.search(content) for pattern in keyword_patterns):
                        matching_files.append(md_file)
                except:
                    continue
        
        return matching_files
    
    def search_by_date(self, days: int = 7, directories: Optional[List[str]] = None) -> List[Path]:
        """Find files modified within the last N days."""
        if directories is None:
            directories = self.source_dirs
        
        cutoff = datetime.now() - timedelta(days=days)
        matching_files = []
        
        for dir_name in directories:
            dir_path = self.vault_path / dir_name
            if not dir_path.exists():
                continue
            
            for md_file in dir_path.rglob("*.md"):
                try:
                    mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                    if mtime >= cutoff:
                        matching_files.append(md_file)
                except:
                    continue
        
        return sorted(matching_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def search_in_directory(self, directory: str, pattern: str = "*.md") -> List[Path]:
        """Search for files in a specific directory."""
        dir_path = self.vault_path / directory
        if not dir_path.exists():
            return []
        
        return list(dir_path.glob(pattern))
    
    def gather_files(self, 
                    tags: Optional[List[str]] = None,
                    keywords: Optional[List[str]] = None,
                    days: Optional[int] = None,
                    directories: Optional[List[str]] = None,
                    paths: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Gather files from multiple sources with various filters."""
        all_files: Set[Path] = set()
        
        # Explicit paths
        if paths:
            for path in paths:
                file_path = self.vault_path / path
                if file_path.exists():
                    all_files.add(file_path)
        
        # Tag search
        if tags:
            tag_files = self.search_by_tags(tags, directories)
            all_files.update(tag_files)
        
        # Keyword search
        if keywords:
            keyword_files = self.search_by_keywords(keywords, directories)
            all_files.update(keyword_files)
        
        # Date search
        if days:
            date_files = self.search_by_date(days, directories)
            all_files.update(date_files)
        
        # Read file contents
        results = []
        for file_path in all_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                results.append({
                    "path": str(file_path.relative_to(self.vault_path)),
                    "name": file_path.name,
                    "content": content,
                    "mtime": datetime.fromtimestamp(file_path.stat().st_mtime)
                })
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
        
        return results
    
    def organize_by_theme(self, files: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Organize gathered files into thematic collections."""
        files_content = "\n\n".join([
            f"---\nSOURCE: {f['path']}\n{f['content'][:2000]}"
            for f in files
        ])
        
        prompt = f"""Organize this information about "{topic}" into thematic collections:

{files_content}

Please organize into:
1. 3-5 main themes that emerge
2. For each theme:
   - Key insights from sources
   - Quotes/excerpts to preserve
   - Connections between sources
3. Cross-theme connections
4. Most important insights overall
5. Gaps in our knowledge

Structure this clearly and thematically."""
        
        result = summarize(prompt, CURL_PROMPT)
        return {"topic": topic, "organized": result, "file_count": len(files)}
    
    def create_reading_list(self, files: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Create a curated reading list with annotations."""
        files_list = "\n".join([
            f"{i+1}. {f['path']} (modified: {f['mtime'].strftime('%Y-%m-%d')})"
            for i, f in enumerate(files)
        ])
        
        files_content = "\n\n".join([
            f"---\n{files_list[i+1]}\n{f['content'][:1000]}"
            for i, f in enumerate(files[:10])
        ])
        
        prompt = f"""Create a curated reading list about "{topic}" from these sources:

{files_list}

Sample content:
{files_content}

Create:
1. Annotated reading list with priority
2. Short summary of each source
3. Why it's valuable
4. Recommended reading order
5. Key takeaways from each

Be selective - highlight the most valuable sources."""
        
        result = summarize(prompt, CURL_PROMPT)
        return {"topic": topic, "reading_list": result, "sources": [f["path"] for f in files]}
    
    def synthesize_curated(self, files: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Synthesize curated information into a coherent whole."""
        files_content = "\n\n".join([
            f"---\nSOURCE: {f['path']}\n{f['content']}"
            for f in files
        ])
        
        prompt = f"""Synthesize this curated information about "{topic}":

{files_content}

Create a comprehensive synthesis:
1. Executive summary (1 paragraph)
2. Key insights organized by theme
3. Consensus and disagreements between sources
4. Most surprising or counterintuitive findings
5. Actionable implications
6. Open questions for further exploration

Make this a coherent, narrative synthesis rather than just a list."""
        
        result = summarize(prompt, CURL_PROMPT)
        return {"topic": topic, "synthesis": result, "sources": len(files)}
    
    def build_repository(self, files: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Build a personal knowledge repository on the topic."""
        organized = self.organize_by_theme(files, topic)
        reading_list = self.create_reading_list(files, topic)
        synthesis = self.synthesize_curated(files, topic)
        
        return {
            "topic": topic,
            "organized": organized,
            "reading_list": reading_list,
            "synthesis": synthesis,
            "sources_count": len(files)
        }


def format_curl_report(topic: str, results: Dict[str, Any], mode: str) -> str:
    """Format curation results as markdown."""
    
    md = f"# Information Curation: {topic}\n\n"
    md += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md += f"Mode: {mode}\n\n"
    md += "---\n\n"
    
    if mode == "gather":
        md += "## Gathered Sources\n\n"
        md += f"**Total sources found**: {results.get('count', 0)}\n\n"
        md += "### Files:\n\n"
        for path in results.get("paths", []):
            md += f"- [[{path}]]\n"
    
    elif mode == "organize":
        md += "## Thematic Organization\n\n"
        md += f"**Sources**: {results.get('file_count', 0)}\n\n"
        md += results.get("organized_text", "")
    
    elif mode == "reading-list":
        md += "## Curated Reading List\n\n"
        md += f"**Sources**: {len(results.get('sources', []))}\n\n"
        md += results.get("reading_list_text", "")
    
    elif mode == "synthesize":
        md += "## Synthesis\n\n"
        md += f"**Sources**: {results.get('sources_count', 0)}\n\n"
        md += results.get("synthesis_text", "")
    
    elif mode == "repository":
        md += "## Knowledge Repository\n\n"
        md += f"**Sources**: {results.get('sources_count', 0)}\n\n"
        md += "### Synthesis\n\n"
        md += str(results.get("synthesis_result", {}).get("synthesis", ""))[:1000] + "...\n\n"
        md += "### Reading List\n\n"
        md += str(results.get("reading_list_result", {}).get("reading_list", ""))[:500] + "...\n\n"
    
    md += "\n---\n*Generated by Curl Skill - Information Curation*"
    
    return md


def main():
    """Main function for information curation."""
    parser = argparse.ArgumentParser(
        description="Curl - Information curation from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill curl "AI" --tags ai machine-learning
  /skill curl "recent" --days 7 --organize
  /skill curl "topic" --keywords "keyword1" "keyword2" --synthesize
  /skill curl "reading" --paths "file1.md" "file2.md" --reading-list
  /skill curl "project" --directory "01 - Projects/MyProject" --repository
  /skill curl "topic" --tags tag --days 14 --save
"""
    )
    
    parser.add_argument(
        "topic",
        type=str,
        help="Topic for curation"
    )
    
    parser.add_argument(
        "--tags",
        type=str,
        nargs="*",
        help="Search by tags"
    )
    
    parser.add_argument(
        "--keywords",
        type=str,
        nargs="*",
        help="Search by keywords"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Search files from last N days"
    )
    
    parser.add_argument(
        "--directories",
        type=str,
        nargs="*",
        default=None,
        help="Directories to search"
    )
    
    parser.add_argument(
        "--paths",
        type=str,
        nargs="*",
        help="Specific file paths"
    )
    
    parser.add_argument(
        "--directory",
        type=str,
        default=None,
        help="Specific directory to search"
    )
    
    parser.add_argument(
        "--gather",
        action="store_true",
        help="Just gather and list files"
    )
    
    parser.add_argument(
        "--organize",
        action="store_true",
        help="Organize by theme"
    )
    
    parser.add_argument(
        "--reading-list",
        action="store_true",
        help="Create reading list"
    )
    
    parser.add_argument(
        "--synthesize",
        action="store_true",
        help="Synthesize curated info"
    )
    
    parser.add_argument(
        "--repository",
        action="store_true",
        help="Build full knowledge repository"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to Sources"
    )
    
    args = parser.parse_args()
    
    curator = InformationCurator()
    results = {}
    mode = "gather"
    
    print(f"📚 Curating information about: {args.topic}\n")
    
    # Gather files
    files = []
    
    if args.directory:
        files.extend([
            {"path": str(p.relative_to(VAULT_PATH)),
             "name": p.name,
             "content": p.read_text(encoding="utf-8"),
             "mtime": datetime.fromtimestamp(p.stat().st_mtime)}
            for p in curator.search_in_directory(args.directory)
        ])
    else:
        files = curator.gather_files(
            tags=args.tags,
            keywords=args.keywords,
            days=args.days,
            directories=args.directories,
            paths=args.paths
        )
    
    if not files:
        print("⚠️ No files found matching criteria.")
        return
    
    print(f"📄 Found {len(files)} sources\n")
    
    # Determine mode
    if args.organize:
        mode = "organize"
        print("🗂️ Organizing by theme...")
        org_result = curator.organize_by_theme(files, args.topic)
        results["organized_text"] = str(org_result)
        results["file_count"] = len(files)
    
    elif args.reading_list:
        mode = "reading-list"
        print("📖 Creating reading list...")
        rl_result = curator.create_reading_list(files, args.topic)
        results["reading_list_text"] = str(rl_result)
        results["sources"] = rl_result.get("sources", [])
    
    elif args.synthesize:
        mode = "synthesize"
        print("🔗 Synthesizing...")
        synth_result = curator.synthesize_curated(files, args.topic)
        results["synthesis_text"] = str(synth_result)
        results["sources_count"] = len(files)
    
    elif args.repository:
        mode = "repository"
        print("🏗️ Building knowledge repository...")
        repo_result = curator.build_repository(files, args.topic)
        results.update(repo_result)
    
    else:
        mode = "gather"
        results["count"] = len(files)
        results["paths"] = [f["path"] for f in files]
    
    # Generate report
    report = format_curl_report(args.topic, results, mode)
    print("\n" + report)
    
    # Save if requested
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_topic = args.topic.replace(' ', '_').replace('/', '_')
        save_note(f"Sources/Curl - {safe_topic} - {date_str}.md", report)
    
    print("\n✅ Curation complete!")


if __name__ == "__main__":
    main()