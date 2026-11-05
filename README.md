# Build Cool Things with Python

**From Zero to Real-World Builder**

A project-first Python learning repository. Start with small terminal programs,
explore creative visuals, then build useful tools and interactive applications.
New numbered projects target Python 3.12 or later and include tests, exercises,
and outputs from real execution.

## Learning path and project navigation

| Batch | Project | What you will learn |
| --- | --- | --- |
| 1 - Foundations | [01 Number Guessing](projects/01-number-guessing/README.md) | Input, validation, conditions, loops, functions |
| 1 - Foundations | [02 Rock, Paper, Scissors](projects/02-rock-paper-scissors/README.md) | Rules, randomness, dictionaries, scoring |
| 1 - Foundations | [03 Password Generator](projects/03-password-generator/README.md) | Strings, validation, secure randomness |
| 2 - Creative Python | [04 Bloomcraft](projects/visual-art-lab/04-bloomcraft/README.md) | Generative flower animation |
| 2 - Creative Python | [05 Heartglow](projects/visual-art-lab/05-heartglow/README.md) | Multilingual heart animation |
| 2 - Creative Python | [06 Spiral Ink](projects/visual-art-lab/06-spiral-ink/README.md) | Image-to-text spiral artwork |
| 3 - Useful tools | [07 Smart File Organizer](projects/07-smart-file-organizer/README.md) | Paths, safe transfers, collision handling, undo journals |
| 3 - Useful tools | [08 QR Code Studio](projects/08-qr-code-studio/README.md) | Input validation, libraries, raster and vector exports |
| 4 - Applications | [09 Expense Tracker Dashboard](projects/09-expense-tracker-dashboard/README.md) | CSV validation, Pandas, filters, charts, Streamlit |
| 4 - Applications | [10 Maze-Solving Visualizer](projects/10-maze-solving-visualizer/README.md) | Graphs, independent BFS/DFS, animation, shortest paths |

The final ten-project sequence runs from 01 to 10. Chapters 04-06 stay grouped
inside [Visual Art Lab](projects/visual-art-lab/README.md); its artwork is preserved.
PDF tools, website monitoring, and other advanced proposals remain future work.

## Install

Use Python 3.12 or later:

```powershell
python -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install -r projects/08-qr-code-studio/requirements.txt -r projects/09-expense-tracker-dashboard/requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`. The three foundation
projects and organizer/maze terminal modes need only the standard library.
Desktop windows need Tk; check with `python -m tkinter`. QR Code Studio needs
qrcode and Pillow. The dashboard needs Streamlit and Pandas. Visual Art Lab has
its own existing setup instructions, including NumPy where required.

## Simple desktop launchers

On Windows, open a project folder and double-click `desktop.pyw` (with Python
file associations configured). These tools now have the same simple launch option
as the three foundation projects:

| Tool | Desktop script | Main flow |
| --- | --- | --- |
| [Smart File Organizer](projects/07-smart-file-organizer/README.md) | `projects/07-smart-file-organizer/desktop.pyw` | Choose folder, review, organize; preview and undo the latest run |
| [QR Code Studio](projects/08-qr-code-studio/README.md) | `projects/08-qr-code-studio/desktop.pyw` | Enter text, choose presets, generate, save |
| [Expense Tracker](projects/09-expense-tracker-dashboard/README.md) | `projects/09-expense-tracker-dashboard/desktop.pyw` | Browser opens automatically; choose CSV, filter, download |

You can also run `python gui.py` inside any of these project folders. First-time
installation instructions still apply. The expense tracker launcher manages its
own local server; keep it open while using the browser dashboard. Existing
terminal commands remain available.

## Try a project

From the repository root:

```powershell
python projects/01-number-guessing/main.py
python projects/02-rock-paper-scissors/main.py
python projects/03-password-generator/main.py --length 20
python projects/07-smart-file-organizer/main.py --gui
python projects/08-qr-code-studio/main.py --gui
python -m streamlit run projects/09-expense-tracker-dashboard/app.py --server.address 127.0.0.1
python projects/10-maze-solving-visualizer/main.py --predefined
```

The first three projects also have separate desktop windows:

```powershell
python projects/01-number-guessing/gui.py
python projects/02-rock-paper-scissors/gui.py
python projects/03-password-generator/gui.py
```

Their `main.py` commands remain the terminal versions. On Windows, use `pythonw`
instead of `python` or double-click each project's `desktop.pyw` (with Python
file associations configured) to open a window without a console. No additional
runtime packages are needed for these three desktop apps beyond working Tk.

The organizer previews by default. Use its README to practice on a temporary
folder before applying moves. The expense CSV is synthetic. Passwords in saved
sample output are public demonstrations and must not be used as credentials.
Each project README explains its module layout, run/test commands, expected
behavior, limitations, and troubleshooting.

## Tests, samples, and screenshots

```powershell
python scripts/run_project_tests.py
```

The runner isolates every available chapter unittest suite, including Spiral Ink, and records exact
counts and logs under `research/verification/`. Unit tests use temporary files
and synthetic inputs; dashboard interaction uses Streamlit AppTest.
See [the verification report](research/verification/README.md) for exact results,
application checks, and screenshots. Each project's `samples/` contains actual
terminal output or curated sample files; the desktop applications have genuine
captures under `screenshots/`. Each `exercises.md` offers easy, medium, and
advanced challenges.

Optional capture/QR-decoding tools are separate from runtime dependencies:

```powershell
python -m pip install -r scripts/requirements-verification.txt
python -m playwright install chromium
python scripts/capture_project_outputs.py
python scripts/check_beginner_guis.py
python scripts/check_tool_guis.py
```

The capture script runs a temporary local Streamlit server and closes it after
verification. Visual Art Lab retains its existing checker at
`scripts/check_visual_art_lab.py`; the new project runner does not rewrite it.

## Repository records

[AGENTS.md](AGENTS.md) defines coding, testing, documentation, and originality
conventions. The [existing license audit](research/license-audit.md),
[source snapshots](research/source-snapshots.json), and
[adaptation record](research/local-adaptations.json) remain available.
[New project dependency and reference records](research/new-projects-license-audit.md)
track the additions without changing the rights of existing artwork or making
unsupported authorship claims.

This work implements projects only. Book chapters, Word documents, and publisher
materials are deferred.


## Final folder layout and Git hygiene

[folder-structure.txt](folder-structure.txt) lists the source layout. Regenerate
it with `python scripts/show_project_structure.py --write folder-structure.txt`.
Virtual environments, bytecode, local outputs, and transient diagnostic runs are
ignored. Original artwork, curated samples/screenshots, and provenance records
remain eligible for version control. Locally generated verification results are
recreated by the check scripts and are not required in a source checkout.

The [folder standardization audit](research/folder-renames/2026-11-05-final-ten/README.md)
records path changes, preservation checks, and the Git-metadata limitation.
