# pokestadiumgs session handoff — start here

Paste-ready prompt for the next session. Repo: /home/tsranso/Code/pokestadiumgs,
branch farm-port. Last verified state: 107 functions matched (64.8%, 3,704 owners
left), 21 evidenced renames, ROM byte-identical at every gate, tree extract-stable.

---

Continue the Pokemon Stadium 2 decompilation campaign at /home/tsranso/Code/pokestadiumgs
(branch farm-port, HEAD 28da95c8 or later; ROM builds byte-identical, tree is extract-stable).
107 functions matched so far (64.8%, 3,704 owners left), 21 evidenced renames applied.
Work autonomously in the established pattern; ask me only for pushes/PRs.

READ FIRST (in this order):
1. matching_notes/NOTES.md — wave log, dead ends, integration protocol, fleet rules
2. matching_notes/IDO_TRICKS.md — compiler lessons (the "Wave-1 lessons" section especially)
3. matching_notes/ROUND_SETUP.md — the matcher-agent protocol (spool format, shared-tree rules)
4. matching_notes/SWEEP_2026-10-19.tsv — the master work queue: all 3,716 remaining
   functions, m2c-drafted and scored (A_adopt 59 / B_farm 338 / C_agent 783 / D_structural 2,536)

THE QUEUE, IN ORDER:
1. A_adopt: gate the 59 score-0 drafts (drafts + .meta in matching_notes/sweep_zero/).
   Splice ~15 at a time via matching_notes/splice_manual.py, full make must print
   "build/pokestadiumgs-us.z64: OK", bisect failures with matching_notes/revert_splice.py.
   SCORE-0 IS NOT PROOF (jtbl entry-count traps: func_80047104, func_82800628 are the
   cautionary tales in NOTES.md).
2. B_farm: launch the permuter farm on the sub-100 scores (a dozen sit at <=8). Pattern:
   farm-seeds-N branch off current farm-port with drafts spliced (rename-normalize with
   matching_notes/rename_map.sed, dedup colliding typedefs), then
   sbatch --export=ALL,SEED_BRANCH=farm-seeds-N,TIME_LIMIT=08:00:00,FUNCS_OVERRIDE="func:src:4:2 ..."
   matching_notes/palmetto_job.sh ; monitor with matching_notes/farm_status.sh ;
   adopt zeros with matching_notes/adopt_candidate.py (full-make gated).
3. Wave 6: matcher agents on the C_agent tier (cross-ref matching_notes/CROSSPORT_2026-10-19.txt
   — ~80 S1 cross-port twins >=0.9 remain unworked; S1 repo is READ-ONLY at
   /home/tsranso/Code/pokestadium). Agent waves: 4-6 parallel subagents, disjoint files,
   spool protocol per ROUND_SETUP.md; integrate with fixups + rm -r build/src + full make.
4. Renames: batch per wave when evidence is concrete (US symbol table only; word-boundary
   rewrites incl. cross-file callers; make extract + full make + map cross-check;
   update matching_notes/rename_map.sed with the new pairs).
5. Upstream: branches up/renames up/frag79 up/585D0 up/C380-jpeg up/frag67 up/frag11
   exist off michiiik's master (creation clean, NOT yet gated). Before opening PRs:
   git fetch origin, re-split if master moved, gate each branch with a local full make
   in a worktree. PR order: up/renames first. Do not push without my go-ahead.

HARD RULES (all learned the hard way):
- Invoke python ONLY via .venv/bin/python3 (system python3 is 3.6 and breaks tools).
- The full make printing "build/pokestadiumgs-us.z64: OK" is the ONLY match proof;
  fd.sh CURRENT (0) can lie (relocations, jtbl extents).
- Fleet rule: no agent builds while the integrator runs make extract or a full make.
- Farm seed branches MUST be re-cut after every rename wave (stale tracked src vs
  regenerated asm/ = undefined-symbol failures). Seed trees gate with COMPARE=0.
- After every integration: rm -r build/src before the full make (NFS stale objects);
  re-run matching_notes/corpus.py build after waves.
- rm -rf and heredocs are permission-blocked; use rm -r and the write/edit tools.
- The permuter's own score is unreliable — judge candidates with fd.sh, adopt only
  through the ROM gate.

Suggested first command:
cd /home/tsranso/Code/pokestadiumgs && git log --oneline -3 && git status --short
&& grep -c A_adopt matching_notes/SWEEP_2026-10-19.tsv && env PATH="$PWD/.venv/bin:$HOME/local/bin:/usr/local/bin:/usr/bin:/bin" make -j32 PYTHON="$PWD/.venv/bin/python3" 2>&1 | tail -2

Then start on queue item 1. Overnight autonomy is fine: waves + farm + gates + commits,
matching the rhythm of the last two sessions (every commit ROM-gated, NOTES.md updated
per wave, no pushes without me).

---

## Extra context (not part of the paste)

- If the first command's build fails, something drifted — check `git status` for stray
  splices before anything else.
- If `tsranso/pokestadiumgs` exists on the gitea by then, add an instruction to
  `git push gitea farm-port` after the first green gate (remote is already configured;
  the backup still doesn't exist off-machine).
- Scratch assets that persist in /tmp/opencode (shared mount, survives restarts):
  the sweep copy `/tmp/opencode/sweep` (isolated, fully built — reusable for isolated
  verification builds), `sweep_scratch/full2/results.jsonl` (raw sweep results),
  `w5b_verify` (wave-5 part-2 verification tree). All regenerable; none are load-bearing.
- Key tool map (all in matching_notes/): fd.sh, var.py, m2ctx.py, mkdraft.py,
  try_candidate.py, adopt_candidate.py, ccs.py, corpus.py, symcheck.py, splice_manual.py,
  revert_splice.py, rename_map.sed, sweep.py, crossport_join.py, upstream_split.sh,
  upstream_filter_addrs.py, permuter_farm.sh, palmetto_job.sh, farm_status.sh,
  farm_logfilter.py, farm_splice.py.
- Parked items with full recipes in matching_notes/spool/*.meta: the spline trio
  (func_8290E040/E0FC/E1D8), func_84164C28 + func_84168CA4 (joint fragment79 datamig),
  func_82202628 (fragment17 yaml migration), func_8002781C (score-5 clue documented),
  func_80047158 (farm import failure, uninspected).
- Coverage history: 63.8% -> 64.8% across five waves (25+31+12+7+3+18+7+2 = 105 matches
  via waves/farm, plus 2 yaml-pair; per-commit counts in `git log`).
