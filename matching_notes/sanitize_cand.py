#!/usr/bin/env python3
"""Sanitize a permuter candidate for splicing into a real src file.

Permuter candidates carry standalone prologues (basic-type typedefs that
clash with ultratypes.h, GBI struct typedefs that clash with gbi.h, decls
the file already provides in an incompatible spelling, trailing
C_FUNCTION_PADDING pragmas that the repo's asm-processor honors but the
permuter's harness ignored). This tool emits a splice-safe candidate:

- split at the target function's (last) definition,
- drop #define/#pragma/#include lines and basic-type typedefs,
- drop decls whose symbol the src file already declares BEFORE the splice
  point (the file's spelling is the codegen truth),
- drop everything after the function's final closing brace (trailing decls
  and C_FUNCTION_PADDING pragmas - only keep those if the target .s really
  carries trailing padding, which the integrator must verify by hand),
- keep novel externs, prototypes, and non-conflicting struct typedefs.

usage: .venv/bin/python3 matching_notes/sanitize_cand.py <func> <src-file> <candidate.c> <out.c>
"""
import re
import sys

func, src_path, cand_path, dst = sys.argv[1:5]
src = open(src_path).read()
cand = open(cand_path).read()

BASIC = {"u8", "s8", "u16", "s16", "u32", "s32", "u64", "s64", "f32", "f64"}

# standard gbi.h / ultralib / ultratypes typedefs: a real translation unit
# already has all of these; a candidate redeclaring any of them conflicts
LIB_TYPES = re.compile(
    r"^(?:G\w+|Tri|Vtx|Mtx|Gfx|Objs\w*|OS\w+|u?int\d+_t|size_t|NULL_ty)$"
)

def last_def(text, name):
    m = None
    for mm in re.finditer(
        r"^[ \t]*(?:[A-Za-z_][\w\s\*]*?)\b%s\s*\([^;{}]*\)\s*\{" % re.escape(name),
        text, re.M,
    ):
        m = mm
    return m

m = last_def(cand, func)
if m is None:
    sys.exit(f"no definition of {func} in candidate")
prologue, body = cand[: m.start()], cand[m.start():]

# cut everything after the function's final closing brace
end = body.rfind("\n}\n")
if end >= 0:
    body = body[: end + 3]

# statements in the prologue, keeping multi-line typedefs whole
stmts, cur, depth = [], [], 0
for line in prologue.splitlines():
    cur.append(line)
    depth += line.count("{") - line.count("}")
    if line.rstrip().endswith(";") and depth == 0:
        stmts.append("\n".join(cur))
        cur = []
if cur and any(l.strip() for l in cur):
    stmts.append("\n".join(cur))

def decl_symbols(chunk):
    names = set()
    for mm in re.finditer(r"^\s*extern\s[^;]+?\b(\w+)\s*(?:\(|\[|;)", chunk, re.M):
        names.add(mm.group(1))
    for mm in re.finditer(r"^[\w\s\*]+?\b(\w+)\s*\([^;{]*\)\s*;", chunk, re.M):
        names.add(mm.group(1))
    for mm in re.finditer(r"\}\s*(\w+)\s*;", chunk):
        names.add(mm.group(1))
    for mm in re.finditer(r"typedef\s[^;=]+?\b(\w+)\s*;", chunk):
        names.add(mm.group(1))
    return names

pragma = re.search(
    r'#pragma\s+GLOBAL_ASM\("[^"]*/%s\.s"\)' % re.escape(func), src
)
file_before = src[: pragma.start()] if pragma else src
file_syms = decl_symbols(file_before)

kept = []
for st in stmts:
    s = st.strip()
    if not s or s.startswith("#") or s.startswith("extern float sqrtf"):
        continue
    td = re.match(r"typedef\s[^;]*?\b(\w+)\s*;$", s.replace("\n", " "))
    if (td and (td.group(1) in BASIC or LIB_TYPES.match(td.group(1)))) or re.match(
        r"typedef\s+(?:unsigned|signed|short|long|char|int|float|double)\s", s
    ):
        continue
    syms = decl_symbols(st)
    td_name = re.search(r"\}\s*(\w+)\s*;\s*$", st.strip())
    if td_name and LIB_TYPES.match(td_name.group(1)):
        continue  # gbi/ultralib typedef block: headers provide these
    if syms and syms <= file_syms:
        continue
    kept.append(st)

out = ("\n".join(kept) + "\n\n" + body) if kept else body
open(dst, "w").write(out)
print(f"{func}: kept {len(kept)} prologue stmt(s), body {len(body.splitlines())} lines")
