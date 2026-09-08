# Layered efficacy readout from the two 2026-09-07 runs (private)

Inputs: lambo-2026-09-07 and vimanam-2026-09-07 (as-deployed, reader claude-sonnet-5, blind Opus grader), plus top_k=20 recalls of all 12 questions against the same 990-concept store copy (hitk-2026-09-07/). Answer-bearing concept labels are in the script output recorded below; two labels are partial (dogfood-topology needs two concepts; embedder-superseded has no record of the 2026-08-23 cutover in the store).

Layer 1, retrieval (no LLM). Of 12 questions, 7 have answer-bearing concepts in the store, 3 do not (throttle rationale, packaging, brand: the last two predate the store), 2 are absent by design. Over the 7 answerable: covered@1 2/7, @2 4/7, @3 4/7, @5 4/7, @10 4/7, @20 6/7. First answer-bearing rank: 1,1,2,2,3,7,>20. The rendered context handed to readers held 2 to 3 hits, so the readers effectively saw covered@2-3 = 4/7. Two failures are ranking, not coverage: embedder-superseded (rank 3 for the candle half, K-decision at >5) and model-roles (>20).

Layer 2, reader given coverage. Lambo arm: correct 6/8 when the rendered context covered the rubric, 0/6 when it did not. The two covered misses are the record-action answers that repeated a stale 2026-08-20 hypothesis alongside the correct mechanism.

Layer 3, staleness. Lambo arm, lambo run: 2/12 presented superseded facts as current (embedder), 2/12 repeated a stale hypothesis; vimanam run 0/12. File arm 0/24.

Layer 4, hallucination and abstention. 0/48 answers invented a fact. Abstentions were the failure mode everywhere else.

Layer 5, efficiency. Evidence tokens per correct answer: vimanam file 2,467 vs Lambo 477; lambo run file 4,542 vs Lambo 2,058. Full prompt tokens per correct answer: vimanam 4,334 vs 2,994; lambo run 6,628 vs 12,270. Recall p50 86-94 ms server-side at 990 concepts.

Controls not run: matched-corpus (ingest the notes into a fresh Lambo session) and equal-budget (cap the file arm at Lambo's byte budget). Both need new reader runs.
