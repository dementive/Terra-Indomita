"""Diff two Imperator error.log files from boots of different mod versions. Timestamps, file line
numbers and the mod's root path are normalised away, so only genuinely new messages show.

Usage: python errorlog_diff.py <before.log> <after.log> [out.txt]
"""
import re
import sys
from collections import Counter

NORM = [
    (re.compile(r"^\[\d\d:\d\d:\d\d\]"), ""),
    (re.compile(r"(?i)c:[\\/].*?[\\/]mod[\\/][^\\/]+[\\/]"), "<MOD>/"),
    (re.compile(r"\b(line|Line|row)[:= ]+\d+"), r"\1 N"),
    (re.compile(r"\(\d+, \d+\)"), "(N, N)"),
]


def load(path):
    out = Counter()
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        for rx, rep in NORM:
            line = rx.sub(rep, line)
        out[line] += 1
    return out


def main(before, after, out=None):
    b, a = load(before), load(after)
    new, fixed = a - b, b - a
    print(f"before {sum(b.values())} lines, after {sum(a.values())} | new {sum(new.values())} | gone {sum(fixed.values())}")
    src = Counter(re.match(r"\[([^\]:]+)", k).group(1) if k.startswith("[") else "?" for k in new.elements())
    print("new by source:", src.most_common(12))
    if out:
        with open(out, "w", encoding="utf-8") as f:
            for k, n in sorted(new.items()):
                f.write(f"{n}\t{k}\n")


if __name__ == "__main__":
    main(*sys.argv[1:4])
