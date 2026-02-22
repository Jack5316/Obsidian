"""Shared configuration for AI Vault automation scripts."""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load .env from vault root
VAULT_PATH = Path(__file__).resolve().parent.parent
load_dotenv(VAULT_PATH / ".env")

# API keys & credentials
ARK_API_KEY = os.getenv("ARK_API_KEY", "")
BEARBLOG_USER = os.getenv("BEARBLOG_USER", "")
BEARBLOG_PASSWORD = os.getenv("BEARBLOG_PASSWORD", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
THINGS_AUTH_TOKEN = os.getenv("THINGS_AUTH_TOKEN", "")
CUBOX_API_URL = os.getenv("CUBOX_API_URL", "")  # Full URL from Cubox 偏好设置 > API 扩展
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")  # From newsapi.org
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")  # From gnews.io

# Default to DeepSeek for cost savings
DEFAULT_MODEL = DEEPSEEK_MODEL

# AI clients
# DeepSeek client (default - cost effective)
deepseek_ai = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)

# Ark client (optional - for legacy or specific use cases)
ark_ai = OpenAI(
    api_key=ARK_API_KEY,
    base_url="https://ark.cn-beijing.volces.com/api/coding/v1",
)

# Backward compatibility: alias ai to deepseek_ai
ai = deepseek_ai


def get_ai_client(model: str = DEFAULT_MODEL):
    """Get the appropriate AI client based on the model."""
    if model.startswith("ark-") or model == "ark-code-latest":
        return ark_ai
    return deepseek_ai


def summarize(text: str, prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Send text to AI for summarization/processing."""
    client = get_ai_client(model)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()


def save_note(relative_path: str, content: str) -> Path:
    """Save a note to the vault. Creates parent directories as needed."""
    full_path = VAULT_PATH / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    print(f"Saved: {full_path}")
    return full_path


# Self-reflection and self-evolution tracking
try:
    from self_reflection import SystemBehaviorTracker
    # Global tracker instance
    TRACKER = SystemBehaviorTracker()
except ImportError as e:
    print(f"Warning: Self-reflection module not available: {e}")
    TRACKER = None

# Self-evolution configuration
LEARNING_RATE = 0.1
ADAPTATION_THRESHOLD = 0.8
MAX_EVOLUTION_ITERATIONS = 100
EVOLUTION_LOG_PATH = VAULT_PATH / "_logs" / "evolution_log.json"
LEARNING_LOG_PATH = VAULT_PATH / "_logs" / "learning_log.json"

# Bilibili configuration
BILIBILI_SESSDATA = os.getenv("BILIBILI_SESSDATA", "")
BILIBILI_USER_AGENT = os.getenv("BILIBILI_USER_AGENT",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
