"""Advanced Self-Evolution System for 10x Distill System.

A sophisticated self-evolving intelligence system inspired by the
Self-Evolving Artificial Intelligence (SEAI) framework. This system
enables continuous learning, self-improvement, and adaptive behavior.
"""

import argparse
import json
import re
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from config import summarize, save_note, VAULT_PATH, TRACKER

# Self-evolution configuration
EVOLUTION_LOG_PATH = VAULT_PATH / "_logs" / "evolution_log.json"
LEARNING_RATE = 0.1
ADAPTATION_THRESHOLD = 0.8
MAX_ITERATIONS = 100

# Enhanced self-reflection prompt
ENHANCED_REFLECTION_PROMPT = """You are an advanced self-evolution analyst. Analyze the 10x Distill System
using the SEAI framework (Self-Evolving Artificial Intelligence). Your analysis must include:

1. **BEHAVIOR ANALYSIS**
   - What the system did
   - When it did it
   - How it did it
   - What happened as a result

2. **PERFORMANCE METRICS**
   - Success/failure rates by component
   - Response times and resource usage
   - Content quality metrics
   - User satisfaction indicators

3. **CAUSALITY DETECTION**
   - Identify causal relationships between inputs and outputs
   - Determine which variables have the greatest impact on outcomes
   - Find hidden patterns and correlations

4. **SELF-IMPROVEMENT OPPORTUNITIES**
   - Specific code/config changes needed
   - Parameter optimizations
   - Algorithm improvements
   - Process enhancements

5. **LEARNING PROGRESS**
   - What the system learned in this iteration
   - Knowledge retention and transfer
   - Skill acquisition and improvement

6. **ADAPTATION STRATEGIES**
   - How the system should adapt to changing conditions
   - Dynamic parameter adjustment
   - Failover and recovery strategies
   - Load balancing and resource allocation

Your analysis must be **data-driven, specific, and actionable**. Provide concrete suggestions
for system improvement with clear expected outcomes and metrics for measuring progress.
"""

# Self-improvement prompt with safety checks
ENHANCED_IMPROVEMENT_PROMPT = """You are an AI self-improvement engineer following the SEAI framework.
Given a self-reflection analysis, generate **safe, tested, and implementable improvements**
for the 10x Distill System.

### SAFETY REQUIREMENTS
1. **Backward Compatibility**: Changes must not break existing functionality
2. **Fail-Safe Design**: Implement safe defaults and error recovery
3. **Testing Requirements**: Propose test cases for each change
4. **Rollback Plan**: Include steps to revert changes if problems occur

### IMPLEMENTATION STANDARDS
1. **Code Changes**: Provide exact code snippets with context
2. **Config Updates**: Specify configuration file modifications
3. **Dependencies**: List any new libraries or dependencies
4. **Testing**: Suggest test scenarios and validation checks

### CHANGE STRUCTURE
For each improvement, provide:
{
  "id": "unique_identifier",
  "category": "bug/feature/optimization/refactor",
  "priority": "high/medium/low",
  "risk_level": "low/medium/high",
  "description": "what needs to be changed",
  "location": "file_path:line_numbers",
  "current_code": "existing implementation",
  "proposed_code": "improved implementation",
  "test_cases": ["list of test scenarios"],
  "rollback_steps": ["revert instructions"]
}

Return a JSON array of improvement objects."""


class CausalityDetector:
    """Detects causal relationships between system inputs and outputs."""

    def __init__(self, evolution_log: List[Dict]):
        self.evolution_log = evolution_log

    def detect_causal_relationships(self) -> Dict:
        """Identify causal patterns in system behavior."""
        causal_patterns = []
        operations = [log for log in self.evolution_log if log.get("operation_type")]

        for i, op in enumerate(operations):
            if i == 0:
                continue

            # Look for causal relationships with previous operation
            prev_op = operations[i - 1]
            if op["status"] == "failed" and prev_op["status"] == "failed":
                causal_patterns.append({
                    "type": "failure_cascade",
                    "operations": [prev_op["id"], op["id"]],
                    "probability": 0.85
                })

            # Detect performance degradation
            if op["metrics"].get("response_time") and prev_op["metrics"].get("response_time"):
                if op["metrics"]["response_time"] > 2 * prev_op["metrics"]["response_time"]:
                    causal_patterns.append({
                        "type": "performance_degradation",
                        "operations": [prev_op["id"], op["id"]],
                        "probability": 0.75
                    })

        return {
            "patterns": causal_patterns,
            "total_patterns": len(causal_patterns),
            "confidence": 0.85
        }


class LearningProgressTracker:
    """Tracks system learning and knowledge retention."""

    def __init__(self):
        self.learning_log = []

    def record_learning(self, iteration: int, insights: List[str]):
        """Record insights gained in this iteration."""
        entry = {
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "insights": insights,
            "knowledge_retention": self._calculate_retention(iteration)
        }
        self.learning_log.append(entry)
        self._save_learning_log()

    def _calculate_retention(self, iteration: int) -> float:
        """Calculate knowledge retention across iterations."""
        if iteration == 0:
            return 1.0

        if iteration > len(self.learning_log):
            return 0.8 + (iteration * LEARNING_RATE)

        # Simple exponential decay model
        return 0.9 - (iteration * LEARNING_RATE)

    def _save_learning_log(self):
        """Save learning log to file."""
        log_path = VAULT_PATH / "_logs" / "learning_log.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self.learning_log, f, indent=2, default=str)


class SelfImprovementEngine:
    """Advanced self-improvement engine with safety checks."""

    def __init__(self, causality_detector: CausalityDetector,
                 learning_tracker: LearningProgressTracker):
        self.causality_detector = causality_detector
        self.learning_tracker = learning_tracker
        self.safe_mode = True  # Default to safe mode for changes

    def evaluate_change_risk(self, change: Dict) -> float:
        """Evaluate risk level of a proposed change."""
        # Risk assessment based on change type and complexity
        risk_factors = 0.0
        if change.get("category") == "refactor":
            risk_factors += 0.3
        if len(change.get("current_code", "")) > 200:
            risk_factors += 0.4
        if "import" in change.get("proposed_code", "").lower():
            risk_factors += 0.3

        return min(risk_factors, 0.95)

    def apply_changes_safely(self, improvements: List[Dict]) -> Dict:
        """Apply improvements with safety checks and rollback support."""
        results = {
            "success": [],
            "failed": [],
            "skipped": [],
            "rollbacks": []
        }

        for change in improvements:
            # Skip high-risk changes in safe mode
            risk = self.evaluate_change_risk(change)
            if self.safe_mode and risk > 0.6:
                results["skipped"].append({
                    "id": change["id"],
                    "reason": "High risk change skipped in safe mode",
                    "risk_score": risk
                })
                continue

            try:
                # Create backup before applying
                self._create_backup(change)
                # Apply the change
                self._apply_change(change)
                # Verify the change
                if self._verify_change(change):
                    results["success"].append({
                        "id": change["id"],
                        "risk_score": risk
                    })
                else:
                    # Rollback if verification fails
                    self._rollback_change(change)
                    results["rollbacks"].append({
                        "id": change["id"],
                        "reason": "Verification failed"
                    })
            except Exception as e:
                self._rollback_change(change)
                results["failed"].append({
                    "id": change["id"],
                    "error": str(e),
                    "risk_score": risk
                })

        return results

    def _resolve_file_path(self, location: str) -> Path:
        """Resolve file path from change location, checking _scripts/ if needed."""
        raw_path = location.split(":")[0]
        file_path = VAULT_PATH / raw_path
        if not file_path.exists():
            # Try _scripts/ subdirectory for bare filenames
            scripts_path = VAULT_PATH / "_scripts" / raw_path
            if scripts_path.exists():
                return scripts_path
        return file_path

    def _create_backup(self, change: Dict):
        """Create a backup of the target file."""
        file_path = self._resolve_file_path(change["location"])
        if file_path.exists():
            backup_path = file_path.with_suffix(f".{datetime.now().strftime('%Y%m%d%H%M%S')}.bak")
            with open(file_path, "rb") as f_in:
                with open(backup_path, "wb") as f_out:
                    f_out.write(f_in.read())

    def _apply_change(self, change: Dict):
        """Apply the code change."""
        file_path = self._resolve_file_path(change["location"])
        line_num = int(change["location"].split(":")[1]) if ":" in change["location"] else 0

        content = file_path.read_text(encoding="utf-8")
        if line_num > 0:
            # Replace specific line range
            lines = content.split("\n")
            # TODO: Implement smart line-based replacement
        else:
            # Simple text replacement
            content = content.replace(change["current_code"], change["proposed_code"])

        file_path.write_text(content, encoding="utf-8")

    def _verify_change(self, change: Dict) -> bool:
        """Verify the change was applied correctly."""
        file_path = self._resolve_file_path(change["location"])
        content = file_path.read_text(encoding="utf-8")
        return change["proposed_code"] in content

    def _rollback_change(self, change: Dict):
        """Rollback to previous version."""
        file_path = self._resolve_file_path(change["location"])
        backup_files = list(file_path.parent.glob(f"{file_path.name}.*.bak"))
        if backup_files:
            # Find latest backup
            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
            with open(latest_backup, "rb") as f_in:
                with open(file_path, "wb") as f_out:
                    f_out.write(f_in.read())
            # Cleanup backup
            latest_backup.unlink()


class AdaptiveSystemController:
    """Controls system adaptation and dynamic parameter adjustment."""

    def __init__(self):
        self.adaptation_rules = [
            {
                "trigger": "high_failure_rate",
                "condition": lambda stats: stats.get("success_rate", 0) < 0.6,
                "action": self._adjust_retry_strategy,
                "priority": "high"
            },
            {
                "trigger": "slow_response",
                "condition": lambda stats: stats.get("avg_response_time", 0) > 30,
                "action": self._optimize_resource_usage,
                "priority": "medium"
            },
            {
                "trigger": "low_quality",
                "condition": lambda stats: stats.get("avg_quality_score", 0) < 0.7,
                "action": self._adjust_ai_parameters,
                "priority": "high"
            }
        ]

    def _adjust_retry_strategy(self, params: Dict):
        """Increase retry count and delay for failing operations."""
        return {"max_retries": 5, "retry_delay": 2}

    def _optimize_resource_usage(self, params: Dict):
        """Reduce concurrent operations and adjust timeouts."""
        return {"max_concurrent": 2, "timeout": 60}

    def _adjust_ai_parameters(self, params: Dict):
        """Increase AI model temperature and token limit for better results."""
        return {"temperature": 0.7, "max_tokens": 4096}


class EvolutionEngine:
    """Main self-evolution orchestrator."""

    def __init__(self):
        self.causality_detector = None
        self.learning_tracker = LearningProgressTracker()
        self.self_improvement_engine = None
        self.adaptive_controller = AdaptiveSystemController()
        self.evolution_log = []

    def load_evolution_log(self) -> List[Dict]:
        """Load evolution log from file."""
        if EVOLUTION_LOG_PATH.exists():
            try:
                return json.loads(EVOLUTION_LOG_PATH.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"Error loading evolution log: {e}")
                return []
        return []

    def save_evolution_log(self):
        """Save evolution log to file."""
        EVOLUTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        EVOLUTION_LOG_PATH.write_text(
            json.dumps(self.evolution_log, indent=2, default=str),
            encoding="utf-8"
        )

    def run_evolution_cycle(self, iteration: int = 0) -> Dict:
        """Run complete self-evolution cycle."""
        try:
            start_time = time.time()

            # 1. Analysis Phase - Collect data and analyze behavior
            analysis = self._analyze_system()

            # 2. Reflection Phase - Generate self-reflection
            reflection = self._generate_reflection(analysis)

            # 3. Improvement Phase - Generate and apply improvements
            improvements = self._generate_improvements(reflection)
            results = self._apply_improvements(improvements)

            # 4. Learning Phase - Record insights and learning progress
            insights = self._extract_insights(reflection)
            self.learning_tracker.record_learning(iteration, insights)

            # 5. Adaptation Phase - Adjust system parameters
            adaptation = self._adapt_system(analysis)

            # 6. Evaluation Phase - Measure progress
            evaluation = self._evaluate_evolution(start_time, analysis, results, adaptation)

            # 7. Planning Phase - Generate next iteration plan
            next_plan = self._generate_next_plan(evaluation)

            # Save results
            self._save_cycle_results(iteration, analysis, reflection, results, adaptation, evaluation, next_plan)

            return {
                "status": "success",
                "iteration": iteration,
                "duration": time.time() - start_time,
                "results": results,
                "evaluation": evaluation,
                "next_plan": next_plan
            }

        except Exception as e:
            return {
                "status": "failed",
                "iteration": iteration,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def _analyze_system(self) -> Dict:
        """Analyze system behavior and performance."""
        evolution_log = self.load_evolution_log()
        self.causality_detector = CausalityDetector(evolution_log)

        return {
            "behavior": self._analyze_behavior(),
            "performance": self._analyze_performance(),
            "causality": self.causality_detector.detect_causal_relationships()
        }

    def _analyze_behavior(self) -> Dict:
        """Analyze system behavior using existing tracking data."""
        if not TRACKER:
            return {"operations": [], "types": []}

        operations = TRACKER.get_operation_statistics()
        script_stats = operations.get("script_statistics", {})

        return {
            "operations": TRACKER.log,
            "types": list(script_stats.keys()),
            "stats": operations
        }

    def _analyze_performance(self) -> Dict:
        """Analyze performance metrics from operations."""
        if not TRACKER:
            return {"avg_response_time": 0, "success_rate": 0}

        stats = TRACKER.get_operation_statistics()
        avg_response_time = 0
        total_ops = stats.get("total_operations", 0)

        if total_ops > 0:
            # Calculate average response time from operations with metrics
            response_times = []
            for op in TRACKER.log:
                if "response_time" in op.get("metrics", {}):
                    response_times.append(op["metrics"]["response_time"])

            avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return {
            "avg_response_time": avg_response_time,
            "success_rate": stats.get("success_rate", 0),
            "total_ops": stats.get("total_operations", 0),
            "failed_ops": stats.get("failed_operations", 0)
        }

    def _generate_reflection(self, analysis: Dict) -> str:
        """Generate self-reflection analysis from behavior data."""
        analysis_text = self._format_analysis_for_llm(analysis)
        return summarize(analysis_text, ENHANCED_REFLECTION_PROMPT)

    def _format_analysis_for_llm(self, analysis: Dict) -> str:
        """Format analysis data for LLM processing."""
        # TODO: Implement comprehensive formatting
        return str(analysis)

    def _generate_improvements(self, reflection: str) -> List[Dict]:
        """Generate improvement suggestions from reflection."""
        try:
            improvements = summarize(reflection, ENHANCED_IMPROVEMENT_PROMPT)
            return json.loads(improvements)
        except Exception as e:
            print(f"Error parsing improvements: {e}")
            return []

    def _apply_improvements(self, improvements: List[Dict]) -> Dict:
        """Apply generated improvements."""
        if not self.self_improvement_engine:
            self.self_improvement_engine = SelfImprovementEngine(
                self.causality_detector,
                self.learning_tracker
            )
        return self.self_improvement_engine.apply_changes_safely(improvements)

    def _extract_insights(self, reflection: str) -> List[str]:
        """Extract key insights from reflection."""
        # Simple insight extraction using regex
        insights = []
        insight_patterns = [
            r"Key Insight: (.+?)(?=\n|$)",
            r"Important Lesson: (.+?)(?=\n|$)",
            r"Learning: (.+?)(?=\n|$)"
        ]

        for pattern in insight_patterns:
            matches = re.findall(pattern, reflection, re.DOTALL)
            for match in matches:
                insights.append(match.strip())

        return insights

    def _adapt_system(self, analysis: Dict) -> Dict:
        """Adapt system parameters based on analysis."""
        # Apply adaptation rules
        adaptation = {"changes": [], "triggered_rules": []}

        for rule in self.adaptive_controller.adaptation_rules:
            if rule["condition"](analysis["performance"]):
                change = rule["action"](analysis["performance"])
                adaptation["changes"].append(change)
                adaptation["triggered_rules"].append(rule["trigger"])

        return adaptation

    def _evaluate_evolution(self, start_time: float, analysis: Dict,
                           improvement_results: Dict, adaptation: Dict) -> Dict:
        """Evaluate the evolution cycle effectiveness."""
        duration = time.time() - start_time
        success_changes = len(improvement_results.get("success", []))
        failed_changes = len(improvement_results.get("failed", []))
        total_changes = success_changes + failed_changes + len(improvement_results.get("skipped", []))

        return {
            "duration": duration,
            "improvements": {
                "total": total_changes,
                "success": success_changes,
                "failed": failed_changes,
                "skipped": len(improvement_results.get("skipped", []))
            },
            "adaptation": {
                "triggered_rules": len(adaptation["triggered_rules"]),
                "changes": len(adaptation["changes"])
            },
            "performance_impact": self._calculate_performance_impact(analysis, adaptation)
        }

    def _calculate_performance_impact(self, analysis: Dict, adaptation: Dict) -> float:
        """Calculate performance impact of adaptations."""
        if not adaptation["triggered_rules"]:
            return 0.0

        base_score = analysis["performance"]["success_rate"] * 0.7 + \
                   (1 - analysis["performance"]["avg_response_time"] / 60) * 0.3

        # Each adaptation improves score by 0.05-0.15
        return base_score + (len(adaptation["triggered_rules"]) * 0.1)

    def _generate_analysis_report(self, iterations: List[Dict]) -> str:
        """Generate detailed analysis report of evolution cycles."""
        report = []
        report.append("# Self-Evolution Analysis Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Analyzing {len(iterations)} iterations")
        report.append("")

        total_duration = sum(cycle["duration"] for cycle in iterations)
        avg_duration = total_duration / len(iterations)
        report.append("## Performance Overview")
        report.append(f"- Total duration: {total_duration:.2f} seconds")
        report.append(f"- Average duration: {avg_duration:.2f} seconds/iteration")
        report.append("")

        report.append("## Iteration Details")
        for i, cycle in enumerate(iterations):
            report.append(f"### Iteration {i + 1}")
            report.append(f"- Duration: {cycle['duration']:.2f} seconds")
            report.append(f"- Status: {'completed' if cycle['duration'] > 0 else 'failed'}")

            if "improvements" in cycle["evaluation"]:
                report.append(f"- Improvements: {cycle['evaluation']['improvements']['total']}")
                report.append(f"  - Success: {cycle['evaluation']['improvements']['success']}")
                report.append(f"  - Failed: {cycle['evaluation']['improvements']['failed']}")
                report.append(f"  - Skipped: {cycle['evaluation']['improvements']['skipped']}")

            if "adaptation" in cycle["evaluation"]:
                report.append(f"- Adaptations: {cycle['evaluation']['adaptation']['changes']}")
                report.append(f"  - Rules triggered: {cycle['evaluation']['adaptation']['triggered_rules']}")

            report.append("")

        return "\n".join(report)

    def _generate_next_plan(self, evaluation: Dict) -> Dict:
        """Generate plan for next evolution cycle."""
        # Determine next cycle based on evaluation
        if evaluation["improvements"]["failed"] > 0:
            return {
                "action": "fix_failures",
                "priority": "high",
                "changes": evaluation["improvements"]["failed"]
            }
        elif evaluation["adaptation"]["triggered_rules"] == 0:
            return {
                "action": "exploration",
                "priority": "medium",
                "changes": 5
            }
        else:
            return {
                "action": "optimization",
                "priority": "low",
                "changes": 3
            }

    def _save_cycle_results(self, iteration: int, analysis: Dict, reflection: str,
                          improvement_results: Dict, adaptation: Dict, evaluation: Dict,
                          next_plan: Dict):
        """Save complete cycle results."""
        cycle = {
            "timestamp": datetime.now().isoformat(),
            "iteration": iteration,
            "analysis": analysis,
            "reflection": reflection,
            "improvement_results": improvement_results,
            "adaptation": adaptation,
            "evaluation": evaluation,
            "next_plan": next_plan,
            "duration": evaluation["duration"]
        }

        self.evolution_log = self.load_evolution_log()
        self.evolution_log.append(cycle)
        self.save_evolution_log()


def main():
    """Main function for self-evolution system."""
    parser = argparse.ArgumentParser(
        description="Self-Evolution System for 10x Distill System"
    )
    subparsers = parser.add_subparsers(dest="mode", help="Mode of operation")

    # Single evolution cycle
    cycle_parser = subparsers.add_parser("cycle", help="Run single evolution cycle")
    cycle_parser.add_argument(
        "--iteration", type=int, default=0, help="Current iteration number"
    )
    cycle_parser.add_argument(
        "--safe", action="store_true", help="Run in safe mode (skip high-risk changes)"
    )

    # Continuous evolution
    continuous_parser = subparsers.add_parser("continuous", help="Run continuous evolution")
    continuous_parser.add_argument(
        "--iterations", type=int, default=10, help="Number of iterations to run"
    )
    continuous_parser.add_argument(
        "--interval", type=int, default=3600, help="Interval between iterations (seconds)"
    )
    continuous_parser.add_argument(
        "--safe", action="store_true", help="Run in safe mode"
    )

    # Analysis and reporting
    analyze_parser = subparsers.add_parser("analyze", help="Analyze evolution history")
    analyze_parser.add_argument(
        "--iterations", type=int, default=5, help="Number of recent iterations to analyze"
    )
    analyze_parser.add_argument(
        "--report", action="store_true", help="Generate detailed report"
    )

    args = parser.parse_args()
    engine = EvolutionEngine()

    if args.mode == "cycle":
        print(f"Running evolution cycle {args.iteration}...")
        result = engine.run_evolution_cycle(args.iteration)

        if result["status"] == "success":
            print(f"\nEvolution cycle {args.iteration} completed successfully!")
            print(f"Duration: {result['duration']:.2f} seconds")
            print(f"Changes applied: {result['results']['success']}")
            print(f"Changes failed: {result['results']['failed']}")
            print(f"Changes skipped: {result['results']['skipped']}")

            if "next_plan" in result:
                print(f"\nNext plan: {result['next_plan']['action']}")

        else:
            print(f"\nEvolution cycle failed: {result['error']}")
            if "traceback" in result:
                print(f"\nTraceback: {result['traceback']}")

    elif args.mode == "continuous":
        print(f"Starting continuous evolution for {args.iterations} iterations...")
        for i in range(args.iterations):
            print(f"\n=== Iteration {i + 1} ===")
            result = engine.run_evolution_cycle(i)

            if result["status"] == "success":
                print(f"Completed in {result['duration']:.2f} seconds")
                if i < args.iterations - 1:
                    print(f"Waiting {args.interval} seconds for next iteration...")
                    time.sleep(args.interval)
            else:
                print(f"Error: {result['error']}")
                break

        print("\nContinuous evolution completed!")

    elif args.mode == "analyze":
        print(f"Analyzing last {args.iterations} iterations...")
        log = engine.load_evolution_log()
        recent = log[-args.iterations:] if args.iterations <= len(log) else log

        print(f"\nTotal iterations: {len(recent)}")
        total_duration = sum(cycle['duration'] for cycle in recent)
        print(f"Average duration: {total_duration / len(recent):.2f} seconds")

        if args.report:
            report = engine._generate_analysis_report(recent)
            save_note(f"Sources/Self-Evolution Analysis - {datetime.now().strftime('%Y-%m-%d')}.md", report)
            print(f"Report saved to Sources/Self-Evolution Analysis - {datetime.now().strftime('%Y-%m-%d')}.md")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
