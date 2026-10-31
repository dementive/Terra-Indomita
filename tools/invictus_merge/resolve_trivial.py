"""Resolve zdiff3 conflict hunks that need no judgement, in place:
  - one side's change is whitespace-only relative to base -> take the other side
  - both sides are the same ignoring whitespace           -> take ours (TI)
Remaining hunks are left untouched. Line endings and BOMs are preserved.

Usage: python resolve_trivial.py <file>...   (prints remaining hunk counts)
"""
import re
import sys

HUNK_RE = re.compile(
    r"^<<<<<<< [^\n]*\n(?P<ours>.*?)^\|\|\|\|\|\|\| [^\n]*\n(?P<base>.*?)^=======\n(?P<theirs>.*?)^>>>>>>> [^\n]*\n",
    re.S | re.M)


def norm(s):
    return " ".join(s.split())


def resolve(text):
    remaining = 0

    def sub(m):
        nonlocal remaining
        o, b, t = m.group("ours"), m.group("base"), m.group("theirs")
        if norm(o) == norm(t) or norm(b) == norm(t):
            return o
        if norm(b) == norm(o):
            return t
        remaining += 1
        return m.group(0)
    return HUNK_RE.sub(sub, text), remaining


def main(paths):
    total = 0
    for p in paths:
        raw = open(p, "rb").read()
        crlf = b"\r\n" in raw
        text = raw.decode("utf-8", errors="surrogateescape").replace("\r\n", "\n")
        new, n = resolve(text)
        if new != text:
            out = new.replace("\n", "\r\n") if crlf else new
            open(p, "wb").write(out.encode("utf-8", errors="surrogateescape"))
        print(f"{n}\t{p}")
        total += n
    print("remaining hunks:", total, file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
