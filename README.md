# Lambo: A Living Topological Memory Substrate for Multi-Agent Software Development

[![Paper PDF](https://img.shields.io/badge/Paper-PDF-red.svg)](site/public/lambo-paper.pdf)
[![Web Edition](https://img.shields.io/badge/Web-Edition-blue.svg)](https://nrynss.github.io/lambo-paper/)
[![Lambo Core](https://img.shields.io/badge/Lambo-Core_Engine-green.svg)](https://github.com/nrynss/lambo)

This repository contains the formal research paper, reproducible multi-rig telemetry datasets, figure generation pipelines, and the interactive web edition for **Lambo**, an in-memory topological memory daemon for multi-agent software engineering swarms.

---

## Abstract

Autonomous coding agents operate within ephemeral process lifecycles. When agents complete execution, their intermediate reasoning and architectural context vanish. Standard vector stores suffer from semantic drift and lack topological dependency awareness.

We present **Lambo**, an in-memory topological memory daemon for multi-agent software engineering. Lambo models development state as a directed typed graph with an earned canonization lifecycle. Concurrent agents coordinate through an asynchronous write queue with monotonic receipts. Context retrieval uses three-leg hybrid candidate scoring and prioritized breadth-first topological expansion:
1. **Phase 1:** Max-merges lexical (BM25), recency, and dense vector signals (BGE-M3 1024-dim).
2. **Phase 2:** Traverses structural dependency edges while respecting invalidation semantics.
3. **Phase 3:** Enforces canonical-first ranking and hot-list conflict preservation under token budgets.

We evaluate Lambo using continuous 5-minute health sampling (2,486 heartbeat snapshots) over a 12-day live production deployment. Deduplication rates reached 12.0% during synchronized review swarms on Metal (against 0.9% in single-agent sessions) and 4.3% among swarm-named agents on CUDA (against 1.7% in non-swarm streams, 2.2% aggregate). Zero infrastructure-level faults occurred across all checkpoints. Tool-level execution misses (25% to 28% on inspect) revealed a text-surface affordance gap that motivates rendering explicit node identifiers. Finally, we formulate the multi-repository dispersion effect to explain why consensus promotion requires namespace scoping, and characterize hardware-specific memory paging overheads on unified memory platforms.

---

## Repository Structure

```text
lambo-paper/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions workflow (compiles PDF & deploys site)
├── data/
│   ├── cuda_telemetry.json     # Stamped extract from live production dogfooding logs
│   └── metal_telemetry.json    # Stamped extract from signed Apple Silicon reviews
├── scripts/
│   ├── extract_telemetry.py    # Reads live rig logs and writes stamped JSON datasets
│   ├── plot_figures.py         # Reproduces vector PDF and web PNG figures
│   └── verify_constraints.py   # Linter auditing zero em dashes, zero semicolons, sentence limits
├── site/                       # Astro + Starlight web edition
│   ├── astro.config.mjs        # Starlight configuration with KaTeX and Mermaid
│   ├── package.json
│   ├── public/                 # Built PDF and image assets
│   └── src/content/docs/       # Markdown paper chapters and interactive artifacts
├── src/                        # LaTeX manuscript source
│   ├── main.tex                # Full LaTeX paper
│   ├── references.bib          # 15 peer-reviewed citations
│   ├── fig0_architecture.pdf   # Architectural diagram
│   ├── fig1_dispersion.pdf     # Dispersion effect plot
│   ├── fig2_latency.pdf        # Vector scan latency plot
│   ├── fig3_dedup_regimes.pdf  # Multi-rig deduplication bar chart
│   └── main.pdf                # Compiled manuscript
├── Makefile                    # One-command build automation
└── README.md
```

---

## Reproduction and Building

### 1. Extract Stamped Telemetry
```bash
python3 scripts/extract_telemetry.py
```

### 2. Generate Vector Figures
```bash
python3 scripts/plot_figures.py
```

### 3. Verify Writing Constraints
Audits strict academic criteria: zero semicolons, zero em dashes, sentences $\le 30$ words, and exactly 15 peer-reviewed citations:
```bash
python3 scripts/verify_constraints.py
```

### 4. Compile Manuscript PDF
Using [Tectonic](https://tectonic-typesetting.github.io/):
```bash
make pdf
# or directly:
cd src && tectonic main.tex
```

If `tectonic` is not on your PATH, install the same pinned build CI uses. It is
downloaded from the upstream release, checked against a recorded sha256, and
placed in `~/.local/bin`:
```bash
make tectonic
```
To use a copy you already have, pass its path: `make pdf TECTONIC=/path/to/tectonic`.

### 5. Build Web Edition
```bash
cd site
npm install
npm run build
```

---

## Citation

```bibtex
@article{narayan2026lambo,
  title={Lambo: A Living Topological Memory Substrate for Multi-Agent Software Development},
  author={Narayan SS},
  journal={arXiv preprint},
  year={2026}
}
```
