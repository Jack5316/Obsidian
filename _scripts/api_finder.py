"""API Finder - Find the best database and API interfaces for a particular subject.

Uses AI to recommend the best databases, REST/GraphQL APIs, SDKs, and data interfaces
for any topic or use case.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


API_FINDER_PROMPT = """You are an expert on databases, APIs, and data interfaces. Your task is to find the best database and API options for a given subject or use case.

The user is looking for: "{topic}"

Please recommend the BEST available options across these categories:

1. **Databases** — Best databases for this domain (SQL, NoSQL, vector DBs, time-series, graph, etc.)
   - Include: name, type, key features, pricing tier (free/paid), link
   - Consider: hosted vs self-hosted, scalability, ecosystem

2. **REST APIs** — Public or commercial APIs that provide data/services for this subject
   - Include: name, provider, endpoint, auth type, rate limits, documentation link
   - Note free tiers and pricing where relevant

3. **GraphQL APIs** — GraphQL interfaces if available for this domain

4. **SDKs & Client Libraries** — Official or well-maintained client libraries for the recommended APIs
   - Include: language, package name, GitHub/npm/pypi link

5. **Data Marketplaces & Aggregators** — Platforms that aggregate multiple APIs (e.g., RapidAPI, Apify) for this subject

6. **Alternative Interfaces** — Webhooks, streaming APIs, bulk export options if applicable

For each recommendation, include:
- Name and brief description
- URL or documentation link
- Why it's best for this subject
- Key limitations or considerations

Also include:
- **Quick Start** — Top 2–3 options to try first
- **Comparison** — When to choose which (e.g., "Use X for real-time, Y for batch")

Format in clean Markdown with clear headings. No YAML frontmatter.
Use [[wikilinks]] for related concepts. Be specific with URLs and package names."""


def find_apis(topic: str) -> str:
    """Find the best databases and APIs for a given subject using AI."""
    prompt = API_FINDER_PROMPT.format(topic=topic)
    result = summarize(topic, prompt)
    return result


def main():
    """Main function for the API finder skill."""
    parser = argparse.ArgumentParser(
        description="Find the best database and API interfaces for a subject",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/api_finder.py "stock market data"
  python3 _scripts/api_finder.py "weather" --save
  python3 _scripts/api_finder.py "AI/LLM embeddings"
""",
    )
    parser.add_argument(
        "topic",
        type=str,
        help="Subject or use case to find databases and APIs for",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to vault",
    )
    args = parser.parse_args()

    print(f"Finding databases and APIs for: {args.topic}")
    print("=" * 60)

    result = find_apis(args.topic)
    print(result)

    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_topic = args.topic.replace(" ", "-").replace("/", "-").replace("\\", "-")[:50]
        save_note(f"Sources/API Guide - {safe_topic} - {date_str}.md", result)
        print(f"\nSaved: Sources/API Guide - {safe_topic} - {date_str}.md")


if __name__ == "__main__":
    main()
