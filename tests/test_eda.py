import pandas as pd
import pytest

from civiclens.analysis.eda import run_eda, summary_by_commodity, summary_by_state


@pytest.fixture
def wide_df():
    return pd.DataFrame(
        [
            {"state": "Delhi", "commodity": "Onion", "retail_price": 25.0,
             "wholesale_price": 20.0, "margin_pct": 0.25},
            {"state": "Delhi", "commodity": "Onion", "retail_price": 27.0,
             "wholesale_price": 22.0, "margin_pct": 0.227},
            {"state": "Kerala", "commodity": "Onion", "retail_price": 30.0,
             "wholesale_price": 20.0, "margin_pct": 0.5},
            {"state": "Kerala", "commodity": "Rice", "retail_price": None,
             "wholesale_price": None, "margin_pct": None},
        ]
    )


def test_summary_by_state_excludes_missing_margin(wide_df):
    result = summary_by_state(wide_df)
    assert set(result["state"]) == {"Delhi", "Kerala"}
    delhi = result[result["state"] == "Delhi"].iloc[0]
    assert delhi["count"] == 2


def test_summary_by_commodity_excludes_missing_margin(wide_df):
    result = summary_by_commodity(wide_df)
    assert list(result["commodity"]) == ["Onion"]


def test_run_eda_returns_expected_keys(wide_df, tmp_path, monkeypatch):
    import civiclens.report.figures as figures_module

    monkeypatch.setattr(figures_module, "FIGURES_DIR", tmp_path)
    summary = run_eda(wide_df)
    assert summary["n_rows_with_margin"] == 3
    assert "state_summary" in summary
    assert "commodity_summary" in summary
    assert list(tmp_path.glob("*.png"))
