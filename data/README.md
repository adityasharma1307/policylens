# Data provenance

## Source chain
- **Original publisher:** Dept. of Consumer Affairs, Ministry of Consumer Affairs, Food & Public Distribution, Government of India — Price Monitoring Division (PMD), sourced from market-level entries in AGMARKNET (`agmarknet.gov.in`).
- **Republisher used for ingestion:** Dataful, by Factly Media & Research (`https://dataful.in/collections/755/`) — republishes the PMD/AGMARKNET data as clean per-commodity CSV/XLSX/Parquet exports.

## Coverage
- **Commodities (17, all confirmed ingested):** onion, wheat, rice, sugar, milk, moong dal, tur/arhar dal, masoor dal, atta (wheat flour), tea (loose), iodised salt, sunflower/mustard/soya/palm/groundnut oil (packed), vanaspati.
- **Schema (confirmed from real files):** `date, state, market, commodity, price, unit, note` — long-format, one row per state × commodity × day × price-type. `market` holds `Retail`/`Wholesale` as a category, not a physical market name — granularity is **state-level**, not sub-state. `unit` varies by commodity (e.g. ₹/quintal for onion wholesale vs ₹/kg retail, ₹/100L vs ₹/L for milk) — requires normalization in Phase 2.
- **Time range:** 2014–2026, daily. 251,132 rows per commodity, 4,269,244 rows total across all 17 (verified via `make ingest`).
- **Citation format** (from each dataset's bundled `metadata.csv`): "Ministry of Consumer Affairs Food and Public Distribution. Essential Commodity: State-wise Daily Wholesale and Retail Price of [Commodity] [Data set]. Dataful. https://dataful.in/datasets/[id]"

## License / access
- Original government data falls under India's open-data policy for data.gov.in-linked publications (National Data Sharing and Accessibility Policy).
- Dataful's per-dataset `is_premium`/`price` metadata is unreliable — several commodities showed `is_premium: false, price: 0` in page metadata but still triggered a payment gate on actual download. **Confirmed paid**: accessed via a Dataful Bronze subscription (student-discounted, ~₹2,950/mo, 15 dataset downloads/30 days) plus 2 individual dataset purchases (~₹500 each) to cover all 17 commodities.
- Dataful's own Terms & Conditions govern reuse/redistribution of their processed exports (separate from the underlying government data's license) — review before publishing derived data externally (e.g. the public dashboard), since redistribution rights on a paid dataset may be more restrictive than on open government data.
- **Attribution required in any published output** (dashboard, policy brief): Dept. of Consumer Affairs, Government of India (original data), Dataful / Factly Media & Research (processing/republishing).
- Downloads are subscription/purchase-limited (15/30 days on Bronze) — ingestion should fetch and cache each commodity file once (Phase 1 `data/raw/`, DVC-tracked) rather than re-downloading on every pipeline run.

## Known caveats (confirmed during Phase 1 ingestion)
- Real missingness in `price`: 1,262/251,132 rows missing for Onion, 28,093/251,132 for Milk (spot-checked) — likely inconsistent state-level reporting rather than data corruption. Every dropped/imputed row must be attributable to a named rule (Phase 2 DoD), not silently dropped.
- `unit` is not uniform across commodities or price-types — must be normalized (e.g. quintal → kg) before computing `margin_pct` in Phase 2.
- Raw files are 17 zips (`<dataset_id>- Dataful.zip`, each containing `metadata.csv` + one data CSV) in `data/raw/`, DVC-tracked as a single directory (`data/raw.dvc`). They were purchased and downloaded manually via browser (Dataful requires a login-gated payment flow that resists automation) — `civiclens.ingest.loaders` reads them from disk rather than re-fetching over HTTP. Re-running `make ingest` re-validates and re-hashes but does not re-download.
