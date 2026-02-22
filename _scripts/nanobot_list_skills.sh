#!/usr/bin/env bash
# Direct skill list — bypasses agent (avoids summarization)
# Usage: ./nanobot_list_skills.sh  or  bash _scripts/nanobot_list_skills.sh
cd "$(dirname "$0")/.."
python3 _scripts/org_skill.py --list
