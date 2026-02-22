# Nanobot Skills Integration Test Plan

**Goal:** Verify nanobot can discover, invoke, and use PAI vault skills via exec tool. Test via both CLI (`nanobot agent`) and Telegram.

**Prerequisites:**
- nanobot configured with workspace = vault path
- `NANOBOT_SKILLS.md` in vault root
- `~/.nanobot/workspace/AGENTS.md` updated with PAI skill instructions

---

## Phase 1: Discovery & Intent Matching

| # | Test | User Input | Expected Behavior | Pass/Fail |
|---|------|------------|-------------------|-----------|
| 1.1 | List skills | "List all available skills" | Nanobot reads NANOBOT_SKILLS.md or org-list, returns skill categories | |
| 1.2 | What can you do | "What skills can you run?" | Summarizes PAI skills (arxiv, hn, rag, etc.) | |
| 1.3 | Ambiguous skill | "Get me some news" | Clarifies: HN, Reddit, Chinese news, or AI brief? | |
| 1.4 | Natural language | "I want my morning AI digest" | Maps to ai-brief, runs `python3 _scripts/ai_brief.py` | |

---

## Phase 2: Zero-Arg Skills (No User Input Required)

| # | Skill | User Input | Command | Expected Output | Pass/Fail |
|---|-------|------------|---------|-----------------|-----------|
| 2.1 | org-list | "List automation scripts" | `org_skill.py --list` | List of scripts | |
| 2.2 | org-status | "Check script status" | `org_skill.py --status` | Recent run status | |
| 2.3 | arxiv | "Run arxiv digest" | `arxiv_digest.py` | Note in Sources/ | |
| 2.4 | hn | "Get HN digest" | `hn_newsletter.py` | HN digest note | |
| 2.5 | obsidian-vault | "Vault analytics" | `obsidian_vault_analytics.py --save` | Stats/health note | |
| 2.6 | daily-synthesis | "Daily synthesis" | `daily_synthesis.py` | Synthesis note | |
| 2.7 | til | "TIL: Python list comprehensions" | `til_capture.py "Python list comprehensions"` | TIL note created | |

---

## Phase 3: Single-Arg Skills

| # | Skill | User Input | Command | Expected Output | Pass/Fail |
|---|-------|------------|---------|-----------------|-----------|
| 3.1 | dictionary | "Look up serendipity" | `dictionary.py serendipity` | Definition, etymology | |
| 3.2 | wiki | "Explain quantum entanglement" | `wiki.py "quantum entanglement"` | Wiki-style tutorial | |
| 3.3 | rag | "Search my vault for mental models" | `rag_query.py "mental models"` | RAG results | |
| 3.4 | web-search | "Search for latest Claude 4 news" | `web_search.py "Claude 4 release"` | Search results | |
| 3.5 | project | "List my projects" | `project_track.py list` | Project list | |
| 3.6 | goal | "Review my goals" | `goal_track.py review` | Goal review | |

---

## Phase 4: Multi-Arg / Complex Skills

| # | Skill | User Input | Command | Expected Output | Pass/Fail |
|---|-------|------------|---------|-----------------|-----------|
| 4.1 | bookmark | "Process this URL: https://example.com/article" | `bookmark_process.py URL` | Structured note | |
| 4.2 | meeting | "Structure these meeting notes: [path]" | `meeting_notes.py PATH` | Action items | |
| 4.3 | debate | "Debate: universal basic income" | `debate_steelman.py "universal basic income"` | Steelman report | |
| 4.4 | deep-research | "Deep research on RAG architectures" | `deep_research.py "RAG architectures"` | Research report | |

---

## Phase 5: Error Handling & Edge Cases

| # | Test | User Input | Expected Behavior | Pass/Fail |
|---|------|------------|-------------------|-----------|
| 5.1 | Unknown skill | "Run the flux capacitor" | Graceful: "I don't have that skill. Here are similar ones..." | |
| 5.2 | Missing arg | "Run dictionary" (no word) | Asks for the word to look up | |
| 5.3 | Script error | Skill that fails (e.g. bad API key) | Reports error, suggests check config | |
| 5.4 | Long-running | "Run org-daily" | Explains it may take minutes, runs or offers to run | |

---

## Phase 6: Telegram-Specific

| # | Test | Channel | User Input | Expected | Pass/Fail |
|---|------|---------|------------|----------|-----------|
| 6.1 | Telegram auth | Telegram | Any message | Only user 6684292977 gets response | |
| 6.2 | Skill via Telegram | Telegram | "Run org-list" | Same as CLI: exec → response | |
| 6.3 | Output length | Telegram | "HN digest" | Truncates or summarizes if very long | |

---

## Execution Checklist

- [ ] Phase 1: Discovery (4 tests)
- [ ] Phase 2: Zero-arg skills (7 tests)
- [ ] Phase 3: Single-arg skills (6 tests)
- [ ] Phase 4: Complex skills (4 tests)
- [ ] Phase 5: Error handling (4 tests)
- [ ] Phase 6: Telegram (3 tests)

**Total: 28 test cases**

---

## Quick Smoke Test (5 min)

Run these 5 first to validate the integration:

1. `nanobot agent -m "List all available skills"`
2. `nanobot agent -m "Run org-list"`
3. `nanobot agent -m "Look up serendipity in the dictionary"`
4. `nanobot agent -m "TIL: nanobot can run PAI skills"`
5. `nanobot agent -m "What's in my vault? Run obsidian-vault analytics"`

---

## Notes

- **Env:** Scripts load `.env` from vault root via `config.py` (VAULT_PATH). When exec runs `python3 _scripts/xxx.py` from vault, cwd should be vault — verify scripts resolve paths correctly.
- **API keys:** Skills like arxiv, hn, web-search need keys in vault `.env`. Nanobot exec inherits its env; scripts load dotenv from vault, so keys should be available.
- **Cleanup:** Delete test output files (e.g. Sources/* from test runs) per user preference after tests.
