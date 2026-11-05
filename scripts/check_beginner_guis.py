"""Exercise the three desktop interfaces and save genuine window captures.

Run with a desktop display and Pillow installed. The actual system clipboard is
not changed: its two write methods are mocked only while checking the Copy button.
"""

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import traceback
import tkinter as tk
from unittest.mock import patch

from PIL import ImageGrab

ROOT = Path(__file__).resolve().parents[1]
RESULTS = []
CALLBACK_ERRORS = []


def load_gui(name: str, project: Path):
    sys.path.insert(0, str(project))
    spec = importlib.util.spec_from_file_location(name, project / "gui.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def root_window() -> tk.Tk:
    root = tk.Tk()
    def callback_error(kind, value, tb):
        CALLBACK_ERRORS.append("".join(traceback.format_exception(kind, value, tb)))
    root.report_callback_exception = callback_error
    return root


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def passed(name: str, details: str) -> None:
    RESULTS.append({"name": name, "status": "passed", "detail": details})
    print(f"PASS: {name}", flush=True)


def capture(root: tk.Tk, project: Path) -> None:
    root.update_idletasks()
    root.update()
    image = ImageGrab.grab(window=root.winfo_id())
    check(sum(high - low for low, high in image.convert("RGB").getextrema()) > 0, "Blank capture")
    image.save(project / "screenshots/app.png")


def check_guessing() -> None:
    project = ROOT / "projects/01-number-guessing"
    gui = load_gui("number_guessing_gui", project)
    root = root_window()
    try:
        app = gui.NumberGuessingApp(root, rng=random.Random(7))
        for value in ("not a number", "10000"):
            app.guess.set(value)
            app.guess_button.invoke()
        check(app.game.remaining == 7, "Invalid guesses consumed attempts")
        secret = app.game.secret
        for value in (secret - 1, secret + 1):
            app.guess.set(str(value))
            app.guess_button.invoke()
        check(app.game.remaining == 5 and len(app.history.get_children()) == 2, "History or attempts incorrect")
        capture(root, project)
        app.guess.set(str(secret))
        app.guess_button.invoke()
        check(app.game.won and app.game.finished, "Winning guess did not finish the game")
        check(str(app.guess_button.cget("state")) == "disabled", "Finished game still enabled")
        app.submit()
        check(len(app.game.guesses) == 3, "Finished game accepted another guess")
        app.difficulty.set("Easy")
        app.new_game()
        check(app.game.high == 20 and app.game.remaining == 5, "Difficulty reset failed")
        check(not app.history.get_children(), "New game kept old history")
        wrong = 1 if app.game.secret != 1 else 20
        for _ in range(app.game.limit):
            app.guess.set(str(wrong))
            app.guess_button.invoke()
        check(app.game.finished and not app.game.won, "Losing round did not end")
        check(str(app.game.secret) in app.feedback.cget("text"), "Loss did not reveal secret")
        passed("number guessing desktop", "Validation, hints, history, win/loss, difficulty reset, and finished-state controls")
    finally:
        root.destroy()


def check_rps() -> None:
    project = ROOT / "projects/02-rock-paper-scissors"
    gui = load_gui("rps_gui", project)
    root = root_window()
    try:
        app = gui.RockPaperScissorsApp(root, rng=random.Random(7))
        for button in app.move_buttons:
            button.invoke()
        check(len(app.match.history) == 3 and sum(app.match.score.values()) == 3, "Round scoring failed")
        for key, label in app.score_labels.items():
            check(label.cget("text") == str(app.match.score[key]), "Displayed score differs from rules")
        capture(root, project)
        while not app.match.finished:
            app.move_buttons[0].invoke()
        app.choose("paper")
        check(len(app.match.history) == 5, "Finished match accepted another move")
        check(all(str(button.cget("state")) == "disabled" for button in app.move_buttons), "Move buttons not disabled")
        app.rounds.set("3")
        app.new_match()
        check(app.match.rounds == 3 and not app.match.history, "New match did not reset state")
        check(all(label.cget("text") == "0" for label in app.score_labels.values()), "Scores did not reset")
        passed("rock paper scissors desktop", "Move-button callbacks, score cards, round history, final state, and reset")
    finally:
        root.destroy()


def check_passwords() -> None:
    project = ROOT / "projects/03-password-generator"
    gui = load_gui("passwords_gui", project)
    root = root_window()
    try:
        app = gui.PasswordGeneratorApp(root)
        app.length.set("20")
        app.count.set("2")
        app.groups[-1].set(False)
        app.generate()
        check(len(app.passwords) == 2 and all(len(value) == 20 and value.isalnum() for value in app.passwords), "Generation settings were ignored")
        original = app.passwords.copy()
        check(app.table.item("0", "values")[1] == "*" * 20, "Passwords not masked by default")
        app.show_passwords.set(True)
        app.update_visibility()
        check(app.table.item("0", "values")[1] == original[0], "Reveal control failed")
        check(app.passwords == original, "Reveal unexpectedly regenerated passwords")
        app.table.selection_set("1")
        copied = []
        with patch.object(root, "clipboard_clear"), patch.object(root, "clipboard_append", side_effect=copied.append):
            app.copy_button.invoke()
        check(copied == [original[1]], "Copy did not use the selected unmasked password")
        app.length.set("24")
        check(not app.passwords and str(app.copy_button.cget("state")) == "disabled", "Changed settings kept stale results")
        for selected in app.groups:
            selected.set(False)
        app.generate()
        check(not app.passwords and "group" in app.status.cget("text"), "Empty character selection was not rejected")
        app.length.set("oops")
        app.generate()
        check("whole numbers" in app.status.cget("text"), "Invalid number did not show feedback")
        app.length.set("20")
        app.count.set("2")
        for selected in app.groups:
            selected.set(True)
        app.show_passwords.set(False)
        app.generate()
        capture(root, project)
        app.clear_results()
        check(not app.passwords and not app.table.get_children(), "Clear left password results behind")
        passed("password generator desktop", "Settings, masking/reveal, mocked clipboard copy, stale-result clearing, invalid input, and clear")
    finally:
        root.destroy()


def main() -> int:
    report = ROOT / "research/verification/beginner-gui-checks.json"
    cli_files = [ROOT / f"projects/{name}/main.py" for name in
                 ("01-number-guessing", "02-rock-paper-scissors", "03-password-generator")]
    cli_hashes = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in cli_files}
    try:
        check_guessing()
        check_rps()
        check_passwords()
        check(not CALLBACK_ERRORS, "\n".join(CALLBACK_ERRORS))
        cases = ((cli_files[0], ["--low", "5", "--high", "5"], "5\n", "Correct!"),
                 (cli_files[1], ["--rounds", "1", "--seed", "7"], "r\n", "Final score:"),
                 (cli_files[2], ["--length", "16"], None, None))
        for path, arguments, typed, expected in cases:
            result = subprocess.run([sys.executable, str(path), *arguments], input=typed,
                                    text=True, capture_output=True, check=True, timeout=15)
            check(expected in result.stdout if expected else len(result.stdout.strip()) == 16,
                  f"CLI smoke check failed: {path}")
            check(hashlib.sha256(path.read_bytes()).hexdigest() == cli_hashes[str(path)], "CLI entry point changed")
        passed("existing CLI launchers", "All three terminal programs still run; main.py entry points unchanged")
        return 0
    except Exception:
        RESULTS.append({"name": "GUI verification", "status": "failed", "detail": traceback.format_exc()})
        traceback.print_exc()
        return 1
    finally:
        report.write_text(json.dumps({"recorded_utc": datetime.now(timezone.utc).isoformat(),
                                      "checks": RESULTS, "callback_errors": CALLBACK_ERRORS}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
