#!/usr/bin/env python3
"""llm_decomp.py: LLM-powered decompilation seed generator.

Uses an OpenAI-compatible endpoint (vLLM on a Palmetto GPU node, see
llm_serve.sh) to draft C for functions where m2c fails or is structurally
wrong. The LLM does NOT need to produce byte-exact C — it produces a
semantically right-shaped draft that the existing verification and
refinement layers (fd.sh, permuter farm, agent waves) then close.

Architecture:
    target .s + file context + IDO conventions
        -> LLM (N sampled candidates)
        -> try_candidate.py batch (compile + score + restore)
        -> best candidate per function
        -> seed-branch format (for the permuter) or adoption (if score 0)

Prompt design: the system prompt carries the IDO-7.1 constraints distilled
from IDO_TRICKS.md (types, no-return-void quirks, uopt behaviors) and the
repo's coding conventions. The user prompt carries the function's .s, its
file's existing declarations (from the m2ctx context), and any region doc.

usage:
  .venv/bin/python3 matching_notes/llm_decomp.py --endpoint http://node:8000/v1 \
      --targets <func1,func2,... | m2c-fail | d-structural> \
      --samples 4 --output matching_notes/llm_drafts/
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PY = os.path.join(REPO, ".venv/bin/python3")

SYSTEM_PROMPT = """\
You are an expert MIPS decompiler for a Nintendo 64 game built with IDO 7.1.
Your task: read the IDO 7.1 assembly listing for one function and write the
C source that, when compiled by IDO cc -O2 for MIPS (mips2, -EB, O32 ABI),
produces exactly those instructions.

HARD RULES FOR THE C YOU WRITE:
- Types: u8/s8/u16/s16/u32/s32/f32/f64 only (N64 decomp conventions).
- No #include, no printf, no comments in the function body.
- Function signature: infer from register usage ($a0-$a3 are params, $v0 is
  the return). Floats in $f12/$f14 are f32 params.
- Locals: snake_case, declare exactly the ones the asm spills (count the
  sw/lw pairs in the prologue/epilogue to get the frame size).
- Access struct fields through u8* casts: *(s16*)((u8*)arg0 + 0x1C).
- Switch statements: write a plain C switch with the case values from the
  jump table. IDO emits jr through a table for switches with >3 cases.
- Graphics macros (gSP*, gDP*): call them as regular functions.
- Do NOT try to control register allocation. Write natural, straightforward
  C. IDO's optimizer will allocate registers; the refinement layer fixes
  mismatches.

OUTPUT FORMAT: output ONLY the C function, nothing else. No markdown fences,
no explanation, just the C code starting with the return type.
"""


def find_asm(func):
    asm = os.path.join(REPO, "asm", "us", "nonmatchings")
    for d, _, files in os.walk(asm):
        if func + ".s" in files:
            return os.path.join(d, func + ".s")
    return None


def find_src(func):
    for d, _, files in os.walk(os.path.join(REPO, "src")):
        for f in sorted(files):
            if not f.endswith(".c"):
                continue
            with open(os.path.join(d, f), errors="replace") as fh:
                if re.search(r'GLOBAL_ASM\("[^"]*%s\.s"\)' % re.escape(func), fh.read()):
                    return os.path.relpath(os.path.join(d, f), REPO)
    return None


def extract_context(src_path, func):
    """the file's existing externs and typedefs near the target's splice point"""
    with open(os.path.join(REPO, src_path), errors="replace") as fh:
        text = fh.read()
    m = re.search(r'#pragma\s+GLOBAL_ASM\("[^"]*/%s\.s"\)' % re.escape(func), text)
    if not m:
        return ""
    before = text[max(0, m.start() - 3000):m.start()]
    # keep extern lines, typedefs, and #defines
    lines = []
    for line in before.splitlines():
        if re.match(r'\s*(extern\s|typedef\s|#define\s|(void|s32|u32|u8|s8|f32|s16|u16)\s+\w+\()', line):
            lines.append(line)
    return "\n".join(lines[-30:])


def build_user_prompt(func, asm_text, context, region_note=""):
    parts = [f"Decompile this function (name it `{func}`):\n"]
    if region_note:
        parts.append(f"Region notes from prior work:\n{region_note}\n")
    if context:
        parts.append(f"Existing declarations in this file (use these types/prototypes):\n"
                     f"```c\n{context}\n```\n")
    parts.append(f"Assembly (IDO 7.1, MIPS mips2, O32):\n```\n{asm_text}\n```\n"
                 f"Write the C for `{func}`. Output only the C code.")
    return "\n".join(parts)


def call_llm(endpoint, model, system, user, temperature, max_tokens, api_key=None):
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(
        endpoint.rstrip("/") + "/chat/completions",
        data=body,
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
    msg = data["choices"][0]["message"]
    # reasoning models put output in "reasoning" when content is null
    return msg.get("content") or msg.get("reasoning") or ""


def clean_candidate(text):
    """strip markdown fences and leading/trailing noise"""
    text = text.strip()
    m = re.search(r"```c\s*\n(.*?)```", text, re.S)
    if m:
        text = m.group(1)
    # strip any markdown that survived
    text = re.sub(r"^```.*$", "", text, flags=re.M).strip()
    return text


def verify_candidate(func, src_path, cand_text, workdir):
    """splice, compile, score, restore — via try_candidate.py"""
    os.makedirs(workdir, exist_ok=True)
    cand_path = os.path.join(workdir, f"{func}_cand.c")
    with open(cand_path, "w") as f:
        f.write(cand_text)
    r = subprocess.run(
        [PY, os.path.join(HERE, "try_candidate.py"), src_path, func, cand_path],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    out = r.stdout + r.stderr
    m = re.search(r"CURRENT \((\d+)", out)
    if m:
        return int(m.group(1)), out
    return None, out


def load_targets(spec):
    if spec == "m2c-fail":
        funcs = []
        with open(os.path.join(HERE, "SWEEP_2026-10-19.tsv")) as fh:
            next(fh)
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 6 and p[3] == "fail":
                    funcs.append(p[0])
        return funcs
    if spec == "d-structural":
        funcs = []
        with open(os.path.join(HERE, "SWEEP_2026-10-19.tsv")) as fh:
            next(fh)
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 6 and p[5] == "D_structural":
                    funcs.append(p[0])
        return funcs
    return [f.strip() for f in spec.split(",") if f.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="https://llm.rcd.clemson.edu/v1",
                    help="OpenAI-compatible endpoint (default: RCD gateway)")
    ap.add_argument("--api-key-file",
                    default=os.path.expanduser("~/.config/rcd-llm/api-key"))
    ap.add_argument("--model", default="gptoss-120b",
                    help="model name on the endpoint")
    ap.add_argument("--targets", required=True,
                    help="comma list, 'm2c-fail', or 'd-structural'")
    ap.add_argument("--samples", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--output", default=os.path.join(HERE, "llm_drafts"))
    ap.add_argument("--verify", action="store_true",
                    help="verify candidates (needs the LLM endpoint to be down; "
                         "or run without --verify to just generate)")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    api_key = ""
    if os.path.exists(args.api_key_file):
        with open(args.api_key_file) as f:
            api_key = f.read().strip()

    targets = load_targets(args.targets)
    if args.limit:
        targets = targets[:args.limit]
    print(f"# {len(targets)} targets, {args.samples} samples each")

    os.makedirs(args.output, exist_ok=True)
    generated = 0
    for func in targets:
        asm_path = find_asm(func)
        src_path = find_src(func)
        if not asm_path or not src_path:
            print(f"SKIP {func}: no .s or no src")
            continue
        with open(asm_path, errors="replace") as fh:
            asm_text = fh.read()
        # trim extremely long asm (context window)
        if len(asm_text) > 12000:
            asm_text = asm_text[:12000] + "\n... (truncated)"
        context = extract_context(src_path, func)

        user = build_user_prompt(func, asm_text, context)
        best_text, best_score = None, None
        for i in range(args.samples):
            try:
                raw = call_llm(args.endpoint, args.model, SYSTEM_PROMPT,
                               user, args.temperature, args.max_tokens, api_key)
            except Exception as e:
                print(f"  {func} sample {i}: LLM error {e}")
                continue
            cand = clean_candidate(raw)
            if len(cand) < 20:
                continue
            if args.verify:
                score, out = verify_candidate(func, src_path, cand,
                                               os.path.join(args.output, "tmp"))
                if score is not None and (best_score is None or score < best_score):
                    best_score, best_text = score, cand
            else:
                best_text = cand
                best_score = -1  # unknown
            generated += 1

        if best_text:
            out_path = os.path.join(args.output, f"{func}.c")
            with open(out_path, "w") as f:
                f.write(best_text)
            with open(out_path.replace(".c", ".meta"), "w") as f:
                f.write(f"func={func}\nfile={src_path}\nscore={best_score}\n"
                        f"samples={args.samples}\nsource=llm\n")
            print(f"  {func}: score={best_score} -> {out_path}")
        else:
            print(f"  {func}: no usable candidate")

    print(f"\n{generated} candidates generated for {len(targets)} functions")
    print(f"output: {args.output}/")


if __name__ == "__main__":
    main()
