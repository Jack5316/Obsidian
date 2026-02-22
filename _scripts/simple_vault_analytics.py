#!/usr/bin/env python3
"""Simple Obsidian Vault Analytics - No CLI dependency.

This script provides basic analytics by directly parsing the vault files.
"""

import os
import re
from pathlib import Path
from collections import Counter
from datetime import datetime

VAULT_PATH = Path(__file__).resolve().parent.parent


def count_files():
    """Count files by type."""
    total_files = 0
    md_files = 0
    other_files = 0
    ext_counts = Counter()

    for root, dirs, files in os.walk(VAULT_PATH):
        # Skip hidden directories (including .obsidian, .git, etc.)
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            total_files += 1
            ext = Path(file).suffix.lower()
            ext_counts[ext] += 1
            
            if ext == '.md':
                md_files += 1
            else:
                other_files += 1
    
    return {
        'total': total_files,
        'markdown': md_files,
        'other': other_files,
        'extensions': ext_counts
    }


def count_tags():
    """Count tag usage."""
    tags = Counter()
    
    for root, dirs, files in os.walk(VAULT_PATH):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find tags in format #tag or #tag/subtag
                found_tags = re.findall(r'#(\w[\w/-]*)', content)
                for tag in found_tags:
                    tags[tag] += 1
    
    # Convert to list of dicts with count
    tag_list = [{'tag': tag, 'count': count} for tag, count in tags.items()]
    tag_list.sort(key=lambda x: x['count'], reverse=True)
    
    return tag_list


def count_links():
    """Count internal links."""
    links = []
    
    for root, dirs, files in os.walk(VAULT_PATH):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find internal links [[Link]] or [[Path/File|Alias]]
                found_links = re.findall(r'\[\[([^\]]*)\]\]', content)
                links.extend(found_links)
    
    return Counter(links)


def count_tasks():
    """Count tasks by status."""
    total_tasks = 0
    todo_tasks = 0
    done_tasks = 0
    
    for root, dirs, files in os.walk(VAULT_PATH):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find tasks in format - [ ] or - [x]
                task_lines = re.findall(r'^.*?(\[.\]).*$', content, re.MULTILINE)
                
                for task in task_lines:
                    total_tasks += 1
                    if task == '[ ]':
                        todo_tasks += 1
                    elif task == '[x]' or task == '[X]':
                        done_tasks += 1
    
    return {
        'total': total_tasks,
        'todo': todo_tasks,
        'done': done_tasks,
        'completion_rate': (done_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }


def count_folders():
    """Count top-level folders (excluding hidden ones)."""
    folders = []
    for item in os.listdir(VAULT_PATH):
        item_path = os.path.join(VAULT_PATH, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            folders.append(item)
    
    return len(folders), folders


def main():
    print("\n=== Simple Obsidian Vault Analytics ===")
    
    # File Statistics
    file_counts = count_files()
    print(f"\n📁 File Statistics:")
    print(f"  Total files: {file_counts['total']}")
    print(f"  Markdown files: {file_counts['markdown']}")
    print(f"  Other files: {file_counts['other']}")
    print(f"  File types:")
    for ext, count in file_counts['extensions'].most_common(10):
        print(f"    {ext}: {count}")
    
    # Folder Statistics
    folder_count, folders = count_folders()
    print(f"\n📂 Folder Statistics:")
    print(f"  Total folders: {folder_count}")
    print(f"  Top-level folders: {', '.join(folders)}")
    
    # Tag Analysis
    tags = count_tags()
    print(f"\n🏷️ Tag Analysis:")
    print(f"  Total tags: {len(tags)}")
    print(f"  Top 10 tags:")
    for tag in tags[:10]:
        print(f"    #{tag['tag']}: {tag['count']}")
    
    # Link Analysis
    links = count_links()
    print(f"\n🔗 Link Analysis:")
    print(f"  Total internal links: {sum(links.values())}")
    print(f"  Unique internal links: {len(links)}")
    print(f"  Top 10 linked files:")
    for link, count in links.most_common(10):
        print(f"    [[{link}]]: {count}")
    
    # Task Analysis
    tasks = count_tasks()
    print(f"\n✅ Task Analysis:")
    print(f"  Total tasks: {tasks['total']}")
    print(f"  TODO tasks: {tasks['todo']}")
    print(f"  Done tasks: {tasks['done']}")
    print(f"  Completion rate: {tasks['completion_rate']:.1f}%")
    
    # Vault Size
    total_size = 0
    for root, dirs, files in os.walk(VAULT_PATH):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
    size_mb = total_size / (1024 * 1024)
    print(f"\n💾 Vault Size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()