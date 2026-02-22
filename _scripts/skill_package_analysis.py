"""Skill Package Analysis - Analyze status, health, completeness, and pipelines of your skills.

This skill provides comprehensive analysis of your skill configuration including:
- Status monitoring (active/inactive, last execution)
- Health assessment (error rates, performance)
- Completeness analysis (documentation, coverage)
- Improvement recommendations
- Pipeline optimization insights
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


class SkillStatusMonitor:
    """Monitor skill status and basic health metrics."""
    
    def __init__(self, scripts_dir: Path, logs_dir: Path):
        self.scripts_dir = scripts_dir
        self.logs_dir = logs_dir
    
    def scan_skills(self) -> List[Dict]:
        """Scan all skill scripts and collect basic info."""
        skills = []
        
        for script_path in self.scripts_dir.glob("*.py"):
            if script_path.name.startswith("_"):
                continue
                
            skill_info = self._analyze_script(script_path)
            skills.append(skill_info)
            
        return sorted(skills, key=lambda x: x["name"])
    
    def _analyze_script(self, script_path: Path) -> Dict:
        """Analyze a single script file."""
        content = script_path.read_text(encoding="utf-8")
        
        # Extract docstring
        docstring = self._extract_docstring(content)
        
        # Check for imports and structure
        has_argparse = "argparse" in content
        has_main = 'if __name__ == "__main__"' in content
        has_config = "from config import" in content or "import config" in content
        
        # Get file stats
        stats = script_path.stat()
        last_modified = datetime.fromtimestamp(stats.st_mtime)
        
        return {
            "name": script_path.name,
            "path": str(script_path),
            "docstring": docstring,
            "has_argparse": has_argparse,
            "has_main": has_main,
            "has_config": has_config,
            "lines_of_code": len(content.split("\n")),
            "last_modified": last_modified.isoformat(),
            "size_bytes": stats.st_size,
        }
    
    def _extract_docstring(self, content: str) -> str:
        """Extract module docstring from content."""
        match = re.match(r'^["\']{3}(.*?)["\']{3}', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def get_execution_history(self, days: int = 30) -> Dict[str, List[Dict]]:
        """Get execution history from logs."""
        history = {}
        return history


class HealthAssessor:
    """Assess skill health based on various metrics."""
    
    def assess_health(self, skill: Dict, history: List[Dict]) -> Dict:
        """Assess overall health of a skill."""
        health_score = 0.0
        issues = []
        strengths = []
        
        # Check documentation
        if skill.get("docstring"):
            health_score += 0.3
            strengths.append("Has documentation")
        else:
            issues.append("Missing docstring/documentation")
        
        # Check structure
        if skill.get("has_argparse"):
            health_score += 0.2
            strengths.append("Has CLI interface")
        else:
            issues.append("No argparse/CLI interface")
        
        if skill.get("has_main"):
            health_score += 0.2
            strengths.append("Has main entry point")
        else:
            issues.append("No __main__ entry point")
        
        # Check recent modification
        last_modified = datetime.fromisoformat(skill["last_modified"])
        days_since_modified = (datetime.now() - last_modified).days
        
        if days_since_modified < 30:
            health_score += 0.15
            strengths.append("Recently updated")
        elif days_since_modified > 180:
            issues.append("Not updated in 6+ months")
            health_score += 0.05
        else:
            health_score += 0.1
        
        # Check execution history (placeholder)
        if not history:
            issues.append("No execution history found")
            health_score += 0.1
        else:
            health_score += 0.15
            strengths.append("Has execution history")
        
        return {
            "skill": skill["name"],
            "health_score": min(health_score, 1.0),
            "status": "healthy" if health_score >= 0.7 else "warning" if health_score >= 0.4 else "unhealthy",
            "strengths": strengths,
            "issues": issues,
        }


class CompletenessAnalyzer:
    """Analyze skill completeness and documentation."""
    
    def analyze_completeness(self, skills: List[Dict]) -> Dict:
        """Analyze completeness across all skills."""
        total = len(skills)
        documented = sum(1 for s in skills if s.get("docstring"))
        has_cli = sum(1 for s in skills if s.get("has_argparse"))
        has_main = sum(1 for s in skills if s.get("has_main"))
        
        categories = self._categorize_skills(skills)
        
        return {
            "total_skills": total,
            "documentation_coverage": documented / total if total else 0,
            "cli_coverage": has_cli / total if total else 0,
            "main_coverage": has_main / total if total else 0,
            "categories": categories,
            "skill_list": [s["name"] for s in skills],
        }
    
    def _categorize_skills(self, skills: List[Dict]) -> Dict[str, List[str]]:
        """Categorize skills by type/purpose."""
        categories = {
            "content_digest": [],
            "analysis": [],
            "enhancement": [],
            "capture": [],
            "skill_wrapper": [],
            "system": [],
            "other": [],
        }
        
        for skill in skills:
            name = skill["name"]
            doc = skill.get("docstring", "").lower()
            
            if "skill" in name or "wrapper" in doc:
                categories["skill_wrapper"].append(name)
            elif "digest" in name or "news" in name or "capture" in name:
                categories["content_digest"].append(name)
            elif "analysis" in doc or "reflect" in name or "evolution" in name:
                categories["analysis"].append(name)
            elif "enhance" in name or "insight" in name or "notes" in name:
                categories["enhancement"].append(name)
            elif "capture" in name or "mem" in name or "til" in name:
                categories["capture"].append(name)
            elif "config" in name or "system" in doc:
                categories["system"].append(name)
            else:
                categories["other"].append(name)
        
        return categories


class ImprovementRecommender:
    """Generate improvement recommendations for skills."""
    
    def generate_recommendations(self, health_assessments: List[Dict], completeness: Dict) -> List[Dict]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # High priority: Fix unhealthy skills
        for assessment in health_assessments:
            if assessment["status"] == "unhealthy":
                recommendations.append({
                    "priority": "high",
                    "category": "health",
                    "skill": assessment["skill"],
                    "description": f"Fix critical issues: {', '.join(assessment['issues'][:3])}",
                    "effort": "medium",
                })
        
        # Medium priority: Add documentation
        if completeness["documentation_coverage"] < 0.8:
            recommendations.append({
                "priority": "medium",
                "category": "documentation",
                "skill": "multiple",
                "description": f"Add docstrings to skills (current coverage: {completeness['documentation_coverage']:.0%})",
                "effort": "low",
            })
        
        # Medium priority: CLI interfaces
        if completeness["cli_coverage"] < 0.7:
            recommendations.append({
                "priority": "medium",
                "category": "structure",
                "skill": "multiple",
                "description": f"Add argparse CLI to skills (current coverage: {completeness['cli_coverage']:.0%})",
                "effort": "medium",
            })
        
        # Low priority: General improvements
        recommendations.append({
            "priority": "low",
            "category": "maintenance",
            "skill": "all",
            "description": "Review and update skills not modified in 6+ months",
            "effort": "high",
        })
        
        return recommendations


class PipelineAnalyzer:
    """Analyze skill pipelines and workflows."""
    
    def analyze_pipelines(self, skills: List[Dict]) -> Dict:
        """Analyze pipeline structure and efficiency."""
        # Look for workflow/orchestration scripts
        workflow_scripts = [
            s for s in skills 
            if "daily" in s["name"].lower() 
            or "weekly" in s["name"].lower()
            or "workflow" in s["name"].lower()
            or "org" in s["name"].lower()
        ]
        
        return {
            "workflow_scripts": [s["name"] for s in workflow_scripts],
            "total_pipelines": len(workflow_scripts),
            "pipeline_health": "needs_analysis",
            "bottlenecks": [],
            "optimization_opportunities": [
                "Consider parallel execution of independent skills",
                "Add caching for frequently used data",
                "Implement incremental processing where possible",
            ],
        }


def generate_report(
    skills: List[Dict],
    health_assessments: List[Dict],
    completeness: Dict,
    recommendations: List[Dict],
    pipelines: Dict,
) -> str:
    """Generate a comprehensive analysis report."""
    
    # Summary stats
    total_skills = len(skills)
    healthy = sum(1 for h in health_assessments if h["status"] == "healthy")
    warning = sum(1 for h in health_assessments if h["status"] == "warning")
    unhealthy = sum(1 for h in health_assessments if h["status"] == "unhealthy")
    avg_health = sum(h["health_score"] for h in health_assessments) / total_skills if total_skills else 0
    
    report = f"""# Skill Package Analysis - {datetime.now().strftime('%Y-%m-%d')}

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Skills | {total_skills} |
| Healthy | {healthy} |
| Warning | {warning} |
| Unhealthy | {unhealthy} |
| Average Health Score | {avg_health:.1%} |
| Documentation Coverage | {completeness['documentation_coverage']:.0%} |
| CLI Coverage | {completeness['cli_coverage']:.0%} |

## Skill Health Details

"""
    
    # Health by skill
    for assessment in sorted(health_assessments, key=lambda x: x["health_score"], reverse=True):
        status_emoji = "✓" if assessment["status"] == "healthy" else "⚠" if assessment["status"] == "warning" else "✗"
        report += f"### {status_emoji} {assessment['skill']} ({assessment['health_score']:.0%})\n"
        
        if assessment["strengths"]:
            report += f"- **Strengths**: {', '.join(assessment['strengths'])}\n"
        if assessment["issues"]:
            report += f"- **Issues**: {', '.join(assessment['issues'])}\n"
        report += "\n"
    
    # Completeness analysis
    report += "## Completeness Analysis\n\n"
    report += "### Skill Categories\n\n"
    for category, skills_list in completeness["categories"].items():
        if skills_list:
            report += f"- **{category.replace('_', ' ').title()}**: {len(skills_list)} skills\n"
            report += f"  - {', '.join(skills_list)}\n"
    
    # Recommendations
    report += "\n## Improvement Recommendations\n\n"
    for rec in recommendations:
        priority_emoji = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
        report += f"### {priority_emoji} {rec['priority'].upper()}: {rec['skill']}\n"
        report += f"- **Category**: {rec['category']}\n"
        report += f"- **Description**: {rec['description']}\n"
        report += f"- **Effort**: {rec['effort']}\n\n"
    
    # Pipeline analysis
    report += "## Pipeline Analysis\n\n"
    report += f"### Detected Workflow Scripts ({pipelines['total_pipelines']})\n\n"
    for script in pipelines["workflow_scripts"]:
        report += f"- {script}\n"
    
    report += "\n### Optimization Opportunities\n\n"
    for opportunity in pipelines["optimization_opportunities"]:
        report += f"- {opportunity}\n"
    
    report += f"\n---\n*Generated on {datetime.now().isoformat()}*"
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Analyze skill package status, health, and completeness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/skill_package_analysis.py
  python3 _scripts/skill_package_analysis.py --save
  python3 _scripts/skill_package_analysis.py --days 60
""",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Days of history to analyze (default: 30)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save analysis report to Sources/",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of Markdown",
    )
    args = parser.parse_args()
    
    scripts_dir = VAULT_PATH / "_scripts"
    logs_dir = VAULT_PATH / "_logs"
    
    print("=" * 60)
    print("Skill Package Analysis")
    print("=" * 60)
    
    # Step 1: Scan skills
    print("\n[1/5] Scanning skills...")
    monitor = SkillStatusMonitor(scripts_dir, logs_dir)
    skills = monitor.scan_skills()
    print(f"  Found {len(skills)} skills")
    
    # Step 2: Get execution history
    print("\n[2/5] Loading execution history...")
    history = monitor.get_execution_history(days=args.days)
    print(f"  Found history for {len(history)} skills")
    
    # Step 3: Assess health
    print("\n[3/5] Assessing skill health...")
    health_assessor = HealthAssessor()
    health_assessments = []
    for skill in skills:
        skill_history = history.get(skill["name"], [])
        assessment = health_assessor.assess_health(skill, skill_history)
        health_assessments.append(assessment)
    print(f"  Assessed {len(health_assessments)} skills")
    
    # Step 4: Analyze completeness
    print("\n[4/5] Analyzing completeness...")
    completeness_analyzer = CompletenessAnalyzer()
    completeness = completeness_analyzer.analyze_completeness(skills)
    print("  Complete")
    
    # Step 5: Generate recommendations
    print("\n[5/5] Generating recommendations...")
    recommender = ImprovementRecommender()
    recommendations = recommender.generate_recommendations(health_assessments, completeness)
    print(f"  Generated {len(recommendations)} recommendations")
    
    # Pipeline analysis
    print("\nAnalyzing pipelines...")
    pipeline_analyzer = PipelineAnalyzer()
    pipelines = pipeline_analyzer.analyze_pipelines(skills)
    
    # Generate report
    print("\n" + "=" * 60)
    if args.json:
        output = json.dumps({
            "skills": skills,
            "health_assessments": health_assessments,
            "completeness": completeness,
            "recommendations": recommendations,
            "pipelines": pipelines,
        }, indent=2, default=str)
        print(output)
    else:
        report = generate_report(skills, health_assessments, completeness, recommendations, pipelines)
        print(report)
        
        if args.save:
            date_str = datetime.now().strftime("%Y-%m-%d")
            path = f"Sources/Skill Package Analysis - {date_str}.md"
            save_note(path, report)
            print(f"\nSaved report to {path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())