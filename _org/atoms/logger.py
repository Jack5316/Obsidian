"""Execution logger atom - Handles logging and result tracking."""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


@dataclass
class ScriptResult:
    """Result of a single script execution."""

    script_name: str
    description: str
    start_time: str
    end_time: str
    duration: float
    success: bool
    output: str = ""
    error: str = ""
    exit_code: Optional[int] = None


@dataclass
class ExecutionSummary:
    """Summary of an entire execution session."""

    session_id: str
    start_time: str
    end_time: str
    total_duration: float
    total_scripts: int
    skipped_scripts: int
    successful_scripts: int
    failed_scripts: int
    results: List[ScriptResult]
    metadata: Dict[str, Any]


class ExecutionLogger:
    """Logger for tracking script execution results."""

    def __init__(self, logs_dir: Path):
        self.logs_dir = logs_dir
        self.logs_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def create_script_result(
        self,
        script_name: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        success: bool,
        output: str = "",
        error: str = "",
        exit_code: Optional[int] = None,
    ) -> ScriptResult:
        """Create a script result object."""
        duration = (end_time - start_time).total_seconds()
        return ScriptResult(
            script_name=script_name,
            description=description,
            start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            duration=duration,
            success=success,
            output=output,
            error=error,
            exit_code=exit_code,
        )

    def save_session_log(
        self,
        results: List[ScriptResult],
        skipped: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Save complete session log to file."""
        start_time = datetime.now()
        if results:
            start_time = datetime.strptime(results[0].start_time, "%Y-%m-%d %H:%M:%S")

        end_time = datetime.now()
        if results:
            end_time = datetime.strptime(results[-1].end_time, "%Y-%m-%d %H:%M:%S")

        total_duration = sum(r.duration for r in results)

        summary = ExecutionSummary(
            session_id=self.session_id,
            start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            total_duration=total_duration,
            total_scripts=len(results) + len(skipped),
            skipped_scripts=len(skipped),
            successful_scripts=sum(1 for r in results if r.success),
            failed_scripts=sum(1 for r in results if not r.success),
            results=results,
            metadata=metadata or {},
        )

        log_file = self.logs_dir / f"org_session_{self.session_id}.log"

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(asdict(summary), f, indent=2, ensure_ascii=False)

        return log_file

    def print_summary(self, results: List[ScriptResult], skipped: List[str]) -> None:
        """Print execution summary to console."""
        print("\n" + "=" * 60)
        print("EXECUTION SUMMARY")
        print("=" * 60)

        total = len(results) + len(skipped)
        successful = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        total_duration = sum(r.duration for r in results)

        print(f"\nTotal scripts:    {total}")
        print(f"Skipped:          {len(skipped)}")
        print(f"Ran:              {len(results)}")
        print(f"Successful:       {successful}")
        print(f"Failed:           {failed}")
        print(f"Total duration:   {total_duration:.2f}s")

        if results:
            print("\nDetails:")
            print("-" * 40)
            for result in results:
                status = "✓" if result.success else "✗"
                print(f"{status} {result.script_name:<25} {result.duration:6.2f}s")
                if not result.success and result.error:
                    print(f"  Error: {result.error[:100]}...")
