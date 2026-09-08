# Frozen memory comparison

Mode: as-deployed. Reader: claude. Model: claude-sonnet-5.

Scores are manual rubric judgments; inspect their evidence and rationale.

| Question | Repeat | File | Lambo | Lambo − file |
|---|---:|---:|---:|---:|
| merge-workflow | 1 | 1 | 1 | +0 |
| merge-workflow | 2 | 1 | 1 | +0 |
| ci-clippy-failure | 1 | 1 | 1 | +0 |
| ci-clippy-failure | 2 | 1 | 1 | +0 |
| diff-design | 1 | 0 | 1 | +1 |
| diff-design | 2 | 0 | 1 | +1 |
| packaging-decision | 1 | 1 | 0 | -1 |
| packaging-decision | 2 | 1 | 0 | -1 |
| brand-org | 1 | 1 | 0 | -1 |
| brand-org | 2 | 1 | 0 | -1 |
| missing-downloads | 1 | 1 | 1 | +0 |
| missing-downloads | 2 | 1 | 1 | +0 |

File: 10/12; Lambo: 8/12.
Reader failures: file=0, lambo=0.

Repeated answers are not independent questions. Reader wall time includes CLI startup and network; it is not retrieval latency.
This is a replay of exported contexts, not an end-to-end native memory benchmark. Canonization is outside scope.
