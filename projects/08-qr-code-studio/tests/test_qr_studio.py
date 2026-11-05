from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qr_studio import export_qr, make_matrix


class QRTests(unittest.TestCase):
    def test_quiet_zone_and_square_matrix(self):
        matrix = make_matrix("Hello Python")
        self.assertTrue(all(len(row) == len(matrix) for row in matrix))
        self.assertTrue(all(not value for row in matrix[:4] for value in row))
        self.assertTrue(all(not value for row in matrix for value in row[:4]))

    def test_unicode_text(self):
        self.assertTrue(make_matrix("Hello \u4e16\u754c"))

    def test_both_exports_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            png, svg = (Path(folder) / name for name in ("code.png", "code.svg"))
            export_qr("https://www.python.org/", png, scale=6)
            export_qr("https://www.python.org/", svg, foreground="#112233")
            with Image.open(png) as image:
                self.assertEqual(image.width, image.height)
                self.assertEqual(image.getpixel((0, 0)), (255, 255, 255))
            self.assertTrue(ET.parse(svg).getroot().tag.endswith("svg"))
            with self.assertRaises(FileExistsError):
                export_qr("different", png)

    def test_bad_urls(self):
        for value in ("https://", "http:/bad", "ftp://example.org", "https://example.org:bad", "https://a b"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                make_matrix(value)

    def test_bad_settings(self):
        for text, scale, dark, light in ((" ", 10, "black", "white"), ("ok", 1, "black", "white"),
                                        ("ok", 10, "white", "black"), ("ok", 10, "#aaa", "white"),
                                        ("ok", 10, "nonsense", "white"), ("x" * 1201, 10, "black", "white")):
            with self.subTest(text=text[:5], scale=scale, dark=dark), self.assertRaises(ValueError):
                make_matrix(text, scale, dark, light)

    def test_invalid_extension(self):
        with self.assertRaises(ValueError):
            export_qr("hello", Path("test.jpg"))
