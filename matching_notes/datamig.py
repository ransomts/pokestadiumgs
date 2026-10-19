#!/usr/bin/env python3
"""datamig: execute blob-ownership data migrations (the wave-1 func_82202628 class).

A parked score-0 match whose statics/jtbls/literals live in an asm-owned data
blob cannot be adopted until the blob splits and the C object owns its bytes.
Every such function in matching_notes/spool/*.meta carries a hand-verified
recipe; this tool executes them reproducibly.

Recipe format (Python module with a RECIPE dict), see datamig_recipes/:

    RECIPE = {
        "name": "fragment17_82202628",
        "steps": [
            {"op": "splice", "spool": "func_82202628",
             "file": "src/fragments/17/fragment17_10FFC0.c",
             "func": "func_82202628"},
            {"op": "edit", "file": "...", "find": "...", "replace": "..." | None},
            {"op": "yaml", "find": "- [0x11DAB0, .rodata, fragments/17/fragment17_10FFC0]",
             "replace": "- [0x11DA90, .rodata, fragments/17/fragment17_10FFC0]"},
            {"op": "yaml", "find": "- [0x11DAB0, rodata]",
             "insert_after": ["- [0x11DA90, .rodata, x] # comment"]},
            {"op": "ld", "lines": ["SECTION NAME (NOLOAD) : { ... }"]},  # aliases.ld
        ],
    }

Safety: every `find` must occur exactly once in its file; the run aborts
before the build gate if anything mismatches. The gate is two full
extract+make cycles, both of which must print the ROM-OK line.

usage: .venv/bin/python3 matching_notes/datamig.py run|check <recipe-name>
"""
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RECIPES = os.path.join(HERE, "datamig_recipes")
ROM_OK = "build/pokestadiumgs-us.z64: OK"


def load_recipe(name):
    p = os.path.join(RECIPES, name + ".py")
    if not os.path.exists(p):
        sys.exit(f"no recipe {p}")
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.RECIPE


def read(f):
    with open(os.path.join(REPO, f)) as fh:
        return fh.read()


def write(f, text):
    p = os.path.join(REPO, f)
    with open(p, "w") as fh:
        fh.write(text)
    os.utime(p, None)


def splice(spool, file, func):
    r = subprocess.run(
        [os.path.join(REPO, ".venv/bin/python3"),
         os.path.join(HERE, "splice_manual.py"), file, func,
         os.path.join(HERE, "spool", spool + ".c")],
        cwd=REPO, capture_output=True, text=True,
    )
    print("  splice:", (r.stdout or r.stderr).strip())
    if r.returncode != 0:
        sys.exit("splice failed")


def apply_edit(file, find, replace):
    text = read(file)
    n = text.count(find)
    if n != 1:
        sys.exit(f"edit: {find!r} occurs {n}x in {file} (want exactly 1)")
    write(file, text.replace(find, replace if replace is not None else ""))


def apply_yaml(find, replace=None, insert_after=None):
    apply_edit("yamls/us/rom.yaml", find, replace)
    if insert_after:
        text = read("yamls/us/rom.yaml")
        if text.count(find) != 1:
            sys.exit(f"yaml anchor {find!r} not unique")
        write("yamls/us/rom.yaml",
              text.replace(find, find + "\n" + "\n".join(insert_after)))


def apply_ld(lines):
    text = read("linker_scripts/us/aliases.ld")
    block = "\n/* datamig: NOLOAD section (fixed-address C-owned bss) */\n" + \
            "\n".join(lines) + "\n"
    write("linker_scripts/us/aliases.ld", text + block)


def run_steps(steps, dry):
    for st in steps:
        op = st["op"]
        if dry:
            # verify finds without applying
            text = read(st.get("file", "yamls/us/rom.yaml"))
            f = st.get("find")
            if f and text.count(f) != 1:
                sys.exit(f"check: {f!r} occurs {text.count(f)}x (want 1)")
            print(f"  ok: {op} {str(f)[:60]}")
            continue
        if op == "splice":
            splice(st["spool"], st["file"], st["func"])
        elif op == "edit":
            apply_edit(st["file"], st["find"], st.get("replace"))
            print(f"  edit: {st['file']}")
        elif op == "yaml":
            if st.get("replace") is not None:
                apply_yaml(st["find"], st["replace"])
            else:
                apply_yaml(st["find"], insert_after=st.get("insert_after", []))
            print(f"  yaml: {st['find'][:60]}")
        elif op == "ld":
            apply_ld(st["lines"])
            print("  ld: aliases.ld + section")
        else:
            sys.exit(f"unknown op {op}")


def gate():
    env = dict(os.environ)
    env["PATH"] = os.path.join(REPO, ".venv/bin") + ":" + env.get("PATH", "")
    for cycle in (1, 2):
        for target in ("extract", "rom"):
            r = subprocess.run(
                ["make", target, "-j32", f"PYTHON={REPO}/.venv/bin/python3"],
                cwd=REPO, capture_output=True, text=True, env=env, timeout=1200,
            )
            out = r.stdout + r.stderr
            if r.returncode != 0 or (target == "rom" and ROM_OK not in out):
                tail = "\n".join(out.splitlines()[-12:])
                sys.exit(f"gate cycle {cycle} ({target}) FAILED:\n{tail}")
        print(f"  gate cycle {cycle}: extract + make OK")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("run", "check"):
        sys.exit(__doc__)
    recipe = load_recipe(sys.argv[2])
    print(f"recipe: {recipe['name']} ({len(recipe['steps'])} steps)")
    run_steps(recipe["steps"], dry=(sys.argv[1] == "check"))
    if sys.argv[1] == "run":
        gate()
        print("DONE:", recipe["name"])


if __name__ == "__main__":
    main()
