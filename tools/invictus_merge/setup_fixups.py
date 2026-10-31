"""Consistency fixes after setup_merge.py, comparing the working tree with HEAD (pre-merge TI):

1. Countries with setup blocks but no countries.txt registration get their HEAD line back
   (TI kept a country Invictus culled, so the merge dropped its registration).
2. A province owned by several countries keeps only the owners it had in HEAD (TI's map and
   ownership win); if it had none, it goes to the first claimant that isn't sharing it.
3. Provinces that aren't land on TI's map (sea, lake, river, wasteland, impassable) are removed
   from ownership lists when the merge added them.
4. A country whose capital it no longer owns gets the first province it owns; a country that
   the merge added and that has no land left is removed (Invictus content for land TI's map
   doesn't have).

Writes reports/setup_fixups.csv.
"""
import csv
import os
import re
from collections import defaultdict

import pdx
from gitio import TI_ROOT, decode, encode, git
from mapdata import parse_default_map

HERE = os.path.dirname(__file__)
COUNTRIES = "setup/main/02_countries.txt"
REGISTRY = "setup/countries/countries.txt"


def ownership(text):
    root = pdx.parse(text)
    owners, nodes = defaultdict(list), {}
    for c in root.get_all("country"):
        for n in c.value.get("countries").value.items:
            if not n.is_block:
                continue
            nodes[n.key] = n
            for occ in n.value.get_all("own_control_core"):
                for v in occ.value.items:
                    if v.key is None and not v.is_block and str(v.value).isdigit():
                        owners[int(v.value)].append(n.key)
    return root, owners, nodes


TREASURES = "setup/main/02_treasures.txt"
TI_TREASURE_FLOOR = 1000  # Invictus owns treasure IDs below this, TI's own live at and above it


def treasure_db(text):
    out = {}
    for tm in pdx.parse(text).get_all("treasure_manager"):
        db = tm.value.get("database")
        for n in db.value.items if db else []:
            if n.key and n.key.isdigit():
                out.setdefault(int(n.key), n)
    return out


def treasure_key(text, node):
    m = re.search(r'\bkey\s*=\s*"?([\w]+)', text[node.start:node.end])
    return m.group(1) if m else None


def fix_treasure_collisions(log, inv_ref="upstream/main", base_ref="f2e32b70d"):
    """A treasure ID TI added below TI_TREASURE_FLOOR that Invictus has since used for a different
    treasure: the keyed merge blended them. Give TI's treasure the next free ID >= the floor and put
    Invictus's back under its ID."""
    path = os.path.join(TI_ROOT, TREASURES)
    cur, bom, _ = decode(open(path, "rb").read())
    head = decode(git("show", f"HEAD:{TREASURES}"))[0]
    inv = decode(git("show", f"{inv_ref}:setup/main/00_default.txt"))[0]
    cn, hn, inn = treasure_db(cur), treasure_db(head), treasure_db(inv)
    base_ids = set(treasure_db(decode(git("show", f"{base_ref}:setup/main/00_default.txt"))[0]))
    taken = set(cn)
    for tid in sorted((set(hn) & set(inn)) - base_ids):
        if tid >= TI_TREASURE_FLOOR or treasure_key(head, hn[tid]) == treasure_key(inv, inn[tid]):
            continue
        new_id = next(i for i in range(max(taken | {TI_TREASURE_FLOOR - 1}) + 1, 10 ** 6) if i not in taken)
        taken.add(new_id)
        ti_block = re.sub(rf"^{tid}(\s*=)", rf"{new_id}\1", head[hn[tid].start:hn[tid].end])
        ind = cur[cur.rfind("\n", 0, cn[tid].start) + 1:cn[tid].start]
        cur = cur[:cn[tid].start] + ti_block + "\n" + ind + inv[inn[tid].start:inn[tid].end] + cur[cn[tid].end:]
        cn = treasure_db(cur)
        log.append(("treasure", tid, f"TI's {treasure_key(head, hn[tid])} moved to {new_id}; "
                                     f"{tid} is Invictus's {treasure_key(inv, inn[tid])}"))
    open(path, "wb").write(encode(cur, bom, True))


def main():
    log = []
    fix_treasure_collisions(log)
    path = os.path.join(TI_ROOT, COUNTRIES)
    text, bom, _ = decode(open(path, "rb").read())
    for _ in range(5):  # restoring a country's land can create new overlaps; iterate to a fixed point
        text, n = fix_pass(text, log)
        if not n:
            break
    open(path, "wb").write(encode(text, bom, True))
    register(text, log)
    with open(os.path.join(HERE, "reports", "setup_fixups.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tag", "province", "action"])
        w.writerows(log)
    for r in log:
        print(*r)


def fix_pass(text, log):
    head_text = decode(git("show", f"HEAD:{COUNTRIES}"))[0]
    _, head_owners, head_nodes = ownership(head_text)
    _, owners, nodes = ownership(text)
    dm = parse_default_map("HEAD")
    nonland = set().union(*(dm.get(k, set()) for k in ("sea_zones", "lakes", "river_provinces", "wasteland",
                                                      "impassable_terrain", "uninhabitable")))
    remove = defaultdict(set)  # tag -> provinces to drop from its lists
    for pid, tags in owners.items():
        added_by_merge = [t for t in tags if t not in head_owners.get(pid, [])]
        if pid in nonland:
            for t in added_by_merge:
                remove[t].add(pid)
                log.append((t, pid, "removed: not land on TI map"))
            continue
        if len(set(tags)) > 1:
            keep = [t for t in tags if t in head_owners.get(pid, [])] or [tags[0]]
            for t in set(tags) - set(keep):
                remove[t].add(pid)
                log.append((t, pid, f"removed: also owned by {'/'.join(keep)} (TI ownership wins)"))
    edits = []
    final_land = {}
    for tag, n in nodes.items():
        land = []
        for occ in n.value.get_all("own_control_core"):
            for v in occ.value.items:
                if v.key is None and not v.is_block and str(v.value).isdigit():
                    if int(v.value) in remove.get(tag, ()):
                        edits.append((v.start, v.end, ""))
                    else:
                        land.append(int(v.value))
        final_land[tag] = land
    # capitals / landless countries
    for tag, n in nodes.items():
        land = final_land[tag]
        cap = n.value.get("capital")
        capv = int(cap.value) if cap is not None and str(cap.value).isdigit() else None
        head_bad = tag in head_nodes and (lambda hc: hc is None or tag not in head_owners.get(int(hc.value) if str(hc.value).isdigit() else -1, []))(head_nodes[tag].value.get("capital"))
        if not land:
            if tag not in head_nodes:
                s, e = pdx.node_with_indent(text, n)
                edits.append((s, e, ""))
                log.append((tag, "", "country removed: Invictus-added, no land on TI map"))
            elif any(tag in o for o in head_owners.values()):
                # Invictus moved this country onto land TI's map doesn't have: keep TI's land and capital
                h = head_nodes[tag]
                occs, hoccs = n.value.get_all("own_control_core"), h.value.get_all("own_control_core")
                if occs and hoccs:
                    edits.append((occs[0].start, occs[0].end, head_text[hoccs[0].start:hoccs[0].end]))
                hcap = h.value.get("capital")
                if cap is not None and hcap is not None:
                    edits.append((cap.val_start, cap.val_end, hcap.value))
                log.append((tag, "", "land and capital restored from TI: Invictus's land for it isn't on TI's map"))
            continue
        if capv not in land and not head_bad:
            if cap is not None:
                edits.append((cap.val_start, cap.val_end, str(land[0])))
            log.append((tag, land[0], f"capital {capv} not owned -> {land[0]}"))
    clean, last = [], -1
    for s, e, r in sorted(set(edits), key=lambda x: (x[0], -x[1])):
        if s < last:
            continue  # inside a removed country
        clean.append((s, e, r))
        last = max(last, e)
    return pdx.splice(text, clean), len(clean)


def register(text, log):
    # registrations
    reg_path = os.path.join(TI_ROOT, REGISTRY)
    reg, rbom, _ = decode(open(reg_path, "rb").read())
    head_reg = decode(git("show", f"HEAD:{REGISTRY}"))[0]
    registered = set(re.findall(r'^\s*([A-Z0-9]{3})\s*=', reg, re.M))
    _, _, nodes_now = ownership(text)
    restore = []
    for tag in nodes_now:
        if tag not in registered:
            m = re.search(rf'^\s*{tag}\s*=\s*"[^"]+"[^\n]*$', head_reg, re.M)
            if m:
                restore.append(m.group(0).strip())
                log.append((tag, "", "re-registered in countries.txt (TI kept this country)"))
            else:
                log.append((tag, "", "UNREGISTERED and not in HEAD registry"))
    if restore:
        reg = reg.rstrip("\n") + "\n\n# Kept by Terra Indomita (culled in Invictus)\n" + "\n".join(restore) + "\n"
        open(reg_path, "wb").write(encode(reg, rbom, True))


if __name__ == "__main__":
    main()
