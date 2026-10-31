"""Keyed 3-way merges for Paradox script and localisation, used instead of line merges where TI and
Invictus both reworked a file.

Script: children of a block are matched by (key, occurrence). For each child:
  same on both sides -> keep; changed on one side only -> take that side (including add/delete);
  changed on both -> recurse into it if both are blocks and depth allows, else keep TI's and log it.
Text is spliced into TI's file, so untouched regions stay byte-identical.
Localisation: same rule per loc key; Invictus-only keys are inserted after their predecessor.

CLI (during a conflicted merge, reads index stages 1/2/3):
  python semantic_merge.py script <depth> <path>...
  python semantic_merge.py loc <path>...
Conflicts kept as TI are appended to reports/semantic_conflicts.csv.
"""
import csv
import os
import re
import sys

import pdx
from gitio import TI_ROOT, decode, encode, git

HERE = os.path.dirname(__file__)
AI_WEIGHT_KEYS = {"chance", "ai_will_do", "ai_chance", "ai_weight"}


def _children(text, blk):
    """{(key, n): node} preserving order; bare (unkeyed) values collapse into one ('#values', 0) entry."""
    out, counts = {}, {}
    vals = []
    for n in blk.items:
        if n.key is None:
            vals.append(n)
            continue
        k = (n.key, counts.get(n.key, 0))
        counts[n.key] = k[1] + 1
        out[k] = n
    if vals:
        out[("#values", 0)] = vals
    return out


def _canon(text, node):
    if node is None:
        return None
    if isinstance(node, list):
        return " ".join(pdx.canon(text, v) for v in node)
    return pdx.canon(text, node)


def _span(node):
    if isinstance(node, list):
        return node[0].start, node[-1].end
    return node.start, node.end


def _src(text, node):
    s, e = _span(node)
    return text[s:e]


def merge_block(b_text, b_blk, o_text, o_blk, t_text, t_blk, depth, path, trail, log):
    """Returns list of edits [(start, end, replacement)] against o_text for this block's children."""
    bc = _children(b_text, b_blk) if b_blk is not None else {}
    oc = _children(o_text, o_blk)
    tc = _children(t_text, t_blk)
    edits = []
    t_order = list(tc.keys())
    for k in list(dict.fromkeys(list(oc) + t_order + list(bc))):
        b, o, t = bc.get(k), oc.get(k), tc.get(k)
        cb, co, ct = _canon(b_text, b), _canon(o_text, o), _canon(t_text, t)
        name = "/".join(trail + [f"{k[0]}" + (f"[{k[1]}]" if k[1] else "")])
        if co == ct or ct == cb:
            continue  # nothing to take from Invictus
        if co == cb:
            # only Invictus changed this child: take its version (add / replace / delete)
            if o is None:
                anchor = _insert_point(o_text, o_blk, oc, t_order, k)
                indent = _indent_of(o_text, o_blk, oc)
                edits.append((anchor, anchor, "\n" + indent + _src(t_text, t)))
                log.append((path, name, "added-from-invictus", ""))
            elif t is None:
                s, e = pdx.node_with_indent(o_text, o) if not isinstance(o, list) else _span(o)
                edits.append((s, e, ""))
                log.append((path, name, "deleted-as-invictus", ""))
            else:
                s, e = _span(o)
                edits.append((s, e, _src(t_text, t)))
            continue
        # both changed
        if k[0] in AI_WEIGHT_KEYS and o is not None and t is not None:
            # Invictus reworks AI weights systematically (script values shipped with the merge);
            # TI's edits to the same weights were local tweaks, so Invictus's version wins here
            s, e = _span(o)
            edits.append((s, e, _src(t_text, t)))
            log.append((path, name, "both-changed:took-Invictus-AI-weights", ""))
            continue
        if (depth > 0 and o is not None and t is not None and not isinstance(o, list) and not isinstance(t, list)
                and o.is_block and t.is_block and (b is None or (not isinstance(b, list) and b.is_block))):
            edits += merge_block(b_text, b.value if b is not None else None, o_text, o.value, t_text, t.value,
                                 depth - 1, path, trail + [k[0]], log)
            continue
        kind = "both-changed:kept-TI" if o is not None and t is not None else (
            "TI-deleted-Invictus-changed:kept-deleted" if o is None else "TI-changed-Invictus-deleted:kept-TI")
        log.append((path, name, kind, (_src(t_text, t) if t is not None else "")[:300].replace("\n", " ")))
    return edits


def _indent_of(text, blk, oc):
    for v in oc.values():
        n = v[0] if isinstance(v, list) else v
        ls = pdx.line_start(text, n.start)
        if text[ls:n.start].strip() == "":
            return text[ls:n.start]
    return "\t"


def _insert_point(o_text, o_blk, oc, t_order, k):
    """after the nearest preceding sibling (in Invictus order) that exists in TI, else at block end"""
    i = t_order.index(k)
    for prev in reversed(t_order[:i]):
        if prev in oc:
            return _span(oc[prev])[1]
    for nxt in t_order[i + 1:]:
        if nxt in oc:
            s = _span(oc[nxt])[0]
            return pdx.line_start(o_text, s) - 1 if pdx.line_start(o_text, s) > 0 else s
    is_root = o_text[o_blk.start:o_blk.start + 1] != "{"
    if is_root:
        return len(o_text.rstrip())
    return o_blk.end - 1


def merge_script(b_text, o_text, t_text, depth, path, log):
    b_blk = pdx.parse(b_text) if b_text is not None else None
    edits = merge_block(b_text, b_blk, o_text, pdx.parse(o_text), t_text, pdx.parse(t_text), depth, path, [], log)
    return pdx.splice(o_text, _dedupe(edits))


def _dedupe(edits):
    edits = sorted(set(edits), key=lambda e: (e[0], e[1]))
    out, last = [], -1
    for s, e, r in edits:
        if s < last:
            continue
        out.append((s, e, r))
        last = max(e, s)
    return out


LOC_RE = re.compile(r'^(\s*)([^\s#:"]+):(\d*)\s*(".*)?$')


def _loc_entries(text):
    """ordered list of (key, line) plus {key: line_index}"""
    lines = text.split("\n")
    keys = {}
    for i, line in enumerate(lines):
        m = LOC_RE.match(line)
        if m and m.group(4) is not None:
            keys.setdefault(m.group(2), i)
    return lines, keys


def merge_loc(b_text, o_text, t_text, path, log):
    bl, bk = _loc_entries(b_text or "")
    ol, ok = _loc_entries(o_text)
    tl, tk = _loc_entries(t_text)
    norm = lambda s: " ".join(s.split()) if s is not None else None
    val = lambda lines, keys, k: norm(lines[keys[k]]) if k in keys else None
    replace, delete, insert_after = {}, set(), {}
    t_order = sorted(tk, key=tk.get)
    for k in dict.fromkeys(list(ok) + t_order + list(bk)):
        b, o, t = val(bl, bk, k), val(ol, ok, k), val(tl, tk, k)
        if o == t or t == b:
            continue
        if o == b:
            if o is None:
                i = t_order.index(k)
                prev = next((p for p in reversed(t_order[:i]) if p in ok), None)
                insert_after.setdefault(ok[prev] if prev else ok[min(ok, key=ok.get)] if ok else 0, []).append(tl[tk[k]])
                log.append((path, k, "added-from-invictus", ""))
            elif t is None:
                delete.add(ok[k])
                log.append((path, k, "deleted-as-invictus", ""))
            else:
                replace[ok[k]] = tl[tk[k]]
            continue
        log.append((path, k, "both-changed:kept-TI" if o and t else "one-deleted:kept-TI", (tl[tk[k]] if t else "")[:300]))
    out = []
    for i, line in enumerate(ol):
        if i not in delete:
            out.append(replace.get(i, line))
        out += insert_after.get(i, [])
    return "\n".join(out)


def stage(i, path):
    try:
        return decode(git("show", f":{i}:{path}"))
    except RuntimeError:
        return None


def write_log(log):
    out = os.path.join(HERE, "reports", "semantic_conflicts.csv")
    new = not os.path.exists(out)
    with open(out, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["path", "key", "outcome", "invictus_version"])
        w.writerows(log)


def main(mode, *args):
    log = []
    if mode == "script":
        depth, paths = int(args[0]), args[1:]
    else:
        paths = args
    for path in paths:
        b, o, t = stage(1, path), stage(2, path), stage(3, path)
        bt = b[0] if b else None
        if mode == "script":
            merged = merge_script(bt, o[0], t[0], depth, path, log)
        else:
            merged = merge_loc(bt, o[0], t[0], path, log)
        with open(os.path.join(TI_ROOT, path), "wb") as f:
            f.write(encode(merged, o[1], True))
        n = sum(1 for r in log if r[0] == path and r[2].startswith(("both", "TI-", "one-")))
        print(f"{n}\tkept-TI conflicts\t{path}")
    write_log(log)


if __name__ == "__main__":
    main(*sys.argv[1:])
