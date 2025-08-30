#!/usr/bin/env python3
"""Run all crawler scripts and save their outputs.

This utility searches the repository for crawler scripts and executes
each of them, storing combined stdout and stderr logs in a dedicated
``results`` directory. Non-crawler utility modules are skipped.

Use the ``--dry-run`` flag to see which scripts would be executed without
actually running them.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
from typing import Iterable

# Directory containing this script
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
# Destination for output logs
RESULT_DIR = SCRIPT_DIR / "results"
# Files that should not be executed as crawlers
EXCLUDE = {
    "crawler_base.py",
    "constants.py",
    "sessions.py",
    "run_all_crawlers.py",
}


def discover_scripts(directory: pathlib.Path) -> Iterable[pathlib.Path]:
    """Yield runnable crawler scripts from ``directory``."""
    for script in sorted(directory.glob("*.py")):
        if script.name in EXCLUDE:
            continue
        yield script


def run_script(script: pathlib.Path, dry_run: bool = False) -> int:
    """Run ``script`` and write its output to a log file.

    Returns the subprocess' return code.
    """
    log_file = RESULT_DIR / f"{script.stem}.log"
    if dry_run:
        print(f"[DRY RUN] Would execute {script.name} -> {log_file}")
        return 0
    with log_file.open("w") as fh:
        completed = subprocess.run(
            ["python", str(script)],
            stdout=fh,
            stderr=subprocess.STDOUT,
            cwd=SCRIPT_DIR,
        )
        return completed.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List scripts without executing them",
    )
    args = parser.parse_args()

    RESULT_DIR.mkdir(exist_ok=True)

    for script in discover_scripts(SCRIPT_DIR):
        code = run_script(script, dry_run=args.dry_run)
        if code != 0:
            print(f"{script.name} exited with status {code}")


if __name__ == "__main__":
    main()
