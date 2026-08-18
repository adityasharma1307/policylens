import json
from datetime import date

import pandas as pd
import streamlit as st

from civiclens.config import DUCKDB_PATH, ROOT_DIR
from civiclens.warehouse.duck import get_connection

RESULTS_PATH = ROOT_DIR / "reports" / "results.json"


def warehouse_ready() -> bool:
    return DUCKDB_PATH.exists()


def results_ready() -> bool:
    return RESULTS_PATH.exists()


@st.cache_resource
def _connection():
    return get_connection()


@st.cache_data
def load_results() -> dict:
    return json.loads(RESULTS_PATH.read_text())


@st.cache_data
def filter_options() -> dict:
    con = _connection()
    states = con.execute("SELECT state FROM dim_state ORDER BY state").fetchdf()["state"].tolist()
    commodities = (
        con.execute("SELECT commodity FROM dim_commodity ORDER BY commodity")
        .fetchdf()["commodity"]
        .tolist()
    )
    bounds = con.execute("SELECT MIN(date) AS lo, MAX(date) AS hi FROM dim_date").fetchdf()
    return {
        "states": states,
        "commodities": commodities,
        "date_min": bounds["lo"].iloc[0].date(),
        "date_max": bounds["hi"].iloc[0].date(),
    }


@st.cache_data
def query_fact(
    states: tuple[str, ...],
    commodities: tuple[str, ...],
    date_start: date,
    date_end: date,
) -> pd.DataFrame:
    con = _connection()
    sql = """
        SELECT date, state, commodity, retail_price, wholesale_price, margin_pct
        FROM fact_price_view
        WHERE state IN ?
          AND commodity IN ?
          AND date BETWEEN ? AND ?
    """
    return con.execute(sql, [list(states), list(commodities), date_start, date_end]).fetchdf()


@st.cache_data
def state_commodity_medians() -> pd.DataFrame:
    con = _connection()
    return con.execute(
        """
        SELECT state, commodity, MEDIAN(margin_pct) AS median_margin, COUNT(*) AS n
        FROM fact_price_view
        WHERE margin_pct IS NOT NULL
        GROUP BY state, commodity
        """
    ).fetchdf()
