import pandas as pd
import plotly.graph_objects as go

from civiclens.dashboard.theme import (
    BASELINE,
    CATEGORICAL,
    FONT_FAMILY,
    GRIDLINE,
    SEQUENTIAL_BLUE,
    SURFACE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

DIVERGING_POSITIVE = CATEGORICAL["blue"]
DIVERGING_NEGATIVE = "#e34948"  # categorical slot 8 (red), used here as the diverging pole
BLUE_COLORSCALE = [[i / (len(SEQUENTIAL_BLUE) - 1), c] for i, c in enumerate(SEQUENTIAL_BLUE)]


def _base_layout(fig: go.Figure, title: str, height: int = 420) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=TEXT_PRIMARY, family=FONT_FAMILY)),
        font=dict(family=FONT_FAMILY, color=TEXT_SECONDARY, size=12),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        height=height,
        margin=dict(l=10, r=10, t=48, b=10),
        hoverlabel=dict(bgcolor=SURFACE, font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY)),
    )
    fig.update_xaxes(
        showgrid=True, gridcolor=GRIDLINE, gridwidth=1, zeroline=False, linecolor=BASELINE
    )
    fig.update_yaxes(showgrid=False, zeroline=False, linecolor=BASELINE)
    return fig


def state_ranking_bar(summary: pd.DataFrame, unit_label: str = "margin") -> go.Figure:
    """Compare-magnitude job: one hue, shade encodes the value itself."""
    ordered = summary.sort_values("median_margin", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=ordered["median_margin"],
            y=ordered["state"],
            orientation="h",
            marker=dict(
                color=ordered["median_margin"],
                colorscale=BLUE_COLORSCALE,
                line=dict(width=0),
            ),
            customdata=ordered[["n"]] if "n" in ordered.columns else None,
            hovertemplate="<b>%{x:.1%}</b> median " + unit_label + "<br>%{y}<extra></extra>",
        )
    )
    fig.update_xaxes(tickformat=".0%", title="Median margin")
    fig.update_layout(bargap=0.25)
    return _base_layout(fig, "State ranking by median retail-wholesale margin", height=760)


def state_commodity_heatmap(pivot: pd.DataFrame) -> go.Figure:
    # Cap the color scale at the 95th percentile: a few genuinely extreme cells
    # (e.g. Delhi x Onion at ~130%) would otherwise stretch the scale and wash
    # out contrast for the other ~95% of cells. Capped cells still show their
    # true value on hover -- only the color saturates, the data doesn't change.
    values = pivot.to_numpy()
    finite = values[~pd.isna(values)]
    zmax = float(pd.Series(finite).quantile(0.95)) if len(finite) else 1.0

    fig = go.Figure(
        go.Heatmap(
            z=values,
            x=pivot.columns,
            y=pivot.index,
            zmin=0,
            zmax=zmax,
            colorscale=BLUE_COLORSCALE,
            hovertemplate="<b>%{z:.1%}</b> median margin<br>%{y} × %{x}<extra></extra>",
            colorbar=dict(title="Margin", tickformat=".0%", outlinewidth=0),
            xgap=2,
            ygap=2,
        )
    )
    fig.update_xaxes(tickangle=-45, side="top")
    return _base_layout(fig, "Median margin by state × commodity", height=820)


def state_effects_diverging_bar(effects: pd.DataFrame) -> go.Figure:
    """Above/below baseline job: diverging color, error bars carry the 95% CI."""
    ordered = effects.sort_values("coef_vs_reference", ascending=True)
    colors = [
        DIVERGING_POSITIVE if v >= 0 else DIVERGING_NEGATIVE for v in ordered["coef_vs_reference"]
    ]
    fig = go.Figure(
        go.Bar(
            x=ordered["coef_vs_reference"],
            y=ordered["state"],
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            error_x=dict(
                type="data",
                symmetric=False,
                array=ordered["ci_high"] - ordered["coef_vs_reference"],
                arrayminus=ordered["coef_vs_reference"] - ordered["ci_low"],
                color=TEXT_MUTED,
                thickness=1,
                width=0,
            ),
            hovertemplate="<b>%{x:+.1%}</b> vs. reference state<br>%{y}<extra></extra>",
        )
    )
    fig.add_vline(x=0, line_width=1, line_color=BASELINE)
    fig.update_xaxes(tickformat="+.0%", title="Coefficient vs. reference state (95% CI)")
    fig.update_layout(bargap=0.25)
    return _base_layout(fig, "Confounder-adjusted state effect on margin", height=760)


def margin_histogram(values: pd.Series) -> go.Figure:
    fig = go.Figure(
        go.Histogram(
            x=values,
            marker=dict(color=CATEGORICAL["blue"], line=dict(width=0)),
            nbinsx=60,
            hovertemplate="%{x:.1%}<br><b>%{y:,}</b> observations<extra></extra>",
        )
    )
    fig.update_xaxes(tickformat=".0%", title="Retail-wholesale margin")
    fig.update_yaxes(title="Count")
    return _base_layout(fig, "Margin distribution (current selection)", height=340)


def retail_vs_wholesale_scatter(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Scattergl(
            x=df["wholesale_price"],
            y=df["retail_price"],
            mode="markers",
            marker=dict(color=CATEGORICAL["blue"], size=5, opacity=0.25, line=dict(width=0)),
            hovertemplate="Wholesale ₹%{x:.1f}<br><b>Retail ₹%{y:.1f}</b><extra></extra>",
        )
    )
    fig.update_xaxes(type="log", title="Wholesale price (₹, log scale)")
    fig.update_yaxes(type="log", title="Retail price (₹, log scale)")
    return _base_layout(fig, "Retail vs. wholesale price", height=420)


def convergence_line(cv_series: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=cv_series["year_month"],
            y=cv_series["cv_across_states"],
            mode="lines",
            line=dict(color=CATEGORICAL["blue"], width=2),
            hovertemplate="%{x}<br><b>CV %{y:.2f}</b><extra></extra>",
        )
    )
    fig.update_yaxes(title="Coefficient of variation across states")
    fig.update_xaxes(title="Month")
    return _base_layout(fig, "Cross-state price dispersion over time", height=340)
