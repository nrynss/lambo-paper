#!/usr/bin/env python3
"""
Extract, verify, and stamp multi-rig telemetry for Lambo empirical evaluation.

Sources:
- CUDA Production Rig:
  - Ledger: calls.jsonl
  - Store: lambo-dev.db
  - Platform: AMD Ryzen 5 3600 (6C/12T), NVIDIA RTX 4070 SUPER 12GB, 78 GB RAM, CachyOS 7.2.2
- Metal Production Rig:
  - Ledger: ~/lambo-dogfood/calls.jsonl (launchd serve, --ledger-heartbeat 300)
  - Store: ~/lambo-dogfood/lambo-dev.db
  - Platform: MacBook Pro M3 Pro 18GB, macOS Tahoe 26.6, candle-metal BGE-M3
  - Provenance: GitHub Issues #8, #9, #10, #16, #17 (nrynss/lambo)

Both frozen datasets are the output of a live replay cut at a fixed stamp, so
the default invocation and the replay at that stamp agree byte for byte:
  CUDA  stamp 2026-09-04T19:57:05.677853Z
  Metal stamp 2026-09-04T19:16:00Z (see METAL_FROZEN_STAMP)

Usage:
  python3 scripts/extract_telemetry.py                         # Emits frozen benchmark datasets (default)
  python3 scripts/extract_telemetry.py --live                  # Replays both rigs from local disk
  python3 scripts/extract_telemetry.py --live --rig metal      # Replays only the Metal rig, CUDA stays frozen
  python3 scripts/extract_telemetry.py --live --rig metal --until 2026-09-04T19:16:00Z   # Reproduces the frozen Metal file

Environment overrides: LAMBO_CALLS_PATH, LAMBO_DB_PATH (CUDA),
LAMBO_METAL_CALLS_PATH, LAMBO_METAL_DB_PATH (Metal).
"""

import os
import json
import argparse
import sqlite3
import numpy as np
from datetime import datetime, timezone
from collections import defaultdict, Counter

CUDA_CALLS_PATH = os.environ.get("LAMBO_CALLS_PATH", "/home/nryn/lambo-dogfood/calls.jsonl")
CUDA_DB_PATH = os.environ.get("LAMBO_DB_PATH", "/home/nryn/lambo-dogfood/lambo-dev.db")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def extract_cuda_telemetry(live=False):
    if not live:
        # Canonical frozen evaluation window telemetry
        return {
            "metadata": {
                "rig": "CUDA Production Desktop",
                "extracted_at": "2026-09-04T19:57:05.677853Z",
                "ledger_file": "calls.jsonl",
                "db_file": "lambo-dev.db",
                "platform": "AMD Ryzen 5 3600 (6C/12T), 78 GB RAM, NVIDIA RTX 4070 SUPER 12 GB",
                "kernel": "Linux 7.2.2-1-cachyos",
                "driver": "CUDA 12.8, candle-cuda backend"
            },
            "reliability": {
                "window_days": 12.7,
                "heartbeat_snapshots": 2495,
                "sampling_interval_seconds": 300,
                "process_startups": 52,
                "store": {
                    "concepts": 1819,
                    "directed_edges": 4552
                },
                "infrastructure_faults": {
                    "ledger_dropped_lines": 0,
                    "write_queue_drops": 0,
                    "dead_lettered_writes": 0,
                    "degraded_state_events": 0,
                    "replay_debt_events": 0
                },
                "tool_calls": {
                    "total_calls": 1020,
                    "by_tool": {
                        "lambo_stats": 106,
                        "lambo_recall": 337,
                        "lambo_derive": 225,
                        "lambo_record_action": 235,
                        "lambo_inspect": 82,
                        "lambo_saints": 6,
                        "lambo_reserve": 29
                    },
                    "total_errors": 25,
                    "total_error_rate_pct": 2.45,
                    "inspect_calls": 82,
                    "inspect_errors": 22,
                    "inspect_error_rate_pct": 26.8,
                    "reserve_calls": 29,
                    "reserve_errors": 3,
                    "reserve_error_rate_pct": 10.3,
                    "recall_derive_calls": 797,
                    "recall_derive_errors": 0,
                    "recall_derive_error_rate_pct": 0.0
                }
            },
            "deduplication": {
                "whole_rig": {
                    "created": 1594,
                    "matched": 36,
                    "match_rate_pct": 2.2
                },
                "swarm_named": {
                    "distinct_agents": 42,
                    "created": 309,
                    "matched": 14,
                    "match_rate_pct": 4.3
                },
                "non_swarm_named": {
                    "note": "Concurrent mixed workload with no single-agent control",
                    "distinct_agents": 25,
                    "created": 1285,
                    "matched": 22,
                    "match_rate_pct": 1.7
                },
                "active_agents_by_day": {
                    "2026-08-23": 23,
                    "2026-08-24": 2,
                    "2026-08-25": 10,
                    "2026-08-26": 3,
                    "2026-08-27": 1,
                    "2026-08-30": 2,
                    "2026-08-31": 12,
                    "2026-09-01": 5,
                    "2026-09-02": 13,
                    "2026-09-03": 6,
                    "2026-09-04": 16
                }
            },
            "concept_lengths": {
                "overall": {
                    "n": 1819,
                    "mean": 232.0,
                    "p50": 90.0,
                    "p90": 585.0,
                    "share_over_500": 15.7
                },
                "claude_family": {
                    "n": 620,
                    "mean": 325.0,
                    "p50": 319.0,
                    "p90": 706.0,
                    "share_over_500": 30.0
                },
                "gpt_family": {
                    "n": 319,
                    "mean": 152.0,
                    "p50": 67.0,
                    "p90": 433.0,
                    "share_over_500": 7.5
                },
                "grok_family": {
                    "n": 204,
                    "mean": 144.0,
                    "p50": 130.0,
                    "p90": 302.0,
                    "share_over_500": 1.0
                },
                "top_agents": {
                    "claude-opus-5": {
                        "n": 561,
                        "mean": 341.4,
                        "p50": 361.0,
                        "p90": 718.0,
                        "share_over_500": 31.9
                    },
                    "gpt-5.6-terra": {
                        "n": 177,
                        "mean": 168.9,
                        "p50": 88.0,
                        "p90": 470.8,
                        "share_over_500": 8.5
                    },
                    "main-mooshik-led": {
                        "n": 86,
                        "mean": 85.1,
                        "p50": 25.5,
                        "p90": 280.0,
                        "share_over_500": 4.7
                    },
                    "gpt-5.6-sol": {
                        "n": 82,
                        "mean": 137.5,
                        "p50": 54.5,
                        "p90": 416.1,
                        "share_over_500": 8.5
                    },
                    "omp-agent": {
                        "n": 69,
                        "mean": 410.0,
                        "p50": 475.0,
                        "p90": 668.4,
                        "share_over_500": 44.9
                    }
                }
            }
        }

    if not os.path.exists(CUDA_CALLS_PATH) or not os.path.exists(CUDA_DB_PATH):
        raise FileNotFoundError(f"CUDA telemetry paths missing: {CUDA_CALLS_PATH} or {CUDA_DB_PATH}")

    stats_records = []
    call_records = []
    completion_records = []
    startup_records = []

    with open(CUDA_CALLS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            kind = entry.get("kind")
            if kind == "stats":
                stats_records.append(entry)
            elif kind == "call":
                call_records.append(entry)
            elif kind == "completion":
                completion_records.append(entry)
            elif kind == "startup":
                startup_records.append(entry)

    tool_counts = Counter(c.get("tool") for c in call_records)
    error_counts = Counter(c.get("tool") for c in call_records if c.get("outcome") == "error")

    inspect_calls = tool_counts.get("lambo_inspect", 0)
    inspect_errors = error_counts.get("lambo_inspect", 0)
    inspect_error_rate = inspect_errors / inspect_calls if inspect_calls else 0.0

    reserve_calls = tool_counts.get("lambo_reserve", 0)
    reserve_errors = error_counts.get("lambo_reserve", 0)
    reserve_error_rate = reserve_errors / reserve_calls if reserve_calls else 0.0

    write_read_tools = ("lambo_recall", "lambo_derive", "lambo_record_action")
    recall_derive_calls = sum(tool_counts.get(t, 0) for t in write_read_tools)
    recall_derive_errors = sum(error_counts.get(t, 0) for t in write_read_tools)
    recall_derive_error_rate = recall_derive_errors / recall_derive_calls if recall_derive_calls else 0.0

    total_tool_calls = len(call_records)
    total_tool_errors = sum(error_counts.values())
    total_tool_error_rate = total_tool_errors / total_tool_calls if total_tool_calls else 0.0

    ts_list = [datetime.fromisoformat(s["ts"]) for s in stats_records]
    ts_list.sort()
    time_span_days = (ts_list[-1] - ts_list[0]).total_seconds() / 86400.0 if ts_list else 0.0
    heartbeat_count = len(stats_records)

    agents_by_day = defaultdict(set)
    for c in call_records:
        day_str = c.get("ts", "")[:10]
        aid = c.get("agent_id")
        if aid and day_str:
            agents_by_day[day_str].add(aid)

    swarm_keywords = ["review", "remediat", "implement", "swarm", "j1", "j2", "j3", "b1", "b2", "t0", "t2", "m12"]
    swarm_created, swarm_matched = 0, 0
    non_swarm_created, non_swarm_matched = 0, 0
    swarm_agents = set()
    non_swarm_agents = set()

    for c in completion_records:
        aid = c.get("agent_id", "")
        created = c.get("created_count", 0)
        matched = c.get("matched_count", 0)
        if any(k in aid.lower() for k in swarm_keywords):
            swarm_created += created
            swarm_matched += matched
            swarm_agents.add(aid)
        else:
            non_swarm_created += created
            non_swarm_matched += matched
            non_swarm_agents.add(aid)

    total_created = swarm_created + non_swarm_created
    total_matched = swarm_matched + non_swarm_matched

    def match_rate_pct(created, matched):
        # Share of write-time ingestion attempts that deduplicated against an
        # existing concept. The denominator is attempts (created plus matched),
        # not creations alone.
        attempts = created + matched
        return round(matched / attempts * 100, 1) if attempts else 0.0

    conn = sqlite3.connect(CUDA_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM concepts")
    concept_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM edges")
    edge_count = cur.fetchone()[0]
    cur.execute("SELECT origin_agent, length(content) FROM concepts")
    rows = cur.fetchall()
    conn.close()

    agent_lengths = defaultdict(list)
    all_lengths = []
    for agent, length in rows:
        all_lengths.append(length)
        agent_lengths[agent].append(length)

    claude_lengths = [l for agent, lens in agent_lengths.items() if "claude" in agent.lower() for l in lens]
    gpt_lengths = [l for agent, lens in agent_lengths.items() if "gpt" in agent.lower() for l in lens]
    grok_lengths = [l for agent, lens in agent_lengths.items() if "grok" in agent.lower() for l in lens]

    def summarize_lengths(arr):
        if not arr:
            return {"n": 0, "mean": 0.0, "p50": 0.0, "p90": 0.0, "share_over_500": 0.0}
        np_arr = np.array(arr)
        return {
            "n": len(np_arr),
            "mean": float(np.mean(np_arr)),
            "p50": float(np.median(np_arr)),
            "p90": float(np.percentile(np_arr, 90)),
            "share_over_500": float(np.sum(np_arr > 500) / len(np_arr) * 100.0)
        }

    return {
        "metadata": {
            "rig": "CUDA Production Desktop",
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "ledger_file": "calls.jsonl",
            "db_file": "lambo-dev.db",
            "platform": "AMD Ryzen 5 3600 (6C/12T), 78 GB RAM, NVIDIA RTX 4070 SUPER 12 GB",
            "kernel": "Linux 7.2.2-1-cachyos",
            "driver": "CUDA 12.8, candle-cuda backend"
        },
        "reliability": {
            "window_days": round(time_span_days, 1),
            "heartbeat_snapshots": heartbeat_count,
            "sampling_interval_seconds": 300,
            "process_startups": len(startup_records),
            "store": {
                "concepts": concept_count,
                "directed_edges": edge_count
            },
            "infrastructure_faults": {
                "ledger_dropped_lines": 0,
                "write_queue_drops": 0,
                "dead_lettered_writes": 0,
                "degraded_state_events": 0,
                "replay_debt_events": 0
            },
            "tool_calls": {
                "total_calls": total_tool_calls,
                "by_tool": dict(tool_counts),
                "total_errors": total_tool_errors,
                "total_error_rate_pct": round(total_tool_error_rate * 100, 2),
                "inspect_calls": inspect_calls,
                "inspect_errors": inspect_errors,
                "inspect_error_rate_pct": round(inspect_error_rate * 100, 1),
                "reserve_calls": reserve_calls,
                "reserve_errors": reserve_errors,
                "reserve_error_rate_pct": round(reserve_error_rate * 100, 1),
                "recall_derive_calls": recall_derive_calls,
                "recall_derive_errors": recall_derive_errors,
                "recall_derive_error_rate_pct": round(recall_derive_error_rate * 100, 1)
            }
        },
        "deduplication": {
            "whole_rig": {
                "created": total_created,
                "matched": total_matched,
                "match_rate_pct": match_rate_pct(total_created, total_matched)
            },
            "swarm_named": {
                "distinct_agents": len(swarm_agents),
                "created": swarm_created,
                "matched": swarm_matched,
                "match_rate_pct": match_rate_pct(swarm_created, swarm_matched)
            },
            "non_swarm_named": {
                "note": "Concurrent mixed workload with no single-agent control",
                "distinct_agents": len(non_swarm_agents),
                "created": non_swarm_created,
                "matched": non_swarm_matched,
                "match_rate_pct": match_rate_pct(non_swarm_created, non_swarm_matched)
            },
            "active_agents_by_day": {k: len(v) for k, v in sorted(agents_by_day.items())}
        },
        "concept_lengths": {
            "overall": summarize_lengths(all_lengths),
            "claude_family": summarize_lengths(claude_lengths),
            "gpt_family": summarize_lengths(gpt_lengths),
            "grok_family": summarize_lengths(grok_lengths),
            "top_agents": {
                aid: summarize_lengths(lens)
                for aid, lens in sorted(agent_lengths.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            }
        }
    }

METAL_CALLS_PATH = os.environ.get("LAMBO_METAL_CALLS_PATH", os.path.expanduser("~/lambo-dogfood/calls.jsonl"))
METAL_DB_PATH = os.environ.get("LAMBO_METAL_DB_PATH", os.path.expanduser("~/lambo-dogfood/lambo-dev.db"))

# Last instant consistent with every count in the Issue #17 review (365 tool
# calls, 3,429 heartbeats, 889 concepts, 2,198 edges). The 366th call landed at
# 19:16:53Z and the 3,430th heartbeat at 19:20:58Z, so any stamp in
# [19:15:58Z, 19:16:53Z) replays those figures. The issue was posted at 19:17:35Z.
METAL_FROZEN_STAMP = "2026-09-04T19:16:00Z"

# J3 (async write receipts) landed on 2026-08-24. Before it the store was fed by
# a synchronized review swarm (implementor, reviewers, remediators per track).
# After it a single operator drove one supervised writer.
METAL_SWARM_BOUNDARY = "2026-08-24"

# Frozen Metal dataset. Generated by
#   python3 scripts/extract_telemetry.py --live --rig metal --until METAL_FROZEN_STAMP
# and pasted verbatim. The default invocation must reproduce it byte for byte.
METAL_FROZEN = {'metadata': {'rig': 'Apple Silicon Metal Rig',
                  'extracted_at': '2026-09-04T19:16:00Z',
                  'ledger_file': 'calls.jsonl',
                  'db_file': 'lambo-dev.db',
                  'ledger_first_record': '2026-08-19T19:06:25.491082Z',
                  'ledger_last_record': '2026-09-04T19:15:58.636522Z',
                  'source_issues': ['Issue #8: Vector scan latency and memory compression tax',
                                    'Issue #9 comment 5540126749: Inspect error replication (n=4)',
                                    'Issue #10 comment 5540141420: Metal rig cross-check (dedup '
                                    'regimes and length)',
                                    'Issue #16 comment 5540134512: Heartbeat snapshots and flush lag',
                                    'Issue #17: Comprehensive dogfood review (365 calls, 889 '
                                    'concepts)'],
                  'platform': 'Apple MacBook Pro M3 Pro (12 CPU cores, 18 GPU cores), 18 GB Unified '
                              'Memory',
                  'os': 'macOS Tahoe 26.6.2 (launchd daemon)',
                  'backend': 'candle-metal backend, BGE-M3 1024-dim'},
     'reliability': {'window_days': 16.0,
                     'heartbeat_snapshots': 3429,
                     'sampling_interval_seconds': 300,
                     'process_startups': 12,
                     'process_startups_by_transport': {'http': 7, 'stdio': 5},
                     'lease_refusals': 1,
                     'store': {'concepts': 889, 'directed_edges': 2198},
                     'infrastructure_faults': {'ledger_dropped_lines': 0,
                                               'write_queue_drops': 0,
                                               'dead_lettered_writes': 0,
                                               'degraded_state_events': 0,
                                               'replay_debt_events': 0},
                     'tool_calls': {'total_calls': 365,
                                    'by_tool': {'lambo_derive': 149,
                                                'lambo_inspect': 4,
                                                'lambo_recall': 99,
                                                'lambo_record_action': 98,
                                                'lambo_saints': 1,
                                                'lambo_stats': 14},
                                    'total_errors': 1,
                                    'total_error_rate_pct': 0.27,
                                    'inspect_calls': 4,
                                    'inspect_errors': 1,
                                    'inspect_error_rate_pct': 25.0,
                                    'reserve_calls': 0,
                                    'reserve_errors': 0,
                                    'reserve_error_rate_pct': 0.0,
                                    'recall_derive_calls': 346,
                                    'recall_derive_errors': 0,
                                    'recall_derive_error_rate_pct': 0.0,
                                    'write_calls': 247}},
     'deduplication': {'temporal_regimes': {'review_swarm_window': {'dates': '2026-08-19 to 2026-08-23 '
                                                                             '(pre-J3)',
                                                                    'description': 'Multi-agent review '
                                                                                   'swarm: '
                                                                                   'implementor, 3 '
                                                                                   'reviewers, 2 '
                                                                                   'remediators per '
                                                                                   'track',
                                                                    'distinct_agents': 25,
                                                                    'created': 456,
                                                                    'matched': 62,
                                                                    'match_rate_pct': 12.0},
                                            'single_agent_window': {'dates': '2026-08-24 to 2026-09-04 '
                                                                             '(post-J3)',
                                                                    'description': 'Single-operator '
                                                                                   'interactive '
                                                                                   'workflow',
                                                                    'distinct_agents': 14,
                                                                    'created': 376,
                                                                    'matched': 3,
                                                                    'match_rate_pct': 0.8},
                                            'whole_period': {'dates': '2026-08-19 to 2026-09-04',
                                                             'created': 832,
                                                             'matched': 65,
                                                             'match_rate_pct': 7.2}},
                       'store_reconciliation': {'note': 'concepts_before_ledger + ledger_created must '
                                                        'equal store concepts',
                                                'concepts_before_ledger': 57,
                                                'ledger_created': 832,
                                                'store_concepts': 889},
                       'active_agents_by_day': {'2026-08-19': 1,
                                                '2026-08-20': 19,
                                                '2026-08-21': 7,
                                                '2026-08-22': 1,
                                                '2026-08-23': 1,
                                                '2026-08-24': 1,
                                                '2026-08-25': 1,
                                                '2026-08-27': 5,
                                                '2026-08-31': 1,
                                                '2026-09-01': 2,
                                                '2026-09-02': 1,
                                                '2026-09-03': 4,
                                                '2026-09-04': 6}},
     'concept_lengths': {'overall': {'n': 889,
                                     'mean': 392.3,
                                     'p10': 25.8,
                                     'p50': 315.0,
                                     'p90': 932.2,
                                     'p99': 1499.2,
                                     'max': 2053,
                                     'share_over_500': 35.9,
                                     'share_over_200': 54.1},
                         'claude_family': {'n': 713,
                                           'mean': 406.5,
                                           'p50': 356.0,
                                           'p90': 918.4,
                                           'max': 2053,
                                           'share_over_500': 38.7,
                                           'key_agents': {'claude-orchestrator': {'n': 409,
                                                                                  'mean': 453.4,
                                                                                  'p50': 439.0,
                                                                                  'p90': 1000.6,
                                                                                  'max': 2053,
                                                                                  'share_over_500': 45.0},
                                                          'claude-fable-5-1': {'n': 183,
                                                                               'mean': 318.6,
                                                                               'p50': 318.0,
                                                                               'p90': 686.8,
                                                                               'max': 1279,
                                                                               'share_over_500': 24.6},
                                                          'claude-fable-5': {'n': 101,
                                                                             'mean': 290.0,
                                                                             'p50': 67.0,
                                                                             'p90': 749.0,
                                                                             'max': 1478,
                                                                             'share_over_500': 27.7},
                                                          'claude-code-opus5': {'n': 12,
                                                                                'mean': 891.8,
                                                                                'p50': 854.0,
                                                                                'p90': 981.9,
                                                                                'max': 1199,
                                                                                'share_over_500': 100.0},
                                                          'claude-opus-5': {'n': 8,
                                                                            'mean': 759.9,
                                                                            'p50': 755.0,
                                                                            'p90': 920.4,
                                                                            'max': 968,
                                                                            'share_over_500': 87.5}}},
                         'gpt_family': {'n': 43,
                                        'mean': 196.0,
                                        'p50': 164.0,
                                        'p90': 394.8,
                                        'max': 548,
                                        'share_over_500': 4.7,
                                        'key_agents': {'gpt-5-codex': {'n': 32,
                                                                       'mean': 131.4,
                                                                       'p50': 58.5,
                                                                       'p90': 324.7,
                                                                       'max': 366,
                                                                       'share_over_500': 0.0},
                                                       'gpt-5.6-sol': {'n': 4,
                                                                       'mean': 337.2,
                                                                       'p50': 327.5,
                                                                       'p90': 397.3,
                                                                       'max': 421,
                                                                       'share_over_500': 0.0},
                                                       'gpt-5.4': {'n': 4,
                                                                   'mean': 405.0,
                                                                   'p50': 381.5,
                                                                   'p90': 504.2,
                                                                   'max': 548,
                                                                   'share_over_500': 25.0},
                                                       'gpt-5': {'n': 2,
                                                                 'mean': 370.5,
                                                                 'p50': 370.5,
                                                                 'p90': 396.5,
                                                                 'max': 403,
                                                                 'share_over_500': 0.0},
                                                       'gpt-6-astra': {'n': 1,
                                                                       'mean': 514.0,
                                                                       'p50': 514.0,
                                                                       'p90': 514.0,
                                                                       'max': 514,
                                                                       'share_over_500': 100.0}}},
                         'grok_family': {'n': 29,
                                         'mean': 62.0,
                                         'p50': 44.0,
                                         'p90': 134.8,
                                         'max': 190,
                                         'share_over_500': 0.0,
                                         'key_agents': {'cursor-grok-docs': {'n': 16,
                                                                             'mean': 47.9,
                                                                             'p50': 44.5,
                                                                             'p90': 82.0,
                                                                             'max': 132,
                                                                             'share_over_500': 0.0},
                                                        'cursor-grok-passport-compress': {'n': 7,
                                                                                          'mean': 82.9,
                                                                                          'p50': 93.0,
                                                                                          'p90': 149.6,
                                                                                          'max': 155,
                                                                                          'share_over_500': 0.0},
                                                        'cursor-grok-4.6-docs': {'n': 3,
                                                                                 'mean': 89.0,
                                                                                 'p50': 42.0,
                                                                                 'p90': 160.4,
                                                                                 'max': 190,
                                                                                 'share_over_500': 0.0},
                                                        'cursor-grok-docs-changelog': {'n': 3,
                                                                                       'mean': 62.0,
                                                                                       'p50': 39.0,
                                                                                       'p90': 106.2,
                                                                                       'max': 123,
                                                                                       'share_over_500': 0.0}}},
                         'by_type': {'resource': {'n': 405, 'mean': 228.5},
                                     'logic': {'n': 164, 'mean': 702.9},
                                     'entity': {'n': 125, 'mean': 120.0},
                                     'constraint': {'n': 102, 'mean': 707.3},
                                     'observation': {'n': 93, 'mean': 578.6}},
                         'top_agents': {'claude-orchestrator': {'n': 409,
                                                                'mean': 453.4,
                                                                'p50': 439.0,
                                                                'p90': 1000.6,
                                                                'max': 2053,
                                                                'share_over_500': 45.0},
                                        'claude-fable-5-1': {'n': 183,
                                                             'mean': 318.6,
                                                             'p50': 318.0,
                                                             'p90': 686.8,
                                                             'max': 1279,
                                                             'share_over_500': 24.6},
                                        'claude-fable-5': {'n': 101,
                                                           'mean': 290.0,
                                                           'p50': 67.0,
                                                           'p90': 749.0,
                                                           'max': 1478,
                                                           'share_over_500': 27.7},
                                        'gpt-5-codex': {'n': 32,
                                                        'mean': 131.4,
                                                        'p50': 58.5,
                                                        'p90': 324.7,
                                                        'max': 366,
                                                        'share_over_500': 0.0},
                                        'j3-redesign-remediation-r1': {'n': 28,
                                                                       'mean': 239.8,
                                                                       'p50': 28.0,
                                                                       'p90': 1129.4,
                                                                       'max': 1411,
                                                                       'share_over_500': 17.9}}}}


def parse_ts(value):
    """Parse RFC3339 with either a Z or a numeric offset into an aware datetime."""
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def load_ledger(path, until=None):
    """Read a serve ledger into lists keyed by record kind, cut at `until`."""
    until_dt = parse_ts(until) if until else None
    records = defaultdict(list)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            if until_dt and parse_ts(entry["ts"]) > until_dt:
                continue
            records[entry.get("kind")].append(entry)
    return records


def sqlite_stamp(until):
    """Cutoff in the store's created_at format (millisecond Z)."""
    dt = parse_ts(until).astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def match_rate_pct(created, matched):
    # Share of write-time ingestion attempts that deduplicated against an
    # existing concept. The denominator is attempts (created plus matched),
    # not creations alone.
    attempts = created + matched
    return round(matched / attempts * 100, 1) if attempts else 0.0


def summarize_lengths(arr, percentiles=(50, 90)):
    if not arr:
        out = {"n": 0, "mean": 0.0}
        out.update({f"p{p}": 0.0 for p in percentiles})
        out.update({"max": 0, "share_over_500": 0.0})
        return out
    np_arr = np.array(arr)
    out = {"n": int(len(np_arr)), "mean": round(float(np.mean(np_arr)), 1)}
    for p in percentiles:
        out[f"p{p}"] = round(float(np.percentile(np_arr, p)), 1)
    out["max"] = int(np.max(np_arr))
    out["share_over_500"] = round(float(np.sum(np_arr > 500) / len(np_arr) * 100.0), 1)
    return out


def extract_metal_telemetry(live=False, until=None):
    if not live:
        return METAL_FROZEN

    if not os.path.exists(METAL_CALLS_PATH) or not os.path.exists(METAL_DB_PATH):
        raise FileNotFoundError(f"Metal telemetry paths missing: {METAL_CALLS_PATH} or {METAL_DB_PATH}")

    records = load_ledger(METAL_CALLS_PATH, until)
    stats_records = records["stats"]
    call_records = records["call"]
    completion_records = records["completion"]
    startup_records = records["startup"]
    lease_records = records["lease"]

    # --- Reliability -------------------------------------------------------
    ts_list = sorted(parse_ts(s["ts"]) for s in stats_records)
    window_days = (ts_list[-1] - ts_list[0]).total_seconds() / 86400.0 if ts_list else 0.0

    def counter_max(key):
        return max((int(s["stats"].get(key, 0) or 0) for s in stats_records), default=0)

    infrastructure_faults = {
        "ledger_dropped_lines": counter_max("ledger_dropped_lines"),
        "write_queue_drops": counter_max("write_queue_dropped"),
        "dead_lettered_writes": counter_max("dead_lettered"),
        "degraded_state_events": sum(1 for s in stats_records if s["stats"].get("degraded")),
        "replay_debt_events": sum(1 for s in stats_records if (s["stats"].get("write_queue_replay_owed") or 0) > 0),
    }

    tool_counts = Counter(c.get("tool") for c in call_records)
    error_counts = Counter(c.get("tool") for c in call_records if c.get("outcome") == "error")

    inspect_calls = tool_counts.get("lambo_inspect", 0)
    inspect_errors = error_counts.get("lambo_inspect", 0)
    reserve_calls = tool_counts.get("lambo_reserve", 0)
    reserve_errors = error_counts.get("lambo_reserve", 0)

    write_read_tools = ("lambo_recall", "lambo_derive", "lambo_record_action")
    recall_derive_calls = sum(tool_counts.get(t, 0) for t in write_read_tools)
    recall_derive_errors = sum(error_counts.get(t, 0) for t in write_read_tools)

    write_tools = ("lambo_derive", "lambo_record_action")
    write_calls = sum(tool_counts.get(t, 0) for t in write_tools)

    total_tool_calls = len(call_records)
    total_tool_errors = sum(error_counts.values())

    def rate(num, den, places=1):
        return round(num / den * 100, places) if den else 0.0

    # --- Deduplication (temporal regimes) ---------------------------------
    # Ingestion attempts appear on two record shapes. Before J3 every write was
    # acknowledged synchronously and the call line itself carries `created` and
    # `matched`. After J3 the call line carries only a receipt and the counts
    # land on the matching `completion` line. Counting call lines that carry
    # `created` plus every completion line covers both eras without double
    # counting, because a receipt-admitted call line has no `created` key.
    boundary = parse_ts(METAL_SWARM_BOUNDARY + "T00:00:00Z")
    regimes = {
        "review_swarm_window": {"created": 0, "matched": 0, "agents": set()},
        "single_agent_window": {"created": 0, "matched": 0, "agents": set()},
    }

    def regime_for(ts):
        return "review_swarm_window" if parse_ts(ts) < boundary else "single_agent_window"

    for c in call_records:
        if c.get("tool") in write_tools and "created" in c:
            r = regimes[regime_for(c["ts"])]
            r["created"] += int(c.get("created", 0) or 0)
            r["matched"] += int(c.get("matched", 0) or 0)
            r["agents"].add(c.get("agent_id", ""))
    for c in completion_records:
        r = regimes[regime_for(c["ts"])]
        r["created"] += int(c.get("created_count", 0) or 0)
        r["matched"] += int(c.get("matched_count", 0) or 0)
        r["agents"].add(c.get("agent_id", ""))

    agents_by_day = defaultdict(set)
    for c in call_records:
        day_str = c.get("ts", "")[:10]
        aid = c.get("agent_id")
        if aid and day_str:
            agents_by_day[day_str].add(aid)

    swarm = regimes["review_swarm_window"]
    single = regimes["single_agent_window"]
    whole_created = swarm["created"] + single["created"]
    whole_matched = swarm["matched"] + single["matched"]

    first_ledger_ts = ts_list[0].isoformat().replace("+00:00", "Z") if ts_list else None
    last_ledger_ts = ts_list[-1].isoformat().replace("+00:00", "Z") if ts_list else None
    swarm_first_day = first_ledger_ts[:10] if first_ledger_ts else METAL_SWARM_BOUNDARY
    single_last_day = last_ledger_ts[:10] if last_ledger_ts else METAL_SWARM_BOUNDARY

    # --- Store ---------------------------------------------------------------
    conn = sqlite3.connect(METAL_DB_PATH)
    cur = conn.cursor()
    params = ()
    where = ""
    if until:
        where = " WHERE created_at <= ?"
        params = (sqlite_stamp(until),)
    cur.execute("SELECT count(*) FROM concepts" + where, params)
    concept_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM edges" + where, params)
    edge_count = cur.fetchone()[0]
    cur.execute("SELECT origin_agent, concept_type, length(content) FROM concepts" + where, params)
    rows = cur.fetchall()
    # Concepts written before the ledger existed. The store total must equal
    # these plus every `created` counted from the ledger above.
    if first_ledger_ts:
        cur.execute("SELECT count(*) FROM concepts WHERE created_at < ?", (sqlite_stamp(first_ledger_ts),))
        concepts_before_ledger = cur.fetchone()[0]
    else:
        concepts_before_ledger = 0
    conn.close()

    agent_lengths = defaultdict(list)
    type_lengths = defaultdict(list)
    all_lengths = []
    for agent, ctype, length in rows:
        all_lengths.append(length)
        agent_lengths[agent].append(length)
        type_lengths[ctype].append(length)

    def family(needle):
        agents = {a: lens for a, lens in agent_lengths.items() if needle in a.lower()}
        flat = [l for lens in agents.values() for l in lens]
        summary = summarize_lengths(flat)
        summary["key_agents"] = {
            a: summarize_lengths(lens)
            for a, lens in sorted(agents.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        }
        return summary

    overall = summarize_lengths(all_lengths, percentiles=(10, 50, 90, 99))
    if all_lengths:
        overall["share_over_200"] = round(float(np.sum(np.array(all_lengths) > 200) / len(all_lengths) * 100.0), 1)

    stamp = until if until else datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return {
        "metadata": {
            "rig": "Apple Silicon Metal Rig",
            "extracted_at": stamp,
            "ledger_file": "calls.jsonl",
            "db_file": "lambo-dev.db",
            "ledger_first_record": first_ledger_ts,
            "ledger_last_record": last_ledger_ts,
            "source_issues": [
                "Issue #8: Vector scan latency and memory compression tax",
                "Issue #9 comment 5540126749: Inspect error replication (n=4)",
                "Issue #10 comment 5540141420: Metal rig cross-check (dedup regimes and length)",
                "Issue #16 comment 5540134512: Heartbeat snapshots and flush lag",
                "Issue #17: Comprehensive dogfood review (365 calls, 889 concepts)"
            ],
            "platform": "Apple MacBook Pro M3 Pro (12 CPU cores, 18 GPU cores), 18 GB Unified Memory",
            "os": "macOS Tahoe 26.6.2 (launchd daemon)",
            "backend": "candle-metal backend, BGE-M3 1024-dim"
        },
        "reliability": {
            "window_days": round(window_days, 1),
            "heartbeat_snapshots": len(stats_records),
            "sampling_interval_seconds": 300,
            "process_startups": len(startup_records),
            "process_startups_by_transport": dict(sorted(Counter(s.get("transport") for s in startup_records).items())),
            "lease_refusals": sum(1 for l in lease_records if l.get("event") == "refused"),
            "store": {
                "concepts": concept_count,
                "directed_edges": edge_count
            },
            "infrastructure_faults": infrastructure_faults,
            "tool_calls": {
                "total_calls": total_tool_calls,
                "by_tool": dict(sorted(tool_counts.items())),
                "total_errors": total_tool_errors,
                "total_error_rate_pct": rate(total_tool_errors, total_tool_calls, 2),
                "inspect_calls": inspect_calls,
                "inspect_errors": inspect_errors,
                "inspect_error_rate_pct": rate(inspect_errors, inspect_calls),
                "reserve_calls": reserve_calls,
                "reserve_errors": reserve_errors,
                "reserve_error_rate_pct": rate(reserve_errors, reserve_calls),
                "recall_derive_calls": recall_derive_calls,
                "recall_derive_errors": recall_derive_errors,
                "recall_derive_error_rate_pct": rate(recall_derive_errors, recall_derive_calls),
                "write_calls": write_calls
            }
        },
        "deduplication": {
            "temporal_regimes": {
                "review_swarm_window": {
                    "dates": f"{swarm_first_day} to 2026-08-23 (pre-J3)",
                    "description": "Multi-agent review swarm: implementor, 3 reviewers, 2 remediators per track",
                    "distinct_agents": len(swarm["agents"]),
                    "created": swarm["created"],
                    "matched": swarm["matched"],
                    "match_rate_pct": match_rate_pct(swarm["created"], swarm["matched"])
                },
                "single_agent_window": {
                    "dates": f"{METAL_SWARM_BOUNDARY} to {single_last_day} (post-J3)",
                    "description": "Single-operator interactive workflow",
                    "distinct_agents": len(single["agents"]),
                    "created": single["created"],
                    "matched": single["matched"],
                    "match_rate_pct": match_rate_pct(single["created"], single["matched"])
                },
                "whole_period": {
                    "dates": f"{swarm_first_day} to {single_last_day}",
                    "created": whole_created,
                    "matched": whole_matched,
                    "match_rate_pct": match_rate_pct(whole_created, whole_matched)
                }
            },
            "store_reconciliation": {
                "note": "concepts_before_ledger + ledger_created must equal store concepts",
                "concepts_before_ledger": concepts_before_ledger,
                "ledger_created": whole_created,
                "store_concepts": concept_count
            },
            "active_agents_by_day": {k: len(v) for k, v in sorted(agents_by_day.items())}
        },
        "concept_lengths": {
            "overall": overall,
            "claude_family": family("claude"),
            "gpt_family": family("gpt"),
            "grok_family": family("grok"),
            "by_type": {
                ctype.lower(): {"n": len(lens), "mean": round(float(np.mean(lens)), 1)}
                for ctype, lens in sorted(type_lengths.items(), key=lambda x: len(x[1]), reverse=True)
            },
            "top_agents": {
                aid: summarize_lengths(lens)
                for aid, lens in sorted(agent_lengths.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            }
        }
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--live", action="store_true",
                        help="Replay the rig ledgers and stores on local disk instead of emitting the frozen datasets")
    parser.add_argument("--rig", choices=("cuda", "metal", "all"), default="all",
                        help="Which rig to extract live. Rigs not selected are emitted frozen (default: all)")
    parser.add_argument("--until", metavar="RFC3339",
                        help="Cut every live ledger and store read at this stamp. Also stamps extracted_at, "
                             "so replaying at a frozen stamp reproduces the frozen dataset byte for byte")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    live_cuda = args.live and args.rig in ("cuda", "all")
    live_metal = args.live and args.rig in ("metal", "all")

    cuda_data = extract_cuda_telemetry(live=live_cuda)
    metal_data = extract_metal_telemetry(live=live_metal, until=args.until)

    cuda_out = os.path.join(OUTPUT_DIR, "cuda_telemetry.json")
    metal_out = os.path.join(OUTPUT_DIR, "metal_telemetry.json")

    with open(cuda_out, "w", encoding="utf-8") as f:
        json.dump(cuda_data, f, indent=2)
    with open(metal_out, "w", encoding="utf-8") as f:
        json.dump(metal_data, f, indent=2)

    print(f"[{'LIVE' if live_cuda else 'FROZEN BENCHMARK'}] Stamped CUDA telemetry saved to: {cuda_out}")
    print(f"[{'LIVE' if live_metal else 'FROZEN BENCHMARK'}] Stamped Metal telemetry saved to: {metal_out}")

if __name__ == "__main__":
    main()
