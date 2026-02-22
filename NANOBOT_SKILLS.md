# PAI Skills Reference for Nanobot

This vault has **70+ skills** (Python scripts) you can invoke via the `exec` tool. Always run from the vault root. Format: `python3 _scripts/<script>.py [args]`.

## How to Invoke a Skill

When the user asks for a skill (e.g. "run arxiv", "get HN digest", "search my vault"), run the corresponding command using the exec tool. Example: `python3 _scripts/arxiv_digest.py`

## Quick Reference by Category

### Orchestration
| Skill | Command |
|-------|---------|
| org | `python3 _scripts/org_skill.py` |
| org-daily | `python3 _scripts/org_skill.py --daily` |
| org-weekly | `python3 _scripts/org_skill.py --weekly` |
| org-list | `python3 _scripts/org_skill.py --list` |
| org-status | `python3 _scripts/org_skill.py --status` |
| org-logs | `python3 _scripts/org_skill.py --logs` |

### Content Curation
| Skill | Command |
|-------|---------|
| ai-brief | `python3 _scripts/ai_brief.py` |
| arxiv | `python3 _scripts/arxiv_digest.py` |
| hn | `python3 _scripts/hn_newsletter.py` |
| reddit | `python3 _scripts/reddit_digest.py` |
| news | `python3 _scripts/tophub_news_simple.py` |
| twitter | `python3 _scripts/twitter_capture.py` |
| bookmark | `python3 _scripts/bookmark_process.py` [URL...] |
| skill-grab | `python3 _scripts/skill_grab.py` |
| product-hunt | `python3 _scripts/product_hunt.py` |

### Knowledge & Search
| Skill | Command |
|-------|---------|
| rag | `python3 _scripts/rag_query.py` "query" |
| filter | `python3 _scripts/filter_query.py` "query" |
| deep-research | `python3 _scripts/deep_research.py` "topic" |
| connect | `python3 _scripts/knowledge_graph.py` |
| concept | `python3 _scripts/concept_extract.py` |
| wiki | `python3 _scripts/wiki.py` "topic" |
| dictionary | `python3 _scripts/dictionary.py` WORD |
| source | `python3 _scripts/source_finder.py` "topic" |

### Capture & Notes
| Skill | Command |
|-------|---------|
| til | `python3 _scripts/til_capture.py` "learning" |
| question | `python3 _scripts/question_capture.py` "question" |
| mem | `python3 _scripts/mem_capture.py` "thought" |
| book | `python3 _scripts/book_notes.py` title "Title" |
| movie | `python3 _scripts/movie_notes.py` "Title" |
| person | `python3 _scripts/person_profile.py` "Name" |

### Tasks & Projects
| Skill | Command |
|-------|---------|
| project | `python3 _scripts/project_track.py` list/create/log |
| goal | `python3 _scripts/goal_track.py` list/review |
| habit | `python3 _scripts/habit_track.py` list/log/analyze |
| obsidian-tasks | `python3 _scripts/obsidian_task_manager.py` |
| things | `python3 _scripts/things.py` add/show/search |

### Synthesis & Writing
| Skill | Command |
|-------|---------|
| daily-synthesis | `python3 _scripts/daily_synthesis.py` |
| weekly | `python3 _scripts/weekly_synthesis.py` |
| essay | `python3 _scripts/essay.py` |
| debate | `python3 _scripts/debate_steelman.py` "topic" |
| thread | `python3 _scripts/thread_from_insights.py` |

### Vault & Obsidian
| Skill | Command |
|-------|---------|
| obsidian-vault | `python3 _scripts/obsidian_vault_analytics.py --save` |
| obsidian-links | `python3 _scripts/obsidian_link_analyzer.py --save` |
| knowledge-graph | `python3 _scripts/knowledge_graph.py --save` |
| clean | `python3 _scripts/clean_redundant.py scan` |
| second-brain-audit | `python3 _scripts/pipeline.py --run second-brain-audit` |

### Utilities
| Skill | Command |
|-------|---------|
| web-fetch | `python3 _scripts/web_fetch.py` URL |
| web-search | `python3 _scripts/web_search.py` "query" |
| notify | `python3 _scripts/notify.py` "Title" "Message" |
| dictionary | `python3 _scripts/dictionary.py` WORD |
| quotes | `python3 _scripts/quotes.py` "topic" |

### Self-Improvement
| Skill | Command |
|-------|---------|
| reflect | `python3 _scripts/self_reflection.py reflect --save` |
| evolve | `python3 _scripts/self_evolution.py cycle` |
| insights | `python3 _scripts/insight_enhancement.py` |
| zen | `python3 _scripts/self_reflection.py reflect` |

### Nanobot Integration
| Skill | Command |
|-------|---------|
| nanobot | `python3 _scripts/nanobot_skill.py` chat/status/gateway/info/list-skills |

### Other
| Skill | Command |
|-------|---------|
| api | `python3 _scripts/api_finder.py` "subject" |
| job-seeking | `python3 _scripts/job_seeking.py` |
| flashcard | `python3 _scripts/flashcard_generate.py` [PATH] |
| gateway | `python3 _scripts/gateway.py` |
| package | `python3 _scripts/package_skill.py --save` |

## Matching User Intent to Skills

- "HN digest" / "hacker news" → hn
- "ArXiv" / "papers" → arxiv
- "search my notes" / "RAG" → rag
- "look up word" → dictionary
- "today I learned" / "TIL" → til
- "remember this" → mem
- "vault stats" / "health" → obsidian-vault
- "list skills" → org-list or read this file
