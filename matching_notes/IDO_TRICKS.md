# IDO 7.1 matching tricks learned in round 1 (Pokemon Stadium decomp)

All of these produced actual matches or big score drops in this codebase.

## Recognising what the original source looked like
- **`addiu rX, rY, 0` before a subtract = 64-bit math.** Timer wraparound was
  `D = (v0 + 0xFFFFFFFFLL + 1) - prev;` (matched func_87802E58 and func_86A01490).
- **`while(1)` loop ending with a stack spill of the next pointer = self-recursive tail call**
  (func_82501B18: `return func_82501B18(arg0->unk_34, arg0->unk_02);`).
- **In-function `static` changes codegen:** IDO knows nothing else aliases it, so it keeps the
  value/address in a register across loops and stores back at each exit, and skips address CSE.
  If register alloc / loop-exit stores around one global won't line up, try making it a function
  static (func_81209374, func_81207DF8, func_86A013C8). Caveat: function statics are placed in
  bss/data at an unpredictable spot; that can break the layout. The data/bss may then need to be
  migrated into C (or a section split) for the match to link.
- **m2c `spXX` names are often spilled CSE temps, not variables.** Inline the expression back;
  this shrinks locals and moves spill slots to the right place (func_87803EAC, func_83500FE8).
- **Conversely, a value spilled into the compiler-temp area may be a CSE'd expression** — writing
  e.g. `var = cond ? 1 : 0;` and using `(1 << var)` in two loops reproduced a single spill.
- **A pointer living in a stack slot just below the named locals may be IDO's own strength-reduced
  pointer** for `arr[i]` indexing (func_80044EA4). Don't declare a cursor local: write plain `arr[i]`
  everywhere and drop a pad so the compiler temp takes that slot.
- **Consecutive stack slots stored/reloaded around calls (spF8, spFC, sp100…) = a local array.**
- **Back-to-back `sw`/`lw` of the same slot in a leaf function = local array (`f32 tmp[N]`)**, not volatile.
- **Ascending-order byte stores = hand-written stores**; IDO emits `for`-loop stores descending.
- **Separate `%hi/%lo(sym+0x14)` bases = separate array symbol** in the original. Watch 8-byte
  alignment of static arrays >= 8 bytes when splitting (D_8780FCCC had to be `[3]`).
- **`%hi(sym+off)` constants per iteration rather than base+offset = index loop**, not pointer walk.
- **`bgez` + 0x4F800000 fixup on int->float = source had a `(u32)` value/cast.**
- **Check for a known SM64 / libultra equivalent first.** func_86B09F64 was `mtxf_rotate_zxy_and_translate`;
  writing it the SM64 way matched every FPU register at once where the m2c-shaped draft never would.
- **Passing structs by value**: floats stored to arg home slots + reads at 0x38.. = by-value
  `Vec3f`/`Vec3s` args (func_86B09F64).

- **Straight-line runs of gfx macros may be an unrolled loop.** IDO unrolls small loops 4x (with
  peeling); the tells are a loop counter still stored (`j = 1`) or `j*2` left unfolded, and a frame
  too big from the macros' `_g` slots (func_84362084: `for (j = 0; j < 5; j++) gSP2Triangles(...)`).
- **Literal spelling matters for rodata/register sharing:** `1e-6f` vs `0.000001f` changed which
  constants shared a register and reordered late_rodata (func_86803C6C). `M_PI` vs `M_PI_F` in a
  double expression gives identical asm but a different ROM ((double)(float)pi) - only the full
  `make` catches it (func_84362084).
- **Loop bound `i < NU` (unsigned) keeps a plain counter compared with `sltiu`;** with a signed bound
  IDO replaces the counter by a pointer or `i*4` (func_88203ED8; fragment23_1AE680.c already uses `j < 8U`).
- **Chained assignment keeps an address alive:** `A = B = 0;` re-reads B, so `&B` has two uses and
  stays in a register (func_80041A98); a volatile store + plain store does not.
- **Float vector init with DOUBLE literals** (`-1.0`, `0.0`) keeps all three multiplies of a dot
  product; with `0.0f` uopt folds the x*0 terms (func_80033D44).
- **A callee's parameter type decides constant sharing:** two calls passing the same constant as
  `u32` and `s32` stop IDO CSE'ing it into an s-register (func_88209B54).
- **Case label ORDER inside one `case a: case b: case c:` group** changes where a reload lands and
  can rotate every t-register after it (func_810010BC).
- **A struct-array loop pointer that m2c types as `&arr[i]` may really be `(u8*)arr + 4`:** check with
  accessmap.py --draft; the symptom is every store one field late (func_80033D44).

## Stack layout
- Every declared local gets a home slot (even unused / register-only ones), top-down in
  declaration order with natural alignment; s16/u8 locals pack. Compiler spill temps go *below*
  all named locals (from 0x18 up / just below the lowest stack-homed local).
- Fix frame size / offsets by deleting m2c's unused junk locals, reordering declarations, adding
  `UNUSED s32 pad;` / `pad[N]` at the right position. `pad[N]` steps can be 16-byte periodic.
- Each `gDisplayListHead++`-style gfx macro has a block-scoped `_g` that takes a slot.
- **Compiler-temp slot order follows where each expression FIRST APPEARS in the source**, not where
  the code is emitted (func_84367660: a dead early copy of six expressions moved their slots).
- **One pointer loop variable shared by two loops in different switch cases**
  (`for (i = 0, ptr = X; ...; i++, ptr++)`) reorders the bottom-of-loop increments and frees a hidden
  temp slot (func_86800B38); its declaration scope (switch vs function) changes the result a lot.
- Spill-temp slot *order* among themselves isn't controlled by declaration order — that remained
  unsolved in several functions (func_8430506C, func_84302658, func_838043F8, func_8850B2D4).
  Ideas not yet tried much: changing which sub-expressions are temps vs named, splitting/merging
  blocks, `if (1) {}` / empty statements, changing loop forms, different variable scoping.
- **Diagnose the stack-diff class before choosing a fix:** every slot shifted by the same amount
  = one named local missing/extra -> declaration surgery (matching_notes/stack_perm.py sweeps
  insert/delete/swap moves). Most slots one way but one slot the other way = spill-slot ORDER
  problem (func_88805AEC, 2026-10-17: every declaration move scored worse; declaration surgery
  is provably useless there). The fix has to change CSE discovery order — statement order,
  temps-vs-literals spelling, or a PERM_RANDOMIZE focus on the statements where the spilled
  CSEs are first discovered (early in the function).

## Registers / scheduling
- Reusing one local for several unrelated values can unify register choice (func_80049A60).
- Statement order of independent assignments swaps registers (func_80013D34).
- Inline ternary vs temp flips operand order of `and`/`multu`; to get a constant first in a
  `multu`, put it in a variable assigned just before the use.
- `(u32)(u64)expr` casts consume ~4 hidden temps and shift the round-robin t-register rotation
  (t6-t9, t0-t5). Add/remove such casts to rotate temps (func_82F0BEF8).
- Reading back a just-stored u8 field gives an extra `andi 0xFF`.
- `x += 1` vs `x++` on u8 changed register allocation. `j != 8` gives `bne`; `j < 8U` gives `sltiu`.
- Swapping which loop variable (i vs j) a loop uses changes reg + spill assignment.
- Integer literals in float context aren't merged with float literals (`1` vs `1.0f`); the same
  constant with different types isn't shared — fix field/extern types (u32 vs s32, u8 vs s8).
- Switch: `default:` placed last with no `break` gave the target block order.
- Odd no-op lines in existing drafts (`if (1) {}`, `if ((a && a) && a) {}`) can be load-bearing;
  test before removing.
- Writing the struct / float constants as plain literals moves them into the function's
  late_rodata; if the rodata lives in asm, keep them `extern`.
- **A global's address cached in an s-register because of a goto loop** disappears if that loop gets a
  second entry (retarget the back-edge to an equivalent label inside another case) - uopt then stops
  treating it as a loop (func_84372670).
- Recursion: `var_s5 = var_s2 = 1;` init + `var_s5 = var_s2;` at loop end pattern (func_88803614).

## Tooling gotchas
- **diff.py `-s` stops at the first `jr ra`**: for functions with early returns fd.sh and ido_bisect
  under-report (a 0 can be a false match). Score such functions without `-s`, with the following
  function left as GLOBAL_ASM so the diff does not run on (4A3E0.c GB channel functions).
- **include/macros.h `CLAMP_MAX`/`CLAMP_MIN` return the LARGER/SMALLER value**, the opposite of their
  names; matched code using them is correct but reads backwards (func_8437B0CC uses ternaries).
- `fd.sh` grep for the score: diff.py prints `CURRENT (N)`, not `Score`; fixed 2026-10-07.
- Repo-root `diff.py` is broken on Python 3.12; use `tools/asm-differ/diff.py -o <func> --format plain`.
- diff.py score 0 is NOT proof: it treats `sym+off` relocation differences as equal. Always confirm
  the full `make` prints `build/pokestadium-us.z64: OK`.

## SCORE TRUST RULES (2026-10-17; after three "cap illusion" incidents in one day)
The ONLY ranking scale in this repo is the FULL diff: NO `-s`, `--max-lines 30000`, against a
forced rebuild. Everything below now produces exactly that scale; do not compare against any
other number.
- `fd.sh` (since 2026-10-17): full diff, `rm -f` the .o first (NFS trap), and prints a loud
  reminder when a 0 shows up. Before that it used `-s` + diff.py's 1000-line default, which
  (a) hides diffs after early returns (func_8004A89C: a false 0 unwrapped a 4-instruction-short
  tail that shifted the whole ROM 0x10) and (b) silently truncates big functions (func_8437B0CC:
  the same edit measured 3083 capped / 6584 full, and later 2873 capped / 7809 full - the
  truncation is not monotone, so a REGRESSION can look like an improvement).
- `var.py` (since 2026-10-17): builds each variant with a forced rebuild and prints the FULL
  score. Older sessions ranked variants with fd.sh's capped output - do not trust old var.py
  numbers in notes.
- `matching_notes/draft_score.py src/f.c func_X`: full score of the committed NON_MATCHING draft,
  file restored. `matching_notes/cand_score.py src/f.c func_X candidate/source.c`: full score of a
  spliced permuter candidate, file restored. Use these for every adopt/keep decision.
- The permuter's OWN score is a different scale per import (and its RANKING disagreed with the
  real fd score on fragment28_2190D0.c and 33FE0.c on 2026-10-17): cand_score every candidate
  before trusting it, never rank by the permuter number.
- A 0 from any of these is still not a match (relocations compare equal): only the full `make`
  printing `: OK` proves a match. That gate caught the false-0 above.

## Other tool traps
- NFS stale-object trap (2026-10-17): `make` on NFS sometimes judges a just-rewritten .c older than the
  .o and SKIPS the rebuild, so a wrapper can print the PREVIOUS state's score. fd.sh and var.py now
  remove the .o before building; any new tool must too (`rm -f build/<file>.o`), or the score is
  advisory only.
- Permuter: always pass `--stack-diffs` (otherwise stack-only diffs score 0). The generated
  `nonmatchings/<f>/compile.sh` has the wrong arg order for tools/preprocess.sh; fix with
  `sed -i 's/-O2 "$INPUT" -o "$OUTPUT"/-O2 -o "$OUTPUT" "$INPUT"/' nonmatchings/<f>/compile.sh`
  (the bad order also leaves a stray file named `-I`). The permuter's pycparser fork mangles
  `sizeof(T) * N` into `sizeof((T) (*N))`; fixed by `matching_notes/permuter_sizeof_prec.patch`
  (apply with `git -C tools/permuter apply ../../matching_notes/permuter_sizeof_prec.patch`, then
  `rm tools/permuter/perm_pycparser/yacctab.py` so the tables regenerate). permuter_farm.sh also
  repairs the pattern in base.c as a fallback.
  Kill with `pkill -f "permuter[.]py nonmatchings/<func>"` (plain pattern kills your own shell).
- Faster than full make: `make build/src/<path>.o` (~6s) then diff, batch-testing variants with a script.
- `src/4A3E0.c` has a struct missing a `;` (`char unk2D[0x13]`) — m2ctx/permuter need it added in their copy.
- When grepping build output for errors, ignore `cfe: Warning` lines.
- Sandbox: `source .venv/bin/activate` / inline `PATH=` may be refused. What worked:
  `env PATH=<MAIN>/.venv/bin:/usr/local/bin:/usr/bin:/bin make -j2 PYTHON=<MAIN>/.venv/bin/python3`,
  or symlink the worktree's `.venv` to MAIN's (it's gitignored).

## Spill-slot order follows when a common subexpression is found (2026-10-16, func_8850B2D4)
Two temps that IDO spills get stack slots in the order their common subexpressions are discovered.
An expression that only becomes identical to another after a constant local is propagated (write it
with the draft's `w`/`h` locals instead of the literal) is found later and so gets the later slot:
swapping the two spill slots of func_8850B2D4 came from writing `((arg2 - 7) + h) << 2`.

## Data layout facts (2026-10-16, Phase D)
- IDO puts every data object on a 4-byte boundary; a label at an unaligned address is a field.
- .data/.rodata are emitted in source order, initialized function statics included (`static T x = 0;`
  -> .data at its source position; no initializer -> .bss).
- String literals from data initializers go to .rodata in source order, one copy per use, each padded
  to 4. A file's sections end padded to 16, so a zero gap ending on a 16-byte boundary is a file edge.
- A named `const` scalar goes to .data; a .rodata float in the ROM is an anonymous literal.


## as1 scheduling ties follow .loc line numbers (2026-10-16, func_80012870, agent-2)
as1 breaks instruction-scheduling ties by the source line recorded in `.loc`. Code attributed to an
earlier statement is scheduled ahead of later statements' stores. uopt sinks expressions built only from
locals/arguments into the call that uses them, but not expressions that load globals or pointers:
computing the call's arguments in their own statements with inline table loads moved the coordinate code
to an earlier line and fixed a one-store scheduling diff. Verified by editing ugen's .G records
(`cc -K`) and re-running as1 alone.

## Other round-8 lessons
- A dead assignment, or an unused initialized local, makes a CSE expression appear earlier in the source,
  which moves its compiler-temp stack slot (func_838043F8, func_82F04604, func_84302658).
- An explicit guard plus `do-while` changes the order of the loop-end stores (func_82F04604).
- Repeated strip/texture blocks can be one loop that IDO unrolled by 2 with a peeled iteration (func_8130337C).
- A comma expression can reorder two adjacent stores (func_8820BE14).
- A "phantom" saved FPR (saved, never used) can be a named float whose register move as1 forwarded away
  (func_80034348: len in fs3).

## uopt copy propagation and live-range identity (2026-10-17, agent-13: func_8004A474, func_84367660)
- `x = <expr of register variables>` is copy-propagated: x's uses become a CSE temp of the expression and
  x itself disappears (so a later reuse of x is a separate range with its own register). To keep x a real
  variable, redefine one operand between the def and a use with code that compiles to nothing (a re-read
  of a CSE'd load, `duty = D_800FD008[7].value;`, or a dead store to a dead parameter, `arg4 = 0.0f;`).
  Loads through memory (`p[0xE] & 8`) are not propagated.
- One variable = one live range over every region where it is live (not split into webs). A variable
  reused early (e.g. `a3_z = arg3->z` for call args, then `a3_z = arg4 * sp128`) inherits interference
  from the early block, including precoloured argument registers f12/f14; use a separate local early.
- Interference is block-granular: two ranges live in the same basic block interfere even if their
  instruction ranges do not overlap. An empty `if (x) {}` is a block boundary.
- Expression temps are coloured in first-appearance order of their expressions (dead copies count).
- Use `matching_notes/ccs.py` (pre-as1 registers; it now adds -I<source dir> for fragment headers) to see the
  real uopt choice: as1 renames/forwards registers, so final asm can hide a `mov.s` from a temp.

## F5 tidy trap (2026-10-17): clang-format breaks the ROM
Running clang-format over a matched file changed instruction scheduling and broke the byte-identical
ROM: as1 breaks scheduling ties by .loc line numbers (see the func_80012870 lesson), so ANY
reflow that changes line attribution can reorder instructions. Permuter-formatted functions can
only be tidied in ways that keep each statement on its original line (or verified with a full make
after every single-statement change).

## u64 perturbations: placement dominates form (2026-10-17, func_8437B0CC)
The `& 0xFFFFFFFFFFFFFFFFu` mask / `(unsigned long long)` cast family (a forced u64 temp that
shifts ugen's allocation) is placement-sensitive far more than form-sensitive: the same test written
with a cast, `!= 0`, or `== 0` instead of the mask can differ by 5000 lines (the cast optimizes
away entirely - only the mask forces the temp), and a mask that is load-bearing at one site
(case-0x1/0x20 unk_4D: 5479 vs 7809) regresses at five sibling sites (5879-9244). The farm found
two working placements by search (the unk_4D mask, then a cast on an sp103 array index - the
second made the first removable, 5479 -> 4724). Sweep sites, don't reason about them; expect
interaction effects between multiple perturbations.
