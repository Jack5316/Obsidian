"""Enhancement tools organism - Handles note enhancement scripts."""

from typing import List, Optional
from ..molecules import ScriptRegistry, ScriptInfo, ExecutionEngine
from ..atoms import VaultConfig
from ..molecules.script_registry import ScriptCategory


class EnhancementTools:
    """Organism for note enhancement workflows."""

    def __init__(
        self,
        config: VaultConfig,
        registry: ScriptRegistry,
        engine: ExecutionEngine,
    ):
        self.config = config
        self.registry = registry
        self.engine = engine

    def get_enhancement_scripts(self) -> List[ScriptInfo]:
        """Get all enhancement scripts."""
        return self.registry.list_scripts(
            category=ScriptCategory.ENHANCEMENT,
            recommended_only=True,
        )

    def run_all_enhancements(
        self,
        skip: Optional[List[str]] = None,
    ):
        """Run all enhancement scripts."""
        scripts = self.get_enhancement_scripts()
        print(f"\n{'=' * 60}")
        print(f"ENHANCEMENT WORKFLOW")
        print(f"Running {len(scripts)} enhancement scripts")
        print(f"{'=' * 60}")

        results = self.engine.execute_scripts(scripts, skip=skip)
        return results

    def run_insight_enhancement(
        self,
        skip: Optional[List[str]] = None,
    ):
        """Run insight enhancement only."""
        insight_scripts = [
            s
            for s in self.get_enhancement_scripts()
            if "insights" in s.tags or "ai" in s.tags
        ]
        print(f"\n{'=' * 60}")
        print(f"INSIGHT ENHANCEMENT WORKFLOW")
        print(f"Running {len(insight_scripts)} insight scripts")
        print(f"{'=' * 60}")

        results = self.engine.execute_scripts(insight_scripts, skip=skip)
        return results
