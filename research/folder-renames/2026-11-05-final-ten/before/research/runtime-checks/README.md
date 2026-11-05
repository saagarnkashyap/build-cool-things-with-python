# Visual Art Lab runtime verification

Updated on 2026-11-05 for **pink lilies, water lily, and Rockstar**.
**All 11 runtime checks and 7 unit tests passed** on Windows with Python
3.14.7, Pillow 12.3.0, and Tk 9.0. No new dependencies were installed.

| Check | Result |
| --- | --- |
| Rockstar PNG export | Passed: 2600 x 4621; decoded and nonuniform |
| Pink lilies PNG export | Passed: 2600 x 2600; decoded and nonuniform |
| Water lily PNG export | Passed: 2600 x 4621; decoded and nonuniform |
| Rockstar animation | Passed: 26,224 / 26,224 glyphs; restart passed |
| Pink lilies animation | Passed: 18,237 / 18,237 glyphs; restart passed |
| Water lily animation | Passed: 26,723 / 26,723 glyphs; restart passed |
| Reject missing input | Passed: exit code 2 |
| Reject empty text | Passed: exit code 2 |
| Reject width below 100 | Passed: exit code 2 |
| Reject source overwrite | Passed: exit code 2 |
| Verify current sources, supplied JPEGs, and removals | Passed |

The photos remain unchanged. All animations completed without recorded callback
errors. The original import manifest is preserved; explicit renames, removals,
and current checksums are tracked in
[local-adaptations.json](../local-adaptations.json).

## Current previews

- [Pink lilies PNG](lilies_spiral.png) and [desktop render](lilies-render.png)
- [Water lily PNG](water_lily_spiral.png) and [desktop render](water-lily-render.png)
- [Rockstar PNG](rockstar_spiral.png) and [desktop render](rockstar-render.png)

All three desktop render buffers were visually inspected. Detailed results and
durations are in [results.json](results.json), with individual `.log` files.
Older preview files in this directory are historical artifacts, not current inputs.

## Reproduce

From the repository root:

```powershell
python -m unittest discover -s projects/visual-art-lab/spiral-ink/tests -v
python scripts/check_visual_art_lab.py --spiral-only
```

The unit tests cover full composition, EXIF rotation, pond shadow lifting, paths
with spaces from another directory, input protection, and CLI configuration.
The [runtime checker](../../scripts/check_visual_art_lab.py) opens `pic1.py`,
`pic2.py`, and the water-lily preset, observes completion, exercises restart
methods, and closes the windows. It also checks full-size PNG exports and four
invalid-input cases. Run without `--spiral-only` to include Bloomcraft and
Heartglow, whose source files were not changed.

## Limits

Python 3.12, other operating systems, different fonts, physical keyboard
shortcuts, manual resizing, and prolonged interactive use were not tested.
Preset gamma lifts shadows in the pond and Rockstar renderings; the pink
lilies retain their original tones.
