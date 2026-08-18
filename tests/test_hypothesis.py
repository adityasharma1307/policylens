import numpy as np
import pandas as pd
import pytest

from policylens.analysis.hypothesis import (
    check_normality,
    check_variance_homogeneity,
    cross_state_convergence,
    intervention_volatility_test,
    kruskal_wallis_by_commodity,
    posthoc_pairwise_states,
)


@pytest.fixture
def wide_df():
    rng = np.random.default_rng(0)
    rows = []
    for state, shift in [("Delhi", 0.20), ("Kerala", 0.05), ("Punjab", 0.05)]:
        for date_offset in range(200):
            rows.append(
                {
                    "state": state,
                    "commodity": "Onion",
                    "date": pd.Timestamp("2020-01-01") + pd.Timedelta(days=date_offset),
                    "wholesale_price": 20.0 + rng.normal(0, 1),
                    "retail_price": None,
                    "margin_pct": shift + rng.normal(0, 0.01),
                }
            )
    return pd.DataFrame(rows)


def test_kruskal_wallis_detects_group_difference(wide_df):
    result = kruskal_wallis_by_commodity(wide_df)
    row = result.iloc[0]
    assert row["commodity"] == "Onion"
    assert row["p_value"] < 0.001
    assert row["epsilon_squared"] > 0
    assert row["k_states"] == 3


def test_kruskal_wallis_bh_columns_present(wide_df):
    result = kruskal_wallis_by_commodity(wide_df)
    assert "p_value_bh" in result.columns
    assert "significant_bh" in result.columns
    assert bool(result["significant_bh"].iloc[0])


def test_posthoc_pairwise_states_covers_all_pairs(wide_df):
    result = posthoc_pairwise_states(wide_df, "Onion")
    assert len(result) == 3  # C(3, 2)
    assert set(result.columns) >= {"state_a", "state_b", "median_diff", "p_value", "p_value_bh"}


def test_posthoc_sorted_by_absolute_median_diff_descending(wide_df):
    result = posthoc_pairwise_states(wide_df, "Onion")
    diffs = result["median_diff"].abs().to_numpy()
    assert (diffs[:-1] >= diffs[1:]).all()


def test_check_normality_flags_skewed_data():
    skewed = pd.DataFrame({"margin_pct": np.random.default_rng(0).exponential(1, size=6000)})
    result = check_normality(skewed)
    assert result["normal_at_alpha_0.05"] is False
    assert result["skewness"] > 0


def test_check_variance_homogeneity_detects_unequal_variance():
    df = pd.DataFrame(
        {
            "state": ["A"] * 500 + ["B"] * 500,
            "margin_pct": np.concatenate(
                [
                    np.random.default_rng(1).normal(0, 0.01, 500),
                    np.random.default_rng(2).normal(0, 1.0, 500),
                ]
            ),
        }
    )
    result = check_variance_homogeneity(df)
    assert result["equal_variance_at_alpha_0.05"] is False


def test_cross_state_convergence_returns_monthly_cv(wide_df):
    result = cross_state_convergence(wide_df, "Onion")
    assert "cv_across_states" in result.columns
    assert (result["cv_across_states"] >= 0).all()


def test_intervention_volatility_test_structure(wide_df):
    wide_df2 = wide_df.copy()
    wide_df2["commodity"] = ["Onion"] * 200 + ["Rice"] * 400
    result = intervention_volatility_test(wide_df2, intervened=("Onion",))
    assert result["intervened_commodities"] == ["Onion"]
    assert "levene_p" in result
