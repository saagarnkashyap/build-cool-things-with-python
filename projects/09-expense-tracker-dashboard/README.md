# Expense Tracker Dashboard

Explore a validated expense CSV with interactive category and date filters, a description search, summaries, monthly trends, and a filtered CSV download.

## Learning objectives

- Validate uploaded CSV data before constructing a DataFrame.
- Aggregate exact integer cents and use Pandas for grouped summaries.
- Build native Streamlit controls and test interaction with AppTest.

## Installation

Install Streamlit and Pandas: `python -m pip install -r requirements.txt`. The requirements file records supported version ranges.

Run the commands below **from this project folder**. From the repository root,
first run `cd projects/09-expense-tracker-dashboard`. Activate your Python environment first.

## Open the dashboard without a terminal

Double-click `desktop.pyw` on Windows (with Python file associations configured),
or run `python gui.py` from this project folder. After the first-time dependency
installation above, the launcher starts the local dashboard and opens your
browser automatically. It prefers the repository's `.venv` when available.

1. Try the sample data, or use **Choose an expense CSV** in the browser.
2. Use **CSV format and example** to download a ready-to-edit example.
3. Adjust the filters, or click **Reset filters** to show everything again.
4. Click **Download filtered CSV** when ready.

Keep the small launcher window open while using the dashboard. **Open dashboard**
reopens its browser page, **Stop** shuts down its own server, and **Start dashboard**
starts it again. Closing the launcher also stops its server. Nothing is published;
the server listens only on this computer. Startup problems appear in the launcher,
with **Setup help** for details. The terminal launch below remains available.

[Launcher](screenshots/launcher.png) / [dashboard](screenshots/app.png).

## Usage

```powershell
python -m streamlit run app.py --server.address 127.0.0.1
```

The included `samples/expenses.csv` is entirely synthetic. Required columns are `date,category,description,amount`. Dates use YYYY-MM-DD in 1900-2100. Amounts are nonnegative decimal values with at most two fractional digits and a maximum of 999999999.99. Use one currency per file; no conversion is attempted. Files are limited to 5 MB and 10,000 rows. Invalid rows reject the entire upload with a row-specific error rather than silently changing totals.

Calculations use integer cents; charts convert values only for display. Missing months between selected transactions appear as zero. Clearing category selection intentionally shows an empty state. CSV export escapes spreadsheet formula prefixes in text. Uploaded data is held in a bounded in-process cache, not written to a database or sent to a third-party API. Run locally for personal data and close the server when finished. This is an educational analytics tool.

## Tests and representative output

```powershell
python -m unittest discover -s tests -v
```

[Application capture](screenshots/app.png). See [samples](samples/) for outputs from real execution and
[exercises](exercises.md) for follow-up challenges. The repository-wide test
command is `python scripts/run_project_tests.py` from the repository root.

## Troubleshooting

Use `gui.py` for the launcher, or `python -m streamlit run app.py` for terminal startup; running `python app.py` directly does not start the server. Install requirements in the same environment. Fix the exact row reported by CSV validation. Decimal commas, currency symbols, negative refunds, NaN, and more than two decimal places are not accepted. The dashboard needs both endpoints of the date range. A blank result may simply mean no category is selected.


To exercise the click-through flows and regenerate the real captures, run
`python scripts/check_tool_guis.py` from the repository root. This optional
verification command uses the capture dependencies in
`scripts/requirements-verification.txt`; it stops its temporary local server.
