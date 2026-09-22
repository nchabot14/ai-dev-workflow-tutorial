"""Load ShopSmart sales data and calculate the numbers shown on the dashboard.

This module uses only Pandas (no Streamlit or Plotly), so every function
can be tested with pytest without starting the app.
"""

from pathlib import Path

import pandas as pd

# The 8 columns the PRD says sales-data.csv must have.
REQUIRED_COLUMNS = [
    "date",
    "order_id",
    "product",
    "category",
    "region",
    "quantity",
    "unit_price",
    "total_amount",
]

# Columns that must hold a number on every row.
NUMERIC_COLUMNS = ["quantity", "unit_price", "total_amount"]

# Columns the charts group by; a blank one would drop its row from the chart.
GROUP_COLUMNS = ["category", "region"]


def load_sales_data(path):
    """Read the sales CSV, check its columns and values, and parse dates.

    Raises FileNotFoundError if the file doesn't exist, and ValueError if a
    required column is absent, the file has no rows, a date is blank or
    unreadable, a category or region is blank, or a numeric column holds
    anything but a finite, non-negative number (e.g. "$12.99", N/A, inf, -5).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Sales data file not found: {path}")

    df = pd.read_csv(path)

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    if df.empty:
        raise ValueError("The sales data file has no rows.")

    # Checked here so bad values fail loudly instead of skewing the totals later.
    # Every row must be usable by every chart, or the charts won't add up to the KPIs.
    for column in NUMERIC_COLUMNS:
        numbers = pd.to_numeric(df[column], errors="coerce")
        bad = numbers.isna() | (numbers < 0) | (numbers == float("inf"))
        if bad.any():
            raise ValueError(
                f"Column {column} has {int(bad.sum())} value(s) that are not "
                "valid amounts (blank, text, negative or infinite)."
            )
        df[column] = numbers

    for column in GROUP_COLUMNS:
        blank = df[column].isna() | (df[column].astype(str).str.strip() == "")
        if blank.any():
            raise ValueError(f"Column {column} has {int(blank.sum())} blank value(s).")

    dates = pd.to_datetime(df["date"], errors="coerce")
    bad_dates = int(dates.isna().sum())
    if bad_dates:
        raise ValueError(f"Column date has {bad_dates} value(s) that are blank or not dates.")
    df["date"] = dates
    return df


def total_sales(df):
    """Sum of every transaction's total_amount."""
    return float(df["total_amount"].sum())


def total_orders(df):
    """Number of distinct orders (an order spread over several rows counts once)."""
    return int(df["order_id"].nunique())


def format_currency(value):
    """Whole dollars with thousands separators, e.g. 116500.21 -> "$116,500"."""
    return f"${value:,.0f}"


def format_count(value):
    """Whole number with thousands separators, e.g. 1234 -> "1,234"."""
    return f"{value:,}"


def sales_by_month(df):
    """Total sales per calendar month, oldest first.

    Returns columns "month" (first day of each month) and "total_amount".
    A month with no sales between the first and last month appears with 0.
    """
    monthly = df.resample("MS", on="date")["total_amount"].sum().reset_index()
    return monthly.rename(columns={"date": "month"})


def _sales_by(df, column):
    """Total sales for each value in `column`, highest first."""
    return (
        df.groupby(column, as_index=False)["total_amount"]
        .sum()
        .sort_values("total_amount", ascending=False, ignore_index=True)
    )


def sales_by_category(df):
    """Total sales per product category, highest first."""
    return _sales_by(df, "category")


def sales_by_region(df):
    """Total sales per region, highest first."""
    return _sales_by(df, "region")
