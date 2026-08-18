"""Generate tiny synthetic raw zips matching the real Dataful schema, so CI (and
anyone without a paid Dataful subscription) can exercise the full pipeline
mechanics without the real ~22MB purchased dataset.

Statistically meaningless (5 states x 4 dates x 17 commodities) -- this exists
to prove the pipeline *runs end to end*, not to reproduce the real findings.

SAFETY: always pass an explicit --out-dir. The default is intentionally NOT
data/raw/, so this can never be run accidentally over the real purchased data.
"""

import argparse
import csv
import io
import zipfile
from pathlib import Path

from policylens.ingest.sources import SOURCES

STATES = ["Delhi", "Kerala", "Punjab", "Maharashtra", "Assam"]
DATES = ["01-01-2020", "15-01-2020", "01-02-2020", "15-02-2020"]
BASE_WHOLESALE = 100.0
BASE_RETAIL = 12.5


def _csv_for(commodity: str) -> str:
    # Use csv.writer rather than f-string joins: several real commodity names
    # (e.g. "Salt (Iodised, Packed)") contain commas that must be quoted, or
    # they silently shift every column after them.
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["date", "state", "market", "commodity", "price", "unit", "note"])
    for date_idx, date in enumerate(DATES):
        for state_idx, state in enumerate(STATES):
            wholesale = BASE_WHOLESALE + state_idx * 5 + date_idx * 0.5
            retail = BASE_RETAIL + state_idx * 1.2 + date_idx * 0.1
            retail_str = "" if (state == "Assam" and date_idx == 0) else f"{retail:.2f}"
            writer.writerow(
                [
                    date,
                    state,
                    "Wholesale",
                    commodity,
                    f"{wholesale:.2f}",
                    "price in rupees per quintal",
                    "",
                ]
            )
            writer.writerow(
                [date, state, "Retail", commodity, retail_str, "price in rupees per kilogram", ""]
            )
    return buf.getvalue()


def generate(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for source in SOURCES:
        zip_path = out_dir / f"{source.dataset_id}- Dataful.zip"
        slug = (
            source.commodity.lower()
            .replace(" ", "-")
            .replace("(", "")
            .replace(")", "")
            .replace("/", "-")
            .replace(",", "")
        )
        csv_name = f"essential-commodity-state-wise-daily-wholesale-and-retail-price-of-{slug}.csv"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("metadata.csv", "organisation,Sample Data\n")
            zf.writestr(csv_name, _csv_for(source.commodity))
    print(f"Generated {len(SOURCES)} synthetic raw files in {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        required=True,
        type=Path,
        help="Directory to write synthetic zips into. Never point this at data/raw/ "
        "with real purchased data present -- it will be overwritten.",
    )
    args = parser.parse_args()
    generate(args.out_dir)


if __name__ == "__main__":
    main()
