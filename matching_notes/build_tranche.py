#!/usr/bin/env python3
"""Build a smarter farm tranche from the sweep's B_farm band.

Selection: ascending sweep score (best odds first), validated (pragma still
present AND the nonmatchings .s exists), excluding farmed/adopted/matched
functions and any file another running job owns.

Tuning per function by instruction count (from the sweep):
  small  (< 60 insns):  1 worker x 4 copies  (per-copy ~80 it/s cap dominates)
  medium (60-150):      2 workers x 3 copies
  large  (> 150):        4 workers x 2 copies (compile-bound)

usage: .venv/bin/python3 build_tranche.py <min-score> <max-score> <count> [excl1 excl2 ...]
prints "func:src:W:C" specs, one per line.
"""
import re
import subprocess
import sys

MIN, MAX, COUNT = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
EXCLUDE = set(sys.argv[4:])

rows = []
with open("matching_notes/SWEEP_2026-10-19.tsv") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 6 or p[5] != "B_farm":
            continue
        score = int(p[4]) if p[4].isdigit() else 9999
        if not (MIN <= score <= MAX):
            continue
        rows.append((score, p[0], p[1], int(p[2])))

rows.sort()
out = []
for score, func, src, insns in rows:
    if len(out) >= COUNT:
        break
    if func in EXCLUDE:
        continue
    # slot validation: pragma present and .s exists
    grep = subprocess.run(
        ["grep", "-rls", 'GLOBAL_ASM("[^"]*%s.s"' % func, "src/"],
        capture_output=True, text=True,
    )
    if not grep.stdout.strip():
        continue
    # upstream-exclusion: if michiiik's master already matched this function
    # (pragma absent there), farming it only duplicates their work
    try:
        up = subprocess.run(
            ["git", "show", "origin/master:" + src],
            capture_output=True, text=True,
        )
        if up.returncode == 0 and ('%s.s"' % func) not in up.stdout:
            continue
    except Exception:
        pass
    find = subprocess.run(
        ["find", "asm/us/nonmatchings", "-name", func + ".s"],
        capture_output=True, text=True,
    )
    if not find.stdout.strip():
        continue
    if insns < 60:
        spec = f"{func}:{src}:1:4"
    elif insns <= 150:
        spec = f"{func}:{src}:2:3"
    else:
        spec = f"{func}:{src}:4:2"
    out.append(spec)

print("\n".join(out))
