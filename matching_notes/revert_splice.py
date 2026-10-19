#!/usr/bin/env python3
"""revert_splice.py <src-file> <func>

Undo a splice for <func>: remove the mkdraft marker block (try_candidate) OR the
verbatim spool body (splice_manual), restoring the GLOBAL_ASM pragma.
"""
import os
import re
import sys

src, func = sys.argv[1:3]
text = open(src).read()
rel = os.path.relpath(src, "src")
d = os.path.dirname(rel)
pragma = f'#pragma GLOBAL_ASM("asm/us/nonmatchings/{rel[:-2]}/{func}.s")'

marker = re.compile(
    r'/\* mkdraft:' + re.escape(func) + r' begin \*/.*?/\* mkdraft:' + re.escape(func) + r' end \*/\n?',
    re.S,
)
m = marker.search(text)
if m:
    open(src, "w").write(text[: m.start()] + pragma + "\n" + text[m.end():])
    print(f"reverted {func} (marker block) -> {pragma}")
    sys.exit(0)

spool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spool", f"{func}.c")
if not os.path.exists(spool):
    sys.exit(f"no marker and no spool for {func}")
body = open(spool).read().rstrip("\n")
j = text.find(body)
if j < 0:
    sys.exit(f"spool body for {func} not found in {src}")
open(src, "w").write(text[:j] + pragma + "\n" + text[j + len(body):].lstrip("\n"))
print(f"reverted {func} (spool body) -> {pragma}")
