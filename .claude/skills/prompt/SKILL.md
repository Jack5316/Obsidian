---
name: prompt
description: Generate well-structured and orchestrated prompts. Create prompts with clear role, context, task, output format, and constraints. Apply templates to content, design multi-step workflows, or generate custom prompts from descriptions. Use when you need prompt engineering, structured prompts, or /prompt.
---

# PROMPT Skill (/prompt)

Generate well-structured prompts and orchestrate multi-step prompt workflows. Maintains a library of curated templates and uses AI to create custom prompts or design orchestrated workflows.

## Quick Start

```bash
# List available templates
python3 _scripts/prompt_skill.py list

# Generate a custom prompt from description
python3 _scripts/prompt_skill.py generate "Summarize technical documentation"
```

## What It Does

1. **List** - Browse the prompt template library (summarize, analyze, critique, etc.)
2. **Generate** - Create well-structured prompts from natural language descriptions
3. **Apply** - Run a template against content (from path or inline)
4. **Orchestrate** - Design multi-step prompt workflows (e.g., extract → analyze → synthesize)
5. **Template** - Show raw template text for reference or customization

## Prompt Structure

All generated prompts follow a standard structure:

- **Role** - Expert persona (who is the AI?)
- **Context** - Background that matters
- **Task** - Exact instructions
- **Output Format** - Structure, sections, length
- **Constraints** - Tone, style, what to avoid

## Template Library

| Key | Name | Description |
|-----|------|-------------|
| `summarize` | Summarization | Condense content into key points |
| `analyze` | Analysis | Deep analysis with structure |
| `explain` | Explanation | Explain complex topics simply |
| `critique` | Critical Review | Evaluate with balanced judgment |
| `expand` | Expansion | Expand ideas with depth |
| `compare` | Comparison | Compare and contrast |
| `extract-actions` | Action Extraction | Extract actionable items |
| `socratic` | Socratic Questions | Generate probing questions |
| `steelman` | Steelman | Strengthen opposing views |
| `synthesis` | Synthesis | Cross-domain synthesis |

## Options

### list
- No options - lists all templates

### generate
- `description`: What the prompt should do (required)
- `--save`: Save to vault as `Templates/Prompt - [description] - YYYY-MM-DD.md`

### apply
- `template`: Template key (e.g., summarize, analyze)
- `--content TEXT`: Content to process inline
- `--from-path PATH`: Path to vault note with content
- `--save`: Save output to vault

### orchestrate
- `goal`: What the workflow should achieve (required)
- `--save`: Save to vault as `Templates/Prompt Workflow - [goal] - YYYY-MM-DD.md`

### template
- `key`: Template key - outputs raw template text

## Examples

```bash
# List all templates
python3 _scripts/prompt_skill.py list

# Generate a custom prompt
python3 _scripts/prompt_skill.py generate "Summarize technical documentation for non-experts"
python3 _scripts/prompt_skill.py generate "Explain quantum computing" --save

# Apply template to content
python3 _scripts/prompt_skill.py apply summarize --from-path "Sources/Article - 2026-02-19.md"
python3 _scripts/prompt_skill.py apply analyze --content "Long article text..." --save

# Design orchestrated workflow
python3 _scripts/prompt_skill.py orchestrate "Research a topic and produce a report with recommendations"
python3 _scripts/prompt_skill.py orchestrate "Extract insights from meeting notes and generate action items" --save

# Show raw template
python3 _scripts/prompt_skill.py template steelman
```

## Output

- **list**: Markdown table of templates
- **generate**: Well-structured prompt text (role, context, task, format, constraints)
- **apply**: AI-processed content using the template
- **orchestrate**: Multi-step workflow with prompts for each step
- **template**: Raw template text

## Saved Output

- Generated prompts: `Templates/Prompt - [description] - YYYY-MM-DD.md`
- Applied results: `Sources/[Template Name] - YYYY-MM-DD.md`
- Workflows: `Templates/Prompt Workflow - [goal] - YYYY-MM-DD.md`

## Related

- [[Prompt Template]] - Obsidian template for storing prompts
- [[Prompt Engineering MOC]] - Map of content for prompts
- [[Socrates]] - Socratic questioning (uses similar prompt structure)
