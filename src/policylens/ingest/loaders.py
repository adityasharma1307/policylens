import hashlib
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from policylens.ingest.sources import SOURCES, Source


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_source(source: Source) -> pd.DataFrame:
    """Load one commodity's raw CSV out of its zip, tagged with provenance columns.

    Kept as raw strings deliberately -- type coercion and missing-value handling
    belong to the transform stage, not ingestion.
    """
    if not source.zip_path.exists():
        raise FileNotFoundError(
            f"Missing raw file for dataset {source.dataset_id}: {source.zip_path}"
        )

    with zipfile.ZipFile(source.zip_path) as zf:
        csv_names = [n for n in zf.namelist() if n.endswith(".csv") and n != "metadata.csv"]
        if len(csv_names) != 1:
            raise ValueError(
                f"Expected exactly one data CSV in {source.zip_path}, found {csv_names}"
            )
        with zf.open(csv_names[0]) as f:
            df = pd.read_csv(f, dtype=str)

    df["source_dataset_id"] = source.dataset_id
    df["source_file_sha256"] = sha256_of_file(source.zip_path)
    df["ingested_at"] = datetime.now(UTC).isoformat()
    return df


def load_all_sources(sources: list[Source] = SOURCES) -> pd.DataFrame:
    """Load and concatenate every commodity source into one long-format raw table."""
    frames = [load_source(s) for s in sources]
    return pd.concat(frames, ignore_index=True)
