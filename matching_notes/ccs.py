#!/home/tsranso/Code/pokestadiumgs/.venv/bin/python3
"""ccs.py src/file.c func [out.s]: compile src/file.c with IDO cc -S (pre-as1 assembly,
uopt register choices visible) and print that function's .s.

GS port of the Stadium 1 tool: there is no NON_MATCHING draft stage here, so the
matched C of the file is compiled directly (GLOBAL_ASM pragmas are dropped; the
functions they stand for are simply absent from this -S view). A spliced-in
mkdraft/try_candidate body is compiled too, since it is plain C in the file.
Scratch files live under matching_notes/spool/ccs (gitignored) instead of a
repo-root scratch/ dir; the transient x.s lands at the repo root only for the
duration of the run and is moved away immediately.

usage: .venv/bin/python3 matching_notes/ccs.py src/10BB0.c func_80010334 [extra cc flags]
"""
import os, re, subprocess, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(REPO, "matching_notes", "spool", "ccs")
os.makedirs(SCR, exist_ok=True)
src, func = sys.argv[1], sys.argv[2]
text = open(os.path.join(REPO, src)).read()
# drop GLOBAL_ASM pragmas: unmatched functions are omitted from this -S view
text = re.sub(r'#pragma GLOBAL_ASM\([^)]*\)\n', '', text)
out = os.path.join(SCR, "x.c")
open(out, "w").write(text)
# flags mirror the Makefile's IDO 7.1 C compile line (BUILD_DEFINES + IINC + WARNINGS +
# MIPS_VERSION + ENDIAN + COMMON/RELEASE/GBI/LIBULTRA/C defines + OPTFLAGS), minus -c:
# -S stops at ugen/uopt output. No -DNON_MATCHING: GS has no draft stage.
flags = ("-c -G 0 -non_shared -Xcpluscomm -nostdinc -Wab,-r4300_mul -DVERSION_US=1 -Iinclude -Isrc "
         "-Isrc/libnaudio -Iassets/us -I. -Ibuild -Ilib/ultralib/include -Ilib/ultralib/include/PR "
         "-Ilib/ultralib/include/ido -Iinclude/ -woff 624,649,838,712,516,513,596,564,594 -mips2 -EB "
         "-D_MIPS_SZLONG=32 -DNDEBUG -D_FINALROM -DN_MICRO -DF3DEX_GBI_2 -DBUILD_VERSION=VERSION_L "
         "-DLANGUAGE_C -D_LANGUAGE_C -O2").split()
extra = ["-I" + os.path.dirname(src)] + (sys.argv[3:] if len(sys.argv) > 3 else [])
p = subprocess.run([os.path.join(REPO, "tools/ido/linux/7.1/cc"), "-S"] + flags + extra + [out],
                   cwd=REPO, capture_output=True, text=True)
errs = [l for l in (p.stdout + p.stderr).splitlines() if "Warning" not in l and l.strip()]
if errs:
    print("\n".join(errs[:20]))
# IDO writes <basename>.s into the cwd (the repo root), not next to the input file
s_path = os.path.join(REPO, "x.s")
if not os.path.exists(s_path):
    sys.exit("ccs: no x.s produced (compile failed?) -- output above")
s = open(s_path).read()
os.rename(s_path, os.path.join(SCR, "x.s"))
i = s.find("\t.ent\t%s" % func)
j = s.find("\t.end\t%s" % func, i)
if i < 0 or j < 0:
    sys.exit("ccs: %s not found in x.s (kept at %s)" % (func, os.path.join(SCR, "x.s")))
print(s[i:j])
