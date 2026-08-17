# Data provenance

## Source chain
- **Original publisher:** Dept. of Consumer Affairs, Ministry of Consumer Affairs, Food & Public Distribution, Government of India — Price Monitoring Division (PMD), sourced from market-level entries in AGMARKNET (`agmarknet.gov.in`).
- **Republisher used for ingestion:** Dataful, by Factly Media & Research (`https://dataful.in/collections/755/`) — republishes the PMD/AGMARKNET data as clean per-commodity CSV/XLSX/Parquet exports.

## Coverage
- **Commodities:** onion, wheat, rice, sugar, milk, moong dal, tur/arhar dal, masoor dal, atta (wheat flour), tea (loose), iodised salt, sunflower/mustard/soya/palm/groundnut oil (packed), vanaspati.
- **Granularity:** state × market × commodity × day, retail and wholesale prices.
- **Time range:** 2014–2026, daily.

## License / access
- Original government data falls under India's open-data policy for data.gov.in-linked publications (National Data Sharing and Accessibility Policy).
- Dataful's republished exports were confirmed free (`is_premium: false`, `price: 0`) for onion, wheat, rice, sugar, and milk as of 2026-08-17. **This must be re-verified per commodity at ingestion time** — some Dataful datasets on the same platform are paid, and this was only spot-checked for five commodities.
- Dataful's own Terms & Conditions govern reuse/redistribution of their processed exports (separate from the underlying government data's license) — review before publishing derived data externally (e.g. the public dashboard).
- **Attribution required in any published output** (dashboard, policy brief): Dept. of Consumer Affairs, Government of India (original data), Dataful / Factly Media & Research (processing/republishing).

## Known caveats (carried into Phase 1/2 validation)
- Retail price granularity (state-level average vs. true market-level) is not yet confirmed per commodity — may force collapsing the unit of analysis to state × commodity × day only. Confirm during ingestion (Phase 1).
- Source entries are manually keyed at the market level (AGMARKNET) — expect missing days, typos, and outliers. Every dropped/corrected row must be attributable to a named rule (Phase 2 DoD), not silently dropped.
