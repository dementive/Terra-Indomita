# Merging Invictus into Terra Indomita

**Never run `git merge upstream/main`.** Terra Indomita (TI) and Invictus (INV) use different ID
spaces, and a plain merge silently re-points references. That is how Chinese characters ended up in
Greek events. Merge through the translated vendor branch instead.

## ID spaces (who owns what)

| Thing | Invictus | Terra Indomita |
|---|---|---|
| Characters (`setup/characters`) | IDs 0–1515. Unused ones are dead "Dudley" placeholders in `000_dudley.txt` | 1516+, only in `000_indomita_characters.txt` |
| Provinces | 1–8062 mean the same place in both. INV 8063–9469 are renumbered in TI (9888+). INV's newer IDs map to the TI province covering that land | TI map is authoritative: `map_data/`, `gfx/map/` and `setup/provinces` placement |
| Country tags | `maps/tags.csv`: e.g. INV `SIC` (Sicyon) is `SYC` in TI, INV `AMA` (Amantinia) is `X16` | TI's tags |
| Treasures (`treasure_manager.database`) | below 1000 | 1000+ |
| Families (`setup/main/01_families.txt`, linked by `family = N` in country setup) | below 2000 | 2000+ (`fix_families.py` enforces this) |
| Portrait gene templates (`common/genes/00_genes.txt` `index = N`, stored by number in character `dna`) | Invictus's indices | TI templates take indices after Invictus's. When a merge shifts one, `remap_dna.py` rewrites TI-authored DNA |
| Areas/regions | `maps/areas_regions.csv` maps INV names TI lacks | TI's `map_data` |

## How the merge works

`invictus-translated` is an orphan branch. Each commit on it is an Invictus release rewritten into
TI IDs, without the paths TI owns (map, non-English loc, files TI deleted on purpose, old military
traditions, `setup/provinces`, `setup/main/00_default.txt`). Merging it into `dev-Indomita` gives a
normal 3-way merge where the base is the previous translated release, so only real upstream changes
show up.

## Procedure for the next release

From `tools/invictus_merge/`, with Python 3. Everything reads git objects, so the working tree only
changes where a step says so.

1. **Prepare.**
   - Run `git fetch upstream` (remote = the local Invictus checkout).
   - Fast-forward `dev-indomita-backup` to `dev-Indomita` and push it.
2. **Maps.**
   - Rename `maps/provinces.csv` to `maps/provinces_base.csv`; it now describes the previously merged release.
   - Run `python build_province_map.py upstream/main dev-Indomita` and review `low`/`medium` rows that content actually uses (see step 4's report). Fix a row by setting `method` to `manual`; manual rows survive rebuilds.
   - Run `python build_name_maps.py upstream/main dev-Indomita` for tags and areas/regions, then check any `COLLISION` rows.
3. **Audit and repair references in TI.**
   - Run `python audit_chars.py dev-Indomita <last merged INV sha> upstream/main`, then `python repair.py dev-Indomita <last merged INV sha>`.
   - Review `reports/char_audit.csv` (rows with `change=yes` or `UNRESOLVED`) and commit.
4. **Vendor commit.**
   - Run `python vendor.py next upstream/main dev-Indomita`. This appends translate(INV) to `invictus-translated`.
   - Unmapped or low-confidence IDs are in `reports/vendor_<sha>.csv`.
5. **Merge.**
   - Run `git merge --no-commit -X ignore-space-change -X find-renames=90% invictus-translated`.
   - Run `git checkout --conflict=zdiff3 -- <conflicted files>` and then `python resolve_trivial.py <files>`.
   - Run `python semantic_merge.py loc|script <depth> <files>` for keyed merges. Review `reports/semantic_conflicts.csv`.
6. **Setup.**
   - Run `python setup_merge.py <prev INV> upstream/main provinces_base.csv provinces.csv`, then `python setup_fixups.py`.
   - Port changes to files TI replaced with `port_defines.py` (defines) and `semantic_merge.merge_script` (e.g. `00_hardcoded_inv.txt` into `00_hardcoded.txt`).
7. **Post-merge.**
   - Delete Dudley placeholders for IDs INV now defines.
   - Run `python fix_families.py upstream/main`. It keeps TI's families at 2000+ and restores Invictus families TI shadowed or lacks.
   - Run `python remap_dna.py`. It re-points TI characters' DNA at the gene templates they were made with, if a template's index moved (in January 2025 Invictus's pharaoh headdress took index 18 from `japanese_hairstyles`, putting it on Zhou's king).
   - Run `check_integrity.py scan` on the pre-merge and merged trees, then `diff`.
   - Run imperator-tiger on both trees and diff (see `MERGE_REPORT.md` for the 2026-10 run).
   - After committing the merge, run `python audit_chars.py check HEAD invictus-translated`. It resolves every character reference through blame against the table of the commit that wrote it, and compares the result with HEAD's table. Any row in `reports/char_check.csv` with `change=yes` or `UNRESOLVED` is a reference that now points at a different person.

## Files

- `gitio.py`, `pdx.py`: git plumbing and a span-preserving Paradox script parser.
- `mapdata.py`, `build_province_map.py`: province map builder (local affine projection plus names).
- `build_name_maps.py`: tag and area/region maps.
- `chars.py`, `audit_chars.py`, `repair.py`: character tables, blame-based reference audit, pre-merge repair.
- `refs.py`, `translate.py`, `vendor.py`: ID reference finders, the INV-to-TI translator, the vendor branch.
- `resolve_trivial.py`, `semantic_merge.py`: conflict resolution (whitespace-only hunks; keyed 3-way merges).
- `setup_merge.py`, `setup_fixups.py`, `port_defines.py`: setup data and replaced-file ports.
- `check_integrity.py`: before/after static checks.
- `tiger_diff.py`: diffs two `imperator-tiger --json` reports. Also run tiger on the Invictus checkout and subtract its findings, so you see only merge-induced problems.
- `fix_families.py`, `remap_dna.py`: keep TI's family IDs and portrait gene indices clear of Invictus's.
- `dedupe_defs.py`: resolves definitions duplicated across the two mods; feed it tiger's duplicate-item findings.

## Lessons from the 2026-10 merge

- **Invictus adding a file that redefines a whole TI database entry** silently replaces TI's version. Example: `common/cultures/01_chinese.txt` dropped TI's Chinese cultures. Look for tiger "redefined" warnings in culture, religion and similar files.
- **Content that uses things TI deleted.** Inventions, laws, culture groups, regions and event pictures that TI deleted are still used by new Invictus content. The tiger `missing-item` errors that Invictus itself doesn't have are the to-do list.
- **Loc-key hash collisions.** Two different loc keys can collide on their murmur3 hash. tiger reports these as `localization-key-collision`.
- `obsolete/`: the old renumbering script that corrupted references. Don't use it.
