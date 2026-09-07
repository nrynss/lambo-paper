# File memory versus Lambo

This harness replays frozen memory exports through the same Claude reader. It
preserves exact inputs, outputs, errors, context hashes, model command/version,
and manual grading evidence. It does not yet automate memory ingestion or live
retrieval. It cannot reconstruct the paper's historical five-query anecdote.
Canonization is deferred.

Requires Python 3.10+ (standard library only). Real model runs also require an
authenticated Claude Code CLI supporting the flags shown by `run --help` and the
script's recorded command. No package installation is necessary.

## Try the offline example

From the repository root:

```bash
python3 scripts/compare_memory.py prepare evaluation/example/suite.json --out evaluation/runs/demo-bundle
python3 scripts/compare_memory.py run evaluation/runs/demo-bundle --reader smoke --out evaluation/runs/demo-run
```

The smoke reader always abstains and makes no network/model calls. The example
contains invented data and deliberately identical contexts. It demonstrates the
workflow, not evidence favoring either system. Output folders must be new; existing
artifacts are never overwritten by prepare/run/report. If interrupted, retain the
partial run and start another output folder. There are no automatic retries.

## Freeze a real comparison

Copy the example suite into a private experiment directory. Paths are relative to
the suite JSON. Each question has an ID, question, rubric, and two context exports:

```json
{
  "mode": "as-deployed",
  "provenance": "Describe source snapshots, their hashes, collection date and question selection here.",
  "questions": [{
    "id": "q1",
    "question": "What decision was made and why?",
    "rubric": "State the accepted decision and its rationale, cite reference evidence; otherwise score 0.",
    "contexts": {
      "file": {"path": "file/q1.txt", "provenance": "Record file corpus hash and exact selection procedure."},
      "lambo": {"path": "lambo/q1.txt", "provenance": "Record store hash, engine revision, config and exact recall arguments."}
    }
  }]
}
```

Use `matched-corpus` only when both systems received the same underlying source
information. Use `as-deployed` for actual independent memories, where coverage and
selection both influence outcomes. Save original snapshots alongside the exports;
hashes of exported text alone cannot reproduce retrieval. Preserve failed recalls
as empty context exports and describe their failure in provenance.

Declare questions, reference sources, rubrics, selection rules, retrieval limits,
and repeat count before collecting answers. Do not let the answer-generating
process see the rubric or reference answers. Preserve evidence identifiers in each
context. Include questions about missing information and superseded decisions.
Choose a representative set, rather than questions selected because Lambo wins.

`prepare` rejects contexts over the common UTF-8 byte limit rather than silently
cutting evidence. This limit is not a token-equivalent budget; token counts and
retrieval time must be measured and recorded separately if used in a paper claim.
The default is 24,000 bytes per export and two reader repetitions per question.
Arm order is seeded and alternates across repetitions, balanced for even counts.

```bash
python3 scripts/compare_memory.py prepare /path/to/experiment/suite.json --out evaluation/runs/real-bundle --seed 17 --repeats 2
python3 scripts/compare_memory.py run evaluation/runs/real-bundle --reader claude --model YOUR_PINNED_MODEL_ID --environment-note 'Describe user/admin hooks, memory injection, provider and relevant settings' --out evaluation/runs/real-run
```

Replace `YOUR_PINNED_MODEL_ID` with an available immutable model ID. A moving alias
does not provide a stable model pin. Real runs use your Claude authentication and
incur normal model usage. They inherit environment and policy settings, so the
environment note is required. The harness does not disable security hooks. It
requests no built-in tools or MCP servers, disables skills, supplies a fixed
system prompt, and starts each answer in a fresh temporary working directory.
These controls do not guarantee absence of injected user/admin context. Audit
the environment and disclose any contamination before making controlled claims.
`stdout` retains the Claude JSON envelope, including usage/model metadata when
the CLI supplies it. The timeout includes CLI startup and model response time.

## Grade and inspect differences

The run contains:

- `bundle.json`: frozen questions, rubrics, contexts, and arm key. Keep from graders.
- `run.json`: command, CLI version, environment note, bundle hash, and settings.
- `results.json`: exact prompts, raw stdout/stderr, answers, errors, and reader times.
- `grading.json`: shuffled opaque answer IDs, questions, rubrics, answers, and blank scores.

Give the grader only `grading.json` plus the frozen reference evidence. For every
answer, replace `score: null` with integer `0` or `1` and add a nonempty `rationale`.
Use 1 only if the answer meets the entire predeclared rubric. Failed calls must
score 0. Do not edit answer text or identifiers. Independent human review is
preferable; record a model grader's version/prompt if one is used. Blinding hides
arm labels, but distinctive content may still reveal the memory source.

```bash
python3 scripts/compare_memory.py report evaluation/runs/real-run --grades evaluation/runs/real-run/grading.json
python3 -m unittest discover -s tests -p 'test_compare_memory.py'
```

`report.md` includes per-question paired scores, totals, and failure counts.
`grading.json` retains the rationale for each difference. Incomplete runs and
incomplete grading are rejected. Inspect raw outputs and references when explaining
why an arm succeeded. Repeated reader outputs are not independent questions.
No significance claim or retrieval-latency comparison is generated automatically.
Frozen inputs improve repeatability; stochastic model outputs need not match byte
for byte. Keep the original run as evidence.

Private run directories under `evaluation/runs/` are ignored by Git. Publish only
reviewed, appropriately shareable snapshots, exports, protocol, and results. Until
real runs are collected and graded, the paper's efficacy evidence remains unchanged.
