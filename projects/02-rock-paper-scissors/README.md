# Rock, Paper, Scissors

Play a fixed-length match against the computer and see how a few explicit rules produce wins, losses, and draws.

## Learning objectives

- Normalize input with string methods and dictionaries.
- Express all nine possible matchups with a small rule table.
- Track a score over several rounds and test boundary cases.

## Installation

Only Python 3.12+ standard-library modules are required.

Run the commands below **from this project folder**. From the repository root,
first run `cd projects/02-rock-paper-scissors`. Activate your Python environment first.

## Usage

```powershell
python main.py
python main.py --rounds 3 --seed 7
```

Enter `r`, `p`, `s`, or a full choice. Every valid round counts, including a draw; invalid entries retry the same round. Enter `q` to leave. `--seed` is an optional reproducible practice setting. Normal play uses fresh randomness.

## Desktop window

The command-line version above remains available in `main.py`. Open the separate
desktop version from this project folder:

```powershell
python gui.py
```

On Windows, `pythonw gui.py` opens the window without a console. You can also
double-click `desktop.pyw` when Python file associations are configured. On
macOS/Linux, use `python gui.py`.

The window has large Rock, Paper, and Scissors buttons, R/P/S keyboard
shortcuts, score cards, and round history. Choose 3, 5, or 7 rounds; draws
count as rounds. At the end, move buttons are disabled until New match.
Changing the round count starts a new match.

The desktop interface uses only Tkinter and ttk from the standard library.
Check Tk with `python -m tkinter`. A graphical display is required; if Tk is
missing, install your Python distribution's Tk support or continue using the
terminal version.

[View the working desktop window](screenshots/app.png).
The testable rules stay in the existing logic module; `gui.py` handles the
widgets and `desktop.pyw` is only a Windows launcher.

## Tests and representative output

```powershell
python -m unittest discover -s tests -v
```

[Captured terminal output](samples/terminal-output.txt). See [samples](samples/) for outputs from real execution and
[exercises](exercises.md) for follow-up challenges. The repository-wide test
command is `python scripts/run_project_tests.py` from the repository root.

## Troubleshooting

Use 1-100 rounds. Words are case insensitive; unsupported choices produce a reminder. End-of-input or Ctrl+C ends the match cleanly.


To run the desktop interaction checks and regenerate the real window captures,
use `python scripts/check_beginner_guis.py` from the repository root. That optional
capture script needs Pillow; the desktop applications themselves do not. Copy
behavior is checked with a mock clipboard, preserving the user's clipboard.
