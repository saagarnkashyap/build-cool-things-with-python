from datetime import date
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from expenses import category_summary, export_csv, filter_expenses, monthly_summary, parse_expenses

HEADER = "date,category,description,amount\n"


class ExpenseTests(unittest.TestCase):
    def test_exact_decimal_totals_and_missing_month(self):
        data = parse_expenses((HEADER + "2026-01-01,Food,a,0.10\n2026-03-01,Food,b,0.20\n").encode())
        self.assertEqual(int(category_summary(data)["amount_cents"].sum()), 30)
        self.assertEqual(monthly_summary(data)["amount_cents"].tolist(), [10, 0, 20])

    def test_filters_are_inclusive_and_empty_selection_is_empty(self):
        data = parse_expenses((HEADER + "2026-01-01,Food,Tea,2.50\n").encode())
        day = date(2026, 1, 1)
        self.assertEqual(len(filter_expenses(data, ["Food"], day, day, "tea")), 1)
        self.assertTrue(filter_expenses(data, [], day, day).empty)

    def test_bad_values(self):
        for row in ("2026-02-30,Food,a,1", "2026-01-01,,a,1", "2026-01-01,Food,a,NaN",
                    "2026-01-01,Food,a,-2", "2026-01-01,Food,a,1.005", "2026-01-01,Food,a,1,2"):
            with self.subTest(row=row), self.assertRaises(ValueError):
                parse_expenses((HEADER + row).encode())

    def test_bad_structure_and_encoding(self):
        for content in (b"", HEADER.encode(), b"date,amount\n2026-01-01,2", b"\xff"):
            with self.assertRaises(ValueError):
                parse_expenses(content)

    def test_formula_safe_export_and_ordinary_round_trip(self):
        data = parse_expenses((HEADER + "2026-01-01,Food,=SUM(A1),2.50\n").encode())
        self.assertIn(b"'=SUM(A1)", export_csv(data))
        data["description"] = "Tea"
        self.assertEqual(parse_expenses(export_csv(data))["amount_cents"].tolist(), [250])

    def test_reversed_date_range(self):
        data = parse_expenses((HEADER + "2026-01-01,Food,a,1").encode())
        with self.assertRaises(ValueError):
            filter_expenses(data, ["Food"], date(2026, 2, 1), date(2026, 1, 1))
