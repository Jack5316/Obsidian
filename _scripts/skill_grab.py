"""Collect latest best skills from skills.sh into an Obsidian digest note.

Fetches the skills.sh leaderboard (trending, hot, or all-time), parses skills,
and optionally uses AI to curate a digest. Saves to Sources/.
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Add parent for config
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH

SKILLS_BASE = "https://skills.sh"
SOURCES = {
    "trending": f"{SKILLS_BASE}/trending",
    "hot": f"{SKILLS_BASE}/hot",
    "all": SKILLS_BASE,
}

EXCLUDE_PATHS = {"agents", "docs", "api", "_next", "trending", "hot"}

CURATE_PROMPT = """You are curating the best AI agent skills from skills.sh for a developer using Claude Code and Obsidian.

Given a ranked list of skills (name, install command, URL), produce a concise digest note:

1. **Top Picks** — Select 10–15 skills most valuable for: coding (React, Next.js, Python, testing), AI workflows, Obsidian/knowledge work, and productivity. Briefly explain why each is useful.
2. **By Category** — Group remaining notable skills by theme (frontend, backend, marketing, devops, etc.) with one-line descriptions.
3. **Install** — Include the `npx skills add <owner/repo>` command for each top pick.

Use [[wikilinks]] for key concepts. No YAML frontmatter. Start directly with content.
Output in clean Markdown suitable for Obsidian."""


def fetch_skills(source: str = "trending", max_count: int = 100) -> List[dict]:
    """Fetch and parse skills from skills.sh leaderboard."""
    url = SOURCES.get(source, SOURCES["trending"])
    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    skills = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if not href.startswith("/"):
            continue
        parts = href.strip("/").split("/")
        if len(parts) != 3:
            continue
        owner, repo, skill_name = parts
        if owner in EXCLUDE_PATHS:
            continue
        key = f"{owner}/{repo}/{skill_name}"
        if key in seen:
            continue
        seen.add(key)
        full_url = urljoin(SKILLS_BASE, href)
        skills.append({
            "rank": len(skills) + 1,
            "name": skill_name,
            "owner": owner,
            "repo": repo,
            "install": f"npx skills add {owner}/{repo}",
            "url": full_url,
        })
        if len(skills) >= max_count:
            break

    return skills


def build_raw_markdown(skills: List[dict], source: str) -> str:
    """Build raw markdown list without AI curation."""
    lines = [
        f"# Skills.sh Digest — {source.title()}",
        "",
        f"*Fetched {datetime.now().strftime('%Y-%m-%d %H:%M')} from [skills.sh]({SKILLS_BASE})*",
        "",
        "## Top Skills",
        "",
    ]
    for s in skills:
        lines.append(f"- **{s['name']}** — `{s['install']}`")
        lines.append(f"  - [{s['owner']}/{s['repo']}]({s['url']})")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Collect latest best skills from skills.sh",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/skill_grab.py
  python3 _scripts/skill_grab.py --source hot --count 50
  python3 _scripts/skill_grab.py --no-ai
""",
    )
    parser.add_argument(
        "-s", "--source",
        choices=["trending", "hot", "all"],
        default="trending",
        help="Leaderboard source (default: trending)",
    )
    parser.add_argument(
        "-c", "--count",
        type=int,
        default=50,
        help="Max skills to fetch (default: 50)",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip AI curation; output raw list only",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print to stdout instead of saving",
    )
    args = parser.parse_args()

    print(f"Fetching skills from skills.sh ({args.source})...")
    skills = fetch_skills(args.source, args.count)
    if not skills:
        print("No skills found.")
        return 1

    print(f"Found {len(skills)} skills.")

    if args.no_ai:
        content = build_raw_markdown(skills, args.source)
    else:
        raw_list = "\n".join(
            f"{s['rank']}. {s['name']} — {s['install']} — {s['url']}"
            for s in skills
        )
        content = summarize(raw_list, CURATE_PROMPT)

    if args.print:
        print(content)
        return 0

    date_str = datetime.now().strftime("%Y-%m-%d")
    path = f"Sources/Skills Digest - {date_str}.md"
    save_note(path, content)
    print(f"Saved: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
