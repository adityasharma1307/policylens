import json

import matplotlib.pyplot as plt

from policylens.config import ROOT_DIR
from policylens.report.figures import save_figure

RESULTS_PATH = ROOT_DIR / "reports" / "results.json"

POSITIVE = "#2a78d6"
NEGATIVE = "#e34948"


def plot_state_extremes(n: int = 5) -> plt.Figure:
    """Top and bottom N states by confounder-adjusted margin coefficient -- the
    single figure the policy brief leads with.
    """
    results = json.loads(RESULTS_PATH.read_text())
    effects = sorted(
        results["confounder_model"]["state_effects"],
        key=lambda e: e["coef_vs_reference"],
    )
    selected = effects[:n] + effects[-n:]
    states = [e["state"] for e in selected]
    coefs = [e["coef_vs_reference"] for e in selected]
    ci_low = [e["coef_vs_reference"] - e["ci_low"] for e in selected]
    ci_high = [e["ci_high"] - e["coef_vs_reference"] for e in selected]
    colors = [NEGATIVE if c < 0 else POSITIVE for c in coefs]

    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    ax.barh(states, coefs, color=colors, xerr=[ci_low, ci_high], capsize=2, height=0.6)
    ax.axvline(0, color="#c3c2b7", linewidth=1)
    ax.set_xlabel("Adjusted margin vs. reference state (95% CI)")
    ax.set_title(
        f"Highest- and lowest-markup states (top/bottom {n}, adjusted for commodity+month)"
    )
    ax.xaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(xmax=1))
    fig.tight_layout()
    return fig


def main() -> None:
    path = save_figure(plot_state_extremes(), "brief_state_extremes")
    print(f"Brief figure -> {path}")


if __name__ == "__main__":
    main()
