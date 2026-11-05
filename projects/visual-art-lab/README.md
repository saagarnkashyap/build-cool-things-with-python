# Visual Art Lab

Chapters 04, 05, and 06 of the final ten-project sequence: **Bloomcraft**, **Heartglow**, and **Spiral Ink**.
Bloomcraft and Heartglow retain their imported sources. Spiral Ink has been
adapted to the three supplied photos and a shared renderer.

## Set up

Use Python 3.12 or later. From the repository root:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install pillow numpy
```

On macOS or Linux, use `.venv/bin/python` instead. Use that environment's Python
for the commands below. Bloomcraft needs Pillow and NumPy. Spiral Ink needs
Pillow. Heartglow uses only the standard library. Desktop animations need Tk and
a graphical display; check Tk with `python -m tkinter`. Font availability affects
multilingual text. Dependency versions are not yet pinned.

## Run

| Project | Command from the repository root |
| --- | --- |
| 04 Bloomcraft | `python projects/visual-art-lab/04-bloomcraft/flow.py` |
| 05 Heartglow | `python projects/visual-art-lab/05-heartglow/love.py` |
| 06 Spiral Ink: water lily | `python projects/visual-art-lab/06-spiral-ink/spiral_art.py --preset water-lily` |
| 06 Spiral Ink: pink lilies | `python projects/visual-art-lab/06-spiral-ink/pic2.py` |
| 06 Spiral Ink: Rockstar | `python projects/visual-art-lab/06-spiral-ink/pic1.py` |

Bloomcraft's upstream README names `flower.py`; the actual script is `flow.py`.
Its `--png` and `--gif` options save into the current working directory.

The [Spiral Ink guide](06-spiral-ink/README.md) explains the three photos, custom
text, exports, and controls. Its renamed `pic2.py` and `pic1.py` launchers
open pink lilies and Rockstar respectively. The shared renderer defaults to
pink lilies and also supports `--preset water-lily`. Keep `Pink lilies.jpg`,
`Rockstar.jpg`, and `900508888014745363.jpg` in the repository root.

## Verify

```powershell
python -m unittest discover -s projects/visual-art-lab/06-spiral-ink/tests -v
python scripts/check_visual_art_lab.py --spiral-only
```

To check Bloomcraft and Heartglow as well, run the checker without
`--spiral-only`. It opens animation windows, observes completion, and closes
them automatically. Use `--output-dir` with a fresh directory to preserve existing
exports and captures. Logs, exports, captures, and the latest machine-readable
results are in [runtime-checks](../../research/runtime-checks/README.md).
Use `--only heartglow-gui` or another listed case to rerun a single check.

The checker validates original upstream files against
[source-snapshots.json](../../research/source-snapshots.json), accounting for
the changes, removals, and added assets explicitly recorded in
[local-adaptations.json](../../research/local-adaptations.json). The original
snapshot manifest remains a historical import record.

Python 3.14.7 is available in this workspace; Python 3.12 execution has not been
tested. The original Bloomcraft and Heartglow READMEs link to external screenshots
that require internet access.

## Source records

See the [license audit](../../research/license-audit.md) for source repositories,
asset origins, and permission status. Local project names do not change ownership
or license status.
