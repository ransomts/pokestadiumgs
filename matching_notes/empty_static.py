#!/usr/bin/env python3
"""empty_static.py: find functions whose target .s ends with the dead
jr ra; nop / jr ra; nop double-tail (an unreferenced static empty function
inside the map range).

IDO 7.1 never dead-strips statics and emits exactly `jr ra; nop` for an
empty body; statics get no map symbol, so the map shows the trailing pair
as part of the PRECEDING function. Any candidate match for such a function
needs `static void <next_addr_name>(void) {}` spliced alongside it
(cfe/ugen provably dissolve every in-source construct).

usage:
  .venv/bin/python3 matching_notes/empty_static.py find
  .venv/bin/python3 matching_notes/empty_static.py make-stub <func> <next-hex>
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASM = os.path.join(REPO, "asm", "us", "nonmatchings")

INSN_RE = re.compile(r"/\*\s*([0-9A-F]{6,8})\s+([0-9A-F]{8})\s+([0-9A-F]{8})\s*\*/")
JR_RA = "03E00008"
NOP = "00000000"


def find_all():
    out = []
    for d, _, files in os.walk(ASM):
        for f in sorted(files):
            if not f.endswith(".s"):
                continue
            path = os.path.join(d, f)
            words = []  # (opcode, vram) for insns, ("label",) separators
            with open(path) as fh:
                for line in fh:
                    m = INSN_RE.search(line)
                    if m:
                        words.append((m.group(3), m.group(2)))  # opcode, vram
                    elif re.match(r"\s*(glabel|\.L)", line):
                        words.append(("label", None))
            if len(words) < 4:
                continue
            tail = words[-4:]
            # pattern: jr ra / nop / jr ra / nop, and no label between the
            # two pairs (a label on the final jr means it is reachable and
            # therefore not a separate function)
            if (
                tail[0][0] == JR_RA and tail[1][0] == NOP
                and tail[2][0] == JR_RA and tail[3][0] == NOP
                and all(w[0] != "label" for w in tail)
            ):
                stub_vram = int(tail[2][1], 16)
                out.append((f[:-2], stub_vram))
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "find"
    if mode == "find":
        for func, addr in find_all():
            print(f"{func}\tstub=0x{addr:08X}\tstatic void func_{addr:08X}(void) {{}}")
    elif mode == "make-stub" and len(sys.argv) == 4:
        nxt = sys.argv[3]
        print(f"\nstatic void func_{nxt}(void) {{}}\n")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
