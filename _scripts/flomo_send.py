#!/usr/bin/env python3
"""Send notes to flomo via incoming webhook.

Sends text content to your flomo floating notes application using
the incoming webhook API. Supports tags and rich formatting.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import requests

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import TRACKER, VAULT_PATH

# Default flomo webhook URL - user should set this in .env
# Example: FLOMO_WEBHOOK_URL=https://flomoapp.com/iwh/MjQxMjYx/a5f8df0bdd24034086c277c01a98cbe8/
import os
FLOMO_WEBHOOK_URL = os.getenv("FLOMO_WEBHOOK_URL", "")


def send_to_flomo(content: str, webhook_url: Optional[str] = None) -> bool:
    """
    Send content to flomo via webhook.
    
    Args:
        content: The text content to send (can include #tags)
        webhook_url: Optional custom webhook URL (uses env var if not provided)
    
    Returns:
        True if successful, False otherwise
    """
    url = webhook_url or FLOMO_WEBHOOK_URL
    
    if not url:
        print("Error: No flomo webhook URL configured.")
        print("Please set FLOMO_WEBHOOK_URL in your .env file.")
        return False
    
    try:
        response = requests.post(
            url,
            json={"content": content},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        
        # Check if flomo returned success
        # Flomo typically returns {"code": 0, "message": "success"} on success
        try:
            result = response.json()
            if result.get("code") == 0 or result.get("message") == "success":
                return True
            else:
                print(f"flomo API error: {result}")
                return False
        except (json.JSONDecodeError, KeyError):
            # If response isn't JSON or doesn't have expected fields,
            # consider it successful if HTTP status is OK
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"Error sending to flomo: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Send notes to flomo - /flomo for floating notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/flomo_send.py "My great idea"
  python3 _scripts/flomo_send.py "Project brainstorm" --tag "idea" --tag "project"
  python3 _scripts/flomo_send.py "Book insight" --webhook "https://flomoapp.com/iwh/your/key/"
        """
    )
    parser.add_argument(
        "content", nargs="*", help="Content of the note (quoted string)"
    )
    parser.add_argument(
        "-t", "--tag", action="append", dest="tags",
        help="Add a tag to the note (can use multiple times)"
    )
    parser.add_argument(
        "-w", "--webhook",
        help="Custom flomo webhook URL (overrides env var)"
    )
    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="flomo_send.py",
            operation_type="send_to_flomo",
            status="in_progress",
            metrics={}
        )

    try:
        # Get content - from args or stdin
        content = " ".join(args.content)
        if not content:
            # Read from stdin if no args provided
            if not sys.stdin.isatty():
                content = sys.stdin.read().strip()
        
        if not content:
            print("Usage: /flomo \"Your note here\"")
            print("Error: No content provided for flomo")
            if TRACKER:
                TRACKER.record_operation(
                    script_name="flomo_send.py",
                    operation_type="send_to_flomo",
                    status="failed",
                    metrics={"error": "No content provided"}
                )
            return 1

        # Add tags to content
        if args.tags:
            tag_str = " ".join([f"#{tag}" for tag in args.tags])
            content = f"{content}\n\n{tag_str}"

        # Send to flomo
        success = send_to_flomo(content, args.webhook)
        
        if success:
            print("✅ Note sent to flomo!")
            if TRACKER:
                TRACKER.record_operation(
                    script_name="flomo_send.py",
                    operation_type="send_to_flomo",
                    status="success",
                    metrics={"content_length": len(content)}
                )
            return 0
        else:
            if TRACKER:
                TRACKER.record_operation(
                    script_name="flomo_send.py",
                    operation_type="send_to_flomo",
                    status="failed",
                    metrics={"error": "Failed to send to flomo"}
                )
            return 1
        
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="flomo_send.py",
                operation_type="send_to_flomo",
                status="failed",
                metrics={"error": str(e)}
            )
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
