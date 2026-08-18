import numpy as np
import pandas as pd
import pytest

from civiclens.analysis.models import compute_state_vif, fit_confounder_model, state_effects_table


@pytest.fixture
def wide_df():
    rng = np.random.default_rng(0)
    rows = []
    states = {"Delhi": 0.20, "Kerala": 0.05, "Punjab": 0.08}
    commodities = ["Onion", "Rice"]
    for state, shift in states.items():
        for commodity in commodities:
            for month in range(1, 4):
                for day in range(1, 11):
                    rows.append(
                        {
                            "state": state,
                            "commodity": commodity,
                            "date": pd.Timestamp(f"2020-{month:02d}-{day:02d}"),
                            "margin_pct": shift + rng.normal(0, 0.01),
                        }
                    )
    return pd.DataFrame(rows)


def test_fit_confounder_model_recovers_state_ranking(wide_df):
    model = fit_confounder_model(wide_df)
    effects = state_effects_table(model)
    # Delhi (shift=0.20) is alphabetically first, so patsy omits it as the reference.
    # Punjab (0.08) should rank above Kerala (0.05) relative to that reference.
    kerala_coef = effects.loc[effects["state"] == "Kerala", "coef_vs_reference"].iloc[0]
    punjab_coef = effects.loc[effects["state"] == "Punjab", "coef_vs_reference"].iloc[0]
    assert punjab_coef > kerala_coef


def test_state_effects_table_has_ci_columns(wide_df):
    model = fit_confounder_model(wide_df)
    effects = state_effects_table(model)
    assert {"ci_low", "ci_high", "p_value"} <= set(effects.columns)
    assert (effects["ci_low"] <= effects["ci_high"]).all()


def test_state_effects_excludes_reference_state(wide_df):
    model = fit_confounder_model(wide_df)
    effects = state_effects_table(model)
    # Exactly k-1 states appear as coefficients (one state is the omitted reference).
    assert len(effects) == wide_df["state"].nunique() - 1


def test_compute_state_vif_returns_reasonable_values(wide_df):
    vif = compute_state_vif(wide_df, sample_size=len(wide_df))
    assert (vif["vif"] > 0).all()
    assert (vif["vif"] < 20).all()  # no extreme multicollinearity in this balanced fixture
