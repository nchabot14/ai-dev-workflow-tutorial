# ShopSmart Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page Streamlit dashboard showing ShopSmart's 2024 KPIs, monthly sales trend, and sales by category and region from `data/sales-data.csv`.

**Architecture:** `sales_data.py` holds all loading, validation, calculation, and formatting as plain Pandas functions, tested with pytest. `app.py` is the Streamlit page: it calls those functions and draws Plotly charts. No Streamlit or Plotly code goes in `sales_data.py`.

**Tech Stack:** Python 3.14 (any 3.11+ works), Streamlit, Pandas, Plotly Express, pytest. Plain `venv/` with `requirements.txt`.

**Spec:** `docs/superpowers/specs/2026-09-22-sales-dashboard-design.md`

---

## Ground rules

- **Branch:** work directly on `feature/sales-dashboard`. Do **not** create a git worktree or a new branch.
- **Environment:** plain virtual environment in `venv/` (already in `.gitignore`). No uv, no conda.
  Commands below call `venv/bin/python`, `venv/bin/pip`, and `venv/bin/streamlit` directly so they work
  without activating. (A person at the terminal can instead run `source venv/bin/activate` once and drop the `venv/bin/` prefix.)
- **Numbering:** "Plan Task N" is this plan's own numbering. The bracketed label, e.g. **[TASK-3]**,
  is the milestone in `TASKS.md` that the plan task belongs to. The two are unrelated numbers.
- **Commits:** every commit message starts with the milestone ID, e.g. `TASK-3: Add KPI cards`.
- **`TASKS.md` is the user's.** Do not move tasks between sections or fill in `Commit:` lines.
- **Keep it simple and readable.** Short functions, a docstring on each, comments only where they explain *why*.
- **Stop before deployment.** Plan Task 13 is the user's hand-off; the executor stops after Plan Task 12.

## File map

| File | Responsibility | Created in |
|---|---|---|
| `requirements.txt` | Exact versions of streamlit, pandas, plotly, pytest | Plan Task 1 |
| `pytest.ini` | Lets tests `import sales_data` from the project root; points pytest at `tests/` | Plan Task 1 |
| `app.py` | Streamlit page: header, KPI cards, trend chart, bar charts, error message | Plan Task 1, grows in 3, 6, 8, 10 |
| `sales_data.py` | Load + validate CSV, totals, monthly/category/region breakdowns, formatting | Plan Task 2, grows in 4, 5, 7, 9 |
| `tests/test_sales_data.py` | pytest tests for every function in `sales_data.py` | Plan Task 2, grows in 4, 5, 7, 9 |
| `tests/test_app.py` | Smoke test: the page runs with no exceptions and shows the right KPIs | Plan Task 11 |

## Milestone coverage

| Milestone | Plan Tasks |
|---|---|
| TASK-1 Environment setup | 1 |
| TASK-2 Data loading and structure | 2, 3 |
| TASK-3 KPI cards | 4, 5, 6 |
| TASK-4 Sales trend chart | 7, 8 |
| TASK-5 Category and region breakdowns | 9, 10 |
| TASK-6 Testing and refinement | 11, 12 |
| TASK-7 Deployment (**user executes**) | 13 |

---

### Plan Task 1 [TASK-1]: Virtual environment, dependencies, and a minimal app

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `app.py`

- [ ] **Step 1: Create the virtual environment**

Run: `python3 -m venv venv`
Expected: a `venv/` folder appears. `git status` does not list it (it's in `.gitignore`).

- [ ] **Step 2: Install the four packages**

Run: `venv/bin/pip install streamlit pandas plotly pytest`
Expected: ends with `Successfully installed ...` and no errors.

- [ ] **Step 3: Write `requirements.txt` with exact versions**

Run: `venv/bin/pip freeze | grep -iE '^(streamlit|pandas|plotly|pytest)==' > requirements.txt`

Then check it: `cat requirements.txt`
Expected: exactly four lines, one per package, each like `streamlit==1.xx.x` (your version numbers will vary).

- [ ] **Step 4: Create `pytest.ini`**

```ini
[pytest]
# Put the project root on the import path so tests can `import sales_data`.
pythonpath = .
testpaths = tests
```

- [ ] **Step 5: Create a minimal `app.py`**

```python
"""ShopSmart Sales Dashboard: a Streamlit page built from data/sales-data.csv."""

import streamlit as st

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")

st.title("ShopSmart Sales Dashboard")
```

- [ ] **Step 6: Check the app launches**

Run (in the background): `venv/bin/streamlit run app.py --server.headless true`
Then run: `curl -s http://localhost:8501/_stcore/health`
Expected: `ok`. Opening http://localhost:8501 in a browser shows the title "ShopSmart Sales Dashboard".
Stop the Streamlit process afterwards (Ctrl+C, or kill the background process).

- [ ] **Step 7: Commit**

```bash
git add requirements.txt pytest.ini app.py
git commit -m "TASK-1: Set up venv requirements and minimal Streamlit app"
```

---

### Plan Task 2 [TASK-2]: Load and validate the CSV (test-first)

**Files:**
- Create: `tests/test_sales_data.py`
- Create: `sales_data.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_sales_data.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `venv/bin/python -m pytest -v`
Expected: collection error, `ModuleNotFoundError: No module named 'sales_data'`.

- [ ] **Step 3: Write the minimal implementation**

Create `sales_data.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `venv/bin/python -m pytest -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add sales_data.py tests/test_sales_data.py
git commit -m "TASK-2: Add CSV loading with column validation"
```

---

### Plan Task 3 [TASK-2]: Load the data in the app and show a friendly error

**Files:**
- Modify: `app.py` (replace the whole file)

- [ ] **Step 1: Replace `app.py`**

```python
"""ShopSmart Sales Dashboard: a Streamlit page built from data/sales-data.csv."""

from pathlib import Path

import streamlit as st

import sales_data

DATA_PATH = Path(__file__).parent / "data" / "sales-data.csv"

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")


@st.cache_data
def load_data(path):
    """Read the CSV once; Streamlit reuses the result on later reruns."""
    return sales_data.load_sales_data(path)


try:
    df = load_data(DATA_PATH)
except (FileNotFoundError, ValueError) as error:
    st.error(f"Could not load the sales data. {error}")
    st.stop()

# --- Header ---
st.title("ShopSmart Sales Dashboard")
start, end = df["date"].min(), df["date"].max()
st.caption(f"Sales performance, {start:%B %Y} – {end:%B %Y}")
```

- [ ] **Step 2: Check the app**

Run (in the background): `venv/bin/streamlit run app.py --server.headless true`
Open http://localhost:8501.
Expected: the title, then the caption "Sales performance, January 2024 – December 2024". No error box.
Stop the Streamlit process.

- [ ] **Step 3: Run the tests (nothing should have broken)**

Run: `venv/bin/python -m pytest -v`
Expected: 5 passed.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "TASK-2: Load sales data in the app with an error message on failure"
```

---

### Plan Task 4 [TASK-3]: Total sales and total orders (test-first)

**Files:**
- Modify: `tests/test_sales_data.py` (append)
- Modify: `sales_data.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_sales_data.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `venv/bin/python -m pytest -v`
Expected: the 4 new tests FAIL with `AttributeError: module 'sales_data' has no attribute 'total_sales'` (and `'total_orders'`); the 5 earlier tests pass.

- [ ] **Step 3: Write the minimal implementation**

Append to `sales_data.py`:

```python
def total_sales(df):
    """Sum of every transaction's total_amount."""
    return float(df["total_amount"].sum())


def total_orders(df):
    """Number of distinct orders (an order spread over several rows counts once)."""
    return int(df["order_id"].nunique())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `venv/bin/python -m pytest -v`
Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add sales_data.py tests/test_sales_data.py
git commit -m "TASK-3: Add total sales and total orders calculations"
```

---

### Plan Task 5 [TASK-3]: Number formatting for the KPI cards (test-first)

**Files:**
- Modify: `tests/test_sales_data.py` (append)
- Modify: `sales_data.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_sales_data.py`:

```python
# --- Formatting ---


def test_format_currency_whole_dollars_with_commas():
    assert sales_data.format_currency(116500.21) == "$116,500"


def test_format_currency_millions():
    assert sales_data.format_currency(1234567) == "$1,234,567"


def test_format_count_small_number():
    assert sales_data.format_count(482) == "482"


def test_format_count_adds_commas():
    assert sales_data.format_count(1234) == "1,234"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `venv/bin/python -m pytest -v`
Expected: the 4 new tests FAIL with `AttributeError: ... no attribute 'format_currency'` / `'format_count'`; the other 9 pass.

- [ ] **Step 3: Write the minimal implementation**

Append to `sales_data.py`:

```python
def format_currency(value):
    """Whole dollars with thousands separators, e.g. 116500.21 -> "$116,500"."""
    return f"${value:,.0f}"


def format_count(value):
    """Whole number with thousands separators, e.g. 1234 -> "1,234"."""
    return f"{value:,}"
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `venv/bin/python -m pytest -v`
Expected: 13 passed.

- [ ] **Step 5: Commit**

```bash
git add sales_data.py tests/test_sales_data.py
git commit -m "TASK-3: Add currency and count formatting"
```

---

### Plan Task 6 [TASK-3]: KPI cards on the page

**Files:**
- Modify: `app.py` (append at the end)

- [ ] **Step 1: Append the KPI cards to `app.py`**

```python

# --- KPI cards ---
sales_card, orders_card = st.columns(2)
sales_card.metric("Total Sales", sales_data.format_currency(sales_data.total_sales(df)))
orders_card.metric("Total Orders", sales_data.format_count(sales_data.total_orders(df)))
```

- [ ] **Step 2: Check the app**

Run (in the background): `venv/bin/streamlit run app.py --server.headless true`
Open http://localhost:8501.
Expected: two cards side by side under the header: **Total Sales $116,500** and **Total Orders 482**.
Stop the Streamlit process.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-3: Add KPI cards for total sales and total orders"
```

---

### Plan Task 7 [TASK-4]: Sales by month (test-first)

**Files:**
- Modify: `tests/test_sales_data.py` (append)
- Modify: `sales_data.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_sales_data.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `venv/bin/python -m pytest -v`
Expected: the 3 new tests FAIL with `AttributeError: ... no attribute 'sales_by_month'`; the other 13 pass.

- [ ] **Step 3: Write the minimal implementation**

Append to `sales_data.py`:

```python
def sales_by_month(df):
    """Total sales per calendar month, oldest first.

    Returns columns "month" (first day of each month) and "total_amount".
    A month with no sales between the first and last month appears with 0.
    """
    monthly = df.resample("MS", on="date")["total_amount"].sum().reset_index()
    return monthly.rename(columns={"date": "month"})
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `venv/bin/python -m pytest -v`
Expected: 16 passed.

- [ ] **Step 5: Commit**

```bash
git add sales_data.py tests/test_sales_data.py
git commit -m "TASK-4: Add monthly sales calculation"
```

---

### Plan Task 8 [TASK-4]: Monthly sales trend chart

**Files:**
- Modify: `app.py` (add an import; append the chart)

- [ ] **Step 1: Add the Plotly import**

In `app.py`, change the import block from:

```python
from pathlib import Path

import streamlit as st

import sales_data
```

to:

```python
from pathlib import Path

import plotly.express as px
import streamlit as st

import sales_data
```

- [ ] **Step 2: Append the trend chart to `app.py`**

```python

# --- Monthly sales trend ---
trend = px.line(
    sales_data.sales_by_month(df),
    x="month",
    y="total_amount",
    markers=True,
    title="Monthly Sales Trend",
    labels={"month": "Month", "total_amount": "Sales ($)"},
)
trend.update_traces(hovertemplate="%{x|%b %Y}: $%{y:,.2f}<extra></extra>")
trend.update_xaxes(dtick="M1", tickformat="%b %Y")
st.plotly_chart(trend)
```

(`<extra></extra>` hides Plotly's extra grey hover box so the tooltip shows only our text. `dtick="M1"` puts a tick on every month.)

- [ ] **Step 3: Check the app**

Run (in the background): `venv/bin/streamlit run app.py --server.headless true`
Open http://localhost:8501.
Expected: a full-width line chart below the KPI cards titled "Monthly Sales Trend", with 12 dots from Jan 2024 to Dec 2024, a y-axis labeled "Sales ($)", and an x-axis labeled "Month". Hovering over a dot shows e.g. "Mar 2024: $9,812.44" (the exact figure will differ).
Stop the Streamlit process.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "TASK-4: Add monthly sales trend chart"
```

---

### Plan Task 9 [TASK-5]: Sales by category and by region (test-first)

**Files:**
- Modify: `tests/test_sales_data.py` (append)
- Modify: `sales_data.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_sales_data.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `venv/bin/python -m pytest -v`
Expected: the 6 new tests FAIL with `AttributeError: ... no attribute 'sales_by_category'` / `'sales_by_region'`; the other 16 pass.

- [ ] **Step 3: Write the minimal implementation**

Append to `sales_data.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `venv/bin/python -m pytest -v`
Expected: 22 passed.

- [ ] **Step 5: Commit**

```bash
git add sales_data.py tests/test_sales_data.py
git commit -m "TASK-5: Add sales by category and region calculations"
```

---

### Plan Task 10 [TASK-5]: Category and region bar charts

**Files:**
- Modify: `app.py` (add a constant and a helper; append the charts)

- [ ] **Step 1: Add the color palette constant**

In `app.py`, change:

```python
DATA_PATH = Path(__file__).parent / "data" / "sales-data.csv"
```

to:

```python
DATA_PATH = Path(__file__).parent / "data" / "sales-data.csv"

# Plotly's color-blind-safe palette: one color per bar.
BAR_COLORS = px.colors.qualitative.Safe
```

- [ ] **Step 2: Add the bar chart helper**

In `app.py`, directly after the `load_data` function (before the `try:` line), add:

```python
def bar_chart(data, column, title, axis_label):
    """Vertical bar chart of total_amount per `column`, kept in the data's order."""
    fig = px.bar(
        data,
        x=column,
        y="total_amount",
        color=column,
        color_discrete_sequence=BAR_COLORS,
        # Keep the highest-first order from sales_data instead of sorting A-Z.
        category_orders={column: list(data[column])},
        title=title,
        labels={column: axis_label, "total_amount": "Sales ($)"},
    )
    fig.update_traces(hovertemplate="%{x}: $%{y:,.2f}<extra></extra>")
    fig.update_layout(showlegend=False)  # the axis labels already name each bar
    return fig
```

- [ ] **Step 3: Append the two charts to `app.py`**

```python

# --- Category and region breakdowns ---
category_col, region_col = st.columns(2)
category_col.plotly_chart(
    bar_chart(sales_data.sales_by_category(df), "category", "Sales by Category", "Category")
)
region_col.plotly_chart(
    bar_chart(sales_data.sales_by_region(df), "region", "Sales by Region", "Region")
)
```

- [ ] **Step 4: Check the app**

Run (in the background): `venv/bin/streamlit run app.py --server.headless true`
Open http://localhost:8501.
Expected: below the trend chart, two charts side by side.
- Left, "Sales by Category": Electronics, Wearables, Audio, Smart Home, Accessories from left to right, each a different color, no legend.
- Right, "Sales by Region": North, West, East, South, each a different color, no legend.
- Hovering a bar shows e.g. "Electronics: $42,683.67".

Stop the Streamlit process.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "TASK-5: Add sales by category and region bar charts"
```

---

### Plan Task 11 [TASK-6]: Smoke test for the whole page

**Files:**
- Create: `tests/test_app.py`

- [ ] **Step 1: Write the smoke test**

Create `tests/test_app.py`:

```python
"""Smoke test: run app.py headlessly and check it renders without errors."""

from streamlit.testing.v1 import AppTest


def test_app_runs_and_shows_kpis():
    # The path is relative to this test file. Allow extra time for Plotly's first import.
    app = AppTest.from_file("../app.py", default_timeout=30).run()

    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$116,500"
    assert app.metric[1].value == "482"
```

- [ ] **Step 2: Run the smoke test**

Run: `venv/bin/python -m pytest tests/test_app.py -v`
Expected: 1 passed. (The page was already built in earlier tasks, so this test passes straight away. It guards against future breakage.)

- [ ] **Step 3: Run the full suite**

Run: `venv/bin/python -m pytest -v`
Expected: 23 passed, no warnings section in the summary.

- [ ] **Step 4: Commit**

```bash
git add tests/test_app.py
git commit -m "TASK-6: Add smoke test for the dashboard page"
```

---

### Plan Task 12 [TASK-6]: Final check against the PRD and polish

**Files:**
- Modify: `app.py` only if a check below fails

- [ ] **Step 1: Run every test**

Run: `venv/bin/python -m pytest -v`
Expected: 23 passed.

- [ ] **Step 2: Run the app and watch the terminal**

Run (in the background): `venv/bin/streamlit run app.py --server.headless true`
Open http://localhost:8501 and reload the page once.
Expected: the Streamlit terminal output shows no warnings or tracebacks, and the page appears within about 5 seconds (PRD NFR-1).

- [ ] **Step 3: Check the page against the PRD's acceptance criteria**

Tick each one while looking at the page:

- [ ] KPIs visible: Total Sales **$116,500**, Total Orders **482**, side by side
- [ ] Trend chart: 12 monthly points, Jan–Dec 2024, labeled axes, hover shows exact values
- [ ] Category chart: 5 bars, Electronics first, sorted highest to lowest, hover shows exact values
- [ ] Region chart: 4 bars, North first, sorted highest to lowest, hover shows exact values
- [ ] Every chart has a title and labeled axes
- [ ] No error box and no warnings anywhere
- [ ] Looks presentable in both light and dark mode (Streamlit menu ⋮ → Settings → Theme)

- [ ] **Step 4: Fix the category labels only if they overlap**

If the category names under the left bar chart overlap or are cut off at your window width, add
this line in `bar_chart` in `app.py`, directly after `fig.update_layout(showlegend=False)`:

```python
    fig.update_xaxes(tickangle=-30)
```

Reload the page and confirm the labels are readable. If they were already readable, skip this step.

- [ ] **Step 5: Stop the app and re-run the tests**

Stop the Streamlit process.
Run: `venv/bin/python -m pytest -v`
Expected: 23 passed.

- [ ] **Step 6: Commit (only if Step 4 changed `app.py`)**

```bash
git add app.py
git commit -m "TASK-6: Angle category labels so they stay readable"
```

If nothing changed, there is nothing to commit. Run `git status` and confirm "nothing to commit, working tree clean".

**The executor stops here.** Report the results of Steps 1–3 and hand off to the user for Plan Task 13.

---

### Plan Task 13 [TASK-7]: Deploy to Streamlit Community Cloud (USER EXECUTES; not the agent)

> This task is the user's. The implementing agent must **not** run any of these steps. They are listed so the hand-off is complete.

- [ ] **Step 1: Review and merge**

1. Push the branch: `git push -u origin feature/sales-dashboard`
2. Read the diff and run Claude Code's `/code-review` on the branch; decide what to fix.
3. Merge `feature/sales-dashboard` into `main` (through a GitHub pull request or locally) and make sure `main` is pushed to GitHub.

- [ ] **Step 2: Deploy from `main`**

1. Sign in at https://share.streamlit.io with GitHub.
2. Create an app: choose this repository, branch **`main`**, main file path **`app.py`**.
3. Under **Advanced settings**, pick Python **3.14** if it's offered, otherwise the newest version listed.
4. Deploy and wait for the build log to finish installing `requirements.txt`.

- [ ] **Step 3: Confirm and record**

1. Open the public URL and check it shows Total Sales $116,500, Total Orders 482, and all three charts.
2. Record the URL in `TASKS.md` (or `README.md`), then commit with a `TASK-7:` message and push.
3. Move milestones to **Done** in `TASKS.md` and fill in their `Commit:` lines.
