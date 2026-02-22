---
name: org-daily
description: Run daily automation scripts (ArXiv, HN, Reddit, news, Twitter). Use when user asks for daily curation or /org-daily.
---

# Daily Organization Skill

Runs daily content curation: ArXiv, HN, Reddit, news, Twitter.

## Usage

```bash
python3 _scripts/org_skill.py --daily
```

## Options

- `-v, --verbose`: Stream each script's output (runs sequentially)
- `-s, --skip s1,s2`: Skip specific scripts

## Scripts

arxiv_digest.py, hn_newsletter.py, reddit_digest.py, tophub_news_simple.py, twitter_capture.py

## Output

Notes to `Sources/` with dated filenames (e.g., `Sources/ArXiv Digest - 2026-02-18.md`).
