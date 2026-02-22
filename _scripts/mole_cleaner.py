"""Mole Mac Storage Cleaner - Clean your Mac storage with common cleaning tasks.

Inspired by https://github.com/tw93/Mole, this skill helps you free up disk space
on your Mac by cleaning temporary files, caches, logs, and other unnecessary files.
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import save_note, VAULT_PATH


def get_folder_size(path: Path) -> int:
    """Calculate total size of a folder in bytes."""
    total_size = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass
    return total_size


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def clean_directory(path: Path, dry_run: bool = False) -> tuple[int, int]:
    """Clean a directory and return (number of files cleaned, bytes freed)."""
    files_cleaned = 0
    bytes_freed = 0
    
    if not path.exists():
        return files_cleaned, bytes_freed
    
    try:
        for item in path.iterdir():
            try:
                if item.is_file():
                    size = item.stat().st_size
                    if not dry_run:
                        item.unlink()
                    files_cleaned += 1
                    bytes_freed += size
                elif item.is_dir():
                    dir_size = get_folder_size(item)
                    if not dry_run:
                        shutil.rmtree(item)
                    files_cleaned += 1
                    bytes_freed += dir_size
            except (OSError, PermissionError):
                continue
    except (OSError, PermissionError):
        pass
    
    return files_cleaned, bytes_freed


class MacCleaner:
    """Mac storage cleaning engine."""
    
    def __init__(self):
        self.home = Path.home()
        self.cleaning_tasks = [
            {
                "name": "User Cache",
                "paths": [self.home / "Library" / "Caches"],
                "description": "Application cache files"
            },
            {
                "name": "User Logs",
                "paths": [self.home / "Library" / "Logs"],
                "description": "Application log files"
            },
            {
                "name": "System Cache",
                "paths": [Path("/Library/Caches")],
                "description": "System cache files"
            },
            {
                "name": "System Logs",
                "paths": [Path("/Library/Logs")],
                "description": "System log files"
            },
            {
                "name": "Xcode Derived Data",
                "paths": [self.home / "Library" / "Developer" / "Xcode" / "DerivedData"],
                "description": "Xcode build artifacts"
            },
            {
                "name": "Xcode Archives",
                "paths": [self.home / "Library" / "Developer" / "Xcode" / "Archives"],
                "description": "Xcode archive files"
            },
            {
                "name": "iOS Device Support",
                "paths": [self.home / "Library" / "Developer" / "Xcode" / "iOS DeviceSupport"],
                "description": "iOS device support files"
            },
            {
                "name": "iOS Simulator",
                "paths": [self.home / "Library" / "Developer" / "CoreSimulator"],
                "description": "iOS simulator data"
            },
            {
                "name": "Trash",
                "paths": [self.home / ".Trash"],
                "description": "Trash bin"
            },
            {
                "name": "Downloads",
                "paths": [self.home / "Downloads"],
                "description": "Downloads folder (old files)",
                "optional": True
            }
        ]
    
    def analyze(self) -> dict:
        """Analyze storage without cleaning."""
        results = []
        total_potential = 0
        
        print("=== Analyzing Mac Storage ===\n")
        
        for task in self.cleaning_tasks:
            task_size = 0
            task_files = 0
            
            for path in task["paths"]:
                if path.exists():
                    size = get_folder_size(path)
                    task_size += size
                    # Count files
                    try:
                        task_files += len(list(path.rglob('*')))
                    except (OSError, PermissionError):
                        pass
            
            total_potential += task_size
            results.append({
                "name": task["name"],
                "description": task["description"],
                "size": task_size,
                "files": task_files,
                "optional": task.get("optional", False)
            })
            
            status = "✓" if task_size > 0 else " "
            print(f"{status} {task['name']}: {format_size(task_size)} in {task_files} items")
        
        return {
            "analysis_date": datetime.now().isoformat(),
            "tasks": results,
            "total_potential": total_potential
        }
    
    def clean(self, include_optional: bool = False, dry_run: bool = False) -> dict:
        """Clean storage and return results."""
        results = []
        total_cleaned = 0
        total_files = 0
        
        mode = "Dry Run" if dry_run else "Cleaning"
        print(f"=== {mode} Mac Storage ===\n")
        
        for task in self.cleaning_tasks:
            if task.get("optional", False) and not include_optional:
                print(f"⏭️  Skipping {task['name']} (optional, use --optional to include)")
                continue
            
            task_cleaned = 0
            task_files = 0
            
            for path in task["paths"]:
                files, size = clean_directory(path, dry_run=dry_run)
                task_files += files
                task_cleaned += size
            
            total_cleaned += task_cleaned
            total_files += task_files
            
            results.append({
                "name": task["name"],
                "description": task["description"],
                "size_cleaned": task_cleaned,
                "files_cleaned": task_files,
                "optional": task.get("optional", False)
            })
            
            if task_files > 0:
                status = "🔍" if dry_run else "🧹"
                print(f"{status} {task['name']}: {format_size(task_cleaned)} from {task_files} items")
        
        return {
            "clean_date": datetime.now().isoformat(),
            "dry_run": dry_run,
            "tasks": results,
            "total_cleaned": total_cleaned,
            "total_files": total_files
        }


def format_analysis_report(analysis: dict) -> str:
    """Format analysis report as markdown."""
    md = f"""# Mac Storage Analysis Report

Generated on: {analysis['analysis_date']}

## 📊 Summary

**Total Potential Space to Free**: {format_size(analysis['total_potential'])}

## 📁 Breakdown by Category

| Category | Potential Space | Items | Optional |
|----------|-----------------|-------|----------|
"""
    
    for task in analysis['tasks']:
        optional = "✓" if task['optional'] else ""
        md += f"| {task['name']} | {format_size(task['size'])} | {task['files']} | {optional} |\n"
    
    md += """
## 🧹 Recommendations

1. **Run Dry Run First**: Use `--dry-run` to preview what will be cleaned
2. **Optional Categories**: Use `--optional` to include Downloads folder
3. **Safety First**: Always review before permanent deletion
4. **Regular Maintenance**: Consider monthly cleaning to keep your Mac fast

---

*Report generated by Mole Mac Storage Cleaner*
"""
    return md


def format_cleaning_report(cleaning: dict) -> str:
    """Format cleaning report as markdown."""
    mode = "Dry Run" if cleaning['dry_run'] else "Cleaning"
    md = f"""# Mac Storage {mode} Report

Generated on: {cleaning['clean_date']}

## 📊 Summary

**Total Space {mode}d**: {format_size(cleaning['total_cleaned'])}  
**Total Items {mode}d**: {cleaning['total_files']}

## 📁 Breakdown by Category

| Category | Space {mode}d | Items {mode}d |
|----------|----------------|---------------|
"""
    
    for task in cleaning['tasks']:
        md += f"| {task['name']} | {format_size(task['size_cleaned'])} | {task['files_cleaned']} |\n"
    
    md += f"""
## 💡 Next Steps

{'**This was a dry run - no files were actually deleted.**' if cleaning['dry_run'] else '**Cleaning complete!**'}

{'Run without `--dry-run` to actually clean your Mac.' if cleaning['dry_run'] else 'Restart applications for best performance.'}

---

*Report generated by Mole Mac Storage Cleaner*
"""
    return md


def main():
    """Main function to run Mac storage cleaner."""
    parser = argparse.ArgumentParser(
        description="Mole Mac Storage Cleaner - Clean your Mac storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill mole                    # Analyze storage only
  /skill mole --dry-run          # Preview cleaning
  /skill mole --clean            # Clean storage (safe categories)
  /skill mole --clean --optional # Clean all including Downloads
  /skill mole --save             # Save report to vault
"""
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Perform actual cleaning (default: analyze only)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be cleaned without deleting"
    )
    
    parser.add_argument(
        "--optional",
        action="store_true",
        help="Include optional categories (Downloads folder)"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to vault"
    )
    
    args = parser.parse_args()
    
    cleaner = MacCleaner()
    
    if args.clean or args.dry_run:
        result = cleaner.clean(include_optional=args.optional, dry_run=args.dry_run)
        report = format_cleaning_report(result)
    else:
        result = cleaner.analyze()
        report = format_analysis_report(result)
    
    print("\n" + "="*50 + "\n")
    print(report)
    
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        report_type = "Cleaning" if args.clean or args.dry_run else "Analysis"
        save_path = f"Sources/Mole {report_type} - {date_str}.md"
        save_note(save_path, report)
        print(f"\n✓ Report saved to: {save_path}")


if __name__ == "__main__":
    main()

