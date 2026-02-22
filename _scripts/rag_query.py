"""RAG Query - Retrieval-Augmented Generation over your Obsidian vault.

Inspired by LightRAG (https://github.com/HKUDS/LightRAG). Queries your vault using
hybrid retrieval: keyword search + knowledge graph expansion via wikilinks.
Uses AI only for synthesis—retrieval is deterministic Python.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH, TRACKER

# Directories to exclude from search
EXCLUDE_DIRS = {".git", ".obsidian", ".claude", ".cursor", "_scripts", "_org", "_logs", ".ruff_cache"}

# Max chars per note in context (avoid token overflow)
MAX_CHARS_PER_NOTE = 3000
MAX_TOTAL_CONTEXT = 25000


def find_markdown_files() -> List[Path]:
    """Find all markdown files in the vault."""
    files = []
    for item in VAULT_PATH.iterdir():
        if item.is_dir() and item.name in EXCLUDE_DIRS:
            continue
        if item.is_dir():
            for md in item.rglob("*.md"):
                if any(p.name in EXCLUDE_DIRS for p in md.relative_to(VAULT_PATH).parents):
                    continue
                files.append(md)
        elif item.suffix == ".md":
            files.append(item)
    return files


def search_vault_keyword(query: str, limit: int = 20) -> List[Path]:
    """Search vault using ripgrep for keyword matches."""
    try:
        result = subprocess.run(
            ["rg", "-l", "-i", "-F", "--max-count", "1", query, str(VAULT_PATH)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0 and result.stderr and "No matches" not in result.stderr:
            return []
        lines = [p.strip() for p in result.stdout.strip().split("\n") if p.strip()]
        paths = []
        for line in lines:
            p = Path(line)
            if p.suffix != ".md":
                continue
            try:
                if not p.is_absolute():
                    p = (VAULT_PATH / p).resolve()
                if p.exists() and str(VAULT_PATH) in str(p.resolve()):
                    paths.append(p)
            except (OSError, RuntimeError):
                pass
        return paths[:limit] if paths else []
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def read_note(path: Path) -> Optional[Dict]:
    """Read and parse a note file."""
    try:
        content = path.read_text(encoding="utf-8")
        body = content
        fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if fm_match:
            body = content[fm_match.end() :]
        wikilinks = re.findall(r"\[\[([^\]]+)\]\]", body)
        return {
            "path": path,
            "relative_path": str(path.relative_to(VAULT_PATH)),
            "title": path.stem,
            "content": body,
            "wikilinks": wikilinks,
        }
    except Exception:
        return None


def expand_via_graph(
    seed_paths: List[Path],
    all_files: List[Path],
    depth: int = 1,
    max_extra: int = 10,
) -> List[Path]:
    """Expand retrieval via wikilink graph (LightRAG-style local context)."""
    seen_resolved: Set[Path] = {p.resolve() for p in seed_paths}
    result: List[Path] = list(seed_paths)
    title_to_path: Dict[str, Path] = {}
    for f in all_files:
        title_to_path[f.stem] = f
        title_to_path[f.stem.lower()] = f

    current = list(seed_paths)
    for _ in range(depth):
        next_batch: List[Path] = []
        for p in current:
            note = read_note(p)
            if not note:
                continue
            for link in note["wikilinks"]:
                target = link.split("|")[0].strip()
                cand = title_to_path.get(target) or title_to_path.get(target.lower())
                if cand and cand.resolve() not in seen_resolved:
                    seen_resolved.add(cand.resolve())
                    next_batch.append(cand)
                    result.append(cand)
        current = next_batch[:max_extra]
        if not current:
            break

    return result


def build_context(
    paths: List[Path],
    mode: str,
    query: str,
) -> str:
    """Build context string for LLM from retrieved notes."""
    parts = []
    total = 0
    for p in paths:
        note = read_note(p)
        if not note or len(note["content"].strip()) < 20:
            continue
        excerpt = note["content"][:MAX_CHARS_PER_NOTE]
        if len(note["content"]) > MAX_CHARS_PER_NOTE:
            excerpt += "\n[... truncated ...]"
        block = f"---\n**[[{note['title']}]]** ({note['relative_path']})\n\n{excerpt}"
        if total + len(block) > MAX_TOTAL_CONTEXT:
            break
        parts.append(block)
        total += len(block)
    return "\n\n".join(parts)


RAG_SYSTEM_PROMPT = """You are a retrieval-augmented assistant querying a personal knowledge base (Obsidian vault).
Use ONLY the retrieved context to answer the user's question. Do not invent information.
- Answer based strictly on the context. If the context doesn't contain enough information, say so.
- Use [[wikilinks]] when referencing notes.
- Be concise but thorough. Cite specific notes when making claims.
- If multiple notes conflict, acknowledge the different perspectives."""


def build_user_message(query: str, mode: str, context: str) -> str:
    """Build the user message with query and context."""
    return f"""**User question:** {query}

**Retrieval mode:** {mode}
- naive: Direct keyword matches only
- local: Keyword + graph expansion via wikilinks (local context)
- hybrid: Local + global combined

**Retrieved context:**
{context}"""


def main():
    """Main RAG query entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Query - Retrieval-Augmented Generation over your Obsidian vault (LightRAG-inspired)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/rag_query.py "What do I know about AI agents?"
  python3 _scripts/rag_query.py "Summarize my notes on habits" --mode hybrid
  python3 _scripts/rag_query.py "Key insights on productivity" --save
  python3 _scripts/rag_query.py "Connections between X and Y" --top-k 15
""",
    )
    parser.add_argument("query", type=str, help="Question to answer from vault content")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["naive", "local", "global", "hybrid"],
        default="hybrid",
        help="Retrieval mode (default: hybrid)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=12,
        help="Max number of notes to retrieve (default: 12)",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Graph expansion depth for local/hybrid (default: 1)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save response to Sources/RAG Query - YYYY-MM-DD.md",
    )
    args = parser.parse_args()

    if TRACKER:
        TRACKER.record_operation(
            script_name="rag_query.py",
            operation_type="rag_query",
            status="in_progress",
            metrics={"query": args.query[:50], "mode": args.mode},
        )

    print("🔍 RAG Query (LightRAG-inspired)")
    print(f"   Query: {args.query}")
    print(f"   Mode: {args.mode}")

    all_files = find_markdown_files()
    seed_paths = search_vault_keyword(args.query, limit=args.top_k)

    if not seed_paths:
        # Fallback: scan all files for keyword
        query_lower = args.query.lower()
        for f in all_files:
            if len(seed_paths) >= args.top_k:
                break
            try:
                if query_lower in f.read_text(encoding="utf-8").lower():
                    seed_paths.append(f)
            except Exception:
                pass

    if not seed_paths:
        print("❌ No matching notes found.")
        if TRACKER:
            TRACKER.record_operation(
                script_name="rag_query.py",
                operation_type="rag_query",
                status="failed",
                metrics={"error": "No matches"},
            )
        return

    # Resolve to Path objects
    seed_paths = [p if isinstance(p, Path) else Path(p) for p in seed_paths]

    if args.mode in ("local", "hybrid"):
        expanded = expand_via_graph(
            seed_paths,
            all_files,
            depth=args.depth,
            max_extra=max(5, args.top_k // 2),
        )
        paths = list(expanded)[: args.top_k * 2]
    else:
        paths = seed_paths[: args.top_k]

    context = build_context(paths, args.mode, args.query)
    user_message = build_user_message(
        args.query,
        args.mode,
        context or "(No context retrieved)",
    )

    print(f"   Retrieved {len(paths)} notes")
    for p in paths[:8]:
        try:
            rel = p.relative_to(VAULT_PATH)
        except (ValueError, TypeError):
            rel = p.name
        print(f"   - {rel}")

    print("\n🧠 Generating response...")
    response = summarize(user_message, RAG_SYSTEM_PROMPT)

    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_path = f"Sources/RAG Query - {date_str}.md"
        content = f"# RAG Query: {args.query}\n\n**Mode:** {args.mode} | **Date:** {date_str}\n\n---\n\n{response}"
        save_note(save_path, content)
        print(f"\n💾 Saved to: {save_path}")

    print("\n" + "=" * 60)
    print(response)
    print("=" * 60)

    if TRACKER:
        TRACKER.record_operation(
            script_name="rag_query.py",
            operation_type="rag_query",
            status="success",
            metrics={
                "mode": args.mode,
                "notes_retrieved": len(paths),
            },
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="rag_query.py",
                operation_type="rag_query",
                status="failed",
                metrics={"error": str(e)},
            )
        import traceback

        traceback.print_exc()
        sys.exit(1)
