"""Strict CSV validation and integer-cent calculations, independent of the UI."""

import csv
from datetime import date
from decimal import Decimal
import io
import re

import pandas as pd

COLUMNS = ["date", "category", "description", "amount"]


def parse_expenses(content: bytes) -> pd.DataFrame:
    if len(content) > 5_000_000:
        raise ValueError("CSV must be smaller than 5 MB.")
    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")), strict=True)
        if reader.fieldnames is None or sorted(reader.fieldnames) != sorted(COLUMNS):
            raise ValueError("CSV needs exactly these columns: date,category,description,amount.")
        rows = []
        for number, row in enumerate(reader, start=2):
            if number > 10_001:
                raise ValueError("Use at most 10,000 expense rows.")
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Row {number}: wrong number of fields.")
            values = {key: value.strip() for key, value in row.items()}
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", values["date"]):
                raise ValueError(f"Row {number}: dates must use YYYY-MM-DD.")
            try:
                day = date.fromisoformat(values["date"])
            except ValueError:
                raise ValueError(f"Row {number}: invalid calendar date.") from None
            if not 1900 <= day.year <= 2100:
                raise ValueError(f"Row {number}: use dates between 1900 and 2100.")
            if not values["category"] or len(values["category"]) > 80 or len(values["description"]) > 300:
                raise ValueError(f"Row {number}: use a category (1-80 characters) and description up to 300 characters.")
            if not re.fullmatch(r"(0|[1-9]\d{0,8})(\.\d{1,2})?", values["amount"]):
                raise ValueError(f"Row {number}: amount must be nonnegative, at most 999999999.99, with up to two decimal places.")
            rows.append({"date": pd.Timestamp(day), "category": values["category"],
                         "description": values["description"],
                         "amount_cents": int(Decimal(values["amount"]) * 100)})
        if not rows:
            raise ValueError("CSV needs at least one expense row.")
        return pd.DataFrame(rows).sort_values("date", kind="stable").reset_index(drop=True)
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError(f"Read a UTF-8 CSV with consistent quoting: {exc}") from None


def filter_expenses(data: pd.DataFrame, categories: list[str], start: date,
                    end: date, query: str = "") -> pd.DataFrame:
    if start > end:
        raise ValueError("Start date must not be after end date.")
    mask = (data["category"].isin(categories) & data["date"].between(pd.Timestamp(start), pd.Timestamp(end)))
    if query.strip():
        mask &= data["description"].str.contains(query.strip(), case=False, regex=False)
    return data.loc[mask].copy()


def category_summary(data: pd.DataFrame) -> pd.DataFrame:
    return data.groupby("category", as_index=False)["amount_cents"].sum().sort_values("amount_cents", ascending=False)


def monthly_summary(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(columns=["month", "amount_cents"])
    periods = data["date"].dt.to_period("M")
    totals = data.groupby(periods)["amount_cents"].sum()
    months = pd.period_range(periods.min(), periods.max(), freq="M")
    totals = totals.reindex(months, fill_value=0)
    return pd.DataFrame({"month": months.to_timestamp(), "amount_cents": totals.to_numpy()})


def format_amount(cents: int) -> str:
    return f"{Decimal(int(cents)) / 100:,.2f}"


def export_csv(data: pd.DataFrame) -> bytes:
    """Escape spreadsheet formula prefixes in user-provided text fields."""
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(COLUMNS)
    for row in data.itertuples(index=False):
        text = [value if not value.lstrip().startswith(("=", "+", "-", "@")) else "'" + value
                for value in (row.category, row.description)]
        writer.writerow([row.date.strftime("%Y-%m-%d"), *text, f"{Decimal(int(row.amount_cents)) / 100:.2f}"])
    return output.getvalue().encode("utf-8")
