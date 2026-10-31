"""Build maps/tags.csv and maps/areas_regions.csv (Invictus name -> Terra-Indomita name).

Tags: Invictus tags whose meaning differs in TI. TI re-hosted Invictus's versions of tags it reused
under its own tags (e.g. Amantinia AMA -> X16), so those map by country file; tags that are new in
Invictus but already taken in TI get fresh tags (FRESH_TAGS).

Areas/regions: every Invictus area/region name referenced by content but missing in TI maps to the
TI area/region that holds most of its provinces (through maps/provinces.csv).

Usage: python build_name_maps.py <inv_ref> <ti_ref>
"""
import csv
import os
import re
import sys
from collections import Counter

from gitio import decode, show
from mapdata import parse_areas, parse_regions

HERE = os.path.dirname(__file__)
# Invictus tags that collide with a different TI country and have no TI equivalent: give them new tags
FRESH_TAGS = {"SIC": "SYC", "ELY": "ELS"}  # Sicyon, Elesycia


def country_files(ref):
    text, _, _ = decode(show(ref, "setup/countries/countries.txt"))
    text = re.sub(r"#[^\n]*", "", text)
    return {m.group(1): m.group(2) for m in re.finditer(r'^\s*([A-Z0-9]{3})\s*=\s*"([^"]+)"', text, re.M)}


def load_province_map(name="provinces.csv"):
    with open(os.path.join(HERE, "maps", name), encoding="utf-8") as f:
        return {int(r["inv_id"]): int(r["ti_id"]) for r in csv.DictReader(f) if r["ti_id"]}


def main(inv_ref, ti_ref):
    inv, ti = country_files(inv_ref), country_files(ti_ref)
    base_name = lambda p: os.path.basename(p).lower()
    ti_by_file = {}
    for tag, path in ti.items():
        ti_by_file.setdefault(base_name(path), []).append(tag)
    rows = []
    for tag, path in sorted(inv.items()):
        if tag in ti and base_name(ti[tag]) == base_name(path):
            continue
        hosts = [t for t in ti_by_file.get(base_name(path), []) if t != tag]
        if tag in FRESH_TAGS:
            rows.append((tag, FRESH_TAGS[tag], "fresh", f"INV {path}; TI {tag} is {ti.get(tag)}"))
        elif hosts:
            rows.append((tag, hosts[0], "rehosted", f"INV {path}; TI {tag} is {ti.get(tag, 'unused')}"))
        elif tag in ti:
            rows.append((tag, "", "COLLISION", f"INV {path}; TI {tag} is {ti[tag]}"))
    with open(os.path.join(HERE, "maps", "tags.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["inv_tag", "ti_tag", "method", "note"])
        w.writerows(rows)
    print("tags:", [(r[0], r[1], r[2]) for r in rows])

    pmap = load_province_map()
    inv_areas, ti_areas = parse_areas(inv_ref), parse_areas(ti_ref)
    inv_regions, ti_regions = parse_regions(inv_ref), parse_regions(ti_ref)
    ti_area_of = {p: a for a, ps in ti_areas.items() for p in ps}
    ti_region_of_area = {a: r for r, areas in ti_regions.items() for a in areas}
    out = []
    for area, provs in sorted(inv_areas.items()):
        if area in ti_areas:
            continue
        votes = Counter(ti_area_of.get(pmap.get(p)) for p in provs if pmap.get(p) in ti_area_of)
        best = votes.most_common(1)[0][0] if votes else ""
        share = votes.most_common(1)[0][1] / len(provs) if votes else 0
        out.append(("area", area, best, f"{share:.0%} of {len(provs)} provinces; {dict(votes.most_common(3))}"))
    for region, areas in sorted(inv_regions.items()):
        if region in ti_regions:
            continue
        votes = Counter()
        for a in areas:
            for p in inv_areas.get(a, []):
                ta = ti_area_of.get(pmap.get(p))
                if ta in ti_region_of_area:
                    votes[ti_region_of_area[ta]] += 1
        best = votes.most_common(1)[0][0] if votes else ""
        out.append(("region", region, best, f"{dict(votes.most_common(3))}"))
    with open(os.path.join(HERE, "maps", "areas_regions.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kind", "inv_name", "ti_name", "note"])
        w.writerows(out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main(*sys.argv[1:3])
