from policylens.config import DATA_DIR, INTERIM_DIR, PROCESSED_DIR, RAW_DIR


def test_data_dirs_are_nested_under_data_dir() -> None:
    assert RAW_DIR.parent == DATA_DIR
    assert INTERIM_DIR.parent == DATA_DIR
    assert PROCESSED_DIR.parent == DATA_DIR
