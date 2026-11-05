import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from organizer import apply_moves, plan_moves, undo_moves


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "note.TXT").write_text("keep this")

    def test_preview_does_not_change_anything(self):
        plan = plan_moves(self.root)
        self.assertEqual(plan[0]["destination"], "Documents/note.TXT")
        self.assertEqual([p.name for p in self.root.iterdir()], ["note.TXT"])

    def test_duplicate_name_and_round_trip(self):
        (self.root / "Documents").mkdir()
        (self.root / "Documents/note.TXT").write_text("different")
        plan = plan_moves(self.root)
        self.assertEqual(plan[0]["destination"], "Documents/note (2).TXT")
        manifest, errors = apply_moves(self.root, plan)
        self.assertEqual(errors, [])
        self.assertFalse((self.root / "note.TXT").exists())
        self.assertEqual(len(undo_moves(manifest)), 1)
        undo_moves(manifest, apply=True)
        self.assertEqual((self.root / "note.TXT").read_text(), "keep this")
        self.assertEqual((self.root / "Documents/note.TXT").read_text(), "different")
        self.assertEqual(undo_moves(manifest, apply=True), [])

    def test_reject_stale_plan(self):
        plan = plan_moves(self.root)
        (self.root / "note.TXT").write_text("changed")
        with self.assertRaises(ValueError):
            apply_moves(self.root, plan)

    def test_undo_refuses_changed_content(self):
        manifest, _ = apply_moves(self.root, plan_moves(self.root))
        (self.root / "Documents/note.TXT").write_text("edited")
        with self.assertRaises(ValueError):
            undo_moves(manifest, apply=True)

    def test_undo_refuses_overwrite(self):
        manifest, _ = apply_moves(self.root, plan_moves(self.root))
        (self.root / "note.TXT").write_text("new document")
        with self.assertRaises(FileExistsError):
            undo_moves(manifest, apply=True)

    def test_tampered_manifest_cannot_escape_root(self):
        manifest, _ = apply_moves(self.root, plan_moves(self.root))
        data = json.loads(manifest.read_text())
        data["entries"][0]["source"] = "../outside.txt"
        manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            undo_moves(manifest, apply=True)

    def test_failed_move_leaves_input_and_journal(self):
        with patch("organizer.shutil.copyfileobj", side_effect=PermissionError("locked")):
            manifest, errors = apply_moves(self.root, plan_moves(self.root))
        self.assertTrue(errors)
        self.assertTrue((self.root / "note.TXT").is_file())
        self.assertEqual(json.loads(manifest.read_text())["entries"][0]["status"], "failed")

    def test_pending_move_can_be_recovered(self):
        manifest, _ = apply_moves(self.root, plan_moves(self.root))
        data = json.loads(manifest.read_text())
        data["entries"][0]["status"] = "pending"
        manifest.write_text(json.dumps(data))
        undo_moves(manifest, apply=True)
        self.assertTrue((self.root / "note.TXT").is_file())

    def test_skip_directories_and_hidden_files(self):
        (self.root / "nested").mkdir()
        (self.root / ".hidden").write_text("untouched")
        self.assertEqual(len(plan_moves(self.root)), 1)
