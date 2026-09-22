# Tasks

This file tracks all work for the ShopSmart Sales Dashboard (see `prd/ecommerce-analytics.md`).

## Definition of Done

A milestone moves to **Done** only when:

- All of its acceptance criteria are met
- The app runs locally with `streamlit run app.py`
- Changes are committed with the milestone ID in the message (e.g., `TASK-3: Add KPI cards`)

## To Do

### TASK-7: Deploy to Streamlit Community Cloud
Publish the dashboard at a public, shareable URL (NFR-5).
- [ ] App is deployed to Streamlit Community Cloud from the GitHub repo
- [ ] Public URL loads the dashboard and is recorded in this file or the README

Commit:

## In Progress

## Done

### TASK-1: Environment setup and project initialization
Set up the Python environment, dependencies, and a minimal Streamlit app skeleton.
- [x] `requirements.txt` lists Streamlit, Pandas, and Plotly (Python 3.11+)
- [x] `app.py` exists and shows a "ShopSmart Sales Dashboard" title
- [x] `streamlit run app.py` launches without errors

Commit: f2df397
Notes: Claude's subagent finished and committed this task before the switch to inline execution, so it ran without the requested go-ahead; kept after an inline review. Code unchanged.

### TASK-2: Data loading and basic structure
Load `data/sales-data.csv` with Pandas and organize the app into modular functions.
- [x] CSV loads with `date` parsed as a date and numeric columns as numbers
- [x] Loaded data has 482 rows, 5 categories, and 4 regions
- [x] Data loading is in its own function with basic structure validation

Commit: 1f4c74c
Notes: Plan Task 2 (CSV loader + tests, 33e1a53) was committed by Claude's subagent before the switch to inline execution, before TASK-2 was moved to In Progress; kept after re-running its tests. Plan Task 3 done inline with no changes from me.

### TASK-3: KPI cards
Display Total Sales and Total Orders prominently at the top of the dashboard (FR-1).
- [x] Total Sales shows ~$116,500, formatted as currency (`$X,XXX,XXX`)
- [x] Total Orders shows 482 with thousands separators
- [x] KPIs are side by side and clearly labeled

Commit: d335af8
Notes: clean

### TASK-4: Sales trend chart
Add a Plotly line chart of sales over time (FR-2).
- [x] Line chart shows sales aggregated by month (or day) across the full 12 months
- [x] Axes are labeled and hovering shows exact values

Commit: f3cdf1b
Notes: clean

### TASK-5: Category and region breakdowns
Add side-by-side bar charts for sales by category and by region (FR-3, FR-4).
- [x] Category chart shows all 5 categories, sorted highest to lowest, with Electronics on top
- [x] Region chart shows all 4 regions, sorted highest to lowest
- [x] Both charts have clear labels and interactive tooltips

Commit: f51fd79
Notes: clean

### TASK-6: Testing and refinement
Verify values against the CSV and polish the dashboard for executive presentation.
- [x] All displayed values match calculations from the CSV
- [x] Dashboard runs with no errors or warnings and loads within 5 seconds
- [x] Layout matches the PRD's dashboard layout and looks professional

Commit: ec8b084
Notes: Claude first reported the Plan Task 12 server check as passing, but its server never started (port 8501 was held by an older Streamlit, PID 1416) and the check hit that process; caught and redone on port 8599. Claude had no browser, so the visual checks (layout, label overlap, light/dark mode) were left to me; no Step 4 label fix was applied.
