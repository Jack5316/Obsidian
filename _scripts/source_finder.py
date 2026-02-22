"""Source Finder - Find the best Substack, newsletter, blog, Twitter post, podcast, wiki, article, YouTube video on a particular subject.

Uses AI to help curate and discover the best content sources on any topic.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


SOURCE_FINDER_PROMPT = """You are an expert content curator and researcher. Your task is to help find the very best content sources on a given subject.

The user wants content recommendations for the topic: "{topic}"

Please recommend the BEST available content across these categories:
1. **Substack Newsletters** - High-quality newsletters on Substack
2. **Blogs** - Excellent blogs (personal or professional)
3. **Twitter/X Threads/Posts** - Insightful Twitter content and accounts to follow
4. **Podcasts** - Top podcasts and specific episodes
5. **Articles** - Long-form articles and essays
6. **YouTube Videos** - Educational or insightful videos/channels
7. **Wikis & References** - Comprehensive reference sources

For each recommendation, include:
- Title/Name
- URL or where to find it
- Brief description of why it's valuable
- What makes it stand out from other content on the topic

Also include:
- A "Quick Start" section with the 2-3 most essential sources
- A "Reading Path" section suggesting the order to explore the content

Format everything in clean Markdown with clear headings. Do NOT include YAML frontmatter.
Use [[wikilinks]] for related concepts that might exist in the user's Obsidian vault.

If the topic is very niche and you don't have specific knowledge, provide a research framework for how to find good sources on this topic.
"""


def find_sources(topic: str) -> str:
    """Find the best sources on a given topic using AI."""
    prompt = SOURCE_FINDER_PROMPT.format(topic=topic)
    result = summarize(topic, prompt)
    return result


def main():
    """Main function for the source finder skill."""
    parser = argparse.ArgumentParser(
        description="Source Finder - Find the best content on any subject",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill source "machine learning"          # Find sources on machine learning
  /skill source "philosophy of mind"        # Find sources on philosophy of mind
  /skill source "product management" --save  # Save results to vault
"""
    )
    
    parser.add_argument(
        "topic",
        type=str,
        help="The subject to find content sources for"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to vault"
    )
    
    args = parser.parse_args()
    
    print(f"🔍 Finding the best sources on: {args.topic}")
    print("=" * 60)
    
    result = find_sources(args.topic)
    
    print(result)
    
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        # Create a safe filename
        safe_topic = args.topic.replace(" ", "-").replace("/", "-").replace("\\", "-")[:50]
        save_note(f"Sources/Source Guide - {safe_topic} - {date_str}.md", result)


if __name__ == "__main__":
    main()
