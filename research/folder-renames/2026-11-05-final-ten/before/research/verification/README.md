# Project verification

Recorded: 2026-11-05 (Asia/Calcutta).

**59 unit/UI tests passed across seven new projects: 0 failures, 0 errors,
0 skips. All 6 simplified-tool desktop checks also passed.**

The four beginner desktop/CLI checks from the preceding update remain recorded below.

The nine earlier application/preservation checks remain recorded below.

## Exact test results

| Project | Tests | Result | Log |
| --- | ---: | --- | --- |
| [01-number-guessing](../../projects/01-number-guessing/README.md) | 9 | Passed | [Log](tests-01-number-guessing.log) |
| [02-rock-paper-scissors](../../projects/02-rock-paper-scissors/README.md) | 8 | Passed | [Log](tests-02-rock-paper-scissors.log) |
| [03-password-generator](../../projects/03-password-generator/README.md) | 8 | Passed | [Log](tests-03-password-generator.log) |
| [07-smart-file-organizer](../../projects/07-smart-file-organizer/README.md) | 9 | Passed | [Log](tests-07-smart-file-organizer.log) |
| [09-qr-code-studio](../../projects/09-qr-code-studio/README.md) | 6 | Passed | [Log](tests-09-qr-code-studio.log) |
| [11-expense-tracker](../../projects/11-expense-tracker/README.md) | 13 | Passed | [Log](tests-11-expense-tracker.log) |
| [16-maze-solving-visualizer](../../projects/16-maze-solving-visualizer/README.md) | 6 | Passed | [Log](tests-16-maze-solving-visualizer.log) |

The expense suite includes three Streamlit AppTest interaction tests, six
pure data tests, and four launcher lifecycle tests. AppTest emits an expected bare-mode ScriptRunContext warning;
no assertion failed. The other tests cover validation, game rules, required
password character groups, organizer recovery/conflicts, QR exports, and graph
search correctness. Individual subtests cover additional input combinations.

[Machine-readable test results](test-results.json) and
[exact environment versions](environment.json) are saved alongside this report.

## Simplified tool desktop verification

| Check | Result |
| --- | --- |
| organizer desktop round trip | Passed: Folder chooser, automatic preview, organize, undo preview, and restore preserved original bytes |
| organizer undo conflict | Passed: Newly created source protected; restore disabled with a useful error |
| QR desktop create and save | Passed: Presets, stale-preview protection, PNG/SVG saving, independent PNG decode, invalid colors, and overwrite protection |
| expense dashboard guided page | Passed: Real browser loaded through launcher; example CSV download matches the synthetic sample |
| expense launcher lifecycle | Passed: Automatic browser-open callback, Stop, restart, and close; both owned processes exited |
| visual art preservation | Passed: All 16 source/artwork files unchanged |

[Click-through check details](tool-gui-checks.json). No Tk callback errors
were recorded. All file operations used temporary synthetic fixtures. A real
browser loaded the launcher-managed dashboard. Its two owned server processes
were both confirmed stopped after Stop/restart/close testing.

- [Organizer](../../projects/07-smart-file-organizer/screenshots/app.png)
- [Undo preview](../../projects/07-smart-file-organizer/screenshots/undo.png)
- [QR Studio](../../projects/09-qr-code-studio/screenshots/app.png)
- [Expense launcher](../../projects/11-expense-tracker/screenshots/launcher.png)
- [Expense dashboard](../../projects/11-expense-tracker/screenshots/app.png)

The updated captures were visually inspected. Run
`python scripts/check_tool_guis.py` to reproduce the guided tool checks.

## Beginner desktop verification

| Check | Result |
| --- | --- |
| number guessing desktop | Passed: Validation, hints, history, win/loss, difficulty reset, and finished-state controls |
| rock paper scissors desktop | Passed: Move-button callbacks, score cards, round history, final state, and reset |
| password generator desktop | Passed: Settings, masking/reveal, mocked clipboard copy, stale-result clearing, invalid input, and clear |
| existing CLI launchers | Passed: All three terminal programs still run; main.py entry points unchanged |

[Desktop check details](beginner-gui-checks.json). No Tk callback errors
were recorded. Clipboard methods were mocked while checking Copy; the actual
system clipboard was not changed. The existing `main.py` entry points remain
unchanged and all three CLI smoke checks passed.

- [Number Guessing desktop](../../projects/01-number-guessing/screenshots/app.png)
- [Rock, Paper, Scissors desktop](../../projects/02-rock-paper-scissors/screenshots/app.png)
- [Password Generator desktop](../../projects/03-password-generator/screenshots/app.png)

All three new window captures were visually inspected. Passwords are masked.
Run `python scripts/check_beginner_guis.py` to reproduce these checks.

## Earlier application checks

| Check | Evidence |
| --- | --- |
| organizer dry run | No fixture paths or contents changed |
| organizer desktop preview | Three planned moves; explicit Apply control |
| organizer apply and undo | Duplicate preserved; every original byte restored |
| QR PNG decode | Independent zxing-cpp decoded the exact URL |
| QR desktop | Valid preview and invalid-size feedback exercised |
| maze desktop animations | Generated and predefined mazes animated; BFS=8, DFS=12 |
| expense dashboard browser | Real page, charts, table, and CSV download captured |
| QR SVG decode | Browser-rendered vector export decoded to the exact URL |
| visual art preservation | All 16 existing source/artwork files unchanged |

[Application check details](application-checks.json). The organizer operated
only on temporary synthetic files. Both default preview and complete apply/undo
were exercised. Existing duplicates retained their original contents.

The QR PNG was independently decoded by zxing-cpp. The SVG was rendered by a
real Chromium browser and then independently decoded. Both decoded to the exact
requested URL, not merely an image with a QR-like pattern.

The maze comparison animated a generated maze and the predefined cyclic maze.
In the latter, BFS explored 17 cells and found an 8-edge route; DFS explored 13
and found a 12-edge route. A shorter exploration count does not imply a shorter path.

The expense dashboard was opened in a real local browser; charts and a downloaded
CSV were captured. The temporary loopback server was stopped after verification.

## Screenshots and terminal transcripts

- [Number Guessing: actual terminal transcript](../../projects/01-number-guessing/samples/terminal-output.txt)
- [Rock, Paper, Scissors: actual terminal transcript](../../projects/02-rock-paper-scissors/samples/terminal-output.txt)
- [Password Generator: public demonstration output](../../projects/03-password-generator/samples/terminal-output.txt)
- [Organizer: working preview window](../../projects/07-smart-file-organizer/screenshots/app.png)
- [QR Studio: working preview window](../../projects/09-qr-code-studio/screenshots/app.png)
- [Expense dashboard: real browser capture](../../projects/11-expense-tracker/screenshots/app.png)
- [Maze: predefined comparison](../../projects/16-maze-solving-visualizer/screenshots/app.png)
- [Maze: generated maze comparison](../../projects/16-maze-solving-visualizer/screenshots/generated.png)

All four earlier application captures and all three new desktop captures were visually inspected. They are screenshots
of the running programs, not rendered mockups. The beginner projects provide
actual subprocess transcripts as well, including the inputs used for deterministic games.

## Preservation and provenance

All 16 pre-existing Visual Art Lab source/artwork files in the
[preservation baseline](visual-art-before.json) retain their original SHA-256
hashes. No completed visual project was rewritten. The three root JPEGs are
included in the preservation check. Existing generated historical previews were
not overwritten. Source and dependency records are maintained in the
[new-project audit](../new-projects-license-audit.md).

## Reproduce and limits

From the repository root, after installing project dependencies:

```powershell
python scripts/run_project_tests.py
python -m pip install -r scripts/requirements-verification.txt
python -m playwright install chromium
python scripts/capture_project_outputs.py
python scripts/check_beginner_guis.py
python scripts/check_tool_guis.py
```

Local execution used Windows, Python 3.14.7, Tk 9.0, and the package versions
in environment.json. All 41 numbered-project and verification Python files also passed Python 3.12 grammar
parsing. Execution on Python 3.12, macOS, and Linux was not available here.
GitHub Actions is configured for Python 3.12 and 3.14 on Linux; that remote
workflow has not been run from this workspace. Captures require a display and
browser installation. Manual phone scanning, printing, and prolonged GUI use
were not tested. Organizer folders must not have unrelated concurrent writers;
copy/permission failures retain data for inspection, and OS-specific ACLs are
not a substitute for backups. No manuscript, Word, or publisher artifact was generated.
