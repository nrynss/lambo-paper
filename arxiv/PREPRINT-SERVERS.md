# Preprint and archive submission kit

Everything below is copy-ready. Each service needs the account holder to sign in, accept its terms, and submit, so these steps are done by the author.

## Common fields
- Title: Lambo: A Living Topological Memory Substrate for Multi-Agent Software Development
- Author: Narayan SS (nryn@lambo.dev), independent
- Abstract: `arxiv/abstract.txt` (1,892 characters, plain text)
- Keywords: agent memory, multi-agent systems, software engineering agents, graph memory, retrieval, Model Context Protocol
- Subject: Computer Science, Software Engineering (secondary: Artificial Intelligence)
- Files: `src/main.pdf` (compiled paper), `arxiv/lambo-paper-arxiv-v1.tar.gz` (LaTeX source with .bbl)
- Code and data: https://github.com/nrynss/lambo-paper (release v0.1-preprint), web edition https://nrynss.github.io/lambo-paper/
- Licence: CC BY 4.0 is the default written into CITATION.cff and .zenodo.json. Change both files first if you prefer another licence.
- Version note: work-in-progress preprint v0.1. State this in any "comments" or "notes" field.

## Zenodo (DOI, minutes)
1. Sign in at https://zenodo.org with GitHub. Go to https://zenodo.org/account/settings/github/ and flip the switch for `nrynss/lambo-paper`.
2. Zenodo archives on the next release. Publish a new release (for example `v0.1.1-preprint`) and Zenodo mints a DOI within a minute. The metadata comes from `.zenodo.json`.
3. Paste the DOI badge into README.md and add the DOI to `CITATION.cff` under `identifiers`.

## Software Heritage (permanent code archive)
Save requests for `nrynss/lambo-paper` and `nrynss/lambo` were accepted on 2026-09-08. Check status and get the SWHID at https://archive.softwareheritage.org/browse/origin/directory/?origin_url=https://github.com/nrynss/lambo-paper. Cite the SWHID for the release commit.

## TechRxiv (IEEE, no endorsement)
https://www.techrxiv.org/ then "Submit". Upload `src/main.pdf`, subject Computing and Processing, paste the abstract and keywords, licence CC BY 4.0. Moderation takes one to three business days and yields a DOI.

## OSF Preprints (no endorsement)
https://osf.io/preprints/ then "Add a preprint". Provider: OSF Preprints, discipline Computer and Information Sciences, upload the PDF, add the GitHub link as supplemental material. DOI is immediate on publish.

## SSRN CompSciRN and Preprints.org
Both accept CS preprints without a gatekeeper. Use them only if you want the extra index entries; they carry less weight than arXiv, and Google Scholar may list the copies separately.

## Authorea and Research Square
Both give a DOI plus public commenting. Research Square is tied to journal submission workflows and is a poor fit for an independent preprint. Authorea accepts a PDF upload directly.

## Recommendation
Post to arXiv when the submission flow works, take the Zenodo DOI now, keep the Software Heritage archive, and choose at most one of TechRxiv or OSF. Multiple preprint copies split citations and confuse Google Scholar's merging.

## Google Scholar
The web edition now carries citation meta tags (title, author, date, PDF URL) on every page. Scholar crawls independently and usually indexes within a few weeks. The PDF must remain at https://nrynss.github.io/lambo-paper/lambo-paper.pdf.
