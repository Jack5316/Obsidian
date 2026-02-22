"""Monthly/quarterly system review orchestrator.

Runs L5 Review layer at extended cadence: reflect, evolve, insights, skill-grab.
Saves a dated review note to the vault.
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add parent for VAULT_PATH
sys.path.insert(0, str(Path(__file__).parent))
from config import save_note, VAULT_PATH


def run_script(script: str, args: list, cwd: Path) -> tuple[bool, str]:
    """Run a script and return (success, output)."""
    cmd = ["python3", f"_scripts/{script}"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            timeout=600,
        )
        out = (result.stdout or "") + (result.stderr or "")
        return result.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(
        description="Monthly or quarterly system review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/review_system.py --monthly
  python3 _scripts/review_system.py --quarterly --save
""",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--monthly",
        action="store_true",
        help="30-day review (default)",
    )
    group.add_argument(
        "--quarterly",
        action="store_true",
        help="90-day review",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save review note to vault",
    )
    args = parser.parse_args()

    cwd = VAULT_PATH
    days = 90 if args.quarterly else 30
    period = "quarterly" if args.quarterly else "monthly"

    print("=" * 60)
    print(f"System Review — {period.upper()} ({days}-day lookback)")
    print("=" * 60)

    results = []
    log_lines = [f"Review started: {datetime.now().isoformat()}", f"Period: {period} ({days} days)", ""]

    # 1. Self-reflection
    print("\n[1/4] Self-reflection...")
    ok, out = run_script("self_reflection.py", ["reflect", "--days", str(days), "--save"], cwd)
    results.append(("Self-reflection", ok, out[:500] if out else ""))
    log_lines.append(f"Self-reflection: {'OK' if ok else 'FAIL'}")
    print("✓" if ok else "✗")

    # 2. Self-evolution
    print("\n[2/4] Self-evolution...")
    ok, out = run_script("self_evolution.py", ["cycle", "--safe"], cwd)
    results.append(("Self-evolution", ok, out[:500] if out else ""))
    log_lines.append(f"Self-evolution: {'OK' if ok else 'FAIL'}")
    print("✓" if ok else "✗")

    # 3. Insight enhancement
    print("\n[3/4] Insight enhancement...")
    ok, out = run_script("insight_enhancement.py", ["cycle"], cwd)
    results.append(("Insight enhancement", ok, out[:500] if out else ""))
    log_lines.append(f"Insight enhancement: {'OK' if ok else 'FAIL'}")
    print("✓" if ok else "✗")

    # 4. Skill upgrade
    print("\n[4/4] Skill upgrade (skills.sh)...")
    ok, out = run_script("skill_grab.py", ["-s", "trending"], cwd)
    results.append(("Skill grab", ok, out[:500] if out else ""))
    log_lines.append(f"Skill grab: {'OK' if ok else 'FAIL'}")
    print("✓" if ok else "✗")

    # Summary
    success_count = sum(1 for _, ok, _ in results if ok)
    print("\n" + "=" * 60)
    print(f"Completed: {success_count}/4 steps")
    print("=" * 60)

    log_lines.append("")
    log_lines.append(f"Completed: {success_count}/4")
    for name, ok, _ in results:
        log_lines.append(f"  {name}: {'OK' if ok else 'FAIL'}")

    # Save log
    log_dir = VAULT_PATH / "_logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path.write_text("\n".join(log_lines), encoding="utf-8")
    print(f"\nLog: {log_path}")

    # Save review note
    if args.save:
        today = datetime.now().strftime("%Y-%m-%d")
        note = f"""# System Review — {period.capitalize()} ({today})

## Period
{days}-day lookback

## Steps Run
| Step | Status |
|------|--------|
"""
        for name, ok, _ in results:
            note += f"| {name} | {'✓' if ok else '✗'} |\n"

        note += """
## Manual Checklist
- [ ] Prune stale sources (arxiv_topics.txt, subreddits.txt, twitter_accounts.txt)
- [ ] Archive completed projects
- [ ] Update PARA structure
- [ ] Goodhart check: Are metrics still serving curiosity?

## Tags
- type/review
"""
        save_note(f"Sources/Review - {today}.md", note)
        print(f"Review note saved: Sources/Review - {today}.md")

    return 0 if success_count == 4 else 1


if __name__ == "__main__":
    sys.exit(main())
