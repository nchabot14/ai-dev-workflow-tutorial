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


# --- A tiny made-up table with totals you can check by hand ---
#
#   date        order_id  category   region  total_amount
#   2024-01-05  A1        Audio      North   10.00
#   2024-01-20  A2        Wearables  South   50.00
#   2024-02-10  A3        Audio      South   30.00
#   2024-02-11  A3        Audio      South    5.00   <- same order as above
#
# Total sales 95.00; 3 unique orders; Audio 45 vs Wearables 50;
# North 10 vs South 85; January 60 vs February 35.


@pytest.fixture
def tiny():
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-05", "2024-01-20", "2024-02-10", "2024-02-11"]
            ),
            "order_id": ["A1", "A2", "A3", "A3"],
            "category": ["Audio", "Wearables", "Audio", "Audio"],
            "region": ["North", "South", "South", "South"],
            "total_amount": [10.0, 50.0, 30.0, 5.0],
        }
    )


# --- Totals ---


def test_total_sales_real_data(sales):
    assert sales_data.total_sales(sales) == pytest.approx(116500.21)


def test_total_sales_tiny(tiny):
    assert sales_data.total_sales(tiny) == pytest.approx(95.0)


def test_total_orders_real_data(sales):
    assert sales_data.total_orders(sales) == 482


def test_total_orders_counts_each_order_once(tiny):
    # A3 appears on two rows but is one order.
    assert sales_data.total_orders(tiny) == 3


# --- Formatting ---


def test_format_currency_whole_dollars_with_commas():
    assert sales_data.format_currency(116500.21) == "$116,500"


def test_format_currency_millions():
    assert sales_data.format_currency(1234567) == "$1,234,567"


def test_format_count_small_number():
    assert sales_data.format_count(482) == "482"


def test_format_count_adds_commas():
    assert sales_data.format_count(1234) == "1,234"


# --- Monthly trend ---


def test_sales_by_month_has_twelve_months_in_order(sales):
    monthly = sales_data.sales_by_month(sales)
    assert list(monthly.columns) == ["month", "total_amount"]
    assert list(monthly["month"].dt.month) == list(range(1, 13))


def test_sales_by_month_adds_up_to_total(sales):
    monthly = sales_data.sales_by_month(sales)
    assert monthly["total_amount"].sum() == pytest.approx(116500.21)


def test_sales_by_month_tiny(tiny):
    monthly = sales_data.sales_by_month(tiny)
    assert list(monthly["month"].dt.month) == [1, 2]
    assert list(monthly["total_amount"]) == pytest.approx([60.0, 35.0])


# --- Category and region breakdowns ---


def test_sales_by_category_sorted_highest_first(sales):
    by_category = sales_data.sales_by_category(sales)
    assert list(by_category.columns) == ["category", "total_amount"]
    assert list(by_category["category"]) == [
        "Electronics",
        "Wearables",
        "Audio",
        "Smart Home",
        "Accessories",
    ]


def test_sales_by_category_adds_up_to_total(sales):
    by_category = sales_data.sales_by_category(sales)
    assert by_category["total_amount"].sum() == pytest.approx(116500.21)


def test_sales_by_category_tiny(tiny):
    by_category = sales_data.sales_by_category(tiny)
    assert list(by_category["category"]) == ["Wearables", "Audio"]
    assert list(by_category["total_amount"]) == pytest.approx([50.0, 45.0])


def test_sales_by_region_sorted_highest_first(sales):
    by_region = sales_data.sales_by_region(sales)
    assert list(by_region.columns) == ["region", "total_amount"]
    assert list(by_region["region"]) == ["North", "West", "East", "South"]


def test_sales_by_region_adds_up_to_total(sales):
    by_region = sales_data.sales_by_region(sales)
    assert by_region["total_amount"].sum() == pytest.approx(116500.21)


def test_sales_by_region_tiny(tiny):
    by_region = sales_data.sales_by_region(tiny)
    assert list(by_region["region"]) == ["South", "North"]
    assert list(by_region["total_amount"]) == pytest.approx([85.0, 10.0])
