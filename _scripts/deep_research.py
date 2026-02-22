"""Deep Research - Multi-step research orchestration (8-step methodology).

Orchestrates: vault RAG → external sources → steelman → comprehensive synthesis report.
Supports full 8-step methodology (wshuyi/deep-research) with intermediate artifacts.
Inspired by: wshuyi/deep-research, OpenAI Deep Research, AI-Researcher, Auto-Deep-Research.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH, TRACKER

# Import RAG components
from rag_query import (
    find_markdown_files,
    search_vault_keyword,
    read_note,
    expand_via_graph,
    build_context,
    build_user_message,
    RAG_SYSTEM_PROMPT,
)

# Import source finder
try:
    from source_finder import find_sources
    HAS_SOURCE_FINDER = True
except ImportError:
    HAS_SOURCE_FINDER = False

DEEP_RESEARCH_SYSTEM = """You are a deep research assistant producing comprehensive, multi-perspective reports. Your output should mirror the rigor of academic literature reviews and OpenAI Deep Research reports.

**Report structure (use these exact ## headings):**
1. **Executive Summary** — 2-3 paragraphs: core question, main findings, key takeaway.
2. **Key Findings** — Bullet points or short sections with the most important discoveries.
3. **Evidence from Vault** — What the user's own notes reveal. Use [[wikilinks]] to cite.
4. **External Perspectives** — (if provided) Notable sources, contrasting views, gaps in vault.
5. **Opposing Views** — (if provided) Steelmanned counterarguments the user should consider.
6. **Open Questions** — 3-5 questions worth exploring further.
7. **References** — List of cited notes and sources.

**Style:**
- Thorough but readable. Aim for 1000-2000 words.
- Cite sources explicitly. Use [[note title]] for vault notes.
- Acknowledge uncertainty and conflicting evidence.
- Cross-domain synthesis: note connections to other domains when relevant.
- No YAML frontmatter. Start with # Research Report: [topic]."""

# --- 8-step methodology prompts (wshuyi/deep-research) ---
STEP_0_1_PROMPT = """You are applying the Deep Research 8-step methodology. Perform Step 0 and Step 1.

**Step 0: Problem type identification**
Classify the research topic into one of: Concept Comparison | Decision Support | Trend Analysis | Problem Diagnosis | Knowledge Organization.

**Step 0.5: Time-sensitivity assessment**
Assess: 🔴 Extreme (AI/crypto, 3-6mo) | 🟠 High (cloud/APIs, 6-12mo) | 🟡 Medium (1-2y) | 🟢 Low (no limit).

**Step 1: Problem decomposition**
Break the topic into 2-4 researchable sub-questions. Define boundaries (audience, scope, time).

Output in this exact structure (no YAML frontmatter):
## Problem Type
[Type] — [Brief rationale]

## Time-Sensitivity
[Level] — [Rationale]. Time window: [X months/years].

## Sub-Questions
1. [Sub-question A]
2. [Sub-question B]
3. [Sub-question C]
4. [Sub-question D] (optional)

## Boundaries
- Audience/scope: [who/what]
- Time: [period if relevant]"""

STEP_2_3_PROMPT = """You are applying the Deep Research methodology. Perform Step 2 (source tiering) and Step 3 (fact extraction).

**Source tiering (L1-L4):**
- L1: Official docs, papers, RFCs
- L2: Official blogs, talks, whitepapers
- L3: Media, expert tutorials
- L4: Community, forums, GitHub Issues

**Fact cards:** Each fact must have: Statement, Source (link or note), Confidence (High/Medium/Low).

From the provided content, produce:

## Sources (Step 2)
For each distinct source in the content:
- **Title/Link**: [or "Vault note: [[title]]"]
- **Tier**: L1/L2/L3/L4
- **Summary**: 1-2 sentences

## Fact Cards (Step 3)
For each verifiable fact:
- **Statement**: [Specific fact]
- **Source**: [Which source]
- **Confidence**: High/Medium/Low
- **Applicability**: [Scope if relevant]

Extract 5-15 fact cards. Be precise. No speculation."""

STEP_4_6_PROMPT = """You are applying the Deep Research methodology. Perform Step 4 (comparison framework), Step 5 (reference alignment), and Step 6 (derivation chain).

**Step 4: Comparison framework**
Choose 4-8 dimensions (e.g., mechanism, input/output, pros/cons, use cases, cost/risk). Fill a comparison table using the fact cards.

**Step 5: Reference alignment**
Ensure compared items have clear, consistent definitions.

**Step 6: Derivation chain**
For each dimension, write: Fact → Comparison → Conclusion. Conclusions must trace to facts.

Output structure:
## Comparison Framework
| Dimension | [A] | [B] | Fact basis |
|-----------|-----|-----|------------|
...

## Derivation Process
### Dimension 1: [name]
- **Fact**: [from fact cards]
- **Comparison**: [how A vs B differ]
- **Conclusion**: [evidence-based conclusion]

Repeat for each dimension."""

STEP_7_8_PROMPT = """You are applying the Deep Research methodology. Perform Step 7 (validation) and Step 8 (deliverable).

**Step 7: Use-case validation**
Pick one typical scenario. Apply the conclusions. Does it hold? Any counterexamples?

**Step 8: Deliverable report**
Produce the final report with:
1. One-line summary (meeting-ready)
2. Structured sections: Concept alignment → Mechanism → Similarities → Differences → Use-case → Conclusion
3. Traceable evidence (cite fact cards/sources)

Output structure:
## Validation
- **Scenario**: [description]
- **Expected**: [what conclusions predict]
- **Result**: [holds / counterexample]
- **Checklist**: [facts consistent? no overreach?]

## Final Report
# [Topic] Research Report

## Summary
[One-line core conclusion]

## 1. Concept Alignment
## 2. Mechanism
## 3. Similarities
## 4. Differences
## 5. Use-Case Validation
## 6. Conclusion & Recommendations
## References
[All cited sources]"""


def run_vault_rag(query: str, top_k: int = 15, depth: int = 2) -> str:
    """Retrieve and synthesize vault content via RAG."""
    all_files = find_markdown_files()
    seed_paths = search_vault_keyword(query, limit=top_k)

    if not seed_paths:
        query_lower = query.lower()
        for f in all_files:
            if len(seed_paths) >= top_k:
                break
            try:
                if query_lower in f.read_text(encoding="utf-8").lower():
                    seed_paths.append(f)
            except Exception:
                pass

    if not seed_paths:
        return "(No matching notes found in vault.)"

    seed_paths = [p if isinstance(p, Path) else Path(p) for p in seed_paths]
    expanded = expand_via_graph(
        seed_paths,
        all_files,
        depth=depth,
        max_extra=max(8, top_k // 2),
    )
    paths = list(expanded)[: top_k * 2]
    context = build_context(paths, "hybrid", query)
    user_msg = build_user_message(query, "hybrid", context or "(No context)")
    return summarize(user_msg, RAG_SYSTEM_PROMPT)


def run_source_finder(topic: str) -> str:
    """Find external sources on the topic."""
    if not HAS_SOURCE_FINDER:
        return "(Source finder not available.)"
    return find_sources(topic)


def run_steelman(topic: str) -> str:
    """Generate steelmanned opposing views."""
    STEELMAN_PROMPT = """You are an expert at steelmanning — presenting the strongest possible version of opposing arguments. Given the research topic, identify 2-4 substantive opposing views and present each in 2-3 paragraphs. Be charitable and substantive. No YAML frontmatter."""
    return summarize(topic, STEELMAN_PROMPT)


def build_synthesis_prompt(
    query: str,
    vault_section: str,
    sources_section: Optional[str] = None,
    steelman_section: Optional[str] = None,
) -> str:
    """Build the final synthesis prompt."""
    parts = [
        f"**Research question:** {query}",
        "",
        "**Vault synthesis (from user's Obsidian notes):**",
        vault_section,
    ]
    if sources_section:
        parts.extend(["", "**External sources and perspectives:**", sources_section])
    if steelman_section:
        parts.extend(["", "**Opposing views (steelmanned):**", steelman_section])
    parts.extend([
        "",
        "---",
        "Produce a comprehensive Deep Research report using the structure specified in your system prompt. Synthesize all sections above. Use [[wikilinks]] for vault references.",
    ])
    return "\n".join(parts)


def _safe_topic(topic: str) -> str:
    """Create filesystem-safe topic name."""
    return re.sub(r"[^\w\s-]", "", topic)[:50].strip().replace(" ", "-") or "research"


def run_methodology(
    query: str,
    top_k: int,
    depth: int,
    include_sources: bool,
    include_debate: bool,
    save_final: bool,
) -> str:
    """Run full 8-step methodology with intermediate artifacts."""
    safe = _safe_topic(query)
    base = VAULT_PATH / "Sources" / "Deep Research" / safe
    base.mkdir(parents=True, exist_ok=True)

    def _save(name: str, content: str) -> None:
        path = base / name
        path.write_text(content, encoding="utf-8")
        print(f"   Saved: {path.relative_to(VAULT_PATH)}")

    # Phase 1: Vault RAG
    print("\n📚 Step 0-1: Problem type, time-sensitivity, decomposition...")
    step01 = summarize(
        f"Research topic: {query}\n\nAnalyze and output the structured response.",
        STEP_0_1_PROMPT,
    )
    _save("00_problem_decomposition.md", f"# Problem Decomposition\n\n**Topic:** {query}\n\n---\n\n{step01}")

    # Phase 2: Retrieve content
    print("\n📚 Retrieving from vault...")
    vault_section = run_vault_rag(query, top_k=top_k, depth=depth)
    sources_section = None
    if include_sources and HAS_SOURCE_FINDER:
        print("   Finding external sources...")
        sources_section = run_source_finder(query)
    steelman_section = None
    if include_debate:
        print("   Steelmanning opposing views...")
        steelman_section = run_steelman(query)

    combined = vault_section
    if sources_section:
        combined += "\n\n---\n\n**External sources:**\n" + sources_section
    if steelman_section:
        combined += "\n\n---\n\n**Opposing views:**\n" + steelman_section

    # Step 2-3: Source tiering + fact extraction
    print("\n📋 Step 2-3: Source tiering & fact cards...")
    step23 = summarize(
        f"Research topic: {query}\n\nContent to analyze:\n\n{combined[:12000]}",
        STEP_2_3_PROMPT,
    )
    _save("01_sources.md", step23.split("## Fact Cards")[0].strip() or step23)
    fact_section = "## Fact Cards" in step23 and step23.split("## Fact Cards", 1)[1] or ""
    _save("02_fact_cards.md", fact_section or step23)

    # Step 4-6: Comparison framework + derivation
    print("\n📊 Step 4-6: Comparison framework & derivation...")
    step46 = summarize(
        f"Research topic: {query}\n\nFact cards and sources:\n\n{step23[:8000]}",
        STEP_4_6_PROMPT,
    )
    _save("03_comparison_framework.md", step46)
    _save("04_derivation.md", step46)

    # Step 7-8: Validation + final report
    print("\n✅ Step 7-8: Validation & deliverable...")
    step78 = summarize(
        f"Research topic: {query}\n\nDerivation and framework:\n\n{step46[:8000]}",
        STEP_7_8_PROMPT,
    )
    val_part = step78
    if "## Validation" in step78 and "## Final Report" in step78:
        val_part = step78.split("## Validation", 1)[1].split("## Final Report", 1)[0].strip()
    _save("05_validation.md", f"# Validation\n\n{val_part}")
    final_part = step78
    if "## Final Report" in step78:
        final_part = step78.split("## Final Report", 1)[1].strip()
    _save("FINAL_report.md", f"# {query}\n\n**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n---\n\n{final_part}")

    report = final_part
    if save_final:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_note(f"Sources/Deep Research - {safe} - {date_str}.md", f"# Deep Research: {query}\n\n**Date:** {date_str}\n\n---\n\n{report}")
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Deep Research - Multi-step research orchestration (OpenAI Deep Research / HKUDS inspired)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/deep_research.py "What are the tradeoffs of AI agents vs traditional automation?"
  python3 _scripts/deep_research.py "REST API vs GraphQL" --methodology --sources --debate
  python3 _scripts/deep_research.py "Personal knowledge management" --save
""",
    )
    parser.add_argument(
        "query",
        type=str,
        help="Research question or topic to investigate",
    )
    parser.add_argument(
        "--sources",
        action="store_true",
        help="Include external source recommendations (Substack, podcasts, etc.)",
    )
    parser.add_argument(
        "--debate",
        action="store_true",
        help="Include steelmanned opposing views",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=15,
        help="Max notes to retrieve from vault (default: 15)",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Graph expansion depth for RAG (default: 2)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to Sources/Deep Research - YYYY-MM-DD.md",
    )
    parser.add_argument(
        "--methodology",
        action="store_true",
        help="Use full 8-step methodology with intermediate artifacts (wshuyi/deep-research)",
    )
    args = parser.parse_args()

    if TRACKER:
        TRACKER.record_operation(
            script_name="deep_research.py",
            operation_type="deep_research",
            status="in_progress",
            metrics={"query": args.query[:50]},
        )

    print("🔬 Deep Research (8-step methodology)")
    print(f"   Query: {args.query}")
    if args.methodology:
        print("   Mode: Full 8-step with intermediate artifacts")
        report = run_methodology(
            args.query,
            top_k=args.top_k,
            depth=args.depth,
            include_sources=args.sources,
            include_debate=args.debate,
            save_final=args.save,
        )
        print("\n" + "=" * 60)
        print(report)
        print("=" * 60)
        if TRACKER:
            TRACKER.record_operation(
                script_name="deep_research.py",
                operation_type="deep_research",
                status="success",
                metrics={"query": args.query[:50], "methodology": True, "saved": args.save},
            )
        return

    print("   Phases: vault RAG", end="")
    if args.sources:
        print(" + sources", end="")
    if args.debate:
        print(" + steelman", end="")
    print(" → synthesis")

    # Phase 1: Vault RAG
    print("\n📚 Phase 1: Retrieving from vault...")
    vault_section = run_vault_rag(args.query, top_k=args.top_k, depth=args.depth)
    print("   Done.")

    # Phase 2: External sources (optional)
    sources_section = None
    if args.sources:
        print("\n🌐 Phase 2: Finding external sources...")
        sources_section = run_source_finder(args.query)
        print("   Done.")

    # Phase 3: Steelman (optional)
    steelman_section = None
    if args.debate:
        print("\n⚖️ Phase 3: Steelmanning opposing views...")
        steelman_section = run_steelman(args.query)
        print("   Done.")

    # Phase 4: Synthesis
    print("\n📝 Phase 4: Synthesizing report...")
    user_prompt = build_synthesis_prompt(
        args.query,
        vault_section,
        sources_section,
        steelman_section,
    )
    report = summarize(user_prompt, DEEP_RESEARCH_SYSTEM)

    # Output
    date_str = datetime.now().strftime("%Y-%m-%d")
    title = f"# Deep Research: {args.query}\n\n**Date:** {date_str}\n\n---\n\n{report}"

    if args.save:
        safe_name = re.sub(r'[^\w\s-]', '', args.query)[:40].strip().replace(" ", "-") or "research"
        save_path = f"Sources/Deep Research - {safe_name} - {date_str}.md"
        save_note(save_path, title)
        print(f"\n💾 Saved to: {save_path}")

    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)

    if TRACKER:
        TRACKER.record_operation(
            script_name="deep_research.py",
            operation_type="deep_research",
            status="success",
            metrics={"query": args.query[:50], "saved": args.save},
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="deep_research.py",
                operation_type="deep_research",
                status="failed",
                metrics={"error": str(e)},
            )
        import traceback
        traceback.print_exc()
        sys.exit(1)
