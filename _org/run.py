#!/usr/bin/env python3
"""
AI Vault Automation - Main Runner
==================================

Convenient entry point for the atomic design automation system.

Usage:
  python _org/run.py daily          - Run daily workflow
  python _org/run.py weekly         - Run weekly workflow
  python _org/run.py list           - List available scripts
  python _org/run.py help           - Show help
"""

import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _org.pages.cli import main

if __name__ == "__main__":
    sys.exit(main())
