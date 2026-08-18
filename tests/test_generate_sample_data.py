import csv
import io

from scripts.generate_sample_data import _csv_for


def test_csv_for_quotes_commodity_names_containing_commas():
    # Real commodity names like "Salt (Iodised, Packed)" contain a comma --
    # unescaped, it would shift every column after it.
    csv_text = _csv_for("Salt (Iodised, Packed)")
    reader = csv.reader(io.StringIO(csv_text))
    header = next(reader)
    assert header == ["date", "state", "market", "commodity", "price", "unit", "note"]
    first_row = next(reader)
    assert first_row[3] == "Salt (Iodised, Packed)"
    assert first_row[0] in ("01-01-2020", "date")


def test_csv_for_produces_expected_row_count():
    csv_text = _csv_for("Onion")
    rows = list(csv.reader(io.StringIO(csv_text)))
    # header + (4 dates * 5 states * 2 markets)
    assert len(rows) == 1 + 4 * 5 * 2


def test_csv_for_has_one_missing_price():
    csv_text = _csv_for("Onion")
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    missing = [r for r in rows if r["price"] == ""]
    assert len(missing) == 1
