#!/usr/bin/env python3
"""Batch-test text-replacement variants of one function and print each diff.

usage: matching_notes/var.py src/path/file.c func_XXXXXXXX specfile [max_lines] [--keep]

specfile: variants separated by lines "=====". Each variant is one or more edits
separated by "-----" lines; each edit is  <old text>\n@@@\n<new text>.
Old text is searched for starting at the function's definition. The file is
restored after each variant unless --keep is given (then the last one stays).
The candidate C must already be spliced in place of the function's
`#pragma GLOBAL_ASM` line (this repo has no draft wrapper stage).
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(REPO, "matching_notes", "fd.sh")

f, func, spec = sys.argv[1:4]
lines = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "--keep" else "12"
path = os.path.join(REPO, f)
orig = open(path).read()
for vi, variant in enumerate(open(spec).read().split("=====\n")):
    if not variant.strip():
        continue
    s = orig
    ok = True
    for pair in variant.split("-----\n"):
        if not pair.strip():
            continue
        old, new = pair.split("@@@\n")
        j = s.find(old, s.index(func + "("))
        if j < 0:
            print("NOT FOUND:", old)
            ok = False
            break
        s = s[:j] + new + s[j + len(old):]
    if not ok:
        continue
    open(path, "w").write(s)
    os.utime(path, None)  # NFS: make the rewrite visible to make NOW
    obj = os.path.join("build", f[:-2] + ".o")  # relative: Makefile rules match relative targets
    if os.path.exists(os.path.join(REPO, obj)):
        os.remove(os.path.join(REPO, obj))  # NFS stale-object trap: never trust a cached .o
    print("=== variant", vi, variant.strip().splitlines()[0][:60], flush=True)
    # Full score: NO -s, uncapped. fd.sh's -s + 1000-line cap produced fantasy scores on
    # early-return/big functions (three documented incidents on 2026-10-17) - do not rank with them.
    env = dict(os.environ, PATH=f"{REPO}/.venv/bin:~/local/bin".replace("~", os.path.expanduser("~")) + ":/usr/local/bin:/usr/bin:/bin")
    make = subprocess.run(["make", obj, f"PYTHON={REPO}/.venv/bin/python3"], cwd=REPO, env=env,
                          capture_output=True, text=True)
    errs = [l for l in (make.stdout + make.stderr).splitlines() if "rror" in l and "cfe: Warning" not in l]
    if errs:
        print("BUILD ERROR:", errs[:2])
    else:
        d = subprocess.run([f"{REPO}/.venv/bin/python3", "-W", "ignore",
                            f"{REPO}/tools/asm-differ/diff.py", "-o", func, "--format", "plain",
                            "--max-lines", "30000"], cwd=REPO, capture_output=True, text=True)
        for l in d.stdout.splitlines():
            if "CURRENT" in l:
                print(l.strip())
    if "--keep" not in sys.argv:
        open(path, "w").write(orig)
