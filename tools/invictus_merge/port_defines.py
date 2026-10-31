"""Port Invictus's changes to a file TI replaced with its own copy (e.g. 00_defines_invictus.txt ->
TI's 00_defines.txt), key by key inside each top-level namespace block:
  TI value == Invictus's previous value (or TI lacks the key) -> take Invictus's new value
  TI changed the value itself                                  -> keep TI's, log it
Values listed in MAP_SCALED are pixel distances on Invictus's map and get scaled to TI's map.

Usage: python port_defines.py <inv_prev_ref> <inv_new_ref> <inv_path> <ti_path>
"""
import csv
import os
import sys

import pdx
from gitio import TI_ROOT, decode, encode, git

HERE = os.path.dirname(__file__)
TI_MAP_SCALE = 0.515  # TI's provinces.png is Invictus's world scaled ~0.515 horizontally
MAP_SCALED = {"MAX_RECON_DISTANCE_NAVY"}


def keyed(text):
    out = {}
    for ns in pdx.parse(text).items:
        if ns.is_block:
            for n in ns.value.items:
                if n.key is not None and not n.is_block:
                    out[(ns.key, n.key)] = n
    return out


def main(prev_ref, new_ref, inv_path, ti_path):
    b_text = decode(git("show", f"{prev_ref}:{inv_path}"))[0]
    t_text = decode(git("show", f"{new_ref}:{inv_path}"))[0]
    p = os.path.join(TI_ROOT, ti_path)
    o_text, bom, _ = decode(open(p, "rb").read())
    b, t, o = keyed(b_text), keyed(t_text), keyed(o_text)
    o_root = pdx.parse(o_text)
    edits, log, adds = [], [], {}
    for k, tn in t.items():
        bn = b.get(k)
        if bn is not None and bn.value == tn.value:
            continue
        new = tn.value
        if k[1] in MAP_SCALED and new.replace(".", "").isdigit():
            new = str(round(float(new) * TI_MAP_SCALE))
        line = o_text and t_text[tn.start:t_text.find("\n", tn.start) if "\n" in t_text[tn.start:] else len(t_text)]
        if k[1] in MAP_SCALED:
            line = f"{k[1]} = {new} # Invictus: {tn.value} (\"Italy -> Albion\") scaled to TI's map"
        on = o.get(k)
        if on is None:
            adds.setdefault(k[0], []).append(line.strip())
            log.append((ti_path, "/".join(k), "added", new))
        elif bn is not None and on.value != bn.value and on.value != tn.value:
            log.append((ti_path, "/".join(k), "kept TI", f"TI {on.value}, Invictus {bn.value}->{tn.value}"))
        elif on.value != new:
            edits.append((on.val_start, on.val_end, new))
            log.append((ti_path, "/".join(k), "updated", f"{on.value}->{new}"))
    for ns_name, lines in adds.items():
        ns = next((n for n in o_root.items if n.key == ns_name and n.is_block), None)
        if ns is None:
            log.append((ti_path, ns_name, "namespace missing in TI file; not added", "; ".join(lines)))
            continue
        pos = ns.value.end - 1
        edits.append((pos, pos, "\n\t# From Invictus 1.12\n" + "".join(f"\t{l}\n" for l in lines)))
    open(p, "wb").write(encode(pdx.splice(o_text, sorted(edits)), bom, True))
    out = os.path.join(HERE, "reports", "ported_defines.csv")
    new_file = not os.path.exists(out)
    with open(out, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["file", "key", "action", "detail"])
        w.writerows(log)
    for r in log:
        print(*r)


if __name__ == "__main__":
    main(*sys.argv[1:5])
