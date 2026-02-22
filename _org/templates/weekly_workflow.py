"""Weekly workflow template - Runs weekly automation tasks."""

from typing import List, Optional
from datetime import datetime

from ..atoms import VaultConfig, ExecutionLogger, ScriptRunner
from ..molecules import ScriptRegistry, ExecutionEngine
from ..organisms import ContentDigester, AnalysisTools, EnhancementTools


class WeeklyWorkflow:
    """Template for weekly automation workflow."""

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
        Run the weekly workflow.

        Args:
            skip_digestion: Skip content digestion phase
            skip_analysis: Skip analysis phase
            skip_enhancement: Skip enhancement phase
            skip_scripts: List of specific scripts to skip
        """
        print("\n" + "=" * 60)
        print("WEEKLY WORKFLOW")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        all_results = []
        skipped_list = skip_scripts or []

        # Phase 1: Content Digestion (full)
        if not skip_digestion:
            digestion_results = self.content_digester.run_all_digesters(
                skip=skipped_list
            )
            all_results.extend(digestion_results)
        else:
            print("\nSkipping content digestion phase")

        # Phase 2: Full Analysis
        if not skip_analysis:
            analysis_results = self.analysis_tools.run_all_analysis(skip=skipped_list)
            all_results.extend(analysis_results)
        else:
            print("\nSkipping analysis phase")

        # Phase 3: Full Enhancement
        if not skip_enhancement:
            enhancement_results = self.enhancement_tools.run_all_enhancements(
                skip=skipped_list
            )
            all_results.extend(enhancement_results)
        else:
            print("\nSkipping enhancement phase")

        # Final summary
        print("\n" + "=" * 60)
        print("WEEKLY WORKFLOW COMPLETE")
        print("=" * 60)
        self.logger.print_summary(all_results, skipped_list)

        # Save log
        log_file = self.logger.save_session_log(
            all_results,
            skipped_list,
            metadata={"workflow_type": "weekly"},
        )
        print(f"\nLog saved to: {log_file}")

        return all_results

    def run_synthesis_only(self, skip_scripts: Optional[List[str]] = None):
        """Run only the weekly synthesis part."""
        print("\n" + "=" * 60)
        print("WEEKLY SYNTHESIS ONLY")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        skipped_list = skip_scripts or []
        results = self.analysis_tools.run_weekly_synthesis(skip=skipped_list)

        print("\n" + "=" * 60)
        print("SYNTHESIS COMPLETE")
        print("=" * 60)
        self.logger.print_summary(results, skipped_list)

        log_file = self.logger.save_session_log(
            results,
            skipped_list,
            metadata={"workflow_type": "weekly_synthesis"},
        )
        print(f"\nLog saved to: {log_file}")

        return results
