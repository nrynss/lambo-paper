#!/usr/bin/env python3
"""
Automated verification script for Lambo research paper constraints:
1. Zero semicolons (;) in prose, math, and code
2. Zero em dashes (—, ---) and punctuation dashes (--)
3. Zero sentences > 30 words in prose
4. Exactly 15 bibliography entries, unique keys, and resolved LaTeX citations
   (bibliographic accuracy and publication status require primary-source review)
5. Zero unscrubbed local user paths (/home/) in public data and web docs
6. Zero stale or conflated figures (e.g. 2,486 snapshots, 524 tool calls)
7. Within-file arithmetic consistency of data/*.json (counts sum, rates recompute)
8. Mechanically verified figure consistency across:
   - data/cuda_telemetry.json
   - data/metal_telemetry.json
   - src/main.tex
   - site/src/content/docs/*.mdx
9. Paired-comparison headline figures reconciled against the published run
   artifacts in evaluation/results/2026-09-07/ rather than retyped
"""

import re
import os
import sys
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
DATA_DIR = os.path.join(ROOT_DIR, "data")
SITE_DOCS_DIR = os.path.join(ROOT_DIR, "site", "src", "content", "docs")

TEX_FILE = os.path.join(SRC_DIR, "main.tex")
BIB_FILE = os.path.join(SRC_DIR, "references.bib")
CUDA_DATA_FILE = os.path.join(DATA_DIR, "cuda_telemetry.json")
METAL_DATA_FILE = os.path.join(DATA_DIR, "metal_telemetry.json")

RESULTS_DIR = os.path.join(ROOT_DIR, "evaluation", "results", "2026-09-07")
PAIRED_RUNS = ("lambo-2026-09-07", "vimanam-2026-09-07")


def verify_paired_comparison(tex_text, eval_mdx_text, telem_mdx_text):
    """Derive the paired-comparison headline tokens from the published run
    artifacts, then require the manuscript and the web edition to state them.

    The scores, the graded-answer count, and the coverage depths are read out
    of evaluation/results/2026-09-07/ so a retyped figure in prose cannot drift
    away from the data it claims to summarize.
    """
    problems = []
    if not os.path.isdir(RESULTS_DIR):
        return [f"Published results directory missing: {RESULTS_DIR}"]

    tokens = {}

    # Per-run totals from each run's generated report.
    for run in PAIRED_RUNS:
        report = os.path.join(RESULTS_DIR, run, "run-1", "report.md")
        if not os.path.exists(report):
            problems.append(f"Missing run report: {report}")
            continue
        with open(report, "r", encoding="utf-8") as f:
            text = f.read()
        m = re.search(r"File:\s*(\d+)/(\d+)\s*;\s*Lambo:\s*(\d+)/(\d+)", text)
        if not m:
            problems.append(f"Cannot read paired totals from {report}")
            continue
        short = run.split("-")[0]
        tokens[f"{short} file total"] = f"{m.group(1)}/{m.group(2)}"
        tokens[f"{short} Lambo total"] = f"{m.group(3)}/{m.group(4)}"

    # Graded answers actually present, across both runs. run-1/grading.json is
    # the blank sheet handed to the grader; grader/grading.json is its return.
    graded = 0
    for run in PAIRED_RUNS:
        grading = os.path.join(RESULTS_DIR, run, "grader", "grading.json")
        if not os.path.exists(grading):
            problems.append(f"Missing graded file: {grading}")
            continue
        with open(grading, "r", encoding="utf-8") as f:
            rows = json.load(f)
        graded += len(rows)
        ungraded = [r["answer_id"] for r in rows if r.get("score") is None]
        if ungraded:
            problems.append(f"{grading}: {len(ungraded)} answers still ungraded")
            continue
        # The report totals must equal the grader's own arm sums.
        with open(os.path.join(RESULTS_DIR, run, "bundle", "bundle.json"),
                  "r", encoding="utf-8") as f:
            arms = {j["answer_id"]: j["arm"] for j in json.load(f)["jobs"]}
        sums = {"file": 0, "lambo": 0}
        for r in rows:
            arm = arms.get(r["answer_id"])
            if arm in sums:
                sums[arm] += int(r["score"])
        short = run.split("-")[0]
        for arm, label in (("file", "file"), ("lambo", "Lambo")):
            key = f"{short} {label} total"
            if key in tokens and tokens[key].split("/")[0] != str(sums[arm]):
                problems.append(
                    f"{run}: report states {tokens[key]} for the {label} arm, "
                    f"grader scores sum to {sums[arm]}")
    if graded:
        tokens["graded answer count"] = f"{graded} answers"

    # Coverage depths from the layered efficacy readout.
    efficacy = os.path.join(RESULTS_DIR, "efficacy.md")
    if not os.path.exists(efficacy):
        problems.append(f"Missing layered readout: {efficacy}")
    else:
        with open(efficacy, "r", encoding="utf-8") as f:
            text = f.read()
        for depth, label in (("20", "deep"), ("3", "shallow")):
            m = re.search(r"@%s\s+(\d+)/(\d+)" % depth, text)
            if not m:
                problems.append(f"Cannot read covered@{depth} from {efficacy}")
                continue
            tokens[f"coverage at depth {depth} ({label})"] = f"{m.group(1)} of {m.group(2)}"

    corpora = (
        ("src/main.tex", tex_text),
        ("site/src/content/docs/05-evaluation.mdx", eval_mdx_text),
        ("site/src/content/docs/telemetry-data.mdx", telem_mdx_text),
    )
    for name, token in sorted(tokens.items()):
        for path, text in corpora:
            if token not in text:
                problems.append(f"{name}: expected '{token}' in {path}")
    return problems

def verify():
    failed = False

    with open(TEX_FILE, "r", encoding="utf-8") as f:
        tex_text = f.read()

    # 1. Semicolons
    semicolons = []
    for i, line in enumerate(tex_text.splitlines(), 1):
        if ";" in line:
            semicolons.append((i, line))
    if semicolons:
        print(f"[FAIL] Found {len(semicolons)} semicolons in {TEX_FILE}:")
        for line_no, content in semicolons:
            print(f"  Line {line_no}: {content}")
        failed = True
    else:
        print("[PASS] Zero semicolons found in LaTeX.")

    # 2. Em dashes
    em_dashes = []
    for i, line in enumerate(tex_text.splitlines(), 1):
        if "—" in line or "---" in line:
            em_dashes.append((i, line))
    if em_dashes:
        print(f"[FAIL] Found {len(em_dashes)} em dashes in {TEX_FILE}:")
        for line_no, content in em_dashes:
            print(f"  Line {line_no}: {content}")
        failed = True
    else:
        print("[PASS] Zero em dashes found in LaTeX.")

    # 3. Punctuation dashes
    punct_dashes = []
    for i, line in enumerate(tex_text.splitlines(), 1):
        if re.search(r"\s--\s", line):
            punct_dashes.append((i, line))
    if punct_dashes:
        print(f"[FAIL] Found {len(punct_dashes)} punctuation dashes in {TEX_FILE}:")
        for line_no, content in punct_dashes:
            print(f"  Line {line_no}: {content}")
        failed = True
    else:
        print("[PASS] Zero punctuation double-dashes found.")

    # 4. Citations in references.bib
    with open(BIB_FILE, "r", encoding="utf-8") as f:
        bib = f.read()
    entries = re.findall(r"@\w+\{([^,]+),", bib)
    if len(entries) != 15:
        print(f"[FAIL] Found {len(entries)} citations in bibtex (expected 15): {entries}")
        failed = True
    else:
        print(f"[PASS] Exactly 15 citations found: {entries}")

    cited = {
        key.strip()
        for group in re.findall(r"\\cite(?:\[[^\]]*\])*\{([^}]+)\}", tex_text)
        for key in group.split(",")
    }
    duplicate_keys = sorted({key for key in entries if entries.count(key) > 1})
    missing_keys = sorted(cited - set(entries))
    unused_keys = sorted(set(entries) - cited)
    if duplicate_keys or missing_keys or unused_keys:
        print(f"[FAIL] Duplicate bibliography keys: {duplicate_keys}; unresolved citations: {missing_keys}; uncited entries: {unused_keys}")
        failed = True
    else:
        print("[PASS] Bibliography keys are unique and all LaTeX citations resolve.")
    print("[NOTE] Citation metadata, publication status, and scientific claims require source review.")

    with open(os.path.join(SITE_DOCS_DIR, "08-references.mdx"), encoding="utf-8") as f:
        web_bib_blocks = re.findall(r"```bibtex\s*\n(.*?)\n```", f.read(), re.DOTALL)
    if len(web_bib_blocks) != 1 or web_bib_blocks[0].strip() != bib.strip():
        print("[FAIL] Web bibliography must contain one BibTeX block matching src/references.bib.")
        failed = True
    else:
        print("[PASS] Web and manuscript bibliography sources match.")

    # 5. Sentence lengths in prose
    lines = [l for l in tex_text.splitlines() if not l.strip().startswith("%")]
    content = "\n".join(lines)

    envs = ["equation", r"equation\*", "align", r"align\*", "tabular", r"tabular\*", "algorithm", "algorithmic", "tikzpicture"]
    for env in envs:
        content = re.sub(r"\\begin\{" + env + r"\}.*?\\end\{" + env + r"\}", " ", content, flags=re.DOTALL)

    content = re.sub(r"\\(sub)*section\*?\{[^}]*\}", " ", content)
    content = re.sub(r"\\caption\{([^}]*)\}", r"\1", content)
    content = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", content)
    content = re.sub(r"\$[^$]*\$", "MATH", content)

    paragraphs = content.split("\n\n")
    violating = []
    for p in paragraphs:
        p_clean = " ".join(p.split())
        sentences = re.split(r"(?<=[.!?])\s+", p_clean)
        for s in sentences:
            s = s.strip()
            if not s or s.startswith("\\"):
                continue
            words = s.split()
            if len(words) > 30:
                violating.append((len(words), s))

    if violating:
        print(f"[FAIL] Found {len(violating)} sentences exceeding 30 words:")
        for w, s in violating:
            print(f"  [{w} words]: {s}")
        failed = True
    else:
        print("[PASS] Zero sentences exceeding 30 words found.")

    # 6. Scrubbed paths check: no /home/ in data/*.json or site/src/content/docs/*.mdx
    path_violations = []
    for fpath in [CUDA_DATA_FILE, METAL_DATA_FILE]:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                c = f.read()
            if "/home/" in c:
                path_violations.append((fpath, "Contains /home/ path"))
    if os.path.exists(SITE_DOCS_DIR):
        for fname in os.listdir(SITE_DOCS_DIR):
            if fname.endswith(".mdx"):
                p = os.path.join(SITE_DOCS_DIR, fname)
                with open(p, "r", encoding="utf-8") as f:
                    c = f.read()
                if "/home/" in c:
                    path_violations.append((p, "Contains /home/ path"))
    if path_violations:
        print(f"[FAIL] Found {len(path_violations)} unscrubbed local paths:")
        for p, msg in path_violations:
            print(f"  {p}: {msg}")
        failed = True
    else:
        print("[PASS] Zero unscrubbed local user paths found.")

    # 7. Stale and Conflated Figures Ban
    stale_patterns = [
        (r"2[,.]?486", "Stale snapshot count 2,486 (reconciled figure is 2,495 CUDA / 3,429 Metal / 5,924 total)"),
        (r"2[,.]?494", "Stale snapshot count 2,494 (ledger replay at the frozen stamp gives 2,495)"),
        (r"5[,.]?923", "Stale combined snapshot count 5,923 (reconciled total is 5,924)"),
        (r"524\s+tool", "Stale uptime tool invocation count 524 (reconciled dataset has 1,020 calls)"),
        (r"1[,.]?018", "Stale CUDA tool call count 1,018 (by_tool replay sums to 1,020)"),
        (r"22\s*/\s*78", "Stale inspect denominator 78 (ledger replay at the frozen stamp gives 82)"),
        (r"28\.2", "Stale inspect miss rate 28.2% (recomputed as 26.8% on 22 / 82)"),
        (r"under\s+15\s*ms", "Unqualified vector scan claim 'under 15 ms' (measured 130.1 ms on CUDA, 71.0 ms on Metal)"),
        # Metal figures superseded by the ledger replay at METAL_FROZEN_STAMP (2026-09-04T19:16:00Z).
        (r"\b324\b\s*[&|]\s*3\b", "Stale Metal single-stream created count 324 (replay at the frozen stamp gives 376)"),
        (r"\b780\b\s*[&|]\s*65\b", "Stale Metal aggregate created count 780 (replay at the frozen stamp gives 832)"),
        (r"\b0\.9\\?%", "Stale Metal single-stream dedup rate 0.9% (recomputed as 0.8% on 3 / 379)"),
        (r"\b7\.7\\?%", "Stale Metal aggregate dedup rate 7.7% (recomputed as 7.2% on 65 / 897)"),
        (r"0\s*/\s*361", "Stale Metal recall/derive denominator 361 (recall + derive + record_action at the stamp is 346)"),
        (r"230\s+writes", "Stale Metal write count 230 (derive + record_action calls at the stamp is 247)"),
        (r"837\s+concepts\)", "Stale Metal store size 837 in the length table (store at the stamp holds 889 concepts)"),
        (r"macOS\s+15", "Stale Metal OS version macOS 15 (the rig ran macOS Tahoe 26.6 for the whole window)"),
    ]
    stale_found = []
    # Check in main.tex
    for pat, desc in stale_patterns:
        matches = re.findall(pat, tex_text, re.IGNORECASE)
        if matches:
            stale_found.append((TEX_FILE, desc, len(matches)))

    # Check in web docs
    if os.path.exists(SITE_DOCS_DIR):
        for fname in os.listdir(SITE_DOCS_DIR):
            if fname.endswith(".mdx"):
                p = os.path.join(SITE_DOCS_DIR, fname)
                with open(p, "r", encoding="utf-8") as f:
                    c = f.read()
                for pat, desc in stale_patterns:
                    matches = re.findall(pat, c, re.IGNORECASE)
                    if matches:
                        stale_found.append((p, desc, len(matches)))

    if stale_found:
        print(f"[FAIL] Found {len(stale_found)} occurrences of stale figures:")
        for p, desc, count in stale_found:
            print(f"  {os.path.basename(p)}: {desc} ({count} matches)")
        failed = True
    else:
        print("[PASS] Zero stale or conflated figures found.")

    # 7b. Figure Consistency between data/*.json, src/main.tex, and site/src/content/docs/
    if not os.path.exists(CUDA_DATA_FILE) or not os.path.exists(METAL_DATA_FILE):
        print(f"[FAIL] Telemetry JSON files missing: {CUDA_DATA_FILE} or {METAL_DATA_FILE}")
        failed = True
        return

    with open(CUDA_DATA_FILE, "r", encoding="utf-8") as f:
        cuda_data = json.load(f)
    with open(METAL_DATA_FILE, "r", encoding="utf-8") as f:
        metal_data = json.load(f)

    # 7. Within-file arithmetic: every count and rate in data/*.json must
    # reconcile against its own components. A figure can agree across all three
    # corpora and still be internally impossible, which is how a by_tool
    # breakdown summing to 1,016 sat under a total_calls of 1,018.
    arith = []

    def check_sum(label, parts, total):
        if sum(parts) != total:
            arith.append(f"{label}: components sum to {sum(parts)}, file states {total}")

    def check_rate(label, numerator, denominator, stated, places=1):
        expected = round(numerator / denominator * 100, places) if denominator else 0.0
        if abs(expected - stated) > 1e-9:
            arith.append(f"{label}: {numerator} / {denominator} recomputes to {expected}, file states {stated}")

    ctc = cuda_data["reliability"]["tool_calls"]
    by_tool = ctc["by_tool"]
    check_sum("CUDA by_tool vs total_calls", list(by_tool.values()), ctc["total_calls"])
    check_sum("CUDA inspect_calls vs by_tool", [by_tool["lambo_inspect"]], ctc["inspect_calls"])
    check_sum("CUDA reserve_calls vs by_tool", [by_tool["lambo_reserve"]], ctc["reserve_calls"])
    check_sum("CUDA recall_derive_calls vs by_tool",
              [by_tool["lambo_recall"], by_tool["lambo_derive"], by_tool["lambo_record_action"]],
              ctc["recall_derive_calls"])
    check_sum("CUDA total_errors vs components",
              [ctc["inspect_errors"], ctc["reserve_errors"], ctc["recall_derive_errors"]],
              ctc["total_errors"])
    check_rate("CUDA inspect error rate", ctc["inspect_errors"], ctc["inspect_calls"], ctc["inspect_error_rate_pct"])
    check_rate("CUDA reserve error rate", ctc["reserve_errors"], ctc["reserve_calls"], ctc["reserve_error_rate_pct"])
    check_rate("CUDA total error rate", ctc["total_errors"], ctc["total_calls"], ctc["total_error_rate_pct"], places=2)

    mtc = metal_data["reliability"]["tool_calls"]
    m_by_tool = mtc["by_tool"]
    check_sum("Metal by_tool vs total_calls", list(m_by_tool.values()), mtc["total_calls"])
    check_sum("Metal inspect_calls vs by_tool", [m_by_tool.get("lambo_inspect", 0)], mtc["inspect_calls"])
    check_sum("Metal reserve_calls vs by_tool", [m_by_tool.get("lambo_reserve", 0)], mtc["reserve_calls"])
    check_sum("Metal recall_derive_calls vs by_tool",
              [m_by_tool["lambo_recall"], m_by_tool["lambo_derive"], m_by_tool["lambo_record_action"]],
              mtc["recall_derive_calls"])
    check_sum("Metal write_calls vs by_tool",
              [m_by_tool["lambo_derive"], m_by_tool["lambo_record_action"]], mtc["write_calls"])
    check_sum("Metal total_errors vs components",
              [mtc["inspect_errors"], mtc["reserve_errors"], mtc["recall_derive_errors"]], mtc["total_errors"])
    check_rate("Metal inspect error rate", mtc["inspect_errors"], mtc["inspect_calls"], mtc["inspect_error_rate_pct"])
    check_rate("Metal reserve error rate", mtc["reserve_errors"], mtc["reserve_calls"], mtc["reserve_error_rate_pct"])
    check_rate("Metal recall/derive error rate", mtc["recall_derive_errors"], mtc["recall_derive_calls"],
               mtc["recall_derive_error_rate_pct"])
    check_rate("Metal total error rate", mtc["total_errors"], mtc["total_calls"], mtc["total_error_rate_pct"], places=2)

    # The store must equal the concepts written before the ledger existed plus
    # every creation the ledger recorded. This ties the dedup denominators to
    # the store row in the reliability table.
    mrec = metal_data["deduplication"]["store_reconciliation"]
    check_sum("Metal store reconciliation (pre-ledger + ledger created vs store)",
              [mrec["concepts_before_ledger"], mrec["ledger_created"]], mrec["store_concepts"])
    check_sum("Metal store_reconciliation vs reliability.store.concepts",
              [mrec["store_concepts"]], metal_data["reliability"]["store"]["concepts"])
    check_sum("Metal store_reconciliation ledger_created vs whole_period.created",
              [mrec["ledger_created"]], metal_data["deduplication"]["temporal_regimes"]["whole_period"]["created"])

    # Match rate denominator is ingestion attempts (created plus matched), not creations.
    def check_dedup(label, regime):
        check_rate(label, regime["matched"], regime["created"] + regime["matched"], regime["match_rate_pct"])

    cdd = cuda_data["deduplication"]
    check_sum("CUDA whole_rig created", [cdd["swarm_named"]["created"], cdd["non_swarm_named"]["created"]],
              cdd["whole_rig"]["created"])
    check_sum("CUDA whole_rig matched", [cdd["swarm_named"]["matched"], cdd["non_swarm_named"]["matched"]],
              cdd["whole_rig"]["matched"])
    for key in ("whole_rig", "swarm_named", "non_swarm_named"):
        check_dedup(f"CUDA {key} match rate", cdd[key])

    mdd = metal_data["deduplication"]["temporal_regimes"]
    check_sum("Metal whole_period created",
              [mdd["review_swarm_window"]["created"], mdd["single_agent_window"]["created"]],
              mdd["whole_period"]["created"])
    check_sum("Metal whole_period matched",
              [mdd["review_swarm_window"]["matched"], mdd["single_agent_window"]["matched"]],
              mdd["whole_period"]["matched"])
    for key in ("review_swarm_window", "single_agent_window", "whole_period"):
        check_dedup(f"Metal {key} match rate", mdd[key])

    if arith:
        print(f"[FAIL] Found {len(arith)} within-file arithmetic inconsistencies:")
        for msg in arith:
            print(f"  {msg}")
        failed = True
    else:
        print("[PASS] All within-file counts sum and all rates recompute in data/*.json.")

    # Read combined text for target corpora
    eval_mdx_file = os.path.join(SITE_DOCS_DIR, "05-evaluation.mdx")
    telemetry_mdx_file = os.path.join(SITE_DOCS_DIR, "telemetry-data.mdx")
    with open(eval_mdx_file, "r", encoding="utf-8") as f:
        eval_mdx_text = f.read()
    with open(telemetry_mdx_file, "r", encoding="utf-8") as f:
        telem_mdx_text = f.read()

    # Define authoritative figures to verify
    cuda_snap = cuda_data["reliability"]["heartbeat_snapshots"]
    metal_snap = metal_data["reliability"]["heartbeat_snapshots"]
    total_snap = cuda_snap + metal_snap

    cuda_calls = cuda_data["reliability"]["tool_calls"]["total_calls"]
    metal_calls = metal_data["reliability"]["tool_calls"]["total_calls"]

    cuda_inspect_miss_pct = cuda_data["reliability"]["tool_calls"]["inspect_error_rate_pct"]
    metal_inspect_miss_pct = metal_data["reliability"]["tool_calls"]["inspect_error_rate_pct"]

    metal_swarm_dedup = metal_data["deduplication"]["temporal_regimes"]["review_swarm_window"]["match_rate_pct"]
    metal_single_dedup = metal_data["deduplication"]["temporal_regimes"]["single_agent_window"]["match_rate_pct"]
    metal_agg_dedup = metal_data["deduplication"]["temporal_regimes"]["whole_period"]["match_rate_pct"]
    metal_rd_calls = metal_data["reliability"]["tool_calls"]["recall_derive_calls"]
    metal_writes = metal_data["reliability"]["tool_calls"]["write_calls"]
    metal_concepts = metal_data["reliability"]["store"]["concepts"]
    metal_edges = metal_data["reliability"]["store"]["directed_edges"]

    cuda_swarm_dedup = cuda_data["deduplication"]["swarm_named"]["match_rate_pct"]
    cuda_non_swarm_dedup = cuda_data["deduplication"]["non_swarm_named"]["match_rate_pct"]
    cuda_agg_dedup = cuda_data["deduplication"]["whole_rig"]["match_rate_pct"]

    checks = [
        # (name, expected_token, present_in_tex, present_in_eval_mdx, present_in_telem_mdx)
        ("CUDA Heartbeat Snapshots", f"{cuda_snap:,}", True, True, True),
        ("Metal Heartbeat Snapshots", f"{metal_snap:,}", True, True, True),
        ("Combined Snapshots in Conclusion", f"{total_snap:,}", True, False, False),
        ("CUDA Total Tool Invocations", f"{cuda_calls:,}", True, True, True),
        ("Metal Total Tool Invocations", f"{metal_calls:,}", True, True, True),
        ("CUDA Inspect Miss Rate", f"{cuda_inspect_miss_pct:.1f}%", True, True, False),
        ("Metal Inspect Miss Rate", f"{metal_inspect_miss_pct:.1f}%", True, True, True),
        ("Metal Swarm Dedup Rate", f"{metal_swarm_dedup:.1f}%", True, True, True),
        ("Metal Single Stream Dedup Rate", f"{metal_single_dedup:.1f}%", True, True, True),
        ("Metal Aggregate Dedup Rate", f"{metal_agg_dedup:.1f}%", True, True, False),
        ("Metal Recall/Derive Denominator", f"0 / {metal_rd_calls:,}", True, True, False),
        ("Metal Write Calls", f"{metal_writes} writes", True, True, False),
        ("Metal Store Concepts", f"{metal_concepts:,}", True, True, True),
        ("Metal Store Edges", f"{metal_edges:,}", True, True, True),
        ("CUDA Swarm Dedup Rate", f"{cuda_swarm_dedup:.1f}%", True, True, False),
        ("CUDA Non-Swarm Dedup Rate", f"{cuda_non_swarm_dedup:.1f}%", True, True, False),
        ("CUDA Aggregate Dedup Rate", f"{cuda_agg_dedup:.1f}%", True, True, False),
        ("Hardware RAM 78 GB", "78 GB", True, True, True),
        ("Linux Kernel 7.2.2", "7.2.2", True, True, True),
    ]

    mismatches = []
    for name, token, req_tex, req_eval_mdx, req_telem_mdx in checks:
        tex_token = token.replace("%", r"\%")
        if req_tex and (tex_token not in tex_text and token not in tex_text):
            mismatches.append((name, f"Expected '{token}' (or '{tex_token}') in src/main.tex"))
        if req_eval_mdx and token not in eval_mdx_text:
            mismatches.append((name, f"Expected '{token}' in site/src/content/docs/05-evaluation.mdx"))
        if req_telem_mdx and token not in telem_mdx_text:
            mismatches.append((name, f"Expected '{token}' in site/src/content/docs/telemetry-data.mdx"))

    if mismatches:
        print(f"[FAIL] Found {len(mismatches)} figure consistency mismatches:")
        for name, err in mismatches:
            print(f"  {name}: {err}")
        failed = True
    else:
        print(f"[PASS] All {len(checks)} empirical figures reconcile across data/*.json, src/main.tex, and site/src/content/docs/.")

    # 8. Paired-comparison headline figures against the published run artifacts.
    paired = verify_paired_comparison(tex_text, eval_mdx_text, telem_mdx_text)
    if paired:
        print(f"[FAIL] Found {len(paired)} paired-comparison inconsistencies:")
        for msg in paired:
            print(f"  {msg}")
        failed = True
    else:
        print("[PASS] Paired-comparison headline figures reconcile with "
              "evaluation/results/2026-09-07/.")

    if failed:
        sys.exit(1)
    print("\nALL VERIFICATION CHECKS PASSED!")

if __name__ == "__main__":
    verify()
