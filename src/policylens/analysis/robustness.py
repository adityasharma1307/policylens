import numpy as np
import pandas as pd

from policylens.transform.normalize import pivot_to_wide


def bootstrap_median_margin(df: pd.DataFrame, n_boot: int = 500, seed: int = 42) -> dict:
    """Percentile bootstrap CI for the headline number: overall median retail-wholesale
    margin. Resamples the margin_pct column directly (not model coefficients) --
    bootstrapping the full confounder-adjusted OLS is computationally prohibitive at
    ~2M rows (~65s per fit), so the headline scalar is bootstrapped instead.
    """
    values = df["margin_pct"].dropna().to_numpy()
    rng = np.random.default_rng(seed)
    boot_medians = np.array(
        [np.median(rng.choice(values, size=len(values), replace=True)) for _ in range(n_boot)]
    )
    lo, hi = np.percentile(boot_medians, [2.5, 97.5])
    return {
        "point_estimate": float(np.median(values)),
        "ci_low": float(lo),
        "ci_high": float(hi),
        "n_boot": n_boot,
        "n": int(len(values)),
    }


def rerun_excluding_outliers(long_df: pd.DataFrame) -> pd.DataFrame:
    """Alternative cleaning choice: drop outlier-flagged rows before pivoting, instead
    of the default (keep and flag). Lets the pipeline check whether the headline
    result is sensitive to this choice, per the Phase 4 robustness requirement.
    """
    filtered = long_df[~long_df["price_outlier"]]
    return pivot_to_wide(filtered)
