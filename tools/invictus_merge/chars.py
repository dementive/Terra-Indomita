"""Historical character tables (setup/characters) at any git ref, and person matching across
tables, so a `char:N` written against one table can be re-pointed at the same person in another."""
import difflib
import json
import os
import re

import pdx
from gitio import CACHE_DIR, decode, git, ls_tree, read_blobs

CHAR_KEYS = ("first_name", "family_name", "family", "birth_date", "death_date", "culture", "religion", "female", "father", "mother")


def tree_sha(ref, path):
    out = git("rev-parse", f"{ref}:{path}", check=False).decode().strip()
    return out if re.fullmatch(r"[0-9a-f]{40}", out) else None


def load_table(ref):
    """id -> dict(first_name, family, birth_date, culture, country, file, ...). Cached per tree sha.
    When an ID is defined twice the first definition (alphabetical file order) is kept and the
    duplicate is recorded under '_dupes'."""
    tsha = tree_sha(ref, "setup/characters")
    if tsha is None:
        return {}
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache = os.path.join(CACHE_DIR, f"chars_{tsha}.json")
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            return {int(k) if k.lstrip("-").isdigit() else k: v for k, v in json.load(f).items()}
    tree = ls_tree(ref, "setup/characters")
    files = sorted(p for p in tree if p.endswith(".txt"))
    blobs = read_blobs([tree[p][2] for p in files])
    table, dupes = {}, []
    for p in files:
        text, _, _ = decode(blobs[tree[p][2]])
        root = pdx.parse(text)
        for top in root.items:
            if not top.is_block:
                continue
            country = None
            c = top.value.get("country")
            if c is not None and not c.is_block:
                country = c.value
            for n in top.value.items:
                if n.key is None or not n.key.isdigit() or not n.is_block:
                    continue
                cid = int(n.key)
                rec = {"file": p, "country": country}
                for k in CHAR_KEYS:
                    v = n.value.get(k)
                    if v is not None and not v.is_block:
                        rec[k] = v.value
                if cid in table:
                    dupes.append([cid, p])
                    continue
                table[cid] = rec
    out = dict(table)
    out["_dupes"] = dupes
    with open(cache, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in out.items()}, f)
    return out


def norm(s):
    return re.sub(r"[^a-z]", "", (s or "").lower())


def family_of(rec):
    fam = rec.get("family") or rec.get("family_name") or ""
    return norm(fam.split(":")[-1])


class Matcher:
    """Find a person (record from some table) in a target table."""

    def __init__(self, target):
        self.target = {k: v for k, v in target.items() if isinstance(k, int)}
        self.by_name_birth, self.by_name, self.by_birth = {}, {}, {}
        for cid, r in self.target.items():
            nm, b = norm(r.get("first_name")), r.get("birth_date", "")
            self.by_name_birth.setdefault((nm, b), []).append(cid)
            self.by_name.setdefault(nm, []).append(cid)
            self.by_birth.setdefault(b, []).append(cid)

    def find(self, rec, hint_id=None):
        """-> (target_id or None, how)"""
        nm, b = norm(rec.get("first_name")), rec.get("birth_date", "")
        if not nm and not b:
            return (hint_id, "same-id(no-identity)") if hint_id in self.target else (None, "no-identity")
        c = self.by_name_birth.get((nm, b), [])
        if len(c) > 1:
            c2 = [x for x in c if family_of(self.target[x]) == family_of(rec)] or c
            c = [hint_id] if hint_id in c2 else c2
        if len(c) == 1:
            return c[0], "name+birth"
        if hint_id in self.target:
            t = self.target[hint_id]
            if norm(t.get("first_name")) == nm or (t.get("birth_date") == b and b and family_of(t) == family_of(rec)):
                return hint_id, "same-id"
        # same name, same culture and family, unique (birth date fixed upstream)
        c = [x for x in self.by_name.get(nm, []) if self.target[x].get("culture") == rec.get("culture") and family_of(self.target[x]) == family_of(rec)]
        if len(c) == 1:
            return c[0], "name+family"
        # respelt name, same birth date and family/culture
        c = [x for x in self.by_birth.get(b, []) if b and (family_of(self.target[x]) == family_of(rec) or self.target[x].get("culture") == rec.get("culture"))
             and difflib.SequenceMatcher(None, norm(self.target[x].get("first_name")), nm).ratio() >= 0.75]
        if len(c) == 1:
            return c[0], "fuzzy-name+birth"
        return None, "unresolved"


def describe(rec):
    if not rec:
        return "<undefined>"
    fam = (rec.get("family") or rec.get("family_name") or "").split(":")[-1]
    return f"{rec.get('first_name', '?')} {fam} ({rec.get('country')}, b.{rec.get('birth_date', '?')})".replace("  ", " ")
