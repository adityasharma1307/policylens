import numpy as np
import pandas as pd

from civiclens.analysis.robustness import bootstrap_median_margin, rerun_excluding_outliers


def test_bootstrap_median_margin_ci_contains_point_estimate():
    df = pd.DataFrame({"margin_pct": np.random.default_rng(0).normal(0.1, 0.02, size=2000)})
    result = bootstrap_median_margin(df, n_boot=100, seed=1)
    assert result["ci_low"] <= result["point_estimate"] <= result["ci_high"]


def test_bootstrap_median_margin_is_reproducible_with_same_seed():
    df = pd.DataFrame({"margin_pct": np.random.default_rng(0).normal(0.1, 0.02, size=2000)})
    result_a = bootstrap_median_margin(df, n_boot=50, seed=7)
    result_b = bootstrap_median_margin(df, n_boot=50, seed=7)
    assert result_a["ci_low"] == result_b["ci_low"]
    assert result_a["ci_high"] == result_b["ci_high"]


def test_rerun_excluding_outliers_drops_flagged_rows():
    long_df = pd.DataFrame(
        [
            {"state": "Delhi", "commodity": "Onion", "date": pd.Timestamp("2020-01-01"),
             "market": "Retail", "price_normalized": 25.0, "price_outlier": False},
            {"state": "Delhi", "commodity": "Onion", "date": pd.Timestamp("2020-01-01"),
             "market": "Wholesale", "price_normalized": 20.0, "price_outlier": False},
            {"state": "Delhi", "commodity": "Onion", "date": pd.Timestamp("2020-01-02"),
             "market": "Retail", "price_normalized": 9999.0, "price_outlier": True},
            {"state": "Delhi", "commodity": "Onion", "date": pd.Timestamp("2020-01-02"),
             "market": "Wholesale", "price_normalized": 20.0, "price_outlier": False},
        ]
    )
    result = rerun_excluding_outliers(long_df)
    # 2020-01-02's retail was dropped as an outlier, so that row keeps only wholesale.
    jan2 = result[result["date"] == pd.Timestamp("2020-01-02")].iloc[0]
    assert pd.isna(jan2["retail_price"])
    assert jan2["wholesale_price"] == 20.0
