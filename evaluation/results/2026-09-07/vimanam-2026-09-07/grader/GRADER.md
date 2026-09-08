# Grader provenance

Grader: a separate Claude Opus 5 agent (Claude Code Agent tool, model "opus"), run 2026-09-07 after all 24 reader answers existed.
Inputs: `grading.json` (shuffled opaque answer IDs, no arm key) and `reference.md` (primary-source facts). Instructed to read nothing else.
Rules: integer 0/1 per rubric, whole-rubric-or-nothing, explicit-abstention-only for missing-downloads, abstention scores 0 elsewhere, a correct answer that also asserts something the reference contradicts scores 0, non-ok status scores 0, edit only score and rationale.

Judgement calls reported by the grader (arm added after unblinding; grades were not altered):
1. merge-workflow answers 0006 and 0022 (both Lambo) scored 1 without naming enforce_admins=false; the grader read the rubric's disqualifier sentence as operative. A strict literal reading of clause (a) would flip both to 0 and make Lambo 6/12.
2. brand-org answer 0011 (file) scored 1 without stating the repo move from nrynss/vimanam; the disqualifier is "naming only the org". Strict reading would make file 9/12.
3. diff-design answers 0015 and 0020 (both Lambo) scored 1 without an explicit "not path sets" clause; the affirmative resolved-schema mechanism was present.
No answer failed under the false-assertion rule. Citation format was not penalized.
Blinding limit: bracketed filenames vs "[Type] (score N)" blocks reveal the source to an attentive grader; the grader was told not to infer it.
