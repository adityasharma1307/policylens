import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests


def check_normality(df: pd.DataFrame, sample_size: int = 5000, seed: int = 42) -> dict:
    """Shapiro-Wilk on a fixed-seed subsample -- Shapiro trivially rejects at n>~5000
    regardless of true shape, so skewness/kurtosis on the full data are the more
    informative diagnostics for whether Kruskal-Wallis (vs. ANOVA) is justified.
    """
    values = df["margin_pct"].dropna().to_numpy()
    rng = np.random.default_rng(seed)
    sample = rng.choice(values, size=min(sample_size, len(values)), replace=False)
    stat, p = stats.shapiro(sample)
    return {
        "shapiro_stat": float(stat),
        "shapiro_p": float(p),
        "shapiro_n": int(len(sample)),
        "skewness": float(stats.skew(values)),
        "kurtosis": float(stats.kurtosis(values)),
        "normal_at_alpha_0.05": bool(p > 0.05),
    }


def check_variance_homogeneity(df: pd.DataFrame, group_col: str = "state") -> dict:
    """Levene's test for equal variances of margin_pct across groups."""
    groups = [g["margin_pct"].dropna().to_numpy() for _, g in df.groupby(group_col)]
    groups = [g for g in groups if len(g) > 0]
    stat, p = stats.levene(*groups)
    return {
        "group_col": group_col,
        "levene_stat": float(stat),
        "levene_p": float(p),
        "equal_variance_at_alpha_0.05": bool(p > 0.05),
    }


def kruskal_wallis_by_commodity(df: pd.DataFrame) -> pd.DataFrame:
    """Primary hypothesis test: per commodity, does margin_pct differ across states?
    Effect size is epsilon-squared, the standard nonparametric analogue of eta-squared:
    (H - k + 1) / (n - k). The 17 resulting p-values are BH-corrected as one family.
    """
    rows = []
    for commodity, group in df.groupby("commodity"):
        state_groups = [g["margin_pct"].dropna().to_numpy() for _, g in group.groupby("state")]
        state_groups = [g for g in state_groups if len(g) > 0]
        n = sum(len(g) for g in state_groups)
        k = len(state_groups)
        stat, p = stats.kruskal(*state_groups)
        epsilon_sq = (stat - k + 1) / (n - k) if n > k else float("nan")
        rows.append(
            {
                "commodity": commodity,
                "H_statistic": stat,
                "p_value": p,
                "n": n,
                "k_states": k,
                "epsilon_squared": epsilon_sq,
            }
        )
    result = pd.DataFrame(rows)
    reject, p_adj, _, _ = multipletests(result["p_value"], method="fdr_bh")
    result["p_value_bh"] = p_adj
    result["significant_bh"] = reject
    return result.sort_values("epsilon_squared", ascending=False).reset_index(drop=True)


def posthoc_pairwise_states(df: pd.DataFrame, commodity: str) -> pd.DataFrame:
    """Pairwise Mann-Whitney U across all state pairs for one commodity, BH-corrected
    within that commodity's own family of comparisons. Only meaningful to run for
    commodities where the omnibus Kruskal-Wallis test above was significant.
    """
    sub = df[df["commodity"] == commodity]
    states = sorted(sub["state"].unique())
    rows = []
    for i, s1 in enumerate(states):
        for s2 in states[i + 1 :]:
            a = sub.loc[sub["state"] == s1, "margin_pct"].dropna()
            b = sub.loc[sub["state"] == s2, "margin_pct"].dropna()
            if len(a) == 0 or len(b) == 0:
                continue
            stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
            rows.append(
                {
                    "state_a": s1,
                    "state_b": s2,
                    "median_diff": a.median() - b.median(),
                    "U_statistic": stat,
                    "p_value": p,
                }
            )
    result = pd.DataFrame(rows)
    if len(result):
        reject, p_adj, _, _ = multipletests(result["p_value"], method="fdr_bh")
        result["p_value_bh"] = p_adj
        result["significant_bh"] = reject
    order = result["median_diff"].abs().sort_values(ascending=False).index
    return result.reindex(order).reset_index(drop=True)


def cross_state_convergence(df: pd.DataFrame, commodity: str) -> pd.DataFrame:
    """Secondary hypothesis 1 (exploratory): coefficient of variation of state-level
    median wholesale price over time, for one commodity. A declining CV indicates
    price convergence across states (law of one price); spikes indicate supply shocks.
    """
    sub = df[df["commodity"] == commodity].dropna(subset=["wholesale_price"]).copy()
    sub["year_month"] = sub["date"].dt.to_period("M").astype(str)
    monthly_state = sub.groupby(["year_month", "state"])["wholesale_price"].median().reset_index()
    cv = monthly_state.groupby("year_month")["wholesale_price"].agg(lambda x: x.std() / x.mean())
    return cv.reset_index(name="cv_across_states").sort_values("year_month").reset_index(drop=True)


def intervention_volatility_test(
    df: pd.DataFrame, intervened: tuple[str, ...] = ("Onion",)
) -> dict:
    """Secondary hypothesis 2 (exploratory): Levene's test comparing the variance of
    day-over-day wholesale price % change between intervened commodities (export
    bans/stock limits, e.g. onion) and all others.
    """
    sub = df.dropna(subset=["wholesale_price"]).sort_values(["state", "commodity", "date"]).copy()
    sub["pct_change"] = sub.groupby(["state", "commodity"])["wholesale_price"].pct_change()
    sub = sub.dropna(subset=["pct_change"])

    intervened_changes = sub.loc[sub["commodity"].isin(intervened), "pct_change"]
    other_changes = sub.loc[~sub["commodity"].isin(intervened), "pct_change"]
    stat, p = stats.levene(intervened_changes, other_changes)
    return {
        "intervened_commodities": list(intervened),
        "intervened_variance": float(intervened_changes.var()),
        "other_variance": float(other_changes.var()),
        "levene_stat": float(stat),
        "levene_p": float(p),
        "significantly_different_variance_at_alpha_0.05": bool(p < 0.05),
    }
