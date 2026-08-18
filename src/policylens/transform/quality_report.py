import pandas as pd


def build_quality_report(long_df: pd.DataFrame, wide_df: pd.DataFrame) -> dict:
    """Null rates, price ranges, and cardinality -- the Phase 2 data-quality artifact.

    Row-count deltas between raw and wide are expected and explained here rather than
    treated as errors: India's state/UT list changed mid-panel (J&K split into J&K +
    Ladakh in 2019; Dadra & Nagar Haveli merged with Daman & Diu in 2020), so not every
    state has full date coverage, and pivoting drops state/commodity/date combos with
    zero rows (both Retail and Wholesale missing) rather than raw's fixed cartesian grid.
    """
    per_group = (
        long_df.groupby(["commodity", "market"])
        .agg(
            rows=("price", "size"),
            missing=("price_missing", "sum"),
            outliers=("price_outlier", "sum"),
            price_min=("price", "min"),
            price_max=("price", "max"),
            price_mean=("price", "mean"),
        )
        .reset_index()
    )
    per_group["missing_rate"] = per_group["missing"] / per_group["rows"]

    return {
        "long_table": {
            "total_rows": len(long_df),
            "distinct_states": int(long_df["state"].nunique()),
            "distinct_commodities": int(long_df["commodity"].nunique()),
            "distinct_dates": int(long_df["date"].nunique()),
            "date_range": [str(long_df["date"].min().date()), str(long_df["date"].max().date())],
            "total_missing_price": int(long_df["price_missing"].sum()),
            "total_outliers_flagged": int(long_df["price_outlier"].sum()),
        },
        "wide_table": {
            "total_rows": len(wide_df),
            "rows_missing_retail": int(wide_df["retail_price"].isna().sum()),
            "rows_missing_wholesale": int(wide_df["wholesale_price"].isna().sum()),
            "rows_with_both_prices": int(
                (wide_df["retail_price"].notna() & wide_df["wholesale_price"].notna()).sum()
            ),
        },
        "per_commodity_market": per_group.to_dict(orient="records"),
    }
