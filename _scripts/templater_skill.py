"""Templater Skill - Quickly create Obsidian templates.

Creates Obsidian note templates with YAML frontmatter and Templater syntax.
Supports built-in template types and AI-generated custom templates.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH

TEMPLATES_DIR = VAULT_PATH / "Templates"

# Built-in template library (Obsidian + Templater syntax)
TEMPLATE_LIBRARY = {
    "daily": {
        "name": "Daily Note",
        "description": "Daily note with intention, tasks, learnings, and reflection",
        "content": """---
created: "{{date:YYYY-MM-DD}}"
tags:
  - type/daily
---

# {{date:dddd, MMMM D, YYYY}}

## Morning Intention

> What's the one thing that matters most today?



## Tasks

### Must Do
- [ ]

### Should Do
- [ ]

### Could Do
- [ ]

## Notes & Captures

> Quick thoughts throughout the day. Process into proper notes later.

-

## Learnings

> What did I learn today?

-

## End of Day

### What went well?
-

### What to improve?
-

### Inbox items to process?
- [ ] Check [[00 - Inbox/Start Here|Inbox]]
""",
    },
    "meeting": {
        "name": "Meeting Note",
        "description": "Meeting notes with attendees, agenda, decisions, action items",
        "content": """---
created: "{{date:YYYY-MM-DD}}"
tags:
  - type/fleeting
  - status/processing
---

# {{title}} - {{date:YYYY-MM-DD}}

## Attendees
-

## Agenda
-

## Notes



## Decisions Made
-

## Action Items

- [ ]

## Follow Up

- [ ] Process into relevant project/area notes
""",
    },
    "project": {
        "name": "Project Note",
        "description": "Project tracking with outcome, actions, tasks, and log",
        "content": """---
created: "{{date:YYYY-MM-DD}}"
tags:
  - type/project
  - status/processing
status: active
due: ""
outcome: ""
---

# {{title}}

## Desired Outcome

> What does "done" look like? Be specific.



## Why This Matters



## Next Actions

- [ ]

## Tasks

- [ ]

## Resources & Links

-

## Log

### {{date:YYYY-MM-DD}}
- Project started

## Related

- MOC:
- Area:
""",
    },
    "permanent": {
        "name": "Permanent Note",
        "description": "Evergreen note - one idea that stands on its own",
        "content": """---
created: "{{date:YYYY-MM-DD}}"
tags:
  - type/permanent
  - status/evergreen
---

# {{title}}

> *One idea, in your own words, that stands on its own.*



## Supporting Evidence

-

## Connected Ideas

- Builds on:
- Contradicts:
- Leads to:

## Source Notes

- Originated from:
""",
    },
    "fleeting": {
        "name": "Fleeting Note",
        "description": "Quick capture for raw thoughts and inbox processing",
        "content": """---
created: "{{date:YYYY-MM-DD}}"
tags:
  - type/fleeting
  - status/inbox
---

# {{title}}

## Thought

> What's on your mind? Capture it raw - don't overthink.



## Context

> Where did this come from? What triggered it?



## Next Step

- [ ] Process this note: clarify, link, or discard
""",
    },
    "literature": {
        "name": "Literature Note",
        "description": "Notes from reading - quotes, summary, and connections",
        "content": """---
created: "{{date:YYYY-MM-DD}}"
tags:
  - type/literature
  - status/processing
---

# {{title}}

## Source

- Author:
- Type: (book / article / paper / video)
- Date:

## Summary

> Main argument or thesis in your own words.



## Key Quotes

> 

## My Notes



## Connections

- Relates to:
- Contradicts:
""",
    },
    "moc": {
        "name": "MOC Template",
        "description": "Map of Content - hub note linking related notes",
        "content": """---
created: "{{date:YYYY-MM-DD}}"
tags:
  - type/moc
---

# {{title}} MOC

> Map of Content for [topic]. Links to key notes and sub-MOCs.

## Overview



## Key Notes

- 
- 
- 

## Sub-MOCs

- 

## Related MOCs

- 
""",
    },
    "experiment": {
        "name": "Experiment Log",
        "description": "Structured log for experiments and tests",
        "content": """---
created: "{{date:YYYY-MM-DD}}"
tags:
  - type/experiment
  - status/processing
---

# {{title}} - {{date:YYYY-MM-DD}}

## Hypothesis

> What are we testing?



## Setup

- 

## Procedure

1.
2.
3.

## Results

-

## Conclusion

-

## Next Steps

- [ ]
""",
    },
}


def list_templates():
    """List all templates in the vault's Templates folder."""
    if not TEMPLATES_DIR.exists():
        print("Templates folder not found.")
        return
    files = sorted(TEMPLATES_DIR.glob("*.md"))
    if not files:
        print("No templates found in Templates/")
        return
    print("## Templates in vault\n")
    for f in files:
        print(f"- [[{f.stem}]]")
    print(f"\n({len(files)} templates)")


def create_from_type(template_type: str, name: Optional[str], save: bool) -> str:
    """Create template from built-in type."""
    if template_type not in TEMPLATE_LIBRARY:
        valid = ", ".join(TEMPLATE_LIBRARY.keys())
        return f"Unknown type '{template_type}'. Valid: {valid}"
    tpl = TEMPLATE_LIBRARY[template_type]
    content = tpl["content"]
    display_name = name or tpl["name"]
    if save:
        save_note(f"Templates/{display_name}.md", content)
    return content


def create_from_description(description: str, name: Optional[str], save: bool) -> str:
    """Create template from AI-generated description."""
    prompt = """You are an expert at creating Obsidian note templates. Create a complete, ready-to-use Obsidian template based on the user's description.

Requirements:
1. Use YAML frontmatter with: created (Templater: "{{date:YYYY-MM-DD}}"), tags
2. Use Templater syntax where appropriate: {{date:...}}, {{title}}
3. Include clear section headers and placeholder content
4. Use [[wikilinks]] for internal references when relevant
5. Follow the vault's style: type tags (type/daily, type/project, etc.), status tags
6. Output ONLY the template markdown, no explanation
7. Use > blockquotes for section prompts/hints where helpful
8. Include task checkboxes - [ ] where actions are needed

Create a well-structured template that matches the description."""
    content = summarize(description, prompt)
    # Ensure it starts clean (no markdown code block wrapper)
    if content.startswith("```"):
        lines = content.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines)
    display_name = name or f"Custom - {description[:30]}..."
    if save:
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in display_name)
        save_note(f"Templates/{safe_name}.md", content)
    return content


def show_template(name: str) -> str:
    """Show template content by name (filename without .md)."""
    path = TEMPLATES_DIR / f"{name}.md"
    if not path.exists():
        # Try partial match
        matches = list(TEMPLATES_DIR.glob(f"*{name}*.md"))
        if len(matches) == 1:
            path = matches[0]
        elif len(matches) > 1:
            return f"Multiple matches: {[m.stem for m in matches]}"
        else:
            return f"Template not found: {name}"
    return path.read_text(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Templater - Quickly create Obsidian templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/templater_skill.py list
  python3 _scripts/templater_skill.py create daily
  python3 _scripts/templater_skill.py create daily --name "My Daily" --save
  python3 _scripts/templater_skill.py create "Book review with quotes and rating"
  python3 _scripts/templater_skill.py create "Weekly review template" --save
  python3 _scripts/templater_skill.py show "Daily Note"
""",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="List all templates in vault")

    # create
    create_p = sub.add_parser("create", help="Create a template")
    create_p.add_argument(
        "source",
        help="Built-in type (daily, meeting, project, permanent, fleeting, literature, moc, experiment) OR description for AI-generated template",
    )
    create_p.add_argument("--name", "-n", help="Custom filename (without .md)")
    create_p.add_argument("--save", "-s", action="store_true", help="Save to Templates/")

    # show
    show_p = sub.add_parser("show", help="Show template content")
    show_p.add_argument("name", help="Template name (filename without .md)")

    # types (for reference)
    types_p = sub.add_parser("types", help="List built-in template types")
    types_p.add_argument("--verbose", "-v", action="store_true", help="Show template content")

    args = parser.parse_args()

    if args.command == "list":
        list_templates()
        return

    if args.command == "show":
        print(show_template(args.name))
        return

    if args.command == "types":
        print("## Built-in template types\n")
        for key, tpl in TEMPLATE_LIBRARY.items():
            print(f"- **{key}**: {tpl['description']}")
            if getattr(args, "verbose", False):
                print(f"\n```\n{tpl['content'][:200]}...\n```\n")
        return

    if args.command == "create":
        builtin = list(TEMPLATE_LIBRARY.keys())
        if args.source.lower() in builtin:
            result = create_from_type(args.source.lower(), args.name, args.save)
        else:
            result = create_from_description(args.source, args.name, args.save)
        print(result)


if __name__ == "__main__":
    main()
