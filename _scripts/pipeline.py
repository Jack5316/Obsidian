"""Pipeline - Combine skills into sequential workflows.

Run multiple skills in sequence, use named pipelines, or pick random skills.
"""

import argparse
import json
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Vault root
VAULT_PATH = Path(__file__).resolve().parent.parent
SKILLS_JSON = VAULT_PATH / ".claude" / "skills.json"
PIPELINES_JSON = VAULT_PATH / "_config" / "pipelines.json"


def load_skills() -> dict:
    """Load skills from skills.json. Returns {name: {description, commands}}."""
    if not SKILLS_JSON.exists():
        print(f"Error: {SKILLS_JSON} not found.")
        sys.exit(1)
    data = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    return data.get("skills", {})


def load_pipelines() -> dict:
    """Load named pipelines from pipelines.json."""
    if not PIPELINES_JSON.exists():
        return {}
    try:
        return json.loads(PIPELINES_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_pipelines(pipelines: dict) -> None:
    """Save named pipelines to pipelines.json."""
    PIPELINES_JSON.parent.mkdir(parents=True, exist_ok=True)
    PIPELINES_JSON.write_text(json.dumps(pipelines, indent=2, ensure_ascii=False), encoding="utf-8")


def get_runnable_skills(skills: dict) -> dict:
    """Return skills that have non-empty commands."""
    return {k: v for k, v in skills.items() if v.get("commands") and len(v["commands"]) > 0}


def run_skill(name: str, commands: list, verbose: bool) -> dict:
    """Run a skill's commands. Returns {name, success, duration, error}."""
    start = time.time()
    result = {"name": name, "success": False, "duration": 0, "error": None}

    for cmd in commands:
        # Parse command: "python3 _scripts/xxx.py" or "python3 _scripts/xxx.py --arg"
        parts = cmd.split()
        if not parts:
            continue

        try:
            proc = subprocess.run(
                parts,
                cwd=str(VAULT_PATH),
                capture_output=not verbose,
                text=True,
            )
            if proc.returncode != 0:
                result["error"] = proc.stderr or f"Exit code {proc.returncode}"
                break
        except Exception as e:
            result["error"] = str(e)
            break
    else:
        result["success"] = True

    result["duration"] = time.time() - start
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline - Combine skills into sequential workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pipeline arxiv hn reddit              # Run arxiv, then hn, then reddit
  pipeline --run daily-curation        # Run named pipeline
  pipeline --random 3                  # Run 3 random skills
  pipeline --list                      # List all skills
  pipeline --list-pipelines            # List named pipelines
  pipeline --save daily arxiv hn news # Save as named pipeline
""",
    )
    parser.add_argument(
        "skills",
        nargs="*",
        help="Skill names to run in sequence",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all runnable skills",
    )
    parser.add_argument(
        "--list-pipelines",
        action="store_true",
        help="List named pipelines",
    )
    parser.add_argument(
        "--run", "-r",
        type=str,
        metavar="NAME",
        help="Run a named pipeline",
    )
    parser.add_argument(
        "--random", "-R",
        type=int,
        metavar="N",
        help="Run N random skills",
    )
    parser.add_argument(
        "--save", "-s",
        type=str,
        metavar="NAME",
        help="Save current skill list as named pipeline",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Stream each skill's output to terminal",
    )
    parser.add_argument(
        "--no-fail-stop",
        action="store_true",
        help="Continue pipeline even if a skill fails",
    )
    args = parser.parse_args()

    skills = load_skills()
    runnable = get_runnable_skills(skills)

    # List skills
    if args.list:
        print("Runnable skills:")
        print("-" * 50)
        for name, meta in sorted(runnable.items()):
            desc = (meta.get("description", "") or "")[:60]
            print(f"  {name:<20} {desc}")
        return

    # List pipelines
    if args.list_pipelines:
        pipelines = load_pipelines()
        if not pipelines:
            print("No named pipelines. Create with: pipeline --save NAME skill1 skill2 ...")
            return
        print("Named pipelines:")
        print("-" * 50)
        for name, steps in pipelines.items():
            print(f"  {name}: {' → '.join(steps)}")
        return

    # Save pipeline
    if args.save:
        if not args.skills:
            print("Error: Provide skill names to save. E.g. pipeline --save daily arxiv hn news")
            sys.exit(1)
        pipelines = load_pipelines()
        pipelines[args.save] = args.skills
        save_pipelines(pipelines)
        print(f"Saved pipeline '{args.save}': {' → '.join(args.skills)}")
        return

    # Determine which skills to run
    to_run = []

    if args.run:
        pipelines = load_pipelines()
        if args.run not in pipelines:
            print(f"Error: Pipeline '{args.run}' not found. Use --list-pipelines to see available.")
            sys.exit(1)
        to_run = pipelines[args.run]
    elif args.random is not None:
        if args.random < 1:
            print("Error: --random N requires N >= 1")
            sys.exit(1)
        names = list(runnable.keys())
        if not names:
            print("No runnable skills found.")
            sys.exit(1)
        to_run = random.sample(names, min(args.random, len(names)))
    elif args.skills:
        to_run = args.skills
    else:
        parser.print_help()
        return

    # Validate all skills exist and are runnable
    invalid = [s for s in to_run if s not in runnable]
    if invalid:
        print(f"Error: Unknown or non-runnable skills: {invalid}")
        print("Use --list to see available skills.")
        sys.exit(1)

    # Run pipeline
    print("=" * 60)
    print("Pipeline")
    print("=" * 60)
    print(f"Skills: {' → '.join(to_run)}")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []
    for i, name in enumerate(to_run, 1):
        meta = runnable[name]
        cmds = meta.get("commands", [])
        print(f"[{i}/{len(to_run)}] Running: {name}")
        result = run_skill(name, cmds, args.verbose)
        results.append(result)

        if result["success"]:
            print(f"  ✓ Done ({result['duration']:.1f}s)")
        else:
            print(f"  ✗ Failed: {result['error']}")
            if not args.no_fail_stop:
                print("\nPipeline stopped (use --no-fail-stop to continue on failure)")
                break

    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    success = sum(1 for r in results if r["success"])
    total = len(results)
    duration = sum(r["duration"] for r in results)
    print(f"  Completed: {success}/{total}")
    print(f"  Total time: {duration:.1f}s")
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"  {status} {r['name']} ({r['duration']:.1f}s)")


if __name__ == "__main__":
    main()
