import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

from policylens.ingest.sources import SOURCES

_VALID_DATASET_IDS = {s.dataset_id for s in SOURCES}

raw_prices_schema = DataFrameSchema(
    {
        "date": Column(str, Check.str_matches(r"^\d{2}-\d{2}-\d{4}$"), nullable=False),
        "state": Column(str, nullable=False),
        "market": Column(str, Check.isin(["Retail", "Wholesale"]), nullable=False),
        "commodity": Column(str, nullable=False),
        "price": Column(
            str,
            Check(lambda s: s.isna() | s.str.match(r"^\d+(\.\d+)?$"), element_wise=False),
            nullable=True,
        ),
        "unit": Column(str, nullable=False),
        "note": Column(str, nullable=True),
        "source_dataset_id": Column(int, Check.isin(_VALID_DATASET_IDS), nullable=False),
        "source_file_sha256": Column(str, Check.str_matches(r"^[0-9a-f]{64}$"), nullable=False),
        "ingested_at": Column(str, nullable=False),
    },
    strict=True,
    coerce=False,
)


def validate_raw_prices(df: pa.typing.DataFrame) -> pa.typing.DataFrame:
    return raw_prices_schema.validate(df, lazy=True)


clean_prices_long_schema = DataFrameSchema(
    {
        "date": Column("datetime64[ns]", nullable=False),
        "state": Column(str, nullable=False),
        "market": Column(str, Check.isin(["Retail", "Wholesale"]), nullable=False),
        "commodity": Column(str, nullable=False),
        "price": Column(float, Check.ge(0), nullable=True),
        "unit": Column(str, nullable=False),
        "source_dataset_id": Column(int, Check.isin(_VALID_DATASET_IDS), nullable=False),
        "source_file_sha256": Column(str, Check.str_matches(r"^[0-9a-f]{64}$"), nullable=False),
        "ingested_at": Column(str, nullable=False),
        "price_missing": Column(bool, nullable=False),
        "price_outlier": Column(bool, nullable=False),
        "price_normalized": Column(float, Check.ge(0), nullable=True),
    },
    strict=True,
    coerce=False,
)


def validate_clean_prices_long(df: pa.typing.DataFrame) -> pa.typing.DataFrame:
    return clean_prices_long_schema.validate(df, lazy=True)


prices_wide_schema = DataFrameSchema(
    {
        "state": Column(str, nullable=False),
        "commodity": Column(str, nullable=False),
        "date": Column("datetime64[ns]", nullable=False),
        "retail_price": Column(float, Check.ge(0), nullable=True),
        "wholesale_price": Column(float, Check.ge(0), nullable=True),
        "margin_pct": Column(float, nullable=True),
    },
    strict=True,
    coerce=False,
    unique=["state", "commodity", "date"],
)


def validate_prices_wide(df: pa.typing.DataFrame) -> pa.typing.DataFrame:
    return prices_wide_schema.validate(df, lazy=True)
