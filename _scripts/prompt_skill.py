"""PROMPT Skill - Generate well-structured and orchestrated prompts.

Creates prompts with clear structure (role, context, task, output format, constraints),
maintains a library of useful prompt templates, and orchestrates multi-step prompt workflows.
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH

# --- Prompt Template Library ---
PROMPT_LIBRARY = {
    "summarize": {
        "name": "Summarization",
        "description": "Condense content into key points",
        "template": """You are an expert summarizer. Your task is to distill the following content into a clear, structured summary.

**Structure your output as:**
1. **TL;DR** (1-2 sentences)
2. **Key Points** (3-5 bullet points)
3. **Takeaways** (actionable insights if applicable)

Preserve critical information. Be concise but complete. Use [[wikilinks]] for vault references when relevant.""",
    },
    "analyze": {
        "name": "Analysis",
        "description": "Deep analysis with structure",
        "template": """You are an expert analyst. Analyze the following content systematically.

**Structure your output as:**
1. **Overview** - What is this about?
2. **Strengths** - What works well?
3. **Weaknesses/Gaps** - What's missing or problematic?
4. **Implications** - So what? Why does it matter?
5. **Connections** - Link to related ideas using [[wikilinks]] when relevant

Be substantive. Support claims with evidence from the content.""",
    },
    "explain": {
        "name": "Explanation",
        "description": "Explain complex topics simply",
        "template": """You are an expert educator. Explain the following concept or content as if to an intelligent reader who is new to the topic.

**Structure your output as:**
1. **Core Idea** - One sentence definition
2. **Key Components** - Break it down
3. **How It Works** - Mechanism or logic
4. **Examples** - Concrete illustrations
5. **Common Misconceptions** - What people often get wrong

Use analogies. Avoid jargon or define it. Use [[wikilinks]] for vault references.""",
    },
    "critique": {
        "name": "Critical Review",
        "description": "Evaluate with balanced judgment",
        "template": """You are a critical reviewer. Evaluate the following content with intellectual honesty.

**Structure your output as:**
1. **Thesis** - What is the main argument?
2. **Evidence** - How well is it supported?
3. **Strengths** - What's convincing?
4. **Weaknesses** - What's questionable or missing?
5. **Verdict** - Balanced conclusion with nuance

Steelman the best version of the argument before critiquing. Use [[wikilinks]] for related notes.""",
    },
    "expand": {
        "name": "Expansion",
        "description": "Expand ideas with depth",
        "template": """You are a thoughtful expander. Take the seed idea below and develop it with depth and nuance.

**Structure your output as:**
1. **Core Claim** - Restate the idea clearly
2. **Elaboration** - Develop each dimension
3. **Examples** - Concrete illustrations
4. **Counterpoints** - What might challenge this?
5. **Synthesis** - Integrated view

Add value without diluting. Use [[wikilinks]] to connect to vault knowledge.""",
    },
    "compare": {
        "name": "Comparison",
        "description": "Compare and contrast",
        "template": """You are an expert at comparative analysis. Compare and contrast the following items.

**Structure your output as:**
1. **Overview** - What are we comparing?
2. **Similarities** - Where do they align?
3. **Differences** - Key distinctions
4. **Trade-offs** - Pros and cons of each
5. **When to use which** - Practical guidance

Be fair. Avoid false equivalence. Use [[wikilinks]] when relevant.""",
    },
    "extract-actions": {
        "name": "Action Extraction",
        "description": "Extract actionable items",
        "template": """You are an action-oriented processor. Extract all actionable items from the following content.

**Structure your output as:**
1. **Immediate Actions** - Do today/this week
2. **Short-term** - Next 2-4 weeks
3. **Long-term** - Strategic or ongoing
4. **Blockers** - What might prevent these?
5. **Dependencies** - What needs to happen first?

Format each action as: [ ] Action (context/source). Be specific.""",
    },
    "socratic": {
        "name": "Socratic Questions",
        "description": "Generate probing questions",
        "template": """You are an expert at Socratic questioning. Generate thought-provoking questions to deepen understanding of the following topic.

**Use the SOCRATES framework:**
- S: Clarification (What do you mean by...?)
- O: Origin (Where did this come from?)
- C: Consequence (What follows from this?)
- R: Role Reversal (What if the opposite?)
- A: Assumption (What are we taking for granted?)
- T: Truth/Evidence (How do we know?)
- E: Example (Can you give an example?)
- S: Synthesis (How does this relate to...?)

Generate 2-3 questions per category. Questions should build on each other.""",
    },
    "steelman": {
        "name": "Steelman",
        "description": "Strengthen opposing views",
        "template": """You are an expert at steelmanning — arguing the strongest version of a position, even one you disagree with.

**Structure your output as:**
1. **Charitable Restatement** - State the view in its best form
2. **Strongest Arguments** - Best evidence and reasoning for it
3. **Objections Addressed** - How would proponents respond to common critiques?
4. **Implications** - What follows if this view is correct?

Be genuinely charitable. The goal is understanding, not strawmanning. Use [[wikilinks]] for related ideas.""",
    },
    "synthesis": {
        "name": "Synthesis",
        "description": "Cross-domain synthesis",
        "template": """You are an expert synthesizer. Integrate the following sources into a coherent synthesis.

**Structure your output as:**
1. **Themes** - Recurring patterns across sources
2. **Tensions** - Where do sources disagree or conflict?
3. **Synthesis** - Integrated view that honors the best of each
4. **Implications** - What does this mean for practice/thinking?
5. **Open Questions** - What remains unresolved?

Connect ideas. Find the meta-pattern. Use [[wikilinks]] liberally for vault connections.""",
    },
}

# --- Prompt Structure Generator ---
PROMPT_GENERATOR_SYSTEM = """You are an expert at prompt engineering. Generate well-structured prompts for AI assistants.

**Standard prompt structure:**
1. **Role** - Who is the AI? (expert persona)
2. **Context** - What background matters?
3. **Task** - What exactly should the AI do?
4. **Output Format** - Structure, sections, length
5. **Constraints** - Tone, style, what to avoid

**Principles:**
- Be specific; vagueness produces vague output
- Define the output format explicitly
- Include constraints to avoid common failures
- Use placeholders like {{topic}} or {{content}} for variables
- Keep it focused — one primary task per prompt

**Output:** Return ONLY the prompt text, ready to use. No meta-commentary. Use markdown code block if helpful for structure."""

ORCHESTRATION_PROMPT = """You are a prompt orchestration expert. Design a multi-step prompt workflow for the user's goal.

**Common patterns:**
- Extract → Analyze → Synthesize
- Summarize → Critique → Recommend
- Explain → Compare → Conclude
- Question → Explore → Integrate

**Output format:**
For each step, provide:
1. Step number and name
2. The exact prompt (ready to use)
3. What gets passed to the next step (output of this step becomes input of next)

Return a JSON array of steps. Each step: {"name": "...", "prompt": "...", "passes_to_next": "description of what to pass"}"""


def list_templates():
    """List all available prompt templates."""
    lines = ["# Prompt Template Library\n", "| Key | Name | Description |", "|-----|------|-------------|"]
    for key, meta in PROMPT_LIBRARY.items():
        lines.append(f"| `{key}` | {meta['name']} | {meta['description']} |")
    return "\n".join(lines)


def get_template(key: str) -> str:
    """Get prompt template by key."""
    key = key.strip().lower()
    if key not in PROMPT_LIBRARY:
        valid = ", ".join(PROMPT_LIBRARY.keys())
        raise ValueError(f"Unknown template: {key}. Valid: {valid}")
    return PROMPT_LIBRARY[key]["template"]


def generate_prompt(user_description: str) -> str:
    """Use AI to generate a well-structured prompt from user description."""
    user_input = f"""The user wants a prompt for this purpose:

{user_description}

Generate a complete, well-structured prompt following the standard structure (role, context, task, output format, constraints). Output ONLY the prompt, no commentary."""
    return summarize(user_input, PROMPT_GENERATOR_SYSTEM)


def orchestrate(user_goal: str) -> str:
    """Use AI to design a multi-step prompt workflow."""
    user_input = f"""The user wants to achieve this goal:

{user_goal}

Design a multi-step prompt workflow. Each step's output feeds into the next. Return a JSON array of steps with "name", "prompt", and "passes_to_next" for each."""
    raw = summarize(user_input, ORCHESTRATION_PROMPT)
    # Try to extract JSON if wrapped in markdown
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if json_match:
        raw = json_match.group(1).strip()
    try:
        steps = json.loads(raw)
        out = ["# Orchestrated Prompt Workflow\n", f"**Goal:** {user_goal}\n"]
        for i, s in enumerate(steps, 1):
            out.append(f"## Step {i}: {s.get('name', 'Unnamed')}\n")
            out.append("### Prompt\n```\n")
            out.append(s.get("prompt", ""))
            out.append("\n```\n")
            out.append(f"**Passes to next:** {s.get('passes_to_next', 'N/A')}\n")
        return "".join(out)
    except json.JSONDecodeError:
        return raw


def apply_template(template_key: str, content: str) -> str:
    """Apply a prompt template to content via AI."""
    prompt = get_template(template_key)
    return summarize(content, prompt)


def main():
    parser = argparse.ArgumentParser(
        description="PROMPT Skill - Generate well-structured and orchestrated prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/prompt_skill.py list
  python3 _scripts/prompt_skill.py generate "Summarize technical documentation"
  python3 _scripts/prompt_skill.py apply summarize --content "Long article..."
  python3 _scripts/prompt_skill.py apply summarize --from-path Sources/Article.md
  python3 _scripts/prompt_skill.py orchestrate "Research a topic and produce a report"
  python3 _scripts/prompt_skill.py template summarize
  python3 _scripts/prompt_skill.py generate "Explain quantum computing" --save
""",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="List all prompt templates")

    # generate
    gen = sub.add_parser("generate", help="Generate a well-structured prompt from description")
    gen.add_argument("description", type=str, help="What the prompt should do")
    gen.add_argument("--save", action="store_true", help="Save to vault")

    # apply
    apply = sub.add_parser("apply", help="Apply a template to content")
    apply.add_argument("template", type=str, help="Template key (e.g., summarize, analyze)")
    apply.add_argument("--content", type=str, default=None, help="Content to process")
    apply.add_argument("--from-path", type=str, default=None, help="Path to note with content")
    apply.add_argument("--save", action="store_true", help="Save output to vault")

    # orchestrate
    orch = sub.add_parser("orchestrate", help="Design multi-step prompt workflow")
    orch.add_argument("goal", type=str, help="What the workflow should achieve")
    orch.add_argument("--save", action="store_true", help="Save to vault")

    # template (show raw template)
    tmpl = sub.add_parser("template", help="Show raw template text")
    tmpl.add_argument("key", type=str, help="Template key")

    args = parser.parse_args()

    if args.command == "list":
        print(list_templates())
        return

    if args.command == "template":
        try:
            print(get_template(args.key))
        except ValueError as e:
            print(f"Error: {e}")
            return 1
        return

    if args.command == "generate":
        print("Generating prompt...")
        result = generate_prompt(args.description)
        print("\n" + "=" * 60 + "\n")
        print(result)
        print("\n" + "=" * 60)
        if args.save:
            today = datetime.now().strftime("%Y-%m-%d")
            safe = re.sub(r"[^\w\s-]", "", args.description)[:40].strip() or "prompt"
            path = f"Templates/Prompt - {safe} - {today}.md"
            note = f"""---
type: prompt
date: {today}
description: {args.description}
tags:
  - ai/prompting
  - generated
---

# Generated Prompt

**Use case:** {args.description}

## The Prompt

```
{result}
```

## Variables

Customize as needed for each use.
"""
            save_note(path, note)
            print(f"\nSaved: {path}")
        return

    if args.command == "apply":
        if args.from_path:
            full = VAULT_PATH / args.from_path
            if not full.exists():
                print(f"Error: File not found: {args.from_path}")
                return 1
            content = full.read_text(encoding="utf-8")
            # Strip frontmatter
            fm = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
            if fm:
                content = content[fm.end() :]
        elif args.content:
            content = args.content
        else:
            print("Error: Provide --content or --from-path")
            return 1
        try:
            print(f"Applying template '{args.template}'...")
            result = apply_template(args.template, content.strip())
            print("\n" + "=" * 60 + "\n")
            print(result)
            print("\n" + "=" * 60)
            if args.save:
                today = datetime.now().strftime("%Y-%m-%d")
                meta = PROMPT_LIBRARY.get(args.template, {})
                name = meta.get("name", args.template)
                path = f"Sources/{name} - {today}.md"
                save_note(path, result)
                print(f"\nSaved: {path}")
        except ValueError as e:
            print(f"Error: {e}")
            return 1
        return

    if args.command == "orchestrate":
        print("Designing workflow...")
        result = orchestrate(args.goal)
        print("\n" + "=" * 60 + "\n")
        print(result)
        print("\n" + "=" * 60)
        if args.save:
            today = datetime.now().strftime("%Y-%m-%d")
            safe = re.sub(r"[^\w\s-]", "", args.goal)[:40].strip() or "workflow"
            path = f"Templates/Prompt Workflow - {safe} - {today}.md"
            note = f"""---
type: prompt-workflow
date: {today}
goal: {args.goal}
tags:
  - ai/prompting
  - orchestration
---

{result}
"""
            save_note(path, note)
            print(f"\nSaved: {path}")
        return

    return 0


if __name__ == "__main__":
    try:
        exit(main() or 0)
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
