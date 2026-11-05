"""Compare the final layout with the pre-move preservation records."""

import ast
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).resolve().parent


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    renames = read_json(AUDIT / "rename-map.json")

    def relocated(path: str) -> str:
        for old, new in renames.items():
            if path == old or path.startswith(old + "/"):
                return new + path[len(old):]
        return path

    assets = read_json(AUDIT / "assets-before.json")
    asset_failures = [old for old, sha in assets.items()
                      if not (ROOT / relocated(old)).is_file()
                      or digest(ROOT / relocated(old)) != sha]
    sources = read_json(AUDIT / "project-source-before.json")
    source_changes = [relocated(old) for old, sha in sources.items()
                      if digest(ROOT / relocated(old)) != sha]
    expected_changes = ["projects/08-qr-code-studio/qr_studio.py",
                        "projects/09-expense-tracker-dashboard/gui.py"]
    assert sorted(source_changes) == sorted(expected_changes), source_changes
    visual_sources = [old for old in sources if "/visual-art-lab/" in old]
    assert all(digest(ROOT / relocated(old)) == sources[old] for old in visual_sources)
    assert not asset_failures, asset_failures
    licenses = read_json(AUDIT / "license-files-before.json")
    license_path = "research/reference-repositories/python-starter-lab/LICENSE"
    assert digest(ROOT / license_path) == licenses[license_path]
    original_audit = (AUDIT / "before/research/license-audit.md").read_text(encoding="utf-8")
    expected_audit = original_audit.replace("`spiral-ink/", "`06-spiral-ink/")
    assert (ROOT / "research/license-audit.md").read_text(encoding="utf-8") == expected_audit
    original_sources = read_json(AUDIT / "before/research/source-snapshots.json")
    current_sources = read_json(ROOT / "research/source-snapshots.json")
    for source in original_sources["sources"]:
        source["local_path"] = relocated(source["local_path"])
    assert current_sources == original_sources

    python_files = [*ROOT.glob("projects/**/*.py"), *ROOT.glob("projects/**/*.pyw"),
                    *ROOT.glob("scripts/*.py")]
    python_files = [path for path in python_files if "__pycache__" not in path.parts]
    for path in python_files:
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path), feature_version=(3, 12))

    stale_references = []
    checked = 0
    ignored = {".venv", ".git", "__pycache__", ".pytest_cache", ".ruff_cache",
               "reference-repositories", "folder-renames", "outputs", "runtime-checks"}
    suffixes = {".md", ".py", ".pyw", ".json", ".toml", ".yml", ".yaml", ".txt"}
    for path in ROOT.rglob("*"):
        if set(path.relative_to(ROOT).parts) & ignored or not path.is_file() or path.suffix not in suffixes:
            continue
        text = path.read_text(encoding="utf-8-sig")
        checked += 1
        for old in renames:
            if old in text or old.replace("/", "\\") in text:
                stale_references.append(str(path.relative_to(ROOT)))
    assert not stale_references, stale_references
    assert all(not (ROOT / old).exists() and (ROOT / new).is_dir()
               for old, new in renames.items())

    # Inventory local generated files without inferring anything about Git tracking.
    groups = {".venv": [], "__pycache__": [], "runtime_diagnostics": [], "other_caches": []}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if "reference-repositories" in rel.parts:
            continue
        if ".venv" in rel.parts:
            groups[".venv"].append(rel.as_posix())
        elif "__pycache__" in rel.parts:
            groups["__pycache__"].append(rel.as_posix())
        elif set(rel.parts) & {"outputs", "runtime-outputs", "runtime-checks", "demo-fixtures", "browser-profile"} or path.suffix == ".log":
            groups["runtime_diagnostics"].append(rel.as_posix())
        elif set(rel.parts) & {".pytest_cache", ".ruff_cache", "htmlcov"} or re.match(r"\.coverage($|\.)", path.name):
            groups["other_caches"].append(rel.as_posix())
    inventory = {"tracked_status": "Unknown: no root Git index; nothing removed",
                 "counts": {name: len(paths) for name, paths in groups.items()},
                 "examples": {name: sorted(paths)[:10] for name, paths in groups.items()}}
    (AUDIT / "generated-file-inventory.json").write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    report = {"protected_assets": len(assets), "asset_failures": asset_failures,
              "project_source_files": len(sources), "unchanged_project_source_files": len(sources) - len(source_changes),
              "changed_project_source_files": source_changes,
              "unchanged_visual_python_sources": len(visual_sources),
              "license_file_unchanged": license_path,
              "license_audit_only_changed_paths": True, "source_snapshot_metadata_preserved": True,
              "python_312_grammar_files": len(python_files), "active_text_files_checked": checked,
              "stale_path_references": stale_references, "all_six_moves_verified": True}
    (AUDIT / "integrity-results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
