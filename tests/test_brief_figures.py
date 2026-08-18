import json

import civiclens.report.brief_figures as brief_figures
from civiclens.report.brief_figures import plot_state_extremes


def test_plot_state_extremes_selects_top_and_bottom_n(tmp_path, monkeypatch):
    states = [
        {
            "state": f"S{i}",
            "coef_vs_reference": i / 10,
            "ci_low": i / 10 - 0.01,
            "ci_high": i / 10 + 0.01,
        }
        for i in range(-5, 6)
    ]
    results_path = tmp_path / "results.json"
    results_path.write_text(json.dumps({"confounder_model": {"state_effects": states}}))
    monkeypatch.setattr(brief_figures, "RESULTS_PATH", results_path)

    fig = plot_state_extremes(n=3)
    ax = fig.axes[0]
    labels = [t.get_text() for t in ax.get_yticklabels()]
    assert len(labels) == 6
    assert "S-5" in labels
    assert "S5" in labels
    assert "S0" not in labels
