#!/home/tsranso/Code/pokestadiumgs/.venv/bin/python3
"""Splice a candidate function over its GLOBAL_ASM pragma and score it (file restored unless --keep).

usage: .venv/bin/python3 matching_notes/try_candidate.py src/path/file.c func_XXXXXXXX path/to/candidate.c [--keep]

GS splice port of the Stadium 1 tool (which had no NON_MATCHING stage to rely on): the
candidate replaces the function's `#pragma GLOBAL_ASM(...)` line -- or a mkdraft splice
already sitting there -- using mkdraft.py's marker format, keeping the rest of the file
(including the surrounding `#ifdef VERSION_US ... #endif`) intact. The candidate may be a
full matching_notes/drafts/<func>.c file: its `// mkdraft:` header lines are dropped and
everything from the top of the file up to and including the function's closing brace is
spliced, but only if the part before the function is splice-safe (blank lines, //
comments, preprocessor directives, extern/prototype declarations); otherwise just the
function definition is spliced, as in S1. fd.sh then builds the one object and prints
the full uncapped diff;
the file is restored unless --keep. A 0 here is NOT a match: the full `make` must print
`build/pokestadiumgs-us.z64: OK`.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PY = os.path.join(REPO, ".venv", "bin", "python3")
sys.path.insert(0, HERE)
import mkdraft  # shared splice/restore helpers

if len(sys.argv) < 4:
    sys.exit(__doc__)
src, func, cand = sys.argv[1:4]
keep = "--keep" in sys.argv[4:]

path = os.path.join(REPO, src)
with open(path) as f:
    orig = f.read()
with open(cand) as f:
    c = f.read()

span = mkdraft.func_span(c, func)
if span is None:
    sys.exit("try_candidate: %s definition not found in %s" % (func, cand))
a, b = span
new_fn = c[a:b]

# carry the candidate's prologue (mkdraft M2C shim, externs, prototypes) when it is
# splice-safe, so drafts/<func>.c can be fed back in unchanged
head = []
head_ok = True
for line in c[:a].split("\n"):
    s = line.strip()
    if not s or s.startswith("//"):
        continue
    if s.startswith("#") or (s.endswith(";") and "=" not in s and not s.startswith(("{", "}"))):
        head.append(line)
    else:
        head_ok = False
        break
if head and head_ok:
    new_fn = "\n".join(head) + "\n\n" + new_fn
    print("try_candidate: carrying %d prologue line(s) from the candidate" % len(head))
elif not head_ok:
    print("try_candidate: candidate prologue is not splice-safe; splicing the function only")

new = mkdraft.splice(orig, func, new_fn)
if new is None:
    sys.exit("try_candidate: %s has no GLOBAL_ASM (and no mkdraft splice) for %s" % (src, func))
mkdraft.write_and_touch(path, new)
try:
    p = subprocess.run([mkdraft.FD, src, func, "40"], cwd=REPO)
    score = None
    last = "/tmp/fd_last_%s.txt" % func
    if os.path.exists(last):
        with open(last, errors="replace") as f:
            m = re.search(r"CURRENT \((\d+)", f.read())
        if m:
            score = int(m.group(1))
    if score is not None:
        print("try_candidate: score %d" % score)
    else:
        print("try_candidate: no score")
    sys.exit(0 if score is not None else 1)
finally:
    if not keep:
        mkdraft.write_and_touch(path, orig)
