"""Compare two imperator-tiger --json reports and list findings that are new in the second.
Findings are matched on (rule key, file, message, source line text), so line-number shifts from the
merge don't count as changes.

Usage: python tiger_diff.py <before.json> <after.json> [out.csv]
"""
import csv
import json
import sys
from collections import Counter


def keys(path):
    out = Counter()
    for r in json.load(open(path, encoding="utf-8")):
        loc = r["locations"][0] if r.get("locations") else {}
        out[(r["severity"], r["key"], (loc.get("path") or "").replace("\\", "/"), r["message"],
             (loc.get("line") or "").strip())] += 1
    return out


def main(before, after, out=None):
    b, a = keys(before), keys(after)
    new = a - b
    fixed = b - a
    print(f"before {sum(b.values())}  after {sum(a.values())}  new {sum(new.values())}  fixed {sum(fixed.values())}")
    by = Counter()
    for (sev, key, path, msg, line), n in new.items():
        by[(sev, key)] += n
    for k, n in by.most_common(40):
        print(f"  {n:5}  {k[0]:8} {k[1]}")
    if out:
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["severity", "key", "path", "message", "line", "count"])
            for k, n in sorted(new.items()):
                w.writerow(list(k) + [n])


if __name__ == "__main__":
    main(*sys.argv[1:4])
