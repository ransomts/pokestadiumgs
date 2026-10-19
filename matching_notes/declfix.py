#!/usr/bin/env python3
"""declfix: mechanically repair mkdraft splices that fail to compile.

For each function whose mkdraft splice is in place (marker block) but whose
object does not build, parse the compile error and apply the known fixup
classes, re-compiling after each fix (up to --rounds per function):

  conflicting types for 'X'         -> rewrite the draft's decl of X to the
                                       file's established decl of X (searched
                                       in the pristine .pre outside the splice;
                                       a decl AFTER the splice point is moved
                                       to the file's spelling too - both must
                                       agree, and the file's is established by
                                       matched code)
  redeclared as different kind 'X'  -> if the file defines X as a function,
                                       retype the draft's decl to that
                                       signature; else void X(void);
  too few arguments to 'X'          -> if the draft's decl of X is a
                                       prototype, unprototype it (old-style
                                       parens) so the call compiles; the asm is
                                       the truth for what is really passed
  Unacceptable operand of '+' (cfe) -> retype the void* operand's decl to u8*
  invalid type argument of '*'      -> the operand is declared as a scalar;
                                       retype its decl to u8* (pointer view)

Everything is verified by recompiling; anything the harness cannot fix is
reported for hand surgery. The .o is removed before each compile (NFS trap).

usage: .venv/bin/python3 matching_notes/declfix.py [--rounds 6] func1 func2 ...
       .venv/bin/python3 matching_notes/declfix.py --failed <drafts-log>
"""
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(REPO, ".venv", "bin", "python3")
DRAFTS = os.path.join(REPO, "matching_notes", "drafts")
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

def sh(cmd, timeout=180):
    env = dict(os.environ)
    env["PATH"] = os.path.join(REPO, ".venv", "bin") + ":" + env.get("PATH", "")
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout,
                        env=env)
    return p.returncode, p.stdout + p.stderr

def load(func):
    srcf = open(os.path.join(DRAFTS, func + ".src")).read().strip()
    cur = open(os.path.join(REPO, srcf)).read()
    pre = open(os.path.join(DRAFTS, func + ".pre")).read()
    return srcf, cur, pre

def save(func, srcf, text):
    p = os.path.join(REPO, srcf)
    with open(p, "w") as f:
        f.write(text)
    os.utime(p, None)
    return text

def compile_obj(srcf):
    obj = "build/" + srcf[:-2] + ".o"
    if os.path.exists(os.path.join(REPO, obj)):
        os.remove(os.path.join(REPO, obj))
    rc, out = sh(["make", obj, "PYTHON=" + PY, "RUN_CC_CHECK=1"])
    return rc, ANSI.sub("", out)

def decls_of(name, text):
    """lines in TEXT that declare NAME (extern/prototype/definition)"""
    pats = [
        r"^[^\n;{}]*\b%s\s*\([^;{}]*\)\s*;" % re.escape(name),   # prototype
        r"^[ \t]*(?:extern\s+)?[^\n;{}]*\b%s\s*(?:\[[^]]*\])?\s*;" % re.escape(name),
        r"^[^\n;{}]*\b%s\s*\([^;{}]*\)\s*\{" % re.escape(name),  # definition
    ]
    out = []
    for line in text.splitlines():
        for p in pats:
            if re.search(p, line):
                out.append(line)
                break
    return out

def fix(func, rounds):
    srcf, cur, pre = load(func)
    log = []
    for rnd in range(rounds):
        rc, out = compile_obj(srcf)
        if rc == 0:
            return True, log
        m = (re.search(r"conflicting types for .(\w+).", out)
             or re.search(r"redeclared as different kind of symbol.? .(\w+).", out))
        if m:
            name = m.group(1)
            file_decls = decls_of(name, pre)
            draft_decls = decls_of(name, cur)
            if not draft_decls:
                log.append(f"r{rnd}: {name} conflict but no draft decl found")
                break
            target = None
            for fd in file_decls:
                if fd not in draft_decls:
                    target = fd.strip()
                    break
            if target is None:
                # no established decl: make it old-style so both views compile
                sig = re.search(r"^[ \t]*(?:extern\s+)?([^\n(]*)\b%s\s*\(" % re.escape(name),
                               draft_decls[0])
                ret = sig.group(1).replace("extern", "").strip() if sig else "void"
                target = f"extern {ret} {name}();"
            new = cur.replace(draft_decls[0].strip(), target, 1)
            if new == cur:
                log.append(f"r{rnd}: {name} replace failed")
                break
            cur, _ = new, save(func, srcf, new)
            log.append(f"r{rnd}: retyped {name} -> {target[:60]}")
            continue
        # cfe: "redeclaration of 'X'; previous declaration at line M" - the
        # draft's decl at the error line must adopt the earlier decl's spelling
        m = re.search(r"redeclaration of .(\w+).; previous declaration at line (\d+)", out)
        if m:
            name, prev_line = m.group(1), int(m.group(2))
            em = re.search(r"cfe: Error: [^,]+, line (\d+): redeclaration", out)
            err_line = int(em.group(1)) if em else 0
            lines = cur.splitlines()
            if err_line and 0 < prev_line <= len(lines) and prev_line != err_line:
                prev_decl = lines[prev_line - 1].strip()
                # find the re-decl near the error line (same symbol)
                for j in range(err_line, max(0, err_line - 4), -1):
                    if re.search(r"\b%s\b" % re.escape(name), lines[j - 1]) and j != prev_line:
                        lines[j - 1] = prev_decl
                        cur = save(func, srcf, "\n".join(lines))
                        log.append(f"r{rnd}: {name} redecl@{j} -> spelling@{prev_line}")
                        break
                else:
                    log.append(f"r{rnd}: {name} redecl site not found")
                    break
            else:
                log.append(f"r{rnd}: {name} redecl lines unusable ({prev_line}/{err_line})")
                break
            continue
        m = re.search(r"too few arguments to function .(\w+).", out)
        if m:
            name = m.group(1)
            draft_decls = decls_of(name, cur)
            if draft_decls:
                d = draft_decls[0]
                nd = re.sub(r"\(([^()]*)\)\s*;", "();", d)
                if nd != d:
                    cur = save(func, srcf, cur.replace(d.strip(), nd.strip(), 1))
                    log.append(f"r{rnd}: unprototyped {name}")
                    continue
            log.append(f"r{rnd}: {name} too-few-args, no decl to unprototype")
            break
        m = re.search(r"Unacceptable operand of .[+].", out)
        if m:
            # find the reported line and retype its void* decls
            lm = re.search(r"line (\d+):", out)
            line_no = int(lm.group(1)) if lm else 0
            lines = cur.splitlines()
            changed = False
            for i in range(line_no, max(0, line_no - 60), -1):
                if re.search(r"extern void \*", lines[i - 1]):
                    lines[i - 1] = lines[i - 1].replace("void *", "u8 *")
                    changed = True
                    break
            if changed:
                cur = save(func, srcf, "\n".join(lines))
                log.append(f"r{rnd}: void* -> u8* near line {line_no}")
                continue
            log.append(f"r{rnd}: void*-plus but no decl found")
            break
        m = (re.search(r"invalid type argument of unary .\*.", out)
             or re.search(r"Dereferenced a non-pointer", out))
        if m:
            lm = re.search(r"line (\d+):", out)
            line_no = int(lm.group(1)) if lm else 0
            src_line = cur.splitlines()[line_no - 1] if line_no else ""
            vm = re.search(r"\b(\w+)\s*\[", src_line) or re.search(r"\*\s*(\w+)", src_line)
            if vm:
                name = vm.group(1)
                draft_decls = decls_of(name, cur)
                if draft_decls:
                    nd = re.sub(r"\bint\b|\bs32\b|\bM2C_UNK\b", "u8 *", draft_decls[0], count=1)
                    nd = re.sub(r"\s+%s\s*;" % re.escape(name), " *%s;" % name, nd)
                    if nd != draft_decls[0]:
                        cur = save(func, srcf, cur.replace(draft_decls[0].strip(), nd.strip(), 1))
                        log.append(f"r{rnd}: {name} -> pointer view")
                        continue
            log.append(f"r{rnd}: star-on-int unresolved: {src_line[:50]}")
            break
        log.append(f"r{rnd}: unknown error: " + "; ".join(
            l for l in out.splitlines() if "rror" in l)[:120])
        break
    return False, log

def main():
    argv = sys.argv[1:]
    rounds = 6
    if argv and argv[0] == "--rounds":
        rounds = int(argv[1]); argv = argv[2:]
    if argv and argv[0] == "--failed":
        funcs = []
        for line in open(argv[1]):
            m = re.match(r"=== (\S+) \(", line)
            if m:
                funcs.append(m.group(1))
        argv = []
    else:
        funcs = argv
    ok, bad = [], []
    for f in funcs:
        try:
            good, log = fix(f, rounds)
        except Exception as e:
            good, log = False, [f"exception: {e}"]
        (ok if good else bad).append(f)
        print(("FIXED  " if good else "STUCK  ") + f + ("" if not log else "  [" + "; ".join(log) + "]"))
        sys.stdout.flush()
    print(f"\n{len(ok)} fixed, {len(bad)} stuck")
    if bad:
        print("stuck:", " ".join(bad))

if __name__ == "__main__":
    main()
