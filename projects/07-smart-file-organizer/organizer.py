"""Preview shallow file moves, journal progress, and undo without overwriting."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
from uuid import uuid4

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"},
    "Documents": {".txt", ".pdf", ".md", ".docx", ".csv"},
    "Audio": {".mp3", ".wav", ".flac"},
    "Video": {".mp4", ".mov", ".mkv"},
    "Archives": {".zip", ".tar", ".gz"},
    "Code": {".py", ".js", ".html", ".css", ".json"},
}


def fingerprint(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def category_for(path: Path) -> str:
    return next((name for name, extensions in CATEGORIES.items()
                 if path.suffix.lower() in extensions), "Other")


def safe_path(root: Path, relative: str) -> Path:
    """Reject absolute/traversing paths and symlinks in every existing component."""
    fragment = Path(relative)
    if fragment.is_absolute() or not fragment.parts or any(part in ("..", ".") for part in fragment.parts):
        raise ValueError("Manifest paths must stay inside the selected folder.")
    current = root
    for part in fragment.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Symlinks are not followed: {current.name}")
    if not current.resolve().is_relative_to(root):
        raise ValueError("A path escapes the selected folder.")
    return current


def plan_moves(folder: Path) -> list[dict]:
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Select a real directory, not a symlink.")
    root = folder.resolve()
    planned = []
    reserved = set()
    for source in sorted(root.iterdir(), key=lambda path: path.name.casefold()):
        if source.is_symlink() or not source.is_file() or source.name.startswith("."):
            continue
        category = category_for(source)
        target = safe_path(root, f"{category}/{source.name}")
        number = 2
        while target.exists() or target in reserved:
            target = safe_path(root, f"{category}/{source.stem} ({number}){source.suffix}")
            number += 1
        reserved.add(target)
        planned.append({"source": source.name, "destination": target.relative_to(root).as_posix(),
                        "sha256": fingerprint(source), "status": "planned"})
    return planned


def write_manifest(path: Path, manifest: dict) -> None:
    """Replace only our own manifest, never an input file."""
    temporary = path.with_name(f".{uuid4().hex}.tmp")
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def move_file(source: Path, destination: Path, digest: str) -> None:
    """Recheck immediately before a move; collisions always stop the operation."""
    if not source.is_file() or source.is_symlink() or fingerprint(source) != digest:
        raise ValueError(f"Input changed or disappeared: {source.name}")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Destination already exists: {destination.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also prevents a collision that occurs after the check.
    # Leave partial copies for inspection if copying fails; keep the original.
    with source.open("rb") as incoming, destination.open("xb") as outgoing:
        shutil.copyfileobj(incoming, outgoing)
        outgoing.flush()
        os.fsync(outgoing.fileno())
    shutil.copystat(source, destination, follow_symlinks=False)
    if fingerprint(destination) != digest or fingerprint(source) != digest:
        raise ValueError("Content changed during transfer; both copies were retained.")
    source.unlink()  # Complete a verified move; never discard the only copy.


def apply_moves(folder: Path, plan: list[dict]) -> tuple[Path, list[str]]:
    """Save the journal before moving anything. Errors leave recovery information."""
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Select a real directory.")
    root = folder.resolve()
    # Rebuild instead of trusting a caller-supplied or stale preview.
    if plan != plan_moves(root):
        raise ValueError("The folder changed after preview. Preview it again.")
    state = safe_path(root, ".organizer/manifests")
    state.mkdir(parents=True, exist_ok=True)
    lock = safe_path(root, ".organizer/active.lock")
    try:
        lock_stream = lock.open("x")
    except FileExistsError:
        raise ValueError("Another run or interrupted run holds .organizer/active.lock.") from None
    manifest_path = state / f"{uuid4().hex}.json"
    manifest = {"version": 1, "root": str(root), "created": datetime.now(timezone.utc).isoformat(),
                "entries": [dict(entry) for entry in plan]}
    errors = []
    try:
        write_manifest(manifest_path, manifest)
        for entry in manifest["entries"]:
            entry["status"] = "pending"
            write_manifest(manifest_path, manifest)
            try:
                source = safe_path(root, entry["source"])
                target = safe_path(root, entry["destination"])
                move_file(source, target, entry["sha256"])
                entry["status"] = "moved"
            except (OSError, ValueError) as exc:
                entry["status"] = "failed"
                errors.append(f"{entry['source']}: {exc}")
            write_manifest(manifest_path, manifest)
    finally:
        lock_stream.close()
        lock.unlink()  # Only the tool-created lock; no user documents are deleted.
    return manifest_path, errors


def undo_moves(manifest_path: Path, *, apply: bool = False) -> list[dict]:
    manifest_path = manifest_path.absolute()
    root = manifest_path.parent.parent.parent.resolve()
    if manifest_path.parent.name != "manifests" or manifest_path.parent.parent.name != ".organizer":
        raise ValueError("Use a manifest inside the organized folder's .organizer/manifests/.")
    safe_path(root, manifest_path.relative_to(root).as_posix())
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("version") != 1 or manifest.get("root") != str(root):
        raise ValueError("Manifest version or root does not match its location.")
    if safe_path(root, ".organizer/active.lock").exists():
        raise ValueError("An organizer run is active; undo must wait.")
    candidates = []
    seen = set()
    for entry in manifest["entries"]:
        source_name, destination_name = entry["source"], entry["destination"]
        if len(Path(source_name).parts) != 1 or Path(destination_name).parts[0] not in {*CATEGORIES, "Other"}:
            raise ValueError("Unexpected manifest path layout.")
        source = safe_path(root, source_name)
        target = safe_path(root, destination_name)
        if source in seen:
            raise ValueError("Duplicate source in manifest.")
        seen.add(source)
        if entry["status"] not in ("moved", "pending", "undo_pending"):
            continue
        if source.is_file() and not target.exists() and fingerprint(source) == entry["sha256"]:
            continue  # Already restored, or a pending move never happened.
        if source.exists() or source.is_symlink():
            raise FileExistsError(f"Undo would overwrite {source.name}; move it aside first.")
        if not target.is_file() or fingerprint(target) != entry["sha256"]:
            raise ValueError(f"Organized file changed or is missing: {destination_name}")
        candidates.append(entry)
    # Validate the entire undo before moving any files back.
    if apply:
        lock = safe_path(root, ".organizer/active.lock")
        stream = lock.open("x")
        try:
            for entry in candidates:
                entry["status"] = "undo_pending"
                write_manifest(manifest_path, manifest)
                move_file(safe_path(root, entry["destination"]), safe_path(root, entry["source"]), entry["sha256"])
                entry["status"] = "undone"
                write_manifest(manifest_path, manifest)
        finally:
            stream.close()
            lock.unlink()
    return candidates
