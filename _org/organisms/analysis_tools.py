"""Analysis tools organism - Handles analysis and reflection scripts."""

from typing import List, Optional
from ..molecules import ScriptRegistry, ScriptInfo, ExecutionEngine
from ..atoms import VaultConfig
from ..molecules.script_registry import ScriptCategory


class AnalysisTools:
    """Organism for analysis and reflection workflows."""

    def __init__(
        self,
        config: VaultConfig,
        registry: ScriptRegistry,
        engine: ExecutionEngine,
    ):
        self.config = config
        self.registry = registry
        self.engine = engine

    def get_analysis_scripts(self) -> List[ScriptInfo]:
        """Get all analysis scripts."""
        return self.registry.list_scripts(
            category=ScriptCategory.ANALYSIS,
            recommended_only=True,
        )

    def run_all_analysis(
        self,
        skip: Optional[List[str]] = None,
    ):
        """Run all analysis scripts."""
        scripts = self.get_analysis_scripts()
        print(f"\n{'=' * 60}")
        print(f"ANALYSIS WORKFLOW")
        print(f"Running {len(scripts)} analysis scripts")
        print(f"{'=' * 60}")

        results = self.engine.execute_scripts(scripts, skip=skip)
        return results

    def run_reflection_only(
        self,
        skip: Optional[List[str]] = None,
    ):
        """Run only reflection-related scripts."""
        reflection_scripts = [
            s
            for s in self.get_analysis_scripts()
            if "reflection" in s.tags or "introspection" in s.tags
        ]
        print(f"\n{'=' * 60}")
        print(f"REFLECTION WORKFLOW")
        print(f"Running {len(reflection_scripts)} reflection scripts")
        print(f"{'=' * 60}")

        results = self.engine.execute_scripts(reflection_scripts, skip=skip)
        return results

    def run_evolution_only(
        self,
        skip: Optional[List[str]] = None,
    ):
        """Run only evolution-related scripts."""
        evolution_scripts = [
            s
            for s in self.get_analysis_scripts()
            if "evolution" in s.tags or "improvement" in s.tags
        ]
        print(f"\n{'=' * 60}")
        print(f"EVOLUTION WORKFLOW")
        print(f"Running {len(evolution_scripts)} evolution scripts")
        print(f"{'=' * 60}")

        results = self.engine.execute_scripts(evolution_scripts, skip=skip)
        return results

    def run_weekly_synthesis(
        self,
        skip: Optional[List[str]] = None,
    ):
        """Run weekly synthesis workflow."""
        synthesis_scripts = [
            s
            for s in self.get_analysis_scripts()
            if "weekly" in s.tags or "synthesis" in s.tags
        ]
        print(f"\n{'=' * 60}")
        print(f"WEEKLY SYNTHESIS WORKFLOW")
        print(f"Running {len(synthesis_scripts)} synthesis scripts")
        print(f"{'=' * 60}")

        results = self.engine.execute_scripts(synthesis_scripts, skip=skip)
        return results
