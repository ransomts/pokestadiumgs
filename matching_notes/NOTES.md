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
