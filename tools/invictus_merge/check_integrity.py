"""Static integrity checks over a mod directory. Run it on the pre-merge tree and the merged tree;
`diff` mode lists only problems the merge introduced.

Checks: character references (undefined / Dudley placeholder / duplicate IDs), province references
(not in definition.csv; owns-style triggers pointing at non-land), country tags, area/region names,
duplicate English loc keys, loc files without BOM, brace balance.

Usage:
  python check_integrity.py scan <mod_dir> <out.json>
  python check_integrity.py diff <before.json> <after.json>
"""
import json
import os
import re
import sys
from collections import defaultdict

import pdx
from refs import AREA_RES, character_refs, province_refs

VANILLA = r"C:/Program Files (x86)/Steam/steamapps/common/ImperatorRome/game"
SKIP = ("map_data/", "gfx/", "tools/", ".git", "Province Data Editor/", "content_source/", "music/", "sound/")
TAG_RES = [re.compile(r"(?<![\w.:])c:([A-Z][A-Z0-9]{2})\b"), re.compile(r"\btag\s*=\s*([A-Z][A-Z0-9]{2})\b")]
OWNS_RE = re.compile(r"\b(owns|owns_or_subject_owns|controls)\s*=\s*(\d+)")


def read(path):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig", errors="replace").replace("\r\n", "\n"), bom


def walk(root):
    for d, dirs, files in os.walk(root):
        rel = os.path.relpath(d, root).replace("\\", "/")
        rel = "" if rel == "." else rel + "/"
        dirs[:] = [x for x in dirs if not (rel + x + "/").startswith(SKIP)]
        for f in files:
            if f.endswith((".txt", ".yml")):
                yield rel + f


def defs_csv(root):
    ids, kinds = set(), {}
    with open(os.path.join(root, "map_data/definition.csv"), encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            p = line.split(";")
            if p[0].strip().isdigit():
                ids.add(int(p[0]))
    text = re.sub(r"#[^\n]*", "", read(os.path.join(root, "map_data/default.map"))[0])
    nonland = set()
    for m in re.finditer(r"(\w+)\s*=\s*(LIST|RANGE)\s*\{([^}]*)\}", text):
        v = [int(x) for x in m.group(3).split()]
        nonland |= set(v) if m.group(2) == "LIST" else set(range(v[0], v[1] + 1))
    return ids, nonland


def scan(root):
    issues = defaultdict(list)
    files = sorted(walk(root))
    texts = {}
    for p in files:
        try:
            texts[p] = read(os.path.join(root, p))
        except OSError:
            continue
    # characters
    chars = defaultdict(list)
    dudley = set()
    for p, (t, _) in texts.items():
        if not p.startswith("setup/characters/"):
            continue
        for top in pdx.parse(t).items:
            if top.is_block:
                for n in top.value.items:
                    if n.key and n.key.isdigit() and n.is_block:
                        chars[int(n.key)].append(p)
                        fn = n.value.get("first_name")
                        if fn is not None and fn.value == "Dudley":
                            dudley.add(int(n.key))
    for cid, ps in chars.items():
        if len(ps) > 1:
            issues["duplicate_character_id"].append([str(cid), ",".join(ps)])
    prov_ids, nonland = defs_csv(root)
    areas = set(re.findall(r"^(\w+)\s*=\s*\{", read(os.path.join(root, "map_data/areas.txt"))[0], re.M))
    regions = set(re.findall(r"^(\w+)\s*=\s*\{", read(os.path.join(root, "map_data/regions.txt"))[0], re.M))
    tags = set()
    for base in (root, VANILLA):
        cpath = os.path.join(base, "setup/countries/countries.txt")
        if os.path.exists(cpath):
            tags |= set(re.findall(r"^\s*([A-Z][A-Z0-9]{2})\s*=", re.sub(r"#[^\n]*", "", read(cpath)[0]), re.M))
    loc_keys = defaultdict(list)
    for p, (t, bom) in texts.items():
        if p.startswith("localization/english/") or (p.startswith("localization/replace/") and "_english" in p):
            if not bom:
                issues["loc_without_bom"].append([p, ""])
            if p.startswith("localization/english/"):
                for m in re.finditer(r'^\s*([^\s#:"]+):\d*\s*"', t, re.M):
                    loc_keys[m.group(1)].append(p)
        for cid, s, e in character_refs(p, t):
            if cid not in chars:
                issues["character_undefined"].append([p, str(cid)])
            elif cid in dudley:
                issues["character_is_dudley_placeholder"].append([p, str(cid)])
        if p.startswith("common/province_names/"):
            continue
        for pid, s, e in province_refs(p, t, include_name_defs=False):
            if pid not in prov_ids and pid != 0:
                issues["province_undefined"].append([p, str(pid)])
        if p.endswith(".txt") and not p.startswith(("setup/provinces/", "setup/main/")):
            for m in OWNS_RE.finditer(t):
                if int(m.group(2)) in nonland:
                    issues["owns_nonland_province"].append([p, m.group(2)])
            for rx in TAG_RES:
                for m in rx.finditer(t):
                    if m.group(1) not in tags:
                        issues["tag_undefined"].append([p, m.group(1)])
            for rx, kind in AREA_RES:
                for m in rx.finditer(t):
                    name = m.group(1)
                    if name.startswith("$") or name in ("scope", "this", "root", "prev", "from"):
                        continue
                    if (kind == "area" and name not in areas) or (kind == "region" and name not in regions):
                        issues[f"{kind}_undefined"].append([p, name])
            d = mn = 0
            for k, v, s, e in pdx.tokenize(t):
                d += (k == "open") - (k == "close")
                mn = min(mn, d)
            if d or mn < 0:
                issues["brace_imbalance"].append([p, f"{d}/{mn}"])
    for k, ps in loc_keys.items():
        if len(ps) > 1:
            issues["loc_duplicate_key"].append([k, ",".join(sorted(set(ps)))])
    return {k: sorted(v) for k, v in issues.items()}


def diff(before, after):
    b, a = json.load(open(before, encoding="utf-8")), json.load(open(after, encoding="utf-8"))
    report = {}
    for k in sorted(set(a) | set(b)):
        bs = {tuple(x) for x in b.get(k, [])}
        as_ = {tuple(x) for x in a.get(k, [])}
        report[k] = {"before": len(bs), "after": len(as_), "new": sorted(as_ - bs), "fixed": len(bs - as_)}
    return report


if __name__ == "__main__":
    if sys.argv[1] == "scan":
        res = scan(sys.argv[2])
        json.dump(res, open(sys.argv[3], "w", encoding="utf-8"), indent=0)
        print({k: len(v) for k, v in res.items()})
    else:
        rep = diff(sys.argv[2], sys.argv[3])
        for k, v in rep.items():
            print(f"{k}: before {v['before']} after {v['after']} fixed {v['fixed']} NEW {len(v['new'])}")
            for x in v["new"][:15]:
                print("    ", *x)
