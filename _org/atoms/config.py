"""Vault configuration atom - Manages environment and paths."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv


@dataclass
class VaultConfig:
    """Configuration for the AI Vault automation system."""

    vault_root: Path = field(init=False)
    scripts_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    sources_dir: Path = field(init=False)

    # API credentials
    ark_api_key: str = field(init=False)
    bearblog_user: Optional[str] = field(init=False)
    bearblog_password: Optional[str] = field(init=False)

    # AI configuration
    default_model: str = "ark-code-latest"
    ai_base_url: str = "https://ark.cn-beijing.volces.com/api/coding/v1"

    def __post_init__(self):
        """Initialize paths and load environment variables."""
        self.vault_root = Path(__file__).resolve().parent.parent.parent
        self.scripts_dir = self.vault_root / "_scripts"
        self.logs_dir = self.vault_root / "_logs"
        self.sources_dir = self.vault_root / "Sources"

        # Load environment
        load_dotenv(self.vault_root / ".env")

        self.ark_api_key = os.getenv("ARK_API_KEY", "")
        self.bearblog_user = os.getenv("BEARBLOG_USER")
        self.bearblog_password = os.getenv("BEARBLOG_PASSWORD")

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.sources_dir.mkdir(exist_ok=True)

    def get_script_path(self, script_name: str) -> Path:
        """Get full path to a script."""
        return self.scripts_dir / script_name

    def get_log_path(self, log_name: str) -> Path:
        """Get full path to a log file."""
        return self.logs_dir / log_name
