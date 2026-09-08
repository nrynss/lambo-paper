# arXiv submission bundle, v1

Everything needed to submit this manuscript as a work in progress. Nothing here
is uploaded automatically. The owner performs the submission.

## Contents

| File | Purpose |
|---|---|
| `lambo-paper-arxiv-v1.tar.gz` | The source package to upload |
| `abstract.txt` | Plain-text abstract for the submission form |
| `README.md` | This checklist |

The tarball holds seven files at the top level, no wrapper directory:

- `main.tex`
- `main.bbl`
- `references.bib`
- `fig0_architecture.pdf`, `fig1_dispersion.pdf`, `fig2_latency.pdf`, `fig3_dedup_regimes.pdf`

No `.sty` or `.cls` file is bundled. The manuscript uses only TeX Live packages:
`geometry`, `amsmath`, `amssymb`, `amsfonts`, `booktabs`, `cite`, `microtype`,
`url`, `hyperref`, `graphicx`, `algorithm`, and `algpseudocode`, with the
`IEEEtran` bibliography style.

## Rebuild the tarball

```bash
make pdf                      # regenerates src/main.pdf and src/main.bbl
STAGE=$(mktemp -d)
cp src/main.tex src/main.bbl src/references.bib src/fig[0-3]_*.pdf "$STAGE/"
rm -f arxiv/lambo-paper-arxiv-v1.tar.gz
COPYFILE_DISABLE=1 tar -czf arxiv/lambo-paper-arxiv-v1.tar.gz -C "$STAGE" \
  main.tex main.bbl references.bib \
  fig0_architecture.pdf fig1_dispersion.pdf fig2_latency.pdf fig3_dedup_regimes.pdf
```

Always rebuild the tarball after editing `main.tex`. A stale `main.bbl` inside
the archive is the most common way an arXiv build diverges from the local one.

## Verified before submission

- `python3 scripts/verify_constraints.py` passes.
- `make test` passes.
- `src/main.tex` compiles with Tectonic 0.17.0 to `src/main.pdf`.
- The tarball was extracted into a clean temporary directory and compiled
  there. It produced a byte-identical `main.pdf`, and BibTeX regenerated a
  `main.bbl` identical to the shipped one.

## Upload checklist

1. **Include the `.bbl`.** arXiv does not run BibTeX. The `main.bbl` in the
   archive is what renders the bibliography. `references.bib` is included as
   well so the source also builds under engines that do run BibTeX. If arXiv
   flags the `.bib` as an unused file, that warning is safe to accept.
2. **Primary category: `cs.SE`** (Software Engineering). **Cross-list `cs.AI`**
   (Artificial Intelligence). The paper is a systems experience report about a
   development-time memory daemon, so software engineering is the primary home
   and the agent-memory audience reads `cs.AI`.
3. **Endorsement.** A first-time submitter without an institutional email may
   need an endorsement for `cs.SE` before the submission can be started. Request
   it early. arXiv shows an endorsement code and the categories it covers. An
   endorser must be an established submitter in that archive. Do not begin the
   upload assuming the endorsement will clear the same day.
4. **Announcement cutoff: 14:00 US Eastern, Monday through Friday.** A
   submission completed before that cutoff is announced the following business
   day. Anything after it rolls to the next cycle, and weekend submissions wait
   for Monday. Daylight saving shifts the corresponding local time, so check the
   clock on the arXiv page rather than assuming a fixed offset.
5. **Licence.** Pick deliberately on the submission form. The default
   `arXiv.org perpetual, non-exclusive license` is the most permissive option
   that still keeps every reuse decision with the author, and it is the right
   default for a work in progress. `CC BY 4.0` is the choice if the intent is to
   let others redistribute and adapt freely. The licence cannot be made more
   restrictive later.
6. **Abstract.** Paste `abstract.txt`. It is 1,891 characters, under the 1,920
   character limit that the form enforces. It is a lightly condensed form of the
   manuscript abstract, which is 2,059 characters and therefore does not fit.
   The condensation merges the four pipeline sentences into one and tightens two
   telemetry sentences. No figure, claim, or qualifier was dropped. Regenerate
   it whenever the manuscript abstract changes.
7. **Metadata.** Title and author must match the manuscript exactly. Report the
   comment field as a work in progress and name the data location, for example
   `Work in progress. Evaluation data at github.com/nrynss/lambo-paper under
   evaluation/results/2026-09-07`.
8. **Check the processed PDF.** arXiv shows its own build before you submit.
   Confirm the four figures render, the two tables are intact, and the
   bibliography lists all fifteen entries. Do not submit on the strength of the
   local PDF alone.

## Version plan

Post **v1** now, as a work in progress carrying the preliminary paired
comparison and its stated limits. The results are labelled preliminary in the
manuscript, and the limitations section names both open problems.

Post **v2** after the ranking work lands. v2 should carry, at minimum:

- The rendered context budget widened, or the structured hits exported, so the
  reader receives what the store actually returned.
- A supersession signal in recall, since canonization has never promoted a
  concept and no invalidation edge marked the retired encoder concepts.
- The two controls that were not run: a matched-corpus run and an equal-budget
  run.

Do not replace v1. arXiv keeps every version, and the v1 numbers are the
baseline the ranking fixes are measured against.
