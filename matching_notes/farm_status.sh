#!/bin/bash
# Summarise permuter farm progress from the synced save dir (works from any node).
# usage: matching_notes/farm_status.sh [save_dir]   (default /scratch/$USER/permuter_best_gs)
SAVE_DIR=${1:-/scratch/$USER/permuter_best_gs}
shopt -s nullglob
printf "%-16s %6s %6s %5s  %-19s  %s\n" FUNC BASE BEST CANDS LAST_IMPROVEMENT LATEST_STATUS
for d in "$SAVE_DIR"/*/; do
    f=$(basename "$d"); log="$d/$f.log"
    base=$( [ -f "$log" ] && grep -m1 -o "base score = [0-9]*" "$log" | grep -o "[0-9]*$" )
    best=; n=0
    for s in "$d"/output-*/score.txt; do
        v=$(cat "$s"); n=$((n+1))
        [ -z "$best" ] || [ "$v" -lt "$best" ] && best=$v
    done
    last=$( [ -f "$log" ] && grep -E "found new best|tied best|found a better" "$log" | tail -1 | cut -c1-19 )
    status=$( [ -f "$log" ] && grep " STATUS " "$log" | tail -1 | sed 's/.*STATUS //' )
    printf "%-16s %6s %6s %5d  %-19s  %s\n" "$f" "${base:--}" "${best:--}" "$n" "${last:--}" "${status:--}"
done
echo
echo "Synced at: $(stat -c %y "$SAVE_DIR" 2>/dev/null | cut -c1-19)   (farm syncs every \$SYNC_SECS, default 120)"
squeue -u "$USER" -h -o "job %i %j %T %M on %N" 2>/dev/null
