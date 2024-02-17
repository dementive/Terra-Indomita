"""
Run this script to fix merge errors with character setup for Indomita.
Before running:
1. Make sure to first copy the entire Invictus character setup into the mod and to have ALL TI characters in 000_indomita_characters.txt
2. Copy the Indomita characters from 00_hades.txt into the with the characters in "Tian_" at the top, "Elysium_" below them, and the rest at the bottom of 000_indomita_characters.txt.
"""
import os
import fnmatch
import re
from tqdm import tqdm


def do_replacement(content: str, blocks_map: dict, filepath: str):
    is_character_setup_file = "setup\\characters" in filepath
    is_localization_file = filepath.endswith(".yml")

    if is_localization_file:
        for i in blocks_map:
            current_key = i
            new_key = blocks_map[i]

            pattern = r"\[GetCharacter\('\(int32\){}'\)".format(current_key)
            replacement = f"[GetCharacter('(൝){new_key}')" # Mark finished replacements with "൝" character

            if re.search(pattern, content):
                # Replace [GetCharacter('(int32)X')] with [GetCharacter('(int32)Y')]
                content = re.sub(pattern, replacement, content)

        # Remove marker
        content = content.replace("൝", "int32")

    if not is_localization_file:
        for i in blocks_map:
            current_key = i
            new_key = blocks_map[i]

            pattern = r"{}\s?=\s?{{".format(current_key)
            replacement = (
                f"{new_key} = ഷ" 
            )
            pattern_2 = r"deify_ruler\s?=\s?{}".format(current_key)
            replacement_2 = f"deify_ruler ൝ {new_key}"  # Mark finished replacements with "൝" character

            if (
                is_character_setup_file
                and current_key in content
                and re.search(pattern, content)
            ):
                # Only replace the key if it is in a character setup file
                # Replace "X = {" with "Y = {"
                content = re.sub(pattern, replacement, content)

            if "deify_ruler" in content and re.search(pattern_2, content):
                # Replace "deify_ruler = X" with "deify_ruler = Y"
                content = re.sub(pattern_2, replacement_2, content)

            current_key = "char:" + current_key
            new_key = "ൠ:" + new_key

            if current_key in content:
                # Replace "char:X" with "char:Y"
                content = content.replace(current_key, new_key)

        # Remove markers
        content = content.replace("ഷ", "{")
        content = content.replace("൝", "=")
        content = content.replace("ൠ", "char")

    return content


def process_file(filepath: str, blocks_map: dict):
    with open(filepath, mode="r", encoding="utf-8") as file:
        file_contents = file.read()
        if any(key in file_contents for key in blocks_map.keys()):
            file_contents = do_replacement(file_contents, blocks_map, filepath)
    with open(filepath, mode="w", encoding="utf-8") as file:
        file.write(file_contents)


def main(directory: str, blocks_map: dict):
    EXCLUDED_DIRECTORIES = {
        "common\\achievements",
        "common\\ai_budget",
        "common\\ai_diplochance",
        "common\\coat_of_arms",
        "common\\combat_tactics",
        "common\\cultures",
        "common\\deathreasons",
        "common\\defines",
        "common\\deity_categories",
        "common\\diplomatic_stances",
        "common\\ethnicities",
        "common\\event_pictures",
        "common\\event_themes",
        "common\\faction_impact",
        "common\\genes",
        "common\\governor_policies",
        "common\\graphical_culture_types",
        "common\\great_work_categories",
        "common\\great_work_effects",
        "common\\great_work_materials",
        "common\\great_work_modules",
        "common\\great_work_templates",
        "common\\loyalty",
        "common\\modifier_icons",
        "common\\modifiers",
        "common\\named_colors",
        "common\\opinions",
        "common\\prices",
        "common\\province_names",
        "common\\subject_types",
        "common\\terrain_types",
        "common\\trade_goods",
        "common\\traits",
        "common\\unit_abilities",
        "common\\units",
        "setup\\countries",
        "setup\\post_character",
        "setup\\provinces",
        "Terra-Indomita\\content_source",
        "Terra-Indomita\\credits.txt",
        "Terra-Indomita\\gfx",
        "Terra-Indomita\\map_data",
        "Terra-Indomita\\music",
        "Terra-Indomita\\tools",
    }
    files_to_process = []
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, "*.txt"):
            full_path = os.path.join(path, filename)
            if any(s in full_path for s in EXCLUDED_DIRECTORIES):
                continue
            files_to_process.append(full_path)

        for filename in fnmatch.filter(files, "*.yml"):
            full_path = os.path.join(path, filename)
            files_to_process.append(full_path)

    for filepath in tqdm(files_to_process, desc="Processing files"):
        process_file(filepath, blocks_map)


def find_blocks(file_path: str):
    pattern = r"(\d+)\s?=\s?{"
    with open(file_path, "r", encoding="utf-8") as file:
        file_data = file.read()
    blocks = re.findall(pattern, file_data)
    return blocks


def get_blocks_map(mod_path: str):
    FIRST_FREE_ID = 515  # This should be the same as the first free ID listed in setup\character\000_READ_ME.txt of Invictus.
    file_path = mod_path + "setup\\characters\\000_indomita_characters.txt"
    blocks = find_blocks(file_path)

    blocks_map = {}
    for i in blocks:
        blocks_map[str(i)] = str(FIRST_FREE_ID)
        FIRST_FREE_ID += 1

    return blocks_map


if __name__ == "__main__":
    MOD_PATH = "C:\\Users\\demen\\Documents\\Paradox Interactive\\Imperator\\mod\\Terra-Indomita\\"
    main(MOD_PATH, get_blocks_map(MOD_PATH))
