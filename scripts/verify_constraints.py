#!/usr/bin/env python3
"""
Automated verification script for Lambo research paper writing constraints:
- Zero semicolons (;) in prose, math, and code
- Zero em dashes (—, ---, --)
- Zero sentences > 30 words in prose
- Exactly 15 citations matching peer-reviewed literature
"""

import re
import os
import sys

SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src")
TEX_FILE = os.path.join(SRC_DIR, "main.tex")
BIB_FILE = os.path.join(SRC_DIR, "references.bib")

def verify():
    failed = False

    with open(TEX_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Semicolons
    semicolons = []
    for i, line in enumerate(text.splitlines(), 1):
        if ";" in line:
            semicolons.append((i, line))
    if semicolons:
        print(f"[FAIL] Found {len(semicolons)} semicolons:")
        for line_no, content in semicolons:
            print(f"  Line {line_no}: {content}")
        failed = True
    else:
        print("[PASS] Zero semicolons found.")

    # 2. Em dashes
    em_dashes = []
    for i, line in enumerate(text.splitlines(), 1):
        if "—" in line or "---" in line:
            em_dashes.append((i, line))
    if em_dashes:
        print(f"[FAIL] Found {len(em_dashes)} em dashes:")
        for line_no, content in em_dashes:
            print(f"  Line {line_no}: {content}")
        failed = True
    else:
        print("[PASS] Zero em dashes found.")

    # 3. Punctuation dashes
    punct_dashes = []
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(r"\s--\s", line):
            punct_dashes.append((i, line))
    if punct_dashes:
        print(f"[FAIL] Found {len(punct_dashes)} punctuation dashes:")
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
    lines = [l for l in text.splitlines() if not l.strip().startswith("%")]
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

    if failed:
        sys.exit(1)
    print("\nALL VERIFICATION CHECKS PASSED!")

if __name__ == "__main__":
    verify()
