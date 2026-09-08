# Frozen memory comparison

Mode: as-deployed. Reader: claude. Model: claude-sonnet-5.

Scores are manual rubric judgments; inspect their evidence and rationale.

| Question | Repeat | File | Lambo | Lambo − file |
|---|---:|---:|---:|---:|
| dogfood-topology | 1 | 1 | 0 | -1 |
| dogfood-topology | 2 | 1 | 0 | -1 |
| embedder-superseded | 1 | 1 | 0 | -1 |
| embedder-superseded | 2 | 1 | 0 | -1 |
| record-action-embedding | 1 | 0 | 0 | +0 |
| record-action-embedding | 2 | 0 | 0 | +0 |
| model-roles | 1 | 1 | 0 | -1 |
| model-roles | 2 | 1 | 0 | -1 |
| throttle-interval-why | 1 | 0 | 0 | +0 |
| throttle-interval-why | 2 | 0 | 0 | +0 |
| missing-cloud-cost | 1 | 1 | 1 | +0 |
| missing-cloud-cost | 2 | 1 | 1 | +0 |

File: 8/12; Lambo: 2/12.
Reader failures: file=0, lambo=0.

Repeated answers are not independent questions. Reader wall time includes CLI startup and network; it is not retrieval latency.
This is a replay of exported contexts, not an end-to-end native memory benchmark. Canonization is outside scope.
