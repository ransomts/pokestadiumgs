#!/usr/bin/env python3
"""adopt_wave.py: batch-integrate a set of spooled matches with ONE gate.

The manual wave loop is: for each spool { splice over pragma; apply the
meta's documented neighbor fixups; } then rm -r build/src; full make; on
failure bisect. This tool automates the splice+gate part:

  1. splice every named spool over its pragma (splice_manual semantics)
  2. attempt declfix on any compile failure (known mechanical classes)
  3. ONE full make (rm -r build/src first); print the gate result
  4. on ROM failure, bisect: restore half, regate, repeat (log the culprit)

Neighbor fixups that need judgment (extern retypes, K&R forms) are NOT
automated: declfix covers the mechanical ones; anything it cannot fix is
reported for hand surgery.

usage:
  .venv/bin/python3 matching_notes/adopt_wave.py <func1> [func2 ...]   # from spool names
  .venv/bin/python3 matching_notes/adopt_wave.py --from-spool-dir       # every *.meta
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PY = os.path.join(REPO, ".venv/bin/python3")
ROM_OK = "build/pokestadiumgs-us.z64: OK"
MAKE_ENV = dict(os.environ,
                PATH=os.path.join(REPO, ".venv/bin") + ":" + os.environ.get("PATH", ""))


def spool_meta(func):
    p = os.path.join(HERE, "spool", func + ".meta")
    if not os.path.exists(p):
        return None
    d = {}
    for line in open(p):
        if "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def splice(func):
    meta = spool_meta(func)
    if not meta:
        print(f"SKIP {func}: no meta")
        return False
    src = meta.get("file")
    cand = os.path.join(HERE, "spool", func + ".c")
    if not src or not os.path.exists(cand):
        print(f"SKIP {func}: no file= or spool .c")
        return False
    r = subprocess.run([PY, os.path.join(HERE, "splice_manual.py"),
                        src, func, cand], cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"SPLICE-FAIL {func}: {(r.stdout or r.stderr).strip()}")
        return False
    print(f"spliced {func}")
    return True


def declfix(func):
    r = subprocess.run([PY, os.path.join(HERE, "declfix.py"), func],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def gate():
    subprocess.run(["rm", "-r", os.path.join(REPO, "build/src")], cwd=REPO)
    r = subprocess.run(["make", "-j32", f"PYTHON={PY}"], cwd=REPO,
                       capture_output=True, text=True, env=MAKE_ENV, timeout=1800)
    out = r.stdout + r.stderr
    ok = ROM_OK in out
    return ok, out


def compile_check():
    """host cc syntax gate on the whole tree (fast pre-gate)"""
    r = subprocess.run(["make", "cc-check", f"PYTHON={PY}"], cwd=REPO,
                       capture_output=True, text=True, env=MAKE_ENV, timeout=900)
    return r.returncode == 0, r.stdout + r.stderr


def bisect(failed_funcs):
    """restore half the functions (via git checkout of their files is not
    safe with multiple funcs per file), so: restore via revert_splice when
    a spool copy exists; else git restore the file if it only carries this
    func's splice."""
    # Simplification: try removing one function at a time from the end.
    culprits = []
    active = list(failed_funcs)
    while active:
        trial = active[-1]
        r = subprocess.run([PY, os.path.join(HERE, "revert_splice.py"),
                            spool_meta(trial)["file"], trial],
                           cwd=REPO, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"Bisect: cannot revert {trial} cleanly: {r.stdout}")
            break
        print(f"bisect: reverted {trial}, regating...")
        ok, _ = gate()
        if ok:
            culprits.append(trial)
            break
        active.pop()
    return culprits


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == "--from-spool-dir":
        funcs = sorted(f[:-5] for f in os.listdir(os.path.join(HERE, "spool"))
                       if f.endswith(".meta"))
    else:
        funcs = argv
    if not funcs:
        sys.exit(__doc__)

    spliced = []
    for f in funcs:
        if splice(f):
            spliced.append(f)

    # fast pre-gate: find compile failures, declfix them
    cc_ok, cc_out = compile_check()
    if not cc_ok:
        print("cc-check failed; running declfix on spliced functions")
        for f in spliced:
            if not declfix(f):
                print(f"declfix stuck on {f} (hand surgery needed)")

    print(f"\n{len(spliced)} spliced; gating (one full make)...")
    ok, out = gate()
    if ok:
        print(ROM_OK)
        print("commit-ready:", " ".join(spliced))
    else:
        print("ROM FAILED; bisecting...")
        culprits = bisect(spliced)
        print("culprits:", culprits if culprits else "unknown (gate still red)")


if __name__ == "__main__":
    main()
