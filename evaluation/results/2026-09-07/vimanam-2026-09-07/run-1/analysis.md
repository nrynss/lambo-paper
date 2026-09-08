# Analysis: file memory vs Lambo, vimanam project, 2026-09-07 (run-1)

Result: file 10/12, Lambo 8/12 (six questions, two repeats, reader claude-sonnet-5 at effort medium, 24/24 calls ok, blind Opus grader). Under the grader's stricter alternative readings: file 9/12, Lambo 6/12. One replay on one corpus; no statistical claim.

Why vimanam: both memories were written in the same week (notes modified 2026-09-04/05, 11 store concepts created 2026-09-04/05), the repo is public under the operator's noemaforge org, and the earlier lambo-project run was confounded by stale notes.

## Per question
- merge-workflow: 2/2 both. Both memories recorded the 2026-09-05 merges; both readers gave the unsatisfiable-review reason and the squash + admin path.
- ci-clippy-failure: 2/2 both. Both memories recorded the toolchain-drift incident; Lambo's concept additionally carried the fix location and commit, the file note carried the prevention rule. Rubric accepted either.
- diff-design: file 0/2, Lambo 2/2. The file memory has no note about #45; both file readers abstained correctly. Lambo's top hit was the implementation record ("design option b ... src/diff.rs ... resolve $refs ... JSON-pointer paths"), and both readers reproduced the mechanism.
- packaging-decision: file 2/2, Lambo 0/2. The #32 decision dates from June 2026, before the dogfood store existed (2026-08-19), so the store cannot hold it. Recall surfaced concepts from unrelated projects, redacted as sensitive data. Both Lambo readers abstained.
- brand-org: file 2/2, Lambo 0/2. Same cause: a June decision, absent from the store; recall returned unrelated concepts and the readers abstained.
- missing-downloads: 2/2 both. Every answer abstained explicitly with no invented figure.

## Reading
Where both systems covered the same week, they tied. Each system won exactly the questions only it had ingested: Lambo the in-session implementation decision (#45) that never reached a curated note, file memory the two June decisions that predate the store. In as-deployed mode this is a coverage comparison, and the split is clean enough to say what each mechanism captures: Lambo records what agents did and decided during sessions; the auto-memory records what the operator chose to keep. No stale-decision failure occurred here, unlike the lambo-project run, because nothing in this week's history had been superseded.

## Caveats
1. Context budget asymmetry: file arm 8,222 bytes for every question; Lambo arm 1,154 to 1,429 bytes, containing 2 or 3 of 6 hits (copy ledger, included_in_context). As deployed a Claude Code client also receives the structured hits.
2. Shared session noise: the lambo-dev session holds all projects on this machine, so recall surfaced concepts from unrelated projects, redacted as sensitive data. One such hit sits in exports/lambo/packaging-decision.txt. The redaction ledger is in ../../REDACTIONS.md.
3. Temporal coverage: two of six questions ask about decisions older than the store. That is a property of the operator's history, not a retrieval failure, but it caps Lambo at 8/12 by construction.
4. Environment confound: the user-scope SessionStart hook injected the lambo-dogfood protocol reminder into every reader process, identically in both arms.
5. Grader: a model grader (Opus), with three lenient judgement calls recorded in ../grader/GRADER.md.
6. Repeats are not independent questions.

## For the paper
Usable as a documented as-deployed replay showing complementary coverage, with the stated limits. Not usable as evidence of retrieval superiority in either direction. A matched-corpus run (ingest the five vimanam notes into a fresh Lambo session, ask the same questions) would isolate retrieval from coverage, and exporting the structured hits would remove the budget asymmetry.

## Retrieval time and tokens (added after the run)
Lambo recall, server-side per call (isolated copy ledger, 990 concepts, Metal): 76, 77, 82, 86, 86, 266 ms; p50 86 ms, which matches the paper's Metal scan model (17.6 ms + 64 us x 990 = 81 ms). The 266 ms call was the first recall after the serve started (warm-up). Vector leg absent on two queries (brand-org, missing-downloads) means no candidate cleared the cosine leg, not that the embedder was down.
File arm: reading the six memory files takes 0.16 ms; as deployed, the real cost is model turns spent choosing and reading files, which this replay does not exercise.
Reader wall time is dominated by CLI startup and the model: medians 34.6 s (file) vs 33.8 s (lambo); not a retrieval measurement.
Tokens per answer (median, from the CLI usage envelope; cache_creation and cache_read report the same figure, so the prompt is counted twice in the total): prompt about 3,612 tokens (file) vs 1,996 (lambo); evidence share about 2,060 vs 320 tokens at 4 bytes per token; output 353 vs 324. Cost per answer USD 0.0196 vs 0.0123; whole run USD 0.226 vs 0.144.
