"""Regression checks for the supplied photos and safe image handling."""

import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import spiral_art


class PhotoHandlingTests(unittest.TestCase):
    def setUp(self):
        for name in ("TEXT_PHRASE", "OUT_PATH", "IMAGE_GAMMA", "WINDOW_TITLE"):
            self.addCleanup(setattr, spiral_art, name, getattr(spiral_art, name))

    def test_all_three_photos_keep_their_full_composition(self):
        for preset in spiral_art.PRESETS.values():
            with self.subTest(photo=preset.filename):
                spiral_art.IMAGE_GAMMA = preset.gamma
                with Image.open(preset.path) as original:
                    expected_size = original.size
                rendered_source = spiral_art.load_source(preset.path)
                self.assertEqual(rendered_source.size, expected_size)
                self.assertEqual(rendered_source.mode, "RGB")

    def test_pond_shadow_lift_preserves_black_and_brightens_dark_pixels(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dark.png"
            source = Image.new("RGB", (2, 1))
            source.putpixel((1, 0), (30, 40, 50))
            source.save(path)
            spiral_art.IMAGE_GAMMA = spiral_art.PRESETS["water-lily"].gamma
            result = spiral_art.load_source(path)
            self.assertEqual(result.getpixel((0, 0)), (0, 0, 0))
            self.assertTrue(all(a > b for a, b in zip(result.getpixel((1, 0)), (30, 40, 50))))

    def test_exif_rotation_is_applied(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "rotated.jpg"
            image = Image.new("RGB", (20, 10), "red")
            metadata = image.getexif()
            metadata[274] = 6
            image.save(path, exif=metadata)
            self.assertEqual(spiral_art.load_source(path).size, (10, 20))

    def test_root_relative_filename_resolves_outside_repository(self):
        with tempfile.TemporaryDirectory() as folder, contextlib.chdir(folder):
            # Resolution falls back to the explicit repository root.
            filename = spiral_art.PRESETS["lilies"].filename
            self.assertEqual(spiral_art.resolve_image_path(filename), spiral_art.PRESETS["lilies"].path)

    def test_export_refuses_to_overwrite_an_input_photo(self):
        path = spiral_art.PRESETS["lilies"].path
        original = path.read_bytes()
        with self.assertRaisesRegex(ValueError, "same as the source"):
            spiral_art.save_png(path, path, width=100)
        self.assertEqual(path.read_bytes(), original)

    def test_custom_image_uses_neutral_text_and_unmodified_colors(self):
        path = spiral_art.PRESETS["water-lily"].path
        arguments = ["spiral_art.py", str(path), "--png"]
        with patch.object(sys, "argv", arguments), patch.object(spiral_art, "save_png") as export:
            spiral_art.main()
        self.assertEqual(spiral_art.TEXT_PHRASE, "SPIRAL INK  ")
        self.assertEqual(spiral_art.IMAGE_GAMMA, 1.0)
        export.assert_called_once()

    def test_empty_text_is_rejected_before_rendering(self):
        with patch.object(sys, "argv", ["spiral_art.py", "--text", " "]), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                spiral_art.main()
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
