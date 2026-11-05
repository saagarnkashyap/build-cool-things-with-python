"""Print a source-focused repository tree, optionally saving it with --write."""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "outputs",
            "runtime-outputs", "reference-repositories", "runtime-checks", "demo-fixtures", "browser-profile"}


def source_tree() -> str:
    lines = ["Source-focused repository map; environments, caches, and runtime diagnostics omitted.",
             "Regenerate: python scripts/show_project_structure.py --write folder-structure.txt", "",
             ROOT.name + "/"]

    def visit(folder: Path, prefix: str = "") -> None:
        entries = [path for path in folder.iterdir() if path.name not in EXCLUDED
                   and path.suffix not in (".log", ".pyc", ".pyo")
                   and not (path.parent.name == "verification" and
                            (path.name.endswith("-checks.json") or path.name in ("test-results.json", "environment.json")))]
        entries.sort(key=lambda path: (not path.is_dir(), path.name.casefold()))
        for index, path in enumerate(entries):
            last = index == len(entries) - 1
            suffix = "/" if path.is_dir() else ""
            if path.is_dir() and path.name == "folder-renames":
                suffix += " (audit records)"
            lines.append(prefix + ("`-- " if last else "|-- ") + path.name + suffix)
            if path.is_dir() and path.name != "folder-renames":
                visit(path, prefix + ("    " if last else "|   "))

    visit(ROOT)
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="Save the source map to this text file")
    args = parser.parse_args()
    text = source_tree()
    if args.write:
        args.write.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
