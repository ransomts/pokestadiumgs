#!/home/tsranso/Code/pokestadiumgs/.venv/bin/python3
"""symcheck.py - find symbol-premise errors (wrong base symbol / negative addend /
access past a symbol's end) in the target asm of unmatched functions.

Background: splat names every referenced address after a symbol it knows, so
`D_86A03D40[arg5][arg6 - 6]` in the original source shows up in the target asm as
`%hi(D_86A03C98)` (the address 0xA8 below D_86A03D40 happens to be the start of the
PRECEDING array) plus loads at -0xA4(reg) off D_86A03D40.  A draft that believes the
splat name fights register allocation for hours.  This tool tracks every symbol
reference through the function's registers (lui/addiu/addu/sll/multu/...), computes
the real address of each access from the instruction words, and checks it against a
symbol map (address, size, declared type) built from the ELF, the linker map, the
symbol_addrs files, the data asm and the C definitions.

Usage:
  symcheck.py FUNC [--src FILE] [--asm FILE] [-v]
      Check one function.  The target asm is asm/us/nonmatchings/**/FUNC.s; if that
      file does not exist (function already matched) the function is rebuilt from the
      linked ELF (--elf, default build/pokestadiumgs-us.elf; uses --emit-relocs relocs).
      The draft is the `#ifdef NON_MATCHING` block before FUNC's GLOBAL_ASM pragma, or
      FUNC's definition when there is no pragma; --src overrides the C file.
  symcheck.py --all [-v]
      Every function with a GLOBAL_ASM pragma in src/: summary table.
  symcheck.py --matched-sample N [--seed S] [-v]
      Control run on N random matched C functions (rebuilt from the ELF; the draft is
      the matched C).  Reports the false-positive rate.
  symcheck.py FUNC --emit-asm OUT.s
      Write the ELF-rebuilt function in splat syntax (for testing / reading).

Flag kinds (severity H > M > L; the summary counts H and M as "flags"):
  neg      access/address below the start of the symbol it is named after (negative
           addend, incl. negative displacement off a register holding &sym + index).
  past     addend >= the symbol's known/estimated size; names the symbol the address
           really lands in (kind 'other').
  inside   the named symbol is not a known object start (splat/ld auto name) and the
           address lies inside a defined object.
  hilo     %hi/%lo pair whose combined address != named symbol + addend.
  alias    an indexed access through P reaches exactly the addresses that the same
           function also reaches as S - k (negative addend off S): P is probably S[.. - k].
  draft    draft-side patterns: `S[i - k]`, `(&S)[-k]`, `S - 0x..`, byte-offset casts,
           constant index >= declared dimension.
Draft consistency downgrades a flag (e.g. the draft already writes S[x - k], or does not
use the splat name at all) - see the [draft] line under each flag.
"""

import argparse
import bisect
import os
import random
import re
import struct
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEV_ORDER = {"H": 3, "M": 2, "L": 1, "I": 0}

# --------------------------------------------------------------------------------------
# ELF reader (ELF32 big-endian, linked with --emit-relocs)
# --------------------------------------------------------------------------------------


class Elf:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.data = f.read()
        d = self.data
        if d[:4] != b"\x7fELF":
            raise ValueError(path + ": not an ELF")
        (self.e_shoff,) = struct.unpack_from(">I", d, 0x20)
        self.e_shentsize, self.e_shnum, self.e_shstrndx = struct.unpack_from(">HHH", d, 0x2E)
        self.sections = []
        for i in range(self.e_shnum):
            off = self.e_shoff + i * self.e_shentsize
            name, typ, flags, addr, offset, size, link, info, align, entsize = struct.unpack_from(
                ">IIIIIIIIII", d, off
            )
            self.sections.append(
                dict(idx=i, name_off=name, type=typ, flags=flags, addr=addr, offset=offset,
                     size=size, link=link, info=info, entsize=entsize)
            )
        shstr = self.sections[self.e_shstrndx]
        for s in self.sections:
            s["name"] = self._str(shstr["offset"], s["name_off"])
        self.symbols = []
        symtab = next((s for s in self.sections if s["type"] == 2), None)
        if symtab:
            strtab = self.sections[symtab["link"]]
            for j in range(symtab["size"] // 16):
                nm, val, sz, info, other, shndx = struct.unpack_from(">IIIBBH", d, symtab["offset"] + j * 16)
                self.symbols.append(
                    dict(name=self._str(strtab["offset"], nm), value=val, size=sz,
                         type=info & 0xF, bind=info >> 4, shndx=shndx)
                )
        self.func_syms = {}
        for s in self.symbols:
            if s["type"] == 2 and s["shndx"] not in (0, 0xFFF1):
                self.func_syms.setdefault(s["name"], s)
        self._rel_cache = {}

    def _str(self, base, off):
        end = self.data.index(b"\0", base + off)
        return self.data[base + off:end].decode("latin1")

    def section_for(self, addr, need_exec=True):
        best = None
        for s in self.sections:
            if s["type"] != 1 or s["size"] == 0:
                continue
            if need_exec and not (s["flags"] & 4):
                continue
            if s["addr"] <= addr < s["addr"] + s["size"]:
                best = s
                break
        return best

    def words(self, sec, start, end):
        out = []
        for a in range(start, end, 4):
            (w,) = struct.unpack_from(">I", self.data, sec["offset"] + a - sec["addr"])
            out.append((a, w))
        return out

    def relocs_for(self, sec):
        key = sec["idx"]
        if key in self._rel_cache:
            return self._rel_cache[key]
        res = {}
        for s in self.sections:
            if s["type"] == 9 and s["info"] == sec["idx"]:
                for j in range(s["size"] // 8):
                    off, info = struct.unpack_from(">II", self.data, s["offset"] + j * 8)
                    symi, typ = info >> 8, info & 0xFF
                    sym = self.symbols[symi] if symi < len(self.symbols) else None
                    res.setdefault(off, []).append((typ, sym))
        self._rel_cache[key] = res
        return res


# --------------------------------------------------------------------------------------
# Symbol map
# --------------------------------------------------------------------------------------

PRIM_SIZES = {
    "u8": 1, "s8": 1, "char": 1, "unsigned char": 1, "signed char": 1, "UNK_TYPE1": 1, "bool": 1,
    "u16": 2, "s16": 2, "short": 2, "unsigned short": 2, "UNK_TYPE2": 2,
    "u32": 4, "s32": 4, "int": 4, "unsigned int": 4, "long": 4, "unsigned long": 4, "f32": 4,
    "float": 4, "UNK_TYPE4": 4, "UNK_TYPE": 4, "UNK_PTR": 4, "OSMesg": 4, "uintptr_t": 4, "size_t": 4,
    "u64": 8, "s64": 8, "f64": 8, "double": 8, "long long": 8, "unsigned long long": 8,
    "Gfx": 8, "Vtx": 0x10, "Mtx": 0x40, "MtxF": 0x40, "Vec3f": 0xC, "Vec3s": 6, "Vec3i": 0xC,
    "Color_RGB8": 3, "Color_RGBA8": 4, "Color_RGBA8_u32": 4, "Lights1": 0x18, "Lights2": 0x28,
    "OSMesgQueue": 0x18, "OSThread": 0x1B0, "OSTimer": 0x20, "OSContPad": 6, "OSContStatus": 4,
    "Vp": 0x10, "LookAt": 0x20, "OSIoMesg": 0x18, "OSPiHandle": 0x74,
}

DECL_RE = re.compile(
    r"^\s*(?P<extern>extern\s+)?(?P<static>static\s+)?(?:const\s+|volatile\s+|UNUSED\s+)*"
    r"(?P<type>(?:struct\s+|union\s+|unsigned\s+|signed\s+)?[A-Za-z_]\w*(?:\s+const)?[\s\*]+?)"
    r"\s*(?P<ptr>\**)\s*(?P<name>[A-Za-z_]\w*)\s*(?P<dims>(?:\[[^\]]*\]\s*)*)\s*(?P<end>=|;|\[)"
)
TYPEDEF_END_RE = re.compile(r"^\}\s*(\w+)\s*;\s*//\s*size\s*(?:=|:)\s*(0x[0-9A-Fa-f]+|\d+)")
TYPEDEF_ALIAS_RE = re.compile(r"^typedef\s+([A-Za-z_][\w ]*?)\s+(\w+)\s*;")
DNAME_RE = re.compile(r"^D_([0-9A-Fa-f]{6,8})$")


def parse_int(s):
    s = s.strip()
    try:
        return int(s, 0)
    except ValueError:
        m = re.fullmatch(r"\(?\s*(0x[0-9A-Fa-f]+|\d+)\s*\)?", s)
        return int(m.group(1), 0) if m else None


class Sym:
    __slots__ = ("name", "addr", "size", "size_src", "defined", "src", "ctype", "dims", "elem",
                 "decl_loc", "externs")

    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.size = None
        self.size_src = None
        self.defined = False
        self.src = set()
        self.ctype = None
        self.dims = None
        self.elem = None
        self.decl_loc = None
        self.externs = []

    def decl_str(self):
        if not self.ctype:
            return "?"
        d = "".join("[%s]" % ("" if x is None else x) for x in (self.dims or []))
        return "%s %s%s" % (self.ctype, self.name, d)


class SymMap:
    def __init__(self, elf, verbose=False):
        self.syms = {}
        self.sections = []  # (start, end, obj, sec)
        self.type_sizes = dict(PRIM_SIZES)
        self.src_files = {}
        self._load_elf(elf)
        self._load_map(os.path.join(ROOT, "build", "pokestadiumgs-us.map"))
        self._load_symbol_addrs()
        self._load_auto_syms()
        self._load_data_asm()
        self._load_c()
        self._finalize()

    def _get(self, name, addr):
        s = self.syms.get(name)
        if s is None:
            s = Sym(name, addr)
            self.syms[name] = s
        return s

    def _load_elf(self, elf):
        for s in elf.symbols:
            if not s["name"] or s["type"] in (3, 4):  # section/file
                continue
            if s["shndx"] == 0:
                continue
            if s["name"].startswith(("$", ".")) or s["name"].endswith(("_START", "_END", "_SIZE", "_VRAM", "_ROM_START")):
                continue
            sym = self._get(s["name"], s["value"])
            if s["shndx"] == 0xFFF1:  # ABS: linker-script defined (symbol_addrs / undefined_syms_auto)
                sym.src.add("elf-abs")
            else:
                sym.src.add("elf")
                sym.defined = True
                if s["size"] and s["type"] in (1, 2):
                    sym.size, sym.size_src = s["size"], "elf st_size"

    def _load_map(self, path):
        if not os.path.exists(path):
            return
        sec_re = re.compile(r"^\s*(\.\w+)\s+0x([0-9a-f]+)\s+0x([0-9a-f]+)\s+(\S+\.o)\s*$")
        loc_re = re.compile(r"^\s+0x([0-9a-f]{8,16})\s+(\S+\.o):(\w+)(?::\d+)?\s*$")
        with open(path) as f:
            for line in f:
                m = sec_re.match(line)
                if m:
                    start, size = int(m.group(2), 16), int(m.group(3), 16)
                    if size and start:
                        self.sections.append((start, start + size, m.group(4), m.group(1)))
                    continue
                m = loc_re.match(line)
                if m:
                    sym = self._get(m.group(3), int(m.group(1), 16))
                    sym.defined = True
                    sym.src.add("map-local")
        self.sections.sort()
        self._sec_starts = [s[0] for s in self.sections]

    def section_of(self, addr):
        i = bisect.bisect_right(self._sec_starts, addr) - 1
        while i >= 0:
            s = self.sections[i]
            if s[0] <= addr < s[1]:
                return s
            if s[1] <= addr and i < len(self.sections) - 1:
                break
            i -= 1
        return None

    def _load_symbol_addrs(self):
        rx = re.compile(r"^\s*(\w+)\s*=\s*(0x[0-9A-Fa-f]+)\s*;(.*)$")
        d = os.path.join(ROOT, "linker_scripts", "us")
        for fn in sorted(os.listdir(d)):
            if not (fn.startswith("symbol_addrs") and fn.endswith(".txt")):
                continue
            with open(os.path.join(d, fn)) as f:
                for line in f:
                    m = rx.match(line)
                    if not m:
                        continue
                    sym = self._get(m.group(1), int(m.group(2), 16))
                    sym.src.add("symbol_addrs")
                    sym.defined = True
                    ms = re.search(r"size:(0x[0-9A-Fa-f]+|\d+)", m.group(3))
                    if ms:
                        sym.size, sym.size_src = int(ms.group(1), 0), "symbol_addrs"
                    mt = re.search(r"type:(\S+)", m.group(3))
                    if mt and not sym.ctype:
                        sym.ctype = mt.group(1)

    def _load_auto_syms(self):
        p = os.path.join(ROOT, "linker_scripts", "us", "auto", "undefined_syms_auto.ld")
        if not os.path.exists(p):
            return
        rx = re.compile(r"^\s*(\w+)\s*=\s*(0x[0-9A-Fa-f]+)\s*;")
        with open(p) as f:
            for line in f:
                m = rx.match(line)
                if m:
                    self._get(m.group(1), int(m.group(2), 16)).src.add("auto-ld")

    def _load_data_asm(self):
        base = os.path.join(ROOT, "asm", "us", "data")
        lab_re = re.compile(r"^\s*(?:dlabel|glabel|alabel)\s+(\w+)")
        ln_re = re.compile(r"/\*\s*[0-9A-Fa-f]+\s+([0-9A-Fa-f]{8})\s")
        end_re = re.compile(r"^\s*(?:enddlabel|endlabel)\s+(\w+)")
        for dp, _, fns in os.walk(base):
            for fn in fns:
                if not fn.endswith(".s"):
                    continue
                path = os.path.join(dp, fn)
                labels = []  # [name, addr]
                pending = None
                last_vram = None
                with open(path, errors="replace") as f:
                    for line in f:
                        m = lab_re.match(line)
                        if m:
                            pending = m.group(1)
                            continue
                        if end_re.match(line):
                            if labels and last_vram is not None and labels[-1][2] is None:
                                labels[-1][2] = last_vram
                            continue
                        m = ln_re.search(line)
                        if m:
                            v = int(m.group(1), 16)
                            n = self._item_size(line)
                            last_vram = v + n
                            if pending:
                                if labels and labels[-1][2] is None:
                                    labels[-1][2] = v
                                labels.append([pending, v, None])
                                pending = None
                if labels and labels[-1][2] is None and last_vram:
                    labels[-1][2] = last_vram
                for name, addr, end in labels:
                    sym = self._get(name, addr)
                    sym.addr = addr
                    sym.defined = True
                    sym.src.add("data-asm")
                    if end and end > addr and sym.size_src not in ("C decl", "symbol_addrs"):
                        sym.size, sym.size_src = end - addr, "data-asm labels"

    @staticmethod
    def _item_size(line):
        m = re.search(r"\*/\s*\.(\w+)\s*(.*)$", line)
        if not m:
            return 4
        d, rest = m.group(1), m.group(2)
        n = rest.count(",") + 1 if rest.strip() else 1
        if d in ("word", "float", "4byte"):
            return 4 * n
        if d in ("short", "half", "2byte"):
            return 2 * n
        if d == "byte":
            return n
        if d in ("double", "dword", "8byte"):
            return 8 * n
        if d == "space":
            v = parse_int(rest.split(",")[0])
            return v or 0
        if d in ("ascii", "asciz", "string"):
            try:
                return len(bytes(rest.strip().strip('"'), "latin1").decode("unicode_escape")) + (d != "ascii")
            except Exception:
                return 4
        return 4

    # ---- C side -------------------------------------------------------------------
    def _iter_c_files(self):
        for top in ("include", "src"):
            for dp, _, fns in os.walk(os.path.join(ROOT, top)):
                for fn in fns:
                    if fn.endswith((".c", ".h")):
                        yield os.path.join(dp, fn)

    def read_src(self, path):
        t = self.src_files.get(path)
        if t is None:
            with open(path, errors="replace") as f:
                t = f.read()
            self.src_files[path] = t
        return t

    def _load_c(self):
        files = list(self._iter_c_files())
        # pass 1: type sizes
        for p in files:
            for line in self.read_src(p).splitlines():
                m = TYPEDEF_END_RE.match(line.strip())
                if m:
                    self.type_sizes[m.group(1)] = int(m.group(2), 0)
                    continue
                m = TYPEDEF_ALIAS_RE.match(line.strip())
                if m and "(" not in line and "{" not in line:
                    base = m.group(1).strip()
                    if base.startswith("struct "):
                        base = base[7:]
                    if base in self.type_sizes and m.group(2) not in self.type_sizes:
                        self.type_sizes[m.group(2)] = self.type_sizes[base]
                    if m.group(1).strip().startswith("struct ") and m.group(2) not in self.type_sizes:
                        self._alias_pending = getattr(self, "_alias_pending", []) + [(base, m.group(2))]
        for base, alias in getattr(self, "_alias_pending", []):
            if base in self.type_sizes:
                self.type_sizes.setdefault(alias, self.type_sizes[base])
        # pass 2: declarations of known / D_-named symbols
        for p in files:
            rel = os.path.relpath(p, ROOT)
            for ln, line in enumerate(self.read_src(p).splitlines(), 1):
                if "(" in line.split("=")[0] or line.lstrip().startswith(("return", "#", "//", "/*", "typedef", "case", "goto")):
                    continue
                m = DECL_RE.match(line)
                if not m:
                    continue
                name = m.group("name")
                sym = self.syms.get(name)
                if sym is None:
                    md = DNAME_RE.match(name)
                    if not md or len(md.group(1)) < 7:
                        continue
                    sym = self._get(name, int(md.group(1), 16))
                    sym.src.add("C")
                ctype = (m.group("type").strip() + " " + m.group("ptr")).strip()
                ctype = re.sub(r"\s+", " ", ctype.replace(" *", "*"))
                if ctype in ("return", "else", "goto", "case"):
                    continue
                dims_s = re.findall(r"\[([^\]]*)\]", m.group("dims") or "")
                dims = [parse_int(x) if x.strip() else None for x in dims_s]
                loc = "%s:%d" % (rel, ln)
                if m.group("extern"):
                    sym.externs.append((loc, line.strip()))
                    if sym.ctype is None or sym.decl_loc is None:
                        sym.ctype, sym.dims = ctype, dims
                    continue
                # a definition
                sym.defined = True
                sym.src.add("C def")
                sym.ctype, sym.dims, sym.decl_loc = ctype, dims, loc
        # element sizes / sizes from C
        for sym in self.syms.values():
            if not sym.ctype:
                continue
            es = self.sizeof(sym.ctype)
            sym.elem = es
            if es:
                total = es
                ok = True
                for d in sym.dims or []:
                    if d is None:
                        ok = False
                        break
                    total *= d
                if ok and sym.decl_loc:
                    sym.size, sym.size_src = total, "C decl"
                elif ok and sym.externs and sym.size_src not in ("symbol_addrs",):
                    # extern only: the decomp's belief about the object (asm-defined data/bss)
                    sym.size, sym.size_src = total, "C extern"

    def sizeof(self, ctype):
        t = ctype.strip()
        if t.endswith("*"):
            return 4
        t = re.sub(r"^(struct|union|const|volatile|static)\s+", "", t)
        t = re.sub(r"\s+const$", "", t)
        return self.type_sizes.get(t)

    def _finalize(self):
        defs = sorted({s.addr for s in self.syms.values() if s.defined})
        self._def_addrs = defs
        self._by_addr = defaultdict(list)
        for s in self.syms.values():
            self._by_addr[s.addr].append(s)
        self._all_addrs = sorted(self._by_addr)
        for s in self.syms.values():
            if s.size is not None:
                continue
            i = bisect.bisect_right(defs, s.addr)
            nxt = defs[i] if i < len(defs) else None
            sec = self.section_of(s.addr)
            end = nxt
            if sec and (end is None or end > sec[1]):
                end = sec[1]
            if end is not None and end > s.addr and end - s.addr < 0x100000:
                s.size, s.size_src = end - s.addr, "est. (next symbol)"

    def by_name(self, name):
        s = self.syms.get(name)
        if s is None:
            md = DNAME_RE.match(name)
            if md:
                s = self._get(name, int(md.group(1), 16))
                s.src.add("name-only")
        return s

    def best_at(self, addr):
        """Symbol starting exactly at addr (prefer defined, D_-named for the address)."""
        c = self._by_addr.get(addr)
        if not c:
            return None
        c = sorted(c, key=lambda s: (not s.defined, not s.decl_loc, s.name.startswith("func_")))
        return c[0]

    def container(self, addr, defined_only=True):
        """Symbol whose [addr, addr+size) contains addr (closest start below)."""
        i = bisect.bisect_right(self._all_addrs, addr) - 1
        steps = 0
        while i >= 0 and steps < 64:
            a = self._all_addrs[i]
            for s in sorted(self._by_addr[a], key=lambda s: (not s.defined, not s.decl_loc)):
                if defined_only and not s.defined:
                    continue
                if s.size is not None and a <= addr < a + s.size:
                    return s
                if s.defined:
                    return None  # nearest defined object below does not reach addr
            i -= 1
            steps += 1
        return None

    def enclosing(self, addr, exclude):
        """A different symbol whose C/symbol_addrs-declared extent covers addr."""
        i = bisect.bisect_right(self._all_addrs, addr) - 1
        steps = 0
        while i >= 0 and steps < 256:
            a = self._all_addrs[i]
            if addr - a > 0x10000:
                break
            for s in self._by_addr[a]:
                if s is exclude or s.addr == exclude.addr:
                    continue
                if s.size_src in ("C decl", "C extern", "symbol_addrs") and a <= addr < a + s.size:
                    return s
            i -= 1
            steps += 1
        return None

    def name_for(self, addr):
        s = self.best_at(addr)
        if s:
            return s, 0
        c = self.container(addr) or self.container(addr, defined_only=False)
        if c:
            return c, addr - c.addr
        return None, 0


# --------------------------------------------------------------------------------------
# Instruction decoding
# --------------------------------------------------------------------------------------

REGS = ["zero", "at", "v0", "v1", "a0", "a1", "a2", "a3", "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7",
        "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra"]
CALLER_SAVED = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 24, 25, 31]
LOADS = {0x20: ("lb", 1), 0x21: ("lh", 2), 0x22: ("lwl", 4), 0x23: ("lw", 4), 0x24: ("lbu", 1),
         0x25: ("lhu", 2), 0x26: ("lwr", 4), 0x27: ("lwu", 4), 0x37: ("ld", 8), 0x1A: ("ldl", 8), 0x1B: ("ldr", 8)}
STORES = {0x28: ("sb", 1), 0x29: ("sh", 2), 0x2A: ("swl", 4), 0x2B: ("sw", 4), 0x2E: ("swr", 4),
          0x3F: ("sd", 8), 0x2C: ("sdl", 8), 0x2D: ("sdr", 8)}
FMEM = {0x31: ("lwc1", 4, False), 0x35: ("ldc1", 8, False), 0x39: ("swc1", 4, True), 0x3D: ("sdc1", 8, True)}
BRANCH_OPS = {1, 4, 5, 6, 7, 0x14, 0x15, 0x16, 0x17}


def s32(x):
    x &= 0xFFFFFFFF
    return x - 0x100000000 if x & 0x80000000 else x


def sext16(x):
    return x - 0x10000 if x & 0x8000 else x


class Insn:
    __slots__ = ("vram", "word", "text", "reloc", "op", "rs", "rt", "rd", "sa", "funct", "imm", "simm")

    def __init__(self, vram, word, text, reloc):
        self.vram, self.word, self.text, self.reloc = vram, word, text, reloc
        w = word
        self.op, self.rs, self.rt, self.rd = w >> 26, (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31
        self.sa, self.funct, self.imm = (w >> 6) & 31, w & 63, w & 0xFFFF
        self.simm = sext16(self.imm)


RELOC_TXT_RE = re.compile(r"%(hi|lo|gp_rel)\(\s*([A-Za-z_.$][\w.$]*)\s*(?:([+-])\s*(0x[0-9A-Fa-f]+|\d+))?\s*\)")
LINE_RE = re.compile(r"/\*\s*([0-9A-Fa-f]+)\s+([0-9A-Fa-f]{8})\s+([0-9A-Fa-f]{8})\s*\*/\s+([a-z][\w.]*)\s*(.*)$")


def load_splat_asm(path):
    out = []
    with open(path, errors="replace") as f:
        for line in f:
            m = LINE_RE.search(line)
            if not m:
                continue
            mnem = m.group(4)
            if mnem.startswith("."):
                continue
            vram, word = int(m.group(2), 16), int(m.group(3), 16)
            reloc = None
            mr = RELOC_TXT_RE.search(m.group(5))
            if mr:
                add = 0
                if mr.group(3):
                    add = int(mr.group(4), 0) * (-1 if mr.group(3) == "-" else 1)
                reloc = (mr.group(1), mr.group(2), add)
            out.append(Insn(vram, word, (mnem + " " + m.group(5)).strip(), reloc))
    return out


def find_func_range(elf, symmap, func):
    s = elf.func_syms.get(func)
    if s is None:
        return None
    start = s["value"]
    end = start + s["size"] if s["size"] else None
    if end is None:
        nxt = [f["value"] for f in elf.func_syms.values() if f["value"] > start]
        end = min(nxt) if nxt else start + 4
        sec = symmap.section_of(start)
        if sec:
            end = min(end, sec[1])
    return start, end


def load_elf_func(elf, symmap, func):
    rng = find_func_range(elf, symmap, func)
    if rng is None:
        return None
    start, end = rng
    sec = elf.section_for(start)
    if sec is None:
        return None
    rels = elf.relocs_for(sec)
    out = []
    for a, w in elf.words(sec, start, end):
        reloc = None
        for typ, sym in rels.get(a, []):
            if typ in (5, 6) and sym is not None:
                kind = "hi" if typ == 5 else "lo"
                name = sym["name"] if sym["type"] != 3 else None
                reloc = (kind, name, None)  # addend resolved later from the words
        out.append(Insn(a, w, "", reloc))
    return out


# --------------------------------------------------------------------------------------
# Value tracking
# --------------------------------------------------------------------------------------


class Val:
    """kind 'hi': lui result (hiabs, sym, wadd) + lin;  kind 'lin': base (sym,wadd,abs)|None + lin + const."""
    __slots__ = ("kind", "hiabs", "sym", "wadd", "abs", "lin", "const", "src")

    def __init__(self, kind, hiabs=0, sym=None, wadd=None, abs_=None, lin=None, const=0, src=None):
        self.kind, self.hiabs, self.sym, self.wadd, self.abs = kind, hiabs, sym, wadd, abs_
        self.lin = lin or {}
        self.const = const
        self.src = src

    def has_base(self):
        return self.kind == "lin" and self.sym is not None

    def pure_const(self):
        return self.kind == "lin" and self.sym is None and not self.lin


_varctr = [0]


def fresh(desc):
    _varctr[0] += 1
    return Val("lin", lin={"%s#%d" % (desc, _varctr[0]): 1})


def lin_add(a, b, sign=1):
    r = dict(a)
    for k, v in b.items():
        r[k] = r.get(k, 0) + sign * v
        if r[k] == 0:
            del r[k]
    return r


class Event:
    __slots__ = ("i", "vram", "kind", "mnem", "width", "store", "sym", "wadd", "abs", "lin", "hi_sym",
                 "hi_wadd", "hi_abs", "note")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))


def mnem_of(ins):
    op = ins.op
    if op in LOADS:
        return LOADS[op][0]
    if op in STORES:
        return STORES[op][0]
    if op in FMEM:
        return FMEM[op][0]
    return {9: "addiu", 0xF: "lui", 0xD: "ori"}.get(op, "op%02x" % op)


def analyze(insns, symmap):
    regs = {0: Val("lin")}
    events = []
    pending_kill = False

    def get(r):
        if r == 0:
            return Val("lin")
        v = regs.get(r)
        if v is None:
            v = fresh(REGS[r] + "@in")
            regs[r] = v
        return v

    def setr(r, v):
        if r != 0:
            regs[r] = v

    def resolve(sym_name, wadd, absaddr):
        """Return (Sym, written addend) for a reloc; ELF section relocs get named by address."""
        if sym_name:
            s = symmap.by_name(sym_name)
            if s is not None:
                return s, (wadd if wadd is not None else absaddr - s.addr)
        s, off = symmap.name_for(absaddr)
        return s, off

    # control flow: forward-branch snapshots merged at their targets
    idx_of = {ins.vram: k for k, ins in enumerate(insns)}
    targets = {}
    uncond = set()
    for k, ins in enumerate(insns):
        t = None
        if ins.op in BRANCH_OPS:
            t = ins.vram + 4 + ins.simm * 4
            if ins.op == 4 and ins.rs == 0 and ins.rt == 0:
                uncond.add(k)
        elif ins.op == 2:
            t = (ins.vram & 0xF0000000) | ((ins.word & 0x3FFFFFF) << 2)
            uncond.add(k)
        elif ins.op == 0 and ins.funct == 8:
            uncond.add(k)
        if t is not None and t in idx_of:
            targets[k] = idx_of[t]
    incoming = defaultdict(list)
    target_set = set(targets.values())
    pending_snap = None
    load_ev = {}

    def merge(states):
        if not states:
            return {0: Val("lin")}
        first = states[0]
        out = {}
        for key, v in first.items():
            if all(s.get(key) is v for s in states[1:]):
                out[key] = v
        out[0] = Val("lin")
        return out

    for i, ins in enumerate(insns):
        if i in target_set:
            states = list(incoming.get(i, []))
            if not (i >= 2 and (i - 2) in uncond):
                states.append(regs)
            regs = merge(states) if states else {0: Val("lin")}
        op, rs, rt, rd = ins.op, ins.rs, ins.rt, ins.rd
        kill_after = pending_kill
        pending_kill = False
        snap_after = pending_snap
        pending_snap = targets.get(i)
        rel = ins.reloc
        if op == 0xF:  # lui
            if rel and rel[0] == "hi":
                setr(rt, Val("hi", hiabs=ins.imm << 16, sym=rel[1], wadd=rel[2], src=i))
            else:
                setr(rt, Val("lin", const=ins.imm << 16))
        elif op in (9, 8, 0x19):  # addiu / addi / daddiu
            base = get(rs)
            if rel and rel[0] == "lo":
                if base.kind == "hi":
                    absaddr = (base.hiabs + ins.simm) & 0xFFFFFFFF
                    s, wadd = resolve(rel[1], rel[2], absaddr)
                    hs, hw = (resolve(base.sym, base.wadd, absaddr) if base.sym or base.wadd is not None
                              else (None, None))
                    if s is None:
                        setr(rt, fresh("addr"))
                    else:
                        events.append(Event(i=i, vram=ins.vram, kind="addr", mnem="addiu", sym=s, wadd=wadd,
                                            abs=absaddr, lin=dict(base.lin), hi_sym=hs, hi_wadd=hw,
                                            hi_abs=base.hiabs))
                        setr(rt, Val("lin", sym=s, wadd=wadd, abs_=absaddr, lin=dict(base.lin), const=base.const, src=i))
                else:
                    setr(rt, fresh("lo?"))
            else:
                if base.kind == "lin":
                    setr(rt, Val("lin", sym=base.sym, wadd=base.wadd, abs_=base.abs, lin=dict(base.lin),
                                 const=base.const + ins.simm, src=base.src))
                else:
                    setr(rt, fresh("hi+imm"))
        elif op == 0xD:  # ori
            base = get(rs)
            if base.pure_const() and not rel:
                setr(rt, Val("lin", const=base.const | ins.imm))
            else:
                setr(rt, fresh("ori"))
        elif op in LOADS or op in STORES or op in FMEM:
            if op in LOADS:
                mn, width = LOADS[op]
                store = False
            elif op in STORES:
                mn, width = STORES[op]
                store = True
            else:
                mn, width, store = FMEM[op]
            base = get(rs)
            ev = None
            if rel and rel[0] == "lo":
                if base.kind == "hi":
                    absaddr = (base.hiabs + ins.simm) & 0xFFFFFFFF
                    s, wadd = resolve(rel[1], rel[2], absaddr)
                    hs, hw = (resolve(base.sym, base.wadd, absaddr) if base.sym or base.wadd is not None
                              else (None, None))
                    if s is not None:
                        ev = Event(i=i, vram=ins.vram, kind="deref", mnem=mn, width=width, store=store, sym=s,
                                   wadd=wadd, abs=(absaddr + base.const) & 0xFFFFFFFF, lin=dict(base.lin),
                                   hi_sym=hs, hi_wadd=hw, hi_abs=base.hiabs)
                        if base.const:
                            ev.wadd = s32(wadd + base.const)
            elif rs != 29 and base.has_base():
                absaddr = (base.abs + base.const + ins.simm) & 0xFFFFFFFF
                ev = Event(i=i, vram=ins.vram, kind="deref", mnem=mn, width=width, store=store, sym=base.sym,
                           wadd=s32(base.wadd + base.const + ins.simm), abs=absaddr, lin=dict(base.lin))
            if ev:
                events.append(ev)
            if op in LOADS:
                setr(rt, fresh(mn))
                if ev is not None:
                    load_ev[rt] = (regs[rt], ev)
        elif op == 0:
            f = ins.funct
            if f in (0x21, 0x20, 0x2D):  # addu/add/daddu
                a, b = get(rs), get(rt)
                if rt == 0:
                    setr(rd, a)
                elif rs == 0:
                    setr(rd, b)
                elif a.kind == "hi" and b.kind == "lin" and b.sym is None:
                    setr(rd, Val("hi", hiabs=a.hiabs, sym=a.sym, wadd=a.wadd, lin=lin_add(a.lin, b.lin),
                                 const=a.const + b.const, src=a.src))
                elif b.kind == "hi" and a.kind == "lin" and a.sym is None:
                    setr(rd, Val("hi", hiabs=b.hiabs, sym=b.sym, wadd=b.wadd, lin=lin_add(a.lin, b.lin),
                                 const=a.const + b.const, src=b.src))
                elif a.kind == "lin" and b.kind == "lin" and not (a.sym and b.sym):
                    base = a if a.sym else b
                    setr(rd, Val("lin", sym=base.sym, wadd=base.wadd, abs_=base.abs, lin=lin_add(a.lin, b.lin),
                                 const=a.const + b.const, src=base.src))
                else:
                    setr(rd, fresh("addu"))
            elif f in (0x23, 0x22, 0x2F):  # subu
                a, b = get(rs), get(rt)
                if a.kind == "lin" and b.kind == "lin" and b.sym is None:
                    setr(rd, Val("lin", sym=a.sym, wadd=a.wadd, abs_=a.abs, lin=lin_add(a.lin, b.lin, -1),
                                 const=a.const - b.const, src=a.src))
                else:
                    setr(rd, fresh("subu"))
            elif f == 0x00:  # sll
                if ins.word == 0:
                    pass
                else:
                    a = get(rt)
                    if a.kind == "lin" and a.sym is None:
                        k = 1 << ins.sa
                        setr(rd, Val("lin", lin={x: c * k for x, c in a.lin.items()}, const=a.const * k))
                    else:
                        setr(rd, fresh("sll"))
            elif f == 0x25 and (rt == 0 or rs == 0):  # or = move
                setr(rd, get(rs if rt == 0 else rt))
            elif f in (0x18, 0x19):  # mult/multu
                a, b = get(rs), get(rt)
                if a.pure_const() and b.kind == "lin" and b.sym is None:
                    a, b = b, a
                if b.pure_const() and a.kind == "lin" and a.sym is None:
                    k = b.const
                    regs["lo"] = Val("lin", lin={x: c * k for x, c in a.lin.items()}, const=a.const * k)
                else:
                    regs["lo"] = fresh("mult")
            elif f in (0x1A, 0x1B):
                regs["lo"] = fresh("div")
            elif f == 0x12:  # mflo
                setr(rd, regs.get("lo") or fresh("mflo"))
            elif f == 0x08:  # jr: a register loaded from a table = jump table
                le = load_ev.get(rs)
                if le and regs.get(rs) is le[0]:
                    le[1].kind = "jtbl"
            elif f in (0x0C, 0x0D, 0x11, 0x13) or 0x30 <= f <= 0x36:
                pass
            elif f == 0x09:  # jalr
                setr(rd, fresh("ra"))
                pending_kill = True
            else:
                setr(rd, fresh("r%02x" % f))
        elif op == 3:  # jal
            pending_kill = True
        elif op in BRANCH_OPS or op == 2:
            pass
        elif op == 0x11:  # cop1
            if rs in (0, 1, 2):  # mfc1/dmfc1/cfc1
                setr(rt, fresh("mfc1"))
        elif op in (0xA, 0xB, 0xC, 0xE, 0x18):
            setr(rt, fresh("op%02x" % op))
        elif op in (0x2F, 0x10, 0x12):
            if op == 0x10 and rs == 0:
                setr(rt, fresh("mfc0"))
        else:
            setr(rt, fresh("op%02x" % op))
        if kill_after:
            for r in CALLER_SAVED:
                regs.pop(r, None)
            regs.pop("lo", None)
        if snap_after is not None and snap_after > i:
            incoming[snap_after].append(dict(regs))
    return events


# --------------------------------------------------------------------------------------
# Draft handling
# --------------------------------------------------------------------------------------


_PRAGMAS = None
_ALLP = None


def find_pragma_file(func):
    global _PRAGMAS
    if _PRAGMAS is None:
        _PRAGMAS = {f: (p, a) for f, p, a in all_pragma_funcs()}
    return _PRAGMAS.get(func, (None, None))


def all_pragma_funcs():
    global _ALLP
    if _ALLP is not None:
        return _ALLP
    rx = re.compile(r'GLOBAL_ASM\("([^"]*/(\w+)\.s)"\)')
    res = []
    for dp, _, fns in sorted(os.walk(os.path.join(ROOT, "src"))):
        for fn in sorted(fns):
            if fn.endswith(".c"):
                p = os.path.join(dp, fn)
                with open(p, errors="replace") as f:
                    for m in rx.finditer(f.read()):
                        res.append((m.group(2), p, m.group(1)))
    _ALLP = res
    return res


def extract_func_def(text, func):
    m = re.search(r"^[A-Za-z_][^\n;]*\b%s\s*\([^;{]*\)\s*\{" % re.escape(func), text, re.M)
    if not m:
        return None, None
    i = m.end()
    depth = 1
    while i < len(text) and depth:
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    return text[m.start():i], text.count("\n", 0, m.start()) + 1


def extract_draft(path, func):
    """Return (draft_text, first_line, kind) for FUNC in a C file."""
    with open(path, errors="replace") as f:
        text = f.read()
    m = re.search(r'#pragma\s+GLOBAL_ASM\("[^"]*/%s\.s"\)' % re.escape(func), text)
    if m:
        head = text[:m.start()]
        e = head.rfind("#else")
        n = head.rfind("#ifdef NON_MATCHING")
        if n >= 0 and e > n and "#endif" not in head[n:e]:
            body = head[n:e]
            d, ln = extract_func_def(body, func)
            if d:
                return d, text.count("\n", 0, n) + ln, "NON_MATCHING draft"
            return body, text.count("\n", 0, n) + 1, "NON_MATCHING block"
        return None, None, "no draft (GLOBAL_ASM only)"
    d, ln = extract_func_def(text, func)
    if d:
        return d, ln, "C definition"
    return None, None, "function not found in file"


def find_def_file(func, symmap, obj_hint=None):
    if obj_hint and obj_hint.startswith("build/src/"):
        p = os.path.join(ROOT, obj_hint[len("build/"):-2] + ".c")
        if os.path.exists(p):
            return p
    rx = re.compile(r"^[A-Za-z_][^\n;]*\b%s\s*\([^;{]*\)\s*\{" % re.escape(func), re.M)
    for dp, _, fns in os.walk(os.path.join(ROOT, "src")):
        for fn in fns:
            if fn.endswith(".c"):
                p = os.path.join(dp, fn)
                if rx.search(symmap.read_src(p)):
                    return p
    return None


def draft_lines(draft, first_line, names, limit=4):
    out = []
    if not draft:
        return out
    rx = re.compile(r"\b(%s)\b" % "|".join(re.escape(n) for n in names))
    for k, line in enumerate(draft.splitlines()):
        if rx.search(line):
            out.append((first_line + k, line.strip()))
    if len(out) > limit:
        out = out[:limit] + [(None, "... (%d more)" % (len(out) - limit))]
    return out


def uses(draft, name):
    return bool(draft) and re.search(r"\b%s\b" % re.escape(name), draft) is not None


def index_exprs(text, pos):
    """Balanced `[...]` groups directly following text[pos:]."""
    out = []
    while True:
        while pos < len(text) and text[pos] in " \t":
            pos += 1
        mf = re.match(r"(?:\.|->)\s*\w+", text[pos:])
        if mf:  # struct member chain: S.unk_14[i - 1]
            pos += mf.end()
            continue
        if pos >= len(text) or text[pos] != "[":
            return out
        depth, j = 0, pos
        while j < len(text):
            if text[j] == "[":
                depth += 1
            elif text[j] == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(text[pos + 1:j])
        pos = j + 1


def strip_nested(s):
    """Remove nested [...] and (...) groups, leaving the top-level expression."""
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\[[^\[\]]*\]", "_", s)
    return s


def neg_index_in_draft(draft, name):
    if not draft:
        return False
    for m in re.finditer(r"\b%s\b" % re.escape(name), draft):
        for ix in index_exprs(draft, m.end()):
            if re.search(r"-\s*[\w(]", strip_nested(ix)):
                return True
    pats = [r"\(\s*&\s*%s\s*\)\s*\[\s*-" % re.escape(name),
            r"\b%s\s*-\s*(?:0x|\d)" % re.escape(name),
            r"&\s*%s\s*\[\s*-" % re.escape(name)]
    return any(re.search(p, draft) for p in pats)


DRAFT_PATTERNS = [
    ("neg-index", r"\b(D_\w+|g\w+)\s*(?:\[[^\]]*\]\s*)*\[[^\]\[]*-\s*(?:0x[0-9A-Fa-f]+|\d+)\s*\]"),
    ("neg-ptr", r"\(\s*&\s*(D_\w+|g\w+)\s*\)\s*\[\s*-"),
    ("sym-minus", r"&?\b(D_\w+)\s*-\s*(?:0x[0-9A-Fa-f]+|\d+)\b"),
    ("byte-offset", r"\(\s*u8\s*\*\s*\)\s*&?\s*(D_\w+|g\w+)[^;]*?\+\s*(?:0x[0-9A-Fa-f]+|\d+)"),
    ("cast-of-addr", r"\(\s*\(?\s*[A-Za-z_]\w*\s*\*\s*\)?\s*\)\s*&\s*(D_\w+|g\w+)\b"),
]


def draft_pattern_notes(draft, first_line, symmap):
    notes = []
    if not draft:
        return notes
    for k, line in enumerate(draft.splitlines()):
        s = line.strip()
        if s.startswith("//"):
            continue
        for kind, pat in DRAFT_PATTERNS:
            for m in re.finditer(pat, line):
                notes.append((first_line + k, kind, m.group(1), s))
        # constant index >= declared dimension (not on the declaration itself)
        if DECL_RE.match(line):
            continue
        for m in re.finditer(r"\b(D_[0-9A-Fa-f]{8}|g\w+)((?:\s*\[[^\]\[]*\])+)", line):
            sym = symmap.syms.get(m.group(1))
            if not sym or not sym.dims:
                continue
            idx = re.findall(r"\[([^\]\[]*)\]", m.group(2))
            for d, ix in zip(sym.dims, idx):
                v = parse_int(ix)
                if d is not None and v is not None and v >= d:
                    notes.append((first_line + k, "index>=dim", m.group(1), s))
    seen = set()
    out = []
    for n in notes:
        key = (n[0], n[1], n[2])
        if key not in seen:
            seen.add(key)
            out.append(n)
    return out


# --------------------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------------------


def hx(v):
    return ("-0x%X" % -v) if v < 0 else ("0x%X" % v)


def decompose(sym, off):
    """C-ish spelling of byte offset `off` (may be beyond the size) into sym's declared shape."""
    if sym is None:
        return None
    es = sym.elem
    if not es:
        return "(u8*)&%s + %s" % (sym.name, hx(off))
    dims = list(sym.dims or [])
    strides = []
    acc = es
    for d in reversed(dims[1:]):
        strides.insert(0, acc * (d or 1))
        acc *= d or 1
    strides.append(es) if dims else None
    if not dims:
        if off % es == 0 and off != 0:
            return "(&%s)[%d]" % (sym.name, off // es)
        return "%s%s" % (sym.name, "" if off == 0 else " + byte %s" % hx(off))
    idx = []
    rem = off
    for st in strides:
        q = rem // st
        idx.append(q)
        rem -= q * st
    s = sym.name + "".join("[%d]" % q for q in idx)
    if rem:
        s += " (+%s into the element)" % hx(rem)
    return s


def dim_strides(sym):
    if not sym or not sym.elem or not sym.dims:
        return []
    out = []
    acc = sym.elem
    for d in reversed(sym.dims):
        out.insert(0, acc)
        acc *= d or 1
    return out


def neg_suggestions(sym, e, strides):
    """Spell a negative constant byte offset e as `[x - k]` on each index stride."""
    out = []
    ds = dim_strides(sym)
    names = "ijklmn"
    for st in sorted(set(abs(x) for x in strides if x), reverse=True):
        k = (-e + st - 1) // st
        field = e + k * st
        if st in ds:
            q = ds.index(st)
            idx = "".join("[%s%s]" % (names[p], (" - %d" % k) if p == q else "") for p in range(len(ds)))
            out.append("stride %s = dim %d: %s%s%s" % (hx(st), q, sym.name, idx,
                                                     (" + field %s" % hx(field)) if field else ""))
        else:
            out.append("stride %s: %s[.. - %d]%s" % (hx(st), sym.name, k, (" + field %s" % hx(field)) if field else ""))
    return out


class Flag:
    def __init__(self, sev, kind, msg, ev=None, suggest=None, draft=None, names=()):
        self.sev, self.kind, self.msg, self.ev = sev, kind, msg, ev
        self.suggest = suggest or []
        self.draft = draft
        self.names = names
        self.vrams = [ev.vram] if ev else []
        self.count = 1
        self.raw_sev = sev


def classify(events, symmap, draft):
    flags = []
    refs = []
    for ev in events:
        S = ev.sym
        e = ev.wadd if ev.wadd is not None else ev.abs - S.addr
        ix = " + idx" if ev.lin else ""
        strides = sorted({abs(c) for c in ev.lin.values()}, reverse=True)
        stxt = (" strides " + ",".join(hx(s) for s in strides)) if strides else ""
        what = "%s %s%s" % (ev.mnem, S.name, (" " + hx(e) if e else "")) + ix
        refs.append((ev, S, e))
        # (d) hi/lo mispair
        if ev.hi_sym is not None:
            hs, hw = ev.hi_sym, ev.hi_wadd
            hi_expect = (hs.addr + (hw or 0)) & 0xFFFFFFFF
            lo_expect = (S.addr + (ev.wadd if ev.kind == "addr" else e - 0)) & 0xFFFFFFFF
            hi_ok = ((hi_expect + 0x8000) >> 16) & 0xFFFF == (ev.hi_abs >> 16) & 0xFFFF
            if not hi_ok:
                flags.append(Flag("H", "hilo", "%%hi(%s%s) does not carry to the %%lo address 0x%08X (%s)" % (
                    hs.name, " + " + hx(hw) if hw else "", ev.abs, what), ev, names=(hs.name, S.name)))
        if ev.wadd is not None and ((S.addr + ev.wadd) & 0xFFFFFFFF) != ev.abs:
            flags.append(Flag("H", "hilo", "named %s %s = 0x%08X but the instruction words give 0x%08X (hi from %s)" % (
                S.name, hx(ev.wadd), (S.addr + ev.wadd) & 0xFFFFFFFF, ev.abs,
                ev.hi_sym.name if ev.hi_sym else "?"), ev, names=(S.name,)))
        if S.name.startswith("jtbl") or ev.kind == "jtbl":
            continue  # switch tables are indexed with (case - first_case): negative addends are normal
        landing = symmap.container(ev.abs) if ev.abs is not None else None
        deref = ev.kind == "deref"
        if e < 0:
            sev = "H" if deref else "M"
            sug = neg_suggestions(S, e, [c for c in ev.lin.values()]) if ev.lin else []
            land_txt = ""
            if landing and landing is not S:
                land_txt = "; address lands in %s at %s -> %s" % (landing.name, hx(ev.abs - landing.addr),
                                                                    decompose(landing, ev.abs - landing.addr))
            elif not ev.lin:
                land_txt = "; no defined object contains 0x%08X" % ev.abs
            msg = "negative addend: %s (%s)%s%s" % (what, ev.kind, stxt, land_txt)
            if not ev.lin and landing and landing is not S:
                sug.append("write it as %s" % decompose(landing, ev.abs - landing.addr))
            elif ev.lin and not sug:
                sug.append("%s with a negative index offset (%s)" % (S.name, hx(e)))
            f = Flag(sev, "neg", msg, ev, sug, names=(S.name,) + ((landing.name,) if landing else ()))
            if neg_index_in_draft(draft, S.name):
                f.sev = "L"
                f.draft = "draft already writes a negative index/offset on %s - check WHICH dimension carries it" % S.name
            elif draft and not uses(draft, S.name) and landing and uses(draft, landing.name):
                f.sev = "L"
                f.draft = "draft uses %s here, not %s (consistent)" % (landing.name, S.name)
            flags.append(f)
            continue
        min_size = S.size
        if S.size is not None and ev.lin and S.size_src not in ("C decl", "symbol_addrs"):
            # an indexed access with stride st needs >= st bytes per element: smaller label/estimate
            # sizes just mean the data labels split an array
            min_size = max([S.size] + [abs(c) for c in ev.lin.values()])
        if S.size is not None and S.ctype and S.dims and None in S.dims and S.size_src != "C decl":
            min_size = None  # extern T S[]: open-ended
        if min_size is not None and e >= min_size:
            if landing is not None and landing is not S:
                if not deref and e == S.size:
                    sev = "L"
                    msg = "one-past-end address %s = start of %s (loop end pointer?)" % (what, landing.name)
                else:
                    sev = "H" if deref else "M"
                    msg = "addend %s >= size %s of %s (%s); address lands in %s at %s%s" % (
                        hx(e), hx(S.size), S.name, S.size_src, landing.name, hx(ev.abs - landing.addr), stxt)
                sug = ["%s" % decompose(landing, ev.abs - landing.addr)]
                if ev.lin:
                    sug = ["%s[idx] based at %s" % (landing.name, decompose(landing, ev.abs - landing.addr))]
                f = Flag(sev, "past", msg, ev, sug, names=(S.name, landing.name))
                if draft and not uses(draft, S.name) and uses(draft, landing.name) and f.sev != "L":
                    f.sev = "L"
                    f.draft = "draft uses %s, not %s (consistent)" % (landing.name, S.name)
                if S.size_src and S.size_src.startswith("est") and f.sev == "H":
                    f.sev = "M"
                    f.msg += " [size only estimated]"
                flags.append(f)
            else:
                sev = "M" if deref else "L"
                if not deref and e == S.size:
                    sev = "L"
                flags.append(Flag(sev, "past", "addend %s >= size %s of %s (%s)%s, no defined object at 0x%08X" % (
                    hx(e), hx(S.size), S.name, S.size_src, stxt, ev.abs), ev, names=(S.name,)))
            continue
        cont = symmap.container(S.addr) if not S.defined else None
        if cont is S:
            cont = None
        if cont is None:
            cont = symmap.enclosing(S.addr, S)
        if cont is not None:
            if True:
                f = Flag("M" if cont.ctype else "L", "inside",
                         "%s is %s: it is %s + %s -> %s (%s)" % (
                             S.name, "not a known object start" if not S.defined else
                             "inside the C-declared extent of another object (%s)" % cont.size_src,
                             cont.name, hx(S.addr - cont.addr), decompose(cont, ev.abs - cont.addr), what),
                         ev, ["%s" % decompose(cont, ev.abs - cont.addr)], names=(S.name, cont.name))
                if draft and not uses(draft, S.name):
                    f.sev = "L"
                    f.draft = "draft does not use %s (consistent)" % S.name
                flags.append(f)
    # (e) alias: indexed access through P reaching addresses also reached as S-k
    neg_abs = defaultdict(set)
    neg_strides = defaultdict(set)
    for ev, S, e in refs:
        if e < 0 and ev.lin and ev.kind != "jtbl" and not S.name.startswith("jtbl"):
            neg_abs[S.name].add(ev.abs)
            neg_strides[S.name].add(frozenset(abs(c) for c in ev.lin.values()))
    for sname, addrs in neg_abs.items():
        Ssym = symmap.syms.get(sname)
        lo, hi = min(addrs), max(addrs)
        for ev, P, e in refs:
            if P.name == sname or not ev.lin or e < 0:
                continue
            s_strides = neg_strides[sname]
            p_strides = frozenset(abs(c) for c in ev.lin.values())
            if ev.abs in addrs or (lo <= ev.abs <= hi and p_strides in s_strides):
                k = ev.abs - Ssym.addr
                strides = [c for c in ev.lin.values()]
                sug = ["%s - %s: %s" % (sname, hx(-k), "; ".join(neg_suggestions(Ssym, k, strides)) or "?")]
                f = Flag("H", "alias",
                         "indexed %s %s%s reaches 0x%08X = %s %s, an address this function also reaches as %s minus "
                         "a constant (negative-index accesses at 0x%08X..0x%08X): probably %s[.. - k], not %s" % (
                             ev.mnem, P.name, (" + " + hx(e)) if e else "", ev.abs, sname, hx(k), sname, lo, hi,
                             sname, P.name), ev, sug, names=(P.name, sname))
                if draft and not uses(draft, P.name):
                    f.sev = "L"
                    f.draft = "draft does not use %s (consistent)" % P.name
                flags.append(f)
    for f in flags:
        if f.sev == "H" and f.kind in ("neg", "past", "inside") and draft and uses(draft, f.ev.sym.name) \
                and not f.draft:
            f.sev = "M"
            f.draft = ("draft already uses %s itself (same premise as the asm naming): hint only - check the "
                       "index arithmetic / declared size" % f.ev.sym.name)
    for f in flags:
        if f.ev is not None and f.ev.sym.addr < 0x80000000 and f.kind in ("neg", "past", "inside") and f.sev != "L":
            f.sev = "L"
            f.raw_sev = "L"
            f.draft = "segmented (asset) address: every asset file reuses the same segment range, the symbol map is ambiguous"
    # merge duplicates (neg flags on the same base/index shape are merged across field offsets)
    merged = {}
    for f in flags:
        if f.kind == "neg" and f.ev.lin:
            key = (f.kind, f.sev, f.ev.sym.name, tuple(sorted(abs(c) for c in f.ev.lin.values())))
        else:
            key = (f.kind, f.sev, f.names, (f.ev.sym.name, f.ev.wadd if f.kind != "alias" else None))
        if key in merged:
            m = merged[key]
            m.count += 1
            m.vrams.append(f.ev.vram)
            if f.kind == "neg" and f.ev.lin:
                m.offsets.add(f.ev.wadd)
        else:
            f.offsets = {f.ev.wadd}
            merged[key] = f
    for f in merged.values():
        if f.kind == "neg" and f.ev.lin and len(f.offsets) > 1:
            f.msg += " [constant parts seen: %s]" % ", ".join(hx(x) for x in sorted(f.offsets))
            f.suggest = neg_suggestions(f.ev.sym, min(f.offsets), list(f.ev.lin.values()))
    out = sorted(merged.values(), key=lambda f: (-SEV_ORDER[f.sev], f.vrams[0]))
    return out, refs


# --------------------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------------------


_ASMIDX = None


def find_asm(func):
    global _ASMIDX
    if _ASMIDX is None:
        _ASMIDX = {}
        for dp, _, fns in os.walk(os.path.join(ROOT, "asm", "us", "nonmatchings")):
            for fn in fns:
                if fn.endswith(".s"):
                    _ASMIDX.setdefault(fn[:-2], os.path.join(dp, fn))
    return _ASMIDX.get(func)


class Result:
    def __init__(self, func):
        self.func = func
        self.flags = []
        self.refs = []
        self.notes = []
        self.draft_kind = None
        self.source = None
        self.error = None
        self.draft_file = None
        self.draft_first = None
        self.draft = None

    def counts(self):
        c = defaultdict(int)
        for f in self.flags:
            c[f.sev] += 1
        return c

    def worst(self):
        return self.flags[0] if self.flags else None


def check_function(func, ctx, src=None, asm=None, use_elf=False):
    r = Result(func)
    if asm:
        insns = load_splat_asm(asm)
        r.source = os.path.relpath(asm, ROOT)
    else:
        p = None if use_elf else find_asm(func)
        if p:
            insns = load_splat_asm(p)
            r.source = os.path.relpath(p, ROOT)
        else:
            insns = load_elf_func(ctx.elf, ctx.symmap, func)
            if insns is None:
                r.error = "function not found in asm/us/nonmatchings or %s" % ctx.elf_path
                return r
            r.source = "%s (rebuilt from ELF + emit-relocs)" % os.path.relpath(ctx.elf_path, ROOT)
    if src is None:
        src, _ = find_pragma_file(func)
        if src is None:
            sec = ctx.symmap.section_of(insns[0].vram) if insns else None
            src = find_def_file(func, ctx.symmap, sec[2] if sec else None)
    if src:
        d, ln, kind = extract_draft(src, func)
        r.draft, r.draft_first, r.draft_kind, r.draft_file = d, ln, kind, os.path.relpath(src, ROOT)
    else:
        r.draft_kind = "no C file found"
    events = analyze(insns, ctx.symmap)
    r.flags, r.refs = classify(events, ctx.symmap, r.draft)
    r.notes = draft_pattern_notes(r.draft, r.draft_first or 1, ctx.symmap)
    r.insns = insns
    return r


def sym_desc(s):
    bits = ["0x%08X" % s.addr]
    if s.size is not None:
        bits.append("size %s (%s)" % (hx(s.size), s.size_src))
    else:
        bits.append("size ?")
    if s.ctype:
        bits.append(s.decl_str())
    if not s.defined:
        bits.append("reference-only name")
    return ", ".join(bits)


def print_report(r, ctx, verbose=False):
    print("== %s ==" % r.func)
    if r.error:
        print("  error: " + r.error)
        return
    print("  target: %s" % r.source)
    print("  draft:  %s%s" % (r.draft_kind, (" in %s:%d" % (r.draft_file, r.draft_first)) if r.draft_first else
                              (" (%s)" % r.draft_file if r.draft_file else "")))
    # reference table
    print("\n  symbol references (unique sym/addend/kind):")
    seen = {}
    for ev, S, e in r.refs:
        key = (S.name, e, ev.kind, bool(ev.lin))
        if key in seen:
            seen[key][1] += 1
            continue
        seen[key] = [ev, 1]
    for (name, e, kind, idx), (ev, n) in sorted(seen.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        S = ctx.symmap.syms.get(name)
        strides = sorted({abs(c) for c in ev.lin.values()}, reverse=True)
        print("    %-22s %-8s %-6s %-5s x%-3d %s%s" % (
            name, hx(e) if e else "+0", kind, "idx" if idx else "", n,
            "strides " + ",".join(hx(s) for s in strides) + "  " if strides else "",
            "[" + sym_desc(S) + "]" if verbose or (S and (e < 0 or (S.size is not None and e >= S.size))) else ""))
    if not seen:
        print("    (none)")
    print("\n  flags:")
    if not r.flags:
        print("    none")
    for f in r.flags:
        if f.sev == "I" or (f.sev == "L" and not verbose):
            continue
        at = ",".join("%08X" % v for v in f.vrams[:6]) + (" ..." if len(f.vrams) > 6 else "")
        print("  [%s] %-6s x%d @ %s" % (f.sev, f.kind, f.count, at))
        print("        " + f.msg)
        for n in f.names:
            s = ctx.symmap.syms.get(n)
            if s:
                print("        %s: %s" % (n, sym_desc(s)))
        for s in f.suggest:
            print("        suggest: " + s)
        if f.draft:
            print("        [draft] " + f.draft)
        for ln, txt in draft_lines(r.draft, r.draft_first or 1, f.names):
            print("        draft%s: %s" % ("" if ln is None else " %d" % ln, txt[:150]))
    low = [f for f in r.flags if f.sev == "L"]
    if low and not verbose:
        print("  (%d low-severity flag(s) hidden; -v shows them)" % len(low))
    if r.notes:
        print("\n  draft patterns:")
        for ln, kind, sym, txt in r.notes[:20]:
            print("    %d %-11s %-14s %s" % (ln, kind, sym, txt[:120]))
        if len(r.notes) > 20:
            print("    ... %d more" % (len(r.notes) - 20))
    print()


def summarize(results, title):
    print("%-16s %-4s %-4s %-4s %-6s %s" % ("function", "H", "M", "L", "draft", "worst flag"))
    print("-" * 110)
    for r in results:
        if r.error:
            print("%-16s %s" % (r.func, "error: " + r.error))
            continue
        c = r.counts()
        w = next((f for f in r.flags if f.sev in ("H", "M")), None)
        wtxt = "[%s] %s: %s" % (w.sev, w.kind, w.msg) if w else "-"
        dcol = ("y" if r.draft else "n") + ("/%d" % len(r.notes) if r.notes else "")
        print("%-16s %-4d %-4d %-4d %-6s %s" % (r.func, c["H"], c["M"], c["L"], dcol, wtxt[:150]))
    n = len([r for r in results if not r.error])
    nh = len([r for r in results if not r.error and r.counts()["H"]])
    nm = len([r for r in results if not r.error and (r.counts()["H"] or r.counts()["M"])])
    print("-" * 110)
    print("%s: %d functions, %d with H flags, %d with H or M flags" % (title, n, nh, nm))
    raw = [r for r in results if not r.error and any(f.raw_sev in ("H", "M") for f in r.flags)]
    nref = sum(len(r.refs) for r in results if not r.error)
    print("  before draft-consistency downgrades: %d function(s) with H/M: %s" % (
        len(raw), ", ".join(r.func for r in raw) or "-"))
    print("  symbol references analysed: %d" % nref)


class Ctx:
    def __init__(self, elf_path):
        self.elf_path = elf_path
        self.elf = Elf(elf_path)
        self.symmap = SymMap(self.elf)


def emit_asm(r, ctx, out):
    with open(out, "w") as f:
        f.write("glabel %s\n" % r.func)
        regs = {}
        for ins in r.insns:
            rel = ""
            if ins.reloc:
                kind = ins.reloc[0]
                if kind == "hi":
                    regs[ins.rt] = ins
                    # find matching lo for the full address
                    absaddr = None
                    for j in range(r.insns.index(ins) + 1, min(len(r.insns), r.insns.index(ins) + 40)):
                        k = r.insns[j]
                        if k.reloc and k.reloc[0] == "lo" and k.rs == ins.rt:
                            absaddr = ((ins.imm << 16) + k.simm) & 0xFFFFFFFF
                            break
                else:
                    h = regs.get(ins.rs)
                    absaddr = (((h.imm << 16) if h else 0) + ins.simm) & 0xFFFFFFFF
                if absaddr is not None:
                    s, off = (ctx.symmap.by_name(ins.reloc[1]), None) if ins.reloc[1] else (None, None)
                    if s is not None:
                        off = absaddr - s.addr
                    else:
                        s, off = ctx.symmap.name_for(absaddr)
                    rel = " %%%s(%s%s)" % (kind, s.name if s else "0x%X" % absaddr,
                                           "" if not off else (" + 0x%X" % off if off > 0 else " - 0x%X" % -off))
            f.write("    /* %06X %08X %08X */  %-10s%s\n" % (0, ins.vram, ins.word, mnem_of(ins), rel))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.split("Usage:")[0].strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Usage:" + __doc__.split("Usage:")[1],
    )
    ap.add_argument("func", nargs="?", help="function name, e.g. func_86A01CF0")
    ap.add_argument("--all", action="store_true", help="all GLOBAL_ASM functions: summary table")
    ap.add_argument("--matched-sample", type=int, metavar="N", help="control run on N random matched functions")
    ap.add_argument("--seed", type=int, default=1, help="seed for --matched-sample (default 1)")
    ap.add_argument("--src", help="C file to take the draft from (overrides the pragma search)")
    ap.add_argument("--asm", help="target asm file in splat format (overrides the nonmatchings lookup)")
    ap.add_argument("--elf", default=os.path.join(ROOT, "build", "pokestadiumgs-us.elf"),
                    help="linked ELF with emit-relocs (default build/pokestadiumgs-us.elf)")
    ap.add_argument("--from-elf", action="store_true", help="rebuild FUNC from the ELF even if its .s exists")
    ap.add_argument("--emit-asm", metavar="OUT", help="write the analysed instructions in splat-like syntax")
    ap.add_argument("--details", action="store_true", help="with --all/--matched-sample: full report per function")
    ap.add_argument("-v", "--verbose", action="store_true", help="show low-severity flags and all symbol info")
    ap.add_argument("--sym", metavar="NAME_OR_ADDR", action="append",
                    help="print symbol-map info for a name or 0xADDR (repeatable)")
    a = ap.parse_args()
    if not (a.func or a.all or a.matched_sample or a.sym):
        ap.print_help()
        return 2
    ctx = Ctx(a.elf)
    if a.sym:
        for q in a.sym:
            if q.lower().startswith("0x"):
                addr = int(q, 16)
                s = ctx.symmap.best_at(addr)
                c = ctx.symmap.container(addr)
                print("0x%08X: at=%s container=%s" % (addr, s.name if s else None,
                                                        "%s + %s" % (c.name, hx(addr - c.addr)) if c else None))
                if c:
                    print("   " + decompose(c, addr - c.addr))
            else:
                s = ctx.symmap.by_name(q)
                print("%s: %s" % (q, sym_desc(s) if s else "unknown"))
                if s:
                    print("   sources: %s; decl %s; externs %s" % (",".join(sorted(s.src)), s.decl_loc,
                                                                    [x[0] for x in s.externs][:3]))
        if not (a.func or a.all or a.matched_sample):
            return 0
    if a.func:
        r = check_function(a.func, ctx, src=a.src, asm=a.asm, use_elf=a.from_elf)
        print_report(r, ctx, a.verbose)
        if a.emit_asm and not r.error:
            emit_asm(r, ctx, a.emit_asm)
            print("wrote " + a.emit_asm)
        return 0
    if a.all:
        results = []
        for func, src, _ in all_pragma_funcs():
            r = check_function(func, ctx, src=src)
            results.append(r)
            if a.details:
                print_report(r, ctx, a.verbose)
        summarize(results, "unmatched (GLOBAL_ASM)")
    if a.matched_sample:
        pragma = {f for f, _, _ in all_pragma_funcs()}
        cands = []
        for name, s in ctx.elf.func_syms.items():
            sec = ctx.symmap.section_of(s["value"])
            if not sec or not sec[2].startswith("build/src/") or name in pragma:
                continue
            cands.append(name)
        cands.sort()
        rnd = random.Random(a.seed)
        pick = rnd.sample(cands, min(a.matched_sample, len(cands)))
        results = []
        for func in sorted(pick):
            r = check_function(func, ctx, use_elf=True)
            results.append(r)
            if a.details:
                print_report(r, ctx, a.verbose)
        print()
        summarize(results, "matched control (seed %d, %d candidates)" % (a.seed, len(cands)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
