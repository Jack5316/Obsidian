#!/usr/bin/env python3
"""Fetch and digest GitHub activity for specified repos or users.

Uses GitHub API to fetch recent activity, issues, PRs, and creates a digest.
"""

import argparse
import datetime
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests

from config import summarize, save_note, VAULT_PATH, TRACKER

# GitHub API configuration
GITHUB_API = "https://api.github.com"
REQUEST_DELAY = 1  # Rate limit: 60 requests/hour for unauthenticated
TIMEOUT = 30

# Default configuration
DEFAULT_REPOS = ["microsoft/vscode", "facebook/react", "golang/go", "rust-lang/rust"]
DEFAULT_USER = None

ANALYSIS_PROMPT = """You are a technical analyst reviewing GitHub activity. Given recent GitHub activity
(issues, PRs, releases), create a comprehensive digest. For each repository:

1. Key issues & discussions
2. Interesting PRs & new features
3. Releases & version updates
4. Community activity & trends

Also include:
- Overall tech trends across repos
- Notable projects & contributors
- Suggested [[wikilinks]] for technical concepts

Focus on what's technically interesting and potentially impactful.
Do NOT include YAML frontmatter - start directly with the overview."""


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or .env file."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        env_path = VAULT_PATH / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("GITHUB_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                    break
    return token


def github_request(endpoint: str, token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Make a request to GitHub API."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Personal-AI-Infra/1.0",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        time.sleep(REQUEST_DELAY)
        resp = requests.get(
            f"{GITHUB_API}/{endpoint}",
            headers=headers,
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  GitHub API error for {endpoint}: {e}")
        return None


def fetch_repo_activity(repo: str, token: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
    """Fetch recent activity for a repository."""
    since = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat() + "Z"
    
    activity = {
        "repo": repo,
        "issues": [],
        "pulls": [],
        "releases": [],
    }
    
    # Issues
    issues = github_request(
        f"repos/{repo}/issues?state=all&sort=updated&per_page=20&since={since}",
        token
    )
    if issues:
        activity["issues"] = [
            {
                "title": i["title"],
                "url": i["html_url"],
                "state": i["state"],
                "comments": i["comments"],
                "user": i["user"]["login"],
            }
            for i in issues[:10]
            if not i.get("pull_request")  # Filter out PRs
        ]
    
    # Pull Requests
    pulls = github_request(
        f"repos/{repo}/pulls?state=all&sort=updated&per_page=20",
        token
    )
    if pulls:
        activity["pulls"] = [
            {
                "title": p["title"],
                "url": p["html_url"],
                "state": p["state"],
                "user": p["user"]["login"],
            }
            for p in pulls[:10]
        ]
    
    # Releases
    releases = github_request(f"repos/{repo}/releases?per_page=10", token)
    if releases:
        activity["releases"] = [
            {
                "name": r["name"],
                "tag": r["tag_name"],
                "url": r["html_url"],
                "published_at": r["published_at"][:10],
            }
            for r in releases[:5]
        ]
    
    return activity


def format_activity_data(activity: Dict[str, Any]) -> str:
    """Format GitHub activity data for AI analysis."""
    lines = [f"**Repository: {activity['repo']}**"]
    
    if activity["issues"]:
        lines.append("\nIssues:")
        for i in activity["issues"]:
            lines.append(f"- [{i['state']}] {i['title']} ({i['url']}) by {i['user']}")
    
    if activity["pulls"]:
        lines.append("\nPull Requests:")
        for p in activity["pulls"]:
            lines.append(f"- [{p['state']}] {p['title']} ({p['url']}) by {p['user']}")
    
    if activity["releases"]:
        lines.append("\nReleases:")
        for r in activity["releases"]:
            lines.append(f"- {r['name']} ({r['tag']}) - {r['published_at']}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch GitHub activity digest",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-r", "--repos", nargs="+", default=DEFAULT_REPOS,
        help=f"Repositories to track (default: {', '.join(DEFAULT_REPOS)})"
    )
    parser.add_argument(
        "-d", "--days", type=int, default=7,
        help="Days of activity to fetch (default: 7)"
    )
    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="github_digest.py",
            operation_type="fetch_github_activity",
            status="in_progress",
            metrics={"repos": len(args.repos)}
        )

    try:
        token = get_github_token()
        if token:
            print("Using GitHub token for higher rate limits")
        
        print(f"Fetching GitHub activity for {len(args.repos)} repos...")
        
        all_activity = []
        for repo in args.repos:
            print(f"  Fetching {repo}...")
            activity = fetch_repo_activity(repo, token, args.days)
            all_activity.append(activity)
        
        # Format data for AI
        activity_text = "\n\n---\n\n".join(format_activity_data(a) for a in all_activity)
        
        print(f"Generating digest with AI...")
        digest_body = summarize(activity_text, ANALYSIS_PROMPT)
        
        # Save to Obsidian
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"GitHub Digest - {today}.md"
        
        note = f"""---
type: github-digest
date: {today}
repos: [{', '.join(args.repos)}]
tags:
  - source/github
  - tech
  - development
---

# GitHub Digest - {today}

> [!info] Activity from {len(all_activity)} repositories (last {args.days} days)

---

## AI Summary & Analysis

{digest_body}

---

*Data provided by GitHub API (https://api.github.com)*
"""
        
        save_note(f"Sources/{filename}", note)
        print(f"Digest saved to Sources/{filename}")
        
        # Track operation completion
        if TRACKER:
            TRACKER.record_operation(
                script_name="github_digest.py",
                operation_type="fetch_github_activity",
                status="success",
                metrics={
                    "repos": len(all_activity),
                    "output_file": f"Sources/{filename}"
                }
            )
        
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="github_digest.py",
                operation_type="fetch_github_activity",
                status="failed",
                metrics={"error": str(e)}
            )
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
