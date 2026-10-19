#!/bin/bash
# Run decomp-permuter on several functions in parallel, seeded from the best known source.
#
# usage: matching_notes/permuter_farm.sh <repo> <default_workers> <hours> func_X:src/a.c[:W[:C]] ...
#
# - <repo> must be a full checkout with .venv, asm/, tools/permuter (symlinks are fine).
# - GS has no committed drafts: import.py reads each function's body from the C as compiled
#   in <repo>, so its seed must already be spliced into the src/ file there (palmetto_job.sh
#   SEED_BRANCH=<branch> stages a branch carrying the spliced seeds, or splice by hand).
# - Per-function tuning: `func:src:W:C` runs that function with W workers and C copies
#   (defaults: the <default_workers> arg and $COPIES). Copies are independent permuters on
#   the same function, the only way past the ~80 it/s main-process cap, so small functions
#   want many copies x 2-3 workers and slow-compiling giants want few copies x 5-6 workers.
# - Work dir: $FARM_DIR (default $TMPDIR/permuter, the job-private local SSD). Improved candidates
#   land in $FARM_DIR/nonmatchings/<func>/output-<score>-<n>/source.c and are rsynced to
#   $SAVE_DIR (default /scratch/$USER/permuter_best_gs) every $SYNC_SECS (120) and at the end.
# - Checkpoint/restart: the saved candidates ARE the checkpoint (the search itself is memoryless).
#   On start, if $SAVE_DIR/<func>/output-*/source.c exists, the lowest-scoring one replaces the
#   imported base.c (RESEED=0 disables). Delete $SAVE_DIR/<func> to start from the seed again.
# - Mid-run re-seed: after every sync, a copy trailing its function's global best (across all
#   copies and all jobs sharing $SAVE_DIR) by RESEED_PCT% (default 10) plus RESEED_ABS (default
#   15) score points is restarted from that best candidate — at most once per RESEED_COOLDOWN
#   (2700 s), never the copy holding the best, and never in the last RESEED_MIN_LEFT (600 s) of
#   the farm. A restart only forfeits the in-flight candidate; its saved candidates stay in
#   $SAVE_DIR. RESEED_PCT=0 disables all of this. A global best of 0 means the function matched:
#   its remaining copies are stopped (--stop-on-zero already stops the copy that found it).
# - Observability: each <func>.log has timestamped improvement lines plus a STATUS snapshot
#   every $SNAP_SECS (300) with iterations, errors and it/s; `re-seed` lines mark mid-run
#   restarts. Summarise with farm_status.sh.
# - Judge candidates with matching_notes/fd.sh, not the permuter score (statics inflate it).
# - COPIES=N (default 1) is the default copy count for functions without an explicit :C.
# - DIVERSITY=1 (default): copies past the first re-seed from the k-th best distinct saved
#   candidate instead of the single best, so copies explore different basins. DIVERSITY=0
#   makes every copy start from the global best.
# - RUN_TAG=x names this job's runs <func>__x1, <func>__x2, ... so several jobs can share SAVE_DIR.
# - FOCUS_DIR=dir: start <func> from dir/<func>.c when present (a candidate with PERM_RANDOMIZE()
#   around the code that still differs) instead of the import/re-seed.
set -u
REPO=$(readlink -f "$1"); WORKERS=$2; HOURS=$3; shift 3
FARM_DIR=${FARM_DIR:-${TMPDIR:-/tmp}/permuter}
SAVE_DIR=${SAVE_DIR:-/scratch/$USER/permuter_best_gs}
SYNC_SECS=${SYNC_SECS:-120}  # cheap; scancel did not trigger the TERM sync (2026-10-16), so sync often
SNAP_SECS=${SNAP_SECS:-300}
RESEED=${RESEED:-1}
RESEED_PCT=${RESEED_PCT:-10}
RESEED_ABS=${RESEED_ABS:-15}
RESEED_COOLDOWN=${RESEED_COOLDOWN:-2700}
RESEED_MIN_LEFT=${RESEED_MIN_LEFT:-600}
COPIES=${COPIES:-1}
RUN_TAG=${RUN_TAG:-}
FOCUS_DIR=${FOCUS_DIR:-}
HERE=$(cd "$(dirname "$0")" && pwd)
FOCUS_DIR=${FOCUS_DIR:-$HERE/focus}  # per-function focused starts; presence of <func>.c opts in
HERE=$(cd "$(dirname "$0")" && pwd)
PY="$REPO/.venv/bin/python3"
export PATH="$REPO/.venv/bin:$HOME/local/bin:/usr/local/bin:/usr/bin:/bin"
export PYTHONUNBUFFERED=1
mkdir -p "$FARM_DIR" "$SAVE_DIR"
cd "$FARM_DIR" || exit 1
ln -sfn "$REPO/tools" tools 2>/dev/null
shopt -s nullglob
END_AT=$(( $(date +%s) + $(awk "BEGIN{printf \"%d\", $HOURS * 3600}") ))
FARM_START=$(date +%s)
declare -A sub started seedv run_workers

best_saved() {  # print path of the lowest-scoring saved source.c for $1, if any
    local best= bestv=
    for s in "$SAVE_DIR/$1"/output-*/score.txt "$SAVE_DIR/$1"__*/output-*/score.txt; do
        [ -f "$s" ] || continue
        v=$(cat "$s")
        if [ -z "$bestv" ] || [ "$v" -lt "$bestv" ]; then bestv=$v; best=${s%score.txt}source.c; fi
    done
    [ -n "$best" ] && [ -f "$best" ] && echo "$best"
}

best_kth() {  # $1=func $2=k: k-th best DISTINCT saved candidate, by score then content hash
              # (equal-score ties are different basins and count separately). Empty if < k.
    local f=$1 k=$2 s line path h x skip n=0
    local -a cands=() seen=()
    for s in "$SAVE_DIR/$f"/output-*/score.txt "$SAVE_DIR/$f"__*/output-*/score.txt; do
        [ -f "$s" ] && [ -f "${s%score.txt}source.c" ] || continue
        cands+=("$(cat "$s") ${s%score.txt}source.c")
    done
    [ ${#cands[@]} -ge 1 ] || return 0
    while IFS= read -r line; do
        path=${line#* }
        h=$(md5sum < "$path" 2>/dev/null | cut -d" " -f1)
        [ -n "$h" ] || continue
        skip=0
        for x in "${seen[@]}"; do [ "$x" = "$h" ] && skip=1; done
        [ "$skip" = 1 ] && continue
        seen+=("$h")
        n=$((n+1))
        [ "$n" -eq "$k" ] && { echo "$path"; return 0; }
    done < <(printf '%s\n' "${cands[@]}" | sort -n)
    return 0
}

score_of() {  # print the lowest score.txt under $1/output-*/, empty if there is none
    local s v bestv=
    for s in "$1"/output-*/score.txt; do
        [ -f "$s" ] || continue
        v=$(cat "$s")
        if [ -z "$bestv" ] || [ "$v" -lt "$bestv" ]; then bestv=$v; fi
    done
    echo "$bestv"
}

seed_score() {  # $1 = a candidate's source.c; its score.txt sits in the same dir
    cat "$(dirname "$1")/score.txt" 2>/dev/null
}

start_run() {  # $1=run $2=workers: launch one permuter for the run, until END_AT
    local run=$1 secs
    secs=$(( END_AT - $(date +%s) )); [ "$secs" -lt 60 ] && secs=60
    ( timeout "$secs" "$PY" "$REPO/tools/permuter/permuter.py" "nonmatchings/$run" \
          --stack-diffs --best-only --stop-on-zero -j"$2" 2>&1 \
      | "$PY" "$HERE/farm_logfilter.py" "$SNAP_SECS" >> "nonmatchings/$run.log" ) &
    sub[$run]=$!
    started[$run]=$(date +%s)
    run_workers[$run]=$2
}

kill_run() {  # $1=run: stop the permuter processes of one run (TERM, then KILL)
    pkill -TERM -f "nonmatchings/$1 " 2>/dev/null
    for _ in $(seq 1 20); do pgrep -f "nonmatchings/$1 " >/dev/null 2>&1 || return 0; sleep 0.5; done
    pkill -KILL -f "nonmatchings/$1 " 2>/dev/null
}

reseed_restart() {  # $1=run $2=best source.c: restart the run seeded from $2
    local run=$1 src=$2
    echo "$(date '+%F %T') re-seed $run from $src"
    echo "$(date '+%F %T') re-seed from $src" >> "nonmatchings/$run.log"
    kill_run "$run"
    rm -rf "nonmatchings/$run"/output-*  # stale (already synced to SAVE_DIR) and would mask the new seed
    cp "$src" "nonmatchings/$run/base.c"
    seedv[$run]=$(seed_score "$src")
    start_run "$run" "${run_workers[$run]}"
}

reseed_check() {  # after a sync: restart copies trailing their function's global best,
                  # and stop copies of functions that matched elsewhere
    [ "$RESEED_PCT" -gt 0 ] || return 0
    local now run func own gsrc gscore
    now=$(date +%s)
    for run in "${!sub[@]}"; do
        kill -0 "${sub[$run]}" 2>/dev/null || continue          # finished already (matched or crashed)
        [ $(( END_AT - now )) -gt "$RESEED_MIN_LEFT" ] || continue
        [ $(( now - ${started[$run]} )) -ge "$RESEED_COOLDOWN" ] || continue
        func=${run%%__*}
        own=$(score_of "nonmatchings/$run"); [ -n "$own" ] || own=${seedv[$run]:-}
        [ -n "$own" ] || continue
        gsrc=$(best_saved "$func"); [ -n "$gsrc" ] || continue
        # Metric-era gate: rename waves / re-extracts change symbol-era scoring, so a
        # score.txt older than this farm is not comparable to current scores (2026-10-17:
        # func_88805AEC's pre-rename "1228" churned every reseed onto a worse base). Only
        # mid-run re-seed onto candidates saved since the farm started.
        [ "$(stat -c %Y "$(dirname "$gsrc")/score.txt" 2>/dev/null || echo 0)" -ge "$FARM_START" ] || continue
        gscore=$(seed_score "$gsrc")
        [ -n "$gscore" ] || continue
        if [ "$gscore" -eq 0 ] && [ "$own" -ne 0 ]; then
            echo "$(date '+%F %T') $func matched elsewhere (score 0), stopping $run"
            kill_run "$run"
            continue
        fi
        [ "$own" -le "$gscore" ] && continue                     # holds or ties the global best
        [ $(( own - gscore )) -ge $(( gscore * RESEED_PCT / 100 + RESEED_ABS )) ] || continue
        reseed_restart "$run" "$gsrc"
    done
}

for spec in "$@"; do
    IFS=: read -r func src w c _ <<< "$spec"
    w=${w:-$WORKERS}; c=${c:-$COPIES}
    asm=$(find "$REPO/asm/us/nonmatchings" -name "$func.s" | head -1)
    if [ -z "$asm" ]; then echo "no asm for $func, skipping"; continue; fi
    rm -rf "nonmatchings/$func" "$REPO/nonmatchings/$func"   # else import.py appends -1, -2, ...
    (cd "$REPO" && "$PY" tools/permuter/import.py "$src" "$asm") || { echo "import failed: $func"; continue; }
    # import.py writes into $REPO/nonmatchings/<func>; move it next to the farm.
    mkdir -p nonmatchings; mv "$REPO/nonmatchings/$func" "nonmatchings/$func"
    # (Stadium 1 needed a preprocess.sh arg-order fix here — GS's import.py already emits
    # INPUT before OUTPUT, verified 2026-10-18, see matching_notes/NOTES.md. Nothing to do.)
    rm -f "nonmatchings/$func/-I"
    # pycparser mangles `sizeof(T) * N` into `sizeof((T) (*N))`, which IDO rejects. Undo it.
    # (tools/permuter already carries permuter_sizeof_prec.patch; kept as a safety net.)
    sed -i -E 's/sizeof\(\(([A-Za-z_][A-Za-z0-9_ ]*)\) \(\*([0-9A-Fa-fx]+)\)\)/(\2 * sizeof(\1))/g' "nonmatchings/$func/base.c"
    seed=$( [ "$RESEED" != 0 ] && best_saved "$func" )
    if [ -n "$FOCUS_DIR" ] && [ -f "$FOCUS_DIR/$func.c" ]; then
        cp "nonmatchings/$func/base.c" "nonmatchings/$func/base.draft.c"
        cp "$FOCUS_DIR/$func.c" "nonmatchings/$func/base.c"
        echo "$func: focused start from $FOCUS_DIR/$func.c"
        seed=
    elif [ -n "$seed" ]; then
        cp "nonmatchings/$func/base.c" "nonmatchings/$func/base.draft.c"
        cp "$seed" "nonmatchings/$func/base.c"
        echo "$func: re-seeded from $seed"
    fi
    # Big initialized global arrays (e.g. migrated sample data) are re-parsed by IDO on every
    # candidate but only the function's code is scored: turn them into externs. 2.5x more
    # iterations on func_81209374 (290 KB -> 4 KB base.c), same base score. STRIP_DATA=0 disables.
    if [ "${STRIP_DATA:-1}" != 0 ]; then
        "$PY" - "nonmatchings/$func/base.c" <<'PYEOF'
import re, sys
p = sys.argv[1]; t = open(p).read(); out = []
for line in t.split("\n"):
    m = re.match(r"^((?:[A-Za-z_]\w*\s+)+\**\s*\w+\s*(?:\[[^\]]*\])+)\s*=\s*\{.*\};\s*$", line)
    out.append("extern " + m.group(1) + ";" if m and len(line) > 1000 and not line.startswith("static") else line)
open(p, "w").write("\n".join(out))
print(f"{p}: {len(t)} -> {len(chr(10).join(out))} bytes")
PYEOF
    fi
    sv=$([ -n "${seed:-}" ] && seed_score "$seed")
    for k in $(seq 1 "$c"); do
        run=$func; [ "$k" -gt 1 ] && run=${func}__c$k
        [ -n "$RUN_TAG" ] && run=${func}__${RUN_TAG}$k
        [ "$run" != "$func" ] && { rm -rf "nonmatchings/$run"; cp -r "nonmatchings/$func" "nonmatchings/$run"; }
        # Diversity seeding (DIVERSITY=0 disables): copies past the first start from the
        # k-th best DISTINCT saved candidate instead of the global best, so copies hunt
        # different basins instead of converging on one (mid-run re-seed still pulls a
        # copy over once it trails by RESEED_PCT/RESEED_ABS). Copy 1 keeps the best seed.
        if [ "$RESEED" != 0 ] && [ "${DIVERSITY:-1}" != 0 ] && [ ! -f "$FOCUS_DIR/$func.c" ] && [ "$k" -gt 1 ]; then
            myseed=$(best_kth "$func" "$k")
            [ -z "$myseed" ] && myseed=$seed
            if [ -n "$myseed" ] && [ "$myseed" != "$seed" ]; then
                cp "$myseed" "nonmatchings/$run/base.c"
                seedv[$run]=$(seed_score "$myseed")
                echo "  $run: diversity seed $(seed_score "$myseed")"
            fi
        fi
        if [ -n "${seedv[$run]:-}" ]; then :; elif [ -n "$sv" ]; then seedv[$run]=$sv; fi
        echo "starting $run with $w workers"
        start_run "$run" "$w"
    done
    # tagged runs are copies; drop the untagged template so it never syncs over another job's <func>/
    [ -n "$RUN_TAG" ] && rm -rf "nonmatchings/$func"
done
[ ${#sub[@]} -eq 0 ] && { echo "nothing started"; exit 1; }

sync_best() {
    for d in nonmatchings/*/; do
        f=$(basename "$d")
        mkdir -p "$SAVE_DIR/$f"
        rsync -a --include='output-*/***' --include='base.c' --include='base.draft.c' --exclude='*' \
            "$d" "$SAVE_DIR/$f/" 2>/dev/null
        cp -f "nonmatchings/$f.log" "$SAVE_DIR/$f/" 2>/dev/null
    done
    touch "$SAVE_DIR"
}
any_alive() { local p; for p in "${sub[@]}"; do kill -0 "$p" 2>/dev/null && return 0; done; return 1; }
# Preemption / scancel / time limit: Slurm sends TERM (KillWait 30 s before KILL). Sync what we have.
on_term() {
    echo "$(date '+%F %T') TERM received, final sync"
    local p r
    for r in "${!sub[@]}"; do pkill -TERM -f "nonmatchings/$r " 2>/dev/null; done
    for p in "${sub[@]}"; do kill "$p" 2>/dev/null; done
    sleep 2
    for r in "${!sub[@]}"; do pkill -KILL -f "nonmatchings/$r " 2>/dev/null; done
    sync_best; exit 143
}
trap on_term TERM INT HUP
while any_alive; do sleep "$SYNC_SECS" & wait $!; any_alive || break; sync_best; reseed_check; done
sync_best
echo "farm done; best candidates in $SAVE_DIR"
bash "$HERE/farm_status.sh" "$SAVE_DIR"
