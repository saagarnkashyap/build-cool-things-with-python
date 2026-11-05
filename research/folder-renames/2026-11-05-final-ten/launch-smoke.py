"""Smoke-check final chapter entry points without replacing curated assets."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).parent / "runtime-outputs/launch"
CHECKS = []

GUI_HARNESS = r'''
from pathlib import Path
import runpy
import sys
import tkinter as tk
import traceback

path = Path(sys.argv[1])
chapter = sys.argv[2]
sys.path.insert(0, str(path.parent))
original = tk.Tk.mainloop
errors = []
opened = []
def report(self, kind, value, tb):
    errors.append(''.join(traceback.format_exception(kind, value, tb)))
def loop(root, *args, **kwargs):
    opened.append(root.title())
    def close():
        labels = []
        def visit(widget):
            if 'Label' in widget.winfo_class():
                labels.append(str(widget.cget('text')))
            for child in widget.winfo_children():
                visit(child)
        visit(root)
        if not any(text.startswith(chapter + ' /') for text in labels):
            errors.append('Wrong or missing chapter badge: ' + chapter)
        handler = root.protocol('WM_DELETE_WINDOW')
        if handler:
            root.tk.eval(handler)
        else:
            root.destroy()
    root.after(100, close)
    original(root, *args, **kwargs)
tk.Tk.report_callback_exception = report
tk.Tk.mainloop = loop
runpy.run_path(str(path), run_name='__main__')
if errors or not opened:
    raise RuntimeError('\n'.join(errors) or 'No desktop window opened')
print('Opened and closed:', ', '.join(opened))
'''


def run(name, arguments):
    result = subprocess.run(arguments, cwd=OUTPUT, capture_output=True, text=True,
                            encoding="utf-8", env=dict(os.environ, PYTHONUTF8="1"), timeout=45)
    (OUTPUT / f"{name}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"{name} failed: {result.stderr}")
    CHECKS.append({"name": name, "status": "passed"})
    print("PASS:", name, flush=True)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    python = sys.executable
    desktop_projects = ("01-number-guessing", "02-rock-paper-scissors", "03-password-generator",
                        "07-smart-file-organizer", "08-qr-code-studio", "09-expense-tracker-dashboard")
    for name in desktop_projects:
        project = ROOT / "projects" / name
        if (project / "main.py").exists():
            run(name + "-cli-help", [python, str(project / "main.py"), "--help"])
        for filename in ("gui.py", "desktop.pyw"):
            run(name + "-" + filename.replace(".", "-"),
                [python, "-c", GUI_HARNESS, str(project / filename), name[:2]])
    maze = ROOT / "projects/10-maze-solving-visualizer/main.py"
    run("maze-cli-help", [python, str(maze), "--help"])
    run("maze-predefined-solve", [python, str(maze), "--predefined", "--solve"])
    qr = ROOT / "projects/08-qr-code-studio/main.py"
    for extension in ("png", "svg"):
        run("qr-cli-" + extension, [python, str(qr), "Final layout verification",
                                   "--output", str(OUTPUT / f"qr-example.{extension}")])

    # Exercise the actual renamed dashboard path and module imports via a browser.
    project = ROOT / "projects/09-expense-tracker-dashboard"
    spec = importlib.util.spec_from_file_location("renamed_dashboard_launcher", project / "launcher.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    server = module.DashboardServer()
    try:
        server.start()
        deadline = time.monotonic() + 30
        while not server.healthy():
            if time.monotonic() > deadline or server.process.poll() is not None:
                raise RuntimeError(server.diagnostics())
            time.sleep(0.1)
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            cached = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"
            browsers = sorted(cached.glob("chromium-*/chrome-win64/chrome.exe"))
            browser = playwright.chromium.launch(headless=True, executable_path=str(browsers[-1]) if browsers else None)
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.goto(server.url)
                page.get_by_role("heading", name="Selected transactions", exact=True).wait_for(timeout=30000)
                page.get_by_text("315.95", exact=True).wait_for()
                CHECKS.append({"name": "renamed-expense-dashboard", "status": "passed"})
                print("PASS: renamed-expense-dashboard", flush=True)
            finally:
                browser.close()
    finally:
        server.stop()
    (OUTPUT / "results.json").write_text(json.dumps({"checks": CHECKS}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
