---
name: deep-research
description: |
  Deep Research (8-step methodology) — Transform vague topics into high-quality, deliverable research reports.
  Systematic fact extraction, source tiering (L1>L2>L3>L4), time-sensitivity assessment, and verifiable "Fact→Conclusion" chains.
  Use when: deep research, comprehensive report, thorough investigation, concept comparison, decision support, trend analysis.
  Inspired by wshuyi/deep-research + OpenAI Deep Research + HKUDS.
---

# Deep Research (/deep-research)

8-step methodology that transforms vague topics into high-quality, deliverable research reports. Combines **wshuyi/deep-research** systematic rigor with PAI vault-native retrieval.

## Core Principles

- **Conclusions from mechanism comparison** — Not "I feel like X"; only evidence-based reasoning
- **Fact-first, then derivation** — Nail down facts before drawing conclusions
- **Source tiering** — L1 (official) > L2 (blogs) > L3 (media) > L4 (community)
- **Intermediate artifacts** — Save each step for traceability and recovery

## Quick Start

```bash
# Basic (vault RAG → synthesis)
python3 _scripts/deep_research.py "What are the tradeoffs of AI agents vs traditional automation?"

# Full 8-step methodology with intermediate artifacts
python3 _scripts/deep_research.py "REST API vs GraphQL" --methodology --sources --debate

# Save to vault
python3 _scripts/deep_research.py "Personal knowledge management" --save
```

## Workflow (8 Steps)

| Step | Name | Output |
|------|------|--------|
| **0** | Problem type identification | `00_problem_decomposition.md` |
| **0.5** | Time-sensitivity assessment | (appended to 00) |
| **1** | Problem decomposition & boundary | `00_problem_decomposition.md` |
| **2** | Source tiering & authority locking | `01_sources.md` |
| **3** | Fact extraction & evidence cards | `02_fact_cards.md` |
| **4** | Build comparison framework | `03_comparison_framework.md` |
| **5** | Reference alignment | (in 03) |
| **6** | Fact → Conclusion derivation chain | `04_derivation.md` |
| **7** | Use case validation (sanity check) | `05_validation.md` |
| **8** | Deliverable formatting | `FINAL_report.md` |

## Output Structure

When `--methodology` is used, artifacts are saved to:

```
Sources/Deep Research/<topic>/
├── 00_problem_decomposition.md   # Problem type, sub-questions, time-sensitivity
├── 01_sources.md                 # Source links, tier (L1-L4), summary
├── 02_fact_cards.md              # Facts with citation, confidence
├── 03_comparison_framework.md    # Dimensions, comparison table
├── 04_derivation.md              # Fact → Comparison → Conclusion chains
├── 05_validation.md             # Use-case sanity check
└── FINAL_report.md              # Deliverable report
```

## Problem Types

| Type | Focus |
|------|-------|
| **Concept comparison** | Mechanism differences,适用边界 |
| **Decision support** | Cost, risk, benefit tradeoffs |
| **Trend analysis** | History, drivers, predictions |
| **Problem diagnosis** | Root cause, evidence chain |
| **Knowledge organization** | Definition, classification, relations |

## Time-Sensitivity (Step 0.5 — BLOCKING for AI/tech)

| Level | Domains | Time window |
|------|---------|-------------|
| 🔴 **Extreme** | AI/LLM, crypto, blockchain | 3–6 months |
| 🟠 **High** | Cloud, frontend, APIs | 6–12 months |
| 🟡 **Medium** | Languages, DBs, OS | 1–2 years |
| 🟢 **Low** | Algorithms, theory | No limit |

For 🔴/🟠: enforce time windows, require version numbers, prioritize official docs.

## Source Tiering (L1–L4)

| Tier | Type | Use |
|------|------|-----|
| **L1** | Official docs, papers, RFCs | Definitions, verifiable facts |
| **L2** | Official blogs, talks, whitepapers | Design intent, architecture |
| **L3** | Media, expert tutorials | Intuition, examples |
| **L4** | Community, forums, GitHub Issues | Blind spots, real user concerns |

**Rule:** Conclusions must trace to L1/L2. L3/L4 are auxiliary.

## Fact Cards Template

```markdown
## Fact #[n]
- **Statement**: [Specific fact]
- **Source**: [Link / doc section]
- **Confidence**: High / Medium / Low
- **Applicability**: [Target audience/scope]
```

## Report Structure (Step 8)

1. **One-line summary** — Reproducible in a meeting
2. **Structured sections** — Clear headings for the derivation chain
3. **Traceable evidence** — Key facts with source links

```markdown
# [Topic] Research Report

## Summary
[One-line core conclusion]

## 1. Concept alignment
## 2. Mechanism
## 3. Similarities
## 4. Differences
## 5. Use-case validation
## 6. Conclusion & recommendations
## References
```

## Options

- `query` — Research question or topic (required)
- `--methodology` — Use full 8-step flow with intermediate artifacts
- `--sources` — Include external source recommendations
- `--debate` — Include steelmanned opposing views
- `--top-k N` — Max notes to retrieve (default: 15)
- `--depth N` — Graph expansion depth (default: 2)
- `--save` — Save final report to `Sources/Deep Research - YYYY-MM-DD.md`

## Examples

```bash
# Quick vault-only research
python3 _scripts/deep_research.py "How does my thinking about habits connect to goals?"

# Full 8-step with external + debate
python3 _scripts/deep_research.py "LLM agents for scientific discovery" --methodology --sources --debate --save

# Concept comparison (methodology mode)
python3 _scripts/deep_research.py "REST API vs GraphQL" --methodology --sources
```

## Quality Checklist

- [ ] Core conclusions backed by L1/L2 facts
- [ ] No vague "maybe" without uncertainty note
- [ ] Comparison dimensions complete
- [ ] At least one use-case validation
- [ ] References complete, links accessible
- [ ] One-line summary clear and reproducible

## Related Skills

- `/rag` — Single-query vault search
- `/essay` — Long-form synthesis from notes
- `/debate` — Steelman only
- `/source` — External sources only
- `/filter` — Precision RAG extraction

## Reference

- [wshuyi/deep-research](https://github.com/wshuyi/deep-research) — 8-step methodology source
- OpenAI Deep Research, HKUDS AI-Researcher — Multi-step orchestration inspiration
