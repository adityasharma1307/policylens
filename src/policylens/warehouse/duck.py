import duckdb
import pandas as pd

from policylens.config import DUCKDB_PATH, PROCESSED_DIR


def get_connection() -> duckdb.DuckDBPyConnection:
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DUCKDB_PATH))


def build_warehouse(con: duckdb.DuckDBPyConnection | None = None) -> duckdb.DuckDBPyConnection:
    """Load data/processed/prices_wide.parquet into a small star schema:
    dim_state, dim_commodity, dim_date + fact_price, plus a denormalized
    fact_price_view for convenient querying.
    """
    con = con or get_connection()
    wide_path = str(PROCESSED_DIR / "prices_wide.parquet")

    con.execute(
        """
        CREATE OR REPLACE TABLE dim_state AS
        SELECT ROW_NUMBER() OVER (ORDER BY state) AS state_id, state
        FROM (SELECT DISTINCT state FROM read_parquet(?))
        """,
        [wide_path],
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE dim_commodity AS
        SELECT ROW_NUMBER() OVER (ORDER BY commodity) AS commodity_id, commodity
        FROM (SELECT DISTINCT commodity FROM read_parquet(?))
        """,
        [wide_path],
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE dim_date AS
        SELECT DISTINCT
            date,
            EXTRACT(year FROM date) AS year,
            EXTRACT(month FROM date) AS month,
            strftime(date, '%Y-%m') AS year_month
        FROM read_parquet(?)
        """,
        [wide_path],
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE fact_price AS
        SELECT
            w.date,
            s.state_id,
            c.commodity_id,
            w.retail_price,
            w.wholesale_price,
            w.margin_pct
        FROM read_parquet(?) w
        JOIN dim_state s USING (state)
        JOIN dim_commodity c USING (commodity)
        """,
        [wide_path],
    )
    con.execute(
        """
        CREATE OR REPLACE VIEW fact_price_view AS
        SELECT
            f.date, d.year, d.month, d.year_month,
            s.state, c.commodity,
            f.retail_price, f.wholesale_price, f.margin_pct
        FROM fact_price f
        JOIN dim_state s USING (state_id)
        JOIN dim_commodity c USING (commodity_id)
        JOIN dim_date d USING (date)
        """
    )
    return con


def query(sql: str, con: duckdb.DuckDBPyConnection | None = None) -> pd.DataFrame:
    con = con or get_connection()
    return con.execute(sql).fetchdf()
