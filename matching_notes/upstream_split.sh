#!/usr/bin/env bash
#
# upstream_split.sh -- split farm-port changes into per-group branches off
# origin/master for upstreaming (one PR per fragment / main-segment file).
#
# Usage:
#   matching_notes/upstream_split.sh <group> [--dry-run]
#
#   <group> is one of:
#     frag<N>     all our final-state changes under src/fragments/<N>/
#     <name>      one main-segment file src/<name>.c (e.g. 585D0, dp_intro)
#     C380-jpeg   src/C380.c plus its Makefile CC_OLD rule (owner group C380)
#     renames     catch-all: linker_scripts/us/symbol_addrs_code.txt rename
#                 lines whose symbol is NOT solely owned by a single src
#                 group (referenced by 0 or >=2 groups' files)
#
# A group's branch up/<group> starts at origin/master and contains exactly:
#   1. the final-state diff BASE..SRC_REF of the group's src files
#      (`git diff BASE..SRC_REF -- <pathspec> | git apply --3way`), and
#   2. the symbol_addrs_code.txt renames for symbols referenced only by
#      that group's files (via upstream_filter_addrs.py); multi-group
#      symbols are left for the "renames" group so the table changes
#      partition cleanly across PRs.
#
# --dry-run applies everything to a throwaway detached worktree, reports
# CLEAN or CONFLICT (with conflicted files / failed hunks), and creates no
# branch.  Without it, a clean apply is committed on up/<group>; a
# conflicting apply leaves the worktree in place for manual resolution.
#
# Env overrides:
#   BASE      fork point          (default 0ed2fd9f, michiiik master)
#   SRC_REF   our branch          (default farm-port)
#   UP_REMOTE upstream remote     (default origin)
#   UP_PREFIX branch prefix       (default up/)
#
# Read-only w.r.t. remotes: this script never fetches or pushes.
#
set -euo pipefail

BASE="${BASE:-0ed2fd9f}"
SRC_REF="${SRC_REF:-farm-port}"
REMOTE="${UP_REMOTE:-origin}"
PREFIX="${UP_PREFIX:-up/}"
ADDRS="linker_scripts/us/symbol_addrs_code.txt"
NOTES_DIR="$(cd "$(dirname "$0")" && pwd)"
FILTER="$NOTES_DIR/upstream_filter_addrs.py"

group="${1:-}"
mode="${2:-}"
if [ -z "$group" ] || { [ -n "$mode" ] && [ "$mode" != "--dry-run" ]; }; then
    sed -n '2,31p' "$0" | sed 's/^#\{1,\} \{0,1\}//'
    exit 2
fi

# --- resolve group -> pathspec --------------------------------------------
# pathspec may list several files; leave it UNQUOTED at use sites so it
# word-splits into multiple pathspecs.
pathspec=""
owner=""    # ownership group when it differs from the branch name
case "$group" in
    C380-jpeg) pathspec="src/C380.c Makefile"; owner="C380" ;;
esac
if [ "$group" != "renames" ] && [ -z "$pathspec" ]; then
    if git cat-file -e "$SRC_REF:src/${group}.c" 2>/dev/null; then
        pathspec="src/${group}.c"
    elif [ -n "$(git ls-tree --name-only "$SRC_REF" "src/fragments/${group}" 2>/dev/null)" ]; then
        pathspec="src/fragments/${group}"
        group="frag${group}"
    else
        echo "error: unknown group '$group' (no src/$group.c, no src/fragments/$group/)" >&2
        exit 2
    fi
fi

for rev in "$BASE" "$SRC_REF" "$REMOTE/master"; do
    git rev-parse --verify -q "$rev^{commit}" >/dev/null \
        || { echo "error: revision '$rev' not found (fetch first?)" >&2; exit 2; }
done
echo "group:       $group"
echo "pathspec:    ${pathspec:-<none -- symbol_addrs renames only>}"

# --- map every touched src file to its group name --------------------------
file2group() {
    case "$1" in
        src/fragments/*/*) echo "frag$(printf '%s' "$1" | cut -d/ -f3)" ;;
        src/*.c)           printf '%s\n' "$1" | sed 's|^src/||; s|\.c$||' ;;
    esac
}
ALL_GROUPS="$(git diff --name-only "$BASE..$SRC_REF" -- src/ \
             | while read -r f; do file2group "$f"; done | sort -u)"

# --- rename pairs (old -> new) from the symbol table diff ------------------
declare -A NEW2OLD=()
while read -r old new; do
    NEW2OLD["$new"]="$old"
done < <(git diff "$BASE..$SRC_REF" -- "$ADDRS" \
         | grep -E '^[-+][A-Za-z_]' \
         | sed -n 's/^-/O /p; s/^+/N /p' \
         | awk '{ sym = $2; sub(/=.*/, "", sym); if ($1 == "O") o = sym; else print o, sym }')

# --- per-symbol ownership: groups whose files reference the new name -------
declare -A OWNERS=()
for new in "${!NEW2OLD[@]}"; do
    OWNERS["$new"]="$(git grep -l -w "$new" "$SRC_REF" -- src/ 2>/dev/null \
                       | sed "s|^$SRC_REF:||" \
                       | while read -r f; do file2group "$f"; done | sort -u | tr '\n' ' ')"
done

# --- symbols owned by THIS group --------------------------------------------
symfile="$(mktemp /tmp/opencode/up_syms.XXXXXX)"
owned_new=""
owned_old=""
for new in "${!NEW2OLD[@]}"; do
    read -ra os <<< "${OWNERS[$new]}"
    take=false
    if [ "$group" = "renames" ]; then
        # catch-all: not (exactly one owner which is a known split group)
        if [ "${#os[@]}" -ne 1 ] || ! printf '%s\n' "$ALL_GROUPS" | grep -qx "${os[0]}"; then
            take=true
        fi
    elif [ "${#os[@]}" -eq 1 ] && [ "${os[0]}" = "${owner:-$group}" ]; then
        take=true
    fi
    if $take; then
        owned_new="$owned_new $new"
        owned_old="$owned_old ${NEW2OLD[$new]}"
    fi
done
if [ -n "${owned_new// /}" ]; then
    printf '%s\n' $owned_new $owned_old >"$symfile"
    echo "owned renames (new): ${owned_new# }"
else
    echo "owned renames (new): (none)"
fi

# --- throwaway worktree off origin/master -----------------------------------
WT="$(mktemp -d /tmp/opencode/up_split.XXXXXX)"
rmdir "$WT"
if [ "$mode" = "--dry-run" ]; then
    git worktree add --detach --quiet "$WT" "$REMOTE/master"
else
    git worktree add --quiet -b "${PREFIX}${group}" "$WT" "$REMOTE/master"
fi
trap 'rm -f "$symfile"; git worktree remove --force "$WT" >/dev/null 2>&1 || true' EXIT

status=CLEAN
faillog="$(mktemp /tmp/opencode/up_apply.XXXXXX)"

# --- 1) group's src files: final-state diff, three-way apply ----------------
if [ -n "$pathspec" ]; then
    echo "src diff:    $(git diff --name-only "$BASE..$SRC_REF" -- $pathspec | wc -l) file(s) vs $BASE"
    if ! git diff "$BASE..$SRC_REF" -- $pathspec \
         | git -C "$WT" apply --3way --whitespace=nowarn - >"$faillog" 2>&1; then
        status=CONFLICT
    fi
fi

# --- 2) owned symbol_addrs renames: filtered diff, three-way apply -----------
if [ -n "${owned_new// /}" ]; then
    if ! python3 "$FILTER" --base "$BASE" --ref "$SRC_REF" --symbols-file "$symfile" \
         | git -C "$WT" apply --3way --whitespace=nowarn - >>"$faillog" 2>&1; then
        status=CONFLICT
    fi
fi

# --- report -------------------------------------------------------------------
if [ "$status" = CLEAN ]; then
    echo "result:      CLEAN"
else
    echo "result:      CONFLICT"
    echo "--- apply diagnostics (failed hunks) ---"
    grep -E '^(error|warning):' "$faillog" | sort -u | head -10 || true
fi
unmerged="$(git -C "$WT" status --porcelain 2>/dev/null | awk '$1 ~ /U/ {print $2}')"
if [ -n "$unmerged" ]; then
    echo "--- unmerged files (three-way conflicts) ---"
    printf '%s\n' "$unmerged"
    echo "--- conflict markers ---"
    while read -r f; do
        grep -n '^<<<<<<<' "$WT/$f" | head -3 | sed "s|^|$f:|"
    done <<<"$unmerged"
fi

if [ "$mode" = "--dry-run" ]; then
    echo "dry-run:     worktree discarded, no branch created"
    [ "$status" = CLEAN ] && exit 0 || exit 1
fi
if [ "$status" = CLEAN ]; then
    git -C "$WT" add -A
    git -C "$WT" commit --quiet -m \
"upstream split: $group (farm-port final-state changes)

Pathspec: ${pathspec:-<renames only>}
Owned renames: ${owned_new:-none}
Squashed from $BASE..$SRC_REF, applied onto $REMOTE/master."
    echo "committed:   ${PREFIX}${group} (off $REMOTE/master)"
    exit 0
fi
trap - EXIT
rm -f "$symfile"
echo "worktree:    $WT (kept for manual resolution)"
echo "next:        git -C $WT add -A && git -C $WT commit"
exit 1
