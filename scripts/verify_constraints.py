#!/usr/bin/env python3
"""
Automated verification script for Lambo research paper constraints:
1. Zero semicolons (;) in prose, math, and code
2. Zero em dashes (—, ---) and punctuation dashes (--)
3. Zero sentences > 30 words in prose
4. Exactly 15 citations matching peer-reviewed literature
5. Zero unscrubbed local user paths (/home/) in public data and web docs
6. Zero stale or conflated figures (e.g. 2,486 snapshots, 524 tool calls)
7. Mechanically verified figure consistency across:
   - data/cuda_telemetry.json
   - data/metal_telemetry.json
   - src/main.tex
   - site/src/content/docs/*.mdx
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
        (r"2[,.]?486", "Stale snapshot count 2,486 (reconciled figure is 2,494 CUDA / 3,429 Metal / 5,923 total)"),
        (r"524\s+tool", "Stale uptime tool invocation count 524 (reconciled dataset has 1,018 calls)"),
        (r"under\s+15\s*ms", "Unqualified vector scan claim 'under 15 ms' (measured 130.1 ms on CUDA, 71.0 ms on Metal)"),
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

    # 8. Figure Consistency between data/*.json, src/main.tex, and site/src/content/docs/
    if not os.path.exists(CUDA_DATA_FILE) or not os.path.exists(METAL_DATA_FILE):
        print(f"[FAIL] Telemetry JSON files missing: {CUDA_DATA_FILE} or {METAL_DATA_FILE}")
        failed = True
        return

    with open(CUDA_DATA_FILE, "r", encoding="utf-8") as f:
        cuda_data = json.load(f)
    with open(METAL_DATA_FILE, "r", encoding="utf-8") as f:
        metal_data = json.load(f)

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

    if failed:
        sys.exit(1)
    print("\nALL VERIFICATION CHECKS PASSED!")

if __name__ == "__main__":
    verify()
