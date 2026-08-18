import matplotlib

matplotlib.use("Agg")
from pathlib import Path

import matplotlib.pyplot as plt

from civiclens.config import ROOT_DIR

FIGURES_DIR = ROOT_DIR / "reports" / "figures"


def save_figure(fig: plt.Figure, name: str) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path
