"""Translate an Invictus tree into Terra-Indomita's ID space.

Province IDs go through maps/provinces*.csv, country tags through maps/tags.csv, area/region names
through maps/areas_regions.csv. Character IDs need no translation: Invictus owns IDs below 1516.
Paths Terra-Indomita owns (its map, non-English localisation, files it deleted on purpose, the
military-tradition files it replaced, and setup files handled by semantic_merge.py) are left out
entirely, so a merge never touches TI's version of them.

As a library: Translator(map_csv).translate_text(path, text) and vendor_tree(...).
As a script: python translate.py report <inv_ref> <map_csv> <ti_ref>   (dry run, writes a report)
"""
import csv
import os
import re
import sys
from collections import Counter

import refs as R
from gitio import decode, encode, git, is_text_path, ls_tree, read_blobs

HERE = os.path.dirname(__file__)
TI_OWNED_PREFIXES = (
    "map_data/", "gfx/map/", "content_source/map_objects/", "tools/", "setup/provinces/",
    "common/military_traditions/", ".github/", ".scripts/", ".vscode/", "Province Data Editor/", "music/",
)
TI_OWNED_FILES = {"setup/main/00_default.txt", "descriptor.mod", ".gitattributes", ".gitignore", "README.md",
                  "thumbnail.png", "thumbnail.jpg", "imperator-tiger.conf"}
NON_ENGLISH_LOC = re.compile(r"^localization/(?!english/|replace/|load_tips/)|^localization/.*_l_(?!english\b)[a-z_]+\.yml$")
PROV_BASE_KEY_RE = re.compile(r"^\s*PROV(\d+):\d*\s")
PROV_SUFFIX_RE = re.compile(r"PROV(\d+)_")
DISTANCE_RE = re.compile(r"\b(distance|squared_distance|max_distance|MAX_\w*DISTANCE\w*)\b[^\n]{0,60}?(\d{2,})")


def is_ti_owned(path, ti_deleted=frozenset()):
    return (path.startswith(TI_OWNED_PREFIXES) or path in TI_OWNED_FILES or bool(NON_ENGLISH_LOC.match(path))
            or path in ti_deleted)


def ti_deliberate_deletions(base_ref, ti_ref):
    """Paths in base that TI deleted without a >=90% rename."""
    out = git("diff", "--name-status", "-M90%", "--diff-filter=D", base_ref, ti_ref).decode("utf-8")
    return frozenset(line.split("\t", 1)[1] for line in out.splitlines() if line.startswith("D"))


class Translator:
    def __init__(self, province_csv="provinces.csv"):
        self.pmap, self.pconf, self.pname = {}, {}, {}
        with open(os.path.join(HERE, "maps", province_csv), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["ti_id"]:
                    pid = int(r["inv_id"])
                    self.pmap[pid] = int(r["ti_id"])
                    self.pconf[pid] = r["confidence"] if r["method"] != "identity" else "identity"
                    self.pname[pid] = r["inv_name"]
        targets = Counter(self.pmap.values())
        # a TI province can host an INV province's names/loc only if nothing else maps onto it
        self.one_to_one = {p for p, t in self.pmap.items() if targets[t] == 1}
        with open(os.path.join(HERE, "maps", "tags.csv"), encoding="utf-8") as f:
            self.tmap = {r["inv_tag"]: r["ti_tag"] for r in csv.DictReader(f) if r["ti_tag"]}
        self.tag_rxs = R.tag_token_res(self.tmap) if self.tmap else None
        with open(os.path.join(HERE, "maps", "areas_regions.csv"), encoding="utf-8") as f:
            self.amap = {(r["kind"], r["inv_name"]): r["ti_name"] for r in csv.DictReader(f) if r["ti_name"]}

    def prov(self, pid):
        return self.pmap.get(pid)

    def nameable(self, pid):
        """Can PROVn_* names / loc for INV province pid be carried over to its TI province?"""
        return self.pconf.get(pid) == "identity" or (pid in self.one_to_one and self.pconf.get(pid) == "high")

    def translate_text(self, path, text, log=None, drop_names=True):
        """-> new text. log (list) receives (path, line, kind, old, new, confidence) for every change
        and ('unmapped', ...) for IDs with no mapping."""
        log = log if log is not None else []
        lines_dropped = 0
        # 1. drop province-name definitions that TI owns (base PROVn keys of non-identity provinces,
        #    and culture names / province_names entries that can't be carried over one-to-one)
        if drop_names and (path.endswith(".yml") or path.startswith("common/province_names/")):
            kept = []
            for i, line in enumerate(text.split("\n")):
                drop = None
                m = PROV_BASE_KEY_RE.match(line)
                if m and path.endswith(".yml") and self.pconf.get(int(m.group(1))) not in (None, "identity"):
                    drop = int(m.group(1))
                for m2 in PROV_SUFFIX_RE.finditer(line):
                    pid = int(m2.group(1))
                    if pid in self.pmap and not self.nameable(pid):
                        drop = pid
                if path.startswith("common/province_names/"):
                    mk = re.match(r"\s*(\d+)\s*=", line)
                    if mk and int(mk.group(1)) in self.pmap and not self.nameable(int(mk.group(1))):
                        drop = int(mk.group(1))
                if drop is not None:
                    lines_dropped += 1
                    log.append((path, i + 1, "drop-name", drop, line.strip()[:60], self.pconf.get(drop, "")))
                else:
                    kept.append(line)
            text = "\n".join(kept)

        # 2. province IDs
        prefs = R.province_refs(path, text, include_name_defs=drop_names)

        def fp(pid):
            new = self.pmap.get(pid)
            if new is None:
                log.append((path, 0, "unmapped-province", pid, "", ""))
                return None
            if new != pid:
                log.append((path, 0, "province", pid, new, self.pconf.get(pid)))
            return new
        text, plog = R.rewrite(text, [(p, s, e) for p, s, e in prefs], fp)

        # 3. tags
        if self.tag_rxs:
            text, tlog = R.rewrite(text, R.tag_refs(path, text, self.tag_rxs), lambda t: self.tmap.get(t))
            log += [(path, ln, "tag", o, n, "") for o, n, ln in tlog]

        # 4. areas / regions
        arefs = R.area_region_refs(text)
        text, alog = R.rewrite(text, [((k, n), s, e) for k, n, s, e in arefs], lambda kn: self.amap.get(kn))
        log += [(path, ln, "area/region", o[1], n, "") for o, n, ln in alog]
        return text

    def distance_flags(self, path, text):
        if not path.endswith(".txt"):
            return []
        return [(path, text.count("\n", 0, m.start()) + 1, m.group(0)[:80]) for m in DISTANCE_RE.finditer(text)]


def vendor_tree(inv_ref, province_csv, ti_deleted, log):
    """Translated tree of inv_ref: {path: (mode, sha_or_None, bytes_or_None)}."""
    tr = Translator(province_csv)
    tree = ls_tree(inv_ref)
    keep = {p: v for p, v in tree.items() if v[1] == "blob" and not is_ti_owned(p, ti_deleted)}
    text_paths = [p for p in keep if p.endswith((".txt", ".yml"))]
    blobs = read_blobs([keep[p][2] for p in text_paths])
    out = {}
    for p, (mode, _, sha) in keep.items():
        if p not in text_paths:
            out[p] = (mode, sha, None)
            continue
        raw = blobs[sha]
        text, bom, crlf = decode(raw)
        new = tr.translate_text(p, text, log)
        out[p] = (mode, sha, None) if new == text else (mode, None, encode(new, bom, crlf))
    return out


def report(inv_ref, province_csv, ti_ref, base_ref="f2e32b70d"):
    log = []
    ti_deleted = ti_deliberate_deletions(base_ref, ti_ref)
    tree = vendor_tree(inv_ref, province_csv, ti_deleted, log)
    changed = sum(1 for v in tree.values() if v[2] is not None)
    print(f"{len(tree)} files kept, {changed} translated")
    c = Counter((k, conf) for _, _, k, _, _, conf in log)
    print(c.most_common())
    out = os.path.join(HERE, "reports", f"translate_{inv_ref.replace('/', '_')}.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "line", "kind", "old", "new", "confidence"])
        w.writerows(log)
    print("wrote", out)


if __name__ == "__main__":
    if sys.argv[1] == "report":
        report(sys.argv[2], sys.argv[3], sys.argv[4])
