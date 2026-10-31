# Review B: gameplay content (Invictus 1.12 merge)

Covers the 95 logged decisions in `review_B_content.csv`. Format: `file | key | decision | reason`.
Decision types: kept TI / took INV / combined / restored.

## Decisions

events/mission_events/1.3 - Punic Wars/me_roman_9_eastern_glory.txt | me_roman_9_eastern_glory.5/option | combined | Took the INV rework (state-capital legion check, 3 new eastern regions, every_province split, loyalty < 66 + remove_all_offices, p:1.owner). Kept TI's bohemia_region because bohemia_area does not exist on the TI map.
events/mission_events/me_fezzani.txt | me_fezzani.303/option | took INV | Switched to INV's delayed founding (founding_city_in_progress + state_improvement.6 after 730 days). TI's set_city_status was legacy code, not a TI redesign. Kept p:9962.
events/mission_events/me_fezzani.txt | me_fezzani.402/option | took INV | Same delayed-founding change on p:10027.
events/mission_events/me_tasm.txt | me_tasm.30/option | took INV | TI's p:8829/8830/8832/8833 are Chinese provinces (Shangyong, Fangling and others) on the current map. INV's 11211-11216 are the Yamama provinces, including the new 11216.
events/warfare_events.txt | warfare.1/option | kept TI | TI's Japan AI-chance modifier is the only difference (add/add file, no base).
events/warfare_events.txt | warfare.1/option[1] | combined | Kept TI's Japan-AI trigger and migration_age_looting_effect. Took INV's commenting-out of the colossus branch, since dhe_colossus_of_rhodes.13 is commented out in the merged tree.
events/warfare_events.txt | warfare.1/option[2] | combined | Kept TI's trigger and migration effect. Took INV's `number_of_personality_traits > max_number_of_traits_svalue` and the colossus removal.
events/warfare_events.txt | warfare.1/option[3] | combined | Kept TI's migration effect. Took INV's trait-count fix and the colossus removal, and now fire distinction.22 (a country_event) on the employer.
events/warfare_events.txt | warfare.3/immediate | took INV | Saves scope mercenary_to_bribe, which ai_should_counter_bribe_mercenary needs.
events/warfare_events.txt | warfare.3/option | took INV | TI's AI weight read local_var:merc_payoff_value, which nothing in the merged tree sets any more. Now uses ai_should_counter_bribe_mercenary.
events/warfare_events.txt | warfare.3/option[1] | took INV | Same as above.
events/warfare_events.txt | warfare.7/immediate | took INV | distinction.25 is a country_event, so it is now fired in employer scope.
decisions/master_dharana.txt | country_decisions/master_dharana/potential | combined | Kept TI's charvaka and added INV's Parthia-mission Buddhist-ruler clause (parthia_missions_123 exists).
decisions/master_dhyana.txt | country_decisions/master_dhyana/potential | combined | Same as master_dharana.
decisions/master_samadhi.txt | country_decisions/master_samadhi/potential | combined | Same as master_dharana.
decisions/trade_good_decisions.txt | country_decisions/amber_province_decision_1/potential | combined | Uses TI's global variable and `owns`, with INV's renumbering Korkei -> Vorganium (2151). Before the fix the working tree mixed TI fields (6912) and INV fields (2151).
decisions/trade_good_decisions.txt | country_decisions/amber_province_decision_1/effect | combined | Uses TI's set_global_variable with p:2151 and vorganium_amber_mod. korkei_amber_mod does not exist, and Korkei is wootz_steel in TI.
decisions/trade_good_decisions.txt | country_decisions/amber_province_decision_2/potential | combined | Uses TI's global variable and `owns`, with INV's Vorganium -> Rugia (4750) (matches the decision_2 loc).
decisions/trade_good_decisions.txt | country_decisions/amber_province_decision_2/effect | combined | Uses TI's set_global_variable with p:4750 and rugia_amber_mod.
decisions/trade_good_decisions.txt | country_decisions/amber_province_decision_3 | took INV (deleted) | After the renumbering it duplicated Rugia (decision_2), had no loc, and nothing references it.
common/character_interactions/propose_marriage.txt | propose_marriage/potential_trigger/scope:actor | kept TI | TI deliberately removed the monarchy-only restriction (see the file header).
common/character_interactions/propose_marriage.txt | propose_marriage/allowed_trigger/hidden:scope:actor | kept TI | Same as above.
common/character_interactions/propose_marriage.txt | propose_marriage/allowed_trigger/hidden:scope:target.employer | kept TI | Same as above.
common/character_interactions/propose_marriage.txt | propose_marriage/allowed_trigger/scope:target | combined | Added INV's `prisoner = no` and `is_mercenary = no` to TI's block.
common/character_interactions/propose_marriage.txt | propose_marriage/allowed_trigger/trigger_if | combined | Added INV's prisoner and mercenary guards to the candidate checks.
common/character_interactions/propose_marriage.txt | propose_marriage/allowed_trigger/trigger_else | combined | Same as trigger_if.
common/laws/00_monarchy.txt | monarchy_military_reforms | kept deleted | TI blanked this file and keeps a reworked copy in common/laws/03_military.txt. INV's value changes are listed for the owner below.
common/laws/00_monarchy.txt | monarchy_maritime_laws | kept deleted | Reworked copy lives in common/laws/04_naval.txt.
common/laws/00_republic.txt | republic_military_recruitment_laws | kept deleted | Reworked copy lives in 03_military.txt.
common/laws/00_republic.txt | republic_military_recruitment_car_laws | kept deleted | Reworked copy lives in 03_military.txt.
common/laws/00_republic.txt | republican_mediterranean_laws | kept deleted | Reworked copy lives in 04_naval.txt.
common/laws/00_republic.txt | republican_mediterranean_car_laws | kept deleted | Reworked copy lives in 04_naval.txt.
common/missions/01_Albion_missions.txt | albion_mission/albion_main_mission_7_5/allow | combined | INV's albion_main_mission_7_5tt custom_tooltip wrapper plus TI's tribal foundry and tribal mine alternatives.
common/missions/01_Albion_missions.txt | albion_mission/albion_main_mission_8_11/allow | combined | INV's omen_brigantia requirements (has_this_omen, is_holy_site_of_deity) plus TI's tribal sacred-building alternative.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_17 | restored | Not really deleted. TI's task_15 allow was missing a `}`, so every later task was nested inside task_15. Fixed the brace and took INV's `potential = has_variable = was_GAR`.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_101 | restored | Brace fix, then took INV's potential `tag = PSY` -> `has_variable = was_PSY` (on_start sets the was_X variables).
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_102 | restored | Brace fix, then took INV's was_PSY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_103 | restored | Brace fix. Combined TI's tribal-farm alternative with INV's was_PSY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_104 | restored | Brace fix, then took INV's was_PSY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_105 | restored | Brace fix, then took INV: was_PSY potential, allow simplified to `owns = 3338` plus `treasury >= 65`, set_owned_by dropped from the tooltip.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_106 | restored | Brace fix. Combined TI's tribal-farm alternative with INV's was_PSY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_107 | restored | Brace fix, then took INV's was_PSY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_108 | restored | Brace fix, then took INV's was_PSY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_109 | restored | Brace fix, then took INV's was_PSY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_110 | restored | Brace fix, then took INV's was_PSY potential and requires (task_114 dropped).
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_111 | restored | Brace fix, then took INV's was_PSY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_113 | restored | Brace fix, then took INV's was_PSY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_114 | restored | Brace fix, then took INV's was_PSY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_201 | restored | Brace fix, then took INV's was_NAS potential (on_start sets was_NAS for tag NSM).
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_202 | restored | Brace fix, then took INV's was_NAS potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_203 | restored | Brace fix, then took INV's was_NAS potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_204 | restored | Brace fix. Combined TI's soda_area and tribal-farm changes with INV's was_NAS potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_205 | restored | Brace fix. Combined TI's soda_area with INV's was_NAS potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_206 | restored | Brace fix. Combined TI's p:9972 requirement and tribal alternatives with INV's was_NAS/was_PHZ potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_207 | restored | Brace fix, then took INV's was_NAS potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_208 | restored | Brace fix, then took INV's was_NAS potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_209 | restored | Brace fix, then took INV's was_NAS potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_302 | restored | Brace fix, then took INV's was_MHY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_303 | restored | Brace fix. Combined TI's tribal alternatives with INV's was_MHY potential. The tooltip now shows the founding modifier, matching the me_fezzani.303 change.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_304 | restored | Brace fix, then took INV's was_MHY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_305 | restored | Brace fix. Combined TI's tribal alternatives with INV's was_ variables, and wrapped the potential in `OR` (both TI and INV had an AND of two exclusive vars, so it was never true).
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_306 | restored | Brace fix, then took INV's was_MHY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_307 | restored | Brace fix. Combined TI's soda_area with INV's was_MHY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_308 | restored | Brace fix. Combined TI's soda_area with INV's was_MHY potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_401 | restored | Brace fix, then took INV's was_MKA potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_402 | restored | Brace fix. Combined TI's tribal alternatives with INV's was_MKA potential. The tooltip now shows the founding modifier, matching the me_fezzani.402 change.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_403 | restored | Brace fix, then took INV's was_MKA potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_404 | restored | Brace fix, then took INV's was_MKA potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_405 | restored | Brace fix, then took INV's was_MKA potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_406 | restored | Brace fix. Combined TI's soda_area with INV's was_MKA potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_407 | restored | Brace fix. Combined TI's soda_area with INV's was_MKA potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_501 | restored | Brace fix, then took INV's was_PHZ potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_502 | restored | Brace fix, then took INV's was_PHZ potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_503 | restored | Brace fix, then took INV's was_PHZ potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_504 | restored | Brace fix, then took INV's was_PHZ potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_505 | restored | Brace fix, then took INV's was_PHZ potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_506 | restored | Brace fix, then took INV's was_PHZ potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_507 | restored | Brace fix. Combined TI's soda_area with INV's was_PHZ potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_508 | restored | Brace fix. Combined TI's soda_area and tribal-farm changes with INV's was_PHZ potential.
common/missions/02_fezzani_missions_01.txt | fezzani_mission_01/fezzani_mission_01_task_20 | restored | Brace fix. Took INV's was_X potential. Kept TI's allow (owns_region = fezzan_region) and TI's on_completion; INV's has_formed_fezzan check sat inside the tooltip TI replaced.
common/missions/02_vandalia_lugia_form.txt | barbaricum_vandalia_lugia_mission/barbaricum_vandalia_lugia_mission_task_5/allow | combined | INV's vandal_boihaemian_relations_tt custom_tooltip wrapper plus TI's region:bohemia_region.
common/missions/02_vandalia_lugia_form.txt | barbaricum_vandalia_lugia_mission/barbaricum_vandalia_lugia_mission_task_8/on_completion | combined | Took INV's structure (fires flavor_germanics.46, Lugus tooltip, show_as_tooltip, capital formable effects) and kept TI's bohemia_region in the tooltip.
common/missions/02_vandalia_lugia_form.txt | barbaricum_vandalia_lugia_mission/barbaricum_vandalia_lugia_mission_task_12/on_completion | combined | Took INV's structure (fires flavor_germanics.50, show_as_tooltip) and kept TI's bohemia_region.
common/missions/02_zhangzhung_missions.txt | 01_zhangzhung_missions/01_zhangzhung_missions_task_16/on_completion | combined | Kept TI's PI/treasury deduction to match TI's allow. Took INV's delayed city founding and restored the +1 finesse that the me_zhangzhung.16 tooltip promises.
common/modifiers/00_from_missions_adriatic_pirate.txt | corrupt_pirate_den | kept TI | Unreferenced in both TI and the merged tree. Harmless dead definition the owner may delete.
common/modifiers/02_from_missions_icenia.txt | iron_weapons_icenia | kept TI | Unreferenced (dead definition); harmless.
common/modifiers/02_invictus_random_modifiers.txt | paradisial_gardens_modifier | kept TI | Unreferenced (dead definition); harmless.
common/on_action/00_ambitions_inv.txt | scheme_exploit_populous_start/effect/random_holdings | combined | Kept TI's limit (metropolises allowed) and took INV's scope name exploiting_holding. The finish on_action and the 01_schemes_inv.txt abort use scope:exploiting_holding, so TI's name broke the scheme.
common/on_action/00_ambitions_inv.txt | ambition_grow_up | kept deleted | TI removed it during its Jan-2025 upstream merge. Nothing references the on_action; has_ambition = ambition_grow_up in customizable loc refers to the ambition, not the on_action.
common/on_action/00_monthly_country.txt | monthly_country_pulse/events/#values | combined | TI's list (no punic_resurgence) plus INV's me_turdetania_2_heirs_tartessia.65. Also repaired random_events: the merge had dropped the null-weight line. Now `635 = 0` and comet.4, with TI's punic removal kept; INV moved the germanic/gaul flavor events to main_event_pulse_country.txt.
common/scripted_triggers/00_missions.txt | state_improvement_military_trigger | kept deleted | TI defines it in common/scripted_triggers/province_investment_triggers.txt (TI rework), so a copy here would be a duplicate. INV's SPA fix is listed for the owner below.
common/scripted_triggers/00_missions.txt | state_improvement_civic_trigger | kept deleted | Same; TI's definition is in province_investment_triggers.txt.
common/scripted_triggers/00_trait_groups_inv_1_0.txt | has_bloodline_trigger/OR/has_trait[62] | combined | Added INV's hecatomnid next to TI's East Asian bloodlines.
common/scripted_triggers/00_trait_groups_inv_1_0.txt | has_bloodline_trigger/OR/has_trait[63] | combined | Added INV's oxyartid. INV's pylaemenes -> shaushtatar duplicate fix was already merged.
common/wargoals/00_default_inv.txt | horde_conquest/attacker/conquer_cost | kept TI | Both sides changed one number (base -0.1, TI 0, INV 0.6). Kept TI's value and flagged it for the owner.

## Extra edits in batch files (outside the logged keys)

common/missions/02_fezzani_missions_01.txt | task_15 allow | fixed | Added the missing `}` after the `or` block (TI commit 9e2b26d47 "hmmmmm"). TI's own pre-merge file was unbalanced (1 0); it is now 0 0.
decisions/trade_good_decisions.txt | gemstones_province_decision_4, wine_province_decision_1 | combined | New INV decisions now use TI's once-per-world pattern (has_global_variable/set_global_variable and `owns`), like the other 65 trade-good decisions.

## For the mod owner

- **bohemia_area:** the region does not exist on the TI map; TI's region is bohemia_region. The coordinator's region rename pass has since fixed most uses. When this review finished, the only file still using it was common/scripted_effects/00_parthia_march_effect.txt (lines 367, 450, 534, 802), which is outside this batch. Lines 534 and 802 also build names and loc keys from it (`WHICH = bohemia_area`, `bohemia_area_march_F`), so check the loc before renaming.
- **horde_conquest attacker conquer_cost:** TI 0 vs INV 0.6.
- **Laws:** TI's relocated laws in 03_military.txt and 04_naval.txt lack INV 1.12's changes. INV changed:
  - maritime law allow from `is_port = yes` to `num_of_port_building >= 1`
  - `rank >= regional_power` to `num_of_cities >= 25` on reform unlocks
  - Carthage reform unlock from `rank >= great_power` to major_power OR had_military_reforms
  - allow_mercenary_training tooltips, plus several value tweaks

  Port these if wanted.
- **state_improvement SPA fix:** INV 1.12 notes that state_improvement_military_SPA is really the civic modifier, and moved its check from the military trigger to the civic trigger. TI's copies in province_investment_triggers.txt still list it under military.
- **Korkei (6912) gemstones decision:** INV's new gemstones_province_decision_4 targets Korkei, which is wootz_steel on the TI map. It works mechanically but may be thematically wrong.
- **punic_resurgence events:** .10/.11/.13/.16/.18 exist but TI has never fired them (removed from the monthly pulse since 2022). I kept them unfired.
- **Fezzan task_105 and city founding:** task_105 now requires owning p:3338 plus 65 treasury (INV). Fezzani and Zhangzhung city founding now take 2 years (INV mechanic).
