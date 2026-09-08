# Redactions applied to this results directory

Some recall hits, ledger snippets, reader prompts and reader answers in this
directory were redacted. The removed material is sensitive data unrelated to
this study. Nothing else was changed.

## Marker format

Each removal was replaced in place by a marker of the form
`[REDACTED: sensitive data, N bytes]`, where N is the UTF-8 byte length of the
removed text. In rendered recall contexts the trailing `[Type] (score N)`
marker is kept, so a reader can still see that a hit occupied that slot and
what it scored.

JSON files were rewritten with formatting arguments detected from the original
file, so a redacted file differs from its source only on the lines carrying a
marker.

## Per-file counts

| File | Removals | Bytes |
|---|---:|---:|
| `hitk/brand-org.json` | 7 | 776 |
| `hitk/ci-clippy-failure.json` | 13 | 1,560 |
| `hitk/diff-design.json` | 4 | 405 |
| `hitk/dogfood-topology.json` | 1 | 120 |
| `hitk/embedder-superseded.json` | 2 | 240 |
| `hitk/merge-workflow.json` | 12 | 1,440 |
| `hitk/missing-cloud-cost.json` | 4 | 480 |
| `hitk/missing-downloads.json` | 3 | 360 |
| `hitk/model-roles.json` | 3 | 360 |
| `hitk/packaging-decision.json` | 4 | 480 |
| `hitk/record-action-embedding.json` | 3 | 304 |
| `hitk/throttle-interval-why.json` | 8 | 960 |
| `lambo-2026-09-07/bundle/bundle.json` | 18 | 1,692 |
| `lambo-2026-09-07/exports/file/all.md` | 1 | 94 |
| `lambo-2026-09-07/exports/lambo/calls.jsonl` | 2 | 428 |
| `lambo-2026-09-07/exports/lambo/missing-cloud-cost.full.json` | 1 | 216 |
| `lambo-2026-09-07/exports/lambo/throttle-interval-why.full.json` | 2 | 919 |
| `lambo-2026-09-07/run-1/bundle.json` | 18 | 1,692 |
| `lambo-2026-09-07/run-1/results.json` | 12 | 1,128 |
| `vimanam-2026-09-07/bundle/bundle.json` | 12 | 3,576 |
| `vimanam-2026-09-07/exports/lambo/brand-org.full.json` | 7 | 1,743 |
| `vimanam-2026-09-07/exports/lambo/brand-org.txt` | 2 | 539 |
| `vimanam-2026-09-07/exports/lambo/calls.jsonl` | 15 | 2,524 |
| `vimanam-2026-09-07/exports/lambo/ci-clippy-failure.full.json` | 4 | 1,952 |
| `vimanam-2026-09-07/exports/lambo/diff-design.full.json` | 1 | 126 |
| `vimanam-2026-09-07/exports/lambo/merge-workflow.full.json` | 5 | 2,001 |
| `vimanam-2026-09-07/exports/lambo/merge-workflow.txt` | 1 | 340 |
| `vimanam-2026-09-07/exports/lambo/missing-downloads.full.json` | 2 | 765 |
| `vimanam-2026-09-07/exports/lambo/packaging-decision.full.json` | 4 | 1,065 |
| `vimanam-2026-09-07/exports/lambo/packaging-decision.txt` | 1 | 313 |
| `vimanam-2026-09-07/grader/grading.json` | 5 | 1,136 |
| `vimanam-2026-09-07/run-1/bundle.json` | 12 | 3,576 |
| `vimanam-2026-09-07/run-1/graded-evidence.json` | 5 | 1,136 |
| `vimanam-2026-09-07/run-1/grading.json` | 5 | 1,136 |
| `vimanam-2026-09-07/run-1/results.json` | 18 | 4,656 |

Total: 217 removals across 35 files, 40,238 bytes.

## Integrity of the exports

`bundle/bundle.json` and `run-1/bundle.json` still record the pre-redaction
`sha256` and `bytes` of every context handed to a reader. Those digests are
deliberately left as they were. They no longer match the redacted text, which
is the point. A reader can see exactly which contexts were touched, and can
confirm that every untouched context is byte-for-byte the text the reader
actually received.

Of the 24 contexts across the two bundles, 15 still hash to their recorded
digest. The lambo run keeps 6 of 12 and the vimanam run keeps 9 of 12. The same
counts hold for `run-1/bundle.json`. `run-1/results.sha256` and
`bundle/bundle.sha256` are likewise the pre-redaction digests of the original
artifacts.

Check it yourself:

```python
import json, hashlib
b = json.load(open("vimanam-2026-09-07/bundle/bundle.json"))
for q in b["questions"]:
    for arm, c in q["contexts"].items():
        ok = hashlib.sha256(c["text"].encode()).hexdigest() == c["sha256"]
        print(q["id"], arm, "verbatim" if ok else "redacted")
```

## What was not redacted

Question sets, rubrics, scores, rationales, grader provenance, timings, token
counts, node identifiers, and every concept about the operator's own
open-source projects are unchanged. Local paths under the operator home
directory are retained because they identify the corpora.
