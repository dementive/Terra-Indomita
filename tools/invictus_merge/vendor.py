"""Create commits on the orphan branch `invictus-translated`: each one is an Invictus ref translated
into Terra-Indomita's ID space (translate.py), without the paths TI owns.

First run (no branch yet):  python vendor.py init <inv_base_ref> <inv_new_ref> <ti_ref>
    -> V0 = translate(inv_base_ref), V1 = translate(inv_new_ref) on top of it
Later merges:               python vendor.py next <inv_new_ref> <ti_ref>
    -> one more commit translate(inv_new_ref) on top of the branch

Provinces whose Invictus definition is unchanged since the previous vendor commit keep the mapping
that commit used, so remapping noise never shows up as an upstream change.
"""
import csv
import os
import sys
import time

from gitio import git, rev_parse
from mapdata import load_definitions
from translate import Translator, ti_deliberate_deletions, vendor_tree

HERE = os.path.dirname(__file__)
BRANCH = "refs/heads/invictus-translated"


def stabilise(tr_new, tr_prev, prev_ref, new_ref):
    dp, dn = load_definitions(prev_ref), load_definitions(new_ref)
    pinned = 0
    for pid, ti in tr_prev.pmap.items():
        if dp.get(pid) == dn.get(pid) and tr_new.pmap.get(pid) != ti:
            tr_new.pmap[pid], tr_new.pconf[pid] = ti, tr_prev.pconf[pid]
            pinned += 1
    return pinned


def fast_import_commit(tree, message, parent=None, mark=1):
    name = git("config", "user.name").decode().strip()
    email = git("config", "user.email").decode().strip()
    now = int(time.time())
    msg = message.encode()
    out = [f"commit {BRANCH}\nmark :{mark}\n".encode(),
           f"author {name} <{email}> {now} +0000\ncommitter {name} <{email}> {now} +0000\n".encode(),
           b"data %d\n" % len(msg), msg, b"\n"]
    if parent:
        out.append(f"from {parent}\n".encode())
    out.append(b"deleteall\n")
    for path, (mode, sha, data) in sorted(tree.items()):
        p = path.encode("utf-8")
        if p.startswith(b'"') or b"\n" in p:
            raise ValueError(f"unsupported path {path!r}")
        if data is None:
            out.append(b"M %s %s %s\n" % (mode.encode(), sha.encode(), p))
        else:
            out.append(b"M %s inline %s\ndata %d\n" % (mode.encode(), p, len(data)))
            out.append(data)
            out.append(b"\n")
    out.append(b"\n")
    return b"".join(out)


def write_log(name, log):
    os.makedirs(os.path.join(HERE, "reports"), exist_ok=True)
    with open(os.path.join(HERE, "reports", name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "line", "kind", "old", "new", "confidence"])
        w.writerows(log)


def main(mode, *args):
    if mode == "init":
        base_ref, new_ref, ti_ref = args
        ti_deleted = ti_deliberate_deletions(base_ref, ti_ref)
        tr0, tr1 = Translator("provinces_base.csv"), Translator("provinces.csv")
        print("pinned unchanged provinces to base mapping:", stabilise(tr1, tr0, base_ref, new_ref))
        log0, log1 = [], []
        t0 = vendor_tree(base_ref, tr0, ti_deleted, log0)
        t1 = vendor_tree(new_ref, tr1, ti_deleted, log1)
        s0, s1 = rev_parse(base_ref), rev_parse(new_ref)
        stream = fast_import_commit(t0, f"Invictus {s0[:10]} translated to Terra-Indomita IDs\n\nSource: SnowletTV/Invictus {s0}\n", mark=1)
        stream += fast_import_commit(t1, f"Invictus {s1[:10]} translated to Terra-Indomita IDs\n\nSource: SnowletTV/Invictus {s1}\n", parent=":1", mark=2)
        write_log(f"vendor_{s0[:10]}.csv", log0)
        write_log(f"vendor_{s1[:10]}.csv", log1)
    elif mode == "next":
        new_ref, ti_ref = args
        prev = rev_parse(BRANCH)
        prev_src = git("log", "-1", "--format=%b", prev).decode().split("Invictus ")[-1].split()[0]
        ti_deleted = ti_deliberate_deletions(prev_src, ti_ref)
        tr_prev, tr = Translator("provinces_base.csv"), Translator("provinces.csv")
        print("pinned:", stabilise(tr, tr_prev, prev_src, new_ref))
        log = []
        t = vendor_tree(new_ref, tr, ti_deleted, log)
        s = rev_parse(new_ref)
        stream = fast_import_commit(t, f"Invictus {s[:10]} translated to Terra-Indomita IDs\n\nSource: SnowletTV/Invictus {s}\n", parent=prev)
        write_log(f"vendor_{s[:10]}.csv", log)
    else:
        raise SystemExit(__doc__)
    git("fast-import", "--quiet", "--force", input=stream)
    print(git("log", "--oneline", "-3", BRANCH).decode())


if __name__ == "__main__":
    main(*sys.argv[1:])
