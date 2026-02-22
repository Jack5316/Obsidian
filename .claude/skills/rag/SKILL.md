---
name: rag
description: Retrieval-Augmented Generation over your Obsidian vault. Query your knowledge base with hybrid retrieval (keyword + graph expansion via wikilinks). Inspired by LightRAG. Use when you want to ask questions about your notes, search your vault with AI synthesis, or /rag.
---

# RAG Skill (/rag)

Retrieval-Augmented Generation over your Obsidian vault. Inspired by [LightRAG](https://github.com/HKUDS/LightRAG) — a simple, fast RAG system that combines keyword search with knowledge graph expansion. Uses **Python for retrieval** (deterministic, low cost) and **AI only for synthesis** (judgment, summarization).

## Quick Start

```bash
# Query your vault
python3 _scripts/rag_query.py "What do I know about AI agents?"

# Hybrid mode (keyword + graph expansion)
python3 _scripts/rag_query.py "Summarize my notes on habits" --mode hybrid

# Save response to vault
python3 _scripts/rag_query.py "Key insights on productivity" --save
```

## Retrieval Modes (LightRAG-inspired)

| Mode | Description |
|------|-------------|
| **naive** | Direct keyword matches only (ripgrep search) |
| **local** | Keyword + graph expansion via `[[wikilinks]]` (local context) |
| **hybrid** | Local + broader vault coverage (default) |

## Features

1. **Keyword search** — Uses ripgrep for fast, deterministic retrieval
2. **Graph expansion** — Follows wikilinks to related notes (LightRAG-style local context)
3. **AI synthesis** — Only the final answer uses LLM; retrieval is script-based
4. **Obsidian-native** — Output uses `[[wikilinks]]` for direct navigation

## Options

- `query` — Question to answer from vault content (required)
- `--mode {naive,local,hybrid}` — Retrieval mode (default: hybrid)
- `--top-k N` — Max notes to retrieve (default: 12)
- `--depth N` — Graph expansion depth for local/hybrid (default: 1)
- `--save` — Save response to `Sources/RAG Query - YYYY-MM-DD.md`

## Examples

```bash
# Basic query
python3 _scripts/rag_query.py "What are my main projects?"

# Focused search with more notes
python3 _scripts/rag_query.py "Connections between meditation and productivity" --top-k 15

# Naive mode (keyword only, no graph expansion)
python3 _scripts/rag_query.py "Alpha Vantage" --mode naive

# Deeper graph expansion
python3 _scripts/rag_query.py "How does my thinking about X connect to Y?" --depth 2 --save
```

## Output

- **Terminal**: Markdown response with cited `[[note]]` references
- **Saved note** (with `--save`): `Sources/RAG Query - YYYY-MM-DD.md`

## Design Principles (from LightRAG)

- **Scripts before prompts** — Retrieval is Python (ripgrep + graph traversal); AI only for answer synthesis
- **Knowledge graph** — Wikilinks form a lightweight graph; expansion captures "local" context
- **Hybrid retrieval** — Combines direct matches with graph-neighbor context for richer answers

## Related

- [LightRAG](https://github.com/HKUDS/LightRAG) — Full RAG with entity extraction, vector DB, Neo4j
- `/connect` — Find relationships between notes (manual exploration)
- `/random-walk` — Serendipitous discovery through linked notes
