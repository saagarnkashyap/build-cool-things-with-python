"""Run the imported programs without modifying their source snapshots.

Run from the repository root with ``python scripts/check_visual_art_lab.py``.
Results, logs, exports, and window captures go to research/runtime-checks/.
GUI checks require a desktop display. Each child process has a timeout.
"""

from __future__ import annotations

import argparse
from collections import Counter
import gc
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "runtime-checks"
SCRIPTS = {
    "bloomcraft": ROOT / "projects/visual-art-lab/04-bloomcraft/flow.py",
    "heartglow": ROOT / "projects/visual-art-lab/05-heartglow/love.py",
    "rockstar": ROOT / "projects/visual-art-lab/06-spiral-ink/pic1.py",
    "lilies": ROOT / "projects/visual-art-lab/06-spiral-ink/pic2.py",
    "water-lily": ROOT / "projects/visual-art-lab/06-spiral-ink/spiral_art.py",
}


def check_gui(name: str) -> None:
    """Run the real entry point and observe its Tk event loop until completion."""
    import tkinter as tk
    from PIL import ImageGrab, ImageTk

    script = SCRIPTS[name]
    namespace = {"__name__": "__main__", "__file__": str(script)}
    errors: list[str] = []
    observations: dict[str, object] = {}
    original_loop = tk.Tk.mainloop

    def callback_error(self, kind, value, tb):
        errors.append("".join(traceback.format_exception(kind, value, tb)))

    def observed_loop(window, *args, **kwargs):
        started = time.monotonic()
        finished_at = None
        app = None
        app_class = namespace.get("App") or getattr(sys.modules.get("spiral_art"), "App", None)
        if app_class is not None:
            app = next(obj for obj in gc.get_objects() if isinstance(obj, app_class))

        def observe():
            nonlocal finished_at
            try:
                elapsed = time.monotonic() - started
                if errors:
                    window.destroy()
                    return
                if name == "heartglow":
                    done = not namespace["spawning"] and not namespace["active"]
                    observations["phrases_placed"] = len(namespace["main_ids"])
                    observations["phrases_expected"] = len(namespace["ORDER"])
                    done = done and len(namespace["main_ids"]) == len(namespace["ORDER"]) > 0
                elif name == "bloomcraft":
                    done = app.clock >= namespace["T_END"] + 1
                    observations["animation_clock"] = app.clock
                else:
                    done = app.drawn == app.sp.n and app.sp.n > 0 and not app.running
                    observations["glyphs_drawn"] = app.drawn
                    observations["glyphs_expected"] = app.sp.n

                if done and finished_at is None:
                    finished_at = elapsed
                if finished_at is not None and elapsed - finished_at >= 1.0:
                    observations["completed"] = True
                    observations["window_size"] = [window.winfo_width(), window.winfo_height()]
                    if app is not None:
                        ImageTk.getimage(app.photo).save(OUTPUT / f"{name}-render.png")
                    try:
                        x, y = window.winfo_rootx(), window.winfo_rooty()
                        capture = ImageGrab.grab(bbox=(x, y, x + window.winfo_width(), y + window.winfo_height()))
                        capture.save(OUTPUT / f"{name}-window.png")
                        observations["window_capture"] = "saved"
                    except OSError:
                        try:
                            capture = ImageGrab.grab(window=window.winfo_id())
                            capture.save(OUTPUT / f"{name}-window.png")
                            observations["window_capture"] = "saved using window capture"
                        except OSError as exc:
                            observations["window_capture"] = str(exc)
                    if name == "heartglow":
                        namespace["cv"].postscript(file=str(OUTPUT / "heartglow-canvas.ps"), colormode="color")
                    if name == "bloomcraft":
                        app.toggle()
                        if not app.paused:
                            raise RuntimeError("Pause handler did not pause")
                        app.toggle()
                        app.restart()
                        if app.paused or app.clock != 0:
                            raise RuntimeError("Resume/restart handlers failed")
                        observations["pause_resume_restart_handlers"] = "passed"
                    elif app is not None:
                        app.start()
                        if not app.running or app.drawn >= app.sp.n:
                            raise RuntimeError("Restart handler did not restart animation")
                        observations["restart_handler"] = "passed"
                    window.destroy()
                    return
                if elapsed > 110:
                    raise TimeoutError("Animation did not complete within 110 seconds")
                window.after(200, observe)
            except Exception:
                errors.append(traceback.format_exc())
                window.destroy()

        window.after(200, observe)
        original_loop(window, *args, **kwargs)
        observations["loop_seconds"] = round(time.monotonic() - started, 2)

    tk.Tk.report_callback_exception = callback_error
    tk.Tk.mainloop = observed_loop
    if name == "heartglow":
        import turtle

        # Turtle invokes the Tcl event loop directly, bypassing Tk.mainloop.
        turtle.TurtleScreenBase.mainloop = lambda screen: observed_loop(screen.cv.winfo_toplevel())
    sys.argv = [str(script)] + (["--preset", "water-lily"] if name == "water-lily" else [])
    sys.path.insert(0, str(script.parent))
    # Preserve normal entry-point semantics, including __file__ and __main__.
    exec(compile(script.read_bytes(), str(script), "exec"), namespace)
    if errors:
        raise RuntimeError("\n".join(errors))
    if not observations.get("completed"):
        raise RuntimeError("The GUI exited before its animation completed")
    print(json.dumps(observations, indent=2), flush=True)


def check_images(pattern: str, minimum: int, animated: bool = False) -> dict:
    """Decode generated images and reject empty or unexpectedly static output."""
    from PIL import Image, ImageStat

    paths = sorted(OUTPUT.glob(pattern))
    if len(paths) < minimum:
        raise RuntimeError(f"Expected at least {minimum} outputs for {pattern}; got {len(paths)}")
    results = []
    for path in paths:
        with Image.open(path) as image:
            frames = getattr(image, "n_frames", 1)
            if animated and frames != 541:
                raise RuntimeError(f"Expected 541 GIF frames; got {frames}")
            hashes = set()
            for index in range(frames):
                image.seek(index)
                image.load()
                if index in (0, frames // 2, frames - 1):
                    rgb = image.convert("RGB")
                    if sum(ImageStat.Stat(rgb).var) == 0:
                        raise RuntimeError(f"Uniform output image: {path.name}, frame {index}")
                    hashes.add(hashlib.sha256(rgb.tobytes()).hexdigest())
            if animated and len(hashes) < 3:
                raise RuntimeError("Sampled GIF frames do not change")
            results.append({"file": path.name, "size": list(image.size), "frames": frames})
    return {"images": results}


def main() -> int:
    global OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT,
                        help="Save generated checks in a separate directory")
    parser.add_argument("--gui-child", choices=SCRIPTS)
    parser.add_argument("--only", choices=[
        "bloomcraft-png", "rockstar-png", "lilies-png", "water-lily-png", "bloomcraft-gif",
        *(f"{name}-gui" for name in SCRIPTS),
        "photo-missing-input", "photo-empty-text", "photo-small-width", "photo-overwrite-input",
    ], help="Rerun one check and update its result in the existing report")
    parser.add_argument("--spiral-only", action="store_true", help="Check all three current Spiral Ink photos")
    args = parser.parse_args()
    OUTPUT = args.output_dir.expanduser().resolve()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if args.gui_child:
        check_gui(args.gui_child)
        return 0

    import PIL
    import tkinter

    try:
        numpy_version = version("numpy")
    except PackageNotFoundError:
        numpy_version = "not installed"

    report = {
        "environment": {"python": sys.version.split()[0], "pillow": PIL.__version__,
                        "numpy": numpy_version, "tk": tkinter.TkVersion},
        "cases": [],
    }
    report_path = OUTPUT / "results.json"
    if args.only and report_path.exists():
        report["cases"] = json.loads(report_path.read_text(encoding="utf-8"))["cases"]

    def record(case):
        existing = next((index for index, item in enumerate(report["cases"])
                         if item["name"] == case["name"]), None)
        if existing is None:
            report["cases"].append(case)
        else:
            report["cases"][existing] = case
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"{case['status'].upper()}: {case['name']}", flush=True)

    def run(name, command, *, timeout=180, expected=0, images=None):
        if args.only and name != args.only:
            return
        if args.spiral_only and name.startswith(("bloomcraft", "heartglow")):
            return
        print(f"RUN: {name}", flush=True)
        started = time.monotonic()
        case = {"name": name, "status": "failed"}
        try:
            result = subprocess.run(command, cwd=OUTPUT, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=timeout,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            (OUTPUT / f"{name}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
            case["exit_code"] = result.returncode
            if result.returncode != expected:
                raise RuntimeError(f"Exit code {result.returncode}; expected {expected}. See {name}.log")
            if images:
                case.update(check_images(*images))
            case["status"] = "passed"
        except Exception as exc:
            case["error"] = str(exc)
        case["seconds"] = round(time.monotonic() - started, 2)
        record(case)

    python = sys.executable
    run("bloomcraft-png", [python, str(SCRIPTS["bloomcraft"]), "--png"], images=("flower*.png", 6))
    run("rockstar-png", [python, str(SCRIPTS["rockstar"]), "--png", "--output", "rockstar_spiral.png"], images=("rockstar_spiral.png", 1))
    run("lilies-png", [python, str(SCRIPTS["lilies"]), "--png", "--output", "lilies_spiral.png"], images=("lilies_spiral.png", 1))
    run("water-lily-png", [python, str(SCRIPTS["water-lily"]), "--preset", "water-lily", "--png", "--output", "water_lily_spiral.png"], images=("water_lily_spiral.png", 1))
    run("bloomcraft-gif", [python, str(SCRIPTS["bloomcraft"]), "--gif"], timeout=600, images=("flower.gif", 1, True))
    for name in SCRIPTS:
        run(f"{name}-gui", [python, str(Path(__file__).resolve()), "--gui-child", name,
                            "--output-dir", str(OUTPUT)])
    for name, arguments in (
        ("photo-missing-input", ["missing-photo.png", "--png"]),
        ("photo-empty-text", ["--text", "", "--png"]),
        ("photo-small-width", ["--width", "99", "--png"]),
        ("photo-overwrite-input", [str(ROOT / "Pink lilies.jpg"), "--png", "--output", str(ROOT / "Pink lilies.jpg")]),
    ):
        run(name, [python, str(SCRIPTS["lilies"]), *arguments], expected=2)

    manifest = json.loads((ROOT / "research/source-snapshots.json").read_text(encoding="utf-8"))
    adaptations_path = ROOT / "research/local-adaptations.json"
    adaptations = json.loads(adaptations_path.read_text(encoding="utf-8")) if adaptations_path.exists() else {}
    changed_files = {item["path"]: item["sha256"] for item in adaptations.get("modified", [])}
    removed_files = set(adaptations.get("removed", []))
    mismatches = []
    for source in manifest["sources"]:
        for item in source["files"]:
            path = ROOT / source["local_path"] / item["path"]
            relative = path.relative_to(ROOT).as_posix()
            if relative in removed_files:
                if path.exists():
                    mismatches.append(relative)
                continue
            expected_hash = changed_files.get(relative, item["sha256"])
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
                mismatches.append(relative)
    for item in adaptations.get("added", []):
        path = ROOT / item["path"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            mismatches.append(item["path"])
    for relative in removed_files:
        if (ROOT / relative).exists() and relative not in mismatches:
            mismatches.append(relative)
    record({"name": "source-integrity", "status": "failed" if mismatches else "passed", "mismatches": mismatches})
    print(dict(Counter(case["status"] for case in report["cases"])), flush=True)
    return int(any(case["status"] != "passed" for case in report["cases"]))


if __name__ == "__main__":
    raise SystemExit(main())
