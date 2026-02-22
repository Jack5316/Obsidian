#!/usr/bin/env python3
"""Job Seeking - Aggregate latest job listings from multiple platforms for China job search.

Sources:
- V2EX 酷工作: Tech community job postings (China-focused, free API)
- RemoteOK: Global remote jobs (includes China-remote roles, free API)

Config: _scripts/job_keywords.txt for keyword filtering (optional).
"""

import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup

from config import summarize, save_note, VAULT_PATH, TRACKER

V2EX_API = "https://www.v2ex.com/api"
REMOTEOK_API = "https://remoteok.com/api"
KEYWORDS_FILE = VAULT_PATH / "_scripts" / "job_keywords.txt"
REQUEST_DELAY = 1.5
TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

DIGEST_PROMPT = """You are a job search curator for someone seeking opportunities in China. Given job listings from V2EX (酷工作) and RemoteOK, create a structured digest:

1. **By category/role** - Group similar roles (e.g., Backend, Frontend, AI/ML, Product, etc.)
2. **For each notable listing** - Title, company/location hint, salary if mentioned, key requirements
3. **Highlight China-relevant** - Flag roles in Beijing, Shanghai, Shenzhen, Hangzhou, or remote-for-China
4. **Actionable** - Note which seem most promising and why
5. **Cross-domain** - If any roles connect to AI, chips, philosophy, or your known interests, note them

Use [[wikilinks]] for skills, cities, and companies where useful.
Do NOT include YAML frontmatter or a title heading - start directly with the first category."""


def load_keywords() -> List[str]:
    """Load optional keyword filter from config file."""
    if not KEYWORDS_FILE.exists():
        return []
    lines = KEYWORDS_FILE.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def fetch_v2ex_jobs(limit: int = 30) -> List[dict]:
    """Fetch job postings from V2EX 酷工作 node."""
    jobs = []
    try:
        time.sleep(REQUEST_DELAY)
        resp = requests.get(f"{V2EX_API}/topics/latest.json", headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        topics = resp.json()
    except Exception as e:
        print(f"  Warning: V2EX fetch failed: {e}")
        return []

    # V2EX 酷工作 node (job postings only; "career" is discussions)
    for t in topics:
        node = t.get("node") or {}
        if node.get("name") != "jobs":
            continue

        jobs.append({
            "source": "V2EX 酷工作",
            "title": t.get("title", ""),
            "url": f"https://www.v2ex.com/t/{t.get('id', '')}",
            "author": t.get("member", {}).get("username", ""),
            "replies": t.get("replies", 0),
            "created": datetime.fromtimestamp(t.get("created", 0)).strftime("%Y-%m-%d %H:%M"),
            "content_preview": (t.get("content", "") or "")[:300].replace("\n", " "),
        })

        if len(jobs) >= limit:
            break

    # Fallback: scrape jobs page when API returns 0 (API only has latest from all nodes)
    if len(jobs) == 0:
        jobs = fetch_v2ex_jobs_fallback(limit)

    return jobs


def fetch_v2ex_jobs_fallback(limit: int = 25) -> List[dict]:
    """Fallback: scrape V2EX 酷工作 page when API returns no jobs."""
    url = "https://www.v2ex.com/go/jobs"
    try:
        time.sleep(REQUEST_DELAY)
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"  Warning: V2EX fallback fetch failed: {e}")
        return []

    jobs = []
    for a in soup.select("span.item_title a"):
        if not a.get("href"):
            continue
        title = a.get_text(strip=True)
        href = a["href"].split("#")[0]
        if not href.startswith("http"):
            href = "https://www.v2ex.com" + href
        jobs.append({
            "source": "V2EX 酷工作",
            "title": title,
            "url": href,
            "author": "",
            "replies": 0,
            "created": "",
            "content_preview": "",
        })
        if len(jobs) >= limit:
            break
    return jobs


def fetch_remoteok_jobs(limit: int = 20) -> List[dict]:
    """Fetch remote job listings from RemoteOK API."""
    jobs = []
    try:
        time.sleep(REQUEST_DELAY)
        resp = requests.get(REMOTEOK_API, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  Warning: RemoteOK fetch failed: {e}")
        return []

    # First item is metadata (last_updated, legal); rest are job objects
    if isinstance(data, list):
        items = data[1:] if (len(data) > 1 and isinstance(data[0], dict) and "position" not in data[0]) else data
    else:
        items = []

    for item in items:
        if not isinstance(item, dict) or not item.get("position"):
            continue
        job_id = item.get("id", "")
        jobs.append({
            "source": "RemoteOK",
            "title": item.get("position", ""),
            "company": item.get("company", "") or "",
            "url": f"https://remoteok.com/l/{job_id}" if job_id else "",
            "location": item.get("location", "") or "",
            "salary": str(item.get("salary_min", "")) if item.get("salary_min") else (str(item.get("salary_max", "")) if item.get("salary_max") else ""),
            "tags": ", ".join(item.get("tags", [])[:5]) if item.get("tags") else "",
            "epoch": item.get("epoch", 0),
        })
        if len(jobs) >= limit:
            break

    return jobs


def filter_by_keywords(jobs: List[dict], keywords: List[str]) -> List[dict]:
    """Filter jobs by keywords (title, content, company, location)."""
    if not keywords:
        return jobs
    kw_lower = [k.lower() for k in keywords]
    filtered = []
    for j in jobs:
        text = " ".join([
            str(j.get("title", "")),
            str(j.get("company", "")),
            str(j.get("location", "")),
            str(j.get("content_preview", "")),
            str(j.get("tags", "")),
        ]).lower()
        if any(k in text for k in kw_lower):
            filtered.append(j)
    return filtered


def main():
    parser = argparse.ArgumentParser(
        description="Job Seeking - Aggregate job listings from V2EX, RemoteOK for China job search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/job_seeking.py
  python3 _scripts/job_seeking.py --v2ex-only
  python3 _scripts/job_seeking.py --keywords Python 北京
  python3 _scripts/job_seeking.py --no-save
""",
    )
    parser.add_argument("--v2ex-only", action="store_true", help="Fetch only V2EX 酷工作")
    parser.add_argument("--remoteok-only", action="store_true", help="Fetch only RemoteOK")
    parser.add_argument("--keywords", nargs="*", help="Filter by keywords (overrides job_keywords.txt)")
    parser.add_argument("--limit-v2ex", type=int, default=25, help="Max V2EX jobs (default: 25)")
    parser.add_argument("--limit-remoteok", type=int, default=15, help="Max RemoteOK jobs (default: 15)")
    parser.add_argument("--no-save", action="store_true", help="Print only, do not save to vault")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI digest, raw listing only")
    args = parser.parse_args()

    keywords = args.keywords if args.keywords is not None else load_keywords()

    all_jobs = []

    if not args.remoteok_only:
        print("Fetching V2EX 酷工作...")
        v2ex = fetch_v2ex_jobs(limit=args.limit_v2ex)
        all_jobs.extend(v2ex)
        print(f"  Found {len(v2ex)} V2EX jobs")

    if not args.v2ex_only:
        print("Fetching RemoteOK...")
        remoteok = fetch_remoteok_jobs(limit=args.limit_remoteok)
        all_jobs.extend(remoteok)
        print(f"  Found {len(remoteok)} RemoteOK jobs")

    if keywords:
        all_jobs = filter_by_keywords(all_jobs, keywords)
        print(f"  After keyword filter: {len(all_jobs)} jobs")

    if not all_jobs:
        print("No jobs found.")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    # Build raw table
    rows = []
    for j in all_jobs:
        title = (j.get("title", "") or "")[:50] + ("..." if len(j.get("title", "") or "") > 50 else "")
        url = j.get("url", "")
        source = j.get("source", "")
        extra = ""
        if j.get("company"):
            extra = j["company"]
        elif j.get("location"):
            extra = j["location"]
        elif j.get("author"):
            extra = f"by {j['author']}"
        rows.append(f"| [{title}]({url}) | {source} | {extra} |")

    table = "\n".join(rows)

    # AI digest
    jobs_text = "\n\n".join(
        "**{title}**\nSource: {source}\nURL: {url}\n{extra}".format(
            title=j.get("title", ""),
            source=j.get("source", ""),
            url=j.get("url", ""),
            extra=" | ".join(
                f"{k}: {v}" for k, v in j.items()
                if k not in ("title", "source", "url") and v
            ),
        )
        for j in all_jobs[:40]
    )

    if args.no_ai:
        digest_body = "*AI digest skipped (--no-ai)*"
    else:
        print("Generating AI digest...")
        digest_body = summarize(jobs_text, DIGEST_PROMPT)

    note = f"""---
type: job-digest
date: {today}
sources: [V2EX 酷工作, RemoteOK]
job_count: {len(all_jobs)}
tags:
  - source/jobs
  - job-seeking
  - china
---

# Job Digest - {today}

> [!info] {len(all_jobs)} job listings from multiple platforms

## Raw Listings

| Title | Source | Extra |
|-------|--------|-------|
{table}

---

## AI Curated Digest

{digest_body}

---

*Sources: V2EX 酷工作 (tech community), RemoteOK (remote jobs). Configure keywords in _scripts/job_keywords.txt*
"""

    if args.no_save:
        print(note)
        return

    save_note(f"Sources/Job Digest - {today}.md", note)
    print(f"Saved: Sources/Job Digest - {today}.md")

    if TRACKER:
        TRACKER.record_operation(
            script_name="job_seeking.py",
            operation_type="job_digest",
            status="success",
            metrics={"count": len(all_jobs)},
        )


if __name__ == "__main__":
    main()
