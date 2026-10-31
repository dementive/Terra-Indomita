# Review C: military, religion and culture (merge decision review)

Columns: file | key | decision | reason

common/cultures/00_aksumite_group.txt | aksumite_group/culture/aksumite | combined | kept TI's `levy_template = levy_ethiopian`, added INV 1.12's new aksumite male/female/family name lists
common/cultures/00_bactrian.txt | bactrian/culture/yuezhi | kept TI (deleted) | TI moved yuezhi to 00_saka_g.txt; INV's `levy_sogdian` doesn't exist in TI (TI removed it)
common/deities/01_chinese_religions.txt | deity_chinese_sheshen/deity_category | kept TI | TI's Chinese pantheon uses TI's justice/wisdom deity categories (this file is TI-authoritative)
common/deities/01_chinese_religions.txt | deity_chinese_jishen/deity_category | kept TI | TI's Chinese pantheon uses TI's justice/wisdom deity categories (this file is TI-authoritative)
common/deities/01_chinese_religions.txt | deity_chinese_fengshi/deity_category | kept TI | TI's Chinese pantheon uses TI's justice/wisdom deity categories (this file is TI-authoritative)
common/deities/01_chinese_religions.txt | deity_chinese_daizong/trigger/owns | kept TI | TI 8480 = Bo (Mt Tai); INV's 10262 is Rybnitsa in TI's map, so the INV Chinese IDs were never translated
common/deities/01_chinese_religions.txt | deity_chinese_graangsreen/trigger/owns | kept TI | TI 9070 = Qian; INV's 11442 is Cyxt in TI's map (untranslated ID)
common/deities/01_chinese_religions.txt | deity_chinese_huashan/trigger/owns | kept TI | TI 8341 = Yinjin; INV's 10517 is Mare Lacadive (a sea tile) in TI's map
common/deities/01_chinese_religions.txt | deity_chinese_huashan/deity_category | kept TI | TI's Chinese pantheon uses TI's justice/wisdom deity categories (this file is TI-authoritative)
common/deities/01_chinese_religions.txt | deity_chinese_gyyngsreen/trigger/owns | kept TI | TI 8689 = Shangquyang; INV's 10479 is Kob Dehad in TI's map
common/deities/01_chinese_religions.txt | deity_chinese_songshan/trigger/owns | kept TI | TI 8400 = Yangcheng; INV's 10182 is Merla in TI's map
common/deities/01_chinese_religions.txt | deity_chinese_xihe/deity_category | kept TI | TI's Chinese pantheon uses TI's justice/wisdom deity categories (this file is TI-authoritative)
common/deities/01_chinese_religions.txt | deity_chinese_xiangjun/trigger/OR | kept TI | TI 9018-9030 = Changsha..Quanling (Xiang river); INV's 11390-11402 are Lanyar/Vaca etc. in TI's map
common/deities/01_chinese_religions.txt | deity_chinese_xiangfuren/trigger/OR | kept TI | same as xiangjun: TI's IDs are the correct Xiang river provinces
common/deities/01_nhialic.txt | deity_buk/on_activate/current_ruler | took INV | INV folded this into `lustful_fertility_apotheosis_effect` (capital harvest effect + force_add_trait lustful). TI's add_trait was a 2023 fix of an invalid effect. The auto-merge had left both and dropped the capital effect
common/levy_templates/01_bactrian.txt | levy_bactrian/archers | kept TI | TI recomposed this template (different unit mix); INV's value tweak targets the old composition
common/levy_templates/01_bactrian.txt | levy_bactrian/heavy_cavalry | kept TI | TI recomposed this template (different unit mix); INV's value tweak targets the old composition
common/levy_templates/01_bactrian.txt | levy_bactrian/light_infantry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_bactrian.txt | levy_central_asia/light_infantry | kept TI | TI recomposed this template (different unit mix); INV's value tweak targets the old composition
common/levy_templates/01_bactrian.txt | levy_central_asia/camels | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_bactrian.txt | levy_central_asia/archers | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_chinese.txt | levy_qin/archers | kept TI | TI's Chinese levies are authoritative. Also removed INV's spearmen 0.35 and light_infantry 0.25, which the merge had grafted on (sum 1.6, pikemen plus spearmen)
common/levy_templates/01_chinese.txt | levy_qin/chariots | kept TI | TI's Chinese levies are authoritative (see levy_qin/archers)
common/levy_templates/01_dacians.txt | levy_dacians/archers | kept TI | TI recomposed it (axemen/archers/LC/spearmen). Also removed INV's heavy_infantry 0.2, which the merge had grafted on (sum 1.2)
common/levy_templates/01_dacians.txt | levy_dacians/light_infantry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_dacians.txt | levy_thracians/heavy_infantry | kept TI | 0.3 belongs to TI's spearmen-based recomposition; INV's 0.2 is part of its light-infantry-heavy mix
common/levy_templates/01_hellenic.txt | levy_cretan/archers | kept TI | TI recomposed this template (different unit mix); INV's value tweak targets the old composition
common/levy_templates/01_hellenic.txt | levy_cretan/light_infantry | kept TI | TI recomposed this template (different unit mix); INV's value tweak targets the old composition
common/levy_templates/01_hellenic.txt | levy_cretan/heavy_infantry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_macedonian/spearmen | kept TI (deleted) | TI uses pikemen for the Macedonian levy
common/levy_templates/01_hellenic.txt | levy_macedonian/heavy_infantry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_magna_graecia/spearmen | kept TI | TI recomposed this template (different unit mix); INV's value tweak targets the old composition
common/levy_templates/01_hellenic.txt | levy_magna_graecia/heavy_cavalry | kept TI (deleted) | TI uses slingers/horse_skirmishers here
common/levy_templates/01_hellenic.txt | levy_magna_graecia/light_cavalry | kept TI (deleted) | TI uses horse_skirmishers here
common/levy_templates/01_hellenic.txt | levy_magna_graecia/heavy_infantry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_spartan/spearmen | kept TI | TI's hoplite-heavy design (spearmen 0.6, LI, LC)
common/levy_templates/01_hellenic.txt | levy_spartan/heavy_cavalry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_spartan/heavy_infantry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_argolis/light_infantry | kept TI | TI recomposed this template (different unit mix); INV's value tweak targets the old composition
common/levy_templates/01_hellenic.txt | levy_argolis/light_cavalry | kept TI | TI's 0.2. Also reverted spearmen 0.35 to TI's 0.4: the merge had applied INV's one-sided tweak to TI's recomposed template
common/levy_templates/01_hellenic.txt | levy_argolis/heavy_infantry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_thessalian/heavy_infantry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_thessalian/light_cavalry | kept TI (deleted) | TI uses horse_skirmishers here
common/levy_templates/01_hellenic.txt | levy_cyrene/light_infantry | kept TI | TI recomposed this template (different unit mix); INV's value tweak targets the old composition
common/levy_templates/01_hellenic.txt | levy_cyrene/heavy_infantry | kept TI | TI's 0.3. Also removed INV's light_cavalry 0.25, which the merge had grafted onto TI's camel-based template (sum 1.25)
common/levy_templates/01_hellenic.txt | levy_cyrene/heavy_cavalry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_cyrene/spearmen | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_bosporan_greek/light_cavalry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_bosporan_greek/heavy_infantry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_epirotes/light_infantry | kept TI | TI recomposed this template (different unit mix); INV's value tweak targets the old composition
common/levy_templates/01_hellenic.txt | levy_epirotes/spearmen | kept TI (deleted) | TI uses pikemen for Epirus
common/levy_templates/01_hellenic.txt | levy_epirotes/heavy_infantry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_hellenic.txt | levy_enetoi | restored | culture `enetoian` (common/cultures/00_hellenic.txt, also in TI HEAD) uses `levy_template = levy_enetoi`, but TI's levy file never defined it. Restored INV 1.12's version
common/levy_templates/01_iranian.txt | levy_carmanian/horse_archers | kept TI | TI recomposed this template (different unit mix); INV's value tweak targets the old composition
common/levy_templates/01_iranian.txt | levy_carmanian/light_cavalry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/levy_templates/01_scythosarmatian.txt | levy_steppes_east/camels | kept TI | TI keeps camels 0.2 with spearmen. Also removed INV's heavy_cavalry 0.3, which the merge had grafted on (sum 1.3)
common/levy_templates/01_scythosarmatian.txt | levy_steppes_east/light_cavalry | kept TI (deleted) | TI dropped this unit from its recomposed template; only the field was removed, nothing references it
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_military/is_valid/trigger_if | kept TI | TI's `exists = root` guard kept; INV has no equivalent
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_military/is_valid/trigger_if[1] | took INV | price and in-progress checks now come from INV's `invest_in_state_button_is_valid` scripted trigger (same logic plus add_scaling_gold_cost_trigger); removed the duplicate copy the auto-merge had left next to it
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_civic/is_valid/trigger_if | kept TI | TI's `exists = root` guard kept; INV has no equivalent
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_civic/is_valid/trigger_if[1] | took INV | price and in-progress checks now come from INV's `invest_in_state_button_is_valid` scripted trigger (same logic plus add_scaling_gold_cost_trigger); removed the duplicate copy the auto-merge had left next to it
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_oratory/is_valid/trigger_if | kept TI | TI's `exists = root` guard kept; INV has no equivalent
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_oratory/is_valid/trigger_if[1] | took INV | price and in-progress checks now come from INV's `invest_in_state_button_is_valid` scripted trigger (same logic plus add_scaling_gold_cost_trigger); removed the duplicate copy the auto-merge had left next to it
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_religious/is_valid/trigger_if | kept TI | TI's `exists = root` guard kept; INV has no equivalent
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_religious/is_valid/trigger_if[1] | took INV | price and in-progress checks now come from INV's `invest_in_state_button_is_valid` scripted trigger (same logic plus add_scaling_gold_cost_trigger); removed the duplicate copy the auto-merge had left next to it
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_military_SPA/is_valid/trigger_if | kept TI | TI's `exists = root` guard kept; INV has no equivalent
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_military_SPA/is_valid/trigger_if[1] | took INV | price and in-progress checks now come from INV's `invest_in_state_button_is_valid` scripted trigger (same logic plus add_scaling_gold_cost_trigger); removed the duplicate copy the auto-merge had left next to it
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_religious_SPA/is_valid/trigger_if | kept TI | TI's `exists = root` guard kept; INV has no equivalent
common/scripted_guis/invest_in_state_buttons.txt | invest_in_state_button_religious_SPA/is_valid/trigger_if[1] | took INV | price and in-progress checks now come from INV's `invest_in_state_button_is_valid` scripted trigger (same logic plus add_scaling_gold_cost_trigger); removed the duplicate copy the auto-merge had left next to it
common/trade_goods/00_default.txt | grain | kept TI (deleted) | TI blanks 00_default.txt and uses its own goods economy (00_TI_goods.txt, no grain). Restoring it would undo that design. Many `grain` references already existed in TI HEAD (owner note)
common/trade_goods/00_default.txt | horses | kept TI (deleted) | TI defines horses in 00_TI_goods.txt (outside this batch). INV's added light_cavalry_discipline 0.1 is flagged for the owner
common/trade_goods/00_default.txt | leather | kept TI (deleted) | TI's 00_TI_goods.txt leather is reworked (LI/slinger/archer defence); INV's spearmen_defensive tweak doesn't apply
common/trade_goods/00_default.txt | glass | kept TI (deleted) | TI's 00_TI_goods.txt already has country_civilization_value = 4 (same as INV's new value)
common/trade_goods/00_default.txt | silphium | kept TI (deleted) | TI's 00_TI_goods.txt silphium is reworked (civilization/omen); INV's civ value tweak doesn't apply
common/unit_abilities/drill_army.txt | drill_army/allow/trigger_if | took INV | INV's mercenary-training exception (legion still required for non-mercs). TI's file was the pre-change INV copy. The merged invention `mercenary_maintenance_cost_inv` sets `unlock_mercenary_training_var` and its loc/laws exist
common/unit_abilities/drill_army.txt | drill_army/ai_will_revoke/OR | took INV | months_to_war < 8 matches INV's ai_will_do tweaks already merged (treasury 40, manpower 6). TI's 12 was the old INV/vanilla value, not a TI rework
common/unit_abilities/military_colonies.txt | military_colonies/allow/unit_owner | kept TI | TI's design gates colonies on the `alexander_legacy` variable. In TI, bactrian_path_14 is a different bonus (it sits after bactria_alexander, which already sets the variable). INV's additions to `hidden` stay
common/unit_abilities/raze.txt | raze_city/start_effect/unit_location | took INV | added INV's `razed_count` province counter; INV's androphagia script values (00_mission_androphagia.txt), now in the merged tree, read it. The file now matches INV
common/unit_abilities/road_building.txt | road_building/hidden | kept TI (deleted) | TI deliberately opened road building to everyone (civic_tech > 4 or the expensive price); INV's hidden would restrict it to Latin/Roman
common/unit_abilities/root_out_pirates.txt | root_out_pirates/allow/unit_owner | combined | kept TI's naval-law variable gate and added INV's `bosporan_antipiracy_mod` alternative (the Bosporan mission promises enables_root_out_pirates_tt). TI's limitless trigger_if became an OR
common/unit_abilities/settle.txt | settle/allow/trigger_if | kept TI | index mismatch only. TI's allow is INV's allow plus TI's is_being_colonized check, and the AI trigger_if is identical
common/unit_abilities/settle.txt | settle/start_effect/if | combined | kept TI's blocks and added INV's androphagia amber block (deps exist: androphagian.41, venedia/hyperborea regions, amber, inv_randomness_value). Removed the duplicate set_conquered_by block the merge had inserted
common/unit_abilities/settle.txt | settle/start_effect/if[1] | kept TI | iron-man achievement block is identical on both sides (index shift only)
common/unit_abilities/unit_recovery.txt | unit_recovery/ai_will_revoke/OR | took INV | pairs with INV's ai_will_do, which was already merged (revoke at morale >= 0.8, or out of war). TI's block was the old vanilla AI; gameplay modifiers are identical. The file now matches INV

## Extra fixes in batch files (outside logged keys)

common/levy_templates/01_chinese.txt | levy_qin | kept TI | removed INV spearmen/light_infantry grafted onto TI's template
common/levy_templates/01_dacians.txt | levy_dacians/heavy_infantry | kept TI | removed INV field grafted onto TI's recomposed template
common/levy_templates/01_hellenic.txt | levy_argolis/spearmen | kept TI | reverted 0.35 to TI's 0.4
common/levy_templates/01_hellenic.txt | levy_cyrene/light_cavalry | kept TI | removed INV field grafted onto TI's template
common/levy_templates/01_scythosarmatian.txt | levy_steppes_east/heavy_cavalry | kept TI | removed INV field grafted onto TI's template
common/scripted_guis/invest_in_state_buttons.txt | 6 vanilla buttons | combined | is_valid is now TI guard + INV scripted trigger; INV's ai_is_valid = no and the shared effect were already merged (AI investing moved to INV's ai_pulse `ai_choose_and_make_investment`). TI's admin/manpower/academic/civ buttons unchanged
common/unit_abilities/settle.txt | start_effect | combined | removed the duplicate set_conquered_by `if` block

Counts: combined=3, kept TI=39, kept TI (deleted)=30, restored=1, took INV=11
