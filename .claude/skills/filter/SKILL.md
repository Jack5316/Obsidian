---
name: filter
description: Precision RAG search over your Obsidian vault. Find exactly and precisely the relevant information on a topic using multi-strategy retrieval, passage-level chunking, and AI reranking. Use when you need exact matches, precise extraction, or to filter vault content to only what's relevant.
---

# Filter Skill (/filter)

Precision RAG search over your Obsidian vault. Returns **only** the most relevant passages on a topic—exact, precise retrieval using the latest RAG techniques: multi-strategy keyword search, passage-level chunking, and AI reranking.

**Filter vs RAG:**
- **Filter** — Precise extraction: "find exactly where X is discussed" → only relevant passages
- **RAG** — Broad synthesis: "what do I know about X?" → full answer with citations

## Quick Start

```bash
# Precision search on a topic
python3 _scripts/filter_query.py "Alpha Vantage API"

# With graph expansion (like RAG hybrid)
python3 _scripts/filter_query.py "habit tracking" --expand

# Save to vault
python3 _scripts/filter_query.py "RAG retrieval" --save
```

## Retrieval Pipeline (Latest RAG Tech)

1. **Multi-strategy retrieval** — Phrase match + term expansion for high recall
2. **Passage chunking** — Split notes by paragraph/section (not full notes)
3. **AI reranking** — Score each passage 0–10 for relevance (over-retrieve → filter)
4. **Precision output** — Return only passages above relevance threshold (default 7+)

## Features

- **Exact & precise** — Only highly relevant passages, no tangential content
- **Passage-level** — Granular retrieval (paragraphs/sections), not whole notes
- **AI reranking** — State-of-the-art relevance filtering (2024–2025 RAG best practice)
- **Configurable threshold** — Adjust strictness (0–10) for precision vs recall
- **Optional graph expansion** — Include wikilink neighbors for broader context

## Options

- `query` — Topic or thing to search for (required)
- `--no-rerank` — Skip AI reranking (faster, less precise)
- `--threshold N` — Min relevance score 0–10 (default: 7)
- `--top-k N` — Max passages to return (default: 15)
- `--expand` — Expand via wikilink graph (hybrid mode)
- `--save` — Save to `Sources/Filter - YYYY-MM-DD.md`

## Examples

```bash
# Basic precision search
python3 _scripts/filter_query.py "stock market analysis"

# Stricter relevance (only 8+)
python3 _scripts/filter_query.py "meditation benefits" --threshold 8

# Faster search without reranking
python3 _scripts/filter_query.py "project tracking" --no-rerank

# Include linked notes
python3 _scripts/filter_query.py "personal AI" --expand --save
```

## Output

- **Terminal**: Markdown list of relevant passages with `[[note]]` citations and relevance scores
- **Saved note** (with `--save`): `Sources/Filter - YYYY-MM-DD.md`

## Related

- `/rag` — Broad synthesis over vault (complementary)
- `/connect` — Find relationships between notes
- `/deep-research` — Multi-step research with external sources
