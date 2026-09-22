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
