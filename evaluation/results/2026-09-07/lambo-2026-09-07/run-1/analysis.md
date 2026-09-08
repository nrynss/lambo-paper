# Analysis: file memory vs Lambo, lambo project, 2026-09-07 (run-1)

Result: file 8/12, Lambo 2/12 (six questions, two repeats, reader claude-sonnet-5 at effort medium, 24/24 calls ok, blind Opus grader). This is one as-deployed replay on one corpus and says nothing statistical.

## Per question
- dogfood-topology: file 2/2, Lambo 0/2. The file note states the launchd HTTP writer and the connect-by-URL rule in one bullet. Lambo's rendered context carried the client-wiring concept (URL, no spawn) but not the launchd half; the reader abstained on deployment.
- embedder-superseded: file 2/2, Lambo 0/2. The file note says candle on Metal and "No llama-server needed since 2026-08-23". Lambo's top hits were 2026-08-20 and 2026-08-22 concepts about the live llama.cpp BGE-M3 embedder; no K2-migration concept ranked, and the store has no invalidation edge or canonical marker on the old concepts (canonization_status None for all 990). The reader presented the superseded embedder as current in both repeats. This is the superseded-information failure the paper discusses, observed directly.
- record-action-embedding: 0/2 both. File memory only records the repair (42 backfilled), not the mechanism. Lambo's context had the mechanism ("record_action concepts previously stored embedding NULL, everything an agent DID was invisible to semantic recall") but also the 2026-08-20 pre-diagnosis finding; the reader repeated both and the grader failed it for asserting a contradicted claim. Faithful to stale evidence, penalized by the rubric.
- model-roles: file 2/2, Lambo 0/2. The directive lives in a file note. The store has no concept stating it (a search for remediation + Opus finds only a review-cycle record), so this is a coverage gap, not a retrieval miss.
- throttle-interval-why: 0/2 both. Neither corpus holds the plist rationale (store: zero concepts mention ThrottleInterval). Correct abstentions in all four answers, scored 0 by design because the rubric demands the fact.
- missing-cloud-cost: 2/2 both. Every answer abstained explicitly with no invented figure.

## Caveats that bound the reading
1. Context budget asymmetry: the file arm received the whole 12,113-byte memory directory for every question; the Lambo arm received the rendered recall context only (1,303 to 1,533 bytes), which included 2 of 5 hits for five questions and 3 of 5 for one (copy ledger, included_in_context). As deployed, a Claude Code client also receives the structured hits, so this export understates what an agent sees.
2. Corpus difference: the file memory is a hand-curated operator summary (5 notes) written for exactly these kinds of questions; the Lambo store is 990 machine-written concepts from development sessions. as-deployed mode measures the deployed memories, not the retrieval algorithm.
3. No canonization ran (canonical_count 0), so Lambo's superseded/current distinction had no signal to work with.
4. Environment confound: the user-scope SessionStart hook injected the lambo-dogfood protocol reminder into every reader process, identically in both arms.
5. Grader: a model grader (Opus), not a human; prompt and judgement call recorded in ../grader/GRADER.md.
6. Repeats are not independent questions; six questions cannot support a significance claim.

## What this suggests for the paper
Do not use these scores as efficacy evidence for Lambo. They are useful as a documented reproduction of two mechanisms the paper argues about: retrieval without supersession signals surfaces stale decisions as current, and rendered-context budgets decide what a reader can cite. A matched-corpus run (same source notes ingested into both systems) and an export that includes the structured hits would isolate retrieval from coverage.

## Retrieval time and tokens (added after the run)
Lambo recall, server-side per call (isolated copy ledger, 990 concepts, Metal): 88, 89, 93, 94, 98, 158 ms for the six exports (p50 94 ms); a warm-up test recall before them took 3,157 ms (model load). Paper model at 990 concepts: 81 ms.
File arm: reading the six files takes 0.16 ms; the deployed cost is model turns, not exercised here.
Reader wall time medians 33.9 s (file) vs 33.4 s (lambo), dominated by CLI startup and the model.
Tokens per answer (median; cache_creation equals cache_read, so totals double-count the prompt): prompt about 4,419 (file) vs 2,045 (lambo); evidence share about 3,030 vs 340 tokens; output 290 vs 284. Cost per answer USD 0.0234 vs 0.0129; whole run USD 0.270 vs 0.148.
