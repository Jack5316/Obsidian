"""Daily workflow template - Runs daily automation tasks."""

from typing import List, Optional
from datetime import datetime

from ..atoms import VaultConfig, ExecutionLogger, ScriptRunner
from ..molecules import ScriptRegistry, ExecutionEngine
from ..organisms import ContentDigester, AnalysisTools, EnhancementTools


class DailyWorkflow:
    """Template for daily automation workflow."""

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

    def run(
        self,
        skip_digestion: bool = False,
        skip_analysis: bool = False,
        skip_enhancement: bool = False,
        skip_scripts: Optional[List[str]] = None,
    ):
        """
        Run the daily workflow.

        Args:
            skip_digestion: Skip content digestion phase
            skip_analysis: Skip analysis phase
            skip_enhancement: Skip enhancement phase
            skip_scripts: List of specific scripts to skip
        """
        print("\n" + "=" * 60)
        print("DAILY WORKFLOW")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        all_results = []
        skipped_list = skip_scripts or []

        # Phase 1: Content Digestion
        if not skip_digestion:
            digestion_results = self.content_digester.run_all_digesters(
                skip=skipped_list
            )
            all_results.extend(digestion_results)
        else:
            print("\nSkipping content digestion phase")

        # Phase 2: Analysis (lightweight daily analysis)
        if not skip_analysis:
            reflection_results = self.analysis_tools.run_reflection_only(
                skip=skipped_list
            )
            all_results.extend(reflection_results)
        else:
            print("\nSkipping analysis phase")

        # Phase 3: Enhancement
        if not skip_enhancement:
            enhancement_results = self.enhancement_tools.run_insight_enhancement(
                skip=skipped_list
            )
            all_results.extend(enhancement_results)
        else:
            print("\nSkipping enhancement phase")

        # Final summary
        print("\n" + "=" * 60)
        print("DAILY WORKFLOW COMPLETE")
        print("=" * 60)
        self.logger.print_summary(all_results, skipped_list)

        # Save log
        log_file = self.logger.save_session_log(all_results, skipped_list)
        print(f"\nLog saved to: {log_file}")

        return all_results

    def run_quick(self, skip_scripts: Optional[List[str]] = None):
        """Run quick daily workflow (only news digestion)."""
        print("\n" + "=" * 60)
        print("QUICK DAILY WORKFLOW")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        skipped_list = skip_scripts or []
        results = self.content_digester.run_news_only(skip=skipped_list)

        print("\n" + "=" * 60)
        print("QUICK WORKFLOW COMPLETE")
        print("=" * 60)
        self.logger.print_summary(results, skipped_list)

        log_file = self.logger.save_session_log(results, skipped_list)
        print(f"\nLog saved to: {log_file}")

        return results
