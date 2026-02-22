#!/usr/bin/env python3
"""Meta Skill - Create new skills following the PAI framework guidelines.

This skill helps you create new skills by:
1. Guiding you through the skill creation process
2. Generating the Python script template
3. Generating the SKILL.md file
4. Providing instructions for registering in skills.json

Based on the "How to Create a New Skill" section in CLAUDE.md.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


def create_python_script(skill_name_hyphen, description, features=None):
    """Create the Python script template."""
    skill_name_snake = skill_name_hyphen.replace('-', '_')
    
    features_list = features if features else ["Feature 1", "Feature 2", "Feature 3"]
    features_str = "\n".join([f"1. **{f}** - Description" for f in features_list])
    
    script_content = f'''#!/usr/bin/env python3
"""{skill_name_hyphen.title()} - {description}

Explain the purpose and key features here.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH


def main():
    """Main function for the skill."""
    parser = argparse.ArgumentParser(
        description="{skill_name_hyphen.title()} - {description}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=\"\"\"
Examples:
  /skill {skill_name_hyphen}                    # Basic usage
  /skill {skill_name_hyphen} --option value    # With options
  /skill {skill_name_hyphen} --save            # Save output
\"\"\"
    )
    
    parser.add_argument(
        "--option",
        type=str,
        help="Description of option"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to vault"
    )
    
    args = parser.parse_args()
    
    # Your skill logic here
    result = "Skill output content..."
    
    if args.save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_note(f"Sources/{skill_name_hyphen.title().replace('-', ' ')} - {{date_str}}.md", result)
    
    print(result)


if __name__ == "__main__":
    main()
'''
    return script_content, skill_name_snake


def create_skill_md(skill_name_hyphen, description, features=None):
    """Create the SKILL.md file content."""
    features_list = features if features else ["Feature 1", "Feature 2", "Feature 3"]
    features_str = "\n".join([f"1. **{f}** - Description" for f in features_list])
    skill_name_snake = skill_name_hyphen.replace('-', '_')
    
    skill_md_content = f'''---
name: {skill_name_hyphen}
description: {description}
---

# {skill_name_hyphen.title().replace('-', ' ')} (/{skill_name_hyphen})

{description}

## Quick Start

```bash
python3 _scripts/{skill_name_snake}.py
```

## Features

{features_str}

## Options

- `--option TEXT`: Description of option
- `--save`: Save output to vault

## Examples

```bash
# Basic usage
python3 _scripts/{skill_name_snake}.py

# With options
python3 _scripts/{skill_name_snake}.py --option value

# Save output
python3 _scripts/{skill_name_snake}.py --save
```

## Output

- **Terminal**: Markdown or text output
- **Saved note**: `Sources/{skill_name_hyphen.title().replace('-', ' ')} - YYYY-MM-DD.md`
'''
    return skill_md_content


def create_skills_json_entry(skill_name_hyphen, description):
    """Create the skills.json entry."""
    skill_name_snake = skill_name_hyphen.replace('-', '_')
    entry = {
        skill_name_hyphen: {
            "description": description,
            "commands": [
                f"python3 _scripts/{skill_name_snake}.py"
            ]
        }
    }
    return json.dumps(entry, indent=2)


def main():
    """Main function for the meta skill."""
    parser = argparse.ArgumentParser(
        description="Meta Skill - Create new skills following PAI framework guidelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill meta-skill create my-new-skill "Description of skill"  # Create new skill
  /skill meta-skill guide                                        # Show creation guide
  /skill meta-skill checklist                                    # Show completion checklist
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new skill")
    create_parser.add_argument("skill_name", help="Hyphenated skill name (e.g., my-new-skill)")
    create_parser.add_argument("description", help="Brief description of the skill")
    create_parser.add_argument("--features", nargs="+", help="List of features (optional)")
    create_parser.add_argument("--output-dir", default=str(VAULT_PATH), help="Output directory")
    
    # Guide command
    guide_parser = subparsers.add_parser("guide", help="Show skill creation guide")
    
    # Checklist command
    checklist_parser = subparsers.add_parser("checklist", help="Show completion checklist")
    
    args = parser.parse_args()
    
    if args.command == "create":
        # Create the skill files
        python_script, skill_name_snake = create_python_script(args.skill_name, args.description, args.features)
        skill_md = create_skill_md(args.skill_name, args.description, args.features)
        skills_json_entry = create_skills_json_entry(args.skill_name, args.description)
        
        # Save Python script
        script_path = Path(args.output_dir) / "_scripts" / f"{skill_name_snake}.py"
        script_path.parent.mkdir(exist_ok=True)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(python_script)
        print(f"✓ Created Python script: {script_path}")
        
        # Make executable
        script_path.chmod(0o755)
        
        # Save SKILL.md
        skill_dir = Path(args.output_dir) / ".claude" / "skills" / args.skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_md_path = skill_dir / "SKILL.md"
        with open(skill_md_path, 'w', encoding='utf-8') as f:
            f.write(skill_md)
        print(f"✓ Created SKILL.md: {skill_md_path}")
        
        # Print summary and next steps
        print("\n" + "="*60)
        print("SKILL CREATED SUCCESSFULLY!")
        print("="*60)
        print("\nNext steps:")
        print("1. Edit the Python script to implement your logic")
        print(f"2. Add this entry to .claude/skills.json:")
        print("\n" + skills_json_entry)
        print("\n3. Test your skill")
        print("4. Run '/skill meta-skill checklist' to verify completion")
        
    elif args.command == "guide":
        # Show the skill creation guide from CLAUDE.md
        guide = '''
# Skill Creation Guide (from CLAUDE.md)

## 1. Create the Python Script (_scripts/my_new_skill.py)
- Follow the common script pattern
- Import from config.py
- Use argparse with examples
- Save output using save_note()

## 2. Create the Skill Definition (.claude/skills/my-new-skill/SKILL.md)
- Include YAML frontmatter
- Add quick start, features, options, examples
- Document output locations

## 3. Register in skills.json
- Add to .claude/skills.json
- Provide clear description with use cases

## 4. Follow Conventions
- Naming: hyphenated for skills, snake_case for scripts
- Documentation: docstrings, SKILL.md, argparse examples
- Output: save to Sources/ with dated filenames
- Configuration: import from config.py, use VAULT_PATH

## Reference Implementations
- Content Curation: arxiv_digest.py, reddit_digest.py
- Task/Management: project_track.py, goal_track.py
- Self-Improvement: self_reflection.py, insight_enhancement.py
- Obsidian Integration: obsidian_vault_analytics.py, memory_consolidator.py
'''
        print(guide)
        
    elif args.command == "checklist":
        # Show the completion checklist
        checklist = '''
# Skill Creation Checklist

Before considering a skill complete:

- [ ] Python script created in _scripts/
- [ ] Script uses argparse with helpful examples
- [ ] Script imports from config.py
- [ ] SKILL.md created in .claude/skills/<skill-name>/
- [ ] Added to .claude/skills.json
- [ ] Tested (runs without errors)
- [ ] Saves output to appropriate location (Sources/, Atlas/, etc.)
- [ ] Uses YAML frontmatter if appropriate (for memory files)
- [ ] Follows "scripts before prompts" principle (Python for deterministic tasks, AI only for judgment)
'''
        print(checklist)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
