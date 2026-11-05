"""Run every available chapter unittest suite in an isolated process."""

from pathlib import Path
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures = 0
    results = []
    reports = ROOT / "research/verification"
    reports.mkdir(parents=True, exist_ok=True)
    projects = [*(ROOT / "projects").glob("[0-9][0-9]-*"),
                *(ROOT / "projects/visual-art-lab").glob("[0-9][0-9]-*")]
    without_suites = []
    for project in sorted(projects, key=lambda path: path.name):
        if not (project / "tests").is_dir():
            without_suites.append(project.name)
            continue
        print(f"\n--- {project.name} ---", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=project,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=dict(os.environ, PYTHONUTF8="1"),
            timeout=120,
        )
        output = result.stdout + result.stderr
        print(output, end="", flush=True)
        (reports / f"tests-{project.name}.log").write_text(output, encoding="utf-8")
        match = re.search(r"Ran (\d+) tests?", output)
        count = int(match.group(1)) if match else 0
        failed = result.returncode != 0 or count == 0
        failures += failed
        results.append({"project": project.name, "tests": count,
                        "status": "failed" if failed else "passed", "exit_code": result.returncode})
    summary = {"python": sys.version.split()[0], "projects": results,
               "total_tests": sum(item["tests"] for item in results), "failed_projects": failures,
               "projects_without_unit_suites": without_suites}
    (reports / "test-results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"\n{summary['total_tests']} tests across {len(results)} projects; {failures} failed project(s).")
    return int(failures > 0)


if __name__ == "__main__":
    raise SystemExit(main())
