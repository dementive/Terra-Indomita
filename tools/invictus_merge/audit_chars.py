"""Audit every character reference in a TI ref by resolving it to the person its author meant.

Two signals, in order:
  1. Base-line template: if the line equals an Invictus base line except for the character IDs, it
     is an Invictus line, and base's IDs are what it should say (TI's earlier renumbering scripts
     corrupted some of these, e.g. Philip II char:35 -> char:714).
  2. Blame: the commit that last wrote the line, and that commit's character table, say who the ID
     meant then. That person is then located in the post-merge table (Invictus main for IDs below
     TI_FIRST_ID, TI's own characters at TI_FIRST_ID and above). Lines last written by the 2024
     renumbering script (BAD_SCRIPT_COMMIT) are resolved from the line as it was before it ran.

Writes reports/char_audit.csv with one row per reference and the proposed ID.

Usage: python audit_chars.py <ti_ref> <inv_base_ref> <inv_main_ref>
"""
import csv
import difflib
import os
import re
import sys
from collections import Counter

from chars import Matcher, describe, load_table
from gitio import decode, git, ls_tree, read_blobs, show
from refs import character_refs

HERE = os.path.dirname(__file__)
TI_FIRST_ID = 1516
BASE_MAX = 551
BAD_SCRIPT_COMMIT = "42034630d"


def blame(ref, path):
    """final_line -> (commit, orig_line, path_in_that_commit)"""
    out = git("blame", "--porcelain", ref, "--", path).decode("utf-8", errors="replace")
    fname, pending, cur = {}, [], None
    for line in out.split("\n"):
        m = re.match(r"^([0-9a-f]{40}) (\d+) (\d+)", line)
        if m:
            cur = m.group(1)
            pending.append((int(m.group(3)), cur, int(m.group(2))))
        elif line.startswith("filename ") and cur:
            fname[cur] = line[9:]
    return {final: (c, orig, fname.get(c, path)) for final, c, orig in pending}


def template(path, line):
    """line with character IDs blanked and whitespace collapsed, plus the IDs in order"""
    refs = character_refs(path, line)
    out, last = [], 0
    for _, s, e in refs:
        out.append(line[last:s])
        out.append("#")
        last = e
    out.append(line[last:])
    return " ".join("".join(out).split()), [r[0] for r in refs]


def same_person(a, b):
    if not a or not b:
        return False
    return (a.get("first_name"), a.get("birth_date")) == (b.get("first_name"), b.get("birth_date"))


def row(path, ln, cid, new, origin, how, commit, person, final, line_text, note):
    return {
        "path": path, "line": ln, "old": cid, "new": "" if new is None else new,
        "change": "yes" if new is not None and new != cid else ("UNRESOLVED" if new is None else ""),
        "origin": origin, "how": how, "commit": (commit or "")[:10], "meant": describe(person),
        "resolves_to_now": describe(final.get(cid)),
        "after_fix": describe(final.get(new) if new is not None else None),
        "note": note, "text": line_text.strip()[:160],
    }


def main(ti_ref, base_ref, main_ref, check=False):
    """check=True: verify a merged ref instead of proposing repairs. Every line is resolved through
    blame against its own commit's table (Invictus lines blame to the vendor commit) and compared
    with ti_ref's own table; any row with change=yes or UNRESOLVED is a reference that changed
    meaning."""
    bad = git("rev-parse", BAD_SCRIPT_COMMIT).decode().strip()
    inv_commits = set() if check else set(git("rev-list", base_ref).decode().split())
    base_tab = load_table(base_ref)
    main_tab = load_table(main_ref)
    ti_tab = load_table(ti_ref)
    if check:
        final = {k: v for k, v in ti_tab.items() if isinstance(k, int)}
    else:
        final = {k: v for k, v in main_tab.items() if isinstance(k, int)}
        final.update({k: v for k, v in ti_tab.items() if isinstance(k, int) and k >= TI_FIRST_ID})
    final_m = Matcher(final)

    tree = ls_tree(ti_ref)
    paths = [p for p in tree if p.endswith((".txt", ".yml")) and not p.startswith(("map_data/", "gfx/", "tools/"))]
    blobs = read_blobs([tree[p][2] for p in paths])
    base_tree = ls_tree(base_ref)
    by_basename = {}
    for bp in base_tree:
        by_basename.setdefault(os.path.basename(bp), set()).add(bp)
    base_cache, era_cache = {}, {}

    def base_text(bp):
        if bp not in base_cache:
            base_cache[bp] = decode(read_blobs([base_tree[bp][2]])[base_tree[bp][2]])[0]
        return base_cache[bp]

    def table_at(commit):
        if commit not in era_cache:
            era_cache[commit] = load_table(commit)
        return era_cache[commit]

    rows = []
    for path in sorted(paths):
        text, _, _ = decode(blobs[tree[path][2]])
        refs = character_refs(path, text)
        if not refs:
            continue
        bl = blame(ti_ref, path)
        lines = text.split("\n")
        base_paths = {path} | {v[2] for v in bl.values()} | by_basename.get(os.path.basename(path), set())
        primary = next((bp for bp in [path] + sorted({v[2] for v in bl.values()}) if bp in base_tree), None)
        aligned = {}
        if primary:
            ti_t = [template(path, l)[0] for l in lines]
            b_lines = base_text(primary).split("\n")
            b_t = [template(primary, l)[0] for l in b_lines]
            sm = difflib.SequenceMatcher(None, ti_t, b_t, autojunk=False)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == "equal":
                    for k in range(i2 - i1):
                        aligned[i1 + k + 1] = b_lines[j1 + k]
        base_tmpl = {}
        for bp in base_paths:
            if bp in base_tree and bp.endswith((".txt", ".yml")):
                for bline in base_text(bp).split("\n"):
                    t, ids = template(bp, bline)
                    if ids:
                        base_tmpl.setdefault(t, set()).add(tuple(ids))
        for cid, s, e in refs:
            ln = text.count("\n", 0, s) + 1
            commit, orig, cpath = bl.get(ln, (None, None, path))
            line_text = lines[ln - 1]
            col = s - (text.rfind("\n", 0, s) + 1)
            lrefs = character_refs(path, line_text)
            ordinal = next((i for i, r in enumerate(lrefs) if r[1] == col), 0)

            t, _ = template(path, line_text)
            cands = base_tmpl.get(t, set()) if not check else set()
            if len(cands) == 1 and len(t.replace("#", "").strip()) >= 20:
                new = next(iter(cands))[ordinal]
                how = "inv-line-untouched" if new == cid else "restored-from-base-line"
                note = "" if new == cid else f"Invictus base line has {new}"
                rows.append(row(path, ln, cid, new, "INV", how, commit, base_tab.get(new), final, line_text, note))
                continue

            if ln in aligned and not check:
                bids = [r[0] for r in character_refs(primary, aligned[ln])]
                if len(bids) == len(lrefs):
                    new = bids[ordinal]
                    how = "inv-line-untouched" if new == cid else "restored-by-alignment"
                    note = "" if new == cid else f"aligned Invictus base line has {new}"
                    rows.append(row(path, ln, cid, new, "INV", how, commit, base_tab.get(new), final, line_text, note))
                    continue

            era_id, era_commit, note = cid, commit, ""
            origin = "INV" if commit in inv_commits else "TI"
            if commit == bad:
                try:
                    pline = decode(show(bad + "^", cpath))[0].split("\n")[orig - 1]
                except Exception:
                    pline = ""
                prefs = character_refs(path, pline)
                if prefs and len(prefs) == len(lrefs):
                    era_id, era_commit = prefs[ordinal][0], bad + "^"
                    note = f"pre-script line had {era_id}"
                else:
                    note = "PRE-SCRIPT LINE NOT FOUND"
            person = table_at(era_commit).get(era_id) if era_commit else None
            if origin == "INV":
                new, how = cid, "inv-line-untouched"
            elif person is None:
                if cid < BASE_MAX and same_person(base_tab.get(cid), main_tab.get(cid)):
                    new, how = cid, "stable-base-id"
                    note = "commit's table incomplete; base and Invictus main agree on this ID"
                else:
                    new, how = None, "undefined-at-commit"
            elif person.get("first_name") == "Dudley":
                guess = cid + 1000
                new, how = (guess, "dudley+1000") if guess in final and guess >= TI_FIRST_ID else (None, "dudley-placeholder")
                note = "written after the +1000 shift with an old-scheme ID; assumed +1000"
            elif final.get(era_id) == person:
                new, how = era_id, "same-record"
            else:
                new, how = final_m.find(person, hint_id=era_id if era_id < TI_FIRST_ID else None)
                if new is None:
                    same = [k for k, v in final.items() if v == person or {kk: vv for kk, vv in v.items() if kk != "file"} == {kk: vv for kk, vv in person.items() if kk != "file"}]
                    if len(same) == 1:
                        new, how = same[0], "record-match"
            rows.append(row(path, ln, cid, new, origin, how, commit, person, final, line_text, note))

    os.makedirs(os.path.join(HERE, "reports"), exist_ok=True)
    out = os.path.join(HERE, "reports", "char_check.csv" if check else "char_audit.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("refs:", len(rows))
    print(Counter((r["origin"], r["change"], r["how"]) for r in rows).most_common())
    print("wrote", out)


if __name__ == "__main__":
    if sys.argv[1] == "check":  # python audit_chars.py check <merged_ref> <vendor_ref>
        main(sys.argv[2], sys.argv[3], sys.argv[3], check=True)
    else:
        main(*sys.argv[1:4])
