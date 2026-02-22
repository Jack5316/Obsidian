"""AI Insight - Gain self-knowledge from vault data.

Analyzes your Obsidian vault to surface insights across:
- Core Mindset (inner conflicts, values, MBTI, CBT/ACT, positives, action guide)
- Cognitive Models (reverse thinking, second-order, anti-intuitive, 主要矛盾, 价值澄清)
- Exploration Frameworks (Soul Question, blind spots, perspectives)
- Key Influences (Munger, Aristotle, Seneca, Tasha Eurich, 复利飞轮)
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from config import summarize, save_note, VAULT_PATH, TRACKER

PRIORITY_TYPES = {"weekly-synthesis", "daily-synthesis", "self-reflection", "self-evolution"}


def collect_notes(
    days: int = 90,
    include_atlas: bool = True,
    include_maps: bool = True,
    include_inbox: bool = True,
    include_para: bool = True,
    topic_keywords: Optional[List[str]] = None,
) -> List[dict]:
    """Collect notes from Sources, Atlas, Maps, Inbox, and PARA areas."""
    notes = []

    def add_note(path: Path, source: str, note_type: str, content: str, mtime=None):
        body = content
        fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if fm_match:
            body = content[fm_match.end():]

        if topic_keywords:
            combined = (path.stem + " " + body).lower()
            if not any(kw.lower() in combined for kw in topic_keywords):
                return

        char_limit = 4000 if source == "Sources" else 3000
        notes.append({
            "filename": path.stem,
            "type": note_type,
            "source": source,
            "date": mtime.strftime("%Y-%m-%d") if mtime else "",
            "content": body[:char_limit],
            "priority": 1 if note_type in PRIORITY_TYPES else 0,
        })

    cutoff = datetime.now() - timedelta(days=days)

    # Sources
    sources_dir = VAULT_PATH / "Sources"
    if sources_dir.exists():
        for md_file in sources_dir.glob("*.md"):
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
            if mtime < cutoff:
                continue
            content = md_file.read_text(encoding="utf-8")
            note_type = "unknown"
            type_match = re.search(r"^type:\s*(.+)$", content, re.MULTILINE)
            if type_match:
                note_type = type_match.group(1).strip()
            add_note(md_file, "Sources", note_type, content, mtime)

    # Atlas
    if include_atlas:
        atlas_dir = VAULT_PATH / "Atlas"
        if atlas_dir.exists():
            for md_file in atlas_dir.glob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                add_note(md_file, "Atlas", "atlas", content)

    # Maps
    if include_maps:
        maps_dir = VAULT_PATH / "Maps"
        if maps_dir.exists():
            for md_file in maps_dir.glob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                add_note(md_file, "Maps", "moc", content)

    # Inbox
    if include_inbox:
        for inbox_name in ["00 - Inbox", "Inbox", "00-Inbox"]:
            inbox_dir = VAULT_PATH / inbox_name
            if inbox_dir.exists():
                for md_file in inbox_dir.glob("*.md"):
                    mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                    if mtime < cutoff:
                        continue
                    content = md_file.read_text(encoding="utf-8")
                    add_note(md_file, "Inbox", "inbox", content, mtime)
                break

    # PARA: Projects, Areas, Resources
    if include_para:
        for para_name in ["01 - Projects", "02 - Areas", "03 - Resources", "Projects", "Areas", "Resources"]:
            para_dir = VAULT_PATH / para_name
            if para_dir.exists():
                for md_file in para_dir.rglob("*.md"):
                    mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                    if mtime < cutoff:
                        continue
                    try:
                        content = md_file.read_text(encoding="utf-8")
                        add_note(md_file, para_name, "para", content, mtime)
                    except Exception:
                        pass

    notes.sort(key=lambda n: (-n["priority"], n["date"] or "0000-00-00"), reverse=True)
    return notes


def build_insight_prompt(focus: Optional[str], notes_text: str) -> str:
    """Build the system prompt for AI Insight analysis."""
    base = """You are an expert in self-knowledge and psychological analysis. Your task is to analyze a personal knowledge base (Obsidian vault) and generate a comprehensive AI Insight report that helps the user understand themselves better.

**Context:** The user has accumulated notes, reflections, syntheses, and thoughts in their vault. Your job is to synthesize this data into actionable self-knowledge across the following dimensions.

---

## 1. Core Mindset and Analysis

(a) **Inner Conflicts** — Identify recurring tensions, contradictions, or dilemmas in the user's thinking. What do they struggle with repeatedly? What opposing forces pull at them?

(b) **Values and What I See as Valuable** — Extract what the user consistently values. What do they prioritize? What principles guide their decisions? What do they consider meaningful?

(c) **MBTI Analysis** — Based on patterns in their writing (decision style, energy sources, information processing, lifestyle orientation), suggest a likely MBTI type with evidence from the notes. Acknowledge this is inferential.

(d) **CBT and ACT Therapy Lenses** — Apply cognitive-behavioral and acceptance-commitment frameworks: What cognitive distortions might appear? What avoidance patterns? What would "acceptance" and "values-based action" look like for them?

(e) **Positives Every Day** — What strengths, wins, and positive patterns emerge? What do they do well? What brings them energy?

(f) **Action Guide** — Concrete, specific next steps the user could take based on this self-knowledge. What should they do more of? Less of? What experiments to try?

---

## 2. Cognitive Models

(a) **Reverse Thinking (Charlie Munger)** — What would "inverting" their typical assumptions reveal? If they wanted to fail, what would they do? What does reverse thinking suggest they're missing?

(b) **Second-Order Thinking** — What are the likely consequences of consequences? What second-order effects might they be overlooking in their decisions?

(c) **Anti-Intuitive Insights** — What counterintuitive truths might apply to their situation? Where might their intuition lead them astray?

(d) **Major Contradictions (主要矛盾)** — In the Maoist sense: what is the primary contradiction in their life or thinking right now? What is the main thing that, if resolved, would unlock everything else?

(e) **Value Clarification (价值澄清)** — What values are implicit but unstated? What would explicit value clarification reveal? Where might values conflict?

---

## 3. Exploration Frameworks

(a) **The Soul Question** — What is the deeper question beneath their surface questions? What are they really asking?

(b) **Mind Topic Extend** — How could their current topics of interest extend into adjacent domains? What connections are they not yet making?

(c) **Resource Digging** — What internal resources (skills, experiences, knowledge) are underutilized? What could they mine from their own history?

(d) **Blind Spot Exploration (盲区探索)** — What might they be unable to see about themselves? What would a trusted outsider notice that they miss?

(e) **Friend's Perspective (朋友视角)** — If a close friend described them, what would they say? What would they encourage or caution?

(f) **Director's Perspective (导演视角)** — If viewing their life as a film, what's the arc? What's the central conflict? What would the director cut or emphasize?

(g) **The Question That Occurs Again and Again** — What question do they keep returning to? What unresolved inquiry haunts their notes?

---

## 4. Key Influences and Figures

(a) **Charlie Munger** — Mental models, latticework, inversion, multidisciplinary thinking. How do these show up (or could show up) in their approach?

(b) **Aristotle** — Virtue ethics, eudaimonia, the golden mean, practical wisdom (phronesis). What Aristotelian insights apply?

(c) **Seneca** — Stoicism, memento mori, control dichotomy, tranquility. What Stoic wisdom resonates with their situation?

(d) **Tasha Eurich** — Self-awareness (internal + external), the "cult of self-awareness." What would Eurich's framework reveal about their blind spots?

(e) **Fuli Flywheel (复利飞轮)** — Compound growth, flywheel effects. What small habits or investments could compound for them? What's their flywheel?

---

## Output Format

- Use markdown with clear ## and ### headings
- Use [[wikilinks]] when referencing specific notes (exact filename without .md)
- Be specific: cite evidence from the notes
- Be constructive: aim to empower, not judge
- If a section has insufficient data, say so and suggest what would help
- Write in second person ("you") where appropriate
- No YAML frontmatter — start directly with # AI Insight Report

"""
    if focus:
        focus_lower = focus.lower()
        if focus_lower in ("mindset", "core", "1"):
            base += "\n**Focus:** Emphasize Section 1 (Core Mindset and Analysis) only. Be thorough in that section; briefly note if other sections have relevant data.\n\n"
        elif focus_lower in ("cognitive", "models", "2"):
            base += "\n**Focus:** Emphasize Section 2 (Cognitive Models) only.\n\n"
        elif focus_lower in ("exploration", "frameworks", "3"):
            base += "\n**Focus:** Emphasize Section 3 (Exploration Frameworks) only.\n\n"
        elif focus_lower in ("influences", "figures", "4"):
            base += "\n**Focus:** Emphasize Section 4 (Key Influences and Figures) only.\n\n"
        else:
            base += f"\n**Focus:** Pay special attention to: {focus}\n\n"

    base += "Analyze the following vault content and produce the AI Insight Report.\n"
    return base


def main():
    parser = argparse.ArgumentParser(
        description="AI Insight - Gain self-knowledge from vault data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/ai_insight.py                    # Full report
  python3 _scripts/ai_insight.py --focus mindset   # Core mindset only
  python3 _scripts/ai_insight.py --days 180        # Deeper look (6 months)
  python3 _scripts/ai_insight.py --no-para         # Exclude Projects/Areas/Resources
  python3 _scripts/ai_insight.py --no-save         # Print only, don't save
""",
    )
    parser.add_argument(
        "--focus",
        type=str,
        default=None,
        help="Focus on one section: mindset, cognitive, exploration, influences",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Look back N days for dated notes (default: 90)",
    )
    parser.add_argument(
        "--no-atlas",
        action="store_true",
        help="Exclude Atlas notes",
    )
    parser.add_argument(
        "--no-maps",
        action="store_true",
        help="Exclude Maps (MOCs)",
    )
    parser.add_argument(
        "--no-inbox",
        action="store_true",
        help="Exclude Inbox notes",
    )
    parser.add_argument(
        "--no-para",
        action="store_true",
        help="Exclude Projects, Areas, Resources",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom output path",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Print to terminal only, do not save to vault",
    )
    args = parser.parse_args()

    if TRACKER:
        TRACKER.record_operation(
            script_name="ai_insight.py",
            operation_type="ai_insight",
            status="in_progress",
            metrics={"focus": args.focus, "days": args.days},
        )

    print("Collecting notes from vault...")
    notes = collect_notes(
        days=args.days,
        include_atlas=not args.no_atlas,
        include_maps=not args.no_maps,
        include_inbox=not args.no_inbox,
        include_para=not args.no_para,
    )

    if not notes:
        print("No notes found. Try increasing --days or including more directories.")
        return

    print(f"Found {len(notes)} notes:")
    by_source = {}
    for n in notes:
        by_source[n["source"]] = by_source.get(n["source"], 0) + 1
    for src, count in sorted(by_source.items()):
        print(f"  {src}: {count}")

    notes_text = "\n\n---\n\n".join(
        "SOURCE: [[{filename}]] ({source}, type: {type}, date: {date})\n\n{content}".format(**n)
        for n in notes
    )

    if len(notes_text) > 120000:
        notes_text = notes_text[:120000] + "\n\n[Additional notes truncated for length...]"

    prompt = build_insight_prompt(args.focus, notes_text)
    print("Generating AI Insight report...")
    report_body = summarize(notes_text, prompt)

    today = datetime.now().strftime("%Y-%m-%d")
    source_index = "\n".join(
        "- [[{}]] ({})".format(n["filename"], n["source"]) for n in notes[:40]
    )
    if len(notes) > 40:
        source_index += f"\n- ... and {len(notes) - 40} more"

    full_note = f"""# AI Insight Report
*Generated {today} from {len(notes)} notes*

---

{report_body}

---

## Notes Analyzed

{source_index}
"""

    if args.no_save:
        print("\n" + "=" * 60 + "\n")
        print(full_note)
        return

    if args.output:
        out_path = args.output
    else:
        out_path = f"Atlas/AI Insight - {today}.md"

    save_note(out_path, full_note)
    print(f"Done! AI Insight report saved to {out_path}.")

    if TRACKER:
        TRACKER.record_operation(
            script_name="ai_insight.py",
            operation_type="ai_insight",
            status="success",
            metrics={
                "focus": args.focus,
                "days": args.days,
                "notes_processed": len(notes),
                "output_file": out_path,
            },
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="ai_insight.py",
                operation_type="ai_insight",
                status="failed",
                metrics={"error": str(e)},
            )
        raise
