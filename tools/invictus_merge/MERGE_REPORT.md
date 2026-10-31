# Invictus 1.12.0.1 → Terra Indomita merge report (2026-10-30)

**Result:**
- Invictus `8dc22b2a78` (1.12.0.1) is merged into `dev-Indomita`. The previously merged upstream was `f2e32b70d1`, merged in `05307d36b` in Jan 2025.
- **Character references:** every one still resolves to the person its author meant.
- **Other references:** no province, area, region or brace problems were introduced.
- **imperator-tiger:** 1,942 errors after the merge vs 1,954 in TI before it. That's fewer errors, while bringing in 3,680 upstream commits.

How to run the next merge: [MERGING.md](MERGING.md). All per-decision logs are in `reports/`.

## Commits (on `dev-Indomita`)

| Commit | What |
|---|---|
| `5e232cf4c` | Merge tooling and ID maps (`tools/invictus_merge/`) |
| `b04f73ac5` | Repair of stale IDs that were **already broken in TI** before this merge |
| `af23e9d33` | Records translated `f2e32b70d1` as merged (`-s ours`). This establishes the merge base |
| `a582f747d` | The merge of `invictus-translated` (Invictus 1.12 in TI IDs) |
| `37804d6b1` | Post-merge fixes found by the integrity checks and imperator-tiger |
| (this report) | Report and final tooling |

`invictus-translated` is an orphan branch holding Invictus releases rewritten into TI IDs (`872427c65` = f2e32b70d1, `05cc9850e` = 1.12.0.1). Keep it: the next merge builds on it.

## 1. Repairs to pre-existing TI breakage (`b04f73ac5`)

**Character references (235 fixed; `reports/char_audit.csv`).** Each reference was resolved through `git blame` to the person meant when it was written.

| Fixed | What was wrong | Examples |
|---|---|---|
| 181 | TI references never shifted when TI's characters moved +1000 in Feb 2025 | Confucius `char:520` → `1520`; Zhao, Han and Wei royals |
| 8 | Written after the shift with old numbers, so they landed on Dudley placeholders | Lu, Yue and Song mission loc |
| 40 | Invictus references corrupted by the old `000_indomita_merge_fix.py`, restored from the Invictus base | Philip II 714 → 35 (17×); Hegesias/Anniceris 661/662 → 468/469; Darius, Cyrus, Bodmelqart, Uthiyan Chera |
| 4 | Mithridates moved by Invictus | `char:97` → 228 in TI on_actions |

Also repaired:
- Ajita (1714) sat in a block with no wrapper, so the game never defined him. The Charvaka deity pointed at 714 and now points at 1714.
- The old renumbering script was retired to `obsolete/`.

**Province IDs, tags and areas in lines TI inherited from Invictus and never edited:**
- 545 province IDs, 81 tags and 11 area/region names were translated to TI's map.
- Example: South Arabia missions pointed at `p:8847` (Invictus Jadis), which is a Chinese province on TI's map. It is now TI's 11229.

## 2. The merge (`a582f747d`)

### ID translation of Invictus content
- **Provinces:** TI's map is Invictus's world rescaled about 0.52×. The province map (`maps/provinces.csv`) was built from a local affine fit on the 7,924 provinces with the same ID and colour (median error 11.5 px), plus unique-name matching near the projected position.
  - 1,356 province references in Invictus 1.12 content were rewritten with high confidence, 46 at low or medium confidence (review list below).
  - Province-name loc for renumbered provinces stays TI's.
- **Tags (`maps/tags.csv`):**
  - Invictus `SIC` (Sicyon) → `SYC`, `ELY` (Elesycia) → `ELS`.
  - The 11 tags TI reused map to TI's hosts: `AMA`→`X16`, `NAS`→`NSM`, `SA0..4`→`ST0..4`, etc. Also `RAY`→`TM6` and `SHN`→`SHT`.
- **Areas/regions (`maps/areas_regions.csv`):** e.g. `shan_area`→`halin_area`, `syrtis_area`→`soda_area`, `bohemia_area`→`bohemia_region`, `himalayan_region`→`xiyu_region`.
- **Characters:** no translation needed. Invictus owns IDs below 1516; its new 551–578 replace Dudley placeholders.
- **Treasures:** ID 867 was TI's Beast of Achelous but Invictus's new Boar's Head Carnyx. TI's moved to 1056 (TI treasures now live at 1000+).

### Conflicts
98 files conflicted (about 430 hunks). They were resolved this way:
- Whitespace-only hunks were dropped automatically.
- Keyed 3-way merges per block, field and loc key (`semantic_merge.py`; `reports/semantic_conflicts.csv`):
  - 1,138 Invictus additions were taken.
  - 254 fields both sides changed kept TI's value.
  - 29 AI-weight blocks took Invictus's rework.
- Three review passes followed (`reports/review_A_balance.md`, `review_B_content.md`, `review_C_military_religion_culture.md`):
  - **Balance:** 108 inventions TI had moved between groups received Invictus's AI weights. TI's unclosed `}` in `00_religious_inventions.txt` (broken since TI commit `278e80578`) is fixed.
  - **Content:**
    - TI's Fezzan missions had a missing `}` that nested every task after task_15. Fixed, and Invictus's Fezzan potentials are applied.
    - The amber decisions were rebuilt with TI's pattern.
    - `me_tasm.30` now targets the Yamama provinces.
  - **Military, religion and culture:** levy totals are back to 1.0, and `levy_enetoi` is restored (it was broken in TI). Unit abilities and deity effects were merged.
- **GUI:**
  - The lobby takes Invictus's new nation-tab system, plus a new **East Asia** tab (TI's 25 Chinese, Korean and Japanese mission nations), selected by default.
  - Invictus tags inside GUI files were translated.

### Setup data (`setup_merge.py`, `setup_fixups.py`)
- `setup/provinces`: 575 province blocks took Invictus's field changes. TI wins on fields both sides changed.
- Invictus `00_default.txt` was merged per entity into TI's split `setup/main/01_families.txt` and `02_*.txt`:
  - 564 additions and 154 deletions.
  - 49 `own_control_core` lists merged as sets.
- **Invictus's 35-tag cull:**
  - Applied to the 27 countries TI never customised.
  - TI kept the 8 it had customised: ARC, ORG, PTA, KAO, PYK, KIO, VRI and TEN. Their `countries.txt` registrations were restored.
- **Ownership:** where the two sides disagreed, TI's existing owner keeps the province (41 cases).
- **Dropped countries:** 9 new Invictus Saharan countries (ATA, ATL, SOI, MOB, ZKO, SFY, EIN, NGT, PHU) have no land on TI's map, so their setup was removed.
- **Siculi (SCU):** keeps TI's land, because Invictus moved it onto a province TI doesn't have.

### Files TI replaced with its own versions
- **Defines:** 27 Invictus define changes were ported into `common/defines/00_defines.txt`. `MAX_RECON_DISTANCE_NAVY` is 1802, Invictus's 3500 ("Italy → Albion") scaled to TI's map.
- **Hardcoded modifiers:** Invictus's changes were ported into `common/modifiers/00_hardcoded.txt`.
- **Military traditions:** only 3 compatible Invictus value tweaks were ported into TI's `ti*` traditions. Invictus's AI weights there targeted modifiers TI had removed.
- **Duplicate definitions:** 29 cases where both mods override the same vanilla effect, trigger or office were reduced to one copy (`reports/dedupe_defs.csv`).
- **Chinese culture group:** Invictus's new `common/cultures/01_chinese.txt` was dropped. It redefined the `chinese` culture group with only `qin` and would have deleted TI's 12 Chinese cultures.

## 3. Post-merge fixes (`37804d6b1`, `reports/postmerge_fixes.csv`)
- **Invictus's own stale character IDs, now fixed in TI:**
  - `dhe_mithridates` and bloodlines `char:97` → 228 (Mithridates).
  - Alexander IV's ruler term 291 → 557.
  - Eumenes loc 408 → 431.
- **Restored definitions** that the merge lost or that Invictus deleted while content still uses them: trait `comradely`, TI heritage `ciusan_heritage`, and event picture `alis_ubbo_greek_soldiers`.
- **Invictus names mapped to TI's:** culture group `scythian_east` → `sarmatian_group`, culture `pyu` → `piaoyue`, and the Parthian march regions.
- **References to inventions and laws TI removed:** remapped where TI has an equivalent, otherwise neutralised.
- **Invasion events:** the pulses for TI-deleted `events/invasions.txt` are disabled.
- **Loc:**
  - Two murmur3 loc-key hash collisions are resolved.
  - Stale `CAS`/`MOB`/`MAN` names that would have mislabelled Invictus countries are removed.
  - Lost loc keys are restored.
- **`ti18_indiantxt` → `ti18_indian.txt`:** without the `.txt` extension, the game never loaded TI's Indian military traditions.

## 4. Validation

| Check | Result |
|---|---|
| Character identity (`audit_chars.py check`, 2,948 refs) | 0 references point at a different person. The 17 rows flagged are reviewed false positives: Invictus renamed the character (same birth date), or the row is a repair commit's own target. |
| Province refs (`check_integrity.py`) | 0 new undefined |
| Area/region refs | 0 new; 6 pre-existing TI region refs fixed |
| Duplicate character IDs | 0 |
| Brace balance | 0 new; 2 pre-existing fixed (plus Fezzan and religious inventions, fixed during review) |
| Every key/definition/event Invictus added since the last merge | Present in the merged tree: 15,807 loc keys, 4,537 definitions, 1,808 events |
| imperator-tiger (English loc) | Errors 1,954 → 1,942. Of 1,030 new findings, 947 also exist in Invictus 1.12 itself. 83 are merge-induced (63 warnings). The 3 remaining error types are listed under "Left as is" |
| Game boot | See section 6 |

## 5. Needs your judgement

1. **Kios (KIO) and the Mithridatid state (MIT) both exist.** TI kept KIO because it had edited it (culture/religion). Invictus replaced KIO with MIT. The other 7 kept culled countries (ARC, ORG, PTA, KAO, PYK, VRI, TEN) had similarly small TI tweaks.
2. **Low/medium-confidence province mappings used by Invictus content** are flagged in `reports/vendor_8dc22b2a78.csv`. They are mostly where TI redrew the land:
   - Burma: Myitnge, Mongmit, Bahmo, Tagaung (`form_pong` / `form_piaoyue`);
   - Nubia: Seiga, Shoshoba;
   - Sicily: Tissa → Centuripae;
   - the Cyrene desert.
3. **`himalayan_region` → `xiyu_region`.** By province count it splits 43 to Xiyu and 34 to Tibet. Used by Tayuan and Parthian content.
4. **Invictus work not carried over because TI deleted the files:**
   - `events/invasions.txt` (Invictus rewrote about 900 lines);
   - the Roman "Eastern Glory" missions;
   - the old Invictus military traditions.
5. **From the reviews:**
   - **Balance:**
     - `dictatorship_step_3` AI weight is now 0 (Invictus's).
     - Theatres can't be built: they require deleted `agressive_expansion_monthly_decay_inv_3` (pre-existing TI bug).
     - `pilum_inv` is undefined (pre-existing).
     - 12 inventions have no AI weight.
   - **Content:**
     - horde_conquest `conquer_cost` kept TI's 0 (base −0.1, Invictus 0.6).
     - TI's laws in `03_military.txt`/`04_naval.txt` lack Invictus 1.12's changes: maritime `num_of_port_building >= 1`, reform unlock `num_of_cities >= 25`, and the Carthage unlock.
     - Sparta's state-investment trigger fix.
     - Korkei (6912) produces wootz steel in TI but is targeted by the new gemstones decision.
   - **Military, religion and culture:**
     - TI has no `grain` trade good, but many missions use it (pre-existing, made worse by new Invictus content).
     - Invictus horses add light-cavalry discipline.
     - Invictus moved AI road building and AI state investment into scripts. Check that they cover TI-only areas such as China, and TI's extra investment buttons.
     - Invictus-style levies were added for new cultures.
     - `yuezhi` has no levy.
6. **TI's Indian military traditions now load for the first time** (the `ti18` rename). Please playtest Indian nations.
7. **Treasure 504** is TI's `treasure_turdetanian_bull`, whose loc is commented out in both mods. Invictus has `treasure_turdetanian_reliefs_iberic` there.

## 6. Game boot test
Both builds loaded the game; `error.log` from each run was compared with `errorlog_diff.py`, which ignores timestamps and line numbers. The merged run's log also covers a played session, so its runtime errors have no counterpart in the baseline run, which only reached the main menu. Results:
- **Pre-merge baseline:** 2,938 log lines. **Merged build:** 2,734.
- **New at setup, fixed in a follow-up commit:**
  - Two subjects with two overlords: DOD (EGY/KSH) and BMB. TI's subject relations win.
  - Defensive-league members with culled tags.
  - Treasure 59 owned twice. It stays with PTA.
  - A road between non-adjacent provinces (1873–1874).
- **Pre-existing in TI, not caused by the merge:**
  - **Hundred Schools deities fail to load.** `setup/main/deities/01_hundredschools.txt` fails to parse ("Unexpected token ﻿deity_manager"), so `deity:omen_suntzu` and `omen_confucius` don't resolve in TI's Chinese missions.
  - **Family lookups fail.** 113 failures before the merge, 98 after. TI reused Invictus family IDs: 10, 46, 47 and 304 were renamed, 82, 91–93 and 500 deleted, and TI's Chinese royal families sit on 1000–1006, which Invictus uses for its Galatian families. So `c:SPA.fam:Eurypontid`, `c:PAP.fam:Pylaemenid`, the Galatian families and others resolve to nothing.
  - **`cchinese_administration_laws`** is a typo in `02_countries.txt`.
  - **Two engine assertions,** `TagID < TAG_LIMIT` and `nIndex > -1`.
- **Probably from Invictus 1.12's own setup:** "Invalid Deity" messages for the new Invictus countries KOR, KOM, ZEL and MAN.

## Left as is
- `lepontic_colonia_scope_20_percent_svalue` is referenced only by Invictus loc. TI deleted the script value along with Invictus's Barbaricum mission values.
- `num_of_tribal_farm_building` / `num_of_tribal_mine_building` were already in TI's Fezzan and Albion missions before the merge.

## 7. Follow-ups after the merge
- **"Emperor of China" window:** the wars-overview button that opens it was shown to every player, and the window shows the player's own ruler (Egypt saw Ptolemaios). It's now limited to countries in the Mandate of Heaven system. This was a pre-existing TI bug.
- **Family IDs** (`fix_families.py`, `reports/fix_families.csv`). TI had reused Invictus family IDs:
  - 30 TI families (the Chinese, Korean and Japanese royal houses) moved +1000 to 2000–2029, with their country links updated.
  - Invictus's families came back at their own IDs:
    - Eurypontid (10), Ozbaalid (46) and Baalshillemi (47), where TI had renamed them;
    - Edescid (304) and Helladis (91) for Selge;
    - the Galatian families (1000–1006), where TI's Chinese houses had sat;
    - Teukrid (92), Orontids (93) and Pylaemenid (500), which were missing.
  - Their countries' `family =` links were restored.
  - Kios's link to the Mithridatid family (now Invictus's MIT) was removed.
  - Every `c:TAG.fam:Key` reference now resolves. The exceptions are 4 that are also broken or commented out in Invictus 1.12: Amyntid, Frataraka, Hannid and `al`.

## Upstream (Invictus) bugs found
These are worth reporting to Invictus. They're fixed in TI but still present in 1.12.0.1:
- `events/dhe/dhe_mithridates.txt` and `events/bloodlines_startup_events.txt` use `char:97` for Mithridates, who is now 228.
- In `setup/post_character/00_default.txt`, Alexander IV's `ruler_term` uses 291 (now Vakhsuvar); he is 557.
- In `antigonid_missions_events_l_english.yml`, the Eumenes reference uses 408 (now Diotimos); he is 431.
- `me_diadochi_empire.txt` references province 9768, and `me_patauion_02.txt` province 33595. Neither exists in Invictus.
