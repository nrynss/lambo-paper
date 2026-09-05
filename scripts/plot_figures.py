#!/usr/bin/env python3
"""
Generate publication-quality figures for the Lambo research paper.
Outputs:
- src/fig1_dispersion.pdf
- src/fig2_latency.pdf
- src/fig3_dedup_regimes.pdf
"""

import os
import json
import shutil
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "src")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 12,
    "lines.linewidth": 1.7,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--"
})

def generate_fig1_dispersion():
    R = np.arange(1, 13)
    # Illustrative model only.  It plots the inverse-R relationship derived
    # under uniform allocation across independent repositories.  It is not a
    # fitted deployment curve and makes no timing claim.
    delta_r = 1.0 / R

    fig, ax1 = plt.subplots(figsize=(4.8, 3.2), dpi=300)

    color = "#1f77b4"
    ax1.set_xlabel("Repository Count $R$")
    ax1.set_ylabel("Expected Citations / Baseline", color=color)
    line1 = ax1.plot(R, delta_r, color=color, marker="o", label="Illustrative ratio $1/R$")
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.set_ylim(-0.05, 1.05)

    ax1.legend(line1, [l.get_label() for l in line1], loc="upper right")
    ax1.text(0.04, 0.08, "Assumptions: uniform allocation\nindependent repository graphs",
             transform=ax1.transAxes, fontsize=8, va="bottom")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig1_dispersion.pdf")
    plt.savefig(out_path)
    plt.savefig(out_path.replace(".pdf", ".png"), dpi=300)
    plt.close()
    print(f"Generated {out_path}")

def generate_fig0_architecture():
    """Schematic matching the inspected receipt and persistence boundaries."""
    fig, ax = plt.subplots(figsize=(9.4, 3.3), dpi=300)
    ax.set_axis_off()
    def box(x, y, w, h, label, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                    facecolor=color, edgecolor="#334155", linewidth=1.1))
        ax.text(x+w/2, y+h/2, label, ha="center", va="center", fontsize=8)
    def arrow(a, b, label=""):
        ax.annotate("", b, a, arrowprops=dict(arrowstyle="->", lw=1.15, color="#334155"))
        if label:
            ax.text((a[0]+b[0])/2, (a[1]+b[1])/2+0.035, label, ha="center", fontsize=7)
    box(0.03, .57, .17, .24, "Agent clients\nderive / action", "#e0f2fe")
    box(.29, .57, .19, .24, "Validation +\ninteraction opening", "#fef3c7")
    box(.57, .57, .17, .24, "Per-agent FIFO\nadmission lanes", "#dcfce7")
    box(.80, .57, .17, .24, "Background graph\napply + receipt state", "#ede9fe")
    box(.80, .13, .17, .22, "Write-behind store\nand clean-close intents", "#fee2e2")
    arrow((.20,.69),(.29,.69),"request")
    arrow((.48,.69),(.57,.69),"accepted job")
    arrow((.74,.69),(.80,.69),"dequeued job")
    arrow((.29,.59),(.20,.59),"receipt / status")
    arrow((.885,.57),(.885,.35),"separate persistence boundary")
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig0_architecture.pdf")
    plt.savefig(out_path)
    plt.savefig(out_path.replace(".pdf", ".png"), dpi=300)
    plt.close()
    print(f"Generated {out_path}")

def generate_fig2_latency():
    # End-to-end recall p50 observations from lambo Issue #8. The fitted
    # lines summarize those observations; they are not isolated Phase-1 scans.
    N = np.linspace(100, 1600, 100)
    cuda_decimal = 8.7 + 0.081 * N
    metal_decimal = 17.6 + 0.064 * N
    cuda_n, cuda_y = np.array([100, 1500]), np.array([16.8, 130.1])
    metal_n, metal_y = np.array([100, 400, 837]), np.array([24.0, 43.7, 71.0])

    fig, ax = plt.subplots(figsize=(4.8, 3.2), dpi=300)
    ax.plot(N, cuda_decimal, label="CUDA fit to observations", color="#2ca02c", linestyle="--")
    ax.plot(N, metal_decimal, label="Metal fit to observations", color="#ff7f0e", linestyle="--")
    ax.scatter(cuda_n, cuda_y, label="CUDA observed p50", color="#2ca02c", zorder=5)
    ax.scatter(metal_n, metal_y, label="Metal observed p50", color="#ff7f0e", zorder=5)

    ax.set_xlabel("Concepts Retaining Embeddings $N$")
    ax.set_ylabel("End-to-End Recall Latency p50 (ms)")
    ax.set_ylim(0, 160)
    ax.legend(loc="upper left")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig2_latency.pdf")
    plt.savefig(out_path)
    plt.savefig(out_path.replace(".pdf", ".png"), dpi=300)
    plt.close()
    print(f"Generated {out_path}")

def generate_fig3_dedup():
    fig, ax = plt.subplots(figsize=(5.2, 3.2), dpi=300)

    # Categories for both rigs
    labels = [
        "Metal: Swarm Window\n(Synchronized J1-J3)",
        "Metal: Single-Agent\n(Sequential post-J3)",
        "Metal: Whole Period\n(Aggregate)",
        "CUDA: Swarm-Named\n(Concurrent tasks)",
        "CUDA: Non-Swarm\n(Concurrent mixed)",
        "CUDA: Whole Period\n(Aggregate)"
    ]
    # Rates come from the stamped datasets so the figure cannot drift from the
    # tables. Order matches `labels` above.
    with open(os.path.join(DATA_DIR, "metal_telemetry.json"), "r", encoding="utf-8") as f:
        metal = json.load(f)["deduplication"]["temporal_regimes"]
    with open(os.path.join(DATA_DIR, "cuda_telemetry.json"), "r", encoding="utf-8") as f:
        cuda = json.load(f)["deduplication"]
    rates = [
        metal["review_swarm_window"]["match_rate_pct"],
        metal["single_agent_window"]["match_rate_pct"],
        metal["whole_period"]["match_rate_pct"],
        cuda["swarm_named"]["match_rate_pct"],
        cuda["non_swarm_named"]["match_rate_pct"],
        cuda["whole_rig"]["match_rate_pct"],
    ]
    colors = ["#9467bd", "#c5b0d5", "#7f7f7f", "#1f77b4", "#aec7e8", "#333333"]

    bars = ax.bar(range(len(rates)), rates, color=colors, width=0.6, edgecolor="black", linewidth=0.8)

    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.annotate(f"{rate:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_ylabel("Write-Time Deduplication Rate (%)")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8.5)
    ax.set_ylim(0, 15)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig3_dedup_regimes.pdf")
    plt.savefig(out_path)
    plt.savefig(out_path.replace(".pdf", ".png"), dpi=300)
    plt.close()
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_fig0_architecture()
    generate_fig1_dispersion()
    generate_fig2_latency()
    generate_fig3_dedup()
    public_dir = os.path.join(OUTPUT_DIR, "..", "site", "public")
    os.makedirs(public_dir, exist_ok=True)
    for stem in ("fig0_architecture", "fig1_dispersion", "fig2_latency", "fig3_dedup_regimes"):
        for extension in ("pdf", "png"):
            name = f"{stem}.{extension}"
            shutil.copy2(os.path.join(OUTPUT_DIR, name), os.path.join(public_dir, name))
