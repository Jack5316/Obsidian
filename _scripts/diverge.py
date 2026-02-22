"""Diverge - Exploratory thinking and idea generation skill.

This skill facilitates divergent thinking - generating multiple creative ideas,
exploring possibilities, branching out from a central concept, and making
unexpected connections. Inspired by neuroscience concepts of neural plasticity
and associative thinking, combined with Tiago Forte's Second Brain principles.

Features:
- Idea generation from a central topic
- Multi-directional exploration paths
- Cross-domain connection discovery
- Random walk through idea space
- Question storming (5 Whys + 5 Hows)
- Mind map generation
"""

import argparse
import sys
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


DIVERGE_PROMPT = """You are a creative thinking assistant specializing in divergent thinking.
Your role is to help generate a wide range of creative ideas, explore multiple
possibilities, and discover unexpected connections.

Key principles:
- Quantity over quality - generate many ideas first, filter later
- Go beyond the obvious - seek wild, unconventional ideas
- Make cross-domain connections - borrow concepts from unrelated fields
- Build on ideas - use "yes, and..." thinking
- Challenge assumptions - question the obvious constraints

For each exploration, provide:
1. Core concept breakdown
2. Multiple divergent branches of thought
3. Cross-domain connections to unrelated fields
4. Provocative questions that challenge assumptions
5. Wild, unexpected ideas that push boundaries
"""


class DivergentThinker:
    """Engine for facilitating divergent thinking."""
    
    def __init__(self):
        self.cross_domain_seeds = [
            "biology", "physics", "music", "cooking", "architecture", 
            "nature", "sports", "technology", "art", "history", "mathematics",
            "psychology", "economics", "ecology", "literature", "design"
        ]
        
        self.question_starters = [
            "What if we reversed...?",
            "How could we combine...?",
            "What if we removed...?",
            "How would an expert in [X] approach this?",
            "What if we exaggerated...?",
            "How could we reuse...?",
            "What if we borrowed from...?",
            "How might we...?"
        ]
    
    def generate_ideas(self, topic: str, count: int = 10) -> List[str]:
        """Generate a list of diverse ideas from a central topic."""
        prompt = f"""Generate {count} diverse, creative ideas about: {topic}

For each idea, think expansively about:
- Different applications of the concept
- Unusual contexts where this might apply
- Opposite or inverted versions
- Combinations with other domains

Output exactly {count} ideas, one per line, numbered 1-{count}.
Each idea should be concise (1-2 sentences) and thought-provoking."""
        
        result = summarize(prompt, DIVERGE_PROMPT)
        return self._parse_list(result)
    
    def explore_branches(self, topic: str, branches: int = 5) -> Dict[str, List[str]]:
        """Explore multiple branching directions from a central topic."""
        prompt = f"""Starting from the central concept: {topic}

Explore {branches} different, distinct directions this topic could branch into.
For each branch:
1. Give it a clear, evocative name
2. Describe the core concept of this branch
3. List 3 sub-ideas or directions within this branch

Make each branch fundamentally different from the others.
Cover various perspectives: practical, theoretical, creative, critical, etc."""
        
        result = summarize(prompt, DIVERGE_PROMPT)
        return {"topic": topic, "branches": self._parse_sections(result)}
    
    def cross_domain_connections(self, topic: str, domains: Optional[List[str]] = None) -> List[str]:
        """Find connections between the topic and unrelated domains."""
        if domains is None:
            domains = random.sample(self.cross_domain_seeds, 5)
        
        prompt = f"""Explore connections between "{topic}" and these unrelated domains: {', '.join(domains)}

For each domain:
1. Find 2-3 surprising, non-obvious connections
2. Explain how concepts from that domain could shed new light on the topic
3. Generate a practical hybrid idea that combines both

Make these connections meaningful, not forced. Look for deep structural similarities."""
        
        result = summarize(prompt, DIVERGE_PROMPT)
        return self._parse_list(result)
    
    def question_storm(self, topic: str, count: int = 15) -> List[str]:
        """Generate provocative questions that challenge assumptions."""
        prompt = f"""Generate {count} provocative, thought-provoking questions about: {topic}

Include:
- Questions that challenge basic assumptions
- "What if..." questions that imagine different scenarios
- Questions that reveal hidden constraints
- Questions that open up new possibilities
- Questions that connect to bigger picture issues

Avoid simple factual questions. Focus on questions that spark thinking.
Number them 1-{count}."""
        
        result = summarize(prompt, DIVERGE_PROMPT)
        return self._parse_list(result)
    
    def mind_map(self, topic: str, depth: int = 3) -> Dict[str, Any]:
        """Create a mind map structure for the topic."""
        prompt = f"""Create a mind map for: {topic}

Structure:
- Central node: {topic}
- Level 1: 5-7 main branches
- Level 2: 3-5 sub-branches for each main branch
- Level 3: 2-3 details for each sub-branch (if depth allows)

Make it rich and interconnected. Use evocative language for each node."""
        
        result = summarize(prompt, DIVERGE_PROMPT)
        return {"topic": topic, "mind_map": result}
    
    def random_walk(self, topic: str, steps: int = 5) -> List[str]:
        """Take a random associative walk from the topic."""
        prompt = f"""Start with: {topic}

Take an associative random walk of {steps} steps. Each step should:
1. Make a surprising, non-obvious connection
2. Jump to a related but unexpected concept
3. Explain the connection between step N and step N+1

Format:
Start: [topic]
Step 1: [concept] (because: [connection])
Step 2: [concept] (because: [connection])
...
Final insight: [what we learned from this walk]"""
        
        result = summarize(prompt, DIVERGE_PROMPT)
        return self._parse_list(result)
    
    def _parse_list(self, text: str) -> List[str]:
        """Parse a numbered list from text."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return [line for line in lines if line and (line[0].isdigit() or ':' in line[:10])]
    
    def _parse_sections(self, text: str) -> List[str]:
        """Parse sections from text."""
        return [section.strip() for section in text.split('\n\n') if section.strip()]


def format_diverge_report(topic: str, results: Dict[str, Any], mode: str) -> str:
    """Format divergence results as markdown."""
    
    md = f"# Divergent Thinking: {topic}\n\n"
    md += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md += f"Mode: {mode}\n\n"
    md += "---\n\n"
    
    if mode == "ideas":
        md += "## Generated Ideas\n\n"
        for idea in results.get("ideas", []):
            md += f"{idea}\n\n"
    
    elif mode == "branches":
        md += "## Exploration Branches\n\n"
        md += results.get("branches_text", "")
    
    elif mode == "cross-domain":
        md += "## Cross-Domain Connections\n\n"
        for conn in results.get("connections", []):
            md += f"{conn}\n\n"
    
    elif mode == "questions":
        md += "## Question Storm\n\n"
        for q in results.get("questions", []):
            md += f"{q}\n\n"
    
    elif mode == "mindmap":
        md += "## Mind Map\n\n"
        md += results.get("mind_map_text", "")
    
    elif mode == "randomwalk":
        md += "## Random Associative Walk\n\n"
        for step in results.get("walk", []):
            md += f"{step}\n\n"
    
    elif mode == "full":
        md += "## Complete Divergence Session\n\n"
        md += "### Generated Ideas\n\n"
        for idea in results.get("ideas", [])[:5]:
            md += f"{idea}\n\n"
        
        md += "### Exploration Branches\n\n"
        md += results.get("branches_text", "")[:500] + "...\n\n"
        
        md += "### Question Storm\n\n"
        for q in results.get("questions", [])[:5]:
            md += f"{q}\n\n"
    
    md += "\n---\n*Generated by Diverge Skill - Exploratory Thinking*"
    
    return md


def main():
    """Main function for divergent thinking."""
    parser = argparse.ArgumentParser(
        description="Diverge - Exploratory thinking and idea generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill diverge "future of work"                  # Full divergence session
  /skill diverge "AI" --ideas 15                   # Generate 15 ideas
  /skill diverge "education" --branches            # Explore branches
  /skill diverge "creativity" --cross-domain       # Cross-domain connections
  /skill diverge "problem" --questions 20          # Question storming
  /skill diverge "topic" --mindmap                 # Generate mind map
  /skill diverge "start" --randomwalk 7            # Random walk
  /skill diverge "topic" --save                     # Save to Sources
"""
    )
    
    parser.add_argument(
        "topic",
        type=str,
        help="Central topic to explore"
    )
    
    parser.add_argument(
        "--ideas",
        type=int,
        default=None,
        help="Generate N ideas"
    )
    
    parser.add_argument(
        "--branches",
        action="store_true",
        help="Explore branching directions"
    )
    
    parser.add_argument(
        "--cross-domain",
        action="store_true",
        help="Find cross-domain connections"
    )
    
    parser.add_argument(
        "--questions",
        type=int,
        default=None,
        help="Generate N questions"
    )
    
    parser.add_argument(
        "--mindmap",
        action="store_true",
        help="Create mind map"
    )
    
    parser.add_argument(
        "--randomwalk",
        type=int,
        default=None,
        help="Take random walk of N steps"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to Sources"
    )
    
    args = parser.parse_args()
    
    thinker = DivergentThinker()
    results = {}
    mode = "full"
    
    print(f"🔀 Exploring: {args.topic}\n")
    
    # Determine which mode to use
    if args.ideas is not None:
        mode = "ideas"
        print(f"💡 Generating {args.ideas} ideas...")
        results["ideas"] = thinker.generate_ideas(args.topic, args.ideas)
    
    elif args.branches:
        mode = "branches"
        print("🌿 Exploring branches...")
        branch_result = thinker.explore_branches(args.topic)
        results["branches_text"] = str(branch_result)
    
    elif args.cross_domain:
        mode = "cross-domain"
        print("🔗 Finding cross-domain connections...")
        results["connections"] = thinker.cross_domain_connections(args.topic)
    
    elif args.questions is not None:
        mode = "questions"
        print(f"❓ Generating {args.questions} questions...")
        results["questions"] = thinker.question_storm(args.topic, args.questions)
    
    elif args.mindmap:
        mode = "mindmap"
        print("🗺️ Creating mind map...")
        mindmap_result = thinker.mind_map(args.topic)
        results["mind_map_text"] = str(mindmap_result)
    
    elif args.randomwalk is not None:
        mode = "randomwalk"
        print(f"🚶 Taking random walk of {args.randomwalk} steps...")
        results["walk"] = thinker.random_walk(args.topic, args.randomwalk)
    
    else:
        mode = "full"
        print("🧠 Full divergence session...")
        results["ideas"] = thinker.generate_ideas(args.topic, 10)
        branch_result = thinker.explore_branches(args.topic)
        results["branches_text"] = str(branch_result)
        results["questions"] = thinker.question_storm(args.topic, 15)
    
    # Generate report
    report = format_diverge_report(args.topic, results, mode)
    print("\n" + report)
    
    # Save if requested
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_topic = args.topic.replace(' ', '_').replace('/', '_')
        save_note(f"Sources/Diverge - {safe_topic} - {date_str}.md", report)
    
    print("\n✅ Divergence complete!")


if __name__ == "__main__":
    main()
