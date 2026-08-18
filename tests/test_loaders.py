import zipfile

import pytest

from policylens.ingest.loaders import load_source, sha256_of_file
from policylens.ingest.sources import Source


@pytest.fixture
def fake_source(tmp_path):
    zip_path = tmp_path / "99999- Dataful.zip"
    csv_content = (
        "date,state,market,commodity,price,unit,note\n"
        "01-01-2020,Delhi,Wholesale,Onion,2000.0,price in rupees per quintal,\n"
        "01-01-2020,Delhi,Retail,Onion,25.0,price in rupees per kilogram,\n"
    )
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("metadata.csv", "organisation,Test Org\n")
        zf.writestr(
            "essential-commodity-state-wise-daily-wholesale-and-retail-price-of-onion.csv",
            csv_content,
        )
    return Source(99999, "Onion", zip_path_override=zip_path)


def test_load_source_returns_expected_rows(fake_source):
    df = load_source(fake_source)
    assert len(df) == 2
    assert set(df["market"]) == {"Wholesale", "Retail"}


def test_load_source_attaches_provenance_columns(fake_source):
    df = load_source(fake_source)
    assert (df["source_dataset_id"] == 99999).all()
    assert df["source_file_sha256"].nunique() == 1
    assert len(df["source_file_sha256"].iloc[0]) == 64
    assert df["ingested_at"].notna().all()


def test_load_source_missing_file_raises(tmp_path):
    source = Source(88888, "Nonexistent", zip_path_override=tmp_path / "missing.zip")
    with pytest.raises(FileNotFoundError):
        load_source(source)


def test_load_source_rejects_multiple_data_csvs(tmp_path):
    zip_path = tmp_path / "77777- Dataful.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("metadata.csv", "organisation,Test Org\n")
        zf.writestr("a.csv", "date,state,market,commodity,price,unit,note\n")
        zf.writestr("b.csv", "date,state,market,commodity,price,unit,note\n")

    source = Source(77777, "Ambiguous", zip_path_override=zip_path)
    with pytest.raises(ValueError):
        load_source(source)


def test_sha256_of_file_is_deterministic(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("hello world")
    assert sha256_of_file(f) == sha256_of_file(f)
    assert len(sha256_of_file(f)) == 64
