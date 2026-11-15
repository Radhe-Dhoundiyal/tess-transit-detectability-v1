"""Recreate the V1.1 comparison figures from the included paired records."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from verify_grid_comparison import read, summarize

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "results/figures"
TEAL, BLUE, OCHRE, INK, MUTED = "#087f7a", "#326eb5", "#a76b10", "#182e3b", "#546a7b"
BACKGROUND = "#f8fafc"


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 12,
        "text.color": INK, "axes.labelcolor": INK,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "figure.facecolor": BACKGROUND, "axes.facecolor": BACKGROUND,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#bdcbd5", "savefig.dpi": 320,
    })


def recovery_figure(frame, summary):
    n = summary["trials"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 7), gridspec_kw={"width_ratios": [1.3, 1]})
    fig.subplots_adjust(left=.09, right=.97, bottom=.29, top=.72, wspace=.4)
    fig.text(.07, .91, "Period-grid recovery on the selected benchmark", size=21, weight="bold")
    fig.text(.07, .84, f"{n} paired trials on {summary['hosts']} selected TESS host substrates", size=14, color=MUTED)
    x = np.arange(2)
    old = [summary["baseline_direct"], summary["baseline_direct_top1_literal"]]
    new = [summary["alternative_direct"], summary["alternative_direct_top1_literal"]]
    ax = axes[0]
    for offset, counts, color, label in ((-.18, old, BLUE, "V1 capped grid"), (.18, new, TEAL, "V1.1 union grid")):
        ax.bar(x + offset, np.array(counts) / n * 100, .32, color=color, label=label, zorder=3)
        for index, count in enumerate(counts):
            ax.text(index + offset, count / n * 100 + 1.1, f"{count}/{n}", ha="center", size=11, weight="bold")
    ax.set_xticks(x, ["Primary direct\ntop-10", "Literal direct\nrank-1"])
    ax.set_ylabel("Recovered injections (%)")
    ax.set_ylim(0, 48)
    ax.grid(axis="y", color="#dde5eb", zorder=0)
    ax.legend(frameon=False, fontsize=10, loc="upper left")
    ax = axes[1]
    delta = summary["absolute_difference"] * 100
    low, high = np.array(summary["difference_percentile_95_ci"]) * 100
    ax.errorbar(delta, 0, xerr=[[delta-low], [high-delta]], fmt="o", markersize=8,
                capsize=5, color=TEAL, linewidth=2)
    ax.axvline(0, color="#bdcbd5", linewidth=1)
    ax.set_xlim(-1, 12)
    ax.set_ylim(-1, 1)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Change in primary recovery\n(percentage points)")
    ax.set_title(f"+{delta:.4f} pp", fontsize=18, weight="bold", pad=18)
    ax.text(.5, .16, f"Descriptive 95% host-bootstrap interval\n+{low:.4f} to +{high:.4f} pp", transform=ax.transAxes,
            ha="center", va="center", size=10, color=MUTED)
    fig.text(.07, .17, f"{summary['paired_gains']} primary gains · {summary['paired_losses']} loss · {summary['unchanged_primary']} unchanged", size=13)
    fig.text(.07, .11, "32 exploratory trials / 4 hosts + 288 extension trials / 36 hosts.\nPeriod-and-epoch recovery; no calibrated detection-significance threshold.", size=11, color=MUTED)
    fig.text(.07, .035, "NASA / TESS / MAST · NASA Exoplanet Archive · Astropy", size=10, color=MUTED)
    fig.savefig(FIGURES / "period_grid_recovery_v1_1_0.png", metadata={"Software": "Matplotlib; scripts/plot_grid_comparison.py"})
    plt.close(fig)


def host_figure(frame):
    records = []
    for _, group in frame.groupby("selection_unit_id"):
        first = group.iloc[0]
        gains = int((~group.baseline_direct_top10 & group.alternative_direct_top10).sum())
        losses = int((group.baseline_direct_top10 & ~group.alternative_direct_top10).sum())
        records.append((int(first.benchmark_order), first.host_name, first.cohort, gains, losses))
    records.sort()
    fig, ax = plt.subplots(figsize=(12, 12))
    fig.subplots_adjust(left=.33, right=.93, top=.84, bottom=.13)
    y = np.arange(len(records))
    gains = np.array([row[3] for row in records])
    losses = np.array([row[4] for row in records])
    ax.barh(y, gains, color=TEAL, height=.67, label="Primary gain", zorder=3)
    ax.barh(y, -losses, color=OCHRE, height=.67, label="Primary loss", zorder=3)
    exploratory = np.array([row[2] == "original_exploratory" for row in records])
    ax.scatter((gains-losses)[exploratory], y[exploratory], s=58, facecolors="none",
               edgecolors=INK, linewidth=1.4, label="Exploratory host (net change)", zorder=4)
    ax.set_yticks(y, [f"{row[0]:02d}  {row[1]}" for row in records], fontsize=10)
    ax.invert_yaxis()
    ax.set_ylim(len(records)-.35, -.7)
    ax.axvline(0, color="#bdcbd5", linewidth=1)
    ax.set_xlim(-1.6, max(gains.max(), 3) + .6)
    ax.set_xticks(np.arange(-1, max(gains.max(), 3)+1))
    ax.grid(axis="x", color="#dde5eb", zorder=0)
    ax.set_xlabel("Change in primary direct top-10 recovery (trials per host)")
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    fig.text(.07, .94, "Where the primary outcomes changed", size=23, weight="bold")
    fig.text(.07, .89, "All 40 hosts · 8 paired injections per host · 20 gains and one loss", size=14, color=MUTED)
    fig.text(.07, .065, "Negative bars retain losses. Open markers identify the original four exploratory hosts.\nHost identities and cohorts follow the saved experiment; this is a selected finite benchmark.", size=11, color=MUTED)
    fig.text(.07, .025, "NASA / TESS / MAST · NASA Exoplanet Archive · Astropy", size=10, color=MUTED)
    fig.savefig(FIGURES / "period_grid_hosts_v1_1_0.png", metadata={"Software": "Matplotlib; scripts/plot_grid_comparison.py"})
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figure", choices=("all", "recovery", "hosts"), default="all")
    args = parser.parse_args()
    frame = read("period_grid_pairs_v1_1_0.csv")
    summary = summarize(frame)["combined_finite_benchmark"]
    style()
    if args.figure in ("all", "recovery"):
        recovery_figure(frame, summary)
    if args.figure in ("all", "hosts"):
        host_figure(frame)
