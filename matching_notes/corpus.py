#!/home/tsranso/Code/pokestadiumgs/.venv/bin/python3
"""corpus.py - look up "what C produced this asm idiom" in the matched corpus.

Indexes every function compiled into build/src/**/*.o (IDO 7.1 output),
pairs it with its C body from src/**/*.c, and lets you regex-search the
compiled asm (raw, or normalized so register allocation and immediates do not
matter). IDO objects carry .mdebug line info, so every instruction is mapped
back to the C source line that produced it.

USAGE (run from anywhere; python is the repo venv):
  PY=/home/tsranso/Code/pokestadiumgs/.venv/bin/python3
  $PY matching_notes/corpus.py build              # (re)build build/corpus/index.json (~1 min)
  $PY matching_notes/corpus.py search 'beqzl .*\\n.*lui' --c --limit 3
  $PY matching_notes/corpus.py search 'lbu (\\w+), .*\\n.*andi \\w+, \\1, 0xff' --window 4
  $PY matching_notes/corpus.py search 'sll t, t, 0x10\\nsra t, t, 0x10'
  $PY matching_notes/corpus.py search 'jal sqrtf' --raw
  $PY matching_notes/corpus.py near func_8430506C            # uses /tmp/fd_last_<f>.txt if present
  $PY matching_notes/corpus.py near func_8430506C --draft    # compile the NON_MATCHING draft
                                                              # (copy under build/corpus/draft) and diff it
  $PY matching_notes/corpus.py show func_84301B00            # one function: asm + C side by side
  $PY matching_notes/corpus.py norm path/to/func.s           # print a .s file in normalized form
  $PY matching_notes/corpus.py siblings func_83501718        # whole-function look-alikes (matched corpus)
  $PY matching_notes/corpus.py siblings func_80034BD4 --c --limit 3   # (matched FUNC works too)
  $PY matching_notes/corpus.py siblings --all-unmatched --limit 3     # one block per GLOBAL_ASM function
                                                                      # + summary table at the end

SIBLINGS: whole-function similarity of FUNC (unmatched: asm/us/nonmatchings/**/FUNC.s; matched: the
  index) against every matched function. Features = multiset of norm-form 1-, 2- and 3-instruction
  n-grams, each weighted by IDF over the matched corpus (common prologue/epilogue/nop grams count
  ~0; rare constants such as `lui at, 0xfd10` count a lot). shared = sum of w*min(count_q, count_s).
    q-in-s = shared/W(FUNC)   (how much of FUNC the sibling contains)
    s-in-q = shared/W(sib)    (how much of the sibling FUNC contains)
    score  = shared/min(W) * (min(W)/max(W))**0.3
  so a same-size twin scores ~ its overlap, and a function contained in a 2x bigger (or smaller)
  one keeps ~80% of it. Measured: twins func_80034824/func_80034BD4 score 0.48; scores >= 0.45 are
  "strong", 0.30-0.45 "possible", below ~0.25 is mostly shared idioms. Also printed: the longest
  common norm run (insn ranges in both, with the sibling's C lines) and `aligned` = the fraction of
  FUNC's insns in difflib's alignment with the sibling. The n-gram postings are precomputed into
  build/corpus/siblings.json (by `build`, or lazily on first use when stale).

FORMS (what PATTERN is matched against; one instruction per line):
  raw   (--raw)  : `lw a0, %lo(D_84385380)(a0)`, `beqzl t6, .L11c`, `jal func_8432C68C`
                   registers without `$`, numbers in lowercase hex, branch targets as
                   `.L<offset from function start>`.
  norm  (default): registers -> class (t s a v at f sp ra zero gp k; fp/s8 -> s),
                   symbols -> SYM (`%hi(SYM)`, `%lo(SYM)(at)`, `jal SYM`), branch targets
                   -> L, memory offsets and addiu immediates -> N. Immediates of
                   sll/srl/sra/andi/ori/xori/lui/li/slti/sltiu are KEPT (0xff, 0x10, ...).
                   e.g. `lw t, N(sp)`, `beqzl t, L`, `andi t, t, 0xff`, `lui at, 0x4f80`.
  loose (--loose): norm with every remaining immediate -> N.
  Pseudo-ops are canonicalized the same way in both objdump and splat input:
  nop, move, li, negu, not, b, beqz/bnez/beqzl/bnezl (beq/bne/beql/bnel against zero).

NEAR: takes the differing target lines (from --draft, --diff FILE, or /tmp/fd_last_FUNC.txt
  written by fd.sh; with none of these it shows the rarest windows of the whole target),
  merges them into regions, and for each region looks up matched functions containing an
  N-insn window (N = window+2 down to 2) of the TARGET asm there, trying forms in order:
  regs (real registers, imms/symbols abstracted; tried first, and form-major, for reg diffs),
  norm, loose. Stack-offset-only regions are just labelled (spill-slot order cannot be told
  from shape) unless --stack, which looks them up with the exact sp offsets kept. Hits are
  ranked by sum(1/#functions sharing the window) and printed with the C lines that
  produced them (from .mdebug line info). --draft also shows which draft C line emitted
  the wrong code. Only IDO 7.1 -O2 files are used unless --any-cc.

PATTERN tips: immediates are hex, so end them with $ or \\b (`andi t, t, 0xff$`, otherwise
0xff also matches 0xfff0); backreferences work in --raw (`lbu (\\w+), .*\\n.*andi \\w+, \\1, 0xff$`).

PATTERN is a Python regex applied to a sliding window of N consecutive
instructions joined by "\\n". The window grows automatically to fit the number
of `\\n` in the pattern, so `beqzl .*\\n.*lui` just works. Use ^/$ freely
(MULTILINE is on: ^ = start of an instruction).
"""

import argparse
import bisect
import collections
import concurrent.futures
import difflib
import glob
import json
import math
import os
import re
import shlex
import shutil
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_DIR = os.path.join(REPO, "build", "corpus")
INDEX = os.path.join(CORPUS_DIR, "index.json")
HOME = os.path.expanduser("~")
OBJDUMP = shutil.which("mips-linux-gnu-objdump") or os.path.join(HOME, "local/bin/mips-linux-gnu-objdump")
TOOL_PATH = os.pathsep.join([os.path.join(REPO, ".venv/bin"), os.path.join(HOME, "local/bin"),
                             "/usr/local/bin", "/usr/bin", "/bin"])
FORMAT_VERSION = 1

# --------------------------------------------------------------------------------------
# Instruction canonicalization / normalization (shared by objdump and splat input)
# --------------------------------------------------------------------------------------

GPRS = (["zero", "at", "v0", "v1", "a0", "a1", "a2", "a3"] + ["t%d" % i for i in range(10)]
        + ["s%d" % i for i in range(9)] + ["k0", "k1", "gp", "sp", "fp", "ra"])
REGS = set(GPRS) | {"f%d" % i for i in range(32)}
# spimdisasm o32 FPR names -> fN
FPR_ALIAS = {}
for _i, _n in enumerate(["fv0", "fv1", "ft0", "ft1", "ft2", "ft3", "fa0", "fa1", "ft4", "ft5",
                         "fs0", "fs1", "fs2", "fs3", "fs4", "fs5"]):
    FPR_ALIAS[_n] = "f%d" % (2 * _i)
    FPR_ALIAS[_n + "f"] = "f%d" % (2 * _i + 1)
REG_ALIAS = dict(FPR_ALIAS, s8="fp")
EXPR_RE = re.compile(r"^\(\s*(?:(?:0x[0-9a-fA-F]+|\d+)|[\s()&|+\-<>~])+\)$")


def canon_reg(r):
    return REG_ALIAS.get(r, r)


def canon_sym(s):
    """Drop asm-processor's `build/src/x.o:` prefix on converted statics."""
    s = s.replace(" ", "")
    return re.sub(r"^[^:()]*\.o:", "", s)
KEEP_IMM = {"sll", "srl", "sra", "andi", "ori", "xori", "lui", "li", "slti", "sltiu"}
NUM_RE = re.compile(r"^-?(0x[0-9a-fA-F]+|\d+)$")
MEM_RE = re.compile(r"^(.*)\((\$?\w+)\)$")
HEXNUM_RE = re.compile(r"-?0x[0-9a-f]+")
BRANCHES = {"b", "beq", "bne", "beql", "bnel", "beqz", "bnez", "beqzl", "bnezl", "blez", "bgtz",
            "bltz", "bgez", "blezl", "bgtzl", "bltzl", "bgezl", "bc1t", "bc1f", "bc1tl", "bc1fl",
            "bltzal", "bgezal", "bal"}


def hexnum(v):
    return ("-0x%x" % -v) if v < 0 else ("0x%x" % v)


def split_ops(s):
    """Split an operand string on commas at paren depth 0."""
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        out.append("".join(cur).strip())
    return out


def canon_operand(op):
    """Canonical raw operand: no `$`, ints as hex, `%lo(sym+0x4)` without spaces."""
    op = op.strip().replace("$", "")
    if op.startswith("%"):
        m = re.match(r"^(%\w+)\((.*?)\)(?:\((\w+)\))?$", op)
        if m:
            inner = canon_sym(m.group(2))
            inner = re.sub(r"\+(0x[0-9A-Fa-f]+|\d+)$", lambda mm: "+" + hexnum(int(mm.group(1), 0)), inner)
            return "%s(%s)%s" % (m.group(1), inner, "(%s)" % canon_reg(m.group(3)) if m.group(3) else "")
        return op.replace(" ", "")
    if NUM_RE.match(op):
        return hexnum(int(op, 0))
    if EXPR_RE.match(op) and re.search(r"(>>|<<|&|\|)", op):   # splat: (0x4F800000 >> 16), (0x12DF0 & 0xFFFF)
        try:
            return hexnum(eval(op, {"__builtins__": {}}, {}))
        except Exception:
            pass
    m = MEM_RE.match(op)
    if m:
        disp = op[:m.start(2) - 1].strip()
        if not disp or NUM_RE.match(disp):
            return "%s(%s)" % (hexnum(int(disp or "0", 0)), canon_reg(m.group(2)))
        # splat: lw t6, (0x137F0 & 0xFFFF)(a2) -- low half of a segment address
        if disp.startswith("(") and disp.endswith(")") and EXPR_RE.match(disp) \
                and re.search(r"(>>|<<|&|\|)", disp):
            try:
                return "%s(%s)" % (hexnum(eval(disp, {"__builtins__": {}}, {})), canon_reg(m.group(2)))
            except Exception:
                pass
    return canon_reg(op)


def canon_insn(mn, ops):
    """Fold real/pseudo instruction spellings onto one form."""
    if mn == "sll" and ops == ["zero", "zero", "0x0"]:
        return "nop", []
    if mn in ("beq", "bne", "beql", "bnel") and len(ops) == 3:
        if ops[1] == "zero":
            if mn == "beq" and ops[0] == "zero":
                return "b", [ops[2]]
            return {"beq": "beqz", "bne": "bnez", "beql": "beqzl", "bnel": "bnezl"}[mn], [ops[0], ops[2]]
    if mn == "beqz" and ops and ops[0] == "zero":
        return "b", ops[1:]
    if mn in ("or", "addu") and len(ops) == 3 and ops[2] == "zero":
        return "move", ops[:2]
    if mn in ("addiu", "ori") and len(ops) == 3 and ops[1] == "zero":
        return "li", [ops[0], ops[2]]
    if mn == "subu" and len(ops) == 3 and ops[1] == "zero":
        return "negu", [ops[0], ops[2]]
    if mn == "nor" and len(ops) == 3 and ops[2] == "zero":
        return "not", ops[:2]
    if mn == "jalr" and len(ops) == 2 and ops[0] == "ra":
        return "jalr", ops[1:]
    if mn in ("cfc1", "ctc1") and len(ops) == 2:
        r = ops[1]
        r = "fcsr" if ("fcsr" in r or r in ("31", "0x1f")) else "fcr" + r.split("_")[-1]
        return mn, [ops[0], r]
    if mn == "break" and ops == ["0x0"]:
        return mn, []
    return mn, ops


def rclass(r):
    if r in ("zero", "sp", "ra", "at", "gp"):
        return r
    if r in ("fp", "s8"):
        return "s"
    if r[0] in "tsavk" and r[1:].isdigit():
        return r[0]
    if r[0] == "f" and r[1:].isdigit():
        return "f"
    return r


def normalize(raw):
    """raw canonical line -> normalized line."""
    parts = raw.split(" ", 1)
    mn = parts[0]
    ops = split_ops(parts[1]) if len(parts) > 1 else []
    out = []
    for i, op in enumerate(ops):
        if op in REGS:
            out.append(rclass(op))
        elif op.startswith("%"):
            m = re.match(r"^(%\w+)\(.*?\)(?:\((\w+)\))?$", op)
            if m:
                out.append("%s(SYM)" % m.group(1) + ("(%s)" % rclass(m.group(2)) if m.group(2) else ""))
            else:
                out.append("SYM")
        elif op.startswith(".L"):
            out.append("L")
        elif NUM_RE.match(op):
            out.append(op if mn in KEEP_IMM else "N")
        else:
            m = MEM_RE.match(op)
            if m and m.group(2) in REGS:
                out.append("N(%s)" % rclass(m.group(2)))
            elif mn in ("jal", "j") and i == len(ops) - 1:
                out.append("SYM")
            else:
                out.append(op)
    return mn + (" " + ", ".join(out) if out else "")


def loosen(norm):
    return HEXNUM_RE.sub("N", norm)


def make_raw(mn, ops):
    mn, ops = canon_insn(mn, [canon_operand(o) for o in ops])
    return mn + (" " + ", ".join(ops) if ops else "")


# --------------------------------------------------------------------------------------
# objdump parsing
# --------------------------------------------------------------------------------------

O_FUNC_RE = re.compile(r"^([0-9a-f]+) <([^>]+)>:$")
O_INSN_RE = re.compile(r"^\s*([0-9a-f]+):\t(\S+)(?:\t(.*))?$")
O_RELOC_RE = re.compile(r"^\s*([0-9a-f]+): (R_MIPS_\w+)\t(.*)$")
O_LINE_RE = re.compile(r"^(\S+?):(\d+)(?: \(discriminator \d+\))?$")
O_TARGET_RE = re.compile(r"^([0-9a-f]+) <([^>+]+)(?:\+0x([0-9a-f]+))?>$")


def objdump(obj):
    p = subprocess.run([OBJDUMP, "-dlrz", "-M", "no-aliases", "--no-show-raw-insn", "-j", ".text", obj],
                       capture_output=True, text=True)
    return p.stdout


def symtab(obj):
    """section -> sorted [(value, size, name)] of data symbols, to name section-relative relocs."""
    p = subprocess.run([OBJDUMP, "-t", obj], capture_output=True, text=True)
    out = collections.defaultdict(list)
    for line in p.stdout.splitlines():
        m = re.match(r"^([0-9a-f]{8}) .{7} (\.\w+)\t([0-9a-f]{8}) (\S+)$", line)
        if m and m.group(4) != m.group(2):
            out[m.group(2)].append((int(m.group(1), 16), int(m.group(3), 16), canon_sym(m.group(4))))
    for v in out.values():
        v.sort()
    return out


def resolve_section(sym, add, secsyms):
    """('.bss', 0x1874) -> 'D_84390020+0x4' when the symbol table names it."""
    lst = secsyms.get(sym) if secsyms else None
    if lst:
        i = bisect.bisect_right([v for v, _, _ in lst], add) - 1
        if i >= 0:
            v, size, name = lst[i]
            # asm-processor's converted statics have size 0: extend them to the next symbol
            end = v + size if size else (lst[i + 1][0] if i + 1 < len(lst) else v + 0x10000)
            if add < end or add == v:
                return name, add - v
    return sym, add


def parse_objdump(text, merge_local_labels=True):
    """-> (list of dicts {name, start, insns:[[off, mnem, opstr, srcline, relocs]]},
    {label: address}).
    Stadium 2's asm-processor assembles GLOBAL_ASM regions with GAS, whose prelude
    makes jlabel'd local labels `.global`; objdump therefore prints one
    pseudo-function per `.L*` label (splitting a splat function into chunks) and
    emits those branches as placeholder offsets + R_MIPS_PC16 relocs.  Merging the
    `.L*` continuations keeps a function whole; the label map resolves the relocs."""
    funcs = []
    labels = {}
    cur = None
    srcline = 0
    for line in text.splitlines():
        m = O_RELOC_RE.match(line)
        if m:
            if cur and cur["insns"]:
                cur["insns"][-1][4].append((m.group(2), m.group(3).strip()))
            continue
        m = O_INSN_RE.match(line)
        if m and cur is not None:
            cur["insns"].append([int(m.group(1), 16), m.group(2), m.group(3) or "", srcline, []])
            continue
        m = O_FUNC_RE.match(line)
        if m:
            cur = {"name": m.group(2), "start": int(m.group(1), 16), "insns": []}
            labels.setdefault(m.group(2), int(m.group(1), 16))
            funcs.append(cur)
            srcline = 0
            continue
        m = O_LINE_RE.match(line)
        if m:
            srcline = int(m.group(2))
    # Local labels can show up as pseudo-functions; merge `.L*` continuations into
    # the preceding function and drop empty entries.
    if merge_local_labels:
        merged = []
        for f in funcs:
            if merged and f["name"].startswith(".L"):
                merged[-1]["insns"].extend(f["insns"])
            else:
                merged.append(f)
        funcs = merged
    return [f for f in funcs if f["insns"]], labels


def lo_imm(op):
    m = MEM_RE.match(op)
    return int((m.group(1) if m else op) or "0", 0)


def with_addend(sym, add, secsyms=None):
    if sym.startswith(".") and secsyms:
        sym, add = resolve_section(sym, add, secsyms)
    return sym + ("+" + hexnum(add) if add else "")


def func_to_raw(f, flen, secsyms=None, labels=None):
    """objdump function -> canonical raw lines (REL addends folded into %hi/%lo like splat;
    R_MIPS_PC16 branch placeholders resolved against `labels`)."""
    insns = f["insns"]
    hi_val = {}
    out = []
    for k, ins in enumerate(insns):
        extra = {}
        for rtype, sym in ins[4]:
            if rtype == "R_MIPS_HI16":
                hops = split_ops(ins[2])
                hi, dreg = int(hops[-1], 0), hops[0]
                lo = None
                first = None
                for ins2 in insns[k + 1:]:
                    if any(t == "R_MIPS_LO16" and s == sym for t, s in ins2[4]):
                        o2 = split_ops(ins2[2])
                        m = MEM_RE.match(o2[-1])
                        base = m.group(2) if m else (o2[1] if len(o2) > 2 else None)
                        if first is None:
                            first = lo_imm(o2[-1])
                        if base == dreg:
                            lo = lo_imm(o2[-1])
                            break
                lo = lo if lo is not None else (first or 0)
                hi_val[sym] = hi
                extra[rtype] = ((hi << 16) + lo) & 0xFFFFFFFF
            elif rtype == "R_MIPS_LO16":
                v = (hi_val.get(sym, 0) << 16) + lo_imm(split_ops(ins[2])[-1])
                extra[rtype] = v & 0xFFFFFFFF
        out.append(objdump_insn_to_raw(f["start"], flen, ins, extra, secsyms, labels))
    return out


def objdump_insn_to_raw(fstart, flen, insn, addends=None, secsyms=None, labels=None):
    off, mn, opstr, _src, relocs = insn
    ops = split_ops(opstr)
    addends = addends or {}
    for rtype, sym in relocs:
        sym = canon_sym(sym)
        add = addends.get(rtype, 0)
        if add >= 0x80000000:
            add -= 0x100000000
        if rtype == "R_MIPS_26":
            if sym.startswith("."):
                tm = O_TARGET_RE.match(ops[-1]) if ops else None
                sym = canon_sym(tm.group(2)) if tm and not tm.group(3) else sym
            ops = ops[:-1] + [sym]
        elif rtype == "R_MIPS_HI16":
            ops = ops[:-1] + ["%%hi(%s)" % with_addend(sym, add, secsyms)]
        elif rtype == "R_MIPS_LO16":
            last = ops[-1]
            m = MEM_RE.match(last)
            if m:
                ops[-1] = "%%lo(%s)(%s)" % (with_addend(sym, add, secsyms), m.group(2))
            else:
                ops[-1] = "%%lo(%s)" % with_addend(sym, add, secsyms)
        elif rtype == "R_MIPS_PC16" and labels and sym in labels:
            # GAS leaves the branch offset as a placeholder (-1) plus a reloc against
            # the (global, jlabel'd) target; the address is only final at link time.
            # Resolve it from the dump's own label addresses so the raw form matches
            # the splat .s, which carries the final ROM encoding.
            if mn in BRANCHES and ops:
                ops[-1] = ".L%x" % (labels[sym] - fstart)
    if (mn in BRANCHES or mn == "j") and ops:
        tm = O_TARGET_RE.match(ops[-1])
        if tm:
            tgt = int(tm.group(1), 16)
            if fstart <= tgt < fstart + flen or mn != "j":
                ops[-1] = ".L%x" % (tgt - fstart)
    return make_raw(mn, ops)


# --------------------------------------------------------------------------------------
# splat .s parsing
# --------------------------------------------------------------------------------------

S_INSN_RE = re.compile(r"^\s*/\*\s*([0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)\s*\*/\s+(\S+)\s*(.*)$")


def parse_splat(path, func=None):
    """-> (name, [raw lines]) of the first function (or `func`) in a splat .s file."""
    insns = []
    name = None
    in_text = True
    for line in open(path, encoding="utf-8", errors="replace"):
        s = line.strip()
        if s.startswith(".section"):
            in_text = ".text" in s
            continue
        if s.startswith(("glabel", "dlabel", "jlabel")):
            if s.startswith("glabel") and in_text and len(s.split()) > 1:
                lab = s.split()[1]
                if name is None and (func is None or lab == func):
                    name = lab
            continue
        if not in_text or name is None:
            continue
        m = S_INSN_RE.match(line)
        if not m or m.group(4).startswith("."):
            continue
        # hand-edited .s files carry trailing /* ... */ comments on operands
        ops = re.sub(r"/\*.*?\*/", "", m.group(5).split("#")[0]).strip()
        insns.append((int(m.group(2), 16), m.group(4), ops))
    if not insns:
        return name, []
    base = insns[0][0]
    out = []
    for vram, mn, opstr in insns:
        ops = split_ops(opstr)
        if (mn in BRANCHES or mn == "j") and ops and re.match(r"^\.L[0-9A-Fa-f]+$", ops[-1]):
            ops[-1] = ".L%x" % (int(ops[-1][2:], 16) - base)
        out.append(make_raw(mn, ops))
    return name, out


# --------------------------------------------------------------------------------------
# C source parsing
# --------------------------------------------------------------------------------------

def mask_c(text):
    """Blank comments, strings, char literals and preprocessor lines (keep newlines)."""
    out = list(text)
    i, n = 0, len(text)
    bol = True
    while i < n:
        c = text[i]
        if bol and c in " \t":
            i += 1
            continue
        if bol and c == "#":
            j = i
            while j < n:
                if text[j] == "\n" and text[j - 1] != "\\":
                    break
                j += 1
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
            continue
        bol = False
        if c == "\n":
            bol = True
            i += 1
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = " "
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            for k in range(i + 1, min(j, n)):
                out[k] = " "
            i = j + 1
        else:
            i += 1
    return "".join(out)


def parse_c_defs(text):
    """-> list of (name, start_line, end_line) of function definitions (1-based, inclusive)."""
    m = mask_c(text)
    defs = []
    depth = 0
    line_starts = [0] + [i + 1 for i, ch in enumerate(text) if ch == "\n"]

    def lineno(pos):
        return bisect.bisect_right(line_starts, pos)

    i, n = 0, len(m)
    while i < n:
        ch = m[i]
        if ch == "{":
            if depth == 0:
                j = i - 1
                while j >= 0 and m[j].isspace():
                    j -= 1
                if j >= 0 and m[j] == ")":
                    d, k = 0, j
                    while k >= 0:
                        if m[k] == ")":
                            d += 1
                        elif m[k] == "(":
                            d -= 1
                            if d == 0:
                                break
                        k -= 1
                    k -= 1
                    while k >= 0 and m[k].isspace():
                        k -= 1
                    e = k + 1
                    while k >= 0 and (m[k].isalnum() or m[k] == "_"):
                        k -= 1
                    name = m[k + 1:e]
                    if name and name not in ("if", "while", "for", "switch") and not name[0].isdigit():
                        # body end
                        d2, p = 0, i
                        while p < n:
                            if m[p] == "{":
                                d2 += 1
                            elif m[p] == "}":
                                d2 -= 1
                                if d2 == 0:
                                    break
                            p += 1
                        sl = lineno(k + 1)
                        # include return-type line(s) above when the name starts its line
                        ls = line_starts[sl - 1]
                        if not m[ls:k + 1].strip() and sl > 1:
                            prev = text[line_starts[sl - 2]:line_starts[sl - 1]].strip()
                            if prev and not prev.endswith((";", "}", "{", "*/")) and not prev.startswith("#"):
                                sl -= 1
                        defs.append((name, sl, lineno(p)))
                        depth = 0
                        i = p + 1
                        continue
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)
        i += 1
    return defs


GLOBAL_ASM_RE = re.compile(r'^\s*#pragma\s+GLOBAL_ASM\(\s*"([^"]+)"\s*\)', re.M)


# --------------------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------------------

MK_RE = re.compile(r"^build/(src/\S+)\.o:\s*(CC|OPTFLAGS|CFLAGS|MIPS_VERSION)\s*(\+?=|:=)\s*(.*)$")


def makefile_flags():
    """Per-file compiler overrides from the Makefile -> list of (glob, var, op, value)."""
    out = []
    try:
        for line in open(os.path.join(REPO, "Makefile")):
            m = MK_RE.match(line.strip())
            if m:
                out.append((m.group(1).replace("%", "*") + ".c", m.group(2), m.group(3), m.group(4).strip()))
    except OSError:
        pass
    return out


def cc_tag(crel, mkflags):
    """'' for the standard IDO 7.1 -O2 build, else a short description."""
    import fnmatch
    tags = []
    for pat, var, op, val in mkflags:
        if fnmatch.fnmatch(crel, pat):
            if var == "CC" and "OLD" in val:
                tags.append("ido5.3")
            elif var == "OPTFLAGS" and not (op == ":=" and val == "-O2"):
                tags.append(val)
            elif var == "CFLAGS" and "-signed" in val:
                tags.append("-signed")
            elif var == "MIPS_VERSION":
                tags.append(val)
    return " ".join(tags)


def cmd_build(args):
    t0 = time.time()
    mkflags = makefile_flags()
    objs = sorted(glob.glob(os.path.join(REPO, "build", "src", "**", "*.o"), recursive=True))
    jobs = []
    for o in objs:
        rel = os.path.relpath(o, os.path.join(REPO, "build"))
        c = os.path.join(REPO, rel[:-2] + ".c")
        if os.path.isfile(c):
            jobs.append((o, c))
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        dumps = list(ex.map(lambda oc: (objdump(oc[0]), symtab(oc[0])), jobs))
    t1 = time.time()

    functions = []
    nfiles = 0
    for (o, c), (dump, secsyms) in zip(jobs, dumps):
        funcs, labels = parse_objdump(dump)
        if not funcs:
            continue
        nfiles += 1
        ctext = open(c, encoding="utf-8", errors="replace").read()
        clines = ctext.split("\n")
        defs = collections.defaultdict(list)
        for name, sl, el in parse_c_defs(ctext):
            defs[name].append((sl, el))
        unmatched = {os.path.basename(p)[:-2] for p in GLOBAL_ASM_RE.findall(ctext)}
        crel = os.path.relpath(c, REPO)
        cc = cc_tag(crel, mkflags)
        for fi, f in enumerate(funcs):
            fend = funcs[fi + 1]["start"] if fi + 1 < len(funcs) else f["insns"][-1][0] + 4
            flen = fend - f["start"]
            name = f["name"]
            matched = name not in unmatched
            srcl = [ins[3] for ins in f["insns"]]
            cands = defs.get(name, [])
            if not cands:   # static renamed by asm-processor, e.g. <file>_<name>
                for dn, dl in defs.items():
                    if name.endswith("_" + dn) or name.endswith(dn):
                        cands = dl
                        break
            best = None
            if cands:
                def score(r):
                    return sum(1 for s in srcl if r[0] <= s <= r[1])
                best = max(cands, key=score)
            raw = func_to_raw(f, flen, secsyms, labels)
            rec = {
                "name": name, "file": crel, "matched": matched, "cc": cc,
                "line": best[0] if best else 0, "end": best[1] if best else 0,
                "c": "\n".join(clines[best[0] - 1:best[1]]) if best else "",
                "raw": raw, "norm": [normalize(r) for r in raw],
                "src": srcl if matched else [0] * len(raw),
            }
            functions.append(rec)
    t2 = time.time()
    meta = {
        "version": FORMAT_VERSION, "built": time.strftime("%Y-%m-%d %H:%M:%S"),
        "build_seconds": round(t2 - t0, 1), "objdump_seconds": round(t1 - t0, 1),
        "objects": nfiles, "functions": len(functions),
        "matched": sum(1 for f in functions if f["matched"]),
        "with_c": sum(1 for f in functions if f["matched"] and f["c"]),
        "instructions": sum(len(f["raw"]) for f in functions),
    }
    os.makedirs(CORPUS_DIR, exist_ok=True)
    tmp = INDEX + ".tmp"
    with open(tmp, "w") as fp:
        json.dump({"meta": meta, "functions": functions}, fp, separators=(",", ":"))
    os.replace(tmp, INDEX)
    meta["index_bytes"] = os.path.getsize(INDEX)
    print("built %s" % os.path.relpath(INDEX, REPO))
    for k, v in meta.items():
        print("  %-16s %s" % (k, v))
    missing = [f["name"] for f in functions if f["matched"] and not f["c"]]
    if missing:
        print("  matched functions without C body located: %d (e.g. %s)" % (len(missing), ", ".join(missing[:5])))
    t3 = time.time()
    build_siblings({"meta": meta, "functions": functions})
    print("built %s  (%.1fs, %d bytes)" % (os.path.relpath(SIB_INDEX, REPO), time.time() - t3,
                                          os.path.getsize(SIB_INDEX)))


def load_index():
    if not os.path.isfile(INDEX):
        sys.exit("no index; run: corpus.py build")
    with open(INDEX) as fp:
        idx = json.load(fp)
    if idx["meta"].get("version") != FORMAT_VERSION:
        sys.exit("index format changed; run: corpus.py build")
    return idx


SP_OFF_RE = re.compile(r"(-?0x[0-9a-f]+)\(sp\)")


def keep_sp(norm, raw):
    """norm form but with the real stack offset kept (for stack-slot questions)."""
    m = SP_OFF_RE.search(raw)
    return norm.replace("N(sp)", m.group(1) + "(sp)") if m else norm


def regs_form(raw):
    """Real registers kept, symbols/labels/most immediates abstracted (for register-allocation questions)."""
    mn = raw.split(" ", 1)[0]
    s = re.sub(r"%(hi|lo)\([^)]*\)", r"%\1(SYM)", raw)
    s = re.sub(r"\.L[0-9a-f]+", "L", s)
    if mn in ("jal", "j"):
        return mn + " SYM"
    if mn not in KEEP_IMM:
        s = HEXNUM_RE.sub("N", s)
    return s


def form_of(f, form):
    if form == "raw":
        return f["raw"]
    if form == "regs":
        if "_regs" not in f:
            f["_regs"] = [regs_form(r) for r in f["raw"]]
        return f["_regs"]
    if form == "normsp":
        if "_normsp" not in f:
            f["_normsp"] = [keep_sp(n, r) for n, r in zip(f["norm"], f["raw"])]
        return f["_normsp"]
    if form == "loose":
        if "_loose" not in f:
            f["_loose"] = [loosen(x) for x in f["norm"]]
        return f["_loose"]
    return f["norm"]


# --------------------------------------------------------------------------------------
# display helpers
# --------------------------------------------------------------------------------------

def fmt_asm(line):
    p = line.split(" ", 1)
    return "%-7s %s" % (p[0], p[1]) if len(p) > 1 else p[0]


def show_snippet(f, lo, hi, marks, ctx=2, out=print, c_lines=True):
    """Print asm f[lo:hi] (+ctx) with markers, then the C lines it came from."""
    a, b = max(0, lo - ctx), min(len(f["raw"]), hi + ctx)
    for i in range(a, b):
        mk = ">" if i in marks else " "
        src = f["src"][i]
        out("   %s %4x  %-44s %s" % (mk, i * 4, fmt_asm(f["raw"][i]), ("L%d" % src) if src else ""))
    if c_lines and f["c"]:
        clines = f["c"].split("\n")
        used = {f["src"][i] for i in range(lo, hi) if f["src"][i]}
        around = {f["src"][i] for i in range(a, b) if f["src"][i]}
        if used:
            out("     C (%s):  '>' = lines that produced the marked asm" % f["file"])
            lo_l, hi_l = min(around), max(around)
            if hi_l - lo_l > 10:   # keep it short: matched lines plus their neighbours
                lines = sorted({x for u in used for x in (u - 1, u, u + 1)})
            else:
                lines = range(lo_l, hi_l + 1)
            prev = None
            for l2 in lines:
                k = l2 - f["line"]
                if 0 <= k < len(clines):
                    if prev is not None and l2 != prev + 1:
                        out("          ...")
                    out("   %s %5d| %s" % (">" if l2 in used else " ", l2, clines[k].rstrip()))
                    prev = l2


def show_c(f, out=print, mark=()):
    out("     --- C %s:%d-%d ---" % (f["file"], f["line"], f["end"]))
    for k, l in enumerate(f["c"].split("\n")):
        ln = f["line"] + k
        out("   %s%5d| %s" % (">" if ln in mark else " ", ln, l.rstrip()))


# --------------------------------------------------------------------------------------
# search
# --------------------------------------------------------------------------------------

def window_for(pattern, n):
    return max(n, pattern.count("\\n") + pattern.count("\n") + 1)


def cmd_search(args):
    idx = load_index()
    form = "raw" if args.raw else ("loose" if args.loose else "norm")
    flags = re.M | (re.I if args.ignore_case else 0)
    try:
        rx = re.compile(args.pattern, flags)
    except re.error as e:
        sys.exit("bad regex: %s" % e)
    W = window_for(args.pattern, args.window)
    results = []
    for f in idx["functions"]:
        if (not f["matched"] and not args.all) or (f.get("cc") and not args.any_cc):
            continue
        if args.file and args.file not in f["file"]:
            continue
        lines = form_of(f, form)
        sites = {}
        n = len(lines)
        for i in range(max(1, n - W + 1)):
            text = "\n".join(lines[i:i + W])
            for m in rx.finditer(text):
                s = i + text.count("\n", 0, m.start())
                e = i + text.count("\n", 0, max(m.start(), m.end() - 1)) + 1
                if s not in sites:
                    sites[s] = e
            if args.max_sites and len(sites) >= 10000:
                break
        if sites:
            results.append((len(sites), len(lines), f, sorted(sites.items())))
    if args.sort == "size":
        results.sort(key=lambda r: (r[1], -r[0]))
    else:
        results.sort(key=lambda r: (-r[0], r[1]))
    total = sum(r[0] for r in results)
    print("pattern %r  form=%s window=%d: %d sites in %d functions%s"
          % (args.pattern, form, W, total, len(results), "" if args.all else " (matched only)"))
    if args.count:
        return
    for cnt, size, f, sites in results[:args.limit]:
        print()
        print("== %s  %s:%d  [%d hit%s, %d insns]%s" % (f["name"], f["file"], f["line"], cnt, "s" * (cnt != 1),
                                                       size, "" if f["matched"] else "  UNMATCHED(draft C)"))
        for s, e in sites[:args.show]:
            show_snippet(f, s, e, set(range(s, e)), ctx=args.context)
            print()
        if cnt > args.show:
            print("   ... %d more sites" % (cnt - args.show))
        if args.c and f["c"]:
            mark = {f["src"][i] for s, e in sites for i in range(s, e)}
            show_c(f, mark=mark)


# --------------------------------------------------------------------------------------
# near
# --------------------------------------------------------------------------------------

_NONMATCH = None


def find_target_asm(func):
    """First asm/us/nonmatchings/**/FUNC.s (one-time walk; a per-func glob is far too slow
    for --all-unmatched / selftest, which look up thousands of functions)."""
    global _NONMATCH
    if _NONMATCH is None:
        _NONMATCH = {}
        for dp, _, fns in os.walk(os.path.join(REPO, "asm", "us", "nonmatchings")):
            for fn in fns:
                if fn.endswith(".s"):
                    _NONMATCH.setdefault(fn[:-2], os.path.join(dp, fn))
    return _NONMATCH.get(func)


def find_src_for(func):
    for c in glob.glob(os.path.join(REPO, "src", "**", "*.c"), recursive=True):
        try:
            t = open(c, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if "/%s.s\"" % func in t:
            return c
    return None


def parse_fd_diff(path, ntarget):
    """asm-differ `--format plain` output (what fd.sh saves to /tmp/fd_last_FUNC.txt) ->
    ({target index: marker}, {target index: current-side text}).
    Markers: r=reg, i=imm, s=stack, |=other, <=only in target, >=only in current."""
    diff, cur = {}, {}
    started = False
    first = None
    last = -1
    for line in open(path, errors="replace"):
        line = line.rstrip("\n")
        if line.startswith("TARGET"):
            started = True
            continue
        if not started or not line.strip():
            continue
        lm = re.match(r"^([0-9a-f]+):\s", line)
        rights = [m for m in re.finditer(r"\s([0-9a-f]+):\s", line)]
        right = rights[-1] if rights else None
        mid = line[(lm.end() if lm else 0):(right.start() + 1 if right else len(line))]
        mm = re.search(r"\s([rils<>|])\s+(?:\d+\s*)?$", " " + mid)
        if lm:
            addr = int(lm.group(1), 16)
            if first is None:
                first = addr
            k = (addr - first) // 4
            last = k
        else:
            k = last + 1   # insertion in current: attach to the next target line
        if mm and 0 <= k < ntarget:
            mk = mm.group(1)
            diff[k] = diff.get(k, mk) if diff.get(k) not in (None, "s") else mk
            if right:
                cur[k] = (cur[k] + " ; " if k in cur and not lm else "") + line[right.end():].strip()
            elif mk == "<":
                cur[k] = "(missing)"
    return diff, cur


def compile_draft(func):
    """Compile the NON_MATCHING draft of func from a copy under build/corpus/draft -> (obj, csrc, src)."""
    src = find_src_for(func)
    if not src:
        sys.exit("no src file with GLOBAL_ASM for %s" % func)
    lines = open(src, encoding="utf-8").read().split("\n")
    p = next(i for i, l in enumerate(lines) if ("/%s.s\"" % func) in l and "GLOBAL_ASM" in l)
    depth, k, else_at = 0, p - 1, None
    while k >= 0:
        s = lines[k].strip()
        if s.startswith("#endif"):
            depth += 1
        elif s.startswith("#if"):
            if depth == 0:
                break
            depth -= 1
        elif s.startswith("#else") and depth == 0:
            else_at = k
        k -= 1
    if k < 0 or else_at is None:
        sys.exit("%s has no #if ... #else draft around its GLOBAL_ASM" % func)
    lines[k] = "#if 1"
    ddir = os.path.join(CORPUS_DIR, "draft")
    os.makedirs(ddir, exist_ok=True)
    csrc = os.path.join(ddir, os.path.basename(src))
    obj = csrc[:-2] + ".o"
    with open(csrc, "w", encoding="utf-8") as fp:
        fp.write("\n".join(lines))
    rel_src = os.path.relpath(src, REPO)
    rel_obj = os.path.join("build", rel_src[:-2] + ".o")
    env = dict(os.environ, PATH=TOOL_PATH)
    mk = subprocess.run(["make", "-n", "-W", rel_src, rel_obj, "PYTHON=" + os.path.join(REPO, ".venv/bin/python3")],
                        cwd=REPO, capture_output=True, text=True, env=env)
    # Stadium 2 has no preprocess.sh; compile lines are either
    #   tools/coalesce_cc.py -c <flags> -o build/src/X.o src/X.c
    # or (files with GLOBAL_ASM/C_FUNCTION_PADDING, or IDO 5.3):
    #   tools/asm-processor/build.py ... [tools/coalesce_cc.py|tools/ido/.../cc] -- mips-linux-gnu-as ... -- -c <flags> -o build/src/X.o src/X.c
    # Both end with `-o <obj> <src>`; the gcc -fsyntax-only check line matches neither marker.
    cmd = next((l for l in mk.stdout.splitlines() if "tools/coalesce_cc.py" in l or "tools/ido/" in l), None)
    if not cmd:
        sys.exit("could not get compile command from make -n:\n" + mk.stdout[-2000:] + mk.stderr[-2000:])
    argv = shlex.split(cmd)
    argv = [obj if a == rel_obj else a for a in argv]
    assert argv[-1] == rel_src, argv[-3:]
    argv = argv[:-1] + ["-I", os.path.dirname(rel_src), csrc]
    r = subprocess.run(argv, cwd=REPO, capture_output=True, text=True, env=env)
    errs = [l for l in (r.stdout + r.stderr).splitlines() if "rror" in l and "cfe: Warning" not in l]
    if r.returncode != 0 or not os.path.isfile(obj):
        sys.exit("draft compile failed:\n" + "\n".join(errs[:20] or (r.stdout + r.stderr).splitlines()[-20:]))
    return obj, csrc, src


def draft_func(obj, func):
    funcs, labels = parse_objdump(objdump(obj))
    for i, f in enumerate(funcs):
        if f["name"] == func:
            fend = funcs[i + 1]["start"] if i + 1 < len(funcs) else f["insns"][-1][0] + 4
            raw = func_to_raw(f, fend - f["start"], symtab(obj), labels)
            return raw, [ins[3] for ins in f["insns"]]
    sys.exit("%s not found in draft object" % func)


def diffkey(raw):
    """Like asm-differ: relocated symbols compare equal (.bss+0x18 vs D_84390020)."""
    return re.sub(r"%(hi|lo)\([^)]*\)", r"%\1(SYM)", raw)


def build_ngrams(funcs, form, W):
    ng = collections.defaultdict(list)
    for fi, f in enumerate(funcs):
        lines = form_of(f, form)
        for i in range(len(lines) - W + 1):
            ng[tuple(lines[i:i + W])].append((fi, i))
    return ng


def regions_of(idxs, gap=2):
    out = []
    for i in sorted(idxs):
        if out and i - out[-1][1] <= gap:
            out[-1][1] = i
        else:
            out.append([i, i])
    return out


def classify(t, d):
    """Kind of difference between a target and a draft raw line (asm-differ-like markers)."""
    if d is None:
        return "<"
    if t is None:
        return ">"
    kt, kd = diffkey(t), diffkey(d)
    if kt == kd:
        return " "
    sp = re.compile(r"-?0x[0-9a-f]+\(sp\)")
    if sp.sub("N(sp)", kt) == sp.sub("N(sp)", kd):
        return "s"
    if normalize(kt) == normalize(kd) and kt.split(" ")[0] == kd.split(" ")[0]:
        return "r" if loosen(normalize(kt)) == loosen(normalize(kd)) else "i"
    return "|"


def cmd_near(args):
    func = args.func
    tpath = find_target_asm(func)
    if not tpath:
        sys.exit("no asm/us/nonmatchings/**/%s.s" % func)
    _, traw = parse_splat(tpath, func)
    tnorm = [normalize(x) for x in traw]
    idx = load_index()
    funcs = [f for f in idx["functions"] if f["matched"] and f["name"] != func and (args.any_cc or not f.get("cc"))]

    diff, cur_side, draft_raw, draft_src, src_file, draft_map = None, {}, None, None, None, {}
    fdpath = args.diff or "/tmp/fd_last_%s.txt" % func
    whole = False
    if args.draft:
        obj, _csrc, src_file = compile_draft(func)
        draft_raw, draft_src = draft_func(obj, func)
        sm = difflib.SequenceMatcher(None, [diffkey(x) for x in traw], [diffkey(x) for x in draft_raw],
                                     autojunk=False)
        diff = {}
        for tag, a1, a2, b1, b2 in sm.get_opcodes():
            if tag == "equal":
                continue
            if tag == "replace" and a2 - a1 == b2 - b1:
                for k in range(a2 - a1):
                    diff[a1 + k] = classify(traw[a1 + k], draft_raw[b1 + k])
                    draft_map[a1 + k] = (b1 + k, b1 + k + 1)
            elif a2 > a1:
                for k in range(a1, a2):
                    diff[k] = "|" if b2 > b1 else "<"
                    draft_map[k] = (b1, b2)
            else:  # pure insertion in the draft
                k = min(a1, len(traw) - 1)
                diff[k] = ">"
                draft_map[k] = (b1, b2)
        for k, (b1, b2) in draft_map.items():
            cur_side[k] = " ; ".join(draft_raw[b1:b2]) or "(missing)"
        same = sum(a2 - a1 for tag, a1, a2, _, _ in sm.get_opcodes() if tag == "equal")
        mode = "draft %s: %d/%d target lines identical (symbols compared like asm-differ), %d draft insns" % (
            os.path.relpath(obj, REPO), same, len(traw), len(draft_raw))
        src_file = src_file
    elif os.path.isfile(fdpath):
        diff, cur_side = parse_fd_diff(fdpath, len(traw))
        mode = "fd diff %s: %d differing target lines" % (fdpath, len(diff))
        src_file = find_src_for(func)
    else:
        whole = True
        diff = {i: "?" for i in range(len(traw))}
        mode = "no diff (no %s; pass --draft or --diff FILE): rarest windows of the whole target" % fdpath

    print("near %s  target %s (%d insns)" % (func, os.path.relpath(tpath, REPO), len(traw)))
    print("mode: " + mode)
    if not diff:
        print("no differing lines")
        return
    kinds = collections.Counter(diff.values())
    if not whole:
        print("diff kinds: " + ", ".join("%s=%d" % ({"s": "stack", "r": "reg", "i": "imm", "|": "other",
                                                      "<": "target-only", ">": "draft-only"}.get(k, k), v)
                                       for k, v in kinds.most_common()))

    # lookup tiers: widest window first (most specific context), norm before loose
    widths = sorted({args.window + 2, args.window + 1, args.window, min(2, args.window)}, reverse=True) \
        if not whole else [args.window]
    forms = ["norm"] + ([] if args.no_loose else ["loose"])
    ngram_cache = {}

    def ngrams(form, W):
        if (form, W) not in ngram_cache:
            ngram_cache[(form, W)] = build_ngrams(funcs, form, W)
        return ngram_cache[(form, W)]

    tforms = {"norm": tnorm, "loose": [loosen(x) for x in tnorm],
              "normsp": [keep_sp(n, r) for n, r in zip(tnorm, traw)],
              "regs": [regs_form(r) for r in traw]}

    def tiers(forms, form_major):
        if form_major:
            return [(W, fm) for fm in forms for W in widths]
        return [(W, fm) for W in widths for fm in forms]

    def lookup(a, b, forms=forms, form_major=False):
        for W, form in tiers(forms, form_major):
            if True:
                tl = tforms[form]
                score = collections.defaultdict(float)
                where = collections.defaultdict(list)
                nwin = 0
                for s in range(max(0, a - W + 1), min(b, len(tl) - W) + 1):
                    hits = ngrams(form, W).get(tuple(tl[s:s + W]), [])
                    if not hits:
                        continue
                    nwin += 1
                    nf = len({fi for fi, _ in hits})
                    for fi, pos in hits:
                        score[fi] += 1.0 / nf
                        where[fi].append((pos, s))
                if score:
                    return W, form, score, where, nwin
        return None

    regions = []
    if whole:
        for i in range(len(traw) - args.window + 1):
            r = lookup(i, i)
            if r:
                regions.append((i, i + args.window - 1, r, max(r[2].values())))
        picked = []
        for r in sorted(regions, key=lambda r: -r[3]):   # rarest first, no overlapping regions
            if all(r[1] < q[0] - 2 or r[0] > q[1] + 2 for q in picked):
                picked.append(r)
            if len(picked) >= args.regions:
                break
        regions = sorted(picked, key=lambda r: r[0])
    else:
        for a, b in regions_of(diff.keys(), gap=args.gap):
            only_stack = all(diff[k] == "s" for k in range(a, b + 1) if k in diff)
            if only_stack and not args.stack:
                regions.append((a, b, "stack", 0))
            elif only_stack:
                # same shape with the same stack offsets: which C put temps in these slots?
                regions.append((a, b, lookup(a, b, forms=["normsp"]), 0))
            elif any(diff.get(k) == "r" for k in range(a, b + 1)):
                # register-allocation diff: prefer corpus code with the target's exact registers
                regions.append((a, b, lookup(a, b, forms=["regs"] + forms, form_major=True), 0))
            else:
                regions.append((a, b, lookup(a, b, forms=["regs"] + forms), 0))

    srcl = open(src_file, encoding="utf-8", errors="replace").read().split("\n") if src_file else None
    nstack = 0
    shown = 0
    for a, b, res, _ in regions:
        if res == "stack":
            nstack += 1
        if shown >= args.regions:
            continue
        shown += 1
        print()
        print("=" * 100)
        print("target region +0x%x..+0x%x  (insns %d-%d)%s" % (a * 4, b * 4, a, b,
              "  [stack-offset-only diff]" if res == "stack" else ""))
        ctx = 2
        for i in range(max(0, a - ctx), min(len(traw), b + ctx + 1)):
            mk = diff.get(i, " ") if not whole else (">" if a <= i <= b else " ")
            extra = ("   | draft: " + cur_side[i]) if cur_side.get(i) else ""
            print("   %s %4x  %-44s%s" % (mk, i * 4, fmt_asm(traw[i]), extra))
        if draft_raw is not None:
            js = sorted({j for i in range(a, b + 1) if i in draft_map for j in range(*draft_map[i])})
            cl = sorted({draft_src[j] for j in js if draft_src[j]})
            if cl and srcl:
                print("   draft C that emitted it (%s):" % os.path.relpath(src_file, REPO))
                for ln in cl[:8]:
                    print("     %5d| %s" % (ln, srcl[ln - 1].rstrip()))
        if res == "stack":
            print("   stack-slot-only: same instructions, different spill/local offsets. A shape lookup cannot")
            print("   tell slot order apart (see IDO_TRICKS.md 'Stack layout'); pass --stack to look it up anyway.")
            continue
        if not res:
            print("   (no matched function contains a %d..%d-insn window here, even loosely)"
                  % (min(widths), max(widths)))
            continue
        W, form, score, where, nwin = res
        ranked = sorted(score.items(), key=lambda kv: (-kv[1], len(funcs[kv[0]]["raw"])))
        print("   corpus: %d matched functions contain a %s %d-insn window of this region (%d windows hit)"
              % (len(score), form, W, nwin))
        for fi, sc in ranked[:args.limit]:
            f = funcs[fi]
            # take the cluster of hit positions around the first hit
            pos = sorted(p for p, _ in where[fi])
            p0 = pos[0]
            p1 = max(p for p in pos if p < p0 + 4 * W) + W
            print("   -- %s  %s:%d  score %.2f  [%d insns]" % (f["name"], f["file"], f["line"], sc, len(f["raw"])))
            show_snippet(f, p0, p1, set(range(p0, p1)), ctx=1, out=lambda s: print("   " + s))
            if args.c:
                show_c(f, out=lambda s: print("   " + s), mark={f["src"][i] for i in range(p0, p1)})
    if shown < len(regions):
        print("\n(%d more regions; --regions N to see more)" % (len(regions) - shown))
    if nstack:
        print("\n%d of %d regions are stack-offset-only." % (nstack, len(regions)))


# --------------------------------------------------------------------------------------
# siblings
# --------------------------------------------------------------------------------------

SIB_INDEX = os.path.join(CORPUS_DIR, "siblings.json")
SIB_VERSION = 1
SIB_NGRAMS = (1, 2, 3)
SIB_ALPHA = 0.3
SIB_FLOOR = 4.0
SIB_STRONG, SIB_POSSIBLE, SIB_WEAK = 0.45, 0.30, 0.22


def sib_features(norm):
    """norm lines -> Counter of hashed 1..3-gram keys (stable across runs)."""
    import hashlib
    c = collections.Counter()
    for n in SIB_NGRAMS:
        for k in range(len(norm) - n + 1):
            key = ("%d|" % n + "\n".join(norm[k:k + n])).encode()
            c[hashlib.blake2b(key, digest_size=6).hexdigest()] += 1
    return c


def build_siblings(idx):
    """Postings {gram: [fi, count, fi, count, ...]} over matched functions + per-function weights."""
    fns = idx["functions"]
    feats = [sib_features(f["norm"]) for f in fns]
    post = collections.defaultdict(list)
    for fi, (f, c) in enumerate(zip(fns, feats)):
        if f["matched"]:
            for g, v in c.items():
                post[g].append(fi)
                post[g].append(v)
    m = sum(1 for f in fns if f["matched"])
    idf_max = math.log(m + 1)
    weight = []
    for c in feats:
        weight.append(round(sum(v * math.log((m + 1) / (len(post.get(g, ())) // 2 + 1)) for g, v in c.items()), 4))
    data = {"version": SIB_VERSION, "index_built": idx["meta"]["built"], "matched": m,
            "idf_max": idf_max, "weight": weight, "post": post}
    tmp = SIB_INDEX + ".tmp"
    with open(tmp, "w") as fp:
        json.dump(data, fp, separators=(",", ":"))
    os.replace(tmp, SIB_INDEX)
    return data


def load_siblings(idx):
    if os.path.isfile(SIB_INDEX):
        with open(SIB_INDEX) as fp:
            data = json.load(fp)
        if data.get("version") == SIB_VERSION and data.get("index_built") == idx["meta"]["built"]:
            return data
    print("(building %s ...)" % os.path.relpath(SIB_INDEX, REPO), file=sys.stderr)
    return build_siblings(idx)


def sib_rank(qnorm, data, fns, skip=-1, any_cc=False):
    """-> [(score, fi, shared, q-in-s, s-in-q)] best first."""
    m = data["matched"]
    post, weight = data["post"], data["weight"]
    shared = collections.defaultdict(float)
    wq = 0.0
    for g, v in sib_features(qnorm).items():
        pl = post.get(g)
        if not pl:
            wq += v * math.log(m + 1)
            continue
        w = math.log((m + 1) / (len(pl) // 2 + 1))
        wq += v * w
        for k in range(0, len(pl), 2):
            shared[pl[k]] += w * min(v, pl[k + 1])
    out = []
    for fi, s in shared.items():
        if fi == skip or (fns[fi].get("cc") and not any_cc):
            continue
        wc = weight[fi]
        lo, hi = min(wq, wc), max(wq, wc)
        if lo <= 0:
            continue
        # containment credit only down to 1/SIB_FLOOR of the bigger side: a 9-insn helper fully
        # contained in a 120-insn function is an idiom, not a sibling
        out.append((s / max(lo, hi / SIB_FLOOR) * (lo / hi) ** SIB_ALPHA, fi, s, s / wq, s / wc))
    out.sort(key=lambda r: (-r[0], len(fns[r[1]]["norm"])))
    return out


def sib_query(func, idx, name2i):
    """FUNC -> (norm lines, location string, index of FUNC in idx or -1)."""
    fi = name2i.get(func, -1)
    tpath = find_target_asm(func)
    if fi >= 0 and idx["functions"][fi]["matched"]:
        f = idx["functions"][fi]
        return f["norm"], "%s:%d (matched)" % (f["file"], f["line"]), fi
    if tpath:
        _, raw = parse_splat(tpath, func)
        if raw:
            return [normalize(r) for r in raw], os.path.relpath(tpath, REPO) + " (unmatched)", fi
    if fi >= 0:
        f = idx["functions"][fi]
        return f["norm"], "%s (unmatched, from build .o)" % f["file"], fi
    sys.exit("%s: not in the index and no asm/us/nonmatchings/**/%s.s" % (func, func))


def sib_label(score):
    return "STRONG" if score >= SIB_STRONG else ("possible" if score >= SIB_POSSIBLE else
                                                 ("weak" if score >= SIB_WEAK else ""))


def sib_block(func, idx, data, name2i, args, out=print):
    """Print one siblings block; return the ranked list."""
    fns = idx["functions"]
    qnorm, where, qi = sib_query(func, idx, name2i)
    ranked = [r for r in sib_rank(qnorm, data, fns, skip=qi, any_cc=args.any_cc) if r[0] >= args.min_score]
    m = data["matched"]

    def line_w(x):
        return math.log((m + 1) / (len(data["post"].get(next(iter(sib_features([x]))), ())) // 2 + 1))

    out("siblings of %s  %s  [%d insns]" % (func, where, len(qnorm)))
    if not ranked:
        out("   (no matched function shares any weighted n-gram above --min-score)")
        return ranked, len(qnorm)
    out("   %-5s  %-6s %-6s %-6s %-7s  %-30s %-44s %s" % ("score", "q-in-s", "s-in-q", "align", "insns", "sibling",
                                                       "file:line", "most distinctive common norm run"))
    for score, fi, _s, cq, cs in ranked[:args.limit]:
        f = fns[fi]
        sm = difflib.SequenceMatcher(None, qnorm, f["norm"], autojunk=False)
        blocks = [blk for blk in sm.get_matching_blocks() if blk.size]
        aligned = sum(blk.size for blk in blocks) / max(1, len(qnorm))
        # most distinctive aligned run (IDF-weighted), so a shared epilogue does not win on length
        a, b, n = max(blocks, key=lambda blk: sum(line_w(x) for x in qnorm[blk.a:blk.a + blk.size])) \
            if blocks else (0, 0, 0)
        srcs = [x for x in f["src"][b:b + n] if x]
        cl = (" C L%d-%d" % (min(srcs), max(srcs))) if srcs else ""
        out("   %.3f  %-6.2f %-6.2f %-6.2f %-7d  %-30s %-44s %d insns: q %d-%d ~ s %d-%d%s  %s" % (
            score, cq, cs, aligned, len(f["norm"]), f["name"], "%s:%d" % (f["file"], f["line"]), n,
            a, a + n - 1, b, b + n - 1, cl, sib_label(score)))
    if args.c:
        for score, fi, _s, _cq, _cs in ranked[:args.limit]:
            f = fns[fi]
            out("")
            out("   == %s  (score %.3f)" % (f["name"], score))
            show_c(f, out=lambda s: out("   " + s))
    return ranked, len(qnorm)


def cmd_siblings(args):
    t0 = time.time()
    idx = load_index()
    data = load_siblings(idx)
    fns = idx["functions"]
    name2i = {}
    for i, f in enumerate(fns):
        name2i.setdefault(f["name"], i)
    if args.all_unmatched:
        names = [f["name"] for f in fns if not f["matched"]]
    elif args.func:
        names = [args.func]
    else:
        sys.exit("give FUNC or --all-unmatched")
    summary = []
    for k, func in enumerate(names):
        if k:
            print()
            print("=" * 100)
        ranked, qn = sib_block(func, idx, data, name2i, args)
        summary.append((func, qn, ranked[0] if ranked else None))
    if args.all_unmatched:
        print()
        print("=" * 100)
        print("SUMMARY: best matched sibling per unmatched function (STRONG >= %.2f, possible >= %.2f, weak >= %.2f)"
              % (SIB_STRONG, SIB_POSSIBLE, SIB_WEAK))
        print("   %-16s %5s  %-30s %5s  %-6s %-6s %-6s %s" % ("function", "insns", "best sibling", "insns", "score",
                                                           "q-in-s", "s-in-q", ""))
        for func, qn, best in sorted(summary, key=lambda r: -(r[2][0] if r[2] else 0)):
            if best:
                f = fns[best[1]]
                print("   %-16s %5d  %-30s %5d  %-6.3f %-6.2f %-6.2f %s" % (func, qn, f["name"], len(f["norm"]),
                                                                    best[0], best[3], best[4], sib_label(best[0])))
            else:
                print("   %-16s %5d  -" % (func, qn))
    print("\n(%.1fs)" % (time.time() - t0), file=sys.stderr)


# --------------------------------------------------------------------------------------
# misc commands
# --------------------------------------------------------------------------------------

def cmd_show(args):
    idx = load_index()
    for f in idx["functions"]:
        if f["name"] == args.func:
            print("%s  %s:%d  matched=%s  %d insns" % (f["name"], f["file"], f["line"], f["matched"], len(f["raw"])))
            lines = form_of(f, "norm" if args.norm else "raw")
            for i, l in enumerate(lines):
                src = f["src"][i]
                txt = ""
                if src and f["c"]:
                    k = src - f["line"]
                    cl = f["c"].split("\n")
                    if 0 <= k < len(cl) and (i == 0 or f["src"][i - 1] != src):
                        txt = cl[k].strip()
                print("  %4x  %-44s %-6s %s" % (i * 4, fmt_asm(l), ("L%d" % src) if src else "", txt))
            return
    sys.exit("not in index: " + args.func)


def cmd_norm(args):
    name, raw = parse_splat(args.path)
    print("# %s" % name)
    for r in raw:
        print(r if args.raw else normalize(r))


def cmd_selftest(args):
    """Round-trip check: unmatched (GLOBAL_ASM) functions exist both in build .o and in the
    splat .s; their canonical raw forms must be identical."""
    idx = load_index()
    bad = 0
    n = 0
    for f in idx["functions"]:
        if f["matched"]:
            continue
        tp = find_target_asm(f["name"])
        if not tp:
            continue
        n += 1
        _, raw = parse_splat(tp, f["name"])
        if raw != f["raw"]:
            bad += 1
            print("MISMATCH %s (%d vs %d)" % (f["name"], len(raw), len(f["raw"])))
            shown = 0
            for i, (x, y) in enumerate(zip(raw, f["raw"])):
                if x != y:
                    print("   %4x  splat: %-40s obj: %s" % (i * 4, x, y))
                    shown += 1
                    if shown >= args.max:
                        break
    print("selftest: %d/%d unmatched functions round-trip identically" % (n - bad, n))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("build", help="(re)build build/corpus/index.json from build/src/**/*.o")
    p.add_argument("-j", "--jobs", type=int, default=8)
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("search", help="regex search over normalized (or raw) asm windows")
    p.add_argument("pattern")
    p.add_argument("--raw", action="store_true", help="match the raw form (real regs/symbols)")
    p.add_argument("--loose", action="store_true", help="match the loose form (all immediates -> N)")
    p.add_argument("--window", type=int, default=1, help="instructions per window (auto-grown to fit \\n)")
    p.add_argument("--c", action="store_true", help="print the whole C body of each hit")
    p.add_argument("--limit", type=int, default=10, help="functions to print")
    p.add_argument("--show", type=int, default=2, help="sites to print per function")
    p.add_argument("--context", type=int, default=2, help="asm context lines around a site")
    p.add_argument("--sort", choices=["count", "size"], default="count",
                   help="rank by hit count (default) or by smallest function first")
    p.add_argument("--file", help="only functions whose source path contains this")
    p.add_argument("--all", action="store_true", help="include unmatched (GLOBAL_ASM) functions")
    p.add_argument("--any-cc", action="store_true", help="also search files built with IDO 5.3 / -O0 / other per-file flags")
    p.add_argument("--count", action="store_true", help="only print the totals")
    p.add_argument("-i", "--ignore-case", action="store_true")
    p.add_argument("--max-sites", action="store_true", help=argparse.SUPPRESS)
    p.set_defaults(fn=cmd_search)

    p = sub.add_parser("near", help="for an unmatched function, find matched functions containing "
                                    "the target asm around each differing line")
    p.add_argument("func")
    p.add_argument("--diff", help="asm-differ plain output (default /tmp/fd_last_FUNC.txt)")
    p.add_argument("--draft", action="store_true",
                   help="compile the #ifdef NON_MATCHING draft (copy under build/corpus/draft) and diff it")
    p.add_argument("--window", type=int, default=3, help="instructions per lookup window (default 3)")
    p.add_argument("--gap", type=int, default=2, help="merge differing lines closer than this into one region")
    p.add_argument("--limit", type=int, default=3, help="corpus functions per region")
    p.add_argument("--regions", type=int, default=12, help="regions to print")
    p.add_argument("--no-loose", action="store_true", help="do not fall back to the loose form")
    p.add_argument("--any-cc", action="store_true", help="also use files built with IDO 5.3 / -O0 / other per-file flags")
    p.add_argument("--stack", action="store_true", help="also look up stack-offset-only regions")
    p.add_argument("--c", action="store_true", help="print whole C bodies (default: only the C lines hit)")
    p.set_defaults(fn=cmd_near)

    p = sub.add_parser("siblings", help="whole-function look-alikes of FUNC among the matched functions")
    p.add_argument("func", nargs="?")
    p.add_argument("--all-unmatched", action="store_true",
                   help="one block per unmatched (GLOBAL_ASM) function, then a summary table")
    p.add_argument("--limit", type=int, default=8, help="siblings per function (default 8)")
    p.add_argument("--min-score", type=float, default=0.0, help="hide siblings scoring below this")
    p.add_argument("--c", action="store_true", help="print each sibling's C body")
    p.add_argument("--any-cc", action="store_true", help="also use files built with IDO 5.3 / -O0 / other per-file flags")
    p.set_defaults(fn=cmd_siblings)

    p = sub.add_parser("show", help="print one indexed function with C line annotations")
    p.add_argument("func")
    p.add_argument("--norm", action="store_true")
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("norm", help="print a splat .s function in normalized (or --raw canonical) form")
    p.add_argument("path")
    p.add_argument("--raw", action="store_true")
    p.set_defaults(fn=cmd_norm)

    p = sub.add_parser("selftest", help="check objdump and splat parsing agree on the unmatched functions")
    p.add_argument("--max", type=int, default=6)
    p.set_defaults(fn=cmd_selftest)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
