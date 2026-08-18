import pandas as pd
import streamlit as st

from civiclens.dashboard import charts
from civiclens.dashboard.data import (
    filter_options,
    load_results,
    query_fact,
    results_ready,
    state_commodity_medians,
    warehouse_ready,
)


def render() -> None:
    st.set_page_config(
        page_title="CivicLens — Essential Commodity Price Margins",
        page_icon="📊",
        layout="wide",
    )

    # -----------------------------------------------------------------------
    # Empty state: pipeline hasn't been run yet.
    # -----------------------------------------------------------------------
    if not warehouse_ready() or not results_ready():
        st.title("CivicLens")
        st.warning("No analysis output found yet. Run the pipeline first, then reload this page:")
        st.code("make ingest && make clean && make warehouse && make analysis", language="bash")
        st.stop()

    results = load_results()
    options = filter_options()

    # -----------------------------------------------------------------------
    # Header
    # -----------------------------------------------------------------------
    st.title("Essential Commodity Price Margins")
    st.caption(
        f"India, {options['date_min']:%b %Y} – {options['date_max']:%b %Y} · "
        f"{len(options['states'])} states/UTs · {len(options['commodities'])} commodities · "
        "Source: Dept. of Consumer Affairs, Govt. of India (via Dataful)"
    )

    primary = results["primary_hypothesis"]
    model = results["confounder_model"]
    bootstrap = results["robustness"]["bootstrap_median_margin"]

    st.markdown(
        f"**Consumers pay a median retail markup of {bootstrap['point_estimate']:.1%} over "
        f"wholesale price** (95% CI: {bootstrap['ci_low']:.1%}–{bootstrap['ci_high']:.1%}), and "
        f"this markup differs significantly by state in "
        f"**{primary['n_significant_after_bh']} of 17 commodities** even after accounting "
        "for commodity and month effects."
    )

    # -----------------------------------------------------------------------
    # KPI row
    # -----------------------------------------------------------------------
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1, st.container(border=True):
        st.metric("Median retail-wholesale margin", f"{bootstrap['point_estimate']:.1%}")
        st.caption(
            f"95% CI {bootstrap['ci_low']:.1%} – {bootstrap['ci_high']:.1%} "
            f"(bootstrap, n={bootstrap['n']:,})"
        )
    with k2, st.container(border=True):
        st.metric(
            "Commodities with a significant state effect",
            f"{primary['n_significant_after_bh']} / 17",
        )
        st.caption("Kruskal-Wallis per commodity, Benjamini-Hochberg corrected")
    with k3, st.container(border=True):
        st.metric("Variance explained by model", f"{model['r_squared']:.1%}")
        st.caption(f"State + commodity + month FE, n={model['n_obs']:,}")
    with k4, st.container(border=True):
        st.metric("Data points analyzed", f"{bootstrap['n']:,}")
        st.caption("State × commodity × day observations with a valid margin")

    st.divider()

    # -----------------------------------------------------------------------
    # Primary visual: state x commodity heatmap
    # -----------------------------------------------------------------------
    st.subheader("Where the margin is highest")
    medians = state_commodity_medians()
    pivot = medians.pivot(index="state", columns="commodity", values="median_margin")
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]
    st.plotly_chart(charts.state_commodity_heatmap(pivot), use_container_width=True)
    st.caption(
        "Color scale capped at the 95th percentile so a few extreme cells (e.g. Delhi × "
        "Onion, ~130%) don't wash out contrast for the rest -- hover any cell for its exact value."
    )

    weighted = medians.assign(weighted=medians["median_margin"] * medians["n"])
    state_summary = weighted.groupby("state").agg(weighted=("weighted", "sum"), n=("n", "sum"))
    state_summary["median_margin"] = state_summary["weighted"] / state_summary["n"]
    state_summary = state_summary.reset_index()[["state", "median_margin", "n"]]
    st.plotly_chart(charts.state_ranking_bar(state_summary), use_container_width=True)

    st.divider()

    # -----------------------------------------------------------------------
    # Model evidence (progressive disclosure)
    # -----------------------------------------------------------------------
    with st.expander("Statistical evidence: confounder-adjusted model", expanded=False):
        st.markdown(
            "OLS regression: `margin_pct ~ state + commodity + year-month`, with state as "
            "the fixed effect of interest and commodity/month as controls. Coefficients are "
            "vs. an omitted reference state; error bars are 95% confidence intervals."
        )
        effects = pd.DataFrame(model["state_effects"])
        st.plotly_chart(charts.state_effects_diverging_bar(effects), use_container_width=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("R²", f"{model['r_squared']:.3f}")
        c2.metric("Condition number", f"{model['condition_number']:.0f}")
        c3.metric("Mean state VIF", f"{model['state_vif_summary']['mean']:.2f}")
        st.caption(
            "Condition number and VIF both indicate no concerning multicollinearity "
            "(VIF well below the common threshold of 5)."
        )
        st.dataframe(
            effects.sort_values("coef_vs_reference", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # -----------------------------------------------------------------------
    # Filters -- scope everything below.
    # -----------------------------------------------------------------------
    st.subheader("Explore the data")
    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        sel_commodities = st.multiselect(
            "Commodities",
            options["commodities"],
            default=options["commodities"],
            key="sel_commodities",
        )
    with f2:
        sel_states = st.multiselect(
            "States", options["states"], default=options["states"], key="sel_states"
        )
    with f3:
        sel_range = st.slider(
            "Date range",
            min_value=options["date_min"],
            max_value=options["date_max"],
            value=(options["date_min"], options["date_max"]),
            key="sel_range",
        )

    if not sel_commodities or not sel_states:
        st.info("Select at least one commodity and one state to see the filtered view.")
        st.stop()

    filtered = query_fact(tuple(sel_states), tuple(sel_commodities), sel_range[0], sel_range[1])

    if filtered.empty:
        st.info("No data for this selection.")
        st.stop()

    e1, e2 = st.columns(2)
    with e1:
        st.plotly_chart(
            charts.margin_histogram(filtered["margin_pct"].dropna()), use_container_width=True
        )
    with e2:
        st.plotly_chart(charts.retail_vs_wholesale_scatter(filtered), use_container_width=True)

    st.download_button(
        "Download filtered data (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="civiclens_filtered_prices.csv",
        mime="text/csv",
    )

    with st.expander(f"Filtered data table ({len(filtered):,} rows)"):
        st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.divider()

    # -----------------------------------------------------------------------
    # Secondary hypotheses (exploratory, clearly labeled)
    # -----------------------------------------------------------------------
    st.subheader("Exploratory findings")
    st.caption(
        "The two analyses below are secondary/exploratory, pre-registered as such in "
        "PROBLEM.md -- not held to the same confirmatory standard as the primary result above."
    )
    sec = results["secondary_hypotheses"]
    iv = sec["intervention_volatility"]

    s1, s2 = st.columns(2)
    with s1:
        st.markdown("**Onion price volatility vs. other commodities**")
        ratio = iv["intervened_variance"] / iv["other_variance"]
        st.metric("Variance ratio (onion : others)", f"{ratio:.1f}×")
        p_text = "<0.001" if iv["levene_p"] < 0.001 else f"={iv['levene_p']:.3f}"
        st.caption(
            f"Levene's test p{p_text} -- onion's day-over-day wholesale price swings "
            "are significantly more volatile."
        )
    with s2:
        st.markdown("**Cross-state price convergence (onion)**")
        convergence = pd.DataFrame(sec["cross_state_convergence_onion"])
        st.plotly_chart(charts.convergence_line(convergence), use_container_width=True)

    st.divider()
    st.caption(
        "Data: Dept. of Consumer Affairs, Ministry of Consumer Affairs Food and Public "
        "Distribution, Government of India, via Dataful (Factly Media & Research). "
        "See PROBLEM.md and data/README.md for methodology, provenance, and limitations."
    )
