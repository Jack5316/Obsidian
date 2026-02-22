"""Script runner atom - Executes individual scripts."""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional


class ScriptRunner:
    """Executes Python scripts and captures output."""

    def __init__(self, vault_root: Path):
        self.vault_root = vault_root

    def run(
        self,
        script_path: Path,
        description: str = "",
        args: Optional[list] = None,
    ) -> Tuple[bool, str, str, int, float]:
        """
        Run a script and return results.

        Returns: (success, stdout, stderr, exit_code, duration_seconds)
        """
        start_time = datetime.now()

        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.vault_root),
                timeout=300,
            )

            duration = (datetime.now() - start_time).total_seconds()

            return (
                result.returncode == 0,
                result.stdout,
                result.stderr,
                result.returncode,
                duration,
            )

        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            return False, "", "Script timed out after 300 seconds", -1, duration

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return False, "", str(e), -1, duration
