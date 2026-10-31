"""Separate TI's family IDs from Invictus's (setup/main/01_families.txt + country links in
setup/main/02_countries.txt), the same way characters and treasures are split:

  Invictus owns family IDs below TI_FAMILY_FLOOR; TI's own families live at TI_FAMILY_FLOOR and up.

1. TI-only families (owner/key not used by Invictus) below the floor move up by TI_FAMILY_SHIFT,
   and every `family = N` link in country setup follows.
2. Where TI redefined an Invictus family ID (renamed key, or its own family on that ID), Invictus's
   definition is restored at that ID. TI's version is kept at a new TI ID only if something still
   references its key.
3. Invictus families missing in TI are restored if their owner country exists, and Invictus's
   `family = N` links are added to countries that lack them.

Usage: python fix_families.py <inv_ref>
"""
import csv
import os
import re
import sys
from collections import defaultdict

import pdx
from gitio import TI_ROOT, decode, encode, git

HERE = os.path.dirname(__file__)
FAMILIES = "setup/main/01_families.txt"
COUNTRIES = "setup/main/02_countries.txt"
TI_FAMILY_FLOOR = 2000
TI_FAMILY_SHIFT = 1000


def fam_nodes(text):
    out = {}
    for f in pdx.parse(text).get_all("family"):
        for n in f.value.get("families").value.items:
            if n.key and n.key.isdigit() and n.is_block:
                k, o = n.value.get("key"), n.value.get("owner")
                out[int(n.key)] = (k.value if k is not None else None, o.value if o is not None else None, n)
    return out


def country_nodes(text):
    out = {}
    for c in pdx.parse(text).get_all("country"):
        for n in c.value.get("countries").value.items:
            if n.is_block:
                out.setdefault(n.key, n)
    return out


def referenced_keys():
    """(key, owner) pairs referenced as c:TAG.fam:Key anywhere in script/setup"""
    out = set()
    for root, dirs, files in os.walk(TI_ROOT):
        rel = os.path.relpath(root, TI_ROOT).replace(os.sep, "/")
        if rel.startswith((".git", "tools", "gfx", "map_data")):
            dirs[:] = []
            continue
        for f in files:
            if f.endswith(".txt"):
                t = open(os.path.join(root, f), "rb").read().decode("utf-8", "replace")
                out |= {(m.group(2), m.group(1)) for m in re.finditer(r"c:([A-Z0-9]{3})\.fam:(\w+)", t)}
    return out


def main(inv_ref):
    log = []
    fpath, cpath = os.path.join(TI_ROOT, FAMILIES), os.path.join(TI_ROOT, COUNTRIES)
    ftext, fbom, _ = decode(open(fpath, "rb").read())
    ctext, cbom, _ = decode(open(cpath, "rb").read())
    inv_text = decode(git("show", f"{inv_ref}:setup/main/00_default.txt"))[0]
    ti, inv = fam_nodes(ftext), fam_nodes(inv_text)
    inv_pairs = {(k, o) for k, o, _ in inv.values()}
    countries, inv_countries = country_nodes(ctext), country_nodes(inv_text)
    refs = referenced_keys()

    fedits, cedits, moved = [], [], {}
    dropped = set()  # (key, owner) of TI copies replaced above, to be restored at Invictus's ID
    taken = set(ti) | set(inv)

    def free_id(want):
        while want in taken:
            want += 1
        taken.add(want)
        return want

    for fid, (key, owner, node) in sorted(ti.items()):
        if fid >= TI_FAMILY_FLOOR:
            continue
        inv_here = inv.get(fid)
        if inv_here and (inv_here[0], inv_here[1]) == (key, owner):
            continue  # same family in both mods
        if (key, owner) in inv_pairs:
            # TI copy of an Invictus family under another ID: put Invictus's family back on this ID
            # (if Invictus uses it) and let the restore below re-create the copy at its own ID
            if inv_here is not None:
                fedits.append((node.start, node.end, inv_text[inv_here[2].start:inv_here[2].end]))
                log.append((fid, f"{inv_here[0]}@{inv_here[1]}", f"restored Invictus family (TI had {key} here)"))
                dropped.add((key, owner))
            continue
        ti_owned = inv_here is None or (key, owner) in refs or fid >= 1000
        if inv_here is not None:
            # restore Invictus's definition at its own ID
            fedits.append((node.start, node.end, inv_text[inv_here[2].start:inv_here[2].end]))
            log.append((fid, f"{inv_here[0]}@{inv_here[1]}", "restored Invictus family (TI had redefined this ID)"))
        if ti_owned:
            new = free_id(fid + TI_FAMILY_SHIFT)
            moved[fid] = new
            block = re.sub(rf"^{fid}(\s*=)", rf"{new}\1", ftext[node.start:node.end])
            if inv_here is None:
                fedits.append((node.key_start, node.key_end, str(new)))
            else:
                fedits.append((node.end, node.end, "\n\t\t" + block))
            log.append((fid, f"{key}@{owner}", f"TI family moved to {new}"))
        elif inv_here is not None:
            log.append((fid, f"{key}@{owner}", "TI rename dropped (key unreferenced)"))

    # Invictus families TI lacks
    add = []
    for fid, (key, owner, node) in sorted(inv.items()):
        if fid in ti or ((key, owner) in {(k, o) for k, o, _ in ti.values() if k and o} and (key, owner) not in dropped):
            continue
        if owner not in countries:
            log.append((fid, f"{key}@{owner}", "not restored: owner country not in TI setup"))
            continue
        add.append(inv_text[node.start:node.end])
        log.append((fid, f"{key}@{owner}", "restored missing Invictus family"))
    if add:
        first = pdx.parse(ftext).get_all("family")[0].value.get("families")
        pos = first.value.end - 1
        fedits.append((pos, pos, "".join("\n\t\t" + a for a in add) + "\n\t"))

    # country links
    restored_ids = {fid for fid, *_ in log if isinstance(fid, int)} | set(inv)
    for tag, n in countries.items():
        links = n.value.get_all("family")
        for f in links:
            if str(f.value).isdigit() and int(f.value) in moved:
                cedits.append((f.val_start, f.val_end, str(moved[int(f.value)])))
        have = {int(f.value) for f in links if str(f.value).isdigit()}
        have = {moved.get(h, h) for h in have}
        inv_n = inv_countries.get(tag)
        if inv_n is None:
            continue
        want = [int(f.value) for f in inv_n.value.get_all("family") if str(f.value).isdigit()]
        missing = [w for w in want if w not in have and w in restored_ids and (w not in ti or w in {fid for fid in ti if ti[fid][:2] == inv[w][:2]} or True)]
        if missing:
            ins = n.value.start + 1
            cedits.append((ins, ins, "".join(f"\n\t\t\tfamily = {m}" for m in missing)))
            log.append((tag, ",".join(map(str, missing)), "added Invictus family links"))

    open(fpath, "wb").write(encode(pdx.splice(ftext, sorted(set(fedits))), fbom, True))
    open(cpath, "wb").write(encode(pdx.splice(ctext, sorted(set(cedits))), cbom, True))
    with open(os.path.join(HERE, "reports", "fix_families.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id_or_tag", "family", "action"])
        w.writerows(log)
    for r in log:
        print(*r)


if __name__ == "__main__":
    main(*sys.argv[1:2])
