"""Custom workflow template - Build custom workflows."""

from typing import List, Optional, Callable
from datetime import datetime

from ..atoms import VaultConfig, ExecutionLogger, ScriptRunner
from ..molecules import ScriptRegistry, ExecutionEngine, ScriptInfo
from ..organisms import ContentDigester, AnalysisTools, EnhancementTools


class CustomWorkflow:
    """Template for building custom automation workflows."""

    def __init__(self):
        self.config = VaultConfig()
        self.registry = ScriptRegistry(self.config.scripts_dir)
        self.logger = ExecutionLogger(self.config.logs_dir)
        self.runner = ScriptRunner(self.config.vault_root)
        self.engine = ExecutionEngine(
            self.config, self.registry, self.logger, self.runner
        )

        self.content_digester = ContentDigester(self.config, self.registry, self.engine)
        self.analysis_tools = AnalysisTools(self.config, self.registry, self.engine)
        self.enhancement_tools = EnhancementTools(
            self.config, self.registry, self.engine
        )

        self._phases: List[dict] = []

    def add_phase(
        self,
        name: str,
        scripts: List[ScriptInfo],
        skip: Optional[List[str]] = None,
        before: Optional[Callable] = None,
        after: Optional[Callable] = None,
    ):
        """
        Add a phase to the custom workflow.

        Args:
            name: Name of the phase
            scripts: List of scripts to run in this phase
            skip: Optional scripts to skip in this phase
            before: Optional callback to run before phase
            after: Optional callback to run after phase
        """
        self._phases.append(
            {
                "name": name,
                "scripts": scripts,
                "skip": skip or [],
                "before": before,
                "after": after,
            }
        )

    def add_phase_by_category(
        self,
        name: str,
        category: str,
        skip: Optional[List[str]] = None,
        before: Optional[Callable] = None,
        after: Optional[Callable] = None,
    ):
        """Add a phase with scripts from a specific category."""
        from ..molecules.script_registry import ScriptCategory

        cat = ScriptCategory(category)
        scripts = self.registry.list_scripts(category=cat, recommended_only=True)
        self.add_phase(name, scripts, skip, before, after)

    def add_phase_by_tags(
        self,
        name: str,
        tags: List[str],
        skip: Optional[List[str]] = None,
        before: Optional[Callable] = None,
        after: Optional[Callable] = None,
    ):
        """Add a phase with scripts matching specific tags."""
        all_scripts = self.registry.list_scripts(recommended_only=True)
        matching_scripts = [
            s for s in all_scripts if any(tag in s.tags for tag in tags)
        ]
        self.add_phase(name, matching_scripts, skip, before, after)

    def run(
        self,
        workflow_name: str = "Custom Workflow",
        skip_scripts: Optional[List[str]] = None,
    ):
        """
        Run the custom workflow.

        Args:
            workflow_name: Name for this workflow execution
            skip_scripts: Additional scripts to skip across all phases
        """
        print("\n" + "=" * 60)
        print(workflow_name.upper())
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Phases: {len(self._phases)}")
        print("=" * 60)

        all_results = []
        global_skip = skip_scripts or []

        for i, phase in enumerate(self._phases, 1):
            phase_name = phase["name"]
            phase_scripts = phase["scripts"]
            phase_skip = phase["skip"] + global_skip

            print(f"\n--- Phase {i}/{len(self._phases)}: {phase_name} ---")

            if phase["before"]:
                phase["before"]()

            phase_results = self.engine.execute_scripts(phase_scripts, skip=phase_skip)
            all_results.extend(phase_results)

            if phase["after"]:
                phase["after"]()

        # Final summary
        print("\n" + "=" * 60)
        print(f"{workflow_name} COMPLETE")
        print("=" * 60)
        self.logger.print_summary(all_results, global_skip)

        # Save log
        log_file = self.logger.save_session_log(
            all_results,
            global_skip,
            metadata={"workflow_type": "custom", "workflow_name": workflow_name},
        )
        print(f"\nLog saved to: {log_file}")

        return all_results
