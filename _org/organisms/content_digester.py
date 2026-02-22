"""Content digester organism - Handles all content ingestion scripts."""

from typing import List, Optional
from ..molecules import ScriptRegistry, ScriptInfo, ExecutionEngine
from ..atoms import VaultConfig, ExecutionLogger, ScriptRunner
from ..molecules.script_registry import ScriptCategory


class ContentDigester:
    """Organism for content digestion workflows."""

    def __init__(
        self,
        config: VaultConfig,
        registry: ScriptRegistry,
        engine: ExecutionEngine,
    ):
        self.config = config
        self.registry = registry
        self.engine = engine

    def get_digestion_scripts(self) -> List[ScriptInfo]:
        """Get all content digestion scripts."""
        return self.registry.list_scripts(
            category=ScriptCategory.CONTENT_DIGEST,
            recommended_only=True,
        )

    def run_all_digesters(
        self,
        skip: Optional[List[str]] = None,
    ):
        """Run all recommended content digestion scripts."""
        scripts = self.get_digestion_scripts()
        print(f"\n{'=' * 60}")
        print(f"CONTENT DIGESTION WORKFLOW")
        print(f"Running {len(scripts)} digestion scripts")
        print(f"{'=' * 60}")

        results = self.engine.execute_scripts(scripts, skip=skip)
        return results

    def run_news_only(
        self,
        skip: Optional[List[str]] = None,
    ):
        """Run only news-related digestion scripts."""
        news_scripts = [
            s
            for s in self.get_digestion_scripts()
            if "news" in s.tags or "tweets" in s.tags
        ]
        print(f"\n{'=' * 60}")
        print(f"NEWS DIGESTION WORKFLOW")
        print(f"Running {len(news_scripts)} news scripts")
        print(f"{'=' * 60}")

        results = self.engine.execute_scripts(news_scripts, skip=skip)
        return results

    def run_research_only(
        self,
        skip: Optional[List[str]] = None,
    ):
        """Run only research-related digestion scripts."""
        research_scripts = [
            s
            for s in self.get_digestion_scripts()
            if "research" in s.tags or "papers" in s.tags
        ]
        print(f"\n{'=' * 60}")
        print(f"RESEARCH DIGESTION WORKFLOW")
        print(f"Running {len(research_scripts)} research scripts")
        print(f"{'=' * 60}")

        results = self.engine.execute_scripts(research_scripts, skip=skip)
        return results
