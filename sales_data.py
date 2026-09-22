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


def load_sales_data(path):
    """Read the sales CSV, check it has every required column, and parse dates.

    Raises FileNotFoundError if the file doesn't exist, and ValueError
    naming the missing columns if any required column is absent.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Sales data file not found: {path}")

    df = pd.read_csv(path)

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    df["date"] = pd.to_datetime(df["date"])
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
