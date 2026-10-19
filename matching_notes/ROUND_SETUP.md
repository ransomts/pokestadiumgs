# Matcher protocol (pokestadiumgs, shared-tree edition)

Read this, then matching_notes/IDO_TRICKS.md (compiler lessons — the single best
predictor of success), then matching_notes/NOTES.md (dead ends; do not retry them).

## Environment

- Repo: /home/tsranso/Code/pokestadiumgs (fully built; expected/ current).
- ALWAYS invoke python as `.venv/bin/python3` (system python3 is 3.6 and broken).
  fd.sh/var.py are invoked directly; everything else via the venv interpreter.
- Tools (all under matching_notes/):
  - `fd.sh <src/file.c> <func> [max_lines]` — build one .o + FULL-uncapped diff. The
    only score you may rank with. Exit 1 with a score line is normal (nonzero).
  - `var.py <src/file.c> <func> <specfile>` — batch text variants (spec: variants
    separated by `=====`, edits by `-----`, each edit `<old>\n@@@\n<new>`).
  - `mkdraft.py <func> <src/file.c>` — m2c draft, spliced over the pragma, scored.
    `mkdraft.py restore <func>` — surgical un-splice (other edits survive).
  - `try_candidate.py <src/file.c> <func> <candidate.c> [--keep]` — splice a candidate,
    score, restore (unless --keep). Carries the candidate's extern prologue.
  - `ccs.py <src/file.c> <func>` — IDO cc -S pre-as1 view (uopt's register choices).
  - `corpus.py show|near|search|siblings` — the 6,912-matched-function oracle
    (`corpus.py show FUNC` prints asm with the C that produced it; `near FUNC`
    works on unmatched functions via the fd.sh temp file).
  - `symcheck.py FUNC` — symbol-premise linter.

## Shared-tree rules (hard)

- Work ONLY on the src files assigned to you. Other agents own other files.
- NEVER `git commit`, NEVER `git add`. Never run `make extract`. Never a full `make`
  (the integrator gates matches with whole-ROM builds). Single objects only, via the
  tools above.
- Leave your src files CLEAN when you finish with a function: `mkdraft.py restore`
  (or try_candidate's auto-restore). `git status` at your finish must show no edits
  to your assigned files.
- If you run fd.sh on a function, the tool deletes and rebuilds its .o — fine.

## Workflow per function

1. Read the target asm `asm/us/nonmatchings/<grp>/<func>.s`. If a sibling is given:
   `corpus.py show <sibling>` and copy its C — the twin usually differs only in
   symbol names/addresses. Retarget every symbol to the names in YOUR target .s
   (the .s is already symbolized with the correct twin-local names).
2. Baseline: `mkdraft.py <func> <file>` (m2c draft + score) — often the sibling C
   scores better; keep whichever is lower and iterate on it.
3. Iterate: hypothesize what the ORIGINAL source looked like (IDO_TRICKS.md), edit,
   `try_candidate.py` or var.py batches, read only the differing lines. ccs.py when
   you suspect a uopt copy-prop/coloring issue.
4. On score 0 — or your best stable score if stuck — SPOOL (below) and restore the
   file. Timebox: if ~40 minutes on one function yields nothing, spool the best
   draft with dead-end notes and move on. New dead ends are a deliverable.

## Spool format (matching_notes/spool/, gitignored)

- `<func>.c` — the EXACT text to splice over the pragma: any externs/typedefs
  (prologue lines the file needs) followed by the function body, in final form
  (mkdraft/try_candidate marker format is applied by the integrator — just give
  clean C, prologue first, then the function).
- `<func>.meta` — lines:
  ```
  func=<func>
  file=src/fragments/NN/....c
  score=<best fd.sh score>
  sibling=<sibling func or none>
  name_suggestion=<Domain_Purpose name, ONLY if evidence is concrete>
  name_evidence=<one sentence: decoded string, sibling identity, call context...>
  notes=<dead ends / what remains>
  ```
  Naming rules (Team Hippodrome, CONTRIBUTING.md): functions `Domain_Purpose`
  (<= 50 chars, specific is good); game globals `gCamelCase`, fragment-statics
  `sCamelCase`, locals `snake_case`; structs `TitleCase`. Only suggest a name
  when you can cite the evidence — otherwise leave name_suggestion empty and the
  integrator keeps the func_ name.

## Truth rules

- fd.sh score 0 is NOT proof of a match (relocations compare equal). Only the
  integrator's full `make` printing `build/pokestadiumgs-us.z64: OK` is.
- Full scores only (no -s, --max-lines 30000) — the tools already enforce this.
- Never rank against a capped number; never trust the permuter's own score.
