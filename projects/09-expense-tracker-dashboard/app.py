"""A local dashboard using synthetic data unless the user uploads a CSV."""

from pathlib import Path
import hashlib

import streamlit as st
from expenses import category_summary, export_csv, filter_expenses, format_amount, monthly_summary, parse_expenses

st.set_page_config(page_title="Expense tracker", page_icon=":material/receipt_long:", layout="wide")
st.title("Expense tracker")
st.caption("Explore spending patterns. One currency per file; all amounts use the same units.")
st.caption("Choose a CSV, adjust the filters, then download the rows you need.")


@st.cache_data(max_entries=8, show_spinner=False)
def load_data(content: bytes):
    return parse_expenses(content)


with st.sidebar:
    st.header("1. Choose your data")
    upload = st.file_uploader("Choose an expense CSV", type="csv", max_upload_size=5)
    with st.expander("CSV format and example"):
        st.caption("Columns: date, category, description, amount. Dates: YYYY-MM-DD. Amounts: 12.50, without a currency symbol.")
        st.download_button("Download example CSV", (Path(__file__).parent / "samples/expenses.csv").read_bytes(),
                           file_name="expense-example.csv", mime="text/csv", on_click="ignore")

content = upload.getvalue() if upload else (Path(__file__).parent / "samples/expenses.csv").read_bytes()
try:
    data = load_data(content)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

if upload is None:
    st.info("Try the sample data below, or choose your own CSV on the left.")


def reset_filters():
    st.session_state["categories"] = sorted(data["category"].unique())
    st.session_state["date_range"] = (data["date"].min().date(), data["date"].max().date())
    st.session_state["query"] = ""


dataset_id = hashlib.sha256(content).hexdigest()
if st.session_state.get("dataset_id") != dataset_id:
    reset_filters()
    st.session_state["dataset_id"] = dataset_id

with st.sidebar:
    st.header("2. Explore your spending")
    st.button("Reset filters", key="reset_filters", on_click=reset_filters)
    categories = st.multiselect("Categories", sorted(data["category"].unique()),
                               key="categories")
    selected_dates = st.date_input("Date range", key="date_range",
                                   min_value=data["date"].min().date(), max_value=data["date"].max().date())
    query = st.text_input("Description contains", key="query")

if len(selected_dates) != 2:
    st.info("Choose both a start date and an end date.")
    st.stop()
filtered = filter_expenses(data, categories, *selected_dates, query)
total = int(filtered["amount_cents"].sum())
with st.container(horizontal=True):
    st.metric("Total expenses", format_amount(total), border=True)
    st.metric("Transactions", str(len(filtered)), border=True)
    st.metric("Categories", str(filtered["category"].nunique()), border=True)

if filtered.empty:
    st.info("No expenses match these filters. Broaden the dates or select more categories.")
else:
    left, right = st.columns(2)
    with left, st.container(border=True):
        st.subheader("By category")
        summary = category_summary(filtered).assign(amount=lambda frame: frame["amount_cents"] / 100)
        st.bar_chart(summary, x="category", y="amount", color="#0f766e", height=300,
                     x_label="Category", y_label="Amount",
                     alt="Total expenses by category for the selected rows")
    with right, st.container(border=True):
        st.subheader("Monthly trend")
        trend = monthly_summary(filtered).assign(amount=lambda frame: frame["amount_cents"] / 100)
        st.line_chart(trend, x="month", y="amount", color="#7c3aed", height=300,
                      x_label="Month", y_label="Amount",
                      alt="Monthly expense totals, including zero-spend months between transactions")

st.subheader("Selected transactions")
display = filtered.assign(amount=filtered["amount_cents"].map(lambda value: f"{value / 100:.2f}"))
display["date"] = display["date"].dt.date
st.dataframe(display.drop(columns="amount_cents"), hide_index=True,
             alt="Expense transactions matching the current filters")
st.download_button("Download filtered CSV", export_csv(filtered), file_name="filtered-expenses.csv", mime="text/csv")
