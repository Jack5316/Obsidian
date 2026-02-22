"""Clean Redundant Notes - Find and remove redundant notes with user permission.

This skill identifies redundant notes in your Obsidian vault:
- Exact duplicates (identical content)
- Empty or stub notes (minimal content)
- Near-duplicates (highly similar content, optional)

Always asks for explicit permission before removing any file.
"""

import argparse
import hashlib
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import VAULT_PATH, save_note


# Directories to exclude from scanning (templates, config, etc.)
EXCLUDE_DIRS = {".obsidian", ".trash", "node_modules", ".git", "_scripts", ".claude"}

# Minimum content length (chars) to consider a note non-stub
STUB_THRESHOLD = 50


def _normalize_content(text: str) -> str:
    """Normalize content for comparison (strip whitespace, normalize newlines)."""
    return text.strip().replace("\r\n", "\n").replace("\r", "\n")


def _content_hash(text: str) -> str:
    """Compute SHA256 hash of normalized content."""
    return hashlib.sha256(_normalize_content(text).encode("utf-8")).hexdigest()


def _is_excluded(rel_path: str) -> bool:
    """Check if path is in an excluded directory."""
    parts = Path(rel_path).parts
    return any(part in EXCLUDE_DIRS for part in parts)


def find_markdown_files(vault_path: Path) -> List[Path]:
    """Find all markdown files in vault, excluding certain directories."""
    files = []
    for md in vault_path.rglob("*.md"):
        try:
            rel = md.relative_to(vault_path)
            if not _is_excluded(str(rel)):
                files.append(md)
        except ValueError:
            continue
    return files


def find_exact_duplicates(files: List[Path]) -> Dict[str, List[Path]]:
    """Find files with identical content (content hash)."""
    hash_to_files: Dict[str, List[Path]] = defaultdict(list)
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            h = _content_hash(content)
            hash_to_files[h].append(f)
        except (OSError, UnicodeDecodeError):
            continue
    return {h: paths for h, paths in hash_to_files.items() if len(paths) > 1}


def find_stub_notes(files: List[Path]) -> List[Tuple[Path, int]]:
    """Find empty or nearly empty notes."""
    stubs = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            # Remove YAML frontmatter for length check
            text = content.strip()
            if text.startswith("---"):
                end = text.find("---", 3)
                if end != -1:
                    text = text[end + 3:].strip()
            body_len = len(_normalize_content(text))
            if body_len < STUB_THRESHOLD:
                stubs.append((f, body_len))
        except (OSError, UnicodeDecodeError):
            continue
    return stubs


def find_near_duplicates(files: List[Path], similarity_threshold: float = 0.9) -> List[Tuple[Path, Path, float]]:
    """Find pairs of notes with highly similar content (optional, slower)."""
    from difflib import SequenceMatcher

    pairs = []
    contents: Dict[Path, str] = {}
    for f in files:
        try:
            contents[f] = _normalize_content(f.read_text(encoding="utf-8", errors="ignore"))
        except (OSError, UnicodeDecodeError):
            continue

    checked = set()
    for p1, c1 in contents.items():
        for p2, c2 in contents.items():
            if p1 >= p2 or (p1, p2) in checked:
                continue
            checked.add((p1, p2))
            if len(c1) < 100 or len(c2) < 100:
                continue
            ratio = SequenceMatcher(None, c1, c2).ratio()
            if ratio >= similarity_threshold:
                pairs.append((p1, p2, ratio))
    return pairs


def format_report(
    duplicates: Dict[str, List[Path]],
    stubs: List[Tuple[Path, int]],
    near_dups: Optional[List[Tuple[Path, Path, float]]] = None,
) -> str:
    """Format scan report as markdown."""
    lines = ["# Redundant Notes Report", ""]

    # Exact duplicates
    if duplicates:
        lines.append("## Exact Duplicates (identical content)")
        lines.append("")
        for h, paths in duplicates.items():
            lines.append(f"**Group ({len(paths)} files):**")
            for p in sorted(paths, key=lambda x: str(x)):
                rel = p.relative_to(VAULT_PATH)
                lines.append(f"- `{rel}`")
            lines.append("")
    else:
        lines.append("## Exact Duplicates")
        lines.append("None found.")
        lines.append("")

    # Stub notes
    if stubs:
        lines.append("## Empty / Stub Notes (< 50 chars)")
        lines.append("")
        for p, length in sorted(stubs, key=lambda x: (x[1], str(x[0]))):
            rel = p.relative_to(VAULT_PATH)
            lines.append(f"- `{rel}` ({length} chars)")
        lines.append("")
    else:
        lines.append("## Empty / Stub Notes")
        lines.append("None found.")
        lines.append("")

    # Near-duplicates (optional)
    if near_dups:
        lines.append("## Near-Duplicates (≥90% similar)")
        lines.append("")
        for p1, p2, ratio in near_dups[:20]:  # Limit to 20 pairs
            r1 = p1.relative_to(VAULT_PATH)
            r2 = p2.relative_to(VAULT_PATH)
            lines.append(f"- `{r1}` ↔ `{r2}` ({ratio:.0%} similar)")
        if len(near_dups) > 20:
            lines.append(f"- ... and {len(near_dups) - 20} more pairs")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Find and remove redundant notes with your permission",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/clean_redundant.py scan              # Scan only, no removal
  python3 _scripts/clean_redundant.py scan --save         # Scan and save report
  python3 _scripts/clean_redundant.py clean             # Scan, then ask before removing
  python3 _scripts/clean_redundant.py clean --stubs     # Only remove stub notes
  python3 _scripts/clean_redundant.py clean --duplicates # Only remove duplicates (keeps one)
""",
    )
    parser.add_argument(
        "mode",
        choices=["scan", "clean"],
        help="scan: find only, no removal. clean: find and remove with permission",
    )
    parser.add_argument(
        "--duplicates",
        action="store_true",
        help="Include exact duplicates in removal (keeps one copy per group)",
    )
    parser.add_argument(
        "--stubs",
        action="store_true",
        help="Include empty/stub notes in removal",
    )
    parser.add_argument(
        "--near-duplicates",
        action="store_true",
        help="Include near-duplicates (≥90%% similar) - slower, requires manual review",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save scan report to Sources/Clean Report - YYYY-MM-DD.md",
    )
    parser.add_argument(
        "--folder",
        type=str,
        default=None,
        help="Limit scan to a specific folder (e.g., Sources, Atlas)",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation (use with caution)",
    )

    args = parser.parse_args()

    # Default: if neither specified, include both
    if not args.duplicates and not args.stubs and not args.near_duplicates:
        args.duplicates = True
        args.stubs = True

    vault = VAULT_PATH
    if not vault.exists():
        print(f"Error: Vault path not found: {vault}")
        sys.exit(1)

    # Collect files
    all_files = find_markdown_files(vault)
    if args.folder:
        folder_path = vault / args.folder
        all_files = [f for f in all_files if str(f).startswith(str(folder_path))]
    print(f"Scanning {len(all_files)} markdown files...")

    # Run detection
    duplicates = find_exact_duplicates(all_files)
    stubs = find_stub_notes(all_files)
    near_dups = None
    if args.near_duplicates:
        print("Checking near-duplicates (this may take a moment)...")
        near_dups = find_near_duplicates(all_files)

    report = format_report(duplicates, stubs, near_dups)
    print(report)

    if args.save:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_note(f"Sources/Clean Report - {date_str}.md", report)

    if args.mode != "clean":
        return

    # Build removal list
    to_remove: List[Path] = []
    kept_for_duplicates: Dict[str, Path] = {}  # hash -> path to keep

    if args.duplicates and duplicates:
        for h, paths in duplicates.items():
            sorted_paths = sorted(paths, key=lambda p: (len(str(p)), str(p)))
            kept_for_duplicates[h] = sorted_paths[0]
            to_remove.extend(sorted_paths[1:])

    if args.stubs and stubs:
        kept_set = set(kept_for_duplicates.values())
        for p, _ in stubs:
            if p not in kept_set:
                to_remove.append(p)

    # Near-duplicates: we don't auto-remove; user must review manually
    if args.near_duplicates and near_dups:
        print("\nNote: Near-duplicates require manual review. Not auto-removed.")

    if not to_remove:
        print("\nNo files scheduled for removal.")
        return

    # Deduplicate (stub might also be in a duplicate group)
    to_remove = list(dict.fromkeys(to_remove))

    print(f"\n--- Removal Summary ---")
    print(f"Files to remove: {len(to_remove)}")
    for p in sorted(to_remove, key=lambda x: str(x)):
        rel = p.relative_to(vault)
        print(f"  - {rel}")

    if not args.yes:
        response = input("\nProceed with removal? [y/N]: ").strip().lower()
        if response not in ("y", "yes"):
            print("Aborted. No files removed.")
            return

    removed = 0
    for p in to_remove:
        try:
            p.unlink()
            print(f"Removed: {p.relative_to(vault)}")
            removed += 1
        except OSError as e:
            print(f"Error removing {p}: {e}")

    print(f"\nDone. Removed {removed} files.")


if __name__ == "__main__":
    main()
