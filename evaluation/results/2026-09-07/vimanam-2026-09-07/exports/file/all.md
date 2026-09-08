# Claude auto-memory export: ~/.claude/projects/-Users-narayan-Documents-work-vimanam/memory (snapshot 2026-09-07)

===== [MEMORY.md] =====
# Memory index

- [always SHA-pin actions](always-sha-pin-actions.md) — standing rule: pin GitHub Actions to commit SHAs, never mutable tags
- [noemaforge brand](noemaforge-brand.md) — vimanam ships its distribution under a "noemaforge" org, not the personal nrynss handle
- [vimanam packaging/dist](vimanam-packaging-dist.md) — #32 resolved: adopt upstream dist, reject GoReleaser, Astral's fork is archived
- [CI clippy toolchain drift](ci-clippy-toolchain-drift.md) — CI stable is newer than local default; run clippy with the newest installed toolchain before pushing
- [vimanam merge workflow](vimanam-merge-workflow.md) — main needs an unsatisfiable review, so squash + --admin; stacked PRs need retarget-before-merge and a rebase

===== [always-sha-pin-actions.md] =====
---
name: always-sha-pin-actions
description: "Always pin GitHub Actions to full commit SHAs, never mutable tags"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e08ce15d-a31b-4080-9850-b711abc3157d
---

Narayan's standing rule: **always pin GitHub Actions to a full 40-character commit SHA**, never
a mutable tag like `@v1`/`@v6`.

**Why:** tags can be silently repointed at malicious code if an action or a maintainer account is
compromised; a commit SHA is immutable and is the only way to use an action as an immutable
release. Keep a `# vX` trailing comment for readability; Dependabot/Renovate update SHA pins.

**How to apply:** pin every `uses:` in every workflow to a SHA. For dist-generated workflows
(which emit tag pins), hand-pin after generation and set `allow-dirty = ["ci"]` so `dist plan`
tolerates it; keep a CI `pin-check` job that fails on any unpinned action. Educate downstream
consumers to pin too (e.g. in action READMEs). See [[vimanam-packaging-dist]].

===== [noemaforge-brand.md] =====
---
name: noemaforge-brand
description: "Narayan publishes vimanam's distribution channels under a \"noemaforge\" brand/org, not his personal nrynss handle"
metadata: 
  node_type: memory
  type: project
  originSessionId: e08ce15d-a31b-4080-9850-b711abc3157d
---

Narayan publishes vimanam under a **`noemaforge`** brand rather than his personal GitHub
handle `nrynss` ("my name seems weird on a tap"). The `noemaforge` GitHub **org was
created 2026-06-26** (https://github.com/noemaforge).

Decision (2026-06-26): **move the whole repo** `nrynss/vimanam` → `noemaforge/vimanam`
(not just the tap) for full brand consistency. All repo-location URLs in the codebase
(Cargo.toml repository/homepage, README, CHANGELOG compare links, CONTRIBUTING,
CODE_OF_CONDUCT security URL) were rewritten to noemaforge, and the local git remote was
repointed. The GitHub repo **transfer itself + re-adding Actions secrets are Narayan's
manual steps**. Kept as personal identity (NOT rebranded): the `authors` email
`nrynss@users.noreply.github.com` and the `@nrynss` security contact in CODE_OF_CONDUCT.

The Homebrew tap is `noemaforge/homebrew-tap` → `brew install noemaforge/tap/vimanam`.
The CI GitHub Action (#9) lives at `noemaforge/vimanam-action` (tags `v0.1.0`, `v1`).

**v0.6.0 shipped 2026-06-26** as the first dist-driven release: crates.io publish,
5-target binaries (incl. aarch64-linux), shell/PowerShell installers, and the Homebrew
formula all succeeded. Org secrets (`CARGO_REGISTRY_TOKEN`, `HOMEBREW_TAP_TOKEN`) are scoped
to the repo and confirmed working (org secrets reach public repos on the Free plan).

When wiring any new public distribution channel for vimanam, default the owning
account to `noemaforge`, not `nrynss`. See [[vimanam-packaging-dist]].

===== [vimanam-packaging-dist.md] =====
---
name: vimanam-packaging-dist
description: "Vimanam adopted dist (cargo-dist) for release automation (#32); GoReleaser rejected; Astral's fork is dead"
metadata: 
  node_type: memory
  type: project
  originSessionId: e08ce15d-a31b-4080-9850-b711abc3157d
---

For vimanam's packaging strategy (#32), the decision is **adopt upstream `dist`
(axodotdev/cargo-dist)** for release automation.

- **GoReleaser rejected**: Go-centric, its toolchain-free `prebuilt` builder is Pro/paid,
  and its Homebrew formula output is deprecated.
- **dist chosen**: actively maintained (v0.32.0, 2026-05-21). The "changed hands" worry
  was a misread — `astral-sh/cargo-dist` was an unofficial fork of 0.28.0 that was
  **archived 2025-12-19** and now redirects to upstream; its fixes are in upstream 0.29.0.
  So there is no live fork to choose; **use upstream axodotdev**.

dist owns `.github/workflows/release.yml` (enforced by `dist generate --check`). Because
dist does **not** publish to crates.io, that step lives in a separate `publish-crate.yml`.
Config is in `dist-workspace.toml`. cargo-binstall works automatically via dist-manifest.json
(no `[package.metadata.binstall]` needed). Tap is under [[noemaforge-brand]].

Action pinning: dist's generated `release.yml` uses mutable tag pins. We hand-pin them to full
commit SHAs and set `allow-dirty = ["ci"]` in `dist-workspace.toml` so `dist plan` tolerates the
edit (otherwise it fails the workflow as "out of date"). A `pin-check` job in `ci.yml` fails if
any action is left unpinned. `dist generate`/`dist init` still rewrite `release.yml` back to tag
pins on regeneration — re-pin afterward; pin-check catches it. See [[always-sha-pin-actions]].

===== [ci-clippy-toolchain-drift.md] =====
---
name: ci-clippy-toolchain-drift
description: "CI runs clippy on latest stable, which is newer than the local default toolchain; run cargo +<newest installed> clippy before pushing"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5c03464c-b1e3-4c4d-b91b-5c081cf870b9
  modified: 2026-09-04T21:06:13.799Z
---

The vimanam CI job "Format, lint, test (stable)" installs the latest stable Rust (1.98 as of 2026-09-05) and runs `cargo clippy --all-targets -- -D warnings`. The local default toolchain lagged at 1.96, so clippy passed locally and failed in CI on a lint (`question_mark`) that only newer clippy emits. Both PRs #91 and #92 hit this on 2026-09-04.

**Why:** `-D warnings` turns any newly added clippy lint into a hard CI failure the moment GitHub's runner picks up a newer stable, independent of the code changed.

**How to apply:** before pushing, run clippy with the newest toolchain installed locally (`rustup toolchain list`; e.g. `cargo +1.97.1 clippy --all-targets -- -D warnings`) or `rustup update stable` first. If CI fails on clippy but local passes, compare `rustc` versions in the CI log before assuming the new code is at fault. Related: [[always-sha-pin-actions]].

===== [vimanam-merge-workflow.md] =====
---
name: vimanam-merge-workflow
description: "vimanam main requires 1 review that nobody can give, so merges need gh pr merge --admin; squash is the convention"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5c03464c-b1e3-4c4d-b91b-5c081cf870b9
  modified: 2026-09-05T16:26:02.313Z
---

`main` in noemaforge/vimanam has branch protection requiring 1 approving review, but the repo is effectively solo and GitHub forbids approving your own PR, so no PR can merge through the normal path. `enforce_admins` is false, so the working merge is `gh pr merge <n> --squash --admin --delete-branch`. Main's history is squash-style (`title (#PR)`), and `deleteBranchOnMerge` is on.

**Why:** confirmed 2026-09-05 while merging PRs #91 and #92. The protection rule is unsatisfiable rather than merely inconvenient, so admin override is the routine path here, not an exception. Still worth confirming with the user before bypassing.

**How to apply:** for *stacked* PRs, retarget the child to `main` **before** merging the parent, or deleting the parent's branch auto-closes the child. After the parent squash-merges, the child's commits no longer share a base with main, so run `git rebase --onto origin/main <parent-branch-tip-sha> <child-branch>`, force-push, and let CI re-run. Also strip any "stacked on #N" line from the child's PR body first, since squash merge puts the body into main's commit message. Related: [[ci-clippy-toolchain-drift]].

