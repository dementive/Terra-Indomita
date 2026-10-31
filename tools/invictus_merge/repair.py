"""Repair stale IDs in a Terra-Indomita ref before merging Invictus, writing into the working tree.

1. Character references: apply every proposed change in reports/char_audit.csv (audit_chars.py).
2. Province IDs, tags and area/region names in lines TI inherited from Invictus and never edited:
   for each TI file that exists in the Invictus base, 3-way merge-file(base, TI, translate(base)).
   Only untouched lines take the translation; where TI edited near a translated line, TI's text is
   kept and the file is listed in reports/repair_conflicts.csv for a manual look.

Usage: python repair.py <ti_ref> <inv_base_ref>
"""
import csv
import os
import subprocess
import sys
import tempfile
from collections import defaultdict

from gitio import TI_ROOT, decode, encode, git, ls_tree, read_blobs
from refs import character_refs
from translate import Translator, is_ti_owned

HERE = os.path.dirname(__file__)


def renames(base_ref, ti_ref):
    out = git("diff", "--name-status", "-M90%", "--diff-filter=R", base_ref, ti_ref).decode("utf-8")
    res = {}
    for line in out.splitlines():
        parts = line.split("\t")
        res[parts[2]] = parts[1]  # ti_path -> base_path
    return res


def merge_file(ours, base, theirs):
    """git merge-file on strings -> (merged_text_favouring_ours, n_conflicts)"""
    with tempfile.TemporaryDirectory() as d:
        paths = []
        for name, txt in (("ours", ours), ("base", base), ("theirs", theirs)):
            p = os.path.join(d, name)
            with open(p, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
                f.write(txt)
            paths.append(p)
        n = subprocess.run(["git", "merge-file", "-p", *paths], capture_output=True).returncode
        res = subprocess.run(["git", "merge-file", "-p", "--ours", *paths], capture_output=True)
        return res.stdout.decode("utf-8", errors="surrogateescape"), n


def main(ti_ref, base_ref):
    tree = ls_tree(ti_ref)
    base_tree = ls_tree(base_ref)
    texts = {}

    def get(path):
        if path not in texts:
            raw = read_blobs([tree[path][2]])[tree[path][2]]
            texts[path] = list(decode(raw))
        return texts[path]

    # 1. characters
    with open(os.path.join(HERE, "reports", "char_audit.csv"), encoding="utf-8") as f:
        audit = list(csv.DictReader(f))
    by_line = defaultdict(list)
    for r in audit:
        by_line[(r["path"], int(r["line"]))].append(r)
    nchar = 0
    for (path, ln), rows in sorted(by_line.items()):
        if not any(r["change"] == "yes" for r in rows):
            continue
        t = get(path)
        lines = t[0].split("\n")
        line = lines[ln - 1]
        refs = character_refs(path, line)
        assert [r[0] for r in refs] == [int(r["old"]) for r in rows], (path, ln)
        edits = []
        for (cid, s, e), r in zip(refs, rows):
            if r["change"] == "yes":
                edits.append((s, e, r["new"]))
                nchar += 1
        for s, e, new in sorted(edits, reverse=True):
            line = line[:s] + new + line[e:]
        lines[ln - 1] = line
        t[0] = "\n".join(lines)
    print("character references changed:", nchar)

    # 2. provinces / tags / areas in untouched inherited lines
    tr = Translator("provinces_base.csv")
    ren = renames(base_ref, ti_ref)
    conflicts, nfiles, log = [], 0, []
    base_blobs = {}
    candidates = []
    for path, v in tree.items():
        if v[1] != "blob" or not path.endswith((".txt", ".yml")) or is_ti_owned(path):
            continue
        bpath = path if path in base_tree else ren.get(path)
        if bpath and bpath in base_tree:
            candidates.append((path, bpath))
    base_blobs = read_blobs([base_tree[b][2] for _, b in candidates])
    for path, bpath in sorted(candidates):
        btext = decode(base_blobs[base_tree[bpath][2]])[0]
        flog = []
        tx = tr.translate_text(bpath, btext, flog, drop_names=False)
        if tx == btext:
            continue
        t = get(path)
        merged, n = merge_file(t[0], btext, tx)
        if n:
            conflicts.append((path, n))
        if merged != t[0]:
            nfiles += 1
            t[0] = merged
            log += [(path,) + x[1:] for x in flog]
    print("files with translated inherited lines:", nfiles, "| files with conflicting hunks kept as TI:", len(conflicts))

    # write changed files to the working tree (CRLF like the rest of the checkout). Re-runs are
    # idempotent: files a previous run modified that no longer need changes go back to ti_ref.
    previously = set(git("diff", "--name-only").decode("utf-8").splitlines())
    changed = 0
    for path, (text, bom, _) in texts.items():
        orig = decode(read_blobs([tree[path][2]])[tree[path][2]])[0]
        if text == orig:
            continue
        with open(os.path.join(TI_ROOT, path), "wb") as f:
            f.write(encode(text, bom, True))
        changed += 1
    for path in previously:
        if path in tree and (path not in texts or texts[path][0] == decode(read_blobs([tree[path][2]])[tree[path][2]])[0]):
            raw = read_blobs([tree[path][2]])[tree[path][2]]
            text, bom, _ = decode(raw)
            with open(os.path.join(TI_ROOT, path), "wb") as f:
                f.write(encode(text, bom, True))
    print("files written:", changed)
    os.makedirs(os.path.join(HERE, "reports"), exist_ok=True)
    with open(os.path.join(HERE, "reports", "repair_conflicts.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "conflicting_hunks"])
        w.writerows(conflicts)
    with open(os.path.join(HERE, "reports", "repair_translations.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "line", "kind", "old", "new", "confidence"])
        w.writerows(log)


if __name__ == "__main__":
    main(*sys.argv[1:3])
