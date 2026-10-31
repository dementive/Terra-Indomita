"""Keep TI characters' portrait DNA pointing at the templates their authors chose.

DNA stores gene templates by their numeric `index` in common/genes/00_genes.txt. When a merge gives an
index to a different template (e.g. the January 2025 merge moved japanese_hairstyles 18 -> 19 and
put egyptian_pharaoh_hairstyles on 18), every TI character created before that silently changes
look. For each DNA string last written by a TI commit, this reads the genes file as of that commit,
resolves each template index to its name, and rewrites it to that template's current index.

Usage: python remap_dna.py [--dry-run]
"""
import base64
import csv
import os
import sys

import pdx
from audit_chars import blame
from gitio import TI_ROOT, decode, encode, git

HERE = os.path.dirname(__file__)
_cache = {}


def genes_at(ref):
    sha = git("rev-parse", f"{ref}:common/genes/00_genes.txt").decode().strip()
    if sha not in _cache:
        root = pdx.parse(decode(git("cat-file", "-p", sha))[0])
        layout = [("color", n.key) for n in root.get("color_genes").value.items if n.key]
        idx = {}
        for sec in ("morph_genes", "accessory_genes"):
            for g in root.get(sec).value.items:
                if g.key and g.is_block:
                    layout.append((sec, g.key))
                    idx[g.key] = {int(t.value.get("index").value): t.key for t in g.value.items
                                  if t.is_block and t.value.get("index") is not None}
        _cache[sha] = (layout, idx)
    return _cache[sha]


def main(dry_run=False):
    cur_layout, cur_idx = genes_at("HEAD")
    by_name = {g: {name: i for i, name in m.items()} for g, m in cur_idx.items()}
    upstream = set()
    for ref in ("f2e32b70d", "upstream/main", "invictus-translated"):
        upstream |= set(git("rev-list", ref).decode().split())
    log = []
    char_dir = os.path.join(TI_ROOT, "setup/characters")
    for f in sorted(os.listdir(char_dir)):
        if not f.endswith(".txt"):
            continue
        path = f"setup/characters/{f}"
        text, bom, _ = decode(open(os.path.join(char_dir, f), "rb").read())
        edits, bl = [], None
        for top in pdx.parse(text).items:
            if not top.is_block:
                continue
            for c in top.value.items:
                d = c.value.get("dna") if c.key and c.key.isdigit() and c.is_block else None
                if d is None:
                    continue
                bl = bl or blame("HEAD", path)
                commit = bl[text.count("\n", 0, d.start) + 1][0]
                if commit in upstream:
                    continue  # Invictus-authored DNA follows Invictus's own indices
                layout, idx = genes_at(commit)
                if layout != cur_layout:
                    log.append((path, c.key, "SKIPPED: gene layout changed since authoring", "", "", commit[:10]))
                    continue
                raw = d.value
                b = bytearray(base64.b64decode(raw + "=" * (-len(raw) % 4)))
                changed = False
                for i, (sec, g) in enumerate(layout):
                    if sec == "color" or 4 * i + 4 > len(b):
                        continue
                    for off in (0, 2):
                        old = b[4 * i + off]
                        name = idx.get(g, {}).get(old)
                        new = by_name.get(g, {}).get(name)
                        if name is not None and new is not None and new != old:
                            b[4 * i + off] = new
                            changed = True
                            log.append((path, c.key, g, f"{name}: {old} -> {new}", "dominant" if off == 0 else "recessive", commit[:10]))
                if changed:
                    enc = base64.b64encode(bytes(b)).decode()
                    if not raw.endswith("="):
                        enc = enc.rstrip("=")
                    edits.append((d.val_start, d.val_end, f'"{enc}"' if text[d.val_start] == '"' else enc))
        if edits and not dry_run:
            open(os.path.join(char_dir, f), "wb").write(encode(pdx.splice(text, edits), bom, True))
    with open(os.path.join(HERE, "reports", "remap_dna.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "character", "gene", "change", "slot", "dna_written_in"])
        w.writerows(log)
    for r in log:
        print(*r)


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
