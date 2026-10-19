#!/usr/bin/env python3
"""
Emit a git-apply(1)-compatible unified diff of
linker_scripts/us/symbol_addrs_code.txt between two revisions, restricted to
changed lines whose symbol is in a requested set.

Changes for symbols NOT in the set are reverted to their base-revision
content, so the emitted diff applies on top of the base revision and contains
exactly the requested symbol changes.  The filtered postimage is written to
the object database (git hash-object -w) and referenced from an `index` line,
so `git apply --3way` works against it.

Usage:
    upstream_filter_addrs.py --base 0ed2fd9f --ref farm-port \
        [--symbols NAME1,NAME2,... | --symbols-file FILE] [--path PATH]

Both the old (base) and new (ref) symbol names of a rename should be passed;
a change block is kept when any symbol it touches is in the set.  With no
matching changes the script emits nothing and exits 0.
"""
import argparse
import difflib
import subprocess
import sys

DEFAULT_PATH = "linker_scripts/us/symbol_addrs_code.txt"


def _run(args, input_text=None):
    return subprocess.run(
        args, input=input_text,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, check=True,
    )


def git_show_lines(rev: str, path: str):
    return _run(["git", "show", f"{rev}:{path}"]).stdout.splitlines(keepends=True)


def git_rev_blob(rev: str, path: str) -> str:
    return _run(["git", "rev-parse", f"{rev}:{path}"]).stdout.strip()


def hash_object_w(content: str) -> str:
    return _run(["git", "hash-object", "-w", "--stdin"], input_text=content).stdout.strip()


def symbol_of(line: str) -> str:
    # "Name = 0xADDR; // type:func" -> "Name"
    return line.split("=", 1)[0].strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--base", required=True, help="base revision (preimage)")
    ap.add_argument("--ref", required=True, help="revision with our renames")
    ap.add_argument("--symbols", help="comma-separated symbol names to keep")
    ap.add_argument("--symbols-file", help="file with one symbol name per line")
    ap.add_argument("--path", default=DEFAULT_PATH)
    args = ap.parse_args()

    if args.symbols_file:
        with open(args.symbols_file) as f:
            keep = {ln.strip() for ln in f if ln.strip()}
    else:
        keep = {s.strip() for s in (args.symbols or "").split(",") if s.strip()}
    if not keep:
        sys.stderr.write("error: no symbols requested\n")
        return 2

    old = git_show_lines(args.base, args.path)
    new = git_show_lines(args.ref, args.path)

    # Walk change blocks; revert every block that does not touch a kept
    # symbol so the remaining diff is exactly the requested renames.
    kept = list(new)
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    for tag, i1, i2, j1, j2 in reversed(sm.get_opcodes()):
        if tag == "equal":
            continue
        touched = {symbol_of(l) for l in old[i1:i2]}
        touched |= {symbol_of(l) for l in new[j1:j2]}
        if not (touched & keep):
            kept[j1:j2] = old[i1:i2]

    if kept == new and old == new:
        return 0  # no changes at all

    body = difflib.unified_diff(
        old, kept,
        fromfile=f"a/{args.path}", tofile=f"b/{args.path}",
        n=3,
    )
    body = list(body)
    if not body:
        return 0  # nothing kept for this symbol set

    postimage = "".join(kept)
    old_sha = git_rev_blob(args.base, args.path)
    new_sha = hash_object_w(postimage)  # enables `git apply --3way`

    sys.stdout.write(f"diff --git a/{args.path} b/{args.path}\n")
    sys.stdout.write(f"index {old_sha[:7]}..{new_sha[:7]} 100644\n")
    sys.stdout.writelines(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
