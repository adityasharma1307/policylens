import matplotlib.pyplot as plt
import pandas as pd

from policylens.report.figures import save_figure


def summary_by_state(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.dropna(subset=["margin_pct"])
        .groupby("state")["margin_pct"]
        .agg(["count", "mean", "median", "std"])
        .sort_values("median", ascending=False)
        .reset_index()
    )


def summary_by_commodity(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.dropna(subset=["margin_pct"])
        .groupby("commodity")["margin_pct"]
        .agg(["count", "mean", "median", "std"])
        .sort_values("median", ascending=False)
        .reset_index()
    )


def plot_margin_by_state(df: pd.DataFrame) -> plt.Figure:
    order = summary_by_state(df)["state"]
    fig, ax = plt.subplots(figsize=(10, 12))
    data = [
        df.loc[df["state"] == s, "margin_pct"].dropna() for s in order
    ]
    ax.boxplot(data, orientation="horizontal", tick_labels=list(order), showfliers=False)
    ax.set_xlabel("Retail-wholesale margin (%)")
    ax.set_title("Margin distribution by state, all commodities pooled")
    return fig


def plot_margin_by_commodity(df: pd.DataFrame) -> plt.Figure:
    order = summary_by_commodity(df)["commodity"]
    fig, ax = plt.subplots(figsize=(10, 7))
    data = [df.loc[df["commodity"] == c, "margin_pct"].dropna() for c in order]
    ax.boxplot(data, orientation="horizontal", tick_labels=list(order), showfliers=False)
    ax.set_xlabel("Retail-wholesale margin (%)")
    ax.set_title("Margin distribution by commodity, all states pooled")
    return fig


def plot_retail_vs_wholesale(df: pd.DataFrame) -> plt.Figure:
    valid = df.dropna(subset=["retail_price", "wholesale_price"])
    sample = valid.sample(n=min(20000, len(valid)), random_state=42)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(sample["wholesale_price"], sample["retail_price"], alpha=0.15, s=5)
    ax.set_xlabel("Wholesale price (normalized)")
    ax.set_ylabel("Retail price (normalized)")
    ax.set_title("Retail vs. wholesale price (20k-row sample, log-log)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    return fig


def run_eda(df: pd.DataFrame) -> dict:
    """Compute summaries and save figures. Returns the summary dict that feeds the
    data-driven parts of the eventual policy brief.
    """
    state_summary = summary_by_state(df)
    commodity_summary = summary_by_commodity(df)
    correlation = df[["retail_price", "wholesale_price"]].dropna().corr().iloc[0, 1]

    save_figure(plot_margin_by_state(df), "margin_by_state")
    save_figure(plot_margin_by_commodity(df), "margin_by_commodity")
    save_figure(plot_retail_vs_wholesale(df), "retail_vs_wholesale")

    return {
        "n_rows_with_margin": int(df["margin_pct"].notna().sum()),
        "retail_wholesale_correlation": float(correlation),
        "overall_margin_mean": float(df["margin_pct"].mean()),
        "overall_margin_median": float(df["margin_pct"].median()),
        "state_summary": state_summary.to_dict(orient="records"),
        "commodity_summary": commodity_summary.to_dict(orient="records"),
    }
