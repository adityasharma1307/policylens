from civiclens.config import DUCKDB_PATH
from civiclens.lineage.emit import emit_job
from civiclens.warehouse.duck import build_warehouse, query


def main() -> None:
    con = build_warehouse()

    counts = {
        table: query(f"SELECT COUNT(*) AS n FROM {table}", con)["n"].iloc[0]
        for table in ["dim_state", "dim_commodity", "dim_date", "fact_price"]
    }
    for table, n in counts.items():
        print(f"{table}: {n} rows")
    print(f"Warehouse -> {DUCKDB_PATH}")

    table_columns = {
        "dim_state": {"state_id": "int", "state": "str"},
        "dim_commodity": {"commodity_id": "int", "commodity": "str"},
        "dim_date": {"date": "date", "year": "int", "month": "int", "year_month": "str"},
        "fact_price": {
            "date": "date",
            "state_id": "int",
            "commodity_id": "int",
            "retail_price": "float",
            "wholesale_price": "float",
            "margin_pct": "float",
        },
    }
    emit_job(
        job_name="warehouse",
        inputs={"data/processed/prices_wide.parquet": table_columns["fact_price"]},
        outputs={f"duckdb://{table}": cols for table, cols in table_columns.items()},
    )


if __name__ == "__main__":
    main()
