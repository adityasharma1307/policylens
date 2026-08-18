import json

import pandas as pd

from civiclens.config import INTERIM_DIR
from civiclens.ingest.loaders import load_source
from civiclens.ingest.sources import SOURCES
from civiclens.validate.schemas import validate_raw_prices


def main() -> None:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    manifest = []
    frames = []
    for source in SOURCES:
        df = load_source(source)
        frames.append(df)
        manifest.append(
            {
                "dataset_id": source.dataset_id,
                "commodity": source.commodity,
                "row_count": len(df),
                "sha256": df["source_file_sha256"].iloc[0],
            }
        )

    raw = pd.concat(frames, ignore_index=True)
    validated = validate_raw_prices(raw)

    out_path = INTERIM_DIR / "raw_prices.parquet"
    validated.to_parquet(out_path, index=False)

    manifest_path = INTERIM_DIR / "ingest_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    print(f"Ingested {len(validated)} rows from {len(SOURCES)} sources -> {out_path}")
    print(f"Manifest written -> {manifest_path}")


if __name__ == "__main__":
    main()
