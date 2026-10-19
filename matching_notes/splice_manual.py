#!/usr/bin/env python3
"""splice_manual.py <src-file> <func> <candidate.c>

Replace the GLOBAL_ASM pragma line for <func> with the candidate file's ENTIRE
content (no single-function span limit — use for spools carrying trailing
padding functions / stubs). The candidate's own prologue (externs/typedefs)
goes where the pragma was.
"""
import re
import sys

src, func, cand = sys.argv[1:4]
text = open(src).read()
body = open(cand).read().rstrip("\n")
pat = re.compile(r'^#pragma GLOBAL_ASM\("[^"]*/' + re.escape(func) + r'\.s"\)\s*$', re.M)
m = pat.search(text)
if not m:
    sys.exit(f"pragma for {func} not found in {src}")
if "/* mkdraft:" in text[m.start():m.end()]:
    sys.exit(f"{src} already carries a splice marker for {func}")
open(src, "w").write(text[:m.start()] + body + text[m.end():])
print(f"spliced {func} into {src} ({len(body)} bytes, manual whole-file)")
