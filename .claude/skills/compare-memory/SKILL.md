---
name: compare-memory
description: Compare Claude answers using frozen file-memory and Lambo context exports, with paired prompts, preserved evidence, and blinded rubric grading for the Lambo paper.
---

# Compare memory

Use `scripts/compare_memory.py` from this repository's root. Read
`evaluation/README.md` for commands, input schema, and experimental boundaries.

1. Establish whether the comparison uses the same source corpus in both systems
   (`matched-corpus`) or their actual deployed memories (`as-deployed`). Unequal
   corpus contents confound claims about retrieval algorithms.
2. Before collecting answers, freeze the questions, reference evidence, and binary
   scoring rubrics. Include direct recall, cross-document relationships, changed
   decisions, and questions that should produce abstention. Do not reconstruct the
   paper's historical five questions from its aggregate scores.
3. Preserve memory snapshots and retrieval procedures. Export the exact file-memory
   context and exact Lambo recall response for each question, with evidence IDs.
   Capture unsuccessful/empty recalls as evidence too. Do not select only favorable
   outputs or rewrite exports to improve an answer. Use an isolated Lambo copy for
   experiments: recall may update state. Do not alter the live dogfood store.
4. Build a suite using the example schema. Record source hashes, snapshot time,
   engine revision/configuration, query parameters, file-selection procedure, and
   retrieval timing separately from reader timing in provenance. Freeze the suite
   before reading model answers. Apply the same declared context budget to both
   arms. The harness cap is UTF-8 bytes, not tokens.
5. Prepare the bundle and run the same pinned Claude model and effort for both
   arms. Each answer uses a fresh process without retrieval tools. Inspect the
   local CLI/environment for additional memory or hook injection and record it;
   retain organization-required controls. If uncontrolled context is injected,
   label the run confounded instead of claiming isolation.
6. Give an independent grader only `grading.json` and the frozen reference evidence,
   not the arm key or either competing output history. Score each answer against
   its predeclared rubric, with a rationale. Use zero for execution failures.
   Arm names are hidden, but content can reveal the source; disclose that limit.
7. Generate the paired report. Discuss individual successes, failures, abstentions,
   and corpus differences. Keep smoke-test results separate from empirical results.
   Do not treat repeated outputs as independent questions or claim statistical
   superiority from a handful of examples.

This skill supports a new reproducible comparison, not a reconstruction of the
historical 3/5 versus 4/5 anecdote. Frozen-context replay does not measure Claude's
native memory-file discovery or end-to-end Lambo retrieval. Canonization is deferred.
Run artifacts may contain private memories; review them before publication.
