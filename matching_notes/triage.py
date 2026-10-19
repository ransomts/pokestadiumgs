#!/usr/bin/env python3
"""triage.py: classify the D_structural bucket into routable work queues.

For every unmatched function with a sweep draft, fuse:
  - the sweep's score + instruction count,
  - a structural parse of the target .s (jump tables, data-symbol refs,
    call count, switch density, size),
  - the S1 twin list (matching_notes/CROSSPORT_2026-10-19.txt)

and emit one of:

  JTBL_BLOB      the .s references jtbl_ symbols not defined in its own
                 file -- the switch table lives in an asm data blob; the
                 match needs a datamig recipe (datamig.py class)
  OWN_JTBL       jtbls defined in the same .s: closeable by agents once the
                 rest of the body matches (m2c usually gets switches right)
  DATA_HEAVY     >= 6 distinct D_/jtbl_ symbol refs: struct/table access
                 heavy; needs retyping analysis (agents, ccs.py)
  CALL_HEAVY     call density high (>= 1 jal per 12 insns): mostly
                 orchestration; register allocation matters most (agents)
  BIG            > 300 instructions: needs long-form attention
  PLAIN          ordinary function: wave material
  M2C_FAIL       could not be drafted (separate list; check S1 twins)

Output: one line per function "FUNC\tCLASS\tscore\tdensity\tn_insns\tn_jt\tn_data\tn_calls"
plus a summary.

usage: .venv/bin/python3 matching_notes/triage.py [--bucket D_structural] [--max N]
"""
import argparse
import os
import re
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASM = os.path.join(REPO, "asm", "us", "nonmatchings")
SWEEP = os.path.join(REPO, "matching_notes", "SWEEP_2026-10-19.tsv")

INSN_RE = re.compile(r"/\*\s*[0-9A-F]{6,8}\s+[0-9A-F]{8}\s+([0-9A-F]{8})\s*\*/")
DLABEL_RE = re.compile(r"^dlabel\s+(\S+)")
GLABEL_RE = re.compile(r"^glabel\s+(\S+)")
JAL_RE = re.compile(r"\bjalr?\s")
HI_RE = re.compile(r"%hi\((\S+?)\)")
LO_RE = re.compile(r"%lo\((\S+?)\)")
JTBL_DEF_RE = re.compile(r"^jtbl_\S+")
BRANCH_TAB_RE = re.compile(r"\b(sll|sr)\s+\$at,\s*\$\w+,\s*2")
JR_V = re.compile(r"\bjr\s+\$(at|v0|v1|t[0-9])\b")


def find_asm(func):
    for d, _, files in os.walk(ASM):
        if func + ".s" in files:
            return os.path.join(d, func + ".s")
    return None


def analyze_s(path):
    n_insns = 0
    n_calls = 0
    jtbl_defs = set()
    sym_refs = set()
    jtbl_refs = set()
    jr_reg = 0
    shift_tab = 0
    with open(path) as fh:
        for line in fh:
            m = DLABEL_RE.match(line)
            if m:
                jtbl_defs.add(m.group(1))
                continue
            m = GLABEL_RE.match(line)
            if m:
                continue
            if INSN_RE.search(line):
                n_insns += 1
                if JAL_RE.search(line):
                    n_calls += 1
                if JR_V.search(line):
                    jr_reg += 1
                if BRANCH_TAB_RE.search(line):
                    shift_tab += 1
                for s in HI_RE.findall(line):
                    sym_refs.add(s)
                for s in LO_RE.findall(line):
                    sym_refs.add(s)
    for s in sym_refs:
        if s.startswith("jtbl_"):
            jtbl_refs.add(s)
    data_refs = {s for s in sym_refs if s.startswith(("D_", "jtbl_"))}
    return {
        "n_insns": n_insns,
        "n_calls": n_calls,
        "jtbl_defs": jtbl_defs,
        "jtbl_refs": jtbl_refs,
        "data_refs": data_refs,
        "jr_reg": jr_reg,
        "shift_tab": shift_tab,
    }


def classify(func, score, m2c_ok, st, twin):
    if not m2c_ok:
        return "M2C_FAIL"
    blob_jtbls = st["jtbl_refs"] - st["jtbl_defs"]
    if blob_jtbls and score > 400:
        return "JTBL_BLOB"
    if st["n_insns"] > 300:
        return "BIG"
    if len(st["data_refs"]) >= 6:
        return "DATA_HEAVY"
    if st["n_insns"] and st["n_calls"] / st["n_insns"] >= 0.085 and st["n_calls"] >= 4:
        return "CALL_HEAVY"
    if st["jtbl_defs"]:
        return "OWN_JTBL"
    return "PLAIN"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", default="D_structural")
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--twins", action="store_true", help="annotate S1 twins")
    args = ap.parse_args()

    twins = set()
    if args.twins:
        with open(os.path.join(REPO, "matching_notes",
                               "CROSSPORT_2026-10-19.txt")) as fh:
            for line in fh:
                m = re.match(r"^(func_\S+)\s+([0-9.]+)", line)
                if m:
                    twins.add(m.group(1))

    rows = []
    with open(SWEEP) as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 6 or p[5] != args.bucket:
                continue
            func, src, insns, m2c, score = p[0], p[1], p[2], p[3], p[4]
            path = find_asm(func)
            if not path:
                continue
            st = analyze_s(path)
            sc = int(score) if score.isdigit() else 0
            cls = classify(func, sc, m2c == "ok", st, func in twins)
            density = sc / st["n_insns"] if st["n_insns"] else 0
            twin_mark = " S1TWIN" if func in twins else ""
            rows.append((func, cls, sc, density, st["n_insns"],
                        len(st["jtbl_refs"] - st["jtbl_defs"]),
                        len(st["data_refs"]), st["n_calls"], twin_mark))
            if args.max and len(rows) >= args.max:
                break

    rows.sort(key=lambda r: (r[1], r[2]))
    for func, cls, sc, dens, ni, njt, nd, nc, tw in rows:
        print(f"{func}\t{cls}\tscore={sc}\tdens={dens:.1f}\tinsns={ni}"
              f"\tblob_jt={njt}\tdata={nd}\tcalls={nc}{tw}")
    print()
    c = Counter(r[1] for r in rows)
    for k in sorted(c, key=lambda k: -c[k]):
        print(f"{k:12s} {c[k]}")


if __name__ == "__main__":
    main()
