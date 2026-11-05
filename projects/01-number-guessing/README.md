# Number Guessing

Build a small conversation with the computer: guess its secret number, use the hints, and finish within a limited number of valid guesses.

## Learning objectives

- Read and validate terminal input without crashing.
- Use comparisons, loops, functions, and a limited-attempt game state.
- Separate game rules from input and test deterministic practice rounds.

## Installation

Only Python 3.12+ standard-library modules are required.

Run the commands below **from this project folder**. From the repository root,
first run `cd projects/01-number-guessing`. Activate your Python environment first.

## Usage

```powershell
python main.py
python main.py --low 1 --high 20 --attempts 5 --seed 7
```

Invalid or out-of-range guesses do not consume attempts. Enter `q` to leave. `--seed` repeats a practice game; normal games choose a fresh secret. The final message reveals the secret after a loss.

## Desktop window

The command-line version above remains available in `main.py`. Open the separate
desktop version from this project folder:

```powershell
python gui.py
```

On Windows, `pythonw gui.py` opens the window without a console. You can also
double-click `desktop.pyw` when Python file associations are configured. On
macOS/Linux, use `python gui.py`.

The window offers Easy, Classic, and Challenge modes, a live attempts bar,
guess history, and inline hints. Invalid input does not consume an attempt.
Press Enter or click Check guess. New game and difficulty changes reset the
round. Completed rounds disable guessing until you start again.

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

If input ends unexpectedly, the game exits cleanly. Check that `--low` is no larger than `--high`, and use at least one attempt. The seed is for learning and reproducible examples, not secret generation.


To run the desktop interaction checks and regenerate the real window captures,
use `python scripts/check_beginner_guis.py` from the repository root. That optional
capture script needs Pillow; the desktop applications themselves do not. Copy
behavior is checked with a mock clipboard, preserving the user's clipboard.
