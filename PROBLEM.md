# PROBLEM.md — CivicLens v1

## Dataset
**India Price Monitoring Division (PMD) essential commodity prices** — daily retail and wholesale prices by state and market, published by the Dept. of Consumer Affairs (sourced via AGMARKNET) and republished as clean per-commodity panels by Factly's Dataful platform (`dataful.in`).

- Coverage: 2014–2026, daily
- Granularity: state × market × commodity × day
- Commodities in scope for v1: onion, wheat, rice, sugar, milk, moong dal, tur/arhar dal, masoor dal, atta (wheat flour), tea (loose), iodised salt, sunflower/mustard/soya/palm/groundnut oil (packed), vanaspati — the commodities with confirmed daily state-wise retail+wholesale coverage.
- Access: free CSV/XLSX/Parquet per commodity, confirmed via direct inspection (`is_premium: false`, `price: 0`) for onion, wheat, rice, sugar, milk; to be re-verified per-commodity during ingestion since some Dataful datasets are paid.
- Provenance chain: AGMARKNET / PMD (Dept. of Consumer Affairs) → Dataful → this project. Full chain documented in `data/README.md`.

## Policy question
Are Indian consumers in some states paying disproportionately high retail markups over wholesale prices for essential commodities — beyond what normal logistics/handling costs would explain — indicating uneven market efficiency or middleman exploitation across states?

## Unit of analysis
One observation = **state × commodity × day**, with:
- `wholesale_price`, `retail_price` (₹ per kg/quintal, as published)
- derived outcome: `margin_pct = (retail_price − wholesale_price) / wholesale_price`

## Primary hypothesis (pre-registered, confirmatory)
- **H0:** Mean `margin_pct` for a given commodity does not differ across states, after accounting for commodity and time (month/year) effects.
- **H1:** Mean `margin_pct` differs significantly across states.
- **Test:** Kruskal–Wallis across states per commodity (margins are expected to be non-normal/skewed — confirmed via assumption checks in Phase 4), effect size via epsilon-squared. Post-hoc pairwise state comparisons with Benjamini–Hochberg correction.
- **Confounder-adjusted model:** OLS regression of `margin_pct` on state (fixed effects), with commodity and year-month fixed effects as controls; report coefficients, 95% CIs, and VIF for multicollinearity.
- **Outcome:** `margin_pct`. **Covariates:** commodity FE, year-month FE, state FE (of interest).

## Secondary hypotheses (exploratory — reported separately, not used to inflate the primary claim)
1. **Cross-state price convergence:** commodity prices converge across states over time (law of one price), except during known supply-shock periods (e.g. onion price spikes), when cross-state dispersion increases. Tested via trend in coefficient-of-variation across states over time, with an event-study window around identified shock periods.
2. **Policy intervention vs. volatility:** commodities subject to active government intervention (export bans/stock limits — e.g. onion) show different price volatility than less-intervened commodities (e.g. tea, salt). Tested via Levene's test comparing variance of price changes between intervened vs. non-intervened commodity groups.

## Limitations (flagged up front)
- Correlational only — no causal claim about *why* margins differ across states without further confounder work (transport cost, perishability, local demand elasticity are not in this dataset and would need to be proxied or acknowledged as omitted).
- Retail price is reported as a state-level average in most Dataful extracts, not always market-level — market-level granularity will be confirmed during ingestion; unit of analysis may need to collapse to state × commodity × day if market-level retail data isn't consistently available.
- Data entry is manual at the market level (AGMARKNET), so missingness/typo-driven outliers are expected and must be handled explicitly (Phase 2), not silently dropped.
