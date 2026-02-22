"""Backup System - Comprehensive backup for personal AI infrastructure.

Backup important components:
- Files (Obsidian vault)
- Docs (important documents)
- Important thoughts (key notes)
- AI system (scripts and configuration)
- Profile (personal information)
- Memory (LLM context)
"""

import argparse
import sys
import os
import shutil
import tarfile
from pathlib import Path
from datetime import datetime

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import save_note, VAULT_PATH


def create_backup(backup_dir: Path, components: list = None) -> Path:
    """Create a backup of the specified components.
    
    Args:
        backup_dir: Directory to store backups
        components: List of components to backup (defaults to all)
    
    Returns:
        Path to the created backup archive
    """
    if components is None:
        components = ['files', 'docs', 'thoughts', 'ai-system', 'profile', 'memory']
    
    # Create backup directory if it doesn't exist
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamp for backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"pai_backup_{timestamp}"
    backup_path = backup_dir / backup_name
    
    # Create temporary directory for backup
    temp_backup = backup_dir / f"temp_{backup_name}"
    temp_backup.mkdir(exist_ok=True)
    
    try:
        # Backup files (Obsidian vault)
        if 'files' in components:
            print("Backing up files (Obsidian vault)...")
            vault_backup = temp_backup / "vault"
            shutil.copytree(VAULT_PATH, vault_backup, 
                           ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '.DS_Store', '.ruff_cache'))
        
        # Backup docs (important documents)
        if 'docs' in components:
            print("Backing up docs...")
            docs_backup = temp_backup / "docs"
            docs_dir = VAULT_PATH / "Sources"
            if docs_dir.exists():
                shutil.copytree(docs_dir, docs_backup)
        
        # Backup important thoughts (key notes)
        if 'thoughts' in components:
            print("Backing up important thoughts...")
            thoughts_backup = temp_backup / "thoughts"
            thoughts_dirs = [
                VAULT_PATH / "Atlas",
                VAULT_PATH / "00 - Inbox",
            ]
            thoughts_backup.mkdir(exist_ok=True)
            for thoughts_dir in thoughts_dirs:
                if thoughts_dir.exists():
                    dest = thoughts_backup / thoughts_dir.name
                    shutil.copytree(thoughts_dir, dest)
        
        # Backup AI system (scripts and configuration)
        if 'ai-system' in components:
            print("Backing up AI system...")
            ai_backup = temp_backup / "ai_system"
            scripts_dir = VAULT_PATH / "_scripts"
            claude_dir = VAULT_PATH / ".claude"
            ai_backup.mkdir(exist_ok=True)
            
            if scripts_dir.exists():
                shutil.copytree(scripts_dir, ai_backup / "_scripts")
            if claude_dir.exists():
                shutil.copytree(claude_dir, ai_backup / ".claude")
            
            # Backup .env file if exists
            env_file = VAULT_PATH / ".env"
            if env_file.exists():
                shutil.copy2(env_file, ai_backup / ".env")
        
        # Backup profile (personal information)
        if 'profile' in components:
            print("Backing up profile...")
            profile_backup = temp_backup / "profile"
            profile_dir = VAULT_PATH / "LLM Context" / "Personal Profile"
            if profile_dir.exists():
                shutil.copytree(profile_dir, profile_backup)
        
        # Backup memory (LLM context)
        if 'memory' in components:
            print("Backing up memory...")
            memory_backup = temp_backup / "memory"
            memory_dir = VAULT_PATH / "LLM Context"
            if memory_dir.exists():
                shutil.copytree(memory_dir, memory_backup)
        
        # Create tar.gz archive
        print(f"Creating backup archive: {backup_name}.tar.gz")
        archive_path = backup_dir / f"{backup_name}.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(temp_backup, arcname=backup_name)
        
        print(f"Backup created successfully: {archive_path}")
        
        # Clean up temporary directory
        shutil.rmtree(temp_backup)
        
        return archive_path
        
    except Exception as e:
        # Clean up on error
        if temp_backup.exists():
            shutil.rmtree(temp_backup)
        raise


def list_backups(backup_dir: Path) -> list:
    """List all available backups.
    
    Args:
        backup_dir: Directory containing backups
    
    Returns:
        List of backup files sorted by date (newest first)
    """
    if not backup_dir.exists():
        return []
    
    backups = list(backup_dir.glob("pai_backup_*.tar.gz"))
    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return backups


def get_backup_info(backup_path: Path) -> dict:
    """Get information about a backup.
    
    Args:
        backup_path: Path to backup archive
    
    Returns:
        Dictionary with backup information
    """
    if not backup_path.exists():
        return {}
    
    stat = backup_path.stat()
    timestamp = datetime.fromtimestamp(stat.st_mtime)
    
    # Extract backup name components
    name = backup_path.stem
    parts = name.split('_')
    if len(parts) >= 4:
        date_str = parts[2]
        time_str = parts[3]
    
    return {
        'path': backup_path,
        'size': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'created': timestamp,
        'name': name
    }


def main():
    """Main function for the backup skill."""
    parser = argparse.ArgumentParser(
        description="Backup System - Comprehensive backup for personal AI infrastructure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill ackup                           # Full backup
  /skill ackup --list                   # List backups
  /skill ackup --components files docs  # Backup specific components
  /skill ackup --dir ~/backups          # Specify backup directory
"""
    )
    
    parser.add_argument(
        "--dir",
        type=str,
        default=str(Path.home() / "pai_backups"),
        help="Directory to store backups (default: ~/pai_backups)"
    )
    
    parser.add_argument(
        "--components",
        type=str,
        nargs='+',
        choices=['files', 'docs', 'thoughts', 'ai-system', 'profile', 'memory'],
        default=None,
        help="Components to backup (default: all)"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available backups"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save backup report to vault"
    )
    
    args = parser.parse_args()
    
    backup_dir = Path(args.dir)
    
    if args.list:
        # List backups
        backups = list_backups(backup_dir)
        
        if not backups:
            print("No backups found.")
            return
        
        print(f"Found {len(backups)} backup(s):\n")
        for i, backup in enumerate(backups, 1):
            info = get_backup_info(backup)
            print(f"{i}. {info['name']}")
            print(f"   Created: {info['created'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Size: {info['size_mb']} MB")
            print()
        
        return
    
    # Create backup
    print("=" * 60)
    print("Personal AI Infrastructure Backup")
    print("=" * 60)
    print()
    
    try:
        backup_path = create_backup(backup_dir, args.components)
        info = get_backup_info(backup_path)
        
        # Generate report
        report = f"""# Backup Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Backup Summary

- **Backup File**: {info['name']}.tar.gz
- **Location**: {backup_path}
- **Size**: {info['size_mb']} MB
- **Created**: {info['created'].strftime('%Y-%m-%d %H:%M:%S')}

## Components Backed Up

"""
        
        if args.components:
            for component in args.components:
                report += f"- {component}\n"
        else:
            report += """- files (Obsidian vault)
- docs (important documents)
- thoughts (important notes)
- ai-system (AI scripts and configuration)
- profile (personal information)
- memory (LLM context)
"""
        
        report += f"""
## Restore Instructions

To restore from this backup:

```bash
# Create temporary directory
mkdir -p /tmp/pai_restore
cd /tmp/pai_restore

# Extract backup
tar -xzf {backup_path}

# Copy components back to vault as needed
```

---
*Backup created by PAI Backup System*
"""
        
        if args.save:
            date_str = datetime.now().strftime("%Y-%m-%d")
            save_note(f"Sources/Backup Report - {date_str}.md", report)
        
        print()
        print("=" * 60)
        print("Backup completed successfully!")
        print("=" * 60)
        print()
        print(report)
        
    except Exception as e:
        print(f"Error creating backup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
