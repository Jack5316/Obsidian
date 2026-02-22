---
name: agent-news
description: >
  Fetch, parse, and summarize news from machine-readable sources designed for
  AI agents. Use when the user asks for news, headlines, or current events via
  structured feeds — RSS/Atom, JSON APIs, or llms.txt-compatible endpoints —
  without scraping human-facing GUIs.
---

# Agent News Skill

Retrieve news programmatically from AI-friendly, structured sources. Prefer
sources that return clean data with no HTML rendering required.

---

## Source Hierarchy

Always try sources in this order, falling back as needed:

### Tier 1 — JSON APIs (cleanest, most structured)

| Source | Endpoint | Notes |
|--------|----------|-------|
| NewsAPI | `https://newsapi.org/v2/top-headlines?apiKey=KEY&q=TOPIC` | Requires free API key from newsapi.org |
| GNews | `https://gnews.io/api/v4/search?q=TOPIC&token=KEY` | Free tier: 100 req/day |
| TheNewsAPI | `https://api.thenewsapi.com/v1/news/top?api_token=KEY` | Good category support |
| Currents API | `https://api.currentsapi.services/v1/latest-news?apiKey=KEY` | Free tier available |

### Tier 2 — RSS/Atom Feeds (XML, universally available, no key needed)

Parse with Python's `feedparser` library.

**General news:**
```
https://feeds.bbci.co.uk/news/rss.xml
https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml
https://feeds.reuters.com/reuters/topNews
https://feeds.skynews.com/feeds/rss/home.xml
https://rss.cnn.com/rss/edition.rss
```

**Technology / AI:**
```
https://techcrunch.com/feed/
https://venturebeat.com/category/ai/feed/
https://www.theverge.com/rss/index.xml
https://feeds.arstechnica.com/arstechnica/index
https://www.technologyreview.com/feed/
https://www.wired.com/feed/rss
```

**Research / AI-specific:**
```
https://bair.berkeley.edu/blog/feed.xml
https://research.google/blog/rss
https://openai.com/news/rss.xml
https://www.anthropic.com/news/rss
```

### Tier 3 — llms.txt endpoints (emerging standard)

Some sites expose a machine-readable content index at `/llms.txt`. Fetch and
parse this to discover structured links to their content.

### Tier 4 — Legacy tophub.today scraping (maintained for backward compatibility)

The existing `tophub_news.py` is preserved for Chinese news.

---

## Usage

```bash
# RSS only (no API key needed)
python3 _scripts/agent_news.py

# With topic filter
python3 _scripts/agent_news.py --topic "AI"

# Specific sources only
python3 _scripts/agent_news.py --sources "BBC,TechCrunch"

# More results
python3 _scripts/agent_news.py --limit 20

# With NewsAPI key (set in .env)
python3 _scripts/agent_news.py --use-api
```

## Output

`Sources/Agent News Digest - YYYY-MM-DD.md` (theme-organized, [[wikilinks]])

---

## Key Principles

- **Never scrape GUI pages** when a feed or API exists for the same source.
- **Prefer structured data** (JSON > RSS/XML > scraped HTML).
- **Respect rate limits** — cache results locally if running multiple queries.
- **Attribute sources** — always include the outlet name and original URL.
- **No hallucination** — only report articles actually returned by the feed.
- **Be transparent about staleness** — note the `published` timestamp.
