import duckdb
import pandas as pd
import pytest

from policylens.warehouse.duck import build_warehouse, query


@pytest.fixture
def wide_parquet(tmp_path, monkeypatch):
    df = pd.DataFrame(
        [
            {"state": "Delhi", "commodity": "Onion", "date": pd.Timestamp("2020-01-01"),
             "retail_price": 25.0, "wholesale_price": 20.0, "margin_pct": 0.25},
            {"state": "Kerala", "commodity": "Onion", "date": pd.Timestamp("2020-01-01"),
             "retail_price": 30.0, "wholesale_price": None, "margin_pct": None},
            {"state": "Delhi", "commodity": "Rice", "date": pd.Timestamp("2020-01-02"),
             "retail_price": 40.0, "wholesale_price": 35.0, "margin_pct": 0.1429},
        ]
    )
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    path = processed_dir / "prices_wide.parquet"
    df.to_parquet(path, index=False)

    import policylens.warehouse.duck as duck_module

    monkeypatch.setattr(duck_module, "PROCESSED_DIR", processed_dir)
    return path


@pytest.fixture
def con():
    connection = duckdb.connect(":memory:")
    yield connection
    connection.close()


def test_build_warehouse_creates_expected_tables(wide_parquet, con):
    build_warehouse(con)
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    assert {"dim_state", "dim_commodity", "dim_date", "fact_price"} <= tables


def test_dim_state_has_distinct_states(wide_parquet, con):
    build_warehouse(con)
    states = query("SELECT state FROM dim_state ORDER BY state", con)
    assert list(states["state"]) == ["Delhi", "Kerala"]


def test_fact_price_row_count_matches_source(wide_parquet, con):
    build_warehouse(con)
    n = query("SELECT COUNT(*) AS n FROM fact_price", con)["n"].iloc[0]
    assert n == 3


def test_fact_price_view_joins_correctly(wide_parquet, con):
    build_warehouse(con)
    result = query(
        "SELECT * FROM fact_price_view WHERE state = 'Delhi' AND commodity = 'Onion'", con
    )
    assert result["retail_price"].iloc[0] == 25.0
    assert result["margin_pct"].iloc[0] == 0.25


def test_fact_price_preserves_nulls(wide_parquet, con):
    build_warehouse(con)
    result = query("SELECT wholesale_price FROM fact_price_view WHERE state = 'Kerala'", con)
    assert result["wholesale_price"].isna().iloc[0]
