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
import matplotlib.pyplot as plt
import numpy as np

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
    k_repo = 3.0
    delta_r = 1.0 / (1.0 + np.exp(0.45 * (R - k_repo)))
    tau_sync = 12.0 + 8.5 * np.log2(R)

    fig, ax1 = plt.subplots(figsize=(4.8, 3.2), dpi=300)

    color = "#1f77b4"
    ax1.set_xlabel("Track Count $R$ Across Repositories")
    ax1.set_ylabel("Cross-Repository Citation Density $\\delta_r$", color=color)
    line1 = ax1.plot(R, delta_r, color=color, marker="o", label="Citation Density $\\delta_r$")
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.set_ylim(-0.05, 1.05)

    ax2 = ax1.twinx()
    color = "#d62728"
    ax2.set_ylabel("Barrier Synchronization $\\tau_{\\mathrm{sync}}$ (ms)", color=color)
    line2 = ax2.plot(R, tau_sync, color=color, marker="s", linestyle="--", label="Barrier Sync $\\tau_{\\mathrm{sync}}$")
    ax2.tick_params(axis="y", labelcolor=color)
    ax2.set_ylim(0, 50)
    ax2.grid(False)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="center right")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig1_dispersion.pdf")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated {out_path}")

def generate_fig2_latency():
    # Number of concepts
    N = np.linspace(100, 5000, 100)
    
    # Measured Decimal ASCII Scan Latency from Issue #8:
    # CUDA: 8.7 ms fixed + 0.081 ms per concept
    # Metal: 17.6 ms fixed + 0.064 ms per concept
    cuda_decimal = 8.7 + 0.081 * N
    metal_decimal = 17.6 + 0.064 * N
    
    # Analytical projection for packed binary BLOB (no decimal parsing):
    # Fixed overhead ~8.7 ms (query embed + CUDA overhead) + ~0.003 ms per concept (pure f32 memcpy/SIMD)
    # Projected latency at 1500 concepts is ~13-25 ms
    projected_binary = 8.7 + 0.0035 * N

    fig, ax = plt.subplots(figsize=(4.8, 3.2), dpi=300)
    ax.plot(N, cuda_decimal, label="Measured CUDA (Decimal ASCII)", color="#2ca02c", linestyle="-")
    ax.plot(N, metal_decimal, label="Measured Metal (Decimal ASCII)", color="#ff7f0e", linestyle="-")
    ax.plot(N, projected_binary, label="Projected Binary BLOB (Analytical)", color="#1f77b4", linestyle=":")

    # Highlight dogfood operating point (~1,500 concepts)
    ax.scatter([1500], [8.7 + 0.081 * 1500], color="#2ca02c", zorder=5)
    ax.scatter([837], [17.6 + 0.064 * 837], color="#ff7f0e", zorder=5)
    ax.annotate("CUDA 1,500 concepts\n(130.1 ms p50)", (1500, 130.1), textcoords="offset points", xytext=(-75, 15),
                arrowprops=dict(arrowstyle="->", color="#2ca02c"))
    ax.annotate("Metal 837 concepts\n(71.0 ms p50)", (837, 71.0), textcoords="offset points", xytext=(15, -25),
                arrowprops=dict(arrowstyle="->", color="#ff7f0e"))

    ax.set_xlabel("Session Concept Count $N$")
    ax.set_ylabel("Recall Phase-1 Vector Scan Latency (ms)")
    ax.set_ylim(0, 450)
    ax.legend(loc="upper left")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig2_latency.pdf")
    plt.savefig(out_path)
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
    plt.close()
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_fig1_dispersion()
    generate_fig2_latency()
    generate_fig3_dedup()
