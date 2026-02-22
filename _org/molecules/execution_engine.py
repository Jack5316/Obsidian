"""Execution engine molecule - Orchestrates script execution."""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Callable

from ..atoms import VaultConfig, ExecutionLogger, ScriptRunner
from ..atoms.logger import ScriptResult
from .script_registry import ScriptRegistry, ScriptInfo


class ExecutionEngine:
    """Orchestrates the execution of multiple scripts."""

    def __init__(
        self,
        config: VaultConfig,
        registry: ScriptRegistry,
        logger: ExecutionLogger,
        runner: ScriptRunner,
    ):
        self.config = config
        self.registry = registry
        self.logger = logger
        self.runner = runner
        self._on_script_start: Optional[Callable[[ScriptInfo], None]] = None
        self._on_script_complete: Optional[
            Callable[[ScriptInfo, ScriptResult], None]
        ] = None

    def on_script_start(self, callback: Callable[[ScriptInfo], None]) -> None:
        """Set callback for when a script starts."""
        self._on_script_start = callback

    def on_script_complete(
        self, callback: Callable[[ScriptInfo, ScriptResult], None]
    ) -> None:
        """Set callback for when a script completes."""
        self._on_script_complete = callback

    def execute_scripts(
        self,
        scripts: List[ScriptInfo],
        skip: Optional[List[str]] = None,
    ) -> List[ScriptResult]:
        """
        Execute a list of scripts.

        Args:
            scripts: List of scripts to execute
            skip: Optional list of script names to skip

        Returns:
            List of execution results
        """
        skip_set = set(skip) if skip else set()
        results: List[ScriptResult] = []

        for script_info in scripts:
            if script_info.name in skip_set:
                print(f"\n=== Skipping {script_info.name} ===")
                continue

            if self._on_script_start:
                self._on_script_start(script_info)

            result = self._execute_single(script_info)
            results.append(result)

            if self._on_script_complete:
                self._on_script_complete(script_info, result)

        return results

    def _execute_single(self, script_info: ScriptInfo) -> ScriptResult:
        """Execute a single script and return the result."""
        script_path = self.config.get_script_path(script_info.name)
        start_time = datetime.now()

        print(f"\n{'=' * 60}")
        print(f"Running: {script_info.name}")
        print(f"Description: {script_info.description}")
        print(f"{'=' * 60}")

        success, stdout, stderr, exit_code, duration = self.runner.run(
            script_path,
            description=script_info.description,
        )

        end_time = datetime.now()

        result = self.logger.create_script_result(
            script_name=script_info.name,
            description=script_info.description,
            start_time=start_time,
            end_time=end_time,
            success=success,
            output=stdout,
            error=stderr,
            exit_code=exit_code,
        )

        if success:
            print(f"\n✓ Success ({duration:.2f}s)")
            if stdout:
                print("\nOutput:")
                print(stdout.strip())
        else:
            print(f"\n✗ Failed ({duration:.2f}s)")
            if stderr:
                print("\nError:")
                print(stderr.strip())

        return result
