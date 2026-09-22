# ShopSmart Sales Dashboard: Design

**Date:** 2026-09-22
**Source:** `prd/ecommerce-analytics.md` (Phase 1 only)
**Milestones:** `TASKS.md` (TASK-1 to TASK-7)
**Branch:** `feature/sales-dashboard`

## Goal

A single-page Streamlit dashboard that shows ShopSmart's 2024 sales from `data/sales-data.csv`:
two KPI cards, a monthly sales trend, and sales by category and by region. It must run locally
with `streamlit run app.py` and be deployable to Streamlit Community Cloud.

Out of scope (PRD Phase 2): filters, date pickers, exports, authentication, databases, drill-down.

## Decisions

| Topic | Decision |
|---|---|
| Trend granularity | Monthly (12 points) |
| Bar orientation | Vertical columns, sorted highest to lowest, left to right |
| Bar colors | A different color per bar, from Plotly's color-blind-safe `Safe` palette; no legend |
| Bad or missing data | Show a clear `st.error` message and stop; no row cleaning |
| Code structure | Two files: `sales_data.py` (calculations) and `app.py` (display) |
| Environment | Plain `venv/` plus `requirements.txt`; no uv or conda |
| Workspace | Current feature branch; no git worktree |

## Data facts (checked against the CSV)

- 482 rows, 482 unique `order_id` values
- Dates from 2024-01-03 to 2024-12-31
- Total sales: $116,500.21
- `quantity × unit_price == total_amount` in every row
- Categories by sales: Electronics, Wearables, Audio, Smart Home, Accessories
- Regions by sales: North, West, East, South

## Files

```
app.py                    # Streamlit page: layout, KPI cards, Plotly charts
sales_data.py             # Pandas only: load, validate, calculate, format
tests/test_sales_data.py  # pytest tests for sales_data.py
tests/test_app.py         # one smoke test: the page runs without exceptions
requirements.txt          # streamlit, pandas, plotly, pytest (exact versions)
data/sales-data.csv       # existing data file
venv/                     # local virtual environment (already in .gitignore)
```

The module is named `sales_data.py`, not `data.py`, so it isn't confused with the `data/` folder.

## `sales_data.py`

It imports only Pandas: no Streamlit and no Plotly, so every function can be tested with pytest directly.

| Function | Returns | Expected with the real CSV |
|---|---|---|
| `load_sales_data(path)` | DataFrame; `date` parsed as datetime | 482 rows |
| `total_sales(df)` | float: sum of `total_amount` | 116,500.21 |
| `total_orders(df)` | int: count of unique `order_id` | 482 |
| `sales_by_month(df)` | DataFrame with `month` and `total_amount`, in calendar order | 12 rows, Jan to Dec |
| `sales_by_category(df)` | DataFrame with `category` and `total_amount`, highest first | 5 rows, Electronics first |
| `sales_by_region(df)` | DataFrame with `region` and `total_amount`, highest first | 4 rows, North first |
| `format_currency(value)` | text in whole dollars with commas | `"$116,500"` |
| `format_count(value)` | text with commas | `"482"` |

`REQUIRED_COLUMNS` holds the 8 PRD columns: `date`, `order_id`, `product`, `category`, `region`,
`quantity`, `unit_price`, `total_amount`.

**Validation:** `load_sales_data` raises `FileNotFoundError` if the file doesn't exist, and a
`ValueError` naming the missing columns (e.g. `Missing columns: region, quantity`) if any
required column is absent.

**Total Orders** counts unique `order_id` values rather than rows, so the KPI stays correct if an
order ever spans several rows.

## `app.py`

The page, from top to bottom:

1. **Page setup:** `st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")`.
2. **Load data:** a small wrapper around `load_sales_data` decorated with `@st.cache_data`, so the
   CSV is read once. If loading raises `FileNotFoundError` or `ValueError`, show `st.error(...)`
   with the message and call `st.stop()`.
3. **Header:** the title "ShopSmart Sales Dashboard" (the PRD sketch's "SHOPMART" is read as a
   typo) and a subtitle with the date range calculated from the data, e.g. "Sales performance,
   January – December 2024".
4. **KPI cards:** `st.columns(2)` with two `st.metric` cards, "Total Sales" (`format_currency`)
   and "Total Orders" (`format_count`), with no change indicators.
5. **Monthly Sales Trend:** full width. A Plotly line with a marker per month, the y-axis
   labeled "Sales ($)" and the x-axis "Month". Hovering shows the month and the exact dollar amount.
6. **Breakdowns:** `st.columns(2)`, left "Sales by Category", right "Sales by Region". Each is a
   vertical Plotly bar chart in the order returned by `sales_data.py` (not re-sorted
   alphabetically), with one color per bar from `plotly.express.colors.qualitative.Safe`, the
   legend hidden, labeled axes, and hover text showing the exact dollar amount.

Charts use Streamlit's default theme, so they follow the viewer's light or dark mode.

## Testing

Test-first for every function in `sales_data.py`.

- **Real CSV:** row count, date type, total sales ≈ 116,500.21 (`pytest.approx`), 482 orders,
  12 months in order, category and region counts and order, and each breakdown summing to the total.
- **Tiny made-up table (3–4 rows):** grouping and sorting by hand-computed values; a duplicated
  `order_id` is counted once.
- **Errors (`tmp_path`):** a missing file raises `FileNotFoundError`; a CSV without `region`
  raises a `ValueError` whose message contains `region`.
- **Formatting:** `format_currency(116500.21) == "$116,500"`, `format_count(482) == "482"`,
  `format_count(1234) == "1,234"`.
- **Smoke test (`tests/test_app.py`):** `streamlit.testing.v1.AppTest` runs `app.py` and asserts
  there are no exceptions.

Checking how the charts look is manual: run `streamlit run app.py` and look at the page.

## Milestone mapping

| Milestone | Covered by |
|---|---|
| TASK-1 | venv, `requirements.txt`, minimal `app.py` that runs |
| TASK-2 | `load_sales_data` and validation (test-first); error message in `app.py` |
| TASK-3 | totals and formatting functions (test-first); KPI cards |
| TASK-4 | `sales_by_month` (test-first); trend chart |
| TASK-5 | category and region functions (test-first); both bar charts |
| TASK-6 | smoke test, full test run, values checked against the CSV, visual polish |
| TASK-7 | **User-executed.** Deploy from `main` after merge (see hand-off below) |

- Plan steps are numbered separately ("Plan Task 1, 2, …") and each is labeled with its milestone.
- Every commit message starts with the milestone ID, e.g. `TASK-3: Add KPI cards`.
- `TASKS.md` is maintained by the user; the plan does not move tasks or fill in `Commit:` lines.

## Deployment hand-off (TASK-7, done by the user)

The plan ends before deployment. The user will:

1. Merge `feature/sales-dashboard` into `main` and push.
2. On Streamlit Community Cloud, create an app from the repo's `main` branch with `app.py` as the
   main file. In advanced settings, choose Python 3.14 if offered, otherwise the newest available.
3. Open the public URL, confirm the dashboard loads, and record the URL in `TASKS.md` or `README.md`.
