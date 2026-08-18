# Results

Headline numbers from `reports/results.json`, produced by `make analysis` against
the full pipeline. Full narrative writeup: `brief/policy_brief.pdf`. Full
methodology and pre-registration: `PROBLEM.md`.

## Headline

| Metric | Value |
|---|---|
| Median retail-wholesale margin | **9.30%** (95% bootstrap CI: 9.29%–9.31%, n=1,966,287) |
| Commodities with a significant state effect (BH-corrected) | **17 / 17** |
| Confounder-adjusted model R² | 0.359 (n=1,966,287) |
| Highest-markup state (adjusted) | Delhi (+13.0pp vs. reference) |
| Lowest-markup state (adjusted) | Ladakh (−5.8pp vs. reference) |
| Delhi vs. Ladakh gap | ~18.8 percentage points |

## Primary hypothesis: Kruskal-Wallis per commodity (states as groups)

Reference state: Andaman and Nicobar Islands (alphabetically first, omitted by
patsy's default treatment coding). Multiple-comparison correction:
Benjamini-Hochberg (FDR) across all 17 tests.

| Commodity | Epsilon² | p-value (BH) | Significant |
|---|---|---|---|
| Salt Pack Iodised | 0.511 | <0.001 | Yes |
| Moong Dal | 0.409 | <0.001 | Yes |
| Milk | 0.362 | <0.001 | Yes |
| Masoor Dal | 0.354 | <0.001 | Yes |
| Sugar | 0.354 | <0.001 | Yes |
| Vanaspati Packed | 0.352 | <0.001 | Yes |
| Groundnut Oil Packed | 0.347 | <0.001 | Yes |
| Onion | 0.343 | <0.001 | Yes |
| Sunflower Oil Packed | 0.341 | <0.001 | Yes |
| Tur Arhar Dal | 0.336 | <0.001 | Yes |
| Mustard Oil Packed | 0.325 | <0.001 | Yes |
| Rice | 0.313 | <0.001 | Yes |
| Tea Loose | 0.282 | <0.001 | Yes |
| Palm Oil Packed | 0.280 | <0.001 | Yes |
| Atta Wheat | 0.247 | <0.001 | Yes |
| Soya Oil Packed | 0.210 | <0.001 | Yes |
| Wheat | 0.190 | <0.001 | Yes |

## Confounder-adjusted model

`margin_pct ~ C(state) + C(commodity) + C(year_month)`, OLS.

| Diagnostic | Value |
|---|---|
| R² | 0.359 |
| N observations | 1,966,287 |
| Condition number | 207 |
| Mean state VIF | 2.33 (max 2.77 — no concerning multicollinearity) |

Full per-state coefficients + 95% CIs: `reports/results.json` →
`confounder_model.state_effects`, or the dashboard's "Statistical evidence"
panel.

## Secondary hypotheses (exploratory, not confirmatory)

| Hypothesis | Result |
|---|---|
| Cross-state price convergence (onion, wholesale CV over time) | Dispersion spikes visible around known supply-shock periods; see `reports/results.json` → `secondary_hypotheses.cross_state_convergence_onion` |
| Intervention-volatility (onion vs. other commodities) | Onion's day-over-day wholesale price variance is **4.5×** other commodities' (Levene's test, p<0.001) |

## Robustness

| Check | Result |
|---|---|
| Bootstrap CI on headline median margin (n_boot=500) | 9.30% [9.29%, 9.31%] |
| Re-run excluding outlier-flagged rows | Median margin shifts by ~0.00007 percentage points — not outlier-driven |

## Assumption checks

| Check | Result | Implication |
|---|---|---|
| Shapiro-Wilk normality (5,000-row subsample) | p≈0, skewness 5.75, kurtosis 62.1 | Confirms non-normality — justifies Kruskal-Wallis over ANOVA, as pre-registered |
| Levene's test, variance homogeneity across states | p≈0 | Confirms heteroscedasticity — another point favoring the nonparametric test |

## Reproducing these numbers

```bash
make ingest      # requires data/raw/ populated (see data/README.md — paid data, manual download)
make clean
make warehouse
make analysis    # writes reports/results.json
make brief       # renders brief/policy_brief.pdf
```

Or, with DVC: `dvc repro` (verified to reproduce identical results and correctly
skip unchanged stages on repeat runs). CI (`.github/workflows/ci.yml`) exercises
the same pipeline mechanics against synthetic sample data
(`scripts/generate_sample_data.py`), since the real data is paid and can't be
redistributed.
