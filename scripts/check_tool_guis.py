"""Verify the simplified tools using synthetic files, a local server, and real captures."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import tkinter as tk
import traceback
from unittest.mock import patch

from PIL import Image
from capture_project_outputs import capture_window, load_module

ROOT = Path(__file__).resolve().parents[1]
RESULTS = []
ERRORS = []


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def passed(name, detail):
    RESULTS.append({"name": name, "status": "passed", "detail": detail})
    print(f"PASS: {name}", flush=True)


def root_window():
    root = tk.Tk()
    def callback_error(kind, value, tb):
        ERRORS.append("".join(traceback.format_exception(kind, value, tb)))
    root.report_callback_exception = callback_error
    return root


def wait_for(root, condition, seconds=45):
    deadline = time.monotonic() + seconds
    while not condition():
        if time.monotonic() > deadline:
            raise TimeoutError("The dashboard did not become ready")
        root.update()
        time.sleep(0.02)


def organizer_checks(folder):
    project = ROOT / "projects/07-smart-file-organizer"
    gui = load_module("organizer_tool_gui", project / "app.py")
    (folder / "Documents").mkdir()
    (folder / "Documents/report.txt").write_text("existing file")
    (folder / "report.txt").write_text("new file")
    (folder / "lesson.py").write_text("print('synthetic')")
    original = {path.relative_to(folder): path.read_bytes() for path in folder.rglob("*") if path.is_file()}
    root = root_window()
    try:
        app = gui.OrganizerApp(root)
        with patch("tkinter.filedialog.askdirectory", return_value=str(folder)):
            app.choose()
        check(len(app.table.get_children()) == 2, "Folder chooser did not generate a preview")
        check((folder / "report.txt").is_file(), "Preview moved files")
        capture_window(root, project / "screenshots/app.png")
        app.apply_button.invoke()
        check(not (folder / "report.txt").exists(), "Organize button did not apply moves")
        app.undo_button.invoke()
        check(app.mode == "undo" and len(app.table.get_children()) == 2, "Undo preview missing")
        check(not (folder / "report.txt").exists(), "Undo preview restored files too early")
        capture_window(root, project / "screenshots/undo.png")
        app.apply_button.invoke()
        for relative, data in original.items():
            check((folder / relative).read_bytes() == data, "GUI undo lost original bytes")
        passed("organizer desktop round trip", "Folder chooser, automatic preview, organize, undo preview, and restore preserved original bytes")
        app.preview()
        app.apply_button.invoke()
        (folder / "report.txt").write_text("new user document")
        app.undo_button.invoke()
        check("overwrite" in app.status.cget("text"), "Undo conflict was not explained")
        check(str(app.apply_button.cget("state")) == "disabled", "Conflicting restore was still enabled")
        check((folder / "report.txt").read_text() == "new user document", "Conflicting source was overwritten")
        passed("organizer undo conflict", "Newly created source protected; restore disabled with a useful error")
    finally:
        root.destroy()


def qr_checks(folder):
    import zxingcpp
    project = ROOT / "projects/08-qr-code-studio"
    gui = load_module("qr_tool_gui", project / "qr_studio.py")
    root = root_window()
    try:
        app = gui.Studio(root)
        root.update()
        app.message.delete("1.0", "end")
        app.message.insert("1.0", "Hello from QR Studio")
        root.update()
        check(app.preview_signature is None, "Edited payload left a stale preview")
        check(all(str(button.cget("state")) == "disabled" for button in app.save_buttons), "Edited payload still saveable")
        app.size_choice.set("Large")
        app.change_size()
        app.color_choice.set("Forest")
        app.change_colors()
        app.generate_button.invoke()
        check(app.preview_signature is not None, "Preset generation failed")
        for extension, button in zip(("png", "svg"), app.save_buttons):
            target = folder / f"new-qr.{extension}"
            with patch("tkinter.filedialog.asksaveasfilename", return_value=str(target)):
                button.invoke()
            check(target.is_file(), f"GUI did not save {extension}")
        with Image.open(folder / "new-qr.png") as image:
            decoded = zxingcpp.read_barcode(image)
            check(decoded is not None and decoded.text == "Hello from QR Studio", "GUI-saved QR did not decode exactly")
        original = (folder / "new-qr.png").read_bytes()
        with patch("tkinter.filedialog.asksaveasfilename", return_value=str(folder / "new-qr.png")):
            app.save_buttons[0].invoke()
        check((folder / "new-qr.png").read_bytes() == original, "Existing export overwritten")
        check("already exists" in app.status.cget("text"), "Overwrite feedback missing")
        app.foreground.set("white")
        app.background.set("white")
        app.generate_button.invoke()
        check(app.preview_signature is None and app.photo is None, "Invalid colors retained an old QR")
        with patch("tkinter.filedialog.asksaveasfilename") as dialog:
            app.save("png")
            dialog.assert_not_called()
        app.change_colors()
        app.size_choice.set("Medium")
        app.change_size()
        app.generate_button.invoke()
        capture_window(root, project / "screenshots/app.png")
        passed("QR desktop create and save", "Presets, stale-preview protection, PNG/SVG saving, independent PNG decode, invalid colors, and overwrite protection")
    finally:
        root.destroy()


def expense_checks(folder):
    from playwright.sync_api import sync_playwright
    project = ROOT / "projects/09-expense-tracker-dashboard"
    gui = load_module("expense_tool_gui", project / "gui.py")
    opened = []
    root = root_window()
    app = gui.ExpenseTrackerLauncher(root, browser=lambda url: opened.append(url) or True)
    try:
        wait_for(root, lambda: bool(opened))
        check(app.server.healthy(), "Launcher opened the browser before health readiness")
        capture_window(root, project / "screenshots/launcher.png")
        with sync_playwright() as playwright:
            cached = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"
            candidates = sorted(cached.glob("chromium-*/chrome-win64/chrome.exe"))
            browser = playwright.chromium.launch(headless=True, executable_path=str(candidates[-1]) if candidates else None)
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1440})
                page.goto(opened[-1])
                page.get_by_role("heading", name="Selected transactions", exact=True).wait_for(timeout=30000)
                page.locator("canvas").first.wait_for()
                page.wait_for_timeout(400)
                page.screenshot(path=str(project / "screenshots/app.png"), full_page=True)
                page.get_by_text("CSV format and example", exact=True).click()
                with page.expect_download() as download:
                    page.get_by_text("Download example CSV", exact=True).click()
                target = folder / "example.csv"
                download.value.save_as(str(target))
                check(target.read_bytes() == (project / "samples/expenses.csv").read_bytes(), "Example download differs from synthetic CSV")
                passed("expense dashboard guided page", "Real browser loaded through launcher; example CSV download matches the synthetic sample")
            finally:
                browser.close()
        first_process = app.server.process
        app.stop_button.invoke()
        check(first_process.poll() is not None and app.server.process is None, "Stop left the dashboard running")
        app.start_button.invoke()
        wait_for(root, lambda: len(opened) == 2)
        second_process = app.server.process
        app.close()
        root = None
        check(second_process.poll() is not None, "Closing the launcher left a child process")
        passed("expense launcher lifecycle", "Automatic browser-open callback, Stop, restart, and close; both owned processes exited")
    finally:
        if root is not None:
            app.close()


def main():
    report = ROOT / "research/verification/tool-gui-checks.json"
    try:
        fixtures = ROOT / "research/verification/demo-fixtures"
        fixtures.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="tools-", dir=fixtures) as folder:
            temporary = Path(folder)
            inbox = temporary / "inbox"
            inbox.mkdir()
            organizer_checks(inbox)
            qr_checks(temporary)
            expense_checks(temporary)
        check(not ERRORS, "\n".join(ERRORS))
        baseline = json.loads((ROOT / "research/verification/visual-art-before.json").read_text(encoding="utf-8"))
        for relative, expected in baseline.items():
            check(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, f"Changed existing art: {relative}")
        passed("visual art preservation", f"All {len(baseline)} source/artwork files unchanged")
        return 0
    except Exception:
        RESULTS.append({"name": "utility GUI checks", "status": "failed", "detail": traceback.format_exc()})
        traceback.print_exc()
        return 1
    finally:
        report.write_text(json.dumps({"recorded_utc": datetime.now(timezone.utc).isoformat(),
                                      "checks": RESULTS, "callback_errors": ERRORS}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
