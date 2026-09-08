# Grader provenance

Grader: a separate Claude Opus 5 agent (Claude Code Agent tool, model "opus"), run 2026-09-07 after all 24 reader answers existed.
Inputs given to the grader: `grading.json` (shuffled opaque answer IDs, no arm key) and `reference.md` (primary-source facts). It was instructed to read nothing else.
Rules given: integer 0/1 per rubric, whole-rubric-or-nothing, explicit-abstention-only for missing-cloud-cost, abstention scores 0 elsewhere, a correct answer that also asserts something the reference contradicts scores 0, non-ok status scores 0, edit only score and rationale.
The grader flagged one judgement call: answers 0015 and 0020 (record-action-embedding) state the NULL-embedding mechanism correctly but repeat a 2026-08-20 finding from their own evidence ("most Constraints/Logics/Entities" unembedded) that the settled diagnosis in commit bef53e6 contradicts; scored 0 under the false-assertion rule. The arm key later showed both were Lambo-arm answers. Grades were not altered after unblinding.
Blinding limit: distinctive content (filenames in brackets vs "[Type] (score N)" blocks) could reveal the source to a grader; the grader was told not to infer it.
