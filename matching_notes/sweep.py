#!/tmp/opencode/sweep/.venv/bin/python3
"""Full m2c draft sweep for pokestadiumgs — runs against the isolated copy at
/tmp/opencode/sweep (never the real repo).

Per function: m2c (mkdraft flags) -> splice over pragma -> make the .o (fd.sh env)
-> asm-differ -o (plain, --max-lines 30000) -> parse CURRENT (N) -> restore src.
Functions are bucketed per owner FILE and processed serially inside a file;
files are processed in parallel across a worker pool.

Mirrors matching_notes/mkdraft.py (m2c flags, M2C macro shim, extern-fix retry,
missing_decls/ctx_decl) and matching_notes/fd.sh (rm -f .o, make env, diff.py
invocation, FULL uncapped score). Keep in sync with those tools.
"""
import argparse
import importlib.util
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

COPY = "/tmp/opencode/sweep"
SCRATCH = "/tmp/opencode/sweep_scratch"
PY = os.path.join(COPY, ".venv", "bin", "python3")
M2C = os.path.join(COPY, "tools", "mips_to_c", "m2c.py")
DIFF = ["tools/asm-differ/diff.py"]
PATHENV = (
    os.path.join(COPY, ".venv", "bin")
    + ":"
    + os.path.expanduser("~/local/bin")
    + ":/usr/local/bin:/usr/bin:/bin"
)

M2C_TIMEOUT = 30      # as instructed
MAKE_TIMEOUT = 90     # build+diff budget ~120s total
DIFF_TIMEOUT = 40

PRAGMA_RE = re.compile(r'#pragma\s+GLOBAL_ASM\("asm/us/nonmatchings/((?:[^"/]+/)+)([^"/]+)\.s"\)')
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
SCORE_RE = re.compile(r"CURRENT \((\d+)\)")

# ------------------------------------------------------------- ctx K&R sanitizer
# BUG 1 fix: src files contain genuine K&R definitions (e.g. src/14640.c's
# `s32 func_8001480C(arg0, arg1) s32 arg0; s32 *arg1; { ... }`) and untyped
# prototypes (`extern s32 f(arg0, arg1);`). m2ctx copies them into the ctx and
# m2c hard-rejects the whole ctx ("K&R-style function header is not
# supported"). Rewrite them into typed prototypes (decl list -> param types,
# `()` fallback) and drop the bodies; m2c only needs declarations.

KR_PARAM_RE = re.compile(r"^\s*(?:arg\d+|a[0-3])\s*$")
KR_HDR_RE = re.compile(r"^(\s*)((?:[A-Za-z_]\w*[\s\*]+)+)([A-Za-z_]\w*)\s*\(([^()]*)\)\s*(.*)$")
# a rettype may not end in a statement keyword (`return f(a, b);` would otherwise
# parse as rettype=return, name=f)
KR_BAD_RET = {"return", "goto", "break", "continue", "else", "case", "default",
              "sizeof", "if", "while", "for", "switch", "do", "typedef", "defined"}


def _split_top(s, sep=","):
    out, depth, cur = [], 0, []
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def _kr_params(plist):
    """param list is bare identifiers only (argN/a0-a3)? (i.e. K&R untyped)"""
    if not plist.strip():
        return False
    return all(KR_PARAM_RE.match(p) for p in _split_top(plist))


def _parse_decls(decl_text, names):
    """' s32 arg0; u8 *arg1;' -> {arg0:'s32', arg1:'u8 *'}; None if unparseable"""
    ty = {}
    for d in decl_text.replace(";", " ; ").split(";"):
        d = d.strip()
        if not d:
            continue
        m = re.match(r"^(.+?)\s*\b([A-Za-z_]\w*)$", d)
        if not m or m.group(2) not in names:
            return None
        ty[m.group(2)] = m.group(1).strip()
    return ty if set(ty) == set(names) else None


def _kr_proto(indent, rettype, name, pnames, ty):
    if ty is not None:
        args = ", ".join("%s %s" % (ty[p], p) for p in pnames)
    else:
        args = ""
    return "%s%s%s(%s);" % (indent, rettype, name, args)


def sanitize_ctx(text):
    """rewrite K&R-style function headers/prototypes in an m2c context so m2c
    accepts it: `ret f(arg0, arg1) decls;...{ body }` -> `ret f(t0 arg0, t1 arg1);`
    (multi-line K&R defs are consumed through their balanced braces)"""
    lines = text.split("\n")
    out = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        m = KR_HDR_RE.match(line)
        if not m or not _kr_params(m.group(4)) or m.group(2).split()[-1] in KR_BAD_RET:
            out.append(line)
            i += 1
            continue
        indent, rettype, name, params, rest = m.groups()
        pnames = [p.strip() for p in _split_top(params)]
        rest_s = rest.strip()
        if rest_s.endswith(";") and "{" not in rest_s and "}" not in rest_s:
            # untyped prototype: `extern s32 f(arg0, arg1);` -> drop arg names
            out.append("%s%s%s();" % (indent, rettype, name))
            i += 1
            continue
        if "{" in rest_s:
            # one-liner K&R definition (decls + body on the header line)
            decl_part = rest_s.split("{", 1)[0]
            out.append(_kr_proto(indent, rettype, name, pnames, _parse_decls(decl_part, pnames)))
            bal = line.count("{") - line.count("}")
            i += 1
            while bal > 0 and i < n:  # body spilled onto following lines
                bal += lines[i].count("{") - lines[i].count("}")
                i += 1
            continue
        if rest_s == "":
            # multi-line K&R: header line, decl lines, then `{` body
            j, decls = i + 1, []
            while j < n and j <= i + 60:
                s = lines[j].strip()
                if s.startswith("{"):
                    break
                if s.endswith(";") and "{" not in s and "}" not in s:
                    decls.append(s)
                    j += 1
                    continue
                j = -1
                break
            if 0 <= j < n and lines[j].strip().startswith("{"):
                out.append(_kr_proto(indent, rettype, name, pnames,
                                     _parse_decls(" ".join(decls), pnames)))
                bal = 0
                while j < n:
                    bal += lines[j].count("{") - lines[j].count("}")
                    j += 1
                    if bal <= 0:
                        break
                i = j
                continue
        out.append(line)  # unrecognized shape: leave untouched
        i += 1
    return "\n".join(out)

# ------------------------------------------------------------- draft emission fix
# BUG 2 fix (draft side): m2c --valid-syntax output needs four textual fixes to
# compile under IDO cfe (the only gate now that RUN_CC_CHECK=0 skips host gcc):
#   1. `void *` params/locals/M2C_FIELD types do pointer arithmetic -> cfe
#      "Unacceptable operand of '+'" (void is not an object type). u8 * compiles
#      to the same addu, and void** field types become u8**.
#   2. m2c reuses ctx struct-unknown typedef names (S1_unk_*) that may be defined
#      later in the file than the splice point -> replace with u8 *.
#   3. `*(M2C_FIELD(a, s32 *, off) + i)`: M2C_FIELD expands to an s32 lvalue, so
#      this is `*(int + int)` -- cfe "Dereferenced a non-pointer" (and a gcc hard
#      error). Wrap the operand in an (s32 *) cast; width follows m2c's IR typing.
#      m2c formats binary ops with surrounding spaces, so `*(` adjacent is always
#      a unary deref.
#   4. `p == &D_X` / `p != &D_X` against m2c's `extern M2C_UNK D_X;` (s32) is a
#      distinct-pointer-type comparison -> cfe "Unacceptable operand of == or !=";
#      cast the address to (u8 *).
FIELD_CALL = r"M2C_FIELD\((?:[^()]|\((?:[^()]|\([^()]*\))*\))*\)"
NEST = r"(?:[^;()]|\((?:[^;()]|\((?:[^;()]|\([^;()]*\))*\))*\))*"
UNARY_STAR = re.compile(r"\*\(\s*(" + FIELD_CALL + r"(?:\s*\+\s*" + NEST + r")?)\s*\)")
ADDR_CMP = re.compile(r"([=!]=)\s*&([A-Za-z_]\w*)(?![\w\[])")
# m2c's invented externs, e.g. `M2C_UNK func_X(s32, u8 *);   /* extern */`
M2C_EXTERN = re.compile(r"^([^\n;()]*?)\b([A-Za-z_]\w*)\s*\(([^()]*)\)\s*;\s*/\* extern \*/\s*$")


def fix_draft(out):
    """apply the emission fixes to an m2c draft"""
    out = re.sub(r"\bvoid \*", "u8 *", out)
    out = re.sub(r"\bS\d+_unk_\w+\s*\*+", "u8 *", out)
    if "M2C_FIELD(" in out:
        out = UNARY_STAR.sub(r"*(s32 *)(\1)", out)
    # locals/params by kind (m2c types here are u8/u16/u32/s8/... -- no 'us' forms)
    ITYPE = r"(?:(?:u|s)(?:8|16|32|64)|(?:unsigned[ \t]+|signed[ \t]+)?(?:char|short|int|long))"
    PTYPE = ITYPE[:-1] + r"|f32|f64|float|double)"
    ints = set(re.findall(r"^[ \t]+%s[ \t]+(\w+);[ \t]*$" % ITYPE, out, re.M))
    ptrs = set(re.findall(r"^[ \t]+%s[ \t]*\*+[ \t]*(\w+);[ \t]*$" % PTYPE, out, re.M))
    sig = re.search(r"\(([^()]*)\)\s*\{", out)
    if sig:
        for p in sig.group(1).split(","):
            toks = p.replace("*", " * ").split()
            if "*" in toks and toks[-1] != "*":
                ptrs.add(toks[-1])
            elif len(toks) == 2 and toks[0] != "void":
                ints.add(toks[-1])
    # int-typed locals used as pointer bases: `*(temp_s0 + x)` derefs an int
    # for cfe; cast to (s32 *) (width follows m2c's IR typing)
    if ints:
        alt = "|".join(sorted(re.escape(n) for n in ints))
        out = re.sub(r"\*\(\s*(" + alt + r")(\s*\+\s*" + NEST + r")?\s*\)",
                     r"*(s32 *)(\1\2)", out)
    # comparisons of a pointer with an int (load or int local): cast the pointer
    # side to u32 -- codegen-neutral, and cfe rejects distinct-type ==/!=
    # comparisons of a pointer with an int (deref-load or int local): cast the
    # pointer side to u32 -- codegen-neutral, and cfe rejects distinct-type ==/!=
    if ptrs:
        ialt = ("|" + "|".join(sorted(re.escape(n) for n in ints))) if ints else ""
        rhs = r"(?:(?:\(\*" + NEST + r"\)|" + FIELD_CALL + r")" + ialt + r")"
        for p in sorted(ptrs):
            out = re.sub(r"\b(" + p + r")\s*([=!]=)\s*(" + rhs +
                         r")(?=\s*(?:&&|\|\||[),;]))", r"((u32)\1\2\3)", out)
    # cfe rejects int+ptr (operand order) and ptr+ptr sums, which m2c emits when
    # a pointer-typed param's true use is an offset: swap / cast to u32
    if ints or ptrs:
        for x in sorted(ints):
            for y in sorted(ptrs):
                out = re.sub(r"\b(%s)\s*\+\s*(%s)\b" % (x, y), r"\2 + \1", out)
        for a in sorted(ptrs):
            out = re.sub(r"\)\s*\+\s*(%s)\b" % a, r")+ (u32)\1", out)
            for b in sorted(ptrs):
                if a != b:
                    out = re.sub(r"\b(%s)\s*\+\s*(%s)\b" % (a, b), r"\1 + (u32)\2", out)
    # `== &X` / `!= &X`: cast both sides to u32 (valid for int and any pointer
    # lhs; codegen-neutral, cfe rejects distinct-type ==/!=)
    out = re.sub(r"\b(\w+)\s*([=!]=)\s*&([A-Za-z_]\w*)(?![\w\[])",
                r"((u32)\1 \2 (u32)&\3)", out)
    return out


def drop_conflicting_externs(out, orig):
    """drop m2c's invented function externs for callees already referenced
    anywhere in the pristine file (call, declaration or stub -- whatever the
    file itself establishes wins; the invented prototype otherwise conflicts
    with it and IDO errors on the redeclaration)"""
    keep = []
    for line in out.split("\n"):
        mm = M2C_EXTERN.match(line)
        if mm and (mm.group(2) + "(") in orig:
            continue
        keep.append(line)
    return "\n".join(keep)


def callee_protos(body, head, tail, func):
    """prototypes for functions the draft calls that are first defined/declared
    LATER in the file: the draft's early call creates an implicit declaration
    that cfe then flags as a redeclaration when it meets the later prototyped
    definition. Returns declaration lines to prepend at the splice point"""
    protos, seen = [], set()
    for name in re.findall(r"\b([A-Za-z_]\w*)\s*\(", body):
        if name in seen or name == func or name in KR_BAD_RET or name.startswith("M2C_"):
            continue
        seen.add(name)
        if (name + "(") in head:
            continue  # the file already establishes it before the splice
        dm = re.search(r"^[ \t]*(?:extern[ \t]+)?((?:[A-Za-z_]\w*[ \t\*]+)+)%s\s*\(([^()]*)\)[ \t]*[;{]"
                       % re.escape(name), tail, re.M)
        if not dm or dm.group(1).split()[-1] in KR_BAD_RET:
            continue
        protos.append("%s%s(%s);" % (dm.group(1), name, dm.group(2)))
    return protos


def unprototype_decl(text, name):
    """turn a declaration of NAME in TEXT into an unprototyped one (same return
    type, `()` params): fixes cfe arg-count/type disagreements with draft calls
    while keeping return-type codegen. -> (text, changed?)"""
    rx = re.compile(r"^([ \t]*(?:extern[ \t]+)?(?:[A-Za-z_]\w*[ \t\*]+)+)%s\s*\([^()]*\)([ \t]*;[^\n]*)$"
                    % re.escape(name), re.M)
    m = rx.search(text)
    if not m:
        return text, False
    return rx.sub(lambda mm: mm.group(1) + name + "()" + mm.group(2), text, count=1), True


def arg_count_failures(mout):
    """callee names from cfe `number of arguments doesn't agree` /
    argument-vs-prototype errors (the line after the error shows the call)"""
    names = []
    lines = [ANSI.sub("", l) for l in mout.splitlines()]
    for i, l in enumerate(lines):
        if "number of arguments doesn't agree" in l or "of function prototype" in l:
            ctx = lines[i + 1] if i + 1 < len(lines) else ""
            names.extend(m.group(1) for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", ctx))
    return [n for n in dict.fromkeys(names)]


def fix_target_decls(spliced, func, proto):
    """make the file's own declarations of the target agree with the draft:
    replace pre-existing prototype/stub lines of FUNC with the draft's
    prototype (duplicate identical prototypes are legal), and inject it before
    FUNC's first reference when that reference is an unprototyped call"""
    if proto is None:
        return spliced
    decl_start = re.compile(r"^[ \t]*(?:extern[ \t]+)?((?:[A-Za-z_]\w*[ \t\*]+)+)%s\s*\(" % re.escape(func))
    ref_re = re.compile(r"\b%s\s*\(" % re.escape(func))
    out, have_decl = [], False
    for ln in spliced.split("\n"):
        dm = decl_start.match(ln)
        if dm and dm.group(1).split()[-1] not in KR_BAD_RET and \
                re.search(r"\([^()]*\)[ \t]*(;|\{[ \t]*\})[ \t]*$", ln):
            out.append(proto)          # prototype or one-line stub of FUNC
            have_decl = True
        elif not have_decl and ref_re.search(ln):
            # first reference is an unprototyped call: precede it with the
            # prototype at FILE scope (a block-scope prototype dies with the
            # enclosing `}`, and the next call would re-conflict with it)
            if ln[:1].isspace():
                j = len(out)
                while j > 0:
                    prev = out[j - 1]
                    if prev.strip() and not prev[:1].isspace():
                        break
                    j -= 1
                out.insert(j - 1 if j > 0 else 0, proto)
            else:
                out.append(proto)
            have_decl = True
            out.append(ln)
        else:
            out.append(ln)
    return "\n".join(out)

# ----------------------------------------------------------------- mkdraft mirrors
M2C_MACROS = """\
#ifndef M2C_FIELD /* sweep: m2c --valid-syntax helpers (mirrors mkdraft.py) */
#define M2C_UNK s32
#define M2C_UNK8 s8
#define M2C_UNK16 s16
#define M2C_UNK32 s32
#define M2C_UNK64 s64
#define M2C_FIELD(expr, type, offset) (*(type)((u8*)(expr) + (offset)))
#define M2C_BITWISE(type, expr) ((type)(expr))
#define M2C_ERROR(desc) 0
#define M2C_TRAP_IF(cond) ((void)0)
#define M2C_BREAK() ((void)0)
#define M2C_SYNC() ((void)0)
#define M2C_CARRY 0
#define M2C_STRUCT_COPY(dst, src) ((dst) = (src))
#endif
"""


def draft_body(code):
    code = code.replace("? ", "M2C_UNK ").replace("?*", "M2C_UNK*")
    if "M2C_" in code:
        return M2C_MACROS + "\n" + code
    return code


def missing_decls(fd_out):
    """identifiers reported undeclared/undefined by the host CC_CHECK or IDO cfe
    (mkdraft.py's helper, verbatim)"""
    ids = []
    for line in fd_out.splitlines():
        line = ANSI.sub("", line)
        if "ndeclared" not in line and "ndefined" not in line:
            continue
        line = line.split("did you mean")[0]
        for m in re.finditer(r"['\u2018\u2019]([A-Za-z_]\w*)['\u2018\u2019]", line):
            ids.append(m.group(1))
        for m in re.finditer(r"\bidentifier\s+['\"]?([A-Za-z_]\w*)['\"]?\s+(?:is\s+)?undefined", line):
            ids.append(m.group(1))
    return [i for i in dict.fromkeys(ids)]


def ctx_decl(name, ctx_text):
    """NAME's declaration from the ctx (mkdraft.py's helper, ctx text passed in).
    The no-extern fallback must keep functions functions: `extern s32 f;` for a
    called f is a variable redeclaration and kills the build under IDO"""
    for line in ctx_text.splitlines():
        s = ANSI.sub("", line)
        s = re.sub(r"/\*.*?\*/\s*$", "", s.split("//")[0]).strip()
        if s.startswith("extern") and s.endswith(";") and "{" not in s and \
                re.search(r"\b%s\b" % re.escape(name), s):
            return s
    if re.search(r"\b%s\s*\(" % re.escape(name), ctx_text):
        return "extern s32 %s(); /* sweep stub: no extern for it in ctx -- check the type */" % name
    return "extern s32 %s; /* sweep stub: no extern for it in ctx -- check the type */" % name


# ----------------------------------------------------------------- m2ctx (imported from the copy)
_spec = importlib.util.spec_from_file_location("m2ctx_sweep", os.path.join(COPY, "matching_notes", "m2ctx.py"))
m2ctx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m2ctx)   # root_dir == COPY

_ctx_cache = {}
_ctx_lock = threading.Lock()


def gen_ctx(src):
    """ctx text for a src file, generated once (file is clean at call time)"""
    with _ctx_lock:
        if src in _ctx_cache:
            return _ctx_cache[src]
    abspath = os.path.join(COPY, src)
    try:
        text = m2ctx.import_c_file(abspath)
        ok = bool(text)
    except SystemExit:
        text, ok = None, False
    except Exception:
        text, ok = None, False
    if ok:
        try:
            text = sanitize_ctx(text)
        except Exception as e:  # sanitizer bug: keep unsanitized text
            print("[sanitize-ctx] %s failed (%s) -- using raw ctx" % (src, e), flush=True)
    with _ctx_lock:
        _ctx_cache[src] = (text, ok)
    return _ctx_cache[src]


# ----------------------------------------------------------------- subprocess helper
def run_cmd(cmd, timeout, env=None, cwd=COPY):
    """run with a fresh process group; returns (rc, 'TIMEOUT'|None, output)"""
    e = os.environ.copy()
    e["PATH"] = PATHENV
    for k in ("MAKEFLAGS", "MFLAGS", "GNUMAKEFLAGS"):
        e.pop(k, None)
    if env:
        e.update(env)
    p = subprocess.Popen(cmd, cwd=cwd, env=e, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, text=True, start_new_session=True)
    try:
        out, _ = p.communicate(timeout=timeout)
        return p.returncode, None, out
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except OSError:
            pass
        out, _ = p.communicate()
        return None, "TIMEOUT", (out or "") + "\n[sweep] TIMEOUT after %ss: %s" % (timeout, cmd[:3])


# ----------------------------------------------------------------- insn counting
INSN_LINE = re.compile(r'^\s*/\*\s*[0-9A-Fa-f]{4,8}\s+[0-9A-Fa-f]{6,8}\s+[0-9A-Fa-f]{4,8}\s*\*/\s*(\S+)')


def count_insns(spath):
    n = 0
    try:
        with open(spath, errors="replace") as f:
            for line in f:
                m = INSN_LINE.match(line)
                if m and not m.group(1).startswith("."):
                    n += 1
    except OSError:
        return -1
    return n


# ----------------------------------------------------------------- enumeration
def enumerate_targets():
    """{srcfile: [(func, sfile), ...]} for every asm/us/nonmatchings pragma"""
    targets = {}
    nmissing = 0
    for dirpath, dirs, files in sorted(os.walk(os.path.join(COPY, "src"))):
        dirs.sort()
        for fname in sorted(files):
            if not fname.endswith(".c"):
                continue
            p = os.path.join(dirpath, fname)
            rel = os.path.relpath(p, COPY)
            with open(p, errors="replace") as f:
                for line in f:
                    m = PRAGMA_RE.search(line)
                    if not m:
                        continue
                    sfile = "asm/us/nonmatchings/%s/%s.s" % (m.group(1), m.group(2))
                    if not os.path.isfile(os.path.join(COPY, sfile)):
                        nmissing += 1
                        continue
                    targets.setdefault(rel, []).append((m.group(2), sfile))
    return targets, nmissing


def parse_map():
    """func -> .o path (relative), from the build map"""
    out = {}
    mapf = os.path.join(COPY, "build", "pokestadiumgs-us.map")
    with open(mapf, errors="replace") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 4 and parts[2] == "build/" and parts[1].startswith("0x"):
                out.setdefault(parts[0], parts[3])
            elif len(parts) == 4 and parts[0].startswith("0x") and parts[2] == "build/":
                pass
    return out


# ----------------------------------------------------------------- per-function sweep
def sweep_func(src, func, sfile, ctx_text, ctx_path, orig, tag_dir):
    """returns result dict; restores the src file before returning"""
    log_path = os.path.join(tag_dir, "logs", func + ".log")
    log_lines = []

    def log(s):
        log_lines.append(s)

    spath = os.path.join(COPY, src)
    res = {"func": func, "file": src, "insns": count_insns(os.path.join(COPY, sfile)),
           "m2c": "?", "score": "FAIL", "bucket": "?"}
    m = re.compile(r'#pragma\s+GLOBAL_ASM\("[^"]*/%s\.s"\)' % re.escape(func)).search(orig)
    if not m:
        res["score"] = "NO_PRAGMA"
        log("pragma not found (regex mismatch)")
        return res
    head = orig[: m.start()]
    try:
        # ---- m2c (mkdraft flags; context is the per-owner-file cached ctx)
        cmd = [PY, M2C, "--target", "mips-ido-c", "--context", ctx_path,
               "--globals", "used", "--valid-syntax", sfile]
        # write the ctx next to a stable path m2c can read
        rc, tmo, out = run_cmd(cmd, M2C_TIMEOUT)
        if tmo:
            res["m2c"] = "timeout"
            log("m2c TIMEOUT")
            return res
        if rc != 0 or not out.strip():
            res["m2c"] = "fail"
            log("m2c failed rc=%s:\n%s" % (rc, (out or "").strip()[-1500:]))
            return res
        res["m2c"] = "ok"
        out = drop_conflicting_externs(fix_draft(out), orig)
        body = draft_body(out.strip("\n"))
        # the draft's own signature -> prototype, used to fix the file's decls of
        # the target (an unprototyped call before the splice or a stale prototype
        # conflicts with the draft definition under IDO)
        sig = re.search(r"^[^\n;{}]*\b%s\s*\([^;{}]*\)\s*\{" % re.escape(func), body, re.M)
        proto = sig.group(0)[: sig.group(0).rfind("{")].strip() + ";" if sig else None
        callee_decls = callee_protos(body, head, orig[m.end():], func)

        # ---- splice / build / diff (extern-fix retries, mkdraft-style)
        decls, added, unproto_done = [], set(), set()
        obj_rel = "build/" + src[:-2] + ".o"
        obj_abs = os.path.join(COPY, obj_rel)

        for attempt in range(4):
            pre = ("\n".join(callee_decls) + "\n") if callee_decls else ""
            full = pre + (("\n".join(decls) + "\n") if decls else "") + body
            spliced = head + full + orig[m.end():]
            if proto:
                spliced = fix_target_decls(spliced, func, proto)
            with open(spath, "w") as f:
                f.write(spliced)
            os.utime(spath, None)
            if os.path.exists(obj_abs):
                os.remove(obj_abs)
            rc, tmo, mout = run_cmd(["make", obj_rel, "PYTHON=" + PY, "RUN_CC_CHECK=0"],
                                    MAKE_TIMEOUT)
            log("attempt %d: make rc=%s%s" % (attempt, rc, " TIMEOUT" if tmo else ""))
            if tmo:
                res["score"] = "TIMEOUT"
                log("make TIMEOUT:\n" + (mout or "").strip()[-1500:])
                return res
            if rc != 0 or not os.path.exists(obj_abs):
                log("make failed rc=%s:\n%s" % (rc, (mout or "").strip()[-4000:]))
                todo = [i for i in missing_decls(mout) if i != func and i not in added]
                if todo:
                    for name in todo:
                        decls.append(ctx_decl(name, ctx_text))
                        added.update(todo)
                    log("retry with decls: " + ", ".join(todo))
                    continue
                # arg-count/type disagreements: unprototype the callee's decl
                changed = False
                for n in arg_count_failures(mout):
                    if n == func or n in unproto_done:
                        continue
                    body, c1 = unprototype_decl(body, n)
                    hit = c1
                    for idx, d in enumerate(callee_decls):
                        nd, c2 = unprototype_decl(d, n)
                        if c2:
                            callee_decls[idx] = nd
                            hit = True
                    if hit:
                        unproto_done.add(n)
                        changed = True
                        log("retry: unprototyped decl of %s" % n)
                if changed:
                    continue
                res["score"] = "BUILD_FAIL"
                return res
            # ---- diff
            rc, tmo, dout = run_cmd([PY] + DIFF + ["-o", func, "--format", "plain",
                                                   "--max-lines", "30000"], DIFF_TIMEOUT)
            if tmo:
                res["score"] = "TIMEOUT"
                log("diff TIMEOUT")
                return res
            sm = SCORE_RE.search(dout)
            if sm is None:
                log("diff produced no score (rc=%s):\n%s" % (rc, (dout or "").strip()[-2500:]))
                res["score"] = "DIFF_FAIL"
                return res
            res["score"] = int(sm.group(1))
            log("score %d" % res["score"])
            if res["score"] == 0:
                # exact splice text that produced 0 (incl. any prepended decls)
                with open(os.path.join(tag_dir, "zero", func + ".c"), "w") as zf:
                    zf.write(full + "\n")
                with open(os.path.join(tag_dir, "zero", func + ".meta"), "w") as zf:
                    zf.write("file=%s\nscore=0\nm2c=direct\n" % src)
            elif res["score"] > 0:
                dl = [l for l in dout.splitlines() if re.search(r"\s[ris]\s|<~|>~|~>", l)]
                log("\n".join(dl[:25]))
            return res
        res["score"] = "BUILD_FAIL"
        return res
    finally:
        # restore + persist log
        try:
            with open(spath, "w") as f:
                f.write(orig)
            os.utime(spath, None)
        except Exception as e:
            log("RESTORE FAILED: %s" % e)
        try:
            with open(log_path, "w") as f:
                f.write("\n".join(log_lines) + "\n")
        except OSError:
            pass


def bucket_of(res):
    if res["m2c"] != "ok" or not isinstance(res["score"], int):
        return "D_structural"
    s = res["score"]
    if s == 0:
        return "A_adopt"
    if s < 300:
        return "B_farm"
    if s < 1500:
        return "C_agent"
    return "D_structural"


# ----------------------------------------------------------------- driver
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="run")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--only-file", action="append", default=None,
                    help="sweep only this src file (repeatable)")
    ap.add_argument("--limit-files", type=int, default=0,
                    help="sweep only the first N files (after sorting)")
    args = ap.parse_args()

    tag_dir = os.path.join(SCRATCH, args.tag)
    os.makedirs(tag_dir, exist_ok=True)
    os.makedirs(os.path.join(tag_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(tag_dir, "zero"), exist_ok=True)
    os.makedirs(os.path.join(SCRATCH, "ctx"), exist_ok=True)

    targets, nmissing = enumerate_targets()
    files = sorted(targets.keys())
    if args.only_file:
        files = [f for f in files if f in set(args.only_file)]
        missing = [f for f in args.only_file if f not in targets]
        if missing:
            print("WARNING: no targets in: %s" % missing)
    if args.limit_files:
        files = files[: args.limit_files]
    print("sweep: %d files, %d functions (%d pragmas with missing .s)"
          % (len(files), sum(len(v) for v in targets.values()), nmissing), flush=True)

    jsonl = os.path.join(tag_dir, "results.jsonl")
    jf = open(jsonl, "a", buffering=1)
    lock = threading.Lock()
    counters = {"done": 0, "total": sum(len(targets[f]) for f in files)}
    t0 = time.time()

    def do_file(src):
        funcs = targets[src]
        orig_path = os.path.join(COPY, src)
        with open(orig_path, errors="replace") as f:
            orig = f.read()
        ctx_text, ctx_ok = gen_ctx(src)
        if not ctx_ok:
            # whole file: ctx failure -> all D_structural
            for func, sfile in funcs:
                res = {"func": func, "file": src, "insns": count_insns(os.path.join(COPY, sfile)),
                       "m2c": "ctx_fail", "score": "FAIL", "bucket": "D_structural"}
                with lock:
                    jf.write(json.dumps(res) + "\n")
                    counters["done"] += 1
            print("[ctx-fail] %s (%d funcs)" % (src, len(funcs)), flush=True)
            return
        ctxp = os.path.join(SCRATCH, "ctx", src.replace("/", "__") + ".ctx")
        with open(ctxp, "w") as f:
            f.write(ctx_text)
        for func, sfile in funcs:
            res = sweep_func(src, func, sfile, ctx_text, ctxp, orig, tag_dir)
            res["bucket"] = bucket_of(res)
            with lock:
                jf.write(json.dumps(res) + "\n")
                counters["done"] += 1
                d, tot = counters["done"], counters["total"]
                if d % 25 == 0 or d == tot:
                    rate = d / max(time.time() - t0, 1e-6)
                    print("[%d/%d] %.0f/min, elapsed %.0fm, eta %.0fm  (last: %s %s)"
                          % (d, tot, rate * 60, (time.time() - t0) / 60,
                             (tot - d) / max(rate, 1e-6) / 60, res["func"], res["score"]),
                          flush=True)
        # verify restored
        with open(orig_path, errors="replace") as f:
            if f.read() != orig:
                print("!!! %s not restored -- rewriting" % src, flush=True)
                with open(orig_path, "w") as f:
                    f.write(orig)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(do_file, files))
    jf.close()
    print("DONE: %d functions in %.1f min -> %s" % (counters["done"], (time.time() - t0) / 60, jsonl), flush=True)


if __name__ == "__main__":
    main()
