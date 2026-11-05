"""Capture actual local applications and independently decode generated QR codes.

Requires the projects' dependencies and scripts/requirements-verification.txt.
The organizer operates only on an automatically created temporary fixture.
"""

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.request

from PIL import Image, ImageGrab

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
RESULTS = []


def passed(name: str, detail: str) -> None:
    RESULTS.append({"name": name, "status": "passed", "detail": detail})
    print(f"PASS: {name}", flush=True)


def load_module(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def capture_window(root, path: Path) -> None:
    root.update_idletasks()
    root.update()
    image = ImageGrab.grab(window=root.winfo_id())
    if sum(channel[1] - channel[0] for channel in image.convert("RGB").getextrema()) == 0:
        raise RuntimeError("Window capture was blank")
    image.save(path)


def cli(project: Path, arguments: list[str]) -> str:
    environment = dict(os.environ, PYTHONUTF8="1")
    result = subprocess.run([sys.executable, str(project / "main.py"), *arguments],
                            capture_output=True, text=True, encoding="utf-8", check=True,
                            timeout=30, env=environment)
    return result.stdout


def organizer_checks(folder: Path) -> None:
    import tkinter as tk
    project = PROJECTS / "07-smart-file-organizer"
    (folder / "Documents").mkdir()
    (folder / "Documents/report.txt").write_text("existing document")
    (folder / "report.txt").write_text("new document")
    (folder / "lesson.py").write_text("print('synthetic example')\n")
    Image.new("RGB", (40, 40), "navy").save(folder / "picture.png")
    originals = {path.relative_to(folder).as_posix(): path.read_bytes() for path in folder.rglob("*") if path.is_file()}
    preview = cli(project, [str(folder)])
    if {path.relative_to(folder).as_posix(): path.read_bytes() for path in folder.rglob("*") if path.is_file()} != originals:
        raise RuntimeError("Dry run changed the fixture")
    passed("organizer dry run", "No fixture paths or contents changed")
    gui = load_module("organizer_gui", project / "app.py")
    root = tk.Tk()
    try:
        app = gui.OrganizerApp(root)
        app.preview()
        if "Choose a folder" not in app.status.cget("text"):
            raise RuntimeError("Empty folder was not rejected")
        app.folder.set(str(folder))
        app.preview()
        if len(app.table.get_children()) != 3:
            raise RuntimeError("Wrong preview row count")
        capture_window(root, project / "screenshots/app.png")
        passed("organizer desktop preview", "Three planned moves; explicit Apply control")
    finally:
        root.destroy()
    applied = cli(project, [str(folder), "--apply"])
    manifest = next((folder / ".organizer/manifests").glob("*.json"))
    undo_preview = cli(project, ["--undo", str(manifest)])
    undone = cli(project, ["--undo", str(manifest), "--apply"])
    for relative, content in originals.items():
        if (folder / relative).read_bytes() != content:
            raise RuntimeError("Undo did not restore original bytes")
    transcript = ("Actual output from a temporary synthetic folder. Paths abbreviated for readability.\n\n"
                  + preview + "\n" + applied + "\n" + undo_preview + "\n" + undone)
    (project / "samples/terminal-output.txt").write_text(transcript.replace(str(folder), "<practice-folder>"), encoding="utf-8")
    passed("organizer apply and undo", "Duplicate preserved; every original byte restored")


def qr_checks(folder: Path) -> None:
    import tkinter as tk
    import zxingcpp
    project = PROJECTS / "08-qr-code-studio"
    payload = "https://www.python.org/"
    outputs = []
    for extension in ("png", "svg"):
        target = folder / f"python.{extension}"
        stdout = cli(project, [payload, "--output", str(target)])
        shutil.copyfile(target, project / f"samples/python.{extension}")
        outputs.append(stdout.replace(str(folder), "<temporary-folder>"))
    decoded = zxingcpp.read_barcode(Image.open(folder / "python.png"))
    if decoded is None or decoded.text != payload:
        raise RuntimeError("Independent PNG QR decoding failed")
    passed("QR PNG decode", "Independent zxing-cpp decoded the exact URL")
    studio = load_module("qr_studio", project / "qr_studio.py")
    root = tk.Tk()
    try:
        app = studio.Studio(root)
        app.scale.set(1)
        app.preview()
        if "Check your settings" not in app.status.cget("text"):
            raise RuntimeError("Invalid QR size did not show an error")
        app.scale.set(10)
        app.preview()
        if "Ready:" not in app.status.cget("text"):
            raise RuntimeError("QR preview failed")
        capture_window(root, project / "screenshots/app.png")
        passed("QR desktop", "Valid preview and invalid-size feedback exercised")
    finally:
        root.destroy()
    (project / "samples/terminal-output.txt").write_text("\n".join(outputs) + "\nIndependent PNG decode: " + decoded.text + "\n", encoding="utf-8")


def maze_checks() -> None:
    import tkinter as tk
    project = PROJECTS / "10-maze-solving-visualizer"
    text = cli(project, ["--predefined", "--solve"])
    if "path=8 edges" not in text or "path=12 edges" not in text:
        raise RuntimeError("Maze counterexample did not match expected lengths")
    (project / "samples/terminal-output.txt").write_text(text, encoding="utf-8")
    gui = load_module("maze_gui", project / "main.py")
    root = tk.Tk()
    try:
        app = gui.MazeApp(root, gui.generate_maze(seed=17))
        app.delay.set(1)
        app.animate()
        deadline = time.monotonic() + 20
        while app.running:
            if time.monotonic() > deadline:
                raise TimeoutError("Maze animation did not finish")
            root.update()
            time.sleep(0.002)
        capture_window(root, project / "screenshots/generated.png")
        app.load(gui.parse_maze(gui.PREDEFINED))
        app.animate()
        while app.running:
            root.update()
            time.sleep(0.002)
        capture_window(root, project / "screenshots/app.png")
        if [result.path_length for result in app.results] != [8, 12]:
            raise RuntimeError("GUI route metrics differ from algorithms")
        passed("maze desktop animations", "Generated and predefined mazes animated; BFS=8, DFS=12")
    finally:
        root.destroy()


def browser_checks(folder: Path) -> None:
    from playwright.sync_api import sync_playwright
    import zxingcpp

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    project = PROJECTS / "09-expense-tracker-dashboard"
    log_path = ROOT / "research/verification/dashboard-server.log"
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", str(project / "app.py"),
             "--server.headless=true", "--server.address=127.0.0.1", f"--server.port={port}",
             "--server.fileWatcherType=none", "--browser.gatherUsageStats=false"],
            stdout=log, stderr=subprocess.STDOUT, cwd=ROOT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        try:
            deadline = time.monotonic() + 30
            while True:
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except OSError:
                    if time.monotonic() > deadline or process.poll() is not None:
                        raise RuntimeError("Dashboard server did not become healthy")
                    time.sleep(0.2)
            with sync_playwright() as playwright:
                # Reuse an installed browser; runtime projects do not depend on Playwright.
                cached = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"
                candidates = list(cached.glob("chromium-*/chrome-win64/chrome.exe"))
                executable = str(sorted(candidates)[-1]) if candidates else None
                browser = playwright.chromium.launch(headless=True, executable_path=executable)
                try:
                    page = browser.new_page(viewport={"width": 1440, "height": 1440})
                    page.goto(f"http://127.0.0.1:{port}")
                    page.get_by_role("heading", name="Selected transactions", exact=True).wait_for(timeout=30000)
                    page.locator("canvas").first.wait_for()
                    page.wait_for_timeout(600)
                    page.screenshot(path=str(project / "screenshots/app.png"), full_page=True)
                    with page.expect_download() as download_event:
                        page.get_by_text("Download filtered CSV", exact=True).click()
                    download_event.value.save_as(str(project / "samples/filtered-expenses.csv"))
                    passed("expense dashboard browser", "Real page, charts, table, and CSV download captured")
                    svg = (PROJECTS / "08-qr-code-studio/samples/python.svg").read_text(encoding="utf-8")
                    page.set_content('<html><body style="margin:0">' + svg + '</body></html>')
                    rendered = folder / "svg-render.png"
                    page.locator("svg").screenshot(path=str(rendered))
                    decoded = zxingcpp.read_barcode(Image.open(rendered))
                    if decoded is None or decoded.text != "https://www.python.org/":
                        raise RuntimeError("SVG QR decode failed after real browser rendering")
                    passed("QR SVG decode", "Browser-rendered vector export decoded to the exact URL")
                finally:
                    browser.close()
        finally:
            process.terminate()
            process.wait(timeout=15)


def main() -> int:
    report = ROOT / "research/verification/application-checks.json"
    try:
        fixtures = ROOT / "research/verification/demo-fixtures"
        fixtures.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="run-", dir=fixtures) as folder:
            temporary = Path(folder)
            inbox = temporary / "inbox"
            inbox.mkdir()
            organizer_checks(inbox)
            qr_checks(temporary)
            maze_checks()
            browser_checks(temporary)
        baseline = json.loads((ROOT / "research/verification/visual-art-before.json").read_text(encoding="utf-8"))
        for relative, expected in baseline.items():
            if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
                raise RuntimeError(f"Existing artwork/source changed: {relative}")
        passed("visual art preservation", f"All {len(baseline)} existing source/artwork files unchanged")
        return 0
    except Exception:
        RESULTS.append({"name": "capture run", "status": "failed", "detail": traceback.format_exc()})
        traceback.print_exc()
        return 1
    finally:
        report.write_text(json.dumps({"recorded_utc": datetime.now(timezone.utc).isoformat(), "checks": RESULTS}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
