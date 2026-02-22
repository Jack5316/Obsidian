---
name: deepseek
description: Chat with DeepSeek API for cost-effective AI conversations. Use DeepSeek to reduce model usage costs while maintaining high-quality AI responses. Use when user says "deepseek", "/deepseek", or wants a cost-effective AI conversation.
---

# DeepSeek Chat Skill (/deepseek)

Chat with DeepSeek API for cost-effective AI conversations while maintaining high-quality responses. Perfect for reducing model usage costs without sacrificing quality.

## Quick Start

```bash
python3 _scripts/deepseek_chat.py "Your question or prompt here"
```

## Features

1. **Cost-Effective AI** - Use DeepSeek API to reduce model usage costs
2. **High-Quality Responses** - DeepSeek provides excellent performance for various tasks
3. **Multiple Models** - Supports `deepseek-chat` (general purpose) and `deepseek-coder` (coding focused)
4. **Streaming Support** - Stream responses in real-time
5. **Custom System Prompts** - Set behavior with system prompts
6. **Temperature Control** - Adjust creativity from focused (0.0) to creative (2.0)

## Options

- `prompt`: Main question or prompt (quoted string)
- `-s, --system TEXT`: System prompt to set AI behavior
- `-m, --model TEXT`: Model to use (deepseek-chat, deepseek-coder)
- `-t, --temperature FLOAT`: Sampling temperature (0-2, default: 0.7)
- `--max-tokens INT`: Maximum tokens in response
- `--stream`: Stream the response in real-time
- `--api-key TEXT`: DeepSeek API key (overrides env var)
- `--base-url TEXT`: DeepSeek API base URL (overrides env var)

## Examples

```bash
# Basic chat
python3 _scripts/deepseek_chat.py "Explain quantum computing in simple terms"

# Code-focused question
python3 _scripts/deepseek_chat.py --model deepseek-coder "Write a Python function to sort a list"

# With system prompt
python3 _scripts/deepseek_chat.py "Tell me a joke" --system "You are a comedian who tells only programming jokes"

# Creative mode (high temperature)
python3 _scripts/deepseek_chat.py "Write a short story" --temperature 1.5

# Streamed response
python3 _scripts/deepseek_chat.py "Explain machine learning" --stream

# From stdin
echo "What is the meaning of life?" | python3 _scripts/deepseek_chat.py
```

## Models

- **deepseek-chat** (default) - General purpose chat model, great for most conversations
- **deepseek-coder** - Specialized for coding tasks, code generation, and debugging

## When to Use

- When you want to reduce model usage costs
- For general purpose conversations and questions
- For code generation and debugging
- For creative writing and brainstorming
- When you need high-quality AI responses at lower cost

## Tips

- Use `--stream` for long responses to see output in real-time
- Lower `--temperature` (0.0-0.3) for more focused, deterministic answers
- Higher `--temperature` (1.0-2.0) for more creative, diverse outputs
- Use `--model deepseek-coder` for all coding-related tasks
- Set custom system prompts with `--system` to tailor AI behavior
- The API key is stored in your .env file as DEEPSEEK_API_KEY
