"""Filter - Precision RAG search over your Obsidian vault.

Searches for relevant information on a topic with exact, precise retrieval using:
- Multi-strategy keyword retrieval (phrase + term expansion)
- Passage-level chunking (not full notes)
- AI reranking for relevance (over-retrieve → filter)
- Precision-first output (only highly relevant passages)

Different from /rag: Filter returns only exact matches; RAG synthesizes broadly.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH, TRACKER

# Reuse RAG infrastructure
from rag_query import (
    find_markdown_files,
    read_note,
    expand_via_graph,
)

# Search config
MAX_PASSAGES_RERANK = 40
MAX_CHARS_PER_PASSAGE = 800
MIN_RELEVANCE_SCORE = 7
MAX_OUTPUT_PASSAGES = 15


def search_vault_multi(
    query: str,
    limit: int = 30,
    use_terms: bool = True,
) -> List[Path]:
    """Multi-strategy search: phrase match + term expansion for recall."""
    seen: set = set()
    results: List[Path] = []

    # 1. Phrase search (exact query)
    try:
        proc = subprocess.run(
            ["rg", "-l", "-i", "-F", "--max-count", "1", query, str(VAULT_PATH)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode == 0 and proc.stdout:
            for line in proc.stdout.strip().split("\n"):
                if line.strip():
                    p = Path(line.strip())
                    if p.suffix == ".md":
                        try:
                            full = (VAULT_PATH / p).resolve() if not p.is_absolute() else p.resolve()
                            if full.exists() and str(VAULT_PATH) in str(full) and full not in seen:
                                seen.add(full)
                                results.append(full)
                        except (OSError, RuntimeError):
                            pass
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    if len(results) >= limit:
        return results[:limit]

    # 2. Term search (split query into words, any match)
    if use_terms and len(results) < limit:
        terms = [t.strip() for t in re.split(r"[\s,;]+", query) if len(t.strip()) >= 2]
        for term in terms[:5]:
            if len(results) >= limit:
                break
            try:
                proc = subprocess.run(
                    ["rg", "-l", "-i", "-F", "--max-count", "1", term, str(VAULT_PATH)],
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                if proc.returncode == 0 and proc.stdout:
                    for line in proc.stdout.strip().split("\n"):
                        if line.strip():
                            p = Path(line.strip())
                            if p.suffix == ".md":
                                try:
                                    full = (VAULT_PATH / p).resolve() if not p.is_absolute() else p.resolve()
                                    if full.exists() and str(VAULT_PATH) in str(full) and full not in seen:
                                        seen.add(full)
                                        results.append(full)
                                except (OSError, RuntimeError):
                                    pass
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

    return results[:limit]


def extract_passages(note: Dict, query: str, max_chars: int = MAX_CHARS_PER_PASSAGE) -> List[Tuple[str, str]]:
    """Split note content into passages (paragraphs/sections) for granular retrieval."""
    content = note.get("content", "")
    title = note.get("title", "")
    rel_path = note.get("relative_path", "")

    if not content or len(content.strip()) < 30:
        return []

    # Split by double newline (paragraphs) or ## headers
    blocks = re.split(r"\n\n+|\n(?=## )", content)
    passages: List[Tuple[str, str]] = []
    header = ""

    for block in blocks:
        block = block.strip()
        if not block or len(block) < 20:
            continue
        if block.startswith("## "):
            header = block.split("\n")[0]
            block = "\n".join(block.split("\n")[1:]).strip()
        if not block:
            continue
        excerpt = block[:max_chars]
        if len(block) > max_chars:
            excerpt += "\n[...]"
        meta = f"[[{title}]] ({rel_path})"
        if header:
            meta += f" - {header}"
        passages.append((meta, excerpt))

    return passages


def rerank_passages(
    query: str,
    passages: List[Tuple[str, str]],
    top_k: int = MAX_OUTPUT_PASSAGES,
    min_score: float = MIN_RELEVANCE_SCORE,
) -> List[Tuple[str, str, float]]:
    """Use AI to score each passage for relevance; return only high-scoring ones."""
    if not passages:
        return []

    # Batch for efficiency (avoid huge context)
    batch_size = 12
    scored: List[Tuple[str, str, float]] = []

    for i in range(0, len(passages), batch_size):
        batch = passages[i : i + batch_size]
        items = "\n\n".join(
            f"[{j+1}] {meta}\n{text}"
            for j, (meta, text) in enumerate(batch)
        )

        prompt = f"""You are a precision retrieval filter. Score each passage below for relevance to the user's query.

**Query:** {query}

**Passages:**
{items}

For each passage [1] through [{len(batch)}], output a single line with format: N:SCORE
- Score 0-10: 10 = directly answers the query, 0 = completely irrelevant.
- Be strict: only 7+ are "relevant". Score 5-6 for tangentially related.
- Output only the numbered lines, one per passage."""

        try:
            resp = summarize(prompt, "You are a precision relevance scorer. Output only lines in format N:SCORE.")
            for line in resp.strip().split("\n"):
                m = re.match(r"(\d+)\s*[:]\s*([\d.]+)", line.strip())
                if m:
                    idx = int(m.group(1)) - 1
                    score = float(m.group(2))
                    if 0 <= idx < len(batch) and score >= min_score:
                        meta, text = batch[idx]
                        scored.append((meta, text, score))
        except Exception:
            continue

    # Sort by score descending, dedupe by content
    scored.sort(key=lambda x: -x[2])
    seen_texts: set = set()
    deduped: List[Tuple[str, str, float]] = []
    for meta, text, score in scored:
        key = text[:100]
        if key not in seen_texts:
            seen_texts.add(key)
            deduped.append((meta, text, score))
        if len(deduped) >= top_k:
            break

    return deduped


FILTER_SYSTEM_PROMPT = """You are a precision retrieval assistant. The user wants ONLY the most relevant information on a topic—nothing tangential.

Extract and present only passages that directly address the query. If multiple passages are relevant, list them with citations. Do not synthesize or add commentary beyond what is in the passages. Use [[wikilinks]] for note references. Be exact and precise."""


def main():
    """Main filter entry point."""
    parser = argparse.ArgumentParser(
        description="Filter - Precision RAG search over your Obsidian vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/filter_query.py "Alpha Vantage API"
  python3 _scripts/filter_query.py "habit tracking" --no-rerank
  python3 _scripts/filter_query.py "RAG retrieval" --save
  python3 _scripts/filter_query.py "stock market" --threshold 7
""",
    )
    parser.add_argument("query", type=str, help="Topic or thing to search for (exact, precise)")
    parser.add_argument(
        "--no-rerank",
        action="store_true",
        help="Skip AI reranking (faster, less precise)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=MIN_RELEVANCE_SCORE,
        help=f"Min relevance score 0-10 for reranking (default: {MIN_RELEVANCE_SCORE})",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=MAX_OUTPUT_PASSAGES,
        help=f"Max passages to return (default: {MAX_OUTPUT_PASSAGES})",
    )
    parser.add_argument(
        "--expand",
        action="store_true",
        help="Expand via wikilink graph (like RAG hybrid)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save response to Sources/Filter - YYYY-MM-DD.md",
    )
    args = parser.parse_args()

    if TRACKER:
        TRACKER.record_operation(
            script_name="filter_query.py",
            operation_type="filter_query",
            status="in_progress",
            metrics={"query": args.query[:50]},
        )

    print("🔍 Filter (precision RAG)")
    print(f"   Query: {args.query}")
    print(f"   Rerank: {'on' if not args.no_rerank else 'off'}")

    all_files = find_markdown_files()
    seed_paths = search_vault_multi(args.query, limit=25, use_terms=True)

    if not seed_paths:
        # Fallback: scan all files
        q_lower = args.query.lower()
        for f in all_files:
            if len(seed_paths) >= 25:
                break
            try:
                if q_lower in f.read_text(encoding="utf-8").lower():
                    seed_paths.append(f)
            except Exception:
                pass

    if not seed_paths:
        print("❌ No matching notes found.")
        if TRACKER:
            TRACKER.record_operation(
                script_name="filter_query.py",
                operation_type="filter_query",
                status="failed",
                metrics={"error": "No matches"},
            )
        return

    seed_paths = [p if isinstance(p, Path) else Path(p) for p in seed_paths]

    if args.expand:
        expanded = expand_via_graph(
            seed_paths,
            all_files,
            depth=1,
            max_extra=10,
        )
        paths = list(expanded)[:35]
    else:
        paths = seed_paths[:25]

    # Extract passages from all notes
    all_passages: List[Tuple[str, str]] = []
    for p in paths:
        note = read_note(p)
        if note:
            all_passages.extend(extract_passages(note, args.query))

    if not all_passages:
        print("❌ No passages extracted.")
        if TRACKER:
            TRACKER.record_operation(
                script_name="filter_query.py",
                operation_type="filter_query",
                status="failed",
                metrics={"error": "No passages"},
            )
        return

    print(f"   Retrieved {len(paths)} notes, {len(all_passages)} passages")

    if args.no_rerank:
        # No reranking: return first N passages (keyword order)
        passages_to_show = all_passages[: args.top_k]
        scored = [(m, t, 0.0) for m, t in passages_to_show]
    else:
        scored = rerank_passages(
            args.query,
            all_passages[:MAX_PASSAGES_RERANK],
            top_k=args.top_k,
            min_score=args.threshold,
        )

    if not scored:
        print("❌ No passages passed the relevance threshold.")
        if TRACKER:
            TRACKER.record_operation(
                script_name="filter_query.py",
                operation_type="filter_query",
                status="failed",
                metrics={"error": "No relevant passages"},
            )
        return

    # Build output
    output_parts = [f"# Filter: {args.query}\n"]
    output_parts.append(f"**Precision RAG** | {len(scored)} relevant passages\n")

    for meta, text, score in scored:
        block = f"---\n**{meta}**"
        if score > 0:
            block += f" (relevance: {score:.1f})"
        block += f"\n\n{text}\n"
        output_parts.append(block)

    output = "\n".join(output_parts)

    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_path = f"Sources/Filter - {date_str}.md"
        save_note(save_path, output)
        print(f"\n💾 Saved to: {save_path}")

    print("\n" + "=" * 60)
    print(output)
    print("=" * 60)

    if TRACKER:
        TRACKER.record_operation(
            script_name="filter_query.py",
            operation_type="filter_query",
            status="success",
            metrics={
                "notes_retrieved": len(paths),
                "passages_returned": len(scored),
            },
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="filter_query.py",
                operation_type="filter_query",
                status="failed",
                metrics={"error": str(e)},
            )
        import traceback

        traceback.print_exc()
        sys.exit(1)
