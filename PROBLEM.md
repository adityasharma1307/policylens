# PROBLEM.md — CivicLens v1

## Dataset
**India Price Monitoring Division (PMD) essential commodity prices** — daily retail and wholesale prices by state and market, published by the Dept. of Consumer Affairs (sourced via AGMARKNET) and republished as clean per-commodity panels by Factly's Dataful platform (`dataful.in`).

- Coverage: 2014–2026, daily. Confirmed via real ingestion: 251,132 rows per commodity, 4,269,244 rows total across all 17.
- Granularity: state × commodity × day, long-format with a `market` column holding `Retail`/`Wholesale` as the price-type category (not a physical market name — resolved during Phase 1 ingestion, see `data/README.md`).
- Commodities in scope for v1 (all 17 confirmed present with both Retail and Wholesale rows): onion, wheat, rice, sugar, milk, moong dal, tur/arhar dal, masoor dal, atta (wheat flour), tea (loose), iodised salt, sunflower/mustard/soya/palm/groundnut oil (packed), vanaspati.
- Access: paid — CSV/XLSX/Parquet per commodity via a Dataful Bronze subscription (student-discounted, ~₹2,950/mo, 15 dataset downloads/30 days) plus 2 individual dataset purchases (~₹500 each) to cover all 17 commodities, since Bronze's limit is 2 short of the full list.
- Provenance chain: AGMARKNET / PMD (Dept. of Consumer Affairs) → Dataful → this project. Full chain documented in `data/README.md`.

## Policy question
Are Indian consumers in some states paying disproportionately high retail markups over wholesale prices for essential commodities — beyond what normal logistics/handling costs would explain — indicating uneven market efficiency or middleman exploitation across states?

## Unit of analysis
Raw data is long-format: one row = **state × commodity × day × price-type** (`price-type` ∈ {Retail, Wholesale}), with a `price` column and a `unit` column that varies by commodity (₹/quintal vs ₹/kg for onion, ₹/100L vs ₹/L for milk, etc. — units must be normalized to a common per-commodity basis in Phase 2 before comparing).

After pivoting price-type to columns, one **analysis observation = state × commodity × day**, with:
- `wholesale_price`, `retail_price` (unit-normalized, ₹ per commodity's base unit)
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
- Granularity is state-level, not sub-state market-level (confirmed during Phase 1 ingestion) — cannot distinguish price variation within a state.
- Real missingness confirmed in the `price` column (e.g. 1,262 missing rows for Onion, 28,093 for Milk out of 251,132) — likely states that don't report retail or wholesale prices consistently. Must be handled explicitly per state/commodity in Phase 2, not silently dropped.
- Underlying data entry is manual (PMD/AGMARKNET), so typo-driven outliers are expected in addition to missingness.
