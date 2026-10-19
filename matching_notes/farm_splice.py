#!/usr/bin/env python3
"""Restore full context to permuter candidates saved with --no-context-output.

Such a source.c holds only the function (and whatever followed it); base.c in the same
directory holds the full import context. This rewrites each trimmed source.c in place as
base.c[:function start] + source.c, so permuter_farm.sh can re-seed from it.

usage: farm_splice.py [save_dir]   (default /scratch/$USER/permuter_best_gs)
"""
import glob
import os
import sys

save_dir = sys.argv[1] if len(sys.argv) > 1 else f"/scratch/{os.environ['USER']}/permuter_best_gs"
for fdir in sorted(glob.glob(os.path.join(save_dir, "func_*"))):
    func = os.path.basename(fdir)
    base_path = os.path.join(fdir, "base.c")
    if not os.path.isfile(base_path):
        continue
    base = open(base_path).read()
    fn_index = base.find(func)
    cut = base.rfind("\n", 0, fn_index) if fn_index != -1 else -1
    if cut == -1:
        print(f"{func}: function not found in base.c, skipped")
        continue
    prefix = base[:cut]
    for src in sorted(glob.glob(os.path.join(fdir, "output-*", "source.c"))):
        text = open(src).read()
        if text.startswith(prefix[:200]):
            continue  # already has context
        open(src, "w").write(prefix + text)
        print(f"{func}: spliced {os.path.relpath(src, save_dir)}")
