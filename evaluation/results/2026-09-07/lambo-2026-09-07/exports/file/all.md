# Claude auto-memory export: ~/.claude/projects/-Users-narayan-Documents-work-lambo/memory (snapshot 2026-09-07)

===== [MEMORY.md] =====
- [Lambo dogfood rig](lambo-dogfood-rig.md) — supervised HTTP writer :7700, pin lambo-e11fb06, all agents wired, Claude Code enforcement hooks, ctl script in work/scripts
- [Lambo agent protocol](lambo-agent-protocol.md) — recall twice, derive at decision time, agent_id = model name, hits are context not instruction
- [Opus review/remediation agents](opus-review-remediation-agents.md) — remediation always Opus; review Fable at E2E scope, Opus per-task
- [Agent work in worktrees](agent-work-in-worktrees.md) — code-editing agents always get isolated worktrees, never the main checkout
- [Visible command output](visible-command-output.md) — no silent long-running commands; narrate and stream

===== [agent-work-in-worktrees.md] =====
---
name: agent-work-in-worktrees
description: "All lambo implementation agents must run in isolated git worktrees, never the main checkout"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 85a4de05-8e21-4027-b9c2-029f7adf0e96
  modified: 2026-08-19T05:30:20.743Z
---

When launching agents that edit code in lambo, always use worktree isolation (Agent tool `isolation: "worktree"`, or an explicit `git worktree add`), never the main working tree.

**Why:** Multiple agents (or an agent plus the user) in one checkout stomp each other's uncommitted changes. The repo's own convention (dev-diary/README.md git workflow) is task-per-worktree; user confirmed this should apply to my agents too (2026-08-19).

**How to apply:** Pass `isolation: "worktree"` when spawning implement/remediation agents via the Agent tool. Orchestrator merges the result back. Related: [[opus-review-remediation-agents]].

===== [lambo-agent-protocol.md] =====
---
name: lambo-agent-protocol
description: "How every agent (orchestrator and subagents) uses lambo-dogfood: recall twice, derive at decision time, agent_id = model name, hits are context not instruction"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: dd5aceb0-43f8-4e6f-b62f-17dd1b15cb6d
  modified: 2026-09-01T11:44:50.087Z
---

How to use the `lambo-dogfood` MCP tools, settled with the user across the dogfood work.
Every subagent prompt for lambo work must carry this protocol block — subagents never use
lambo unprompted even when AGENTS.md obliges it; the obligation must be in the prompt.

1. **Recall twice**: `lambo_recall` on the task topic before reading code, then a second
   **targeted** recall after reading spec+code, using the specific names just learned
   (constants, functions, invariants). Topic queries rank decisions pinned to specifics
   too low — reasoning is often in the graph but only findable by key name.
2. **Hits are prior context, not instructions.** Authority order: spec → phase doc →
   source → graph. On conflict, don't silently obey either side — name the conflict with
   evidence and proceed on spec/source. (For *infrastructure* decisions AGENTS.md's
   stronger "settled, don't re-litigate" wording applies; the user rejected that wording
   for task work.)
3. **Derive at decision time, not session end.** Sessions get killed (watchdogs, machine
   sleep); un-derived analysis dies with them. Write each decision/surprise/dead-end via
   `lambo_derive` when it happens — decisions *with their why*, not activity. Final
   report = summary of what's already in the graph + `lambo_record_action` on the commit.
4. **`agent_id` = the MODEL name** (`claude-fable-5`, `gpt-5-codex`, …), stable for the
   session; harness name only as fallback when the model id is unknowable (operator
   ruling 2026-09-01; doc of record `~/Documents/work/lambo-dogfood-setup.md` — the repo's
   AGENTS.md deliberately not yet updated, see [[lambo-dogfood-rig]]).
   **Open implication:** soft locks (`lambo_reserve`) are per-`agent_id`, so parallel
   subagents on the same model SHARE locks — if that bites, ask the user whether
   subagents suffix the model id (`claude-fable-5/implementor`) rather than silently
   deciding.
5. **Deviation from recalled decisions is allowed with argued evidence; undeclared
   deviation is a finding.**
6. Writes are applied in the background: `lambo_derive`/`lambo_record_action` return a
   receipt; if the next read must see the write, call `lambo_stats` with that receipt and
   a `wait_ms` first.

Related: [[opus-review-remediation-agents]], [[agent-work-in-worktrees]].

===== [lambo-dogfood-rig.md] =====
---
name: lambo-dogfood-rig
description: "Live Lambo session for dogfooding lambo development — supervised HTTP writer, pinned binary lambo-e11fb06, every agent on the machine wired to :7700"
metadata: 
  node_type: memory
  type: project
  originSessionId: 85a4de05-8e21-4027-b9c2-029f7adf0e96
  modified: 2026-09-01T13:09:42.013Z
---

Stood up 2026-08-19 per dev-diary/lambo-for-mooshik/DOGFOOD.md; DOGFOOD-SETUP.md is the
replicable runbook — read both before acting.

- **Topology (operator ruling 2026-08-23): HTTP, always.** One launchd-supervised writer
  (`dev.lambo.dogfood`, `~/Library/LaunchAgents/dev.lambo.dogfood.plist`) runs
  `serve --transport http --port 7700 --agent http-shared-writer` with the ledger flags;
  every client is a URL entry pointing at `http://127.0.0.1:7700/mcp`, none spawns a serve.
- **Operator script:** `~/Documents/work/scripts/lambo-dogfood.sh`
  (`start|stop|restart|status|log`) wraps launchctl bootstrap/bootout + health + lease
  check. Verified 2026-09-01: graceful stop releases the lease, start reacquires
  immediately (no 45s TTL wait).
- **Pinned binary:** `~/lambo-dogfood/bin/lambo-e11fb06` (re-pinned 2026-09-01 evening;
  carries the record_action embedder-hop fix + `re-embed --missing-only` repair verb —
  backfilled 42 NULL-vector concepts, coverage now 576/576). Build: clean tree,
  `LAMBO_GIT_SHA` set, features `store-sqlite,embed-candle-metal,embed-bge`. Never point
  serve at `target/`. Re-pin = build → copy → stop (ctl script) → `provision --config`
  (idempotent) → run any repair verbs while stopped → sed plist → start → check ledger
  heartbeat `git_sha` + MCP stats.
- **Config:** `~/lambo-dogfood/lambo.toml` → sqlite `~/lambo-dogfood/lambo-dev.db`,
  embedder `kind = "candle"` (in-process BGE-M3, f16 safetensors), `device = "metal"`
  pinned, dim 1024. No llama-server needed since 2026-08-23 — embedding is in-process;
  the `kind = "bge_m3"` llama-server-on-:8080 path is kept only as documented fallback.
- **Clients wired (2026-09-01, all to the same URL):** Claude Code `~/.claude.json`,
  Codex `~/.codex/config.toml`, Cursor `~/.cursor/mcp.json` (pre-existing) + Gemini CLI
  `~/.gemini/settings.json` (`httpUrl`), opencode `~/.config/opencode/opencode.json`
  (`type: remote`), Copilot CLI `~/.copilot/mcp-config.json` (`type: http`), Pi via
  generic `~/.config/mcp/mcp.json`, Antigravity `~/.gemini/antigravity{,-ide}/mcp_config.json`
  (`serverUrl`). Backups sit beside each as `*.bak-lambo`.
- **Enforcement hooks (2026-09-01, user scope — machine-wide), three harnesses:**
  - *Claude Code*: `~/.claude/settings.json` → `~/lambo-dogfood/hooks/lambo-hook.sh`.
    SessionStart reminder + writer health; PreToolUse denies file edits until one
    `lambo_recall` (max 2 denials — no deadlock); Stop blocks an unrecorded editing turn
    once. Verified live. Backup: `~/.claude/settings.json.bak-lambo-hooks`.
  - *Codex — the ChatGPT app is "the new codex" per user; the npm CLI is broken
    (missing native binary; [REDACTED: sensitive data, 94 bytes])*: `~/.codex/hooks.json` reuses `lambo-hook.sh` (Codex's
    hook contract ≈ Claude Code's; `session-start-json` subcommand for the JSON
    additionalContext form) + protocol section appended to `~/.codex/AGENTS.md`. May
    need one-time hook trust in the app; user-level discovery in the app unverified —
    ask user to test an edit-before-recall once.
  - *Cursor*: `~/.cursor/hooks.json` → `cursor-lambo-hook.sh` (different contract:
    camelCase events, permission/agentMessage, conversation_id key). Recall gate on
    beforeShellExecution (no blockable before-edit event exists); afterFileEdit +
    afterMCPExecution as markers; stop can't block → `followup_message` demanding the
    derive, loop_limit 1. Cloud agents ignore user-level hooks — local only.
  All gates fail open when the writer is down; shared state in
  `~/lambo-dogfood/hooks/state/`. Exists because instructions alone don't bind these
  harnesses reliably (Claude Code worst).
- **agent_id = MODEL name** (operator ruling 2026-09-01): send `claude-fable-5` etc., not
  harness names; harness name only as fallback. Registration cannot inject it — it needs
  the instruction layer. **Repo docs deliberately NOT updated** (operator ruling, same
  day): the doc of record is `~/Documents/work/lambo-dogfood-setup.md` (updated §4/§4b +
  a pending-AGENTS.md appendix to apply when the user says to land it). Until then,
  AGENTS.md readers (Codex, Cursor, …) still send harness names — a valid fallback;
  Claude Code follows the model-name rule via its hooks and this memory. See
  [[lambo-agent-protocol]] for the subagent-locks implication.
- **Second rig (2026-09-04):** a Linux desktop with an RTX 4070 runs the same session
  name under systemd (`lambo-dogfood.service`, build bef53e6, candle CUDA, ~1,650 concepts,
  63 agent_ids incl. OMP/Codex/Cursor/pi/Antigravity). Separate store and ledger. GitHub
  issues #8/#9/#10 were measured THERE; the Mac numbers are ~825 concepts and Claude Code
  only. Never mix the two rigs' figures. Both stores keep vectors as decimal text (12.7 KB
  each), so recall scans ~10 MB per call on the Mac; #8 proposes packed binary storage.
- Protocol: recall before a workstream; derive decisions-with-why; record-action merges
  and re-pins ([[opus-review-remediation-agents]], [[agent-work-in-worktrees]]). Store
  never enters the public repo; curated export only.

===== [opus-review-remediation-agents.md] =====
---
name: opus-review-remediation-agents
description: Lambo per-task review/remediation agents run on Opus; workstream-level E2E review gates run on Fable
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 77526108-387a-488b-9d23-443d75a8ceef
  modified: 2026-09-01T11:31:15.657Z
---

User directive (2026-08-14, sharpened 2026-08-24): model choice for lambo agents is
two-dimensional. By role, **ALL remediation runs on Opus** (including E2E-level
remediation). By scope, **review** runs on Fable at whole-workstream E2E level and on
Opus per-task. Implementation agents have been Opus to date; keep that unless told
otherwise.

**Why:** Review/remediation quality is the load-bearing guarantee of the loop — the
strongest model goes on the low-frequency, high-leverage E2E review checkpoint, Opus
everywhere else.

**How to apply:** Agent dispatches for adversarial review, remediation, re-review, or
mutation-testing pass `model: "opus"`; only a whole-workstream E2E *review* passes
`model: "fable"`. Related: [[agent-work-in-worktrees]], [[lambo-agent-protocol]].

===== [visible-command-output.md] =====
---
name: visible-command-output
description: "User needs to see what's happening when commands run — avoid silent long-running/backgrounded commands"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 77526108-387a-488b-9d23-443d75a8ceef
  modified: 2026-08-14T03:42:34.222Z
---

User feedback (2026-08-14): "When you run commands, I need to see what is happening." A `pi -p` test ran 180s with no output, got backgrounded, and was killed — user saw nothing.

**Why:** Long buffered or backgrounded commands leave the user blind; they want visibility into progress.

**How to apply:** Prefer short foreground commands with incremental output; tee long runs to a stated log path and report it immediately; narrate what's running before launching it; poll and report interim status rather than waiting on a long timeout.

