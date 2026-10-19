#!/usr/bin/env python3
"""Cross-port join: Pokemon Stadium 1 (matched corpus) -> Stadium GS (unmatched asm).

For every GS function under asm/us/nonmatchings/**/*.s (US build, splat/spimdisasm
format), find the best-matching function in S1's matched corpus index
(build/corpus/index.json) using the same weighted n-gram similarity as
matching_notes/corpus.py `siblings`:

  - features: multiset of hashed 1-, 2- and 3-instruction grams over *normalized*
    instructions (register classes t/s/a/v/f, immediates folded to N, branch
    targets to L, called symbols to SYM) -- GS's corpus.normalize() and
    S1's are byte-identical, so the join is apples-to-apples against the
    index's precomputed "norm" streams;
  - grams weighted by idf: log((m+1)/(df+1)) over the S1 matched set;
  - score = shared / max(min(wq,wc), max(wq,wc)/4) * (min/max)^0.3
    (corpus.py SIB_FLOOR=4.0 containment floor, SIB_ALPHA=0.3).

S1 names are re-resolved through the current S1 ELF symbol table (nm), because
the index predates S1's rename waves (index names are mostly func_*, while the
tree now carries GbApu_*/GbSave_*/... names).

Output (stdout): one line per GS function whose best S1 match scores >= --min-score,
sorted by score desc, then cluster summaries (by S1 name prefix / S1 file) and
threshold totals.  Read-only: touches no repo files.

Usage:
  .venv/bin/python3 matching_notes/crossport_join.py [--min-score 0.6] [--top 40]
      [--s1-repo /home/tsranso/Code/pokestadium] [--jobs N] [--sample N] [--debug]
"""

import argparse
import collections
import concurrent.futures
import glob
import json
import math
import multiprocessing
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus as gs_corpus  # GS matching_notes/corpus.py (parse_splat, normalize, sib_features)

SIB_ALPHA = gs_corpus.SIB_ALPHA   # 0.3
SIB_FLOOR = gs_corpus.SIB_FLOOR   # 4.0
S1_REPO_DEFAULT = "/home/tsranso/Code/pokestadium"
S1_INDEX = "build/corpus/index.json"
S1_ELF = "build/pokestadium-us.elf"
NM = os.path.expanduser("~/local/bin/mips-linux-gnu-nm")

# ---- module globals shared with fork()ed workers (built once in the parent) ----
S1_FNS = None      # [{name,file,cc}, ...] matched S1 functions (compact)
POST = None        # gram -> flat [fi, cnt, fi, cnt, ...]
IDF = None         # gram -> idf weight
WEIGHT = None      # fi -> total feature weight (w-style, same as corpus.py)
M = 0              # number of S1 functions in the postings
IDF_MAX = 0.0      # log(m+1): weight of grams unseen in S1


def load_s1(s1_repo, want_c=True):
    """S1 corpus index -> (compact fn list, current-name map addr->name)."""
    path = os.path.join(s1_repo, S1_INDEX)
    with open(path) as fp:
        idx = json.load(fp)
    fns = []
    for f in idx["functions"]:
        if not f.get("matched"):
            continue
        if want_c and not f.get("c"):
            continue  # can't donate C without C
        if not f.get("norm"):
            continue
        fns.append({"name": f["name"], "file": f.get("file", "?"),
                    "cc": f.get("cc", "")})
    names = {}
    elf = os.path.join(s1_repo, S1_ELF)
    if os.path.isfile(elf) and os.path.isfile(NM):
        out = subprocess.run([NM, elf], capture_output=True, text=True, check=True).stdout
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[1] in "TtWw":
                try:
                    names[int(parts[0], 16)] = parts[2]
                except ValueError:
                    pass
    else:
        print("(warning: %s not found; using stale index names)" % elf, file=sys.stderr)
    return fns, names


def build_postings(fns, norms):
    """corpus.py build_siblings math over the S1 matched set."""
    global POST, IDF, WEIGHT, M, IDF_MAX
    M = len(fns)
    IDF_MAX = math.log(M + 1)
    post = collections.defaultdict(list)
    for fi, cnt in enumerate(norms):
        for g, v in cnt.items():
            post[g].append(fi)
            post[g].append(v)
    idf = {}
    weight = [0.0] * M
    for g, pl in post.items():
        idf[g] = w = math.log((M + 1) / (len(pl) // 2 + 1))
        if w <= 0.0:
            continue
        for k in range(0, len(pl), 2):
            weight[pl[k]] += w * pl[k + 1]
    POST, IDF, WEIGHT = dict(post), idf, weight


def s1_addr(name):
    """func_80XXXXXX -> int address (S1 index names encode VRAM)."""
    m = re.match(r"^(?:func|D)_([0-9A-Fa-f]{6,8})$", name)
    return int(m.group(1), 16) if m else None


def score_query(qnorm):
    """corpus.py sib_rank over the S1 postings -> [(score, fi), ...] best first."""
    shared = collections.defaultdict(float)
    wq = 0.0
    for g, v in gs_corpus.sib_features(qnorm).items():
        pl = POST.get(g)
        if not pl:
            wq += v * IDF_MAX
            continue
        w = IDF[g]
        wq += v * w
        if w <= 0.0:
            continue
        it = iter(pl)
        for fi, cnt in zip(it, it):
            shared[fi] += w * (v if v < cnt else cnt)
    out = []
    for fi, s in shared.items():
        wc = WEIGHT[fi]
        lo, hi = (wq, wc) if wq < wc else (wc, wq)
        if lo <= 0:
            continue
        denom = hi / SIB_FLOOR
        out.append((s / (denom if denom > lo else lo) * (lo / hi) ** SIB_ALPHA, fi))
    out.sort(key=lambda r: (-r[0], r[1]))
    return out


def score_file(relpath):
    """Worker: one GS nonmatching .s -> (relpath, gs_name, n_insns, [(score, fi)...])."""
    path = os.path.join(GS_ROOT, relpath)
    try:
        name, raw = gs_corpus.parse_splat(path)
    except Exception as e:  # noqa: BLE001 - never kill the whole run
        return (relpath, "(parse error: %s)" % e, 0, [])
    if name is None:
        name = os.path.basename(relpath)[:-2]
    if not raw:
        return (relpath, name, 0, [])
    qnorm = [gs_corpus.normalize(r) for r in raw]
    if not qnorm:
        return (relpath, name, 0, [])
    ranked = score_query(qnorm)
    return (relpath, name, len(qnorm), ranked[:4])


# -------------------------------------------------------------------------------------
# clustering
# -------------------------------------------------------------------------------------

PREFIX_BUCKETS = ["GbApu", "GbCart", "GbMbc", "GbSave", "GbPak", "GbGfx", "GbRam",
                  "osGb", "Gb", "S1_"]


def s1_cluster(name):
    for p in PREFIX_BUCKETS:
        if name.startswith(p):
            return p + "*"
    if re.match(r"^func_[0-9A-Fa-f]+$", name):
        return "(func_*)"
    head = re.split(r"[_:]", name)[0]
    return head + "_*" if head and head[0].isalpha() else "misc"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--s1-repo", default=S1_REPO_DEFAULT)
    ap.add_argument("--gs-repo", default=os.path.dirname(HERE))
    ap.add_argument("--min-score", type=float, default=0.6)
    ap.add_argument("--top", type=int, default=40, help="print this many lines before truncating")
    ap.add_argument("--jobs", type=int, default=min(16, os.cpu_count() or 4))
    ap.add_argument("--sample", type=int, default=0, help="debug: only first N GS files")
    ap.add_argument("--all-lines", action="store_true",
                    help="never truncate the per-function listing")
    args = ap.parse_args()

    global GS_ROOT
    GS_ROOT = os.path.join(args.gs_repo, "asm", "us", "nonmatchings")

    t0 = time.time()
    fns, names = load_s1(args.s1_repo)
    ren = {i: names.get(a, f["name"]) if (a := s1_addr(f["name"])) is not None else f["name"]
           for i, f in enumerate(fns)}

    # features for every S1 function (reuse index "norm"; ~1.6M grams, a few seconds)
    with open(os.path.join(args.s1_repo, S1_INDEX)) as fp:
        idx = json.load(fp)
    norms = []
    keep = []
    for f in idx["functions"]:
        if not f.get("matched") or not f.get("c") or not f.get("norm"):
            continue
        norms.append(gs_corpus.sib_features(f["norm"]))
        keep.append(f)
    assert len(keep) == len(fns)
    build_postings(fns, norms)
    del idx, norms
    t_index = time.time() - t0

    paths = sorted(os.path.relpath(p, GS_ROOT)
                   for p in glob.glob(os.path.join(GS_ROOT, "**", "*.s"), recursive=True))
    if args.sample:
        paths = paths[:args.sample]
    t1 = time.time()

    ctx = multiprocessing.get_context("fork")  # COW-share POST/IDF/WEIGHT with workers
    rows = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.jobs, mp_context=ctx) as ex:
        for row in ex.map(score_file, paths, chunksize=8):
            rows.append(row)
    t_score = time.time() - t1

    # ---- assemble ----
    matches = []  # (score, gs_name, relpath, n_insn, [(fi, name)...])
    for relpath, gs_name, n_insn, ranked in rows:
        if not ranked:
            continue
        best = ranked[0][0]
        if best < args.min_score:
            continue
        ties = [(fi, ren[fi]) for sc, fi in ranked[:3] if sc >= best - 0.02]
        matches.append((best, gs_name, relpath, n_insn, ties))
    matches.sort(key=lambda r: (-r[0], r[1]))

    n_insns = sum(r[2] for r in rows)
    n_scored = sum(1 for r in rows if r[2])

    print("# crossport_join: GS(us, unmatched) x S1(matched corpus)")
    print("# s1 index: %s (%d fns, %d with C)  s1 elf names: %d resolved"
          % (os.path.join(args.s1_repo, S1_INDEX), len(fns), len(fns), len(names)))
    print("# gs nonmatchings: %d files, %d with insns, %d instructions"
          % (len(rows), n_scored, n_insns))
    print("# index load+postings %.1fs, scoring %.1fs (%d jobs)  min_score=%.2f"
          % (t_index, t_score, args.jobs, args.min_score))
    print()
    print("%-16s %6s  %-12s %s" % ("gs_func", "score", "s1_func", "s1_name(s)"))
    shown = matches if args.all_lines else matches[:args.top]
    for score, gs_name, relpath, n_insn, ties in shown:
        first_fi, first_name = ties[0]
        s1_func = fns[first_fi]["name"]
        more = "" if len(ties) == 1 else "  | also: " + ", ".join(n for _, n in ties[1:])
        print("%-16s %6.3f  %-12s %s  [%s]%s" % (gs_name, score, s1_func, first_name,
                                                 fns[first_fi]["file"], more))
    if not args.all_lines and len(matches) > args.top:
        print("... (%d more below --min %.2f; rerun with --all-lines)"
              % (len(matches) - args.top, args.min_score))
    hidden = matches[args.top:] if not args.all_lines else []

    # ---- cluster summary ----
    def bucket(score):
        return ">=0.9" if score >= 0.9 else (">=0.8" if score >= 0.8 else ">=0.6")

    cl = collections.defaultdict(collections.Counter)
    for score, gs_name, relpath, n_insn, ties in matches:
        c = s1_cluster(ties[0][1])
        cl[c][bucket(score)] += 1
        cl[c]["all"] += 1
    print()
    print("== clusters by S1 name prefix (best match; counts at score buckets) ==")
    print("%-14s %5s %5s %5s %5s" % ("prefix", "all", ">=.9", ">=.8", ">=.6"))
    for c, cnt in sorted(cl.items(), key=lambda kv: -kv[1]["all"]):
        print("%-14s %5d %5d %5d %5d" % (c, cnt["all"], cnt[">=0.9"], cnt[">=0.8"], cnt[">=0.6"]))

    fl = collections.defaultdict(collections.Counter)
    for score, gs_name, relpath, n_insn, ties in matches:
        f = fns[ties[0][0]]["file"]
        fl[f][bucket(score)] += 1
        fl[f]["all"] += 1
    print()
    print("== top S1 source files among matches (func_* hits live here) ==")
    for f, cnt in sorted(fl.items(), key=lambda kv: -kv[1]["all"])[:15]:
        print("%5d (%4d >=.9)  %s" % (cnt["all"], cnt[">=0.9"], f))

    print()
    print("== totals ==")
    for thr in (0.9, 0.8, 0.6):
        print("GS functions with best S1 match >= %.1f : %d" % (thr, sum(1 for m in matches if m[0] >= thr)))
    print("GS functions scanned: %d (%d below %.2f)"
          % (len(rows), len(rows) - len(matches), args.min_score))
    if hidden:
        print("note: %d rows hidden by --top; use --all-lines" % len(hidden))


if __name__ == "__main__":
    main()
