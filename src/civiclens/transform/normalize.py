import pandas as pd

WHOLESALE_TO_RETAIL_DIVISOR = 100.0
"""Wholesale is always priced per 100 of Retail's base unit (quintal=100kg,
hundred-litres=100L), confirmed across all 17 commodities during Phase 2 inspection.
"""


def normalize_price_units(df: pd.DataFrame) -> pd.DataFrame:
    """Divide Wholesale prices by 100 so Retail and Wholesale are directly comparable
    in the same base unit (₹/kg or ₹/litre). Original `price`/`unit` are left intact
    for auditability.
    """
    df = df.copy()
    divisor = df["market"].map({"Retail": 1.0, "Wholesale": WHOLESALE_TO_RETAIL_DIVISOR})
    df["price_normalized"] = df["price"] / divisor
    return df


def pivot_to_wide(df: pd.DataFrame) -> pd.DataFrame:
    """One row per state x commodity x date, with retail_price/wholesale_price columns
    and the derived margin_pct outcome. Rows where a state/commodity/date combo is
    missing one or both price types keep NaN rather than being dropped.
    """
    wide = df.pivot_table(
        index=["state", "commodity", "date"],
        columns="market",
        values="price_normalized",
        aggfunc="first",
    ).reset_index()
    wide.columns.name = None
    wide = wide.rename(columns={"Retail": "retail_price", "Wholesale": "wholesale_price"})
    wide["margin_pct"] = (wide["retail_price"] - wide["wholesale_price"]) / wide["wholesale_price"]
    return wide
