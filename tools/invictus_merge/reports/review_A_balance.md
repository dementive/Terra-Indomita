# Review A: balance files (inventions + buildings)

Batch: `common/inventions/00_{martial,civic,oratory,religious}_inventions.txt`, `common/buildings/00_default.txt`.
Input: 199 logged decisions (7 both-changed:kept-TI, 6 TI-changed-Invictus-deleted:kept-TI, 186 TI-deleted-Invictus-changed:kept-deleted).

Policy applied: keep TI features/reworks, merge INV fixes, content and balance where compatible, combine where both sides changed.

Format: `file | key | decision | reason`

## both-changed:kept-TI (7)

- buildings/00_default | aqueduct_building/modification_display/1 | kept TI | TI's `1 = local_country_civilization_value` already shows the civ value of TI's reworked aqueduct; INV's `value_civilization_cap` would duplicate it
- civic | civic_1/greek_advanced_mechanics_inv/allow/OR | kept TI | INV's only change was the tooltip key (latin -> hellenic), which TI's broader rework already uses
- oratory | oratory_2/dictatorship_step_2/on_activate/if | combined | kept TI's structure (applies to players too, ROM -> princeps_civitatis, everyone else -> republican_election_4) and added INV's `NOT = { has_law = ... }` guards so the law is not re-enacted when already active (also covers the two kept-deleted else_if rows)
- oratory | oratory_2/dictatorship_step_3/on_activate/if | kept TI | TI replaced the tiered stability penalty with a flat -15 at >85 stability; INV only softened the tier values that TI no longer has
- oratory | oratory_2/dictatorship_step_3/on_activate/hidden_effect | kept TI | both sides tuned the same civil-war size value (`subtract`, TI 1, INV 1.5); TI's deliberate larger civil war wins
- oratory | oratory_2/dictatorship_step_4/allow/OR | combined | kept TI's republic list and added INV's `government = punic_republic` (exists in the merged tree; Carthage could reach step 1/2 via TI's `is_republic` but not step 4)
- religious | religious_1/omen_power_inv_4/on_activate/if | combined | TI removed the hardcoded AI law swap; added INV's replacement `hidden_effect = { ai_choose_and_enact_law = yes }` (generic AI law chooser, already used by other merged inventions and ai_pulse)

## TI-changed-Invictus-deleted:kept-TI (6)

- buildings/00_default | fortress_ramparts_building/ai_will_do | took INV (removed) | INV replaced this vanilla leftover with a `chance` block (brc_fortress_ramparts), which the merge already added; every other building uses `chance`, so the old ai_will_do (TI x10 tweak) was dead/duplicate
- martial | martial_1/discipline_inv_5/on_activate/else_if | took INV (removed) | the merge kept INV's new `if = { is_tribal = no -> ai_choose_and_enact_law }` plus TI's old `else_if = { is_ai is_republic ... }`, which could never fire. TI's only change there was dropping the CAR branch. The AI law chooser handles marian_reforms, republican_recruitment_4 and standing_army_law
- martial | martial_1/draco_inv/allow/custom_tooltip | combined (fixed bad merge) | the merged allow had AND-ed TI's tooltip with INV's OR, so Dacian countries also had to have integrated Dacian culture plus haemic_science. Now INV's OR structure + INV's accurate loc key `integrated_any_dacia_group_culture` + TI's `any_country_culture { is_integrated = yes }` syntax
- martial | martial_1/werewolves_inv/allow/custom_tooltip | combined (fixed bad merge) | same as draco_inv
- religious | religious_1/happiness_for_wrong_group_modifier_inv_3/potential | combined | INV swapped the AI-hiding `trigger_if is_ai` in potential for `ai_will_do factor = 0` (already merged); dropped the redundant is_ai trigger and kept TI's `religious_tech >= 10`
- religious | religious_1/temple_estates_inv/allow | took INV (removed) | INV turned temple_estates_inv into a universal keystone that unlocks the Temple State feature (temple_state_event.2, temple_state_variable, grant_temple_state interaction). The merge took all of that, but TI's Anatolian-only allow would have kept the feature Anatolian-only. TI's edit to the allow had only changed the syntax

## TI-deleted-Invictus-changed:kept-deleted (186)

Breakdown of the 186 rows: 105 invention rows TI actually deleted, 63 invention rows TI only **moved** (other group or file), 1 `civic_2` group row (61 inventions: 45 moved into civic_1 or other files, 16 deleted), 12 `/ai_will_do` rows, 2 dictatorship_step_2 else_if rows and 3 building fields.

- all | 121 inventions TI deleted (105 rows + 16 in civic_2) | kept deleted | TI replaced them with its own tree. Nothing in the 4 invention files references them any more (see the orphan fix below). Other files that still reference some of them are listed under "outside this batch"
- all | 108 inventions TI moved (63 rows + 45 in civic_2) | restored INV change on TI's moved copy (102); kept TI's AI-weight deletion (1, ruler_popularity_gain_inv_1); no INV change to apply (5, all in civic_2) | The keyed merge matched inventions by group, so it read a moved invention as "TI deleted" and dropped INV's independent edits. INV's edits there were mostly a new `ai_will_do` (Invention Relative Chance system). Neither base nor TI had one, so it was inserted as-is into TI's copy, consistent with how the merge treated non-moved inventions. Done for 102 inventions: martial 21, civic 46, oratory 4, religious 31. Full list below
- religious | religious_1/ruler_popularity_gain_inv_1 (moved to oratory_2) | kept deleted | TI moved it and also deleted its ai_will_do, so this is a real TI deletion
- civic | police_baboon_inv (moved, was oratory_2) | combined | INV balance fix `global_unrest -0.5 -> -0.05` applied; TI's `global_monthly_state_loyalty 0.01` kept
- civic | greek_clock_mechanics_inv (moved, was civic_2) | combined | INV tooltip fix `integrated_any_latin_culture -> integrated_any_hellenic_culture` applied to TI's allow
- martial | falconry_inv (moved to military_inventions) | combined | INV bug fix applied: culture group OR integrated culture (base AND-ed them), loc key `integrated_any_thrace_group_culture`; TI's any_country_culture syntax kept
- martial | illyrian_helmet_inv (moved) | combined | INV loc key `integrated_any_illyrian_group_culture` applied; TI's helmet-exclusion NOR kept
- martial | sibyna_inv (moved) | combined | TI's tooltip said `integrated_any_hellenic_culture` while it checks Dacian, Illyrian and Thracian groups. INV changed the key too. Set it to `integrated_any_haemic_culture`, which matches TI's 3-group check
- civic+martial+religious | 10 Indian moved inventions (brahmi_script, cashmere_wool, cataract_surgery, crucible_steel, hindu_number_system, indigo_dye, toe_stirrup, trigonometric_functions, tube_drawn_technology, wootz_steel) | kept TI | INV switched the integration check from an is_culture list to culture_group checks. TI uses the is_culture list as its convention in about 20 of its own Indian inventions (all listed cultures exist), and 3 of these already have the group form. Left for the owner
- civic | polished_ceramics_invention, soap_invention (moved) | kept TI | TI deliberately reworked allow (MRY-only / no integration path); INV's allow edits do not apply
- civic | citizen_promotion_cost_modifier_inv (moved) on_activate | kept TI | TI removed the on_activate; INV only added an AI law call inside it
- martial/oratory/religious | 12 `/ai_will_do` rows (global_start_experience_inv_2/_3, cohort_reinforcement_speed_inv, experience_decay_inv_2, buy_military_tradition_inv, pirate_spawn_chance_inv_1, subject_loyalty_inv, happiness_for_wrong_group_modifier_inv_1/_2, stability_inv_2, global_unrest_inv_2, omen_power_inv_4) | kept deleted | TI removed the AI weight on reworked inventions. INV's IRC weight is tree-specific, so the inventions keep the default weight
- oratory | oratory_2/dictatorship_step_2/on_activate/else_if, else_if[1] | combined | TI's CAR/generic else_if removal kept; INV's has_law guards folded into TI's if/else (see above)
- buildings/00_default | population_building/local_monthly_food_modifier, latifundia_building/local_monthly_food_modifier, barracks_building/modification_display/2 | kept deleted | TI reworked granary, latifundia and barracks without these fields; INV's value tweaks do not apply

### Inventions that received INV's ai_will_do (moved by TI)

- martial (21): bitless_bridle_inv, falconry_inv, fort_maintenance_cost_inv, gallic_timbered_roads_inv, global_manpower_modifier_inv_1, global_manpower_modifier_inv_3, global_manpower_modifier_inv_5, greek_advanced_astronomy_inv_1, greek_advanced_astronomy_inv_2, greek_cartography_inv, illyrian_helmet_inv, indian_crucible_steel_inv, indian_toe_stirrup_inv, indian_wootz_steel_inv, italic_lituus_inv, land_morale_recovery_inv_1, land_morale_recovery_inv_3, land_morale_recovery_inv_5, naval_morale_recovery_inv_1, periplus_inv, sibyna_inv
- civic (46): alphabet_inv, assimilate_pop_cost_modifier_inv_1, build_cost_inv, citizen_promotion_cost_modifier_inv, cotton_trade_inv, global_building_slot_inv, global_citizen_output_inv_1, global_citizen_output_inv_4, global_citizen_output_inv_5, global_freemen_output_inv_1, global_freemen_output_inv_3, global_freemen_output_inv_4, global_freemen_output_inv_5, global_goods_from_slaves_inv, global_population_growth_inv_5, global_settlement_building_slot_inv, global_slaves_happyness_inv, global_slaves_output_inv_1..5, global_tribesmen_output_inv_1, global_tribesmen_output_inv_3, global_tribesmen_output_inv_4, greek_clock_mechanics_inv, greek_fire_hose_inv, greek_odometer_inv, greek_pyoulkos_inv, happiness_for_wrong_culture_modifier_inv_1, happiness_for_wrong_culture_modifier_inv_3, hillock_inv, imperial_aramaic_inv, indian_cashmere_wool_inv, indian_indigo_dye_inv, indian_trigonometric_functions_inv, italic_cursuspublicus_inv, monthly_governor_inv, move_pop_cost_modifier_inv, musnad_script_inv, oratory_tech_investment_inv_1, pahlavi_script_inv, police_baboon_inv, polished_ceramics_invention, polycentric_administration_inv, soap_invention
- oratory (4): global_unrest_inv_4, global_unrest_inv_5, monthly_corruption_inv, thracian_poetry_inv
- religious (31): beer_inv, brahmi_script_invention, canals_and_levees_inv, channeled_irrigation_invention, cosmetics_inv, cuneiform_inv, cured_ham_inv, cylinder_seals_inv, eternal_pyramids_inv, gallic_celtic_calendar_inv, gallic_celtic_plough_inv, global_tribesmen_output_inv_5, greek_epicureanism_inv, greek_stoicism_inv, hieroglyphs_inv, imperial_calendar_invention, indian_cataract_surgery_inv, indian_hindu_number_system_inv, indian_tube_drawn_technology_inv, ink_inv, kariz_inv, meroitic_script_inv, mint_toothpaste_inv, qunnabu_inv, research_points_modifier_inv_2, saqiya_inv, seeder_plough_inv, sexagesimal_inv, solar_calendar_inv, water_clock_inv, yakhchal_inv

## Orphans and pre-existing fixes

- oratory | oratory_1/royal_blemmyan_signature_inv (INV-new) | fixed orphan | it required `gw_effect_charisma_education_inv`, which TI deleted. Changed to `requires = { relation_inv_3 }`. In INV the chain is ae_impact_3 -> relation_inv_1 -> gw_charisma_education -> royal_blemmyan. TI's relation_inv_3 has the same modifier as INV's relation_inv_1 (`improve_relation_impact = 0.20`) and sits at the same depth after ae_impact_3, so the invention stays at the same depth
- other INV-new inventions (iron_club_inv, sporting_theft_inv, apiculture_inv, scapulimancy_inv, blemmyan_script_inv, advanced_ageing_inv, favomancy_inv, sambuca_inv) | kept as merged | requires point at existing TI inventions; cultures, loc keys and AI script values exist
- religious | end of file | fixed TI bug | TI's file never closed `religious_1 = {`: the last `}` was lost when the trailing chinese_philosophy_inv_1 block was commented out. No invention was nested wrongly, since every invention sat at depth 1. Added `}` at EOF, after the commented block. This has been in TI since at least commit 278e80578
- religious | channeled_irrigation_invention | fixed TI bug | it was defined twice in TI's religious_1 (ANU-only copy and an ANU-or-Lankan-Bharat copy). Removed the first, narrower copy; the second has the INV ai_will_do

## AI-weight script value check

Every `factor`, `value` and `min` identifier in the 4 invention files resolves to a script value in `common/script_values/*` (irc_/uct_/cdt_/cds_ from INV's ai_inventions_values.txt). The only exceptions are `civil_war_percent_svalue` (vanilla) and `country_culture_pop_count` (an engine trigger). All `brc_*` building factors resolve. The scripted triggers `should_not_waste_innovations` and `is_large_country_or_will_become_it` exist.

## Needs the owner's judgement

- oratory | dictatorship_step_3/ai_will_do | took INV via the AI-weight rule, not reviewed here | it is now `factor = 0` (INV: the AI takes step_4 instead). TI's old weight let large republics with a 9+ charisma ruler take the civil-war route. TI's step_4 is now always available to the AI (INV potential merged), so the AI goes to step_4
- buildings/00_default | theathre_building allow | pre-existing TI | requires `agressive_expansion_monthly_decay_inv_3`, which does not exist in TI, so theatres cannot be built. Pick a TI invention to unlock them
- martial | verutum_inv, soliferrum_inv, chakram_inv, sibyna_inv | pre-existing TI | NOR-reference `pilum_inv`, which is not defined (TI localisation for it exists)
- civic | global_tax_modifier_inv_3, research_points_modifier_inv_3, global_tax_modifier_inv_2 | pre-existing TI | they use the `integrated_any_latin_culture` tooltip for a hellenic check; INV fixed the same copy-paste in greek_clock_mechanics_inv
- the 12 TI-deleted ai_will_do inventions (listed above) have no AI weight; INV's IRC weights could be added if wanted
- Indian inventions: is_culture list vs INV's culture_group check (see above)

## Outside this batch (dangling invention references the merge introduced)

- events/mission_events/me_parthia.txt -> agressive_expansion_monthly_decay_inv_3
- events/mission_events/me_legia.txt -> lezgiwal_inv
- common/script_values/ai_inventions_values.txt -> global_start_experience_inv_4, global_start_experience_inv_5, silent_trade_inv, recruit_mercenary_inv
- common/scripted_triggers/ai_inventions_triggers.txt -> siege_engineers_inv_4
- common/scripted_triggers/ai_war_triggers.txt, common/character_interactions/merc_buyoff.txt -> recruit_mercenary_inv
- common/scripted_guis/release_subject_button.txt -> loosened_tributaries_inv
- (pre-existing in TI: great_work_effects -> gw_effect_*_inv / agressive_expansion_impact_inv_2 / global_defensive_inv_2; several missions; laws/12_slaves -> freemen_promotion_cost_modifier_inv; unit_abilities/port_assault -> archimedes_death_ray_inv)
