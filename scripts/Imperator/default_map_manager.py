import re
from pathlib import Path

"""
    Autogenerate impassable and sea lists for default.map with the province setup folder as input
"""

def get_provinces_in_file(filename):
    with open(filename, 'r', encoding="utf-8-sig") as file:
        text = file.read()

    provinces = re.findall(r'(\d+)=\{(.+?)\n\}', text, re.DOTALL)
    provs = list()
    sea_provs = list()

    for i in provinces:
        pid = i[0]
        p_data = i[1]
        if '"impassable_terrain"' in p_data:
            provs.append(pid)
        if '"riverine_terrain"' in p_data or '"coastal_terrain"' in p_data or '"ocean"' in p_data:
            sea_provs.append(pid)
    return (provs, sea_provs)

def write_list(li, name, comment):
    if len(li) < 1:
        return
    with open(f"{name}.txt", 'a', encoding="utf-8-sig") as file:
        file.write(f"# {comment}\n")
        file.write(f"{name} = LIST {{ ")
        for i in li:
            file.write(f"{i} ")
        file.write("}\n")

def add_new_region_file(file):
    impassable_ids, sea_ids = get_provinces_in_file(file)
    comment = file.name
    write_list(impassable_ids, "impassable_terrain", comment)
    write_list(sea_ids, "sea_zones", comment)

if __name__ == '__main__':
    path_to_province_setup = "C:\\Users\\demen\\Documents\\Paradox Interactive\\Imperator\\mod\\Chronicles-of-Omniluxia\\setup\\provinces"
    for file in Path(path_to_province_setup).iterdir():
        add_new_region_file(file)
