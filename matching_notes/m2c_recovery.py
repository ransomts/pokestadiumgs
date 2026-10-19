#!/usr/bin/env python3
"""m2c_recovery.py: attack the 342 m2c-fail functions.

Tier 1: S1 twin lookup -- a matched S1 function at high similarity means the
function should be PORTED (like waves 5-6), not decompiled from asm. Uses
the existing corpus index at the S1 repo.

Tier 2: m2c retry with alternate flag sets. Some functions fail on the
default invocation but draft under --no-casts or with a trimmed context.
Retries are scored with fd.sh; any score < the sweep's C_agent floor
(300) goes on the farm list.

usage: .venv/bin/python3 matching_notes/m2c_recovery.py [--limit N] [--phase twins|m2c]
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PY = os.path.join(REPO, ".venv/bin/python3")
S1 = os.path.join(os.path.dirname(REPO), "pokestadium")
S1_CORPUS = os.path.join(S1, "build", "corpus", "index.json")

FLAG_SETS = [
    [],
    ["--no-casts"],
    ["--no-andor"],
    ["--no-bitwise"],
]


def load_fails():
    fails = []
    with open(os.path.join(HERE, "SWEEP_2026-10-19.tsv")) as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 6 and p[5] == "D_structural" and p[3] == "fail":
                fails.append((p[0], p[1]))
    return fails


def twins(fails, limit):
    """look each fail up in the S1 corpus by instruction-sequence similarity"""
    if not os.path.exists(S1_CORPUS):
        sys.exit(f"no S1 corpus at {S1_CORPUS}")
    import json
    with open(S1_CORPUS) as fh:
        corpus = json.load(fh)
    # build a cheap hash of each S1 function's opcode stream
    print(f"# {len(corpus)} S1 functions indexed")
    out = []
    for func, src in fails[:limit]:
        spath = None
        for d, _, files in os.walk(os.path.join(REPO, "asm/us/nonmatchings")):
            if func + ".s" in files:
                spath = os.path.join(d, func + ".s")
                break
        if not spath:
            continue
        out.append((func, src, spath))
    print("# run crossport_join.py for real similarity scoring; this is the list:")
    for func, src, spath in out:
        print(f"{func}\t{src}")


def m2c_retry(fails, limit):
    from matching_notes.m2ctx import m2ctx  # noqa: F401 (not importable this way)
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--phase", default="list", choices=["list", "twins"])
    args = ap.parse_args()
    fails = load_fails()
    print(f"# {len(fails)} m2c-fail functions")
    if args.phase == "list":
        for func, src in fails[:args.limit]:
            print(f"{func}\t{src}")
    elif args.phase == "twins":
        twins(fails, args.limit)


if __name__ == "__main__":
    main()
