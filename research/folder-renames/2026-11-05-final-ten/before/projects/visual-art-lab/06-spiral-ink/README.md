# Spiral Ink

Animate the three current photos as thousands of letters arranged in a spiral.
The complete image and its aspect ratio are preserved, with no portrait mask,
flag overlay, or fixed crop. Source photos remain unchanged.

| Preset | Photo in the repository root | Repeated text | Treatment |
| --- | --- | --- | --- |
| `lilies` (default) | `Pink lilies.jpg` | `LILIES` | Preserve the soft pink petals and natural highlights |
| `water-lily` | `900508888014745363.jpg` | `WATER LILY` | Lift the dark pond details while retaining the reflections |
| `rockstar` | `Rockstar.jpg` | `ROCKSTAR` | Lift the performer's shadows while keeping the warm flames |

Keep these JPEG files in the repository root with their current names. Preset
paths are resolved relative to the code, so they work from other directories too.

## Install and run

Use Python 3.12 or later with Pillow. Desktop animations also require Tk:

```powershell
python -m pip install pillow
# Pink lilies
python projects/visual-art-lab/spiral-ink/pic2.py
# Rockstar
python projects/visual-art-lab/spiral-ink/pic1.py
# Water lily
python projects/visual-art-lab/spiral-ink/spiral_art.py --preset water-lily
```

The shared renderer accepts `--preset lilies`, `--preset water-lily`, or
`--preset rockstar`. Running it without arguments opens the pink lilies.
Both `pic1.py` and `pic2.py` accept the same options. NumPy is not required for
Spiral Ink. Test Tk with `python -m tkinter`.

## Save and customize

```powershell
python projects/visual-art-lab/spiral-ink/pic2.py --png
python projects/visual-art-lab/spiral-ink/pic1.py --png --width 1400
python projects/visual-art-lab/spiral-ink/spiral_art.py --preset water-lily --text "REFLECTIONS  "
python projects/visual-art-lab/spiral-ink/spiral_art.py "path/to/my photo.jpg" --png --output "my-art.png"
```

Default exports go into `projects/visual-art-lab/spiral-ink/outputs/` as
`<photo-name>_spiral.png`. Explicit `--output` paths are relative to the current
working directory; missing output folders are created. Saving over the input
image is rejected. Custom images use neutral `SPIRAL INK` text and their original
colors. Use `--text` to set your own words. EXIF rotation is respected.

In an animation window, press **S** to save a full-size PNG, **R** to restart, or
**Esc** to close. PNG exports work without opening a desktop window.

## Tests and previews

From the repository root:

```powershell
python -m unittest discover -s projects/visual-art-lab/spiral-ink/tests -v
python scripts/check_visual_art_lab.py --spiral-only
```

Unit tests cover source dimensions, shadow lifting, EXIF orientation, paths with
spaces, source protection, and CLI configuration. Runtime checks export all three
photos, run all three animations to completion, and check invalid inputs.
[Results and previews](../../../research/runtime-checks/README.md) are saved under
`research/runtime-checks/`.

## Provenance

The spiral drawing algorithm is adapted from the imported source in the
[snapshot manifest](../../../research/source-snapshots.json). The launch scripts
were renamed to `pic1.py` and `pic2.py`. The earlier source photos have been
replaced with the three JPEGs above. Current checksums and removals are recorded
in [local-adaptations.json](../../../research/local-adaptations.json).
Image origins and publication permissions are tracked in the
[license audit](../../../research/license-audit.md).
