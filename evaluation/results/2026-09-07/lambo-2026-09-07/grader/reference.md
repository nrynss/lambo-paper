# Reference evidence for grading (primary sources, frozen 2026-09-07)

Grade each answer ONLY against its rubric using these facts. Sources are quoted verbatim.

## dogfood-topology
Source: ~/Library/LaunchAgents/dev.lambo.dogfood.plist (ProgramArguments) and ~/Documents/work/scripts/lambo-dogfood.sh header.
```
["\/Users\/narayan\/lambo-dogfood\/bin\/lambo-e11fb06","serve","--config","\/Users\/narayan\/lambo-dogfood\/lambo.toml","--session","lambo-dev","--agent","http-shared-writer","--transport","http","--port","7700","--ledger","\/Users\/narayan\/lambo-dogfood\/calls.jsonl","--ledger-heartbeat","300"]# lambo-dogfood.sh — start/stop the dogfood lambo writer (launchd-supervised HTTP serve).
# The writer is dev.lambo.dogfood: one long-lived `lambo serve --transport http --port 7700`
# that every agent on this machine points at. See dev-diary/lambo-for-mooshik/DOGFOOD-SETUP.md.
set -eu
```
Fact: one launchd-supervised `lambo serve --transport http --port 7700 --agent http-shared-writer`; every agent on the machine points at http://127.0.0.1:7700/mcp and none spawns its own serve.

## embedder-superseded
Source: ~/lambo-dogfood/lambo.toml comments and dev-diary/lambo-for-mooshik/DOGFOOD.md.
```
8:# K2 migration 2026-08-23: in-process candle BGE-M3 on Metal, replacing the
9:# llama-server bge_m3 path. Device is pinned explicitly rather than "auto":
12:# Previous config kept at lambo.toml.bge-backup (kind = "bge_m3", :8080).
14:kind = "candle"
16:device = "metal"
1. **Pin: `21e4cf8`** (K2 migration, 2026-08-23). Binary at
   `~/lambo-dogfood/bin/lambo-21e4cf8`, built
   `--features store-sqlite,embed-candle-metal,embed-bge`; config at
   `~/lambo-dogfood/lambo.toml` (sqlite at `~/lambo-dogfood/lambo-dev.db`,
   **`kind = "candle"`, `device = "metal"`**, dim 1024). The user-scope MCP
   registration in `~/.claude.json` was repointed to the new binary in the same act —
   it is the thing that actually spawns the serve, so a re-pin that skips it silently
   keeps serving the old binary.
   **The rig no longer needs llama-server.** Embedding is in-process; §1 of
   DOGFOOD-SETUP is now only needed to reproduce K1's parity captures, not to run the
   rig. The previous config is kept at `~/lambo-dogfood/lambo.toml.bge-backup`
   (`kind = "bge_m3"`, `127.0.0.1:8080`) so the old path is one copy away.
```
Fact: current embedder is in-process candle BGE-M3 (kind = candle, device = metal, dim 1024), adopted in the K2 migration on 2026-08-23; it replaced the llama-server bge_m3 embedder on 127.0.0.1:8080.

## record-action-embedding
Source: git commit bef53e6 in nrynss/lambo.
```
bef53e6 fix(action): record_action embeds the concepts it creates

`record_action` had no embedder hop, so every concept it created stored
`embedding: NULL` while `derive`'s concepts were embedded. Found dogfooding
2026-09-01: 555 of 946 concepts on the lambo-dev session had no vector, and
the split was categorical rather than partial — Observation 68/68, Logic
109/109 and Constraint 130/130 embedded (all arrive through `derive`), against
Resource 394/454 and Entity 161/185 NULL (the action string plus every
produces / modifies / depends_on entry).

The effect is an inversion: everything an agent CONCLUDED was semantically
searchable, everything it DID was reachable by keyword and graph traversal
only. It also accrued daily rather than draining — 2026-09-01 alone wrote 41
NULL against 39 embedded — so no amount of re-embedding could fix it.

- `record_action_with_embeddings` takes vectors keyed by the exact content
  string and puts them on the concepts it creates. `record_action` stays as
  the keyword-only entry point (a sync signature has nowhere to put a model
  call) and delegates with an empty map.
- `embed_action_contents` embeds the distinct candidate strings off-lock, with
```
Fact: record_action had no embedder hop, so concepts it created were stored with embedding NULL; derive-created concepts were embedded. Effect: what agents DID (Resource/Entity action concepts) was reachable only by keyword and graph traversal while what they CONCLUDED was vector-searchable (an inversion); 555 of 946 concepts on lambo-dev had no vector at discovery.

## model-roles
Source: operator directive recorded 2026-08-14/2026-08-24 (Claude auto-memory opus-review-remediation-agents.md).
```

User directive (2026-08-14, sharpened 2026-08-24): model choice for lambo agents is
two-dimensional. By role, **ALL remediation runs on Opus** (including E2E-level
remediation). By scope, **review** runs on Fable at whole-workstream E2E level and on
Opus per-task. Implementation agents have been Opus to date; keep that unless told
otherwise.

**Why:** Review/remediation quality is the load-bearing guarantee of the loop — the
strongest model goes on the low-frequency, high-leverage E2E review checkpoint, Opus
everywhere else.

```
Fact: ALL remediation runs on Opus; whole-workstream E2E review runs on Fable; per-task review runs on Opus.

## throttle-interval-why
Source: ~/Library/LaunchAgents/dev.lambo.dogfood.plist comment.
```
32-
33:  <!-- macOS analogue of systemd RestartSec. Default is 10s, which sits INSIDE
34-       lease::LEASE_TTL (45s): an abrupt death does not release the lease, so a
35-       retry inside the TTL exits 1 on a refused acquire. 60 > 45 puts every
36-       retry after the lease has lapsed. launchd has no StartLimitIntervalSec
37-       analogue and needs none — it has no permanent-FAILED state, so the
38-       systemd hazard this guards (budget burned, unit dead for good) does not
39-       exist here. -->
40-  <key>ThrottleInterval</key>
```
Fact: launchd default restart delay is 10 s, which sits inside the 45 s single-writer lease TTL (LEASE_TTL); an abrupt death does not release the lease, so a retry inside the TTL exits on a refused acquire. 60 s > 45 s puts every retry after the lease has lapsed.

## missing-cloud-cost
Fact: no cost, price, USD, or per-month figure for the lambo-pg Cloud SQL instance exists in either memory corpus (verified by search of the store copy and the memory directory on 2026-09-07). The only correct answer is an explicit abstention.
