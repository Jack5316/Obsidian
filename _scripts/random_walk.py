"""Random Walk - Explore your Obsidian vault through serendipitous discovery.

Randomly selects notes, analyzes connections, and suggests research paths
through your knowledge base. Perfect for finding forgotten insights or
discovering unexpected connections.
"""

import argparse
import random
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH, TRACKER


def find_markdown_files() -> List[Path]:
    """Find all markdown files in the vault, excluding hidden directories."""
    markdown_files = []
    
    # Directories to exclude
    exclude_dirs = {'.git', '.obsidian', '.claude', '.cursor', '_scripts', '_org', '_logs', '.ruff_cache'}
    
    for item in VAULT_PATH.iterdir():
        if item.is_dir():
            if item.name in exclude_dirs:
                continue
            # Recursively search subdirectories
            for md_file in item.rglob('*.md'):
                markdown_files.append(md_file)
        elif item.suffix == '.md':
            markdown_files.append(item)
    
    return markdown_files


def extract_wikilinks(content: str) -> List[str]:
    """Extract [[wikilink]] targets from markdown content."""
    pattern = r'\[\[([^\]]+)\]\]'
    return re.findall(pattern, content)


def extract_tags(content: str) -> List[str]:
    """Extract #tags from markdown content."""
    pattern = r'#([a-zA-Z_][a-zA-Z0-9_-]*)'
    return re.findall(pattern, content)


def read_note_content(file_path: Path) -> Dict:
    """Read and parse a note file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Remove frontmatter if present
        body = content
        fm_match = re.match(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
        if fm_match:
            body = content[fm_match.end():]
        
        return {
            'path': file_path,
            'relative_path': str(file_path.relative_to(VAULT_PATH)),
            'title': file_path.stem,
            'content': body,
            'full_content': content,
            'wikilinks': extract_wikilinks(body),
            'tags': extract_tags(body),
            'word_count': len(body.split())
        }
    except Exception as e:
        return None


def select_random_notes(count: int = 5, topic: Optional[str] = None) -> List[Dict]:
    """Select random notes from the vault."""
    all_files = find_markdown_files()
    notes = []
    
    for file_path in all_files:
        note = read_note_content(file_path)
        if note and note['word_count'] > 50:  # Skip very short notes
            if topic:
                # Filter by topic if provided
                combined = (note['title'] + ' ' + note['content']).lower()
                if topic.lower() in combined:
                    notes.append(note)
            else:
                notes.append(note)
    
    if not notes:
        return []
    
    # Select random notes
    selected = random.sample(notes, min(count, len(notes)))
    return selected


def trace_connection_path(start_note: Dict, max_depth: int = 3) -> List[Dict]:
    """Trace a path through linked notes starting from a given note."""
    path = [start_note]
    current_note = start_note
    
    all_notes = {n['title']: n for n in [read_note_content(f) for f in find_markdown_files()] if n}
    
    for _ in range(max_depth):
        if not current_note['wikilinks']:
            break
        
        # Filter to links that exist in our vault
        valid_links = [link for link in current_note['wikilinks'] if link in all_notes and link not in [n['title'] for n in path]]
        
        if not valid_links:
            break
        
        # Pick a random valid link
        next_title = random.choice(valid_links)
        next_note = all_notes[next_title]
        path.append(next_note)
        current_note = next_note
    
    return path


def build_research_prompt(notes: List[Dict], path: List[Dict], topic: Optional[str]) -> str:
    """Build the prompt for the AI research assistant."""
    notes_text = "\n\n---\n\n".join(
        f"NOTE: [[{n['title']}]]\n\nTags: {', '.join(n['tags']) if n['tags'] else 'None'}\n\n{n['content'][:2000]}"
        for n in notes
    )
    
    path_text = " → ".join(f"[[{n['title']}]]" for n in path) if len(path) > 1 else "No connected path found"
    
    path_details = "\n\n".join(
        f"STEP {i+1}: [[{n['title']}]]\n\n{n['content'][:1500]}"
        for i, n in enumerate(path)
    )
    
    base = f"""You are a research assistant exploring a personal knowledge base through a random walk. Your role is to:
1. Analyze the randomly selected notes
2. Follow the connection path that was discovered
3. Suggest interesting research directions and questions
4. Highlight forgotten insights or unexpected connections

**Randomly Selected Notes:**
{notes_text}

**Discovery Path:**
{path_text}

**Path Details:**
{path_details}

**Output format:**

# Random Walk Research Exploration

## Today's Discovery Path
- Start: [[{path[0]['title']}]]
- Path: {path_text}

## Key Insights Found
- [Bullet points of interesting insights from the notes]

## Unexpected Connections
- [Connections between notes that weren't obvious]

## Research Questions to Explore
- [Curious questions raised by this random walk]

## Forgotten Gems
- [Notes or ideas the user might have forgotten about]

## Suggested Next Steps
- [Specific actions: read a particular note, create a synthesis, follow a link]

**Rules:**
- Use [[wikilinks]] for all note references
- Be curious and playful - this is about serendipitous discovery
- Prioritize insights the user might have missed
- Suggest concrete, actionable next steps
- Keep the tone enthusiastic and encouraging
"""

    if topic:
        base += f"\n\n**Topic Focus:** This random walk is focused on: '{topic}'. Emphasize insights related to this theme.\n"

    return base


def main():
    """Main function for the random walk skill."""
    parser = argparse.ArgumentParser(
        description="Random Walk - Explore your Obsidian vault through serendipitous discovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill random-walk                    # Basic random walk with 5 notes
  /skill random-walk --count 10         # Explore 10 random notes
  /skill random-walk --topic "AI"       # Random walk focused on AI topic
  /skill random-walk --save             # Save research exploration note
"""
    )
    
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of random notes to select (default: 5)"
    )
    
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Focus random walk on a specific topic"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save research exploration note to vault"
    )
    
    args = parser.parse_args()
    
    if TRACKER:
        TRACKER.record_operation(
            script_name="random_walk.py",
            operation_type="random_walk",
            status="in_progress",
            metrics={"count": args.count, "topic": args.topic},
        )
    
    print("🎲 Starting Random Walk through your vault...")
    print(f"📊 Selecting {args.count} random notes...")
    
    # Select random notes
    random_notes = select_random_notes(args.count, args.topic)
    
    if not random_notes:
        print("❌ No notes found matching criteria.")
        if TRACKER:
            TRACKER.record_operation(
                script_name="random_walk.py",
                operation_type="random_walk",
                status="failed",
                metrics={"error": "No notes found"},
            )
        return
    
    print(f"✅ Found {len(random_notes)} notes:")
    for note in random_notes:
        print(f"  - [[{note['title']}]]")
    
    # Trace a connection path from the first note
    print("\n🔍 Tracing connection path...")
    start_note = random_notes[0]
    connection_path = trace_connection_path(start_note)
    
    if len(connection_path) > 1:
        path_str = " → ".join(f"[[{n['title']}]]" for n in connection_path)
        print(f"✅ Discovery path: {path_str}")
    else:
        print("ℹ️  No outgoing links found from starting note")
    
    # Build prompt and get AI analysis
    print("\n🧠 Analyzing discoveries...")
    prompt = build_research_prompt(random_notes, connection_path, args.topic)
    combined_content = "\n\n".join(n['content'] for n in random_notes + connection_path)
    
    research_result = summarize(combined_content[:150000], prompt)
    
    # Save if requested
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_path = f"Sources/Random Walk - {date_str}.md"
        save_note(save_path, research_result)
        print(f"\n💾 Research exploration saved to: {save_path}")
    
    print("\n" + "="*60)
    print(research_result)
    print("="*60)
    
    if TRACKER:
        TRACKER.record_operation(
            script_name="random_walk.py",
            operation_type="random_walk",
            status="success",
            metrics={
                "count": args.count,
                "topic": args.topic,
                "notes_found": len(random_notes),
                "path_length": len(connection_path),
            },
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="random_walk.py",
                operation_type="random_walk",
                status="failed",
                metrics={"error": str(e)},
            )
        import traceback
        traceback.print_exc()
        sys.exit(1)
