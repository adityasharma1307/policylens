import numpy as np
import pandas as pd

from policylens.dashboard.charts import (
    DIVERGING_NEGATIVE,
    DIVERGING_POSITIVE,
    convergence_line,
    margin_histogram,
    retail_vs_wholesale_scatter,
    state_commodity_heatmap,
    state_effects_diverging_bar,
    state_ranking_bar,
)


def test_state_ranking_bar_sorted_ascending_for_horizontal_bar():
    summary = pd.DataFrame(
        {
            "state": ["Delhi", "Kerala", "Ladakh"],
            "median_margin": [0.20, 0.05, 0.02],
            "n": [10, 10, 10],
        }
    )
    fig = state_ranking_bar(summary)
    bar = fig.data[0]
    # Horizontal bars render bottom-to-top, so ascending y order puts the largest on top.
    assert list(bar.y) == ["Ladakh", "Kerala", "Delhi"]


def test_state_commodity_heatmap_caps_zmax_at_95th_percentile():
    rng = np.random.default_rng(0)
    states = [f"S{i}" for i in range(20)]
    commodities = [f"C{i}" for i in range(20)]
    values = rng.uniform(0.05, 0.15, size=(20, 20))
    values[0, 0] = 5.0  # one extreme outlier cell
    pivot = pd.DataFrame(values, index=states, columns=commodities)

    fig = state_commodity_heatmap(pivot)
    heatmap = fig.data[0]
    assert heatmap.zmax < 1.0  # capped well below the raw 5.0 outlier
    assert heatmap.zmax > 0
    # The outlier's true value is still in the underlying data, just visually capped.
    assert float(np.nanmax(heatmap.z)) == 5.0


def test_state_effects_diverging_bar_colors_by_sign():
    effects = pd.DataFrame(
        {
            "state": ["A", "B"],
            "coef_vs_reference": [0.1, -0.1],
            "ci_low": [0.08, -0.12],
            "ci_high": [0.12, -0.08],
        }
    )
    fig = state_effects_diverging_bar(effects)
    bar = fig.data[0]
    colors = dict(zip(bar.y, bar.marker.color, strict=True))
    assert colors["A"] == DIVERGING_POSITIVE
    assert colors["B"] == DIVERGING_NEGATIVE


def test_margin_histogram_builds_without_error():
    fig = margin_histogram(pd.Series([0.05, 0.1, 0.15, 0.2]))
    assert fig.data[0].type == "histogram"


def test_retail_vs_wholesale_scatter_builds_without_error():
    df = pd.DataFrame({"wholesale_price": [10, 20, 30], "retail_price": [12, 24, 36]})
    fig = retail_vs_wholesale_scatter(df)
    assert fig.data[0].type == "scattergl"


def test_convergence_line_builds_without_error():
    df = pd.DataFrame({"year_month": ["2020-01", "2020-02"], "cv_across_states": [0.3, 0.35]})
    fig = convergence_line(df)
    assert fig.data[0].type == "scatter"
