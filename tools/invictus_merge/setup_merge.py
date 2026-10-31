"""Semantic 3-way merge of Invictus setup data into Terra-Indomita's setup files (working tree).

These files are left out of the vendor branch because a line merge can't work on them: TI moved
province blocks between files and split Invictus's setup/main/00_default.txt into
setup/main/01_families.txt and 02_*.txt. Instead, both Invictus versions (previous and new) are
translated into TI IDs and merged entity by entity:

  setup/provinces/*            per province ID, field by field (semantic_merge.merge_block)
  00_default country.countries per tag, field by field; own_control_core merged as a set
  00_default family.families, treasure_manager.database   per ID
  00_default provinces, road_network, trade, diplomacy    as sets of entries

Only Invictus's own changes (previous -> new) are applied; anything TI changed wins on conflict and
is logged to reports/setup_merge.csv.

Usage: python setup_merge.py <inv_prev_ref> <inv_new_ref> <prev_map_csv> <new_map_csv>
"""
import csv
import os
import re
import sys
from collections import defaultdict

import pdx
from gitio import TI_ROOT, decode, encode, ls_tree, read_blobs
from semantic_merge import _canon, merge_block
from translate import Translator

HERE = os.path.dirname(__file__)
SPLIT = {  # 00_default section -> TI file holding it
    "treasure_manager": "setup/main/02_treasures.txt",
    "family": "setup/main/01_families.txt",
    "diplomacy": "setup/main/02_diplomacy.txt",
    "provinces": "setup/main/02_provinces.txt",
    "road_network": "setup/main/02_road_network.txt",
    "country": "setup/main/02_countries.txt",
    "trade": "setup/main/02_trade.txt",
}
KEYED = {"treasure_manager": "database", "family": "families", "country": "countries"}


# ---------------------------------------------------------------- translation of setup text

def translate_default(text, tr):
    """00_default.txt in INV IDs -> TI IDs. Province-keyed entries whose province can't be carried
    over one-to-one are dropped (TI owns those provinces' setup)."""
    root = pdx.parse(text)
    edits = []

    def prov(n):
        return tr.pmap.get(int(n)) if str(n).isdigit() else None

    for sec in root.items:
        if not sec.is_block:
            continue
        if sec.key == "provinces":
            for n in sec.value.items:
                if n.key and n.key.isdigit():
                    pid = int(n.key)
                    if tr.nameable(pid):
                        edits.append((n.key_start, n.key_end, str(tr.pmap[pid])))
                    else:
                        edits.append(pdx.node_with_indent(text, n) + ("",))
        elif sec.key == "road_network":
            for n in sec.value.items:
                if n.key and n.key.isdigit() and not n.is_block:
                    a, b = prov(n.key), prov(n.value)
                    if a is None or b is None or a == b:
                        edits.append(pdx.node_with_indent(text, n) + ("",))
                    else:
                        edits.append((n.key_start, n.key_end, str(a)))
                        edits.append((n.val_start, n.val_end, str(b)))
        elif sec.key == "trade":
            for route in sec.value.items:
                if not route.is_block:
                    continue
                f, t = route.value.get("from"), route.value.get("to")
                a, b = (prov(f.value) if f else None), (prov(t.value) if t else None)
                if a is None or b is None or a == b:
                    edits.append(pdx.node_with_indent(text, route) + ("",))
                else:
                    edits += [(f.val_start, f.val_end, str(a)), (t.val_start, t.val_end, str(b))]
        elif sec.key == "country":
            cs = sec.value.get("countries")
            for c in cs.value.items if cs else []:
                if not c.is_block:
                    continue
                for occ in c.value.get_all("own_control_core"):
                    seen = set()
                    for v in occ.value.items:
                        if v.key is None and not v.is_block and str(v.value).isdigit():
                            new = tr.pmap.get(int(v.value))
                            if new is None or new in seen:
                                edits.append((v.start, v.end, ""))
                            else:
                                seen.add(new)
                                edits.append((v.start, v.end, str(new)))
    text = pdx.splice(text, sorted(set(edits)))
    # capital = N, tags (owner=/first=/second=/TAG = {) etc.
    return tr.translate_text("setup/main/00_default.txt", text, drop_names=False)


def translate_provinces(text, tr, log, path):
    root = pdx.parse(text)
    edits = []
    for n in root.items:
        if n.key and n.key.isdigit():
            pid = int(n.key)
            if tr.nameable(pid):
                if tr.pmap[pid] != pid:
                    edits.append((n.key_start, n.key_end, str(tr.pmap[pid])))
            else:
                edits.append(pdx.node_with_indent(text, n) + ("",))
    return pdx.splice(text, sorted(set(edits)))


# ---------------------------------------------------------------- helpers

class Doc:
    """A working-tree file being edited by span splicing."""

    def __init__(self, path):
        self.path = path
        raw = open(os.path.join(TI_ROOT, path), "rb").read()
        self.text, self.bom, _ = decode(raw)
        self.root = pdx.parse(self.text)
        self.edits = []

    def save(self):
        if not self.edits:
            return False
        new = pdx.splice(self.text, _dedupe(self.edits))
        with open(os.path.join(TI_ROOT, self.path), "wb") as f:
            f.write(encode(new, self.bom, True))
        return True


def _dedupe(edits):
    out, last = [], -1
    for s, e, r in sorted(set(edits), key=lambda x: (x[0], x[1])):
        if s < last:
            continue
        out.append((s, e, r))
        last = max(e, s)
    return out


def append_into(doc, blk, texts):
    """insert entries just before blk's closing brace"""
    pos = blk.end - 1
    ind = "\t" * 2
    doc.edits.append((pos, pos, "".join("\n" + ind + t for t in texts) + "\n\t"))


# ---------------------------------------------------------------- merges

def merge_setup_provinces(prev_tree, new_tree, tr_prev, tr_new, log):
    def collect(tree, tr):
        out = {}
        for path, text in tree.items():
            t = translate_provinces(text, tr, log, path)
            root = pdx.parse(t)
            for n in root.items:
                if n.key and n.key.isdigit() and n.is_block:
                    out.setdefault(int(n.key), (t, n))
        return out
    base, theirs = collect(prev_tree, tr_prev), collect(new_tree, tr_new)
    ours = defaultdict(list)
    docs = {}
    for path in sorted(p for p in ls_tree("HEAD", "setup/provinces") if p.endswith(".txt")):
        d = docs[path] = Doc(path)
        for n in d.root.items:
            if n.key and n.key.isdigit() and n.is_block:
                ours[int(n.key)].append((d, n))
    changed = 0
    for pid in sorted(set(base) | set(theirs)):
        b, t = base.get(pid), theirs.get(pid)
        cb, ct = (_canon(b[0], b[1]) if b else None), (_canon(t[0], t[1]) if t else None)
        if cb == ct:
            continue
        if not ours.get(pid):
            log.append(("setup/provinces", str(pid), "not-in-TI:skipped", ""))
            continue
        if t is None:
            log.append(("setup/provinces", str(pid), "Invictus-removed:kept-TI", ""))
            continue
        for d, o in ours[pid]:
            sublog = []
            d.edits += merge_block(b[0] if b else None, b[1].value if b else None, d.text, o.value, t[0], t[1].value,
                                   1, d.path, [str(pid)], sublog)
            log += sublog
            changed += 1
    saved = sum(d.save() for d in docs.values())
    print(f"setup/provinces: {changed} province blocks updated, {saved} files written")


def merge_default(prev_text, new_text, tr_prev, tr_new, log):
    b_text, t_text = translate_default(prev_text, tr_prev), translate_default(new_text, tr_new)
    b_root, t_root = pdx.parse(b_text), pdx.parse(t_text)
    for sec, path in SPLIT.items():
        d = Doc(path)
        containers = [n for n in d.root.items if n.key == sec and n.is_block]
        bsec, tsec = b_root.get(sec), t_root.get(sec)
        if not containers or tsec is None:
            log.append((path, sec, "section-missing", ""))
            continue
        if sec in KEYED:
            inner = KEYED[sec]
            ob = [c.value.get(inner) for c in containers if c.value.get(inner)]
            bb = bsec.value.get(inner).value if bsec else None
            tb = tsec.value.get(inner).value
            ours = {}
            for blk in ob:
                for n in blk.value.items:
                    if n.key is not None:
                        ours.setdefault(n.key, n)
            bk = {n.key: n for n in bb.items if n.key is not None} if bb else {}
            tk = {n.key: n for n in tb.items if n.key is not None}
            added = []
            for k in dict.fromkeys(list(tk) + list(bk)):
                b, t, o = bk.get(k), tk.get(k), ours.get(k)
                cb = _canon(b_text, b) if b is not None else None
                ct = _canon(t_text, t) if t is not None else None
                if cb == ct:
                    continue
                co = _canon(d.text, o) if o is not None else None
                name = f"{sec}/{k}"
                if co == ct:
                    continue
                if o is None and b is None:
                    added.append(t_text[t.start:t.end])
                    log.append((path, name, "added-from-invictus", ""))
                elif o is None:
                    log.append((path, name, "TI-deleted-Invictus-changed:kept-deleted", ""))
                elif t is None:
                    if co == cb:
                        d.edits.append(pdx.node_with_indent(d.text, o) + ("",))
                        log.append((path, name, "deleted-as-invictus", ""))
                    else:
                        log.append((path, name, "TI-changed-Invictus-deleted:kept-TI", ""))
                elif co == cb:
                    d.edits.append((o.start, o.end, t_text[t.start:t.end]))
                else:
                    sub = []
                    d.edits += set_aware_merge(b_text, b, d.text, o, t_text, t, path, name, sub)
                    log += sub
            if added:
                append_into(d, ob[0], added)
        else:
            bset = {_canon(b_text, n) for n in bsec.value.items} if bsec else set()
            tset = {_canon(t_text, n): n for n in tsec.value.items}
            onodes = [n for c in containers for n in c.value.items]
            oset = {_canon(d.text, n) for n in onodes}
            removed = bset - set(tset)
            for n in onodes:
                if _canon(d.text, n) in removed:
                    d.edits.append(pdx.node_with_indent(d.text, n) + ("",))
                    log.append((path, f"{sec}/{_canon(d.text, n)[:60]}", "deleted-as-invictus", ""))
            add = [t_text[n.start:n.end] for c, n in tset.items() if c not in bset and c not in oset]
            for a in add:
                log.append((path, f"{sec}/{' '.join(a.split())[:60]}", "added-from-invictus", ""))
            if add:
                append_into(d, containers[0].value, add)
        d.save()
        print(f"{path}: {sum(1 for r in log if r[0] == path)} changes/notes")


SET_FIELDS = {"own_control_core", "treasures"}


def set_aware_merge(b_text, b, o_text, o, t_text, t, path, name, log):
    """field-level merge of one entity (country/family/treasure); bare-value lists in SET_FIELDS are
    merged as sets: TI's list + Invictus additions - Invictus removals."""
    edits = []
    for field in SET_FIELDS:
        bf, of, tf = (n.value.get(field) if n is not None else None for n in (b, o, t))
        if of is None or tf is None:
            continue
        bv = set(bf.value.values()) if bf else set()
        tv, ov = tf.value.values(), of.value.values()
        add = [v for v in tv if v not in bv and v not in ov]
        rem = {v for v in bv if v not in tv}
        if not add and not (rem & set(ov)):
            continue
        for v in of.value.items:
            if v.key is None and not v.is_block and v.value in rem:
                edits.append((v.start, v.end, ""))
        if add:
            edits.append((of.value.end - 1, of.value.end - 1, " " + " ".join(add) + " "))
        log.append((path, f"{name}/{field}", "set-merged", f"+{add} -{sorted(rem & set(ov))}"))
    # everything else: generic keyed merge, with the set fields already handled
    sub = []
    other = merge_block(b_text, b.value if b is not None else None, o_text, o.value, t_text, t.value, 1, path,
                        [name], sub)
    set_spans = [(n.start, n.end) for n in o.value.items if n.key in SET_FIELDS]
    for s, e, r in other:
        if any(ss <= s and e <= se and not (s == e == se) for ss, se in set_spans):
            continue
        edits.append((s, e, r))
    log += [x for x in sub if x[1].split("/")[-1].split("[")[0] not in SET_FIELDS]
    return edits


def reset_targets():
    """Start from HEAD's version of every file this script writes, so re-runs are idempotent."""
    head = ls_tree("HEAD", "setup/provinces", *SPLIT.values())
    blobs = read_blobs([v[2] for v in head.values()])
    for path, v in head.items():
        text, bom, _ = decode(blobs[v[2]])
        with open(os.path.join(TI_ROOT, path), "wb") as f:
            f.write(encode(text, bom, True))


def main(prev_ref, new_ref, prev_csv, new_csv):
    tr_prev, tr_new = Translator(prev_csv), Translator(new_csv)
    log = []
    reset_targets()

    def tree(ref):
        t = ls_tree(ref, "setup/provinces")
        paths = [p for p in t if p.endswith(".txt")]
        blobs = read_blobs([t[p][2] for p in paths])
        return {p: decode(blobs[t[p][2]])[0] for p in paths}

    merge_setup_provinces(tree(prev_ref), tree(new_ref), tr_prev, tr_new, log)
    t = ls_tree(prev_ref, "setup/main/00_default.txt")["setup/main/00_default.txt"][2]
    u = ls_tree(new_ref, "setup/main/00_default.txt")["setup/main/00_default.txt"][2]
    blobs = read_blobs([t, u])
    merge_default(decode(blobs[t])[0], decode(blobs[u])[0], tr_prev, tr_new, log)
    out = os.path.join(HERE, "reports", "setup_merge.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "key", "outcome", "detail"])
        w.writerows(log)
    from collections import Counter
    print(Counter(r[2] for r in log).most_common())


if __name__ == "__main__":
    main(*sys.argv[1:5])
