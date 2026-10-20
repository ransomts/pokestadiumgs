#!/usr/bin/env python3
"""llm_multiseed.py: generate diverse seeds for a function and populate the
permuter's SAVE_DIR so the farm's DIVERSITY mechanism starts copies from
different structural basins.

The permuter's re-seed/diversity logic (permuter_farm.sh):
  - copy 1 starts from the best saved candidate (or the imported seed)
  - copies 2+ start from the k-th best DISTINCT saved candidate
So pre-populating SAVE_DIR/<func>/output-<score>-<N>/source.c with verified
LLM candidates automatically gives each copy a different starting point.

This tool:
  1. Sends the .s + context to the LLM N times at high temperature
     (different samples = different structural interpretations)
  2. Verifies each through try_candidate.py (compile + score)
  3. Deduplicates near-identical candidates (AST-level hash)
  4. Writes the top K diverse candidates into SAVE_DIR in the permuter's
     expected format (output-<score>-<N>/source.c + score.txt)
  5. Optionally runs the LLM-crossover pass: takes the best 2 candidates,
     sends both + their per-instruction diff alignment to the target, and
     asks the LLM to merge them

usage:
  .venv/bin/python3 matching_notes/llm_multiseed.py <func> --samples 8 [--top 4]
  .venv/bin/python3 matching_notes/llm_multiseed.py <func> --crossover
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PY = os.path.join(REPO, ".venv/bin/python3")
SAVE_DIR = "/scratch/tsranso/permuter_best_gs"

# reuse the shared machinery
sys.path.insert(0, HERE)
from llm_decomp import (
    SYSTEM_PROMPT, call_llm, clean_candidate, find_asm, find_src,
    extract_context, build_user_prompt, verify_candidate,
)

CROSSOVER_SYSTEM = """\
You are an expert MIPS decompiler merging two candidate C implementations.
Both candidates were compiled and compared against the target assembly; you
will see which sections of each match the target (marked GOOD) and which
differ (marked DIFF). Write a single merged C function that uses the
APPROACH of candidate A where A matches and the approach of candidate B
where B matches. The merged function must compile under IDO cc -O2.

Output ONLY the merged C function, nothing else.
"""


def llm_candidates(func, src_path, n, endpoint, model, api_key,
                   temperature=0.9, max_tokens=4096):
    """generate n diverse candidates via temperature sampling"""
    asm_path = find_asm(func)
    if not asm_path:
        sys.exit(f"no .s for {func}")
    with open(asm_path, errors="replace") as fh:
        asm_text = fh.read()
    if len(asm_text) > 12000:
        asm_text = asm_text[:12000] + "\n... (truncated)"
    context = extract_context(src_path, func)
    user = build_user_prompt(func, asm_text, context)

    cands = []
    for i in range(n):
        try:
            raw = call_llm(endpoint, model, SYSTEM_PROMPT, user,
                           temperature, max_tokens, api_key)
        except Exception as e:
            print(f"  sample {i}: LLM error {e}")
            continue
        cand = clean_candidate(raw)
        if len(cand) > 30:
            cands.append(cand)
    return cands


def structural_hash(text):
    """normalize away names/formatting; keep structure (blocks, calls, ops)"""
    t = re.sub(r"\b(var_\w+|temp_\w+|sp\w+|new_\w+)\b", "V", text)
    t = re.sub(r"\b\d+\b", "N", t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"func_\w+", "F", t)
    t = re.sub(r"D_\w+", "D", t)
    return hashlib.md5(t.encode()).hexdigest()


def score_and_dedup(func, src_path, cands, workdir):
    """verify each candidate; return [(score, text, hash)] sorted"""
    os.makedirs(workdir, exist_ok=True)
    seen_hashes = set()
    results = []
    for i, cand in enumerate(cands):
        h = structural_hash(cand)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        # repair pass: find undeclared identifiers, prepend their ctx.c externs
        cand = repair_declarations(func, cand, src_path)
        cand_path = os.path.join(workdir, f"{func}_c{i}.c")
        with open(cand_path, "w") as f:
            f.write(cand)
        r = subprocess.run(
            [PY, os.path.join(HERE, "try_candidate.py"), src_path, func,
             cand_path],
            cwd=REPO, capture_output=True, text=True, timeout=120,
        )
        m = re.search(r"CURRENT \((\d+)", r.stdout + r.stderr)
        if m:
            results.append((int(m.group(1)), cand, h))
            print(f"  candidate {i}: score {m.group(1)}")
        else:
            print(f"  candidate {i}: compile fail")
    results.sort(key=lambda r: r[0])
    return results


def repair_declarations(func, cand, src_path, max_rounds=3):
    """find undeclared identifiers from compile errors and prepend ctx.c externs"""
    import tempfile
    prologue = []
    for _ in range(max_rounds):
        # prepend existing prologue lines
        text = "\n".join(prologue) + "\n" + cand if prologue else cand
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False,
                                         dir="/tmp/opencode") as tf:
            tf.write(text)
            tf.flush()
            r = subprocess.run(
                [PY, os.path.join(HERE, "try_candidate.py"), src_path, func,
                 tf.name],
                cwd=REPO, capture_output=True, text=True, timeout=60,
            )
            os.unlink(tf.name)
            out = r.stdout + r.stderr
        if "CURRENT (" in out:
            return text  # compiles
        # extract undeclared identifiers
        missing = set()
        for line in out.splitlines():
            m = re.search(r"'(\w+)' undeclared", line)
            if m and m.group(1) != func:
                missing.add(m.group(1))
        if not missing:
            return text  # different error class, give up
        # look up in ctx.c
        ctx_path = os.path.join(REPO, "ctx.c")
        decls_to_add = []
        if os.path.exists(ctx_path):
            with open(ctx_path, errors="replace") as cf:
                ctx_text = cf.read()
            for name in missing:
                pat = re.compile(
                    r"^\s*extern\s[^;]+?\b%s\s*(?:\(|\[|;)" % re.escape(name),
                    re.M,
                )
                m = pat.search(ctx_text)
                if m:
                    d = m.group(0).strip()
                    if d.endswith(")") and not d.endswith(";"):
                        d += ";"
                    decls_to_add.append(d)
        if not decls_to_add:
            return text  # can't repair
        prologue.extend(decls_to_add)
    return "\n".join(prologue) + "\n" + cand


def populate_save_dir(func, results, top_k):
    """write the top K diverse candidates into SAVE_DIR in permuter format"""
    fdir = os.path.join(SAVE_DIR, func)
    os.makedirs(fdir, exist_ok=True)
    count = 0
    for i, (score, cand, _) in enumerate(results[:top_k]):
        outdir = os.path.join(fdir, f"output-llm-{i}")
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "source.c"), "w") as f:
            f.write(cand)
        with open(os.path.join(outdir, "score.txt"), "w") as f:
            f.write(str(score))
        count += 1
    print(f"  populated {count} candidates in {fdir}/output-llm-*/")
    return count


def crossover(func, src_path, endpoint, model, api_key, workdir):
    """take the best 2 candidates, ask the LLM to merge them"""
    fdir = os.path.join(SAVE_DIR, func)
    # find the two best saved candidates
    best = []
    for d in sorted(os.listdir(fdir)):
        score_file = os.path.join(fdir, d, "score.txt")
        source_file = os.path.join(fdir, d, "source.c")
        if os.path.exists(score_file) and os.path.exists(source_file):
            with open(score_file) as f:
                best.append((int(f.read()), d, source_file))
    best.sort()
    if len(best) < 2:
        print("  crossover: need 2+ candidates")
        return None
    _, d1, s1 = best[0]
    _, d2, s2 = best[1]
    with open(s1) as f:
        cand_a = f.read()
    with open(s2) as f:
        cand_b = f.read()

    # get the target asm for the diff
    asm_path = find_asm(func)
    with open(asm_path, errors="replace") as fh:
        asm_text = fh.read()[:6000]

    user = f"""Merge these two candidates for {func}:

CANDIDATE A (from {d1}):
```c
{cand_a[:3000]}
```

CANDIDATE B (from {d2}):
```c
{cand_b[:3000]}
```

Target assembly (first 60 lines):
```
{asm_text[:3000]}
```

Write the merged C for `{func}`. Output only the C code."""

    try:
        raw = call_llm(endpoint, model, CROSSOVER_SYSTEM, user,
                       0.5, 4096, api_key)
    except Exception as e:
        print(f"  crossover LLM error: {e}")
        return None
    merged = clean_candidate(raw)
    if len(merged) < 30:
        return None
    # verify the merge
    merged_path = os.path.join(workdir, f"{func}_merged.c")
    with open(merged_path, "w") as f:
        f.write(merged)
    r = subprocess.run(
        [PY, os.path.join(HERE, "try_candidate.py"), src_path, func,
         merged_path],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    m = re.search(r"CURRENT \((\d+)", r.stdout + r.stderr)
    if m:
        score = int(m.group(1))
        print(f"  crossover result: score {score}")
        return score, merged
    print("  crossover: compile fail")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("func")
    ap.add_argument("--src", help="src file (found via pragma if omitted)")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--top", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=0.9)
    ap.add_argument("--model", default="leanstral-2603")
    ap.add_argument("--endpoint", default="https://llm.rcd.clemson.edu/v1")
    ap.add_argument("--api-key-file",
                    default=os.path.expanduser("~/.config/rcd-llm/api-key"))
    ap.add_argument("--crossover", action="store_true")
    ap.add_argument("--workdir", default="/tmp/opencode/llm_multiseed")
    args = ap.parse_args()

    api_key = ""
    if os.path.exists(args.api_key_file):
        with open(args.api_key_file) as f:
            api_key = f.read().strip()

    src = args.src or find_src(args.func)
    if not src:
        sys.exit(f"no src for {args.func}")

    print(f"generating {args.samples} candidates for {args.func}...")
    cands = llm_candidates(args.func, src, args.samples, args.endpoint,
                           args.model, api_key, args.temperature)
    print(f"  {len(cands)} usable candidates")

    print("scoring and deduplicating...")
    results = score_and_dedup(args.func, src, cands, args.workdir)
    print(f"  {len(results)} distinct, verified candidates")

    if results:
        print(f"populating SAVE_DIR (top {args.top})...")
        populate_save_dir(args.func, results, args.top)

    if args.crossover and len(results) >= 2:
        print("running LLM crossover...")
        x = crossover(args.func, src, args.endpoint, args.model, api_key,
                      args.workdir)
        if x:
            score, merged = x
            # add the crossover result too if it beats the worst saved
            if results and score < results[0][0]:
                outdir = os.path.join(SAVE_DIR, args.func, "output-llm-x")
                os.makedirs(outdir, exist_ok=True)
                with open(os.path.join(outdir, "source.c"), "w") as f:
                    f.write(merged)
                with open(os.path.join(outdir, "score.txt"), "w") as f:
                    f.write(str(score))
                print(f"  crossover beat the best seed ({score}) — saved")


if __name__ == "__main__":
    main()
