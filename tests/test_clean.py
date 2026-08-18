import pandas as pd
import pytest

from civiclens.transform.clean import clean, flag_price_outliers


@pytest.fixture
def raw_long():
    return pd.DataFrame(
        [
            {
                "date": "01-01-2020",
                "state": "Delhi",
                "market": "Wholesale",
                "commodity": "Onion",
                "price": "2000.0",
                "unit": "price in rupees per quintal",
                "note": None,
                "source_dataset_id": 19942,
                "source_file_sha256": "a" * 64,
                "ingested_at": "2026-08-18T00:00:00+00:00",
            },
            {
                "date": "01-01-2020",
                "state": "Delhi",
                "market": "Retail",
                "commodity": "Onion",
                "price": None,
                "unit": "price in rupees per kilogram",
                "note": None,
                "source_dataset_id": 19942,
                "source_file_sha256": "a" * 64,
                "ingested_at": "2026-08-18T00:00:00+00:00",
            },
            {
                "date": "01-01-2020",
                "state": "Delhi",
                "market": "Wholesale",
                "commodity": "Onion",
                "price": "2000.0",
                "unit": "price in rupees per quintal",
                "note": None,
                "source_dataset_id": 19942,
                "source_file_sha256": "a" * 64,
                "ingested_at": "2026-08-18T00:00:00+00:00",
            },
        ]
    )


def test_clean_drops_exact_duplicates(raw_long):
    result = clean(raw_long)
    assert len(result) == 2


def test_clean_parses_dates_to_datetime(raw_long):
    result = clean(raw_long)
    assert pd.api.types.is_datetime64_any_dtype(result["date"])
    assert result["date"].iloc[0] == pd.Timestamp("2020-01-01")


def test_clean_flags_missing_price_without_dropping(raw_long):
    result = clean(raw_long)
    assert result["price_missing"].sum() == 1
    assert len(result) == 2


def test_clean_removes_note_column(raw_long):
    result = clean(raw_long)
    assert "note" not in result.columns


def test_flag_price_outliers_flags_extreme_value():
    df = pd.DataFrame(
        {
            "commodity": ["Onion"] * 10,
            "market": ["Wholesale"] * 10,
            "price": [100.0, 102.0, 98.0, 101.0, 99.0, 100.0, 103.0, 97.0, 100.0, 100000.0],
        }
    )
    result = flag_price_outliers(df)
    assert result["price_outlier"].iloc[-1]
    assert not result["price_outlier"].iloc[:-1].any()
