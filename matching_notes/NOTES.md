# pokestadiumgs farm-tooling port state

Ported from the Stadium 1 tree (`~/Code/pokestadium/matching_notes/`) on 2026-10-18.
All paths below are relative to this repo. Invoke python tools via `.venv/bin/python3`
(the system python3 is 3.6 and cannot run them).

## What is here

- `matching_notes/fd.sh` — build one object + full-uncapped diff of one function
  (calls `tools/asm-differ/diff.py`, cloned from the Stadium 1 checkout; the vendored
  repo-root `diff.py` does `import imp` and is dead on python 3.12, same as Stadium 1).
  Drafting convention: temporarily replace the function's `#pragma GLOBAL_ASM` line with
  candidate C, then `git restore` the file. Never commit a draft.
- `matching_notes/var.py` — batch text-replacement variants of one spliced function,
  full-score policy. Spec format: variants separated by `=====`, edits by `-----`,
  each edit is `<old>\n@@@\n<new>`.
- `matching_notes/m2ctx.py` — m2c context file generator (GS include set: IINC +
  lib/ultralib + GBI defines; VERSION_US=1).
- `permuter_settings.toml` — decomp-permuter project settings (ido, macro
  preservation, coalesce_cc.py mapped to ido7.1 for decomp.me).
- Untracked tool clones (in `.git/info/exclude`): `tools/permuter` (decomp-permuter
  059609d + permuter_sizeof_prec.patch applied), `tools/asm-differ`,
  `tools/mips_to_c`.

## Verified working (2026-10-18)

- Full build: `make -j32` -> `build/pokestadiumgs-us.z64: OK`; `make diff-init` done.
- `progress.py -v us` overall code baseline: **30.6320%** (assert this number after
  gated operations; function-count coverage per COVERAGE.md is 63.8%).
- fd.sh self-test: score 0 on matched `func_80010334` (src/10BB0.c).
- m2c -> splice -> fd.sh loop on two open functions (below).
- permuter import: `tools/permuter/import.py src/x.c asm/us/nonmatchings/<g>/<f>.s`
  works as-is with GS's build; generated compile.sh calls `tools/coalesce_cc.py`
  directly with INPUT before OUTPUT — the Stadium 1 preprocess.sh arg-order sed is
  NOT needed. sizeof repair via the patched permuter. 8 workers ~117 it/s on a
  login node for a 3-line function.
- import.py needs the draft/C spliced into the src file first (it reads the function
  as compiled); keep `permuter_settings.toml` at the repo root or import warns about
  missing compiler_type.

## Porting gaps (from the Stadium 1 audits)

Not yet ported: corpus.py (compile-command parse: GS has no preprocess.sh; the make
line contains tools/coalesce_cc.py and asm-processor), symcheck.py (rename
build/pokestadium-us.{elf,map} -> pokestadiumgs-us), accessmap.py (CPP flags +
draft mode), ido_bisect.py (compile-command parse, objdump fallback), ccs.py
(include dirs, VERSION_L), mkdraft.py (m2c scaffold; point its m2ctx call at
matching_notes/m2ctx.py), try/adopt/splice candidate tools (replace the draft-splice
with pragma-replacement), permuter_farm.sh + farm_status.sh + farm_logfilter.py +
farm_splice.py, palmetto_job.sh (Slurm), round.sh + round_prompts.py + agent_setup.sh
(prompt must absorb CONTRIBUTING.md/AGENTS.md conventions: gCamelCase/sCamelCase,
Domain_Purpose, //@path, // FAKE / // karodo, hex-vs-decimal rules, and the
no-drafts-committed rule), datamig.py (defer), rename engine (defer; needs us/jp
dual symbol tables, aliases.ld, hand_asm/, REWRITE_FUNCTION pragmas).

## Dead ends (smoke tests, 2026-10-18)

- `func_8000B28C` (src/AC80.c) score 510/530. Target: `li t6,0; li t7,0; lui at,%hi;
  sw t6,%lo(D_80087E30); jr; sw t7,%lo(D_80087E34)` — zeros materialized in registers
  + one shared lui + delay-slot store. Tried (all fold to `sw zero` + 2 lui): two
  extern globals, array base D_80087E30[0]/[1], locals a/b, single local reused,
  pointer base, comma-if, arithmetic nops. Needs corpus.py (idiom search) or ccs.py
  (uopt view) before more attempts. m2c's draft also misses the delay-slot store.
- `func_800649D4` (src/654A0.c) score 300. Target: `li v1,3; jr; move v0,v1` — the
  constant gets its own register before the return. Tried: `return 3`, `ret = 3;
  return ret`, separate decl+assign, empty-if and self-assign blockers; permuter
  35k iterations, never below 300. Likely a structural shape (loop phi / ternary /
  macro) the permuter cannot synthesize.
- `func_82202628` (src/fragments/17/fragment17_10FFC0.c) score 700 STRUCTURAL (body
  25/25 identical; jtbl owned by fragment17 data blob). Full verified data-migration
  recipe in matching_notes/spool/func_82202628.meta: truncate the blob after
  D_8220E0CC, carry `const f32 D_8220E0D0[1] = { 0.001f };` in the prologue, yaml
  [.rodata, fragments/17/fragment17_10FFC0] start 0x11DAB0 -> 0x11DA90. Do this as a
  datamig-style change when convenient.

## Wave log

### Wave 6 (2026-10-19, S1 cross-ports, matcher agents): 10 matches (177 total)
- fc0216e2: all 10 remaining >=1.000 crossport twins (func_800052C4, func_8410A4F8,
  func_84120464, func_841569E0, func_84156AB4, func_84168B00, func_84168C18,
  func_88508B10, func_88508CAC, func_885096E0) via 6 agents on disjoint files,
  spools in matching_notes/spool/. 9 scored fd.sh 0 (several objdump-verified
  beyond the score); func_800052C4 sits at the file floor 10 — its own bytes all
  match, the 2 flagged lines are pre-existing neighbor reloc-text (per its meta,
  spelling D_800CDA30 directly scores 315: do not "fix" it).
- Neighbor-fixup classes this wave (agents verified codegen-neutral per object
  before spooling): three stale bootstrap externs for the target function
  retyped to the true signature + call-site spelling fixes (fragment79_38EFE0:
  func_84120464 (void*,f32,s16), D_84183C90 f32, 0x3F800000->1.0f,
  0x3F666666->0.9f); a matched forwarder's (void) -> () K&R retype
  (fragment79_3C60B0 line 46, BattleAnim_EffectTertiaryOwnerBonePosition —
  pure jal wrapper); a bootstrap extern + caller cast (fragment34_1C5AA0:
  func_885096E0 void(unk_D_88523050*)). Blob-symbol discipline held:
  func_84168C18's divisor is extern f32 D_8418C920 (resolves against the
  existing 3FC0A0 blob; that blob also feeds the PARKED func_84168CA4 — do not
  migrate it without that sibling).
- Stale-.s cleanup after the wave: splice-based adoptions leave the function's
  .s in asm/us/nonmatchings (adopt_candidate.py deletes it; manual splices do
  not), which made progress.py undercount. Deleted the 70 session-adopted
  .s files by hand (59 A_adopt + 10 wave 6 + 8AF1BAE8 via adopt_candidate).
  progress.py -v us now reads 32.1819% (handoff baseline 30.6320%).
  do_c_func_detection regenerates nonmatchings per remaining pragma on every
  make extract, so a deleted .s for a C-owned function stays deleted. Known
  leftovers predating this session: func_80047104.s (wave-4 manual match) and
  the hand_asm pair func_8000B6C0/func_8001FC60 nonmatchings copies.

### Farm seeds 5 + spinoff match (2026-10-19, after A_adopt): 1 match (167 total)
- farm-seeds-5 (700887f8): fresh mkdraft seeds for the sweep's 13 best B_farm
  targets + func_8AF1BAE8. mkdraft needed per-draft prologue surgery (the sweep's
  splice machinery auto-fixes these, mkdraft does not): rets/params redeclared to
  the file's established signatures (func_8AC06D8C s32, D_8419A0A2-class u8 vs
  s8, K&R `()` forms for mixed-arity callers like func_8411E164, address-taken
  callbacks declared as functions not M2C_UNK variables, D_88601890 u8* so cfe
  accepts pointer arithmetic). fd.sh full scores on the branch: 4, 5 x10, 10, 8 x2.
- func_8AF1BAE8 adopted on farm-port (5918a1e9) before farming: its only diffs
  were jal-reloc text (target .s still says func_8004A858, the pre-rename label)
  — full make OK, byte-identical. Seed fixups that mattered: no u16 mask on the
  Ui_DrawGradientQuad args (s32 prototype per src/4AC10.c), sp24 declared
  second for home slot 0x24.
- Farm job 17663103 (work1, 8h, SEED_BRANCH=farm-seeds-5): 13 functions x
  3 workers x 2 copies; staged build verified locally (COMPARE=0) before sbatch.

### Sweep A_adopt adoption (2026-10-19): 59 matches (166 total)
- All 59 score-0 sweep drafts spliced from matching_notes/sweep_zero/ in four
  ROM-gated batches (559ee32c, 6606a640, eac0d6c6, 2b0d3a7a), ~15 at a time.
  No jtbl-extent trap fired: every batch's full make printed
  build/pokestadiumgs-us.z64: OK with the unchanged md5
  1561c75d11cedf356a8ddb1a4a5f9d5d. COVERAGE.md: 6,887/10,532 (65.4%),
  3,645 owners left.
- Integration fixup classes seen when multiple drafts land in one file (all
  codegen-neutral, verified by the per-batch ROM gate):
  1. An m2c prologue's no-prototype extern (`M2C_UNK f();` / `s32 f();`)
     conflicting with the sibling draft's typed definition spliced above it
     (func_8005370C, func_8413D37C, func_88304F5C). Fix: retype the extern to
     the definition's signature and forward the call's arguments
     (func_80053908 now passes (arg0, arg1); target asm keeps a0/a1 in place
     across the jal).
  2. Two drafts declaring the same byte global with swapped s8/u8 types
     (D_8419A0A2/D_8419A0A3). Decide with the asm loads (lbu -> u8); retyping
     a store-only use is neutral.
  3. An already-matched function calling a newly-defined one with an implicit
     int declaration (func_841347A0 -> func_84137DB8): add the correct
     prototype on its own line BEFORE the caller; result-discarding plain-jal
     calls are unaffected. Check this before rebuilding when a file has
     one-liner matched functions referencing the draft target.
- The pre-existing `extern void f();` (no params) next to a `void f(void)`
  definition is C89-compatible — not a conflict; only return-type or
  implicit-int mismatches error.

### Wave 5 (2026-10-19, S1 cross-ports): 25 matches (107 total)
- 18 in commit d2f7e50b (C380 JPEG block x8 via Makefile CC_OLD=IDO 5.3 route —
  CHECK THE DONOR REPO'S PER-FILE COMPILER EXCEPTIONS before fighting regalloc;
  fragment67/79 ParticleGfx+BattleAnim; TradeCable/AuxiliaryEffect/Geo_NodeCamera)
  + 7 in commit 33cf0aca (Sched x3, Storage_GetSramHandle, Jpeg_InitializeDspTask,
  draw_profiler_mode_0, Timer_MeasureElapsedUs) with AC80-data + 7140-bss migrations.
- EXTRACT-STABILITY DEBT CLEARED (follow-up commit): 33cf0aca's migrations are now
  yaml-driven; make extract is safe again. yaml: `- [0x88A20, .data, AC80]` +
  `- [0x88A40, data]` split the 85DA0 blob (AC80.c owns [0x80087E20, 0x80087E40));
  `{vram: 0x800D0490, type: .bss, name: 7140}` + `{vram: 0x800D0510, type: bss,
  name: unk_bss3}` split unk_bss2 (7140.c sramHandle, SUBALIGN(16) 0x74 -> 0x80).
  Nothing stays ld-level. splat auto-insert gotcha: an explicit `.data`/`.bss`
  sibling anchors mid-list, so every LATER src file's auto-inserted section entry
  relocates after it — the regenerated ld shows the 85DA0 blob + AC80.o(.data)
  inside the src .data list and unk_bss/unk_bss2/7140.o(.bss) inside the src .bss
  list. Harmless here because only main (0x2B80 bss) and AC80/7140 own non-empty
  sections in those lists (verify in the .map before the next mid-blob split).
  Verified: two full extract+make cycles -> build/pokestadiumgs-us.z64: OK.
- Parked with recipes: spline trio (func_8290E040/E0FC/E1D8 — statics + orphan .bss
  at 0x8291BC14 + literal blob split; see W5b lessons), func_84164C28 + func_84168CA4
  (fragment79 blob datamig, joint).
- crossport_join.py + CROSSPORT_2026-10-19.txt: 106 GS-unmatched have S1 twins >=0.9
  (52 at 1.000); ~80 remain unworked. Upstream split machinery ready
  (upstream_split.sh, dry-runs clean; up/renames first, then per-fragment PRs).

### Wave 4 (2026-10-19 ~01:00): 9 matches + 5 near-misses + 2 blob-class parks
- 9 matched (see commit): func_80047104 [Font_GetHeightRecordIndex], func_8004A858
  [Ui_DrawGradientQuad] (+neighbor extern retype), func_82800490 [fragment10_main],
  func_82800620 (25 = neighbor rename-noise only), func_80068390, func_800684F0 (10
  reloc-class), func_80069900 (10 reloc-class), func_8006A51C, func_80070DEC.
- PARKED (blob-ownership display class; every byte verified identical, needs the
  fragment23-style yaml migration): func_800630F0 [Type_IdToChartIndex] and
  func_800631B4 [Type_ChartIndexToId] — recipe in spool metas; W4c verified the pair
  ROM-OK in an isolated tree (/tmp/opencode/psv, since removed) via insert
  [0xA5C90, .rodata, 63CF0] + const u32 D_800A5090[1]={0} prefix + 2 extern drops.
- Near-misses farmed: func_8002781C@744 (KEY CLUE in meta: call inside if(mode>=4)
  gives score 5 but the target jal is unconditional — needs the promoted-mode temp in
  a1 with an unconditional call), func_80031564@650 (la-CSE form), func_800333CC@1060
  (jtbl in A4590 blob — yaml migration recipe in meta), func_800113B4@492,
  func_8280105C@220 (missing trailing dead [jr ra;nop] stub).
- FARM MECHANICS FIXED (again): seed drafts alter the ROM BY DESIGN, so the staged
  build gate now runs `make COMPARE=0` (compile+link check only); byte-identity stays
  the integrator's local gate. Seeds branches MUST be re-cut after every rename wave
  (a stale branch's tracked src conflicts with the live tree's regenerated asm/ —
  farm-seeds-2 died on undefined Fragment11_DrawThickPanelFrame). Draft prologue
  typedefs can collide when two seeds land in one file — dedup on the branch.
- Farm job 17634152 (work1, 7h): 11 functions x 4 workers x 2 copies, seeds
  farm-seeds-3, SAVE_DIR /scratch/$USER/permuter_best_gs.

### Wave 3 (2026-10-19 early): 12 matches + 8 farm near-misses
- 12 matched (commit af2948bc): func_8001644C, func_800162D0 (+const SLOWCOPY data),
  func_8000A080 (both reloc-class-10 ROM-identical), func_8006E944, func_800697B8,
  func_8160551C (+no-param fixes), func_81603CD0, func_816039B0 (K&R), func_816044AC,
  func_8005CBA0, func_8005CDDC, func_8005FF0C. func count 6,791/10,532 (64.5%).
- 7 renames (GbApu_ResetSlotFlags, GbApu_InitSlowCopySlot, profiler_log_worker_time,
  Fragment11_DrawTexturedPanelBorder/ThickPanelFrame/BorderedPanelFill,
  GbSave_GetMapObjectPtr) — cross-file callers in dp_intro.c, fragment10_D5250.c,
  fragment87_code.c also rewritten.
- Near-misses farmed (farm-seeds-2 branch): 8005F5D4@60, 80058E60@170, 80058F18@170,
  8000B2A4@115, 8006F83C@712, 8006E858@1859, 80071E48@135, 80047158@165, 80056870@44,
  81604024@430, 800601A4@440.
- FARM BUG FIXED: palmetto_job.sh's SEED_BRANCH staging used
  `git ls-files --others --ignored --directory` as the overlay file list, which
  silently DROPPED .venv/ — the node then ran tools/coalesce_cc.py under system
  python 3.6 ("future feature annotations is not defined") and the gate died
  (job 17626142). New staging: rsync the whole live tree (minus .git/build/nonmatchings)
  then tar-extract the seed branch over it. Always verify a staged build locally
  before sbatch.
- Tool notes from W3 agents: try_candidate auto-restore failed once (verify with git
  diff); var.py old-text cannot span the return type (start at the params); K&R and
  multi-piece spools need matching_notes/splice_manual.py (whole-file splice).

### Wave 2 (2026-10-18 late): 31 matches, ROM-identical
- 31 matched via twin sweep + the 585D0.c cluster (commits 19f51484, 95d1dcc0 renames);
  see those commit messages for the per-function list and required neighbor fixes.

### Wave 1 (2026-10-18 evening): 25 matches, ROM-identical

- 25 functions matched via cross-overlay sibling twins (commit 0652592f); func
  count 6,748/10,532 (64.1%), 3,784 owners left. All fd.sh score 0 except
  func_8AF00240 (20 = reloc-SYMBOL-TEXT only; ROM byte-identical, confirmed by the
  full make).
- 8 semantic renames applied after the match commit (US table only, per upstream
  convention - jp tables keep their own names; verified MoveDamage_ComputeBase_fragment80
  has no jp entry): MoveDamage_ComputeBase_fragment79, ModelPreview_UpdateAutoRotation_fragment33,
  MathUtil_Atan2d_fragment14/48, Rect_Contains, Gfx_SetupOrthoProjection,
  Gfx_DrawTexturedFrame16, Envelope_Advance.
- Integration protocol that worked: agents spool to matching_notes/spool/<func>.{c,meta}
  (never commit, restore src); integrator applies fixups -> try_candidate --keep each ->
  `rm -r build/src` (NFS stale-object paranoia) -> full make must print
  `build/pokestadiumgs-us.z64: OK` -> commit -> rename batch (symbol_addrs_code.txt us +
  word-boundary src rewrites) -> `make extract` + full make -> commit.
- FLEET RULE: no agent fd.sh/make activity while the integrator runs `make extract` or a
  full `make` (extract regenerates asm/ under the agents' feet).
- After each integration, rebuild the objects the agents' experiments dirtied
  (corpus selftest flags them) and re-run `corpus.py build` before trusting the index.


## Upstreaming

Match PRs go to michiiik/pokestadiumgs via its PR gate (docs/PR_GATE.md: rebuild US
ROM to `build/pokestadiumgs-us.z64: OK` in a clean container). Keep this tooling and
all scratch out of those PRs: `tools/` changes force full -B gate rebuilds, and
tracked drafts would skew ci/update_undocumented.py counts. Tooling lives on this
branch only.
