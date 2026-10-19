# pokestadiumgs session handoff — start here

Paste-ready prompt for the next session. Repo: /home/tsranso/Code/pokestadiumgs,
branch farm-port. Last verified state: 177 functions matched this campaign
(65.5% function coverage, 3,634 owners left; progress.py code baseline 32.1819%),
31 evidenced renames total, ROM byte-identical at every gate, tree extract-stable.

---

Continue the Pokemon Stadium 2 decompilation campaign at /home/tsranso/Code/pokestadiumgs
(branch farm-port, HEAD c7bc586f or later; ROM builds byte-identical, tree is extract-stable).
199 campaign matches so far (65.7%, 3,612 owners left), 31 evidenced renames applied.
Work autonomously in the established pattern; ask me only for pushes/PRs.

READ FIRST (in this order):
1. matching_notes/NOTES.md — wave log, dead ends, integration protocol, fleet rules
   (read the newest entries first: sweep A_adopt, farm seeds 5/6, wave 6, the
   stale-.s cleanup, and the farm staging-failure postmortem)
2. matching_notes/IDO_TRICKS.md — compiler lessons
3. matching_notes/ROUND_SETUP.md — the matcher-agent protocol (spool format, shared-tree rules)
4. matching_notes/SWEEP_2026-10-19.tsv — the master work queue: 3,645 remaining
   functions minus the 70 already adopted since the sweep
   (A_adopt 59 + wave-6 cross-ports 10 + 8AF1BAE8), m2c-drafted and scored
   (B_farm ~324 / C_agent ~773 / D_structural 2,536 remain)

SESSION STATE (2026-10-19 ~12:30):
- A_adopt tier: DONE (59 matches, commits 559ee32c/6606a640/eac0d6c6/2b0d3a7a).
- Wave 6: DONE (10 cross-port matches, fc0216e2 + rename batch 82557a8c).
  All >=1.000 crossport twins are now consumed; the >=0.9 leftovers are parked
  or sub-threshold (see matching_notes/CROSSPORT_2026-10-19.txt).
- Farm job 17663884 (SEED_BRANCH=farm-seeds-6, 13 funcs x 3 workers x 2 copies,
  8h) QUEUED on work1 as of ~12:20; job 17663103 (seeds-5) died in its staged
  gate — see NOTES.md for the postmortem before touching the tree while a farm
  job is pending. Adopt zeros with matching_notes/adopt_candidate.py
  (full-make gated; it also deletes the adopted function's nonmatchings .s).
- Parked items with full recipes in matching_notes/spool/*.meta: the spline trio
  (func_8290E040/E0FC/E1D8), func_84164C28 + func_84168CA4 (joint fragment79
  datamig; func_84168C18's D_8418C920 extern resolves against that blob —
  migrate them together), func_82202628 (fragment17 yaml migration),
  func_8002781C (score-5 clue), func_80047158 (farm import failure, uninspected).

THE QUEUE, IN ORDER:
1. B_farm adoption: when job 17663884's farm_status.sh shows BEST 0 entries,
   adopt via matching_notes/adopt_candidate.py (full-make gated). Then re-cut
   seeds (farm-seeds-N+1 off CURRENT farm-port, cherry-pick the seed commit,
   verify staged build with COMPARE=0) and farm the next B_farm tranche
   (scores 10-30 next).
2. Wave 7: matcher agents on the C_agent tier. The crossport twin pool is
  drained; work C_agent by sweep score (ascending) or by cluster (the sweep
  TSV's file column clusters families). 4-6 parallel subagents, disjoint files,
  spool protocol per ROUND_SETUP.md; integrate with fixups + rm -r build/src +
  full make. Prompt template: the wave-6 prompts in this session's history
  worked well (S1-twin-C retarget path avoids the mkdraft ctx.c race).
3. Renames: batch per wave when evidence is concrete (US symbol table only;
   word-boundary rewrites incl. cross-file callers; make extract + full make +
   map cross-check; update matching_notes/rename_map.sed with the new pairs).
   31 pairs live in rename_map.sed.
4. Upstream: branches up/renames up/frag79 up/585D0 up/C380-jpeg up/frag67
   up/frag11 exist off michiiik's master (creation clean, NOT yet gated). The
   wave-6 matches and renames since then are NOT on them. Before opening PRs:
   git fetch origin, re-split if master moved, gate each branch with a local
   full make in a worktree. PR order: up/renames first. Do not push without
   my go-ahead.

HARD RULES (all learned the hard way):
- Invoke python ONLY via .venv/bin/python3 (system python3 is 3.6 and breaks tools).
- The full make printing "build/pokestadiumgs-us.z64: OK" is the ONLY match proof;
  fd.sh CURRENT (0) can lie (relocations, jtbl extents).
- Fleet rule: no agent builds while the integrator runs make extract or a full make.
- EXTENDED FLEET RULE: a pending farm job stages the live tree in its first
  minute; do not leave the tree mid-mutation (mid-extract, half-spliced) while
  a farm job is queued or starting, and re-cut seed branches after EVERY wave
  of matches/renames (git-archive staging overlays the whole tracked tree).
- Farm seed branches MUST be re-cut after every rename wave. Seed trees gate
  with COMPARE=0; pass --time to sbatch explicitly (the in-job scontrol trim
  is best-effort and has failed).
- After every integration: rm -r build/src before the full make (NFS stale objects);
  re-run matching_notes/corpus.py build after waves.
- rm -rf and heredocs are permission-blocked; use rm -r and the write/edit tools.
- The permuter's own score is unreliable — judge candidates with fd.sh, adopt only
  through the ROM gate.
- Splice-based adoptions leave stale .s files under asm/us/nonmatchings that make
  progress.py undercount: delete the adopted function's .s (adopt_candidate.py
  already does; manual splices do not). make extract regenerates nonmatchings
  per remaining pragma, so deleted .s for C-owned functions stay deleted.

Suggested first command:
cd /home/tsranso/Code/pokestadiumgs && git log --oneline -3 && git status --short
&& matching_notes/farm_status.sh | tail -20
&& env PATH="$PWD/.venv/bin:$HOME/local/bin:/usr/local/bin:/usr/bin:/bin" make -j32 PYTHON="$PWD/.venv/bin/python3" 2>&1 | tail -2

Then start on queue item 1 (B_farm adoption if zeros exist, else Wave 7 prep).
Overnight autonomy is fine: waves + farm + gates + commits, matching the rhythm
of the last sessions (every commit ROM-gated, NOTES.md updated per wave, no
pushes without me).

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
  `/tmp/opencode/farm5_stage` (the farm-seeds-6 staged-build verification tree —
  reusable as a template for future staged-build checks). All regenerable.
- Key tool map (all in matching_notes/): fd.sh, var.py, m2ctx.py, mkdraft.py,
  try_candidate.py, adopt_candidate.py, ccs.py, corpus.py, symcheck.py, splice_manual.py,
  revert_splice.py, rename_map.sed, sweep.py, crossport_join.py, upstream_split.sh,
  upstream_filter_addrs.py, permuter_farm.sh, palmetto_job.sh, farm_status.sh,
  farm_logfilter.py, farm_splice.py.
- Coverage history: 63.8% -> 65.5% this campaign (59 sweep A_adopt + 1 farm-seeds
  spinoff + 10 wave-6 cross-ports = 70 today; per-commit counts in `git log`).
- mkdraft-generated seeds need prologue surgery the sweep's splice machinery does
  automatically: see the farm seeds 5/6 notes in NOTES.md for the full fixup list
  before farming any freshly-drafted function.
