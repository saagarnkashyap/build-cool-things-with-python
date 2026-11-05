from pathlib import Path
import sys
import unittest
from streamlit.testing.v1 import AppTest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))


class DashboardTests(unittest.TestCase):
    def test_reset_restores_default_filters(self):
        app = AppTest.from_file(str(PROJECT / "app.py"), default_timeout=20).run()
        app.multiselect(key="categories").set_value(["Transport"]).run()
        app.text_input(key="query").set_value("no matching row").run()
        self.assertEqual(app.metric[1].value, "0")
        app.button(key="reset_filters").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, "12")
        self.assertEqual(app.text_input(key="query").value, "")

    def test_sample_loads_and_filter_changes_totals(self):
        app = AppTest.from_file(str(PROJECT / "app.py"), default_timeout=20).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, "12")
        app.multiselect(key="categories").set_value(["Transport"]).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "54.00")
        self.assertEqual(app.metric[1].value, "3")

    def test_empty_filter_and_text_search(self):
        app = AppTest.from_file(str(PROJECT / "app.py"), default_timeout=20).run()
        app.text_input(key="query").set_value("museum").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, "1")
        app.multiselect(key="categories").set_value([]).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, "0")
        self.assertTrue(any("No expenses" in info.value for info in app.info))
