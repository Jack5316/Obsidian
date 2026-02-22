#!/usr/bin/env python3
"""Chat with DeepSeek API for cost-effective AI conversations.

Use DeepSeek API to reduce model usage costs while maintaining high-quality
AI conversations. Supports chat completions, code generation, and more.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

import requests

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import TRACKER, VAULT_PATH

import os
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


class DeepSeekClient:
    """Client for interacting with DeepSeek API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.base_url = base_url or DEEPSEEK_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Send chat completion request to DeepSeek API.
        
        Args:
            messages: List of message dicts with "role" and "content"
            model: Model to use (defaults to DEEPSEEK_MODEL env var)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            
        Returns:
            API response as dict
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model or DEEPSEEK_MODEL,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        
        if stream:
            payload["stream"] = True
        
        try:
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            if stream:
                return self._handle_stream(response)
            else:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"DeepSeek API error: {e}")
    
    def _handle_stream(self, response: requests.Response) -> Dict[str, Any]:
        """Handle streaming response from DeepSeek API."""
        full_content = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_content += content
                            print(content, end="", flush=True)
                    except json.JSONDecodeError:
                        continue
        
        print()  # New line after stream
        return {
            "choices": [{
                "message": {"content": full_content}
            }],
            "usage": {"total_tokens": "streaming"}
        }


def chat_with_deepseek(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    stream: bool = False,
) -> str:
    """
    Simple one-shot chat with DeepSeek.
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        model: Model to use
        temperature: Sampling temperature
        stream: Whether to stream response
        
    Returns:
        AI response string
    """
    client = DeepSeekClient()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        stream=stream,
    )
    
    return response["choices"][0]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(
        description="Chat with DeepSeek API - /deepseek for cost-effective AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/deepseek_chat.py "Explain quantum computing"
  python3 _scripts/deepseek_chat.py "Write a Python function" --system "You are a coding assistant"
  python3 _scripts/deepseek_chat.py "Tell me a story" --temperature 1.0 --stream
  python3 _scripts/deepseek_chat.py --model deepseek-coder "Debug this code"
        """
    )
    parser.add_argument(
        "prompt", nargs="*", help="Prompt for DeepSeek (quoted string)"
    )
    parser.add_argument(
        "-s", "--system",
        help="System prompt to set behavior"
    )
    parser.add_argument(
        "-m", "--model",
        help="Model to use (deepseek-chat, deepseek-coder)"
    )
    parser.add_argument(
        "-t", "--temperature", type=float, default=0.7,
        help="Sampling temperature (0-2, default: 0.7)"
    )
    parser.add_argument(
        "--max-tokens", type=int,
        help="Maximum tokens in response"
    )
    parser.add_argument(
        "--stream", action="store_true",
        help="Stream the response"
    )
    parser.add_argument(
        "--api-key",
        help="DeepSeek API key (overrides env var)"
    )
    parser.add_argument(
        "--base-url",
        help="DeepSeek API base URL (overrides env var)"
    )
    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="deepseek_chat.py",
            operation_type="deepseek_chat",
            status="in_progress",
            metrics={}
        )

    try:
        # Get prompt - from args or stdin
        prompt = " ".join(args.prompt)
        if not prompt:
            if not sys.stdin.isatty():
                prompt = sys.stdin.read().strip()
        
        if not prompt:
            print("Usage: /deepseek \"Your question or prompt here\"")
            print("Error: No prompt provided for DeepSeek")
            if TRACKER:
                TRACKER.record_operation(
                    script_name="deepseek_chat.py",
                    operation_type="deepseek_chat",
                    status="failed",
                    metrics={"error": "No prompt provided"}
                )
            return 1
        
        # Override API key and base URL if provided
        if args.api_key:
            global DEEPSEEK_API_KEY
            DEEPSEEK_API_KEY = args.api_key
        if args.base_url:
            global DEEPSEEK_BASE_URL
            DEEPSEEK_BASE_URL = args.base_url
        
        if not DEEPSEEK_API_KEY:
            print("Error: No DeepSeek API key configured.")
            print("Please set DEEPSEEK_API_KEY in your .env file.")
            if TRACKER:
                TRACKER.record_operation(
                    script_name="deepseek_chat.py",
                    operation_type="deepseek_chat",
                    status="failed",
                    metrics={"error": "No API key configured"}
                )
            return 1
        
        print("\n🤖 DeepSeek Response:\n")
        print("-" * 50)
        
        response = chat_with_deepseek(
            prompt=prompt,
            system_prompt=args.system,
            model=args.model,
            temperature=args.temperature,
            stream=args.stream,
        )
        
        if not args.stream:
            print(response)
        
        print("-" * 50)
        print("\n✅ Conversation completed with DeepSeek API!")
        
        if TRACKER:
            TRACKER.record_operation(
                script_name="deepseek_chat.py",
                operation_type="deepseek_chat",
                status="success",
                metrics={
                    "prompt_length": len(prompt),
                    "response_length": len(response) if response else 0
                }
            )
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="deepseek_chat.py",
                operation_type="deepseek_chat",
                status="failed",
                metrics={"error": str(e)}
            )
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
