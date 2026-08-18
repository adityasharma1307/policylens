import pandas as pd
import pytest

from policylens.transform.normalize import normalize_price_units, pivot_to_wide


@pytest.fixture
def clean_long():
    return pd.DataFrame(
        [
            {"date": pd.Timestamp("2020-01-01"), "state": "Delhi", "commodity": "Onion",
             "market": "Wholesale", "price": 2000.0},
            {"date": pd.Timestamp("2020-01-01"), "state": "Delhi", "commodity": "Onion",
             "market": "Retail", "price": 25.0},
            {"date": pd.Timestamp("2020-01-01"), "state": "Kerala", "commodity": "Onion",
             "market": "Wholesale", "price": 3000.0},
            # Kerala Retail intentionally missing for this date.
        ]
    )


def test_normalize_divides_wholesale_by_100(clean_long):
    result = normalize_price_units(clean_long)
    wholesale_row = result[(result["state"] == "Delhi") & (result["market"] == "Wholesale")]
    assert wholesale_row["price_normalized"].iloc[0] == 20.0


def test_normalize_leaves_retail_unchanged(clean_long):
    result = normalize_price_units(clean_long)
    retail_row = result[(result["state"] == "Delhi") & (result["market"] == "Retail")]
    assert retail_row["price_normalized"].iloc[0] == 25.0


def test_pivot_computes_margin_pct(clean_long):
    normalized = normalize_price_units(clean_long)
    wide = pivot_to_wide(normalized)
    delhi = wide[wide["state"] == "Delhi"].iloc[0]
    # (25 - 20) / 20 == 0.25
    assert delhi["margin_pct"] == pytest.approx(0.25)


def test_pivot_keeps_missing_side_as_nan_not_dropped(clean_long):
    normalized = normalize_price_units(clean_long)
    wide = pivot_to_wide(normalized)
    kerala = wide[wide["state"] == "Kerala"].iloc[0]
    assert pd.isna(kerala["retail_price"])
    assert kerala["wholesale_price"] == 30.0
    assert pd.isna(kerala["margin_pct"])


def test_pivot_one_row_per_state_commodity_date(clean_long):
    normalized = normalize_price_units(clean_long)
    wide = pivot_to_wide(normalized)
    assert len(wide) == wide.drop_duplicates(subset=["state", "commodity", "date"]).shape[0]
