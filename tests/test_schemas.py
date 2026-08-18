import pandas as pd
import pandera.errors
import pytest

from civiclens.validate.schemas import validate_raw_prices

VALID_ROW = {
    "date": "01-01-2020",
    "state": "Delhi",
    "market": "Wholesale",
    "commodity": "Onion",
    "price": "2000.0",
    "unit": "price in rupees per quintal",
    "note": "",
    "source_dataset_id": 19942,
    "source_file_sha256": "a" * 64,
    "ingested_at": "2026-08-18T00:00:00+00:00",
}


def _df(**overrides):
    row = {**VALID_ROW, **overrides}
    return pd.DataFrame([row])


def test_valid_row_passes():
    validate_raw_prices(_df())


def test_null_price_is_allowed():
    df = _df(price=None)
    validate_raw_prices(df)


def test_bad_market_value_rejected():
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_raw_prices(_df(market="Retial"))


def test_bad_date_format_rejected():
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_raw_prices(_df(date="2020-01-01"))


def test_non_numeric_price_rejected():
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_raw_prices(_df(price="NA"))


def test_unknown_dataset_id_rejected():
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_raw_prices(_df(source_dataset_id=1))


def test_null_state_rejected():
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_raw_prices(_df(state=None))
