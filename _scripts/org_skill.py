"""Skill wrapper to run all available scripts and reflect on the process."""

import argparse
import json
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

VAULT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_JSON = VAULT_ROOT / ".claude" / "skills.json"


def run_script(script_name: str, description: str, verbose: bool = False) -> dict:
    """Run a single script and return execution details."""
    start_time = time.time()
    result = {
        "script": script_name,
        "description": description,
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "success": False,
        "output": "",
        "error": "",
        "duration": 0
    }

    try:
        print(f"\n=== Running {script_name} ===")
        print(f"Description: {description}")

        # Run the script - stream output when verbose, else capture for logs
        process = subprocess.run(
            ["python3", f"_scripts/{script_name}"],
            capture_output=not verbose,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        if verbose:
            result["output"] = "(streamed to terminal)"
            result["error"] = "(streamed to terminal)" if process.returncode != 0 else ""
        else:
            result["output"] = process.stdout
            result["error"] = process.stderr

        if process.returncode == 0:
            result["success"] = True
            print(f"✓ Success")
        else:
            print(f"✗ Failed (Exit code: {process.returncode})")
            if not verbose and process.stderr:
                print(f"Error: {process.stderr}")

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        print(f"✗ Failed: {e}")

    result["duration"] = time.time() - start_time
    result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return result


def main():
    """Skill entry point to run all scripts and reflect on the process."""
    parser = argparse.ArgumentParser(
        description="Organization Skill - Run all available scripts and reflect",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This skill runs all automation scripts in your Obsidian vault and provides
a reflection on the execution process.

Examples:
  /skill org                    # Run all scripts and reflect
  /skill org --skip arxiv_digest.py,twitter_capture.py  # Skip specific scripts
  /skill org --list             # List available scripts
  /skill org-daily              # Run daily scripts
  /skill org-weekly             # Run weekly scripts
  /skill org-status             # Check execution status
  /skill org-logs               # View recent logs
"""
    )

    parser.add_argument(
        "-s", "--skip",
        help="Comma-separated list of scripts to skip"
    )

    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all available scripts and exit"
    )

    parser.add_argument(
        "-d", "--daily",
        action="store_true",
        help="Run only daily automation scripts"
    )

    parser.add_argument(
        "-w", "--weekly",
        action="store_true",
        help="Run only weekly automation scripts"
    )

    parser.add_argument(
        "-st", "--status",
        action="store_true",
        help="Check script execution status and recent runs"
    )

    parser.add_argument(
        "-lo", "--logs",
        action="store_true",
        help="View recent script execution logs"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Stream script output to terminal (default: only show success/fail)"
    )

    args = parser.parse_args()

    # Load scripts from skills.json (full PAI skill list) or fallback to daily scripts
    def load_scripts():
        if SKILLS_JSON.exists():
            try:
                data = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
                skills = data.get("skills", {})
                result = []
                for skill_name, meta in sorted(skills.items()):
                    cmds = meta.get("commands") or []
                    if not cmds:
                        continue
                    # Extract script filename from command (e.g. "python3 _scripts/arxiv_digest.py" -> arxiv_digest.py)
                    cmd = cmds[0]
                    script_file = cmd.split("_scripts/")[-1].split()[0] if "_scripts/" in cmd else None
                    if not script_file or not script_file.endswith(".py"):
                        continue
                    result.append({
                        "name": script_file,  # for run_script
                        "skill": skill_name,  # for --list display
                        "desc": (meta.get("description") or "")[:80],
                    })
                if result:
                    return result
            except (json.JSONDecodeError, OSError):
                pass
        # Fallback: daily org scripts
        return [
            {"name": "arxiv_digest.py", "skill": "arxiv", "desc": "ArXiv paper curation and summarization"},
            {"name": "hn_newsletter.py", "skill": "hn", "desc": "Hacker News newsletter creation"},
            {"name": "reddit_digest.py", "skill": "reddit", "desc": "Reddit content digestion and summarization"},
            {"name": "weekly_synthesis.py", "skill": "weekly", "desc": "Weekly content synthesis"},
            {"name": "tophub_news_simple.py", "skill": "news", "desc": "Simple TopHub news scraping"},
            {"name": "twitter_capture.py", "skill": "twitter", "desc": "Twitter content capture and summarization"},
        ]

    scripts = load_scripts()

    # List available scripts if requested
    if args.list:
        print("PAI Skills (from .claude/skills.json):")
        print("=" * 60)
        for s in scripts:
            print(f"  {s.get('skill', s['name']):<28} - {s['desc']}")
        print(f"\nTotal: {len(scripts)} skills")
        return 0

    # Check script execution status
    if args.status:
        print("Script Execution Status")
        print("======================")

        log_dir = Path(__file__).parent.parent / "_logs"
        if not log_dir.exists():
            print("No logs found - no scripts have been executed yet.")
            return 0

        log_files = list(log_dir.glob("org_skill_*.log"))
        log_files.sort(reverse=True, key=lambda x: x.stat().st_mtime)

        if not log_files:
            print("No org skill execution logs found.")
            return 0

        print(f"Total executions: {len(log_files)}")
        print("\nRecent runs:")
        print("------------")

        for i, log_file in enumerate(log_files[:5]):  # Show last 5 runs
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")

            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    log_content = f.read()

                # Extract statistics from log
                total = 0
                successful = 0
                failed = 0

                if "Total Scripts:" in log_content:
                    total = int(log_content.split("Total Scripts:")[1].split("\n")[0].strip())
                if "Successful:" in log_content:
                    successful = int(log_content.split("Successful:")[1].split("\n")[0].strip())
                if "Failed:" in log_content:
                    failed = int(log_content.split("Failed:")[1].split("\n")[0].strip())

                print(f"{i+1}. {log_file.name}")
                print(f"   Date: {mtime}")
                print(f"   Scripts: {total}, Success: {successful}, Failed: {failed}")

            except Exception as e:
                print(f"{i+1}. {log_file.name}")
                print(f"   Error reading log: {e}")

        return 0

    # View recent logs
    if args.logs:
        log_dir = Path(__file__).parent.parent / "_logs"
        if not log_dir.exists():
            print("No logs directory found.")
            return 0

        log_files = list(log_dir.glob("org_skill_*.log"))
        log_files.sort(reverse=True, key=lambda x: x.stat().st_mtime)

        if not log_files:
            print("No org skill execution logs found.")
            return 0

        # Show content of most recent log
        print(f"Showing log: {log_files[0].name}")
        print("=" * 60)

        try:
            with open(log_files[0], "r", encoding="utf-8") as f:
                print(f.read())
        except Exception as e:
            print(f"Error reading log: {e}")

        return 0

    # Determine which scripts to run based on command
    scripts_to_run = scripts
    if args.daily:
        daily_scripts = [
            "arxiv_digest.py",
            "hn_newsletter.py",
            "reddit_digest.py",
            "tophub_news_simple.py",
            "twitter_capture.py"
        ]
        scripts_to_run = [s for s in scripts if s["name"] in daily_scripts]
        print("Running daily automation scripts only")
    elif args.weekly:
        weekly_scripts = [
            "weekly_synthesis.py"
            # The following scripts require parameters and are disabled:
            # "self_reflection.py",
            # "self_evolution.py"
        ]
        scripts_to_run = [s for s in scripts if s["name"] in weekly_scripts]
        print("Running weekly automation scripts only")

    # Determine scripts to skip
    skip_scripts = []
    if args.skip:
        skip_scripts = [s.strip() for s in args.skip.split(",") if s.strip()]
        print(f"\nSkipping scripts: {', '.join(skip_scripts)}")

    # Run selected scripts
    print("=" * 60)
    if args.daily:
        print("Organization Skill - Running daily automation scripts")
    elif args.weekly:
        print("Organization Skill - Running weekly automation scripts")
    else:
        print("Organization Skill - Running all automation scripts")
    print("=" * 60)

    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total scripts to run: {len([s for s in scripts_to_run if s['name'] not in skip_scripts])}")

    execution_results = []
    verbose = getattr(args, "verbose", False)

    if verbose:
        # Run sequentially to stream output clearly
        for script in scripts_to_run:
            if script["name"] in skip_scripts:
                print(f"\n=== Skipping {script['name']} ===")
                continue
            result = run_script(script["name"], script["desc"], verbose=True)
            execution_results.append(result)
    else:
        # Run scripts in parallel
        with ThreadPoolExecutor(max_workers=len(scripts_to_run)) as executor:
            future_to_script = {}
            for script in scripts_to_run:
                if script["name"] in skip_scripts:
                    print(f"\n=== Skipping {script['name']} ===")
                    continue
                future = executor.submit(run_script, script["name"], script["desc"], False)
                future_to_script[future] = script

            for future in as_completed(future_to_script):
                script = future_to_script[future]
                try:
                    result = future.result()
                    execution_results.append(result)
                except Exception as e:
                    print(f"\n=== Failed to run {script['name']} ===")
                    print(f"Error: {e}")
                    result = {
                        "script": script["name"],
                        "description": script["desc"],
                        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "success": False,
                        "output": "",
                        "error": str(e),
                        "duration": 0,
                        "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    execution_results.append(result)

    # Run daily synthesis after daily curation (reads their output)
    if args.daily:
        successful_count = sum(1 for r in execution_results if r["success"])
        if successful_count >= 2:
            print("\n=== Running daily cross-domain synthesis (sequential) ===")
            synth_result = run_script("daily_synthesis.py", "Daily cross-domain synthesis", verbose=verbose)
            execution_results.append(synth_result)
        else:
            print("\nSkipping daily synthesis (need >=2 successful scripts, got {})".format(successful_count))

    # Generate reflection
    print("\n" + "=" * 60)
    print("Execution Summary & Reflection")
    print("=" * 60)

    # Statistics
    total_scripts = len(scripts_to_run)
    skipped_scripts = len([s for s in scripts_to_run if s["name"] in skip_scripts])
    run_scripts = len(execution_results)
    successful_scripts = sum(1 for r in execution_results if r["success"])
    failed_scripts = run_scripts - successful_scripts
    total_duration = sum(r["duration"] for r in execution_results)

    print(f"\nStatistics:")
    print(f"  Total scripts:     {total_scripts}")
    print(f"  Skipped:           {skipped_scripts}")
    print(f"  Ran:               {run_scripts}")
    print(f"  Successful:        {successful_scripts}")
    print(f"  Failed:            {failed_scripts}")
    print(f"  Total duration:    {total_duration:.2f} seconds")

    if successful_scripts > 0:
        avg_duration = total_duration / successful_scripts
        print(f"  Avg duration/script: {avg_duration:.2f} seconds")

    # Detailed results
    print("\nExecution Details:")
    print("------------------")
    for result in execution_results:
        status = "✓" if result["success"] else "✗"
        duration = f"{result['duration']:.2f}s"
        print(f"{status} {result['script']:<25} {duration:<8}")
        if not result["success"] and result["error"]:
            print(f"  Error: {result['error']}")

    # Reflection
    print("\nReflection:")
    print("-----------")

    if failed_scripts == 0:
        print("All scripts executed successfully! Your Obsidian vault is fully organized and updated.")
    else:
        print(f"{failed_scripts} out of {run_scripts} scripts failed. Check the errors above.")

    if run_scripts == 0:
        print("No scripts were executed. All were skipped.")

    print("\nKey observations:")
    if successful_scripts > 0:
        print(f"- {successful_scripts} scripts successfully completed their tasks")

    if failed_scripts > 0:
        print(f"- {failed_scripts} scripts encountered errors (check logs for details)")

    if skipped_scripts > 0:
        print(f"- {skipped_scripts} scripts were explicitly skipped")

    # Save execution log
    log_file = Path(__file__).parent.parent / "_logs" / f"org_skill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_content = []
    log_content.append("=" * 60)
    log_content.append("ORGANIZATION SKILL EXECUTION LOG")
    log_content.append("=" * 60)
    log_content.append(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_content.append(f"Total Scripts: {total_scripts}")
    log_content.append(f"Skipped: {skipped_scripts}")
    log_content.append(f"Ran: {run_scripts}")
    log_content.append(f"Successful: {successful_scripts}")
    log_content.append(f"Failed: {failed_scripts}")
    log_content.append(f"Total Duration: {total_duration:.2f} seconds")
    log_content.append("")

    log_content.append("DETAILED EXECUTION RESULTS")
    log_content.append("--------------------------")
    for result in execution_results:
        log_content.append("")
        log_content.append(f"Script: {result['script']}")
        log_content.append(f"Description: {result['description']}")
        log_content.append(f"Start Time: {result['start_time']}")
        log_content.append(f"End Time: {result['end_time']}")
        log_content.append(f"Duration: {result['duration']:.2f} seconds")
        log_content.append(f"Status: {'SUCCESS' if result['success'] else 'FAILED'}")
        if result['output']:
            log_content.append("Output:")
            log_content.append(result['output'])
        if result['error']:
            log_content.append("Error:")
            log_content.append(result['error'])
        log_content.append("-" * 40)

    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_content))

    print(f"\nLog file saved to: {log_file}")

    # Determine return code based on success rate
    return 0 if failed_scripts == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
