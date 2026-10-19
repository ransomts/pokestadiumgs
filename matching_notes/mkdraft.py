#!/home/tsranso/Code/pokestadiumgs/.venv/bin/python3
"""mkdraft: m2c a nonmatching function, splice the draft over its GLOBAL_ASM pragma, score it.

USAGE (repo root; repo venv python -- system python3 is 3.6 and unusable)
  .venv/bin/python3 matching_notes/mkdraft.py func_84128B30 src/fragments/79/fragment79_393CA0.c
  .venv/bin/python3 matching_notes/mkdraft.py func_84128B30          # src found via its pragma
  .venv/bin/python3 matching_notes/mkdraft.py restore func_84128B30   # undo the splice
  .venv/bin/python3 matching_notes/mkdraft.py func_X --restore        # same, other spelling
  options: --flags "--no-casts"   extra m2c flags (one string)
           --m2c PATH             default tools/mips_to_c/m2c.py

WHAT IT DOES (GS splice convention -- this repo has no NON_MATCHING draft wrapper; a
function is either matched C or a bare `#pragma GLOBAL_ASM("asm/us/nonmatchings/...")`):
  1. Locates the function's pragma line in the src file and the .s it names (falls back
     to a find under asm/us/nonmatchings/).
  2. Regenerates the m2c context: matching_notes/m2ctx.py writes repo-root ctx.c, rerun
     when ctx.c is absent or older than the src file (ctx.c / ctx.c.m2c are gitignored).
  3. Runs tools/mips_to_c/m2c.py --target mips-ido-c --context ctx.c --globals used
     --valid-syntax on the .s. If the output uses m2c's M2C_* macros (m2c_macros.h), a
     self-contained #ifndef-guarded shim is prepended so the draft compiles.
  4. Writes matching_notes/drafts/<func>.c (first line records the original pragma line
     and the src file), a pristine pre-splice copy of the src file to <func>.pre, and the
     src path to <func>.src.
  5. Splices the draft over the pragma line in the src file between
     `/* mkdraft:<func> begin */` and `/* mkdraft:<func> end */` markers (the surrounding
     `#ifdef VERSION_US ... #endif` is kept) and leaves it spliced in: edit the file and
     re-run matching_notes/fd.sh to iterate. Undo with `mkdraft.py restore <func>`.
  6. Runs matching_notes/fd.sh (build one object + full uncapped diff) and reports the
     CURRENT score. A 0 is NOT a match (relocations compare equal): only a full `make`
     printing `build/pokestadiumgs-us.z64: OK` is.

RESTORE SEMANTICS: the marker block is replaced by the recorded original pragma line, so
  edits elsewhere in the file (including other functions' splices) survive. If no marker
  block is present the file is reported already-clean (or, if it differs from <func>.pre,
  left alone with a hint -- never clobbers). try_candidate.py/adopt_candidate.py reuse this
  splice format (import mkdraft), so `restore` also undoes their --keep splices.
"""
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(REPO, ".venv", "bin", "python3")
M2C = os.path.join(REPO, "tools", "mips_to_c", "m2c.py")
M2CTX = os.path.join(REPO, "matching_notes", "m2ctx.py")
FD = os.path.join(REPO, "matching_notes", "fd.sh")
DRAFTS = os.path.join(REPO, "matching_notes", "drafts")
CTX = os.path.join(REPO, "ctx.c")

# m2c --valid-syntax helper macros (subset of tools/mips_to_c/m2c_macros.h as #defines)
M2C_MACROS = """\
#ifndef M2C_FIELD /* mkdraft: m2c --valid-syntax helpers */
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


def die(msg):
    sys.exit("mkdraft: " + msg)


# ---------------------------------------------------------------- locating / splicing

def pragma_re(func):
    return re.compile(r'#pragma\s+GLOBAL_ASM\("([^"]*/%s\.s)"\)' % re.escape(func))


def marker_re(func):
    """regex matching the whole mkdraft splice block `begin */ ... end */` (newline after
    the end marker is looked ahead at, not consumed, so sub() replacements need no \\n)"""
    b = "/* mkdraft:%s begin */" % func
    e = "/* mkdraft:%s end */" % func
    return b, e, re.compile(re.escape(b) + r"\n.*?\n" + re.escape(e) + r"(?=\n|$)", re.S)


def splice(text, func, body):
    """replace FUNC's GLOBAL_ASM line (or its existing mkdraft splice block) with the
    draft body between mkdraft markers. -> new text, or None if there is no splice target"""
    b, e, rx = marker_re(func)
    block = b + "\n" + body + "\n" + e
    if rx.search(text):
        return rx.sub(lambda _: block, text, count=1)
    m = pragma_re(func).search(text)
    if not m:
        return None
    eol = text.find("\n", m.end())
    t = eol + 1 if eol >= 0 else len(text)
    return text[: m.start()] + block + "\n" + text[t:]


def unsplice(text, func, pragma):
    """replace FUNC's mkdraft splice block with the given pragma line (inverse of splice)"""
    b, e, rx = marker_re(func)
    if not rx.search(text):
        return text
    return rx.sub(lambda _: pragma, text, count=1)


def unwrap(text, func):
    """drop the mkdraft markers, leaving the spliced body as plain C (for adoption).
    -> new text, or None if there is no splice block"""
    b, e, rx = marker_re(func)
    m = rx.search(text)
    if not m:
        return None
    inner = m.group(0)[len(b) + 1: -len(e) - 1]  # strip `begin */\n` and `\n end */`
    return text[: m.start()] + inner + text[m.end():]


def func_span(text, func):
    """(start, end) of `<type> func(...) { ... }`, end just past the closing brace."""
    m = re.search(r"^[^\n;{}#]*\b%s\s*\([^;{]*\)\s*\{" % re.escape(func), text, re.M)
    if not m:
        return None
    depth, i = 0, m.end() - 1
    while i < len(text):
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        if depth == 0:
            return m.start(), i + 1
        i += 1
    return None


def find_asm_file(func):
    nonm = os.path.join(REPO, "asm", "us", "nonmatchings")
    for d, _, files in os.walk(nonm):
        if func + ".s" in files:
            return os.path.relpath(os.path.join(d, func + ".s"), REPO)
    return None


def find_src_file(func):
    for d, dirs, files in os.walk(os.path.join(REPO, "src")):
        dirs.sort()
        for f in sorted(files):
            if f.endswith(".c"):
                p = os.path.join(d, f)
                with open(p, errors="replace") as fh:
                    if pragma_re(func).search(fh.read()):
                        return os.path.relpath(p, REPO)
    return None


def write_and_touch(path, text):
    with open(path, "w") as f:
        f.write(text)
    os.utime(path, None)  # NFS: make the rewrite visible to make NOW


# ---------------------------------------------------------------- pipeline stages

def ensure_ctx(src):
    """regenerate repo-root ctx.c via matching_notes/m2ctx.py if absent/older than src"""
    sp = os.path.join(REPO, src)
    if os.path.exists(CTX) and os.path.getmtime(CTX) >= os.path.getmtime(sp):
        return
    p = subprocess.run([PY, M2CTX, src], cwd=REPO, capture_output=True, text=True)
    if p.returncode != 0 or not os.path.exists(CTX):
        die("m2ctx failed:\n" + (p.stdout + p.stderr).strip()[-2000:])
    print("  ctx.c regenerated by m2ctx.py")


def run_m2c(func, asm, extra_flags):
    cmd = [PY, M2C, "--target", "mips-ido-c", "--context", "ctx.c",
           "--globals", "used", "--valid-syntax"] + extra_flags + [asm]
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        die("m2c failed (rc=%d):\n%s" % (p.returncode, (p.stderr or p.stdout).strip()[-3000:]))
    return p.stdout.strip("\n")


def draft_body(code):
    """m2c output -> text that compiles when spliced into a src file"""
    code = code.replace("? ", "M2C_UNK ").replace("?*", "M2C_UNK*")
    if "M2C_" in code:
        return M2C_MACROS + "\n" + code
    return code


def run_fd(src, func):
    """run fd.sh (streamed live, also captured). -> (score or None, output text)"""
    p = subprocess.Popen([FD, src, func, "40"], cwd=REPO,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = []
    for line in p.stdout:
        out.append(line)
        sys.stdout.write(line)
        sys.stdout.flush()
    p.wait()
    text = "".join(out)
    m = re.search(r"CURRENT \((\d+)", text)
    return (int(m.group(1)) if m else None), text


ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def missing_decls(fd_out):
    """identifiers reported undeclared/undefined by the host CC_CHECK or IDO cfe,
    in first-seen order (the `did you mean` suggestion is ignored)"""
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


def ctx_decl(name):
    """NAME's declaration from ctx.c (extern lines only, reused verbatim so the type is
    right); `extern s32 NAME;` stub (flagged) if the context does not declare it"""
    with open(CTX, errors="replace") as f:
        for line in f:
            s = ANSI.sub("", line)
            s = re.sub(r"/\*.*?\*/\s*$", "", s.split("//")[0]).strip()
            if s.startswith("extern") and s.endswith(";") and "{" not in s and \
                    re.search(r"\b%s\b" % re.escape(name), s):
                return s
    return "extern s32 %s; /* mkdraft stub: no extern for it in ctx.c -- check the type */" % name


# ---------------------------------------------------------------- driver

def draft(func, src, extra_flags, m2c):
    global M2C
    M2C = m2c
    sp = os.path.join(REPO, src)
    with open(sp) as f:
        orig = f.read()
    pm = pragma_re(func).search(orig)
    if pm:
        pristine, pragma = orig, pm.group(0)
    else:
        # maybe re-drafting over an existing splice: recover the pragma from <func>.pre
        pre = os.path.join(DRAFTS, func + ".pre")
        pp = pragma_re(func).search(open(pre).read()) if os.path.exists(pre) else None
        if not pp:
            die("%s has no GLOBAL_ASM for %s" % (src, func))
        pristine, pragma = unsplice(orig, func, pp.group(0)), pp.group(0)
    asm = pragma_re(func).search(pristine).group(1)
    if not os.path.isfile(os.path.join(REPO, asm)):
        found = find_asm_file(func)
        if not found:
            die("no %s (and no %s.s under asm/us/nonmatchings)" % (asm, func))
        asm = found
    print("%s: asm %s, src %s" % (func, asm, src))

    ensure_ctx(src)
    code = run_m2c(func, asm, extra_flags)
    body = draft_body(code)
    os.makedirs(DRAFTS, exist_ok=True)
    with open(os.path.join(DRAFTS, func + ".pre"), "w") as f:
        f.write(pristine)
    with open(os.path.join(DRAFTS, func + ".src"), "w") as f:
        f.write(src + "\n")

    # splice + score; on undeclared-identifier build errors (a use can precede its
    # declaration elsewhere in the file -- m2c's context is order-insensitive), prepend
    # the ctx.c extern line and retry, up to 4 rounds
    decls, added, score, out = [], set(), None, None
    for _ in range(4):
        full = ("\n".join(decls) + "\n" if decls else "") + body
        write_and_touch(sp, splice(pristine, func, full))
        score, out = run_fd(src, func)
        if score is not None:
            break
        todo = [i for i in missing_decls(out) if i != func and i not in added]
        if not todo:
            break
        for name in todo:
            decls.append(ctx_decl(name))
            added.add(name)
            print("  fix: prepended `%s`" % decls[-1])
    full = ("\n".join(decls) + "\n" if decls else "") + body
    print("  spliced into %s (markers: /* mkdraft:%s begin/end */)" % (src, func))
    with open(os.path.join(DRAFTS, func + ".c"), "w") as f:
        f.write("// mkdraft: %s (src: %s)\n" % (pragma, src))
        f.write("// mkdraft: score via matching_notes/fd.sh; undo with matching_notes/mkdraft.py restore %s\n" % func)
        f.write(full + "\n")
    if score is None:
        print("mkdraft: no score for %s (build failed; splice left in place -- fix and re-run "
              "fd.sh, or `mkdraft.py restore %s`)\n%s" % (func, func, "\n".join(out.splitlines()[:5])))
        sys.exit(1)
    print("  draft: %s" % os.path.join("matching_notes", "drafts", func + ".c"))
    print("%s: score %d%s" % (func, score,
          "  (0 is NOT proof of a match: full make must print 'build/pokestadiumgs-us.z64: OK')" if score == 0 else ""))
    return score


def restore(func):
    srcf = os.path.join(DRAFTS, func + ".src")
    pref = os.path.join(DRAFTS, func + ".pre")
    if not (os.path.exists(srcf) and os.path.exists(pref)):
        die("no splice state for %s (matching_notes/drafts/%s.src/.pre missing)" % (func, func))
    with open(srcf) as f:
        src = f.read().strip()
    sp = os.path.join(REPO, src)
    with open(sp) as f:
        cur = f.read()
    with open(pref) as f:
        pre = f.read()
    b, e, rx = marker_re(func)
    if rx.search(cur):
        pp = pragma_re(func).search(pre)
        if not pp:
            die("recorded %s.pre has no GLOBAL_ASM for %s" % (func, func))
        write_and_touch(sp, rx.sub(lambda _: pp.group(0), cur, count=1))
        print("restored %s in %s (marker block -> original pragma line)" % (func, src))
        return
    if cur == pre:
        print("%s: %s already clean" % (func, src))
        return
    die("no marker block for %s in %s and the file differs from the recorded .pre;\n"
        "  inspect `git diff %s`; `git restore %s` only if every change is splice-related"
        % (func, src, src, src))


def main():
    argv = sys.argv[1:]
    if not argv:
        die("usage: mkdraft.py <func> [<src-file>] [--flags ...] [--m2c PATH] | mkdraft.py restore <func>")
    if argv[0] == "restore":
        if len(argv) != 2:
            die("usage: mkdraft.py restore <func>")
        restore(argv[1])
        return
    func = argv[0]
    src, extra, m2c = None, [], M2C
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--restore":
            restore(func)
            return
        elif a == "--flags":
            i += 1
            if i >= len(argv):
                die("--flags needs an argument")
            extra = argv[i].split()
        elif a == "--m2c":
            i += 1
            if i >= len(argv):
                die("--m2c needs an argument")
            m2c = argv[i]
        elif src is None:
            src = a
        else:
            die("unexpected argument %r" % a)
        i += 1
    if src is None:
        src = find_src_file(func)
        if src is None:
            die("no src/ file has a GLOBAL_ASM for %s (pass <src-file> explicitly)" % func)
        print("  src located via pragma scan: " + src)
    draft(func, src, extra, m2c)


if __name__ == "__main__":
    main()
