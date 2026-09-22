# Tasks

This file tracks all work for the ShopSmart Sales Dashboard (see `prd/ecommerce-analytics.md`).

## Definition of Done

A milestone moves to **Done** only when:

- All of its acceptance criteria are met
- The app runs locally with `streamlit run app.py`
- Changes are committed with the milestone ID in the message (e.g., `TASK-3: Add KPI cards`)

## To Do

### TASK-1: Environment setup and project initialization
Set up the Python environment, dependencies, and a minimal Streamlit app skeleton.
- [ ] `requirements.txt` lists Streamlit, Pandas, and Plotly (Python 3.11+)
- [ ] `app.py` exists and shows a "ShopSmart Sales Dashboard" title
- [ ] `streamlit run app.py` launches without errors

Commit:

### TASK-2: Data loading and basic structure
Load `data/sales-data.csv` with Pandas and organize the app into modular functions.
- [ ] CSV loads with `date` parsed as a date and numeric columns as numbers
- [ ] Loaded data has 482 rows, 5 categories, and 4 regions
- [ ] Data loading is in its own function with basic structure validation

Commit:

### TASK-3: KPI cards
Display Total Sales and Total Orders prominently at the top of the dashboard (FR-1).
- [ ] Total Sales shows ~$116,500, formatted as currency (`$X,XXX,XXX`)
- [ ] Total Orders shows 482 with thousands separators
- [ ] KPIs are side by side and clearly labeled

Commit:

### TASK-4: Sales trend chart
Add a Plotly line chart of sales over time (FR-2).
- [ ] Line chart shows sales aggregated by month (or day) across the full 12 months
- [ ] Axes are labeled and hovering shows exact values

Commit:

### TASK-5: Category and region breakdowns
Add side-by-side bar charts for sales by category and by region (FR-3, FR-4).
- [ ] Category chart shows all 5 categories, sorted highest to lowest, with Electronics on top
- [ ] Region chart shows all 4 regions, sorted highest to lowest
- [ ] Both charts have clear labels and interactive tooltips

Commit:

### TASK-6: Testing and refinement
Verify values against the CSV and polish the dashboard for executive presentation.
- [ ] All displayed values match calculations from the CSV
- [ ] Dashboard runs with no errors or warnings and loads within 5 seconds
- [ ] Layout matches the PRD's dashboard layout and looks professional

Commit:

### TASK-7: Deploy to Streamlit Community Cloud
Publish the dashboard at a public, shareable URL (NFR-5).
- [ ] App is deployed to Streamlit Community Cloud from the GitHub repo
- [ ] Public URL loads the dashboard and is recorded in this file or the README

Commit:

## In Progress

## Done
