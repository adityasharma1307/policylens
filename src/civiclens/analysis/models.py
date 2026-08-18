import pandas as pd
import statsmodels.formula.api as smf
from patsy import dmatrix
from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.stats.outliers_influence import variance_inflation_factor


def _with_year_month(df: pd.DataFrame) -> pd.DataFrame:
    data = df.dropna(subset=["margin_pct"]).copy()
    data["year_month"] = data["date"].dt.to_period("M").astype(str)
    return data


def fit_confounder_model(df: pd.DataFrame) -> RegressionResultsWrapper:
    """OLS: margin_pct ~ state FE + commodity FE + year-month FE.

    State is the fixed effect of interest; commodity and year-month are controls,
    matching the confounder-adjusted model pre-registered in PROBLEM.md.
    """
    data = _with_year_month(df)
    return smf.ols("margin_pct ~ C(state) + C(commodity) + C(year_month)", data=data).fit()


def state_effects_table(model: RegressionResultsWrapper) -> pd.DataFrame:
    """Extract state coefficients (vs. the omitted reference state) with 95% CIs."""
    conf = model.conf_int()
    rows = []
    for name in model.params.index:
        if not name.startswith("C(state)["):
            continue
        state = name.split("T.")[-1].rstrip("]")
        rows.append(
            {
                "state": state,
                "coef_vs_reference": model.params[name],
                "ci_low": conf.loc[name, 0],
                "ci_high": conf.loc[name, 1],
                "p_value": model.pvalues[name],
            }
        )
    table = pd.DataFrame(rows).sort_values("coef_vs_reference", ascending=False)
    return table.reset_index(drop=True)


def compute_state_vif(df: pd.DataFrame, sample_size: int = 50000, seed: int = 42) -> pd.DataFrame:
    """VIF for the state dummies only. Computing VIF for all ~200 dummy columns in this
    saturated FE design is slow and largely uninformative (within-category dummies are
    collinear by construction); state is the term we actually interpret.
    """
    data = _with_year_month(df)
    sample = data.sample(n=min(sample_size, len(data)), random_state=seed)
    design = dmatrix(
        "C(state) + C(commodity) + C(year_month)", data=sample, return_type="dataframe"
    )
    state_cols = [c for c in design.columns if c.startswith("C(state)")]
    rows = [
        {"term": col, "vif": variance_inflation_factor(design.values, design.columns.get_loc(col))}
        for col in state_cols
    ]
    return pd.DataFrame(rows)
