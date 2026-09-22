"""ShopSmart Sales Dashboard: a Streamlit page built from data/sales-data.csv."""

from pathlib import Path

import plotly.express as px
import streamlit as st

import sales_data

DATA_PATH = Path(__file__).parent / "data" / "sales-data.csv"

# Plotly's color-blind-safe palette: one color per bar.
BAR_COLORS = px.colors.qualitative.Safe

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")


@st.cache_data
def load_data(path):
    """Read the CSV once; Streamlit reuses the result on later reruns."""
    return sales_data.load_sales_data(path)


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


try:
    df = load_data(DATA_PATH)
except (FileNotFoundError, ValueError) as error:
    st.error(f"Could not load the sales data. {error}")
    st.stop()

# --- Header ---
st.title("ShopSmart Sales Dashboard")
start, end = df["date"].min(), df["date"].max()
st.caption(f"Sales performance, {start:%B %Y} – {end:%B %Y}")

# --- KPI cards ---
sales_card, orders_card = st.columns(2)
sales_card.metric("Total Sales", sales_data.format_currency(sales_data.total_sales(df)))
orders_card.metric("Total Orders", sales_data.format_count(sales_data.total_orders(df)))

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

# --- Category and region breakdowns ---
category_col, region_col = st.columns(2)
category_col.plotly_chart(
    bar_chart(sales_data.sales_by_category(df), "category", "Sales by Category", "Category")
)
region_col.plotly_chart(
    bar_chart(sales_data.sales_by_region(df), "region", "Sales by Region", "Region")
)
