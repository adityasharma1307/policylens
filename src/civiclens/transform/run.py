import json

import pandas as pd

from civiclens.config import INTERIM_DIR, PROCESSED_DIR
from civiclens.lineage.emit import emit_job
from civiclens.transform.clean import clean
from civiclens.transform.normalize import normalize_price_units, pivot_to_wide
from civiclens.transform.quality_report import build_quality_report
from civiclens.validate.schemas import validate_clean_prices_long, validate_prices_wide


def _dtype_map(df: pd.DataFrame) -> dict[str, str]:
    return {col: str(dtype) for col, dtype in df.dtypes.items()}


def main() -> None:
    raw = pd.read_parquet(INTERIM_DIR / "raw_prices.parquet")

    long_df = clean(raw)
    long_df = normalize_price_units(long_df)
    long_df = validate_clean_prices_long(long_df)

    wide_df = pivot_to_wide(long_df)
    wide_df = validate_prices_wide(wide_df)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    long_path = INTERIM_DIR / "clean_prices_long.parquet"
    wide_path = PROCESSED_DIR / "prices_wide.parquet"
    long_df.to_parquet(long_path, index=False)
    wide_df.to_parquet(wide_path, index=False)

    report = build_quality_report(long_df, wide_df)
    report_path = INTERIM_DIR / "data_quality_report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str))

    print(f"Raw rows: {len(raw)} -> clean long rows: {len(long_df)} -> wide rows: {len(wide_df)}")
    print(f"Clean long  -> {long_path}")
    print(f"Wide (analysis-ready) -> {wide_path}")
    print(f"Data quality report -> {report_path}")

    emit_job(
        job_name="transform",
        inputs={"data/interim/raw_prices.parquet": _dtype_map(raw)},
        outputs={
            "data/interim/clean_prices_long.parquet": _dtype_map(long_df),
            "data/processed/prices_wide.parquet": _dtype_map(wide_df),
        },
    )


if __name__ == "__main__":
    main()
