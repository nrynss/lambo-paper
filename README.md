# Lambo: A Living Topological Memory Substrate for Multi-Agent Software Development

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22701169.svg)](https://doi.org/10.5281/zenodo.22701169)
[![Paper PDF](https://img.shields.io/badge/Paper-PDF-red.svg)](site/public/lambo-paper.pdf)
[![Web Edition](https://img.shields.io/badge/Web-Edition-blue.svg)](https://nrynss.github.io/lambo-paper/)
[![Lambo Core](https://img.shields.io/badge/Lambo-Core_Engine-green.svg)](https://github.com/nrynss/lambo)

This repository contains a systems experience report, frozen multi-rig telemetry datasets, figure generation pipelines, and the interactive web edition for **Lambo**, a local graph-memory daemon for multi-agent software engineering.

---

## Abstract

Autonomous coding agents operate within ephemeral process lifecycles. When agents complete execution, their intermediate reasoning and architectural context vanish. Similarity retrieval alone does not explicitly encode dependency or invalidation relationships. We present Lambo, an in-memory topological memory daemon for multi-agent software engineering. Lambo models development state as a directed typed graph with an earned canonization lifecycle. Concurrent agents submit asynchronous writes through per-agent lanes with individual receipt states. Context retrieval uses three-leg hybrid candidate scoring and prioritized breadth-first topological expansion. Phase one merges lexical, recency, and dense vector signals. Phase two traverses structural dependency edges while respecting invalidation semantics. Phase three enforces canonical-first ranking and hot-list conflict preservation under token budgets. We report operational telemetry from two production rigs using nominal 5-minute health sampling. The extract contains 2,495 CUDA and 3,429 Metal heartbeat snapshots. At the nominal interval, those counts correspond to 8.7 and 11.9 interval-equivalent days within 12.7 and 16.0 day windows. Deduplication rates reached 12.0% during synchronized review swarms on Metal (against 0.8% in single-agent sessions) and 4.3% among swarm-named agents on CUDA (against 1.7% in non-swarm streams, 2.2% aggregate). The tracked infrastructure counters were zero in this extract, which does not establish zero failures or data loss. CUDA inspect misses were 22 of 82, while Metal had one miss in four calls and is too small for a cross-rig rate comparison. No concepts reached Canonical status, and the observed Metal store had no concepts eligible for the first promotion gate. A preliminary paired comparison against Claude Code file memory scored 10/12 for file memory against 8/12 for Lambo on one corpus, and 8/12 against 2/12 on a second. We discuss citation dilution as a separate hypothesis and identify controlled retrieval evaluation as future work.

---

## Repository Structure

```text
lambo-paper/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions workflow (compiles PDF & deploys site)
├── arxiv/                      # arXiv v1 submission bundle and upload checklist
│   ├── README.md               # Category, endorsement, cutoff, licence, .bbl checklist
│   ├── abstract.txt            # Plain-text abstract for the submission form
│   └── lambo-paper-arxiv-v1.tar.gz
├── data/
│   ├── cuda_telemetry.json     # Stamped extract from live production dogfooding logs
│   └── metal_telemetry.json    # Stamped replay of the Metal rig ledger and store
├── evaluation/
│   ├── README.md               # Paired file-memory versus Lambo protocol
│   ├── example/                # Synthetic suite that exercises the harness
│   └── results/2026-09-07/     # First two graded runs: suites, bundles, answers,
│                               # grades, grader provenance, hit@k, REDACTIONS.md
├── scripts/
│   ├── compare_memory.py       # Frozen-context comparison harness
│   ├── extract_telemetry.py    # Replays rig ledgers and stores into stamped JSON datasets
│   ├── plot_figures.py         # Reproduces vector PDF and web PNG figures
│   └── verify_constraints.py   # Linter auditing zero em dashes, zero semicolons, sentence limits
├── site/                       # Astro + Starlight web edition
│   ├── astro.config.mjs        # Starlight configuration with KaTeX and Mermaid
│   ├── package.json
│   ├── public/                 # Built PDF and image assets
│   └── src/content/docs/       # Markdown paper chapters and interactive artifacts
├── src/                        # LaTeX manuscript source
│   ├── main.tex                # Full LaTeX paper
│   ├── references.bib          # 15 bibliography entries
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

For a new paired Claude file-memory versus Lambo comparison, see the
[evaluation protocol and commands](evaluation/README.md). The harness replays frozen
context exports and preserves answers for blinded grading. In Claude Code, use
`/compare-memory` to follow the [repository skill](.claude/skills/compare-memory/SKILL.md).
The included synthetic example checks the harness; it adds no empirical results
to the paper.

The first two graded runs are published under
[`evaluation/results/2026-09-07/`](evaluation/results/2026-09-07/README.md):
file memory 8/12 against Lambo 2/12 on the lambo project, and file memory 10/12
against Lambo 8/12 on the vimanam project. That directory holds both suites, both
frozen bundles, all 48 reader answers with grades and grader provenance, `top_k=20`
recalls for every question, and a `REDACTIONS.md` recording what was removed
before publication. These are two runs on one machine and support no significance
claim.

### 1. Extract Stamped Telemetry
The default invocation emits the frozen benchmark datasets in `data/`:
```bash
python3 scripts/extract_telemetry.py
```

Each frozen dataset is a live replay cut at a fixed stamp (CUDA `2026-09-04T19:57:05.677853Z`, Metal `2026-09-04T19:16:00Z`). On a rig that holds the ledger and store, the replay reproduces the frozen file byte for byte:
```bash
python3 scripts/extract_telemetry.py --live --rig metal --until 2026-09-04T19:16:00Z
```

Drop `--until` to extract the current state of a rig, or `--rig` to replay both. Source paths default to the dogfood locations and can be overridden with `LAMBO_CALLS_PATH` / `LAMBO_DB_PATH` (CUDA) and `LAMBO_METAL_CALLS_PATH` / `LAMBO_METAL_DB_PATH` (Metal).

### 2. Generate Vector Figures
```bash
python3 scripts/plot_figures.py
```

### 3. Verify Writing Constraints
Audits writing and cross-file telemetry constraints:
```bash
python3 scripts/verify_constraints.py
```

### 4. Run Harness Tests
Checks the comparison harness for experimental integrity; no model or network calls:
```bash
make test
# or directly:
python3 -m unittest discover -s tests -p 'test_compare_memory.py'
```

### 5. Compile Manuscript PDF
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

### 6. Build Web Edition
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
