import json

import pandas as pd

from civiclens.analysis.eda import run_eda
from civiclens.analysis.hypothesis import (
    check_normality,
    check_variance_homogeneity,
    cross_state_convergence,
    intervention_volatility_test,
    kruskal_wallis_by_commodity,
    posthoc_pairwise_states,
)
from civiclens.analysis.models import compute_state_vif, fit_confounder_model, state_effects_table
from civiclens.analysis.power import achieved_power, minimum_detectable_effect
from civiclens.analysis.robustness import bootstrap_median_margin, rerun_excluding_outliers
from civiclens.config import INTERIM_DIR, PROCESSED_DIR, ROOT_DIR

RESULTS_PATH = ROOT_DIR / "reports" / "results.json"


def main() -> None:
    wide = pd.read_parquet(PROCESSED_DIR / "prices_wide.parquet")
    long = pd.read_parquet(INTERIM_DIR / "clean_prices_long.parquet")

    print("Running EDA...")
    eda_summary = run_eda(wide)

    print("Checking assumptions...")
    normality = check_normality(wide)
    variance_homogeneity = check_variance_homogeneity(wide)

    print("Running primary hypothesis test (Kruskal-Wallis per commodity)...")
    kw_results = kruskal_wallis_by_commodity(wide)
    kw_results["achieved_power"] = kw_results.apply(
        lambda r: achieved_power(int(r["k_states"]), int(r["n"]), r["epsilon_squared"])[
            "achieved_power"
        ],
        axis=1,
    )
    kw_results["mde_eta_squared"] = kw_results.apply(
        lambda r: minimum_detectable_effect(int(r["k_states"]), int(r["n"]))[
            "minimum_detectable_eta_squared"
        ],
        axis=1,
    )

    significant = kw_results[kw_results["significant_bh"]].sort_values(
        "epsilon_squared", ascending=False
    )
    top_commodities = significant["commodity"].head(3).tolist()
    print(f"Running post-hoc pairwise state comparisons for: {top_commodities}")
    posthoc = {c: posthoc_pairwise_states(wide, c) for c in top_commodities}
    for commodity, table in posthoc.items():
        safe_name = commodity.lower().replace(" ", "_").replace("/", "-")
        table.to_csv(ROOT_DIR / "reports" / f"posthoc_{safe_name}.csv", index=False)

    print("Fitting confounder-adjusted OLS model (state + commodity + year-month FE)...")
    model = fit_confounder_model(wide)
    state_effects = state_effects_table(model)
    vif = compute_state_vif(wide)

    print("Running secondary hypotheses (exploratory)...")
    onion_convergence = cross_state_convergence(wide, "Onion")
    intervention_volatility = intervention_volatility_test(wide, intervened=("Onion",))

    print("Running robustness checks (bootstrap + alternative cleaning)...")
    bootstrap = bootstrap_median_margin(wide)
    alt_wide = rerun_excluding_outliers(long)
    alt_median = float(alt_wide["margin_pct"].dropna().median())

    results = {
        "eda": eda_summary,
        "assumption_checks": {
            "normality": normality,
            "variance_homogeneity_by_state": variance_homogeneity,
        },
        "primary_hypothesis": {
            "test": "Kruskal-Wallis per commodity, states as groups",
            "multiple_comparison_correction": "Benjamini-Hochberg (FDR) across the 17 commodities",
            "results": kw_results.to_dict(orient="records"),
            "n_significant_after_bh": int(kw_results["significant_bh"].sum()),
        },
        "posthoc_top_commodities": top_commodities,
        "confounder_model": {
            "formula": "margin_pct ~ C(state) + C(commodity) + C(year_month)",
            "r_squared": float(model.rsquared),
            "n_obs": int(model.nobs),
            "condition_number": float(model.condition_number),
            "state_effects": state_effects.to_dict(orient="records"),
            "state_vif_summary": {
                "min": float(vif["vif"].min()),
                "max": float(vif["vif"].max()),
                "mean": float(vif["vif"].mean()),
            },
        },
        "secondary_hypotheses": {
            "cross_state_convergence_onion": onion_convergence.to_dict(orient="records"),
            "intervention_volatility": intervention_volatility,
        },
        "robustness": {
            "bootstrap_median_margin": bootstrap,
            "alternative_cleaning_exclude_outliers": {
                "median_margin_pct": alt_median,
                "delta_vs_main": alt_median - bootstrap["point_estimate"],
            },
        },
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2, default=str))
    print(f"Results written -> {RESULTS_PATH}")
    print(
        f"Primary: {results['primary_hypothesis']['n_significant_after_bh']}/17 commodities "
        "show a significant state effect (BH-corrected)"
    )
    print(f"Confounder model R^2: {model.rsquared:.3f} on {int(model.nobs)} rows")
    print(
        f"Headline median margin: {bootstrap['point_estimate']:.4f} "
        f"[{bootstrap['ci_low']:.4f}, {bootstrap['ci_high']:.4f}]"
    )


if __name__ == "__main__":
    main()
