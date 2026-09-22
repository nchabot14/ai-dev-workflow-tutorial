"""Tests for sales_data.py, using the real CSV and small made-up tables."""

from pathlib import Path

import pandas as pd
import pytest

import sales_data

DATA_PATH = Path(__file__).parent.parent / "data" / "sales-data.csv"


@pytest.fixture
def sales():
    """The real sales data from data/sales-data.csv."""
    return sales_data.load_sales_data(DATA_PATH)


# --- Loading and validation ---


def test_load_reads_all_rows(sales):
    assert len(sales) == 482


def test_load_parses_dates(sales):
    assert pd.api.types.is_datetime64_any_dtype(sales["date"])


def test_load_has_five_categories_and_four_regions(sales):
    assert sales["category"].nunique() == 5
    assert sales["region"].nunique() == 4


def test_load_raises_when_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        sales_data.load_sales_data(tmp_path / "no-such-file.csv")


def test_load_raises_when_column_missing(tmp_path):
    # A CSV with every required column except "region".
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text(
        "date,order_id,product,category,quantity,unit_price,total_amount\n"
        "2024-01-01,ORD-1,USB-C Cable,Accessories,1,12.99,12.99\n"
    )
    with pytest.raises(ValueError, match="region"):
        sales_data.load_sales_data(bad_csv)
