"""Resolve definitions the merge left duplicated (same top-level key defined twice in one database
folder, e.g. TI overrides vanilla's scripted effect in its copy of 00_event_effects.txt while
Invictus now overrides it in 00_event_effects_inv_1_0.txt). The game would silently use only one.

For each duplicated name, with R = the vanilla or Invictus-base definition as reference:
  copies identical, or TI's copy == R      -> keep Invictus's copy, delete TI's
  Invictus's copy == R (it only moved it)  -> keep TI's copy, delete Invictus's
  both customised                          -> 3-way merge (R, TI, Invictus) into TI's copy,
                                              delete Invictus's, log for review
Names listed in TI_AUTHORITATIVE keep TI's copy regardless (TI-owned content).

Usage: python dedupe_defs.py <tiger_merged.json> <tiger_new.csv>
"""
import csv
import json
import os
import sys
from collections import defaultdict

import pdx
from gitio import TI_ROOT, decode, encode, git
from semantic_merge import merge_block, _dedupe

HERE = os.path.dirname(__file__)
VANILLA = r"C:/Program Files (x86)/Steam/steamapps/common/ImperatorRome/game"
TI_AUTHORITATIVE = {"chinese_religions", "uralic_pantheon", "levy_pontus", "chinese_clothes", "abasgoi"}


def top_defs(text):
    out = defaultdict(list)
    for n in pdx.parse(text).items:
        if n.key:
            out[n.key].append(n)
    return out


def folder_defs(read_file, paths, name):
    for p in paths:
        try:
            t = read_file(p)
        except Exception:
            continue
        ns = top_defs(t).get(name)
        if ns:
            return t, ns[0]
    return None


def main(tiger_json, new_csv):
    bs = chr(92)
    new = {(r["path"], r["message"], r["line"]) for r in csv.DictReader(open(new_csv, encoding="utf-8"))
           if r["key"] in ("duplicate-item", "exact-duplicate-item") and not r["path"].endswith(".yml")}
    pairs = []
    for r in json.load(open(tiger_json, encoding="utf-8")):
        if r["key"] not in ("duplicate-item", "exact-duplicate-item"):
            continue
        locs = r["locations"]
        p0 = locs[0]["path"].replace(bs, "/")
        if (p0, r["message"], (locs[0].get("line") or "").strip()) not in new:
            continue
        name = (locs[0].get("line") or "").split("=")[0].strip()
        pairs.append((name, [(x["path"].replace(bs, "/"), x["linenr"]) for x in locs[:2]]))
    log, edits = [], defaultdict(list)
    cache = {}

    def wt(path):
        if path not in cache:
            cache[path] = decode(open(os.path.join(TI_ROOT, path), "rb").read())
        return cache[path][0]

    for name, locs in pairs:
        folder = os.path.dirname(locs[0][0])
        if not all(os.path.exists(os.path.join(TI_ROOT, p)) for p, _ in locs):
            log.append((name, "skipped: one copy's file no longer exists", str(locs)))
            continue
        copies = []
        for path, linenr in locs:
            t = wt(path)
            for n in top_defs(t).get(name, []):
                if t.count("\n", 0, n.start) + 1 == linenr:
                    copies.append((path, t, n))
        if len(copies) != 2:
            log.append((name, "skipped: could not locate both copies", str(locs)))
            continue

        def origin(c):
            path, t, n = c
            ti = inv = False
            for ref, flag in (("HEAD", "ti"), ("upstream/main", "inv")):
                try:
                    rt = decode(git("show", f"{ref}:{path}"))[0]
                except RuntimeError:
                    continue
                if any(pdx.canon(rt, x) == pdx.canon(t, n) for x in top_defs(rt).get(name, [])):
                    if flag == "ti":
                        ti = True
                    else:
                        inv = True
            return ti, inv
        o0, o1 = origin(copies[0]), origin(copies[1])
        if o0[0] and not o1[0]:
            ti_c, inv_c = copies[0], copies[1]
        elif o1[0] and not o0[0]:
            ti_c, inv_c = copies[1], copies[0]
        elif o0[1] and not o1[1]:
            inv_c, ti_c = copies[0], copies[1]
        else:
            inv_c, ti_c = copies[1], copies[0]
        vanilla_dir = os.path.join(VANILLA, folder)
        ref = None
        if os.path.isdir(vanilla_dir):
            ref = folder_defs(lambda p: decode(open(os.path.join(vanilla_dir, p), "rb").read())[0],
                              sorted(f for f in os.listdir(vanilla_dir) if f.endswith(".txt")), name)
        if ref is None:
            base_files = [p for p in git("ls-tree", "-r", "--name-only", "f2e32b70d", "--", folder).decode().split("\n") if p]
            ref = folder_defs(lambda p: decode(git("show", f"f2e32b70d:{p}"))[0], base_files, name)
        ct, ci = pdx.canon(ti_c[1], ti_c[2]), pdx.canon(inv_c[1], inv_c[2])
        cr = pdx.canon(ref[0], ref[1]) if ref else None

        def delete(c):
            edits[c[0]].append(pdx.node_with_indent(c[1], c[2]) + ("",))

        if name in TI_AUTHORITATIVE:
            delete(inv_c)
            log.append((name, f"kept TI ({ti_c[0]}), deleted Invictus copy ({inv_c[0]})", "TI-owned content"))
        elif ct == ci or ct == cr:
            delete(ti_c)
            log.append((name, f"kept Invictus ({inv_c[0]}), deleted TI copy ({ti_c[0]})",
                        "identical" if ct == ci else "TI copy was unmodified vanilla/base"))
        elif ci == cr:
            delete(inv_c)
            log.append((name, f"kept TI ({ti_c[0]}), deleted Invictus copy ({inv_c[0]})", "Invictus copy unmodified"))
        else:
            sub = []
            n_o, n_t = ti_c[2], inv_c[2]
            es = merge_block(ref[0] if ref else None, ref[1].value if ref else None, ti_c[1], n_o.value,
                             inv_c[1], n_t.value, 2, ti_c[0], [name], sub) if n_o.is_block and n_t.is_block else []
            edits[ti_c[0]] += es
            delete(inv_c)
            log.append((name, f"merged into TI copy ({ti_c[0]}), deleted Invictus copy ({inv_c[0]})",
                        "; ".join(f"{x[1]}:{x[2]}" for x in sub)[:300] or "no field conflicts"))
    for path, es in edits.items():
        text, bom, _ = cache[path]
        open(os.path.join(TI_ROOT, path), "wb").write(encode(pdx.splice(text, _dedupe(es)), bom, True))
    with open(os.path.join(HERE, "reports", "dedupe_defs.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "action", "reason"])
        w.writerows(log)
    for r in log:
        print(" | ".join(r))


if __name__ == "__main__":
    main(*sys.argv[1:3])
