#!/usr/bin/env python3

import argparse
import re
import os
import shutil
import sys
import subprocess
from pathlib import Path

# assuming that this util is in matching_notes/ (local port; upstream tools/ has no m2ctx)
script_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, ".."))

# Project-specific (mirrors pokestadiumgs Makefile IINC + GBI/LIBULTRA defines)
CPP_FLAGS = [
    "-undef",
    "-D__sgi",
    "-DVERSION_US=1",
    "-DTARGET_N64",
    "-D_LANGUAGE_C",
    "-DF3DEX_GBI_2",
    "-D_MIPS_SZLONG=32",
    "-ffreestanding",
    "-nostdinc",
    "-Iinclude",
    "-Isrc",
    "-Isrc/libnaudio",
    "-Iassets/us",
    "-I.",
    "-Ibuild",
    "-Ilib/ultralib/include",
    "-Ilib/ultralib/include/PR",
    "-Ilib/ultralib/include/ido",
    "-DM2C",
]

def import_c_file(in_file) -> str:

    Message = '/**** Context file for Pokemon Stadium 2 *****/\n'

    in_file = os.path.relpath(in_file, root_dir)
    # Prefer clang as C preprocessor if installed on the system
    if shutil.which('clang') is not None:
        cpp = ['clang', '-E', '-P', '-x', 'c', '-Wno-trigraphs']
    else:
        cpp = ['gcc', '-E', '-P']

    cpp_getdefines = [*cpp, "-dM", *CPP_FLAGS, in_file]
    cpp_procfile = [*cpp, *CPP_FLAGS, in_file]

    out_text = ""
    try:
        out_text += subprocess.check_output(cpp_getdefines, cwd=root_dir, encoding="utf-8")
        out_text += subprocess.check_output(cpp_procfile, cwd=root_dir, encoding="utf-8")
    except subprocess.CalledProcessError:
        print(
            "Failed to preprocess input file, when running command:\n",
            cpp_getdefines,
            file=sys.stderr,
            )
        sys.exit(1)

    if not out_text:
        print("Output is empty - aborting")
        sys.exit(1)
    return Message + out_text

def main():
    parser = argparse.ArgumentParser(
        description="""Create a context file which can be used for mips_to_c"""
        )
    parser.add_argument(
        "c_file",
        help="""File from which to create context""",
        )
    args = parser.parse_args()

    output = import_c_file(args.c_file)

    output = sanitize_ctx(output)

    with open(os.path.join(root_dir, "ctx.c"), "w", encoding="UTF-8") as f:
        f.write(output)




# ------------------------------------------------------------- ctx K&R sanitizer
# src files contain genuine K&R definitions and untyped prototypes; m2c
# hard-rejects the whole ctx ("K&R-style function header is not supported").
# Rewrite them into typed prototypes and drop the bodies (m2c only needs
# declarations). Ported from sweep.py's sanitize_ctx so every ctx.c
# generation (mkdraft, future tools) is safe.

KR_PARAM_RE = re.compile(r"^\s*(?:arg\d+|a[0-3])\s*$")
KR_HDR_RE = re.compile(r"^(\s*)((?:[A-Za-z_]\w*[\s\*]+)+)([A-Za-z_]\w*)\s*\(([^()]*)\)\s*(.*)$")
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
    if not plist.strip():
        return False
    return all(KR_PARAM_RE.match(p) for p in _split_top(plist))

def _parse_decls(decl_text, names):
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
            out.append("%s%s%s();" % (indent, rettype, name))
            i += 1
            continue
        if "{" in rest_s:
            decl_part = rest_s.split("{", 1)[0]
            out.append(_kr_proto(indent, rettype, name, pnames, _parse_decls(decl_part, pnames)))
            bal = line.count("{") - line.count("}")
            i += 1
            while bal > 0 and i < n:
                bal += lines[i].count("{") - lines[i].count("}")
                i += 1
            continue
        if rest_s == "":
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
        out.append(line)
        i += 1
    return "\n".join(out)


if __name__ == "__main__":
    main()
