# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A tutorial repo (`README.md`, `pre-work-setup.md`, `workshop-build-deploy.md`) plus the project it builds: the **ShopSmart Sales Dashboard**, a single-page Streamlit app over `data/sales-data.csv`. The app code is just `app.py`, `sales_data.py`, and `tests/`. The other Markdown files at the root are course material, not app docs.

Source of truth for the dashboard, in order: `prd/ecommerce-analytics.md` (requirements) → `docs/superpowers/specs/2026-09-22-sales-dashboard-design.md` (design decisions) → `docs/superpowers/plans/2026-09-22-sales-dashboard.md` (step-by-step plan) → `TASKS.md` (milestone board).

## Commands

Plain `venv/` (no uv or conda). Call the venv binaries directly so nothing needs activating:

```bash
python3 -m venv venv && venv/bin/pip install -r requirements.txt   # setup
venv/bin/streamlit run app.py                                       # run the app (http://localhost:8501)
venv/bin/python -m pytest -v                                        # all tests
venv/bin/python -m pytest tests/test_sales_data.py::test_total_orders_real_data -v   # one test
```

For a headless check, run `venv/bin/streamlit run app.py --server.headless true --server.port 8599` and then `curl http://localhost:8599/_stcore/health` (it returns `ok`). Before trusting the result, see Lessons below.

There is no linter or build step.

## Architecture

- **`sales_data.py`: all logic, Pandas only.** Loading, validation, totals, monthly/category/region breakdowns, and number formatting. It has no Streamlit or Plotly imports, so all of it is unit-testable without starting the app. Keep it that way. New calculations go here, with tests.
- **`app.py`: display only.** It calls `sales_data` functions and draws Plotly Express charts. The layout, top to bottom, is: header and date caption, two KPI `st.metric` cards in `st.columns(2)`, the monthly trend line chart, then category and region bar charts side by side.
- **Error path.** `load_sales_data` raises `FileNotFoundError` or `ValueError` for any bad input: a missing column, an empty file, a blank or unreadable `date`, a blank `category`/`region`, or anything but a finite, non-negative number in `quantity`, `unit_price` or `total_amount`. Every row must be usable by every chart, so the charts always add up to the KPIs. `app.py` catches exactly those two exceptions, shows `st.error`, and calls `st.stop()`. To reject a new kind of bad data, raise `ValueError` in the loader; `app.py` then needs no change. By design the app never cleans or drops rows.
- **Sort order is owned by `sales_data`.** `sales_by_category` and `sales_by_region` return rows highest-first, through the shared `_sales_by` helper. The `bar_chart` helper in `app.py` passes `category_orders` so that Plotly keeps this order instead of sorting A–Z.
- **`sales_by_month`** uses `resample("MS")`, so months are labeled with their first day and a month with no sales appears as 0 rather than being skipped.
- `load_data` in `app.py` is wrapped in `@st.cache_data`, so the CSV is parsed once per server rather than on every rerun.

## Tests

- `tests/test_sales_data.py` uses two fixtures: `sales`, the real CSV, and `tiny`, a 4-row table whose totals can be checked by hand. In `tiny`, order A3 spans two rows to prove that `total_orders` counts distinct `order_id`s.
- `tests/test_app.py` is a headless smoke test using `streamlit.testing.v1.AppTest`. Its path, `"../app.py"`, is relative to the test file.
- `pytest.ini` puts the repo root on `pythonpath`, which is why tests can `import sales_data`.

Expected values from the real CSV, useful when checking changes:
- 482 rows and 482 unique orders, dated 2024-01-03 to 2024-12-31
- Total sales $116,500.21, displayed as `$116,500`
- Categories, highest first: Electronics, Wearables, Audio, Smart Home, Accessories
- Regions, highest first: North, West, East, South

## Workflow conventions

- **Branch:** work on `feature/sales-dashboard`. Don't create git worktrees or extra branches. `main` is updated only by merging a PR.
- **Commits:** every commit message starts with a milestone ID from `TASKS.md`, e.g. `TASK-3: Add KPI cards`. The plan's "Plan Task N" numbers are unrelated to the TASK-N IDs, so map them through the plan's milestone table.
- **`TASKS.md` board:** each milestone moves To Do → In Progress → Done, and board moves are committed separately (e.g. `TASK-3: mark done on the board`).
  - On Done: check off the criteria and put the hash of the milestone's last *code* commit on `Commit:`, not the board commit's hash.
  - Also add a one-line `Notes:` entry recording what Claude got wrong or what the user changed, or `clean` if nothing.
  - Only move tasks or edit the board when asked.
- **Test-first** for anything in `sales_data.py`: add the test, see it fail for the expected reason, implement, then see it pass.
- **Deployment (TASK-7) is the user's.** They merge the PR and deploy `main` / `app.py` on Streamlit Community Cloud. Claude has no browser for this.

## Lessons

These rules come from the `Notes:` lines in `TASKS.md`. Each one records something that needed a human to catch or finish.

- **Work inline and wait for the go-ahead.** Don't dispatch subagents to implement milestones, and don't start or commit a milestone's code before it has been moved to In Progress and the user has said to begin. (TASK-1, TASK-2: a subagent committed work ahead of approval.) If a skill or tool would fork an agent anyway, say so before running it.
- **Make sure a server check is hitting your own server.** If the port is taken, Streamlit logs `Port N is not available` and exits, and a health check or page load then quietly hits whatever older process holds that port. Before reporting a pass, run `lsof -iTCP:<port> -sTCP:LISTEN` to confirm your process is listening, and read the whole log, not a grep for "error" or "warning". (TASK-6: a pass was reported against a stale server.)
- **Visual checks belong to the user unless you can actually see the page.** Claude has no browser here. Checking the figure spec through `AppTest` confirms data, order, labels and hover templates. It does not confirm layout, label overlap, or light/dark appearance. Say which checks are still the user's to do, and don't make layout fixes you haven't seen are needed. (TASK-6.)
