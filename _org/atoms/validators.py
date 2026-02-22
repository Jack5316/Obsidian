"""Validators atom - Input validation utilities."""

from pathlib import Path
from typing import Optional


def validate_script_path(script_path: Path) -> bool:
    """Validate that a script exists and is a Python file."""
    if not script_path.exists():
        return False
    if not script_path.is_file():
        return False
    if script_path.suffix != ".py":
        return False
    return True


def validate_vault_path(vault_path: Path) -> bool:
    """Validate that a path is a valid Obsidian vault."""
    if not vault_path.exists():
        return False
    if not vault_path.is_dir():
        return False
    obsidian_dir = vault_path / ".obsidian"
    return obsidian_dir.exists()


def validate_script_name(script_name: str, scripts_dir: Path) -> Optional[Path]:
    """Validate a script name and return its full path if valid."""
    script_path = scripts_dir / script_name
    if validate_script_path(script_path):
        return script_path
    return None
