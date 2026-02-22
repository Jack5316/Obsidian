"""Converge - Synthesis, prioritization, and decision making skill.

This skill facilitates convergent thinking - synthesizing multiple ideas into
coherent wholes, prioritizing options, making decisions, and narrowing down
possibilities to actionable next steps. Inspired by neuroscience concepts
of cognitive control and decision making, combined with Tiago Forte's
Second Brain principles.

Features:
- Idea synthesis and distillation
- Multi-criteria prioritization
- Decision framework application
- Actionable next step generation
- Trade-off analysis
- Signal extraction from noise
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


CONVERGE_PROMPT = """You are a strategic thinking assistant specializing in convergent thinking.
Your role is to synthesize complex information, prioritize options, make clear
decisions, and identify actionable next steps.

Key principles:
- Find patterns and common themes
- Apply structured decision frameworks
- Balance intuition with analytical thinking
- Make clear, justifiable decisions
- Identify concrete, actionable next steps

For each convergence, provide:
1. Clear synthesis of key patterns
2. Structured prioritization with rationale
3. Decision with justification
4. Clear, actionable next steps
5. Identification of remaining uncertainties
"""


class ConvergentThinker:
    """Engine for facilitating convergent thinking."""
    
    def __init__(self):
        self.prioritization_frameworks = [
            "impact-effort", "urgent-important", "cost-benefit",
            "risk-reward", "value-complexity"
        ]
        
        self.decision_frameworks = [
            "pros-cons", "decision-matrix", "cost-benefit-analysis",
            "swot", "second-order-thinking"
        ]
    
    def synthesize(self, topic: str, ideas: List[str]) -> Dict[str, Any]:
        """Synthesize multiple ideas into coherent patterns."""
        ideas_text = '\n'.join(f"{i+1}. {idea}" for i, idea in enumerate(ideas))
        
        prompt = f"""Synthesize these ideas about: {topic}

Ideas to synthesize:
{ideas_text}

Provide:
1. Key patterns and common themes
2. Core insights that emerge
3. How these ideas connect and reinforce each other
4. A synthesized framework or model that ties everything together
5. The most important 3-5 insights to remember"""
        
        result = summarize(prompt, CONVERGE_PROMPT)
        return {"topic": topic, "synthesis": result}
    
    def prioritize(self, options: List[str], framework: str = "impact-effort", criteria: Optional[List[str]] = None) -> Dict[str, Any]:
        """Prioritize options using a framework."""
        options_text = '\n'.join(f"{i+1}. {opt}" for i, opt in enumerate(options))
        
        criteria_text = ""
        if criteria:
            criteria_text = f"Additional criteria: {', '.join(criteria)}"
        
        prompt = f"""Prioritize these options using the {framework} framework:

Options:
{options_text}

{criteria_text}

Framework: {framework}

For each option, provide:
1. Score/position on {framework} matrix
2. Justification for placement
3. Clear prioritization order
4. Top 3 recommendations with rationale

Be systematic and objective, but also pragmatic about real-world constraints."""
        
        result = summarize(prompt, CONVERGE_PROMPT)
        return {"framework": framework, "prioritization": result}
    
    def decide(self, question: str, options: List[str], framework: str = "pros-cons") -> Dict[str, Any]:
        """Make a clear decision with justification."""
        options_text = '\n'.join(f"{i+1}. {opt}" for i, opt in enumerate(options))
        
        prompt = f"""Make a clear decision about: {question}

Options:
{options_text}

Framework: {framework}

Using the {framework} framework, provide:
1. Clear analysis of each option
2. Comparison and contrast
3. Clear, justifiable decision
4. Second-order consequences to consider
5. Risk mitigation strategy
6. Contingency plans

Make a clear recommendation, don't just analyze forever."""
        
        result = summarize(prompt, CONVERGE_PROMPT)
        return {"question": question, "decision": result}
    
    def next_steps(self, goal: str, synthesis: str) -> List[str]:
        """Generate concrete, actionable next steps."""
        prompt = f"""Generate concrete, actionable next steps for: {goal}

Based on this synthesis:
{synthesis}

Provide:
1. 5-7 specific, actionable next steps
2. Timeline/priority for each
3. Success metrics
4. Potential obstacles and how to overcome
5. Quick wins we can achieve immediately

Each next step should be:
- Specific and concrete (not vague)
- Actionable (someone can actually do it)
- Time-bound (has clear timing)
- Measurable (we can tell if it's done)"""
        
        result = summarize(prompt, CONVERGE_PROMPT)
        return self._parse_list(result)
    
    def tradeoffs(self, options: List[str]) -> Dict[str, Any]:
        """Analyze tradeoffs between options."""
        options_text = '\n'.join(f"{i+1}. {opt}" for i, opt in enumerate(options))
        
        prompt = f"""Analyze the tradeoffs between these options:

{options_text}

For each pair of options, analyze:
1. What you gain by choosing A over B
2. What you lose by choosing A over B
3. Irreversible vs reversible decisions
4. Opportunity costs
5. Second-order implications
6. Which tradeoffs are most critical

Provide a clear tradeoff matrix and guidance on what matters most."""
        
        result = summarize(prompt, CONVERGE_PROMPT)
        return {"options": options, "tradeoffs": result}
    
    def distill(self, content: str, ratio: float = 0.3) -> str:
        """Distill content to its essence."""
        percentage = int(ratio * 100)
        prompt = f"""Distill this content to approximately {percentage}% of its original length:

{content}

Extract:
1. Core essence (what must be preserved
2. Key insights that can't be lost
3. Critical supporting evidence
4. Eliminate redundancy, fluff, and noise

Make it concise but comprehensive."""
        
        return summarize(prompt, CONVERGE_PROMPT)
    
    def full_convergence(self, topic: str, ideas: List[str]) -> Dict[str, Any]:
        """Complete convergence process: synthesize, prioritize, decide, next steps."""
        synthesis = self.synthesize(topic, ideas)
        prioritization = self.prioritize(ideas[:10], "impact-effort")
        tradeoffs = self.tradeoffs(ideas[:5])
        next_steps = self.next_steps(topic, synthesis["synthesis"])
        
        return {
            "synthesis": synthesis,
            "prioritization": prioritization,
            "tradeoffs": tradeoffs,
            "next_steps": next_steps
        }
    
    def _parse_list(self, text: str) -> List[str]:
        """Parse a numbered list from text."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return [line for line in lines if line and (line[0].isdigit() or ':' in line[:10])]


def format_converge_report(topic: str, results: Dict[str, Any], mode: str) -> str:
    """Format convergence results as markdown."""
    
    md = f"# Convergent Thinking: {topic}\n\n"
    md += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md += f"Mode: {mode}\n\n"
    md += "---\n\n"
    
    if mode == "synthesize":
        md += "## Synthesis\n\n"
        md += results.get("synthesis_text", "")
    
    elif mode == "prioritize":
        md += "## Prioritization\n\n"
        md += results.get("prioritization_text", "")
    
    elif mode == "decide":
        md += "## Decision\n\n"
        md += results.get("decision_text", "")
    
    elif mode == "nextsteps":
        md += "## Next Steps\n\n"
        for step in results.get("next_steps", []):
            md += f"{step}\n\n"
    
    elif mode == "tradeoffs":
        md += "## Tradeoff Analysis\n\n"
        md += results.get("tradeoffs_text", "")
    
    elif mode == "distill":
        md += "## Distilled Content\n\n"
        md += results.get("distilled", "")
    
    elif mode == "full":
        md += "## Complete Convergence Session\n\n"
        md += "### Synthesis\n\n"
        md += str(results.get("synthesis_result", {}).get("synthesis", ""))[:500] + "...\n\n"
        md += "### Prioritization\n\n"
        md += str(results.get("prioritization_result", {}).get("prioritization", ""))[:500] + "...\n\n"
        md += "### Next Steps\n\n"
        for step in results.get("next_steps_result", [])[:5]:
            md += f"{step}\n\n"
    
    md += "\n---\n*Generated by Converge Skill - Convergent Thinking*"
    
    return md


def main():
    """Main function for convergent thinking."""
    parser = argparse.ArgumentParser(
        description="Converge - Synthesis, prioritization, decision making",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill converge "future projects" --ideas "idea1" "idea2" "idea3"
  /skill converge --prioritize "option1" "option2" --framework impact-effort
  /skill converge --decide "which project first?" "option1" "option2"
  /skill converge --nextsteps "goal description"
  /skill converge --tradeoffs "option1" "option2" "option3"
  /skill converge --distill file.txt --ratio 0.3
  /skill converge "topic" --ideas "i1" "i2" --full
  /skill converge "topic" --save
"""
    )
    
    parser.add_argument(
        "topic",
        type=str,
        nargs="?",
        help="Topic or question to converge on"
    )
    
    parser.add_argument(
        "--ideas",
        type=str,
        nargs="*",
        help="List of ideas/options to process"
    )
    
    parser.add_argument(
        "--synthesize",
        action="store_true",
        help="Synthesize ideas into patterns"
    )
    
    parser.add_argument(
        "--prioritize",
        action="store_true",
        help="Prioritize options"
    )
    
    parser.add_argument(
        "--decide",
        action="store_true",
        help="Make a decision"
    )
    
    parser.add_argument(
        "--nextsteps",
        action="store_true",
        help="Generate actionable next steps"
    )
    
    parser.add_argument(
        "--tradeoffs",
        action="store_true",
        help="Analyze tradeoffs"
    )
    
    parser.add_argument(
        "--distill",
        type=str,
        default=None,
        help="File to distill"
    )
    
    parser.add_argument(
        "--framework",
        type=str,
        default="impact-effort",
        choices=["impact-effort", "urgent-important", "cost-benefit", 
                 "risk-reward", "value-complexity", "pros-cons",
                 "decision-matrix", "swot"],
        help="Framework to use"
    )
    
    parser.add_argument(
        "--ratio",
        type=float,
        default=0.3,
        help="Distillation ratio (0.1-0.9)"
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full convergence session"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to Sources"
    )
    
    args = parser.parse_args()
    
    thinker = ConvergentThinker()
    results = {}
    mode = "synthesize"
    
    if not args.topic and not args.distill:
        parser.error("Please provide a topic or use --distill")
    
    if args.topic:
        print(f"🎯 Converging on: {args.topic}\n")
    
    # Determine mode
    if args.prioritize and args.ideas:
        mode = "prioritize"
        print("📊 Prioritizing options...")
        prio_result = thinker.prioritize(args.ideas, args.framework)
        results["prioritization_text"] = str(prio_result)
    
    elif args.decide and args.ideas:
        mode = "decide"
        print("⚖️ Making decision...")
        decision_result = thinker.decide(args.topic, args.ideas, args.framework)
        results["decision_text"] = str(decision_result)
    
    elif args.nextsteps:
        mode = "nextsteps"
        print("🚀 Generating next steps...")
        results["next_steps"] = thinker.next_steps(args.topic, "Goal: " + args.topic)
    
    elif args.tradeoffs and args.ideas:
        mode = "tradeoffs"
        print("⚖️ Analyzing tradeoffs...")
        tradeoff_result = thinker.tradeoffs(args.ideas)
        results["tradeoffs_text"] = str(tradeoff_result)
    
    elif args.distill:
        mode = "distill"
        print("🔍 Distilling content...")
        try:
            content = Path(args.distill).read_text()
            results["distilled"] = thinker.distill(content, args.ratio)
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    
    elif args.full and args.ideas:
        mode = "full"
        print("🧠 Full convergence session...")
        full_result = thinker.full_convergence(args.topic, args.ideas)
        results["synthesis_result"] = full_result["synthesis"]
        results["prioritization_result"] = full_result["prioritization"]
        results["next_steps_result"] = full_result["next_steps"]
    
    elif args.ideas:
        mode = "synthesize"
        print("🔗 Synthesizing ideas...")
        synth_result = thinker.synthesize(args.topic, args.ideas)
        results["synthesis_text"] = str(synth_result)
    
    else:
        parser.print_help()
        return
    
    # Generate report
    report = format_converge_report(args.topic or "Content", results, mode)
    print("\n" + report)
    
    # Save if requested
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_topic = (args.topic or "content").replace(' ', '_').replace('/', '_')
        save_note(f"Sources/Converge - {safe_topic} - {date_str}.md", report)
    
    print("\n✅ Convergence complete!")


if __name__ == "__main__":
    main()
