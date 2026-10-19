#!/bin/bash
#SBATCH --job-name=pokestadiumgs-farm
#SBATCH --partition=work1
#SBATCH --account=cuuser_cpsc_ads_s27
#SBATCH --constraint="cpu_gen_genoa|cpu_gen_sapphirerapids"
#SBATCH --nodes=1 --ntasks=1 --cpus-per-task=96 --mem=128G
#SBATCH --time=3-00:00:00
#SBATCH --requeue
#SBATCH --open-mode=append
#SBATCH --signal=B:TERM@120
#SBATCH --output=/scratch/%u/pokestadiumgs_%j.out
#
# Unattended Palmetto job: stage the repo to node-local SSD, verify the build, run the
# permuter farm, and leave a ready tree for Claude Code agents. Edit FUNCS below before
# submitting (func:src[:workers[:copies]] specs), or pass FUNCS_OVERRIDE. For a supervised
# session use `salloc` with the same resources and run the steps by hand.
#
# GS has NO committed drafts (unlike Stadium 1): import.py reads each farmed function from
# the C spliced into its src/ file in the staged tree, so a farm run needs seeds. Either
# put the spliced seeds on a branch and submit with SEED_BRANCH=<branch>, or splice them
# into the working tree of $SRC_REPO and submit with SEED_BRANCH unset (default HEAD).
#
# Env vars (all optional; all propagate to chained phases via --export=ALL):
#   SEED_BRANCH=<tree-ish>  default HEAD stages the working tree as-is (committed +
#                           uncommitted + gitignored inputs, like Stadium 1). Any branch,
#                           tag or commit stages that tree instead, with the gitignored
#                           build inputs (baseroms/, .venv/, asm/, assets/, expected/,
#                           .splat/, tools/permuter|asm-differ|mips_to_c, ...) overlaid
#                           from $SRC_REPO. build/ is never copied in this mode: a fresh
#                           tree forces the full rebuild the gate is there to check.
#   TIME_LIMIT=<time>       effective time limit for this job and every chained phase
#                           (default 1-00:00:00). The header asks for the 3-day partition
#                           max; TIME_LIMIT trims it down (applied best-effort to the
#                           running job via scontrol — #SBATCH cannot read env vars).
#   FUNCS_OVERRIDE="..."    replaces the FUNCS list below.
#   FARM_HOURS=h            farm duration; default is the job's time limit minus 30 min.
#   FARM_PHASES=N           resubmit this job N-1 more times (same resources).
#   RUN_TAG=x                parallel farms sharing permuter_best_gs want distinct tags.
#   SRC_REPO=/path           source checkout (default $HOME/Code/pokestadiumgs).
#
# QoS normal is preemptable (PreemptType=preempt/qos, mode REQUEUE): on preemption Slurm
# requeues the job, which re-stages and re-seeds from /scratch/$USER/permuter_best_gs.
# Logs append across restarts. Phased runs (no 3-day job needed): the saved candidates
# are the checkpoint and every start re-seeds from them, so chain short jobs:
#   sbatch --time=06:00:00 --export=ALL,TIME_LIMIT=06:00:00,FARM_PHASES=4 matching_notes/palmetto_job.sh
# Stop the chain early with `scancel` (the queued successor is submitted only at the end
# of each phase).
set -eu
SRC_REPO=${SRC_REPO:-$HOME/Code/pokestadiumgs}
SEED_BRANCH=${SEED_BRANCH:-HEAD}
TIME_LIMIT=${TIME_LIMIT:-1-00:00:00}
# Stage on the node-local SSD ($TMPDIR = /local_scratch). The job-id suffix keeps
# concurrent farms on the same node out of each other's stage; drop it for manual runs.
STAGE=${TMPDIR:-/tmp}/pokestadiumgs${SLURM_JOB_ID:+-$SLURM_JOB_ID}
export PATH="$HOME/local/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"

echo "node: $(hostname)  cpus: $SLURM_CPUS_PER_TASK  start: $(date)"
# Apply TIME_LIMIT to the running job (lowering a limit is always allowed; if this fails
# the job keeps the limit sbatch assigned it, which the log shows as $LIMIT below).
scontrol update JobId="$SLURM_JOB_ID" TimeLimit="$TIME_LIMIT" 2>/dev/null \
    || echo "note: could not set TimeLimit=$TIME_LIMIT, keeping the sbatch-assigned limit"
mkdir -p "$(dirname "$STAGE")"
# Stage: everything the build needs, including gitignored inputs (venv, asm, permuter, roms).
if [ "$SEED_BRANCH" = "HEAD" ]; then
    rsync -a --delete --exclude '/nonmatchings/' --exclude '.claude/worktrees/' "$SRC_REPO/" "$STAGE/"
else
    # Live working tree wholesale (venv, asm, expected/, tool clones, ROMs all ride along),
    # then the committed tree of $SEED_BRANCH extracted OVER it, so tracked files become
    # the branch's versions while the gitignored build inputs stay. build/ is excluded so
    # the gate force-rebuilds and cannot false-pass on the live tree's ROM. (The previous
    # git ls-files --ignored overlay silently dropped .venv/ — the node then ran
    # tools/coalesce_cc.py under system python 3.6 and the gate died; do not go back.)
    rm -rf "$STAGE"; mkdir -p "$STAGE"
    rsync -a --exclude '/.git/' --exclude '/build/' --exclude '/nonmatchings/' \
        --exclude '.claude/worktrees/' "$SRC_REPO/" "$STAGE/"
    GITARCHIVE=$(mktemp)
    git -C "$SRC_REPO" archive --format=tar "$SEED_BRANCH" > "$GITARCHIVE" \
        || { echo "SEED_BRANCH '$SEED_BRANCH' not found in $SRC_REPO"; exit 1; }
    tar -x -C "$STAGE" -f "$GITARCHIVE"; rm -f "$GITARCHIVE"
fi
cd "$STAGE"
find build -exec touch {} + 2>/dev/null || true

# Gate: the staged tree must build byte-identical before anyone works on it.
env PATH="$STAGE/.venv/bin:$PATH" make -j"$SLURM_CPUS_PER_TASK" PYTHON="$STAGE/.venv/bin/python3" 2>&1 | tail -3
grep -q "build/pokestadiumgs-us.z64: OK" <(env PATH="$STAGE/.venv/bin:$PATH" make PYTHON="$STAGE/.venv/bin/python3" 2>&1 | tail -1) || { echo "BUILD NOT OK"; exit 1; }

# Permuter farm. Spec is func:src[:workers[:copies]]: the permuter's main process caps each
# function at ~80 it/s regardless of workers, so scale by adding copies (independent
# permuters), not workers — small/fast functions want many copies x 2-3 workers,
# slow-compiling giants want few copies x 5-6 workers. Fields left off default to the
# WORKERS computed below and $COPIES. Each function's seed C must be spliced into its src
# file in the staged tree (SEED_BRANCH). Several jobs may farm the same or different lists
# sharing permuter_best_gs: give each a distinct RUN_TAG, e.g.
#   sbatch --job-name=gs-farm-a --export=ALL,RUN_TAG=ga,FUNCS_OVERRIDE="..." matching_notes/palmetto_job.sh
# Mid-run re-seed (permuter_farm.sh) merges their best candidates automatically.
FUNCS=(
  # Examples of the format (open functions from matching_notes/NOTES.md; only farm
  # functions whose seed C is actually spliced into the staged src/ tree):
  # func_8000B28C:src/AC80.c:3:2
  # func_800649D4:src/654A0.c:3:2
)
# FUNCS_OVERRIDE="func_X:src/a.c:3:8 func_Y:src/b.c" replaces the list (e.g. a side job).
[ -n "${FUNCS_OVERRIDE:-}" ] && read -r -a FUNCS <<< "$FUNCS_OVERRIDE"
if [ ${#FUNCS[@]} -eq 0 ]; then
  echo "no FUNCS: put func:src[:W[:C]] specs in FUNCS in this script or pass FUNCS_OVERRIDE"
  exit 1
fi
# Default workers for FUNCS entries without an explicit :W (see the FUNCS comment above).
WORKERS=$(( SLURM_CPUS_PER_TASK / (${#FUNCS[@]} * ${COPIES:-1}) ))
# Farm duration: explicit FARM_HOURS, else the job's time limit minus 30 min (staging + final sync).
LIMIT=$(squeue -h -j "$SLURM_JOB_ID" -o %l)          # D-HH:MM:SS or HH:MM:SS
if [ -z "${FARM_HOURS:-}" ]; then
  FARM_HOURS=$("$STAGE/.venv/bin/python3" -c "
import sys; t=sys.argv[1]; d=0
if '-' in t: d,t=t.split('-'); d=int(d)
h,m,s=(list(map(int,t.split(':')))+[0,0])[:3]
print(max(0.5, round(d*24+h+m/60-0.5,2)))" "$LIMIT")
fi
echo "farm hours: $FARM_HOURS (job limit $LIMIT, TIME_LIMIT $TIME_LIMIT), phases left: ${FARM_PHASES:-1}"
SAVE_DIR=/scratch/$USER/permuter_best_gs bash "$STAGE/matching_notes/permuter_farm.sh" "$STAGE" "$WORKERS" "$FARM_HOURS" "${FUNCS[@]}"
# Chain the next phase (same script, same #SBATCH resources, TIME_LIMIT as the time limit).
if [ "${FARM_PHASES:-1}" -gt 1 ]; then
  next=$(sbatch --time="$TIME_LIMIT" --export=ALL,FARM_PHASES=$((FARM_PHASES-1)),FARM_HOURS="$FARM_HOURS" "$SRC_REPO/matching_notes/palmetto_job.sh" | tail -1)
  echo "next phase: $next"
fi
echo "done: $(date)"
