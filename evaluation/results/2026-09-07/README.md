# Paired memory comparison, 2026-09-07

Two frozen-context comparisons of Claude Code file memory against Lambo recall,
run on 2026-09-07 with the harness in `scripts/compare_memory.py`. This
directory is the published copy of the private run directories. Sensitive data
unrelated to the study was removed before publication. See `REDACTIONS.md`.

These are preliminary results. Two runs on one machine support no significance
claim.

## The two runs

Both runs use the same protocol. Six questions per run, two repeats each, so 12
graded answers per arm and 24 per run. Questions and rubrics were fixed from
primary sources (GitHub branch protection, pull requests, issues, commits,
config files) before any export was read or any answer produced. One question
per knowledge type: policy with rationale, incident cause and fix, design
decision, superseded alternative, cross-document rationale, and one question
whose answer is absent from both corpora, where the only correct response is an
explicit abstention.

Mode is `as-deployed`. Each arm is handed the context its deployed mechanism
actually produces, not a matched corpus. The file arm receives the whole Claude
auto-memory directory for the project. The Lambo arm receives the rendered
`lambo_recall` text result, which is what a text-only MCP client sees.

- `lambo-2026-09-07/` uses the nrynss/lambo project. File corpus: five curated
  notes plus an index, 12,113 bytes. Lambo corpus: the lambo-dev dogfood store.
- `vimanam-2026-09-07/` uses the noemaforge/vimanam project. File corpus: five
  notes plus an index, 8,222 bytes. Lambo corpus: the same store.

The Lambo arm was served from an isolated SQLite copy of the lambo-dev store
taken at 2026-09-07T07:03Z, holding 990 concepts, on `lambo-e11fb06` over HTTP
on port 7701 with candle BGE-M3 at 1024 dimensions on Metal. The live store and
its ledger were not touched.

Reader: Claude Code CLI 2.1.241 `--print`, model `claude-sonnet-5` at effort
medium, no tools, no MCP, skills disabled, fixed system prompt, fresh temporary
working directory. All 48 reader calls returned `ok`.

## Headline scores

| Run | File arm | Lambo arm |
|---|---:|---:|
| lambo project | 8/12 | 2/12 |
| vimanam project | 10/12 | 8/12 |

The grader recorded alternative strict readings of three rubric clauses. Under
those readings the vimanam run is file 9/12 and Lambo 6/12. The judgement calls
are itemised in each run's `grader/GRADER.md`.

Per question, vimanam run, file versus Lambo:

| Question | File | Lambo |
|---|---:|---:|
| merge-workflow | 2/2 | 2/2 |
| ci-clippy-failure | 2/2 | 2/2 |
| diff-design | 0/2 | 2/2 |
| packaging-decision | 2/2 | 0/2 |
| brand-org | 2/2 | 0/2 |
| missing-downloads (abstention) | 2/2 | 2/2 |

Each system won exactly the questions only it had ingested. Lambo won the
in-session implementation decision that never reached a curated note. File
memory won the two June 2026 decisions that predate the store entirely.

## Layered readout

`efficacy.md` separates retrieval from reading. The full readout is there. In
summary, over the seven questions that have an answer-bearing concept in the
store:

- Coverage by depth: covered@1 is 2, @2 through @10 is 4, and @20 is 6. First
  answer-bearing ranks are 1, 1, 2, 2, 3, 7, and beyond 20.
- The rendered context handed to readers held two or three hits, so readers
  effectively saw the @2 to @3 figure of four.
- Reader given coverage: correct on 6 of 8 answers where the rendered context
  covered the rubric, and 0 of 6 where it did not.
- Staleness: in the lambo run's Lambo arm, 2 of 12 answers presented superseded
  facts as current and 2 of 12 repeated a stale hypothesis. Zero elsewhere,
  including all 24 file-arm answers.
- Hallucination: 0 of 48 answers invented a fact. Abstention was the failure
  mode everywhere else.
- Efficiency, evidence tokens per correct answer: vimanam run 2,467 for file
  against 477 for Lambo, lambo run 4,542 against 2,058.
- Server-side recall p50 was 86 to 94 ms at 990 concepts.

`hitk/` holds `top_k=20` ranked hits for all 12 questions against the same
store copy. It is what the coverage-by-depth figures are computed from.

## Grader provenance

Grading was done by a separate Claude Opus 5 agent after all reader answers
existed. It received only shuffled opaque answer identifiers with no arm key
and a `reference.md` of primary-source facts, and was told to read nothing
else. Rules were integer 0 or 1 per rubric, whole rubric or nothing, explicit
abstention only on the abstention question, abstention scores 0 elsewhere, and
a correct answer that also asserts something the reference contradicts scores
0. Grades were not altered after unblinding. Each run's `grader/GRADER.md`
records the provenance and the judgement calls. The blinding is imperfect:
bracketed filenames in one arm and `[Type] (score N)` blocks in the other could
reveal the source to an attentive grader.

## Caveats

These come from each run's `run-1/analysis.md` and bound what the scores mean.

1. Context-budget asymmetry. The file arm received the whole memory directory
   for every question, 8,222 or 12,113 bytes. The Lambo arm received the
   rendered recall text only, 1,154 to 1,533 bytes, containing two or three of
   five or six hits. As deployed a Claude Code client also receives the
   structured hits, so this export understates what an agent sees.
2. Coverage against retrieval. In as-deployed mode this compares the deployed
   memories, not the retrieval algorithms. Two of six vimanam questions ask
   about decisions older than the store, which caps Lambo at 8/12 by
   construction. The lambo run's file corpus is a hand-curated operator summary
   written for exactly these kinds of questions.
3. Shared-session noise. The lambo-dev session holds every project on the
   machine, so recall surfaced concepts from unrelated projects, redacted as
   sensitive data. That is why this directory needed redaction.
4. Hook confound. A user-scope SessionStart hook injected a short lambo-dogfood
   protocol reminder into every reader process, identically in both arms.
5. Model grader, not a human, with the judgement calls noted above.
6. No significance. Repeats are not independent questions, six questions per
   run cannot support a significance claim, and this is one replay on one
   machine.

Controls not run: a matched-corpus run that ingests the same notes into a fresh
Lambo session, and an equal-budget run that caps the file arm at the Lambo byte
budget. Both need new reader runs.

## Layout

Per run:

- `suite.json`: questions, rubrics, and context references.
- `exports/file/all.md`: the file-memory export handed to the file arm.
- `exports/lambo/*.txt`: the rendered recall context per question.
- `exports/lambo/*.full.json`: the same recalls with hits, node ids, and scores.
- `exports/lambo/calls.jsonl`: the isolated copy's ledger, with per-hit legs.
- `bundle/`: the frozen prompt bundle and its digest.
- `run-1/`: reader results, grading, graded evidence, report, analysis, digests.
- `grader/`: grader inputs, output, and provenance.

Shared: `efficacy.md`, `hitk/`, `REDACTIONS.md`.

The snapshot of the file-memory directory is not republished. `all.md` already
contains every one of those files verbatim.
