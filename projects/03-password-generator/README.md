# Password Generator

Generate passwords locally with the standard-library secrets module. Choose length and count, and optionally omit symbols.

## Learning objectives

- Work with strings, character groups, and comprehensions.
- Understand why operating-system-backed randomness is used for credentials.
- Validate settings and test properties without expecting one particular random result.

## Installation

Only Python 3.12+ standard-library modules are required.

Run the commands below **from this project folder**. From the repository root,
first run `cd projects/03-password-generator`. Activate your Python environment first.

## Usage

```powershell
python main.py
python main.py --length 20 --count 3
python main.py --length 16 --no-symbols
```

Each password contains a character from every selected group. Rejection sampling accepts only qualifying strings. Length is 4-128; the default is 16. Count is 1-20. No network, file storage, seeded mode, or password history is used. The four-character minimum is for learning validation, not a recommendation for real accounts. Use longer unique passwords and a password manager.

## Desktop window

The command-line version above remains available in `main.py`. Open the separate
desktop version from this project folder:

```powershell
python gui.py
```

On Windows, `pythonw gui.py` opens the window without a console. You can also
double-click `desktop.pyw` when Python file associations are configured. On
macOS/Linux, use `python gui.py`.

Choose length, batch count, and character groups, then click Generate
passwords. Results are masked until Show passwords is selected. Select a row
and click Copy selected to copy its actual password, even while masked.
Changing settings clears the previous batch; Clear results also removes it
from the window. No passwords are written to files. Clearing the results does
not clear the system clipboard. Clipboard behavior can vary by platform.

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

Short lengths or unsupported counts show an argument error. Printed passwords are visible in terminal scrollback. Every password in a sample transcript is public demonstration output and must never be used as a credential.


To run the desktop interaction checks and regenerate the real window captures,
use `python scripts/check_beginner_guis.py` from the repository root. That optional
capture script needs Pillow; the desktop applications themselves do not. Copy
behavior is checked with a mock clipboard, preserving the user's clipboard.
