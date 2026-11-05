# Final ten-project folder audit

Recorded: 2026-11-05. Scope: folder numbering, references, launch commands,
preservation, and local verification. No chapters or Word documents were created.

## Folder changes

All six moves were checked against the workspace boundary and existing targets
before moving. No target directory existed, and no asset was overwritten.

| Previous folder under `projects/` | Final folder under `projects/` |
| --- | --- |
| `09-qr-code-studio` | `08-qr-code-studio` |
| `11-expense-tracker` | `09-expense-tracker-dashboard` |
| `16-maze-solving-visualizer` | `10-maze-solving-visualizer` |
| `visual-art-lab/bloomcraft` | `visual-art-lab/04-bloomcraft` |
| `visual-art-lab/heartglow` | `visual-art-lab/05-heartglow` |
| `visual-art-lab/spiral-ink` | `visual-art-lab/06-spiral-ink` |

The 01, 02, 03, and 07 folders and the Visual Art Lab container retain their
names. Chapter prefixes inside Visual Art Lab complete the 01-10 sequence.
The [repository map](../../../folder-structure.txt) omits local environments,
caches, and runtime diagnostics; regenerate it with
`python scripts/show_project_structure.py --write folder-structure.txt`.

## Reference inventory and implementation

Before moving, [the inventory](reference-inventory.json) identified 18 referencing
files: eight READMEs, three scripts, two configurations, and five documentation
or provenance records. Tests were also inspected; their imports derive the
project directory rather than hardcoding the old folder names. Exact original
documents and verification records are retained in [before/](before/).

Updated references include the root and project READMEs, license/provenance
paths, verification documentation, capture/check scripts, pytest configuration,
and GitHub Actions dependency paths. Historical log contents remain historical.
The two QR/expense desktop chapter badges now display 08 and 09. Project logic,
module names, entry-point filenames, and dependencies were preserved.

The test runner now includes the numbered visual project test directory.
The art checker accepts a fresh `--output-dir`, allowing new runtime checks
without replacing saved artwork. The source-focused tree helper replaces the
previous listing of the entire virtual environment.

## Verification results

| Verification | Exact result |
| --- | --- |
| Complete available unittest suites | 66 tests across eight suites; zero failures, errors, or skips |
| Pytest configured discovery | 66 tests collected |
| Visual export, animation, invalid-input, source-integrity checks | 15 passed |
| CLI help, desktop entry points, maze solving, PNG/SVG exports, real expense browser page | 22 passed |
| Git ignore probes | 11 generated paths ignored; 11 curated/source paths remain eligible |
| Existing artwork/animation/canvas assets | All 42 SHA-256 hashes unchanged |
| Project Python sources | 41 of 43 byte-identical; only two chapter badge strings changed |
| Python compatibility syntax | All 49 project and shared-script files parse with Python 3.12 grammar |
| Documentation navigation | 120 active local Markdown links checked; zero broken links |

The unit suites contain 9 guessing, 8 RPS, 8 password, 7 Spiral Ink, 9 organizer,
6 QR, 13 expense, and 6 maze tests. Bloomcraft and Heartglow have no unit suites;
their real exports/animations were exercised by the visual checker.

Evidence: [unit results](../../verification/test-results.json),
[visual results](runtime-outputs/visual/results.json),
[launch results](runtime-outputs/launch/results.json),
[integrity results](integrity-results.json), and
[ignore audit](git-ignore-audit.json). The [documentation link audit](documentation-links.json)
records navigation checks. Runtime outputs and test logs are local
ignored diagnostics; the summaries and preservation manifests remain eligible
for version control.

Local execution used Windows, Python 3.14.7, and a real Chromium browser for the
expense dashboard. Desktop entry points were opened and closed programmatically,
with callback errors checked; the renamed QR/expense badges were inspected.
The expense launcher's own local server was stopped after checking the page.
Python 3.12 was checked by grammar parsing, not by executing that interpreter.
Remote GitHub Actions and other operating systems were not run.

## Assets, provenance, and Git limits

All existing artwork and screenshots were preserved, including original root
JPEGs and historical runtime previews. Existing captures may show earlier chapter
numbers. All Visual Art Lab Python sources remain byte-identical. The original
source commits, archive hashes, imported-file checksums, upstream license file,
and permission statuses remain intact. Only local path references changed in
the existing source/license audit; intentional README hash updates are backed
by the exact original records in `before/`.

There is no `.git` directory in this workspace or its parent directories.
Git-aware moves and an index inspection were therefore unavailable; filesystem
renames preserved the contents. No root repository was initialized.

`.gitignore` covers `.venv/`, `__pycache__/`, bytecode, test/coverage caches,
project outputs, organizer journals, cloned references, and transient verification
files. Git itself checked the ignore rules in a disposable scratch repository;
curated artwork, project samples/screenshots, license records, and the folder map
remain eligible for tracking. [The generated-file inventory](generated-file-inventory.json)
records local counts and examples. **Already-tracked generated files cannot be
identified without the original Git index.** Nothing was deleted or untracked.
In the actual Git checkout, inspect that remaining question with
`git ls-files --cached --ignored --exclude-standard` before taking any action.

To repeat the core checks from the root:

```powershell
python scripts/run_project_tests.py
python -m pytest --collect-only -q
# Choose a fresh directory for every art run.
python scripts/check_visual_art_lab.py --output-dir outputs/final-layout-check
python research/folder-renames/2026-11-05-final-ten/verify-integrity.py
```

Art checks require the existing visual dependencies and a display. The extra
browser verification used the existing optional verification dependencies;
no application runtime dependencies were added.
