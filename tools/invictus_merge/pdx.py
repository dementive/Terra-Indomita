"""Minimal span-preserving parser for Paradox script (Clausewitz) text.

parse(text) -> Block. Every Node records character offsets into the source text, so callers
can splice replacements into the original and leave untouched regions byte-identical."""
import re

TOKEN_RE = re.compile(r'''
    (?P<ws>\s+)
  | (?P<comment>\#[^\n]*)
  | (?P<str>"(?:[^"\\\n]|\\.)*"?)
  | (?P<op><=|>=|!=|\?=|==|=|<|>)
  | (?P<open>\{)
  | (?P<close>\})
  | (?P<word>[^\s{}=<>!?\#"]+|[!?])
''', re.X)


class Node:
    __slots__ = ("key", "op", "value", "start", "end", "key_start", "key_end", "val_start", "val_end")

    def __init__(self, key, op, value, start, end, key_start=None, key_end=None, val_start=None, val_end=None):
        self.key, self.op, self.value = key, op, value
        self.start, self.end = start, end
        self.key_start, self.key_end, self.val_start, self.val_end = key_start, key_end, val_start, val_end

    @property
    def is_block(self):
        return isinstance(self.value, Block)

    def __repr__(self):
        return f"Node({self.key!r} {self.op} {self.value!r})"


class Block:
    __slots__ = ("items", "start", "end")

    def __init__(self, items, start, end):
        self.items, self.start, self.end = items, start, end

    def get(self, key):
        for n in self.items:
            if n.key == key:
                return n
        return None

    def get_all(self, key):
        return [n for n in self.items if n.key == key]

    def keyed(self):
        return [n for n in self.items if n.key is not None]

    def values(self):
        """bare list items (e.g. `{ 1 2 3 }`)"""
        return [n.value for n in self.items if n.key is None and not n.is_block]

    def __repr__(self):
        return f"Block({len(self.items)} items)"


def tokenize(text):
    toks = []
    for m in TOKEN_RE.finditer(text):
        kind = m.lastgroup
        if kind in ("ws", "comment"):
            continue
        toks.append((kind, m.group(), m.start(), m.end()))
    return toks


def unquote(s):
    return s[1:-1] if len(s) >= 2 and s[0] == '"' and s[-1] == '"' else s


def parse(text):
    toks = tokenize(text)
    pos = 0

    def parse_block(start, end_tok_expected):
        nonlocal pos
        items = []
        while pos < len(toks):
            kind, val, s, e = toks[pos]
            if kind == "close":
                if end_tok_expected:
                    pos += 1
                    return Block(items, start, e)
                pos += 1  # stray close brace at root: skip
                continue
            if kind == "open":
                pos += 1
                blk = parse_block(s, True)
                items.append(Node(None, None, blk, s, blk.end, val_start=s, val_end=blk.end))
                continue
            if kind == "op":  # stray operator
                pos += 1
                continue
            # word or string: key = value, or bare value
            if pos + 1 < len(toks) and toks[pos + 1][0] == "op":
                op = toks[pos + 1][1]
                pos += 2
                if pos >= len(toks):
                    items.append(Node(unquote(val), op, "", s, toks[pos - 1][3], s, e))
                    break
                vk, vv, vs, ve = toks[pos]
                if vk == "open":
                    pos += 1
                    blk = parse_block(vs, True)
                    items.append(Node(unquote(val), op, blk, s, blk.end, s, e, vs, blk.end))
                else:
                    pos += 1
                    # `key = rgb { 1 2 3 }` / `hsv { }` style typed values
                    if pos < len(toks) and toks[pos][0] == "open" and vk == "word":
                        open_s = toks[pos][2]
                        pos += 1
                        blk = parse_block(open_s, True)
                        items.append(Node(unquote(val), op, blk, s, blk.end, s, e, vs, blk.end))
                    else:
                        items.append(Node(unquote(val), op, unquote(vv), s, ve, s, e, vs, ve))
            else:
                pos += 1
                items.append(Node(None, None, unquote(val), s, e, val_start=s, val_end=e))
        return Block(items, start, len(text))

    return parse_block(0, False)


def canon(text, node_or_block):
    """Whitespace/comment-insensitive canonical form of a node's source, for equality tests."""
    s, e = node_or_block.start, node_or_block.end
    return " ".join(t[1] for t in tokenize(text[s:e]))


def splice(text, edits):
    """Apply [(start, end, replacement)] edits (non-overlapping) to text."""
    out, last = [], 0
    for s, e, rep in sorted(edits, key=lambda x: x[0]):
        assert s >= last, "overlapping edits"
        out.append(text[last:s])
        out.append(rep)
        last = e
    out.append(text[last:])
    return "".join(out)


def line_start(text, pos):
    return text.rfind("\n", 0, pos) + 1


def node_with_indent(text, node):
    """Span of the node extended to the start of its line (when only whitespace precedes it)
    and through the end of its line, for clean whole-line removal/insertion."""
    ls = line_start(text, node.start)
    s = ls if text[ls:node.start].strip() == "" else node.start
    nl = text.find("\n", node.end)
    rest = text[node.end:nl if nl != -1 else len(text)]
    e = (nl + 1 if nl != -1 else len(text)) if rest.strip() == "" or rest.strip().startswith("#") else node.end
    return s, e
