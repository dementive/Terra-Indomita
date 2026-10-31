"""Loaders for map data (definition.csv, provinces.png, areas, regions, province loc names)
at any git ref. Heavy results are cached in .cache/ keyed by blob sha."""
import json
import os
import re
import struct
import zlib
from bisect import bisect_right
from itertools import groupby

from gitio import CACHE_DIR, decode, ls_tree, read_blobs, show

PROV_LOC_RE = re.compile(r'^\s*PROV(\d+):\d*\s*"(.*)"', re.M)


def load_definitions(ref):
    """id -> (rgb_int, name)"""
    text, _, _ = decode(show(ref, "map_data/definition.csv"))
    res = {}
    for line in text.split("\n"):
        if not line or line.startswith("#"):
            continue
        parts = line.split(";")
        if len(parts) < 5 or not parts[0].strip().isdigit():
            continue
        pid = int(parts[0])
        if pid == 0:
            continue
        r, g, b = int(parts[1]), int(parts[2]), int(parts[3])
        res[pid] = ((r << 16) | (g << 8) | b, parts[4].strip())
    return res


def _cache_path(name):
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, name)


def iter_png_rows(png):
    """Pure-stdlib PNG decoder (8-bit RGB/RGBA, non-interlaced) yielding raw RGB(A) rows.
    Pillow isn't usable on this machine's Python, and colour-managed decoders could alter
    province colours, so we unfilter by hand."""
    pos, idat, ihdr = 8, [], None
    while pos < len(png):
        ln, = struct.unpack(">I", png[pos:pos + 4])
        typ = png[pos + 4:pos + 8]
        if typ == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", png[pos + 8:pos + 8 + ln])
        elif typ == b"IDAT":
            idat.append(png[pos + 8:pos + 8 + ln])
        pos += 12 + ln
    w, h, depth, ctype, _, _, interlace = ihdr
    assert depth == 8 and ctype in (2, 6) and interlace == 0, ihdr
    bpp = 3 if ctype == 2 else 4
    stride = w * bpp
    raw = zlib.decompress(b"".join(idat))
    prev = bytearray(stride)
    mask7 = int.from_bytes(b"\x7f" * stride, "big")
    mask8 = int.from_bytes(b"\x80" * stride, "big")
    for y in range(h):
        off = y * (stride + 1)
        ft = raw[off]
        line = bytearray(raw[off + 1:off + 1 + stride])
        if ft == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 255
        elif ft == 2:
            a, b = int.from_bytes(line, "big"), int.from_bytes(prev, "big")
            line = bytearray((((a & mask7) + (b & mask7)) ^ ((a ^ b) & mask8)).to_bytes(stride, "big"))
        elif ft == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 255
        elif ft == 4:
            for i in range(stride):
                if i >= bpp:
                    a, c = line[i - bpp], prev[i - bpp]
                else:
                    a = c = 0
                b = prev[i]
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        yield y, w, h, bpp, line
        prev = line


def load_png_runs(ref):
    """Run-length encode provinces.png: returns (width, height, runs) where runs is
    {rgb_int: [(y, x0, x1_exclusive), ...]}. Cached by blob sha."""
    sha = ls_tree(ref, "map_data/provinces.png")["map_data/provinces.png"][2]
    cache = _cache_path(f"runs_{sha}.json")
    if os.path.exists(cache):
        with open(cache) as f:
            d = json.load(f)
        return d["w"], d["h"], {int(k): v for k, v in d["runs"].items()}
    runs = {}
    w = h = 0
    for y, w, h, bpp, line in iter_png_rows(read_blobs([sha])[sha]):
        px = [(line[i] << 16) | (line[i + 1] << 8) | line[i + 2] for i in range(0, len(line), bpp)]
        x = 0
        for color, grp in groupby(px):
            n = sum(1 for _ in grp)
            runs.setdefault(color, []).append((y, x, x + n))
            x += n
    with open(cache, "w") as f:
        json.dump({"w": w, "h": h, "runs": {str(k): v for k, v in runs.items()}}, f)
    return w, h, runs


class RunLookup:
    """Point lookup (x, y) -> rgb over run-length data."""

    def __init__(self, w, h, runs):
        self.w, self.h = w, h
        rows = [[] for _ in range(h)]
        for color, rs in runs.items():
            for y, x0, x1 in rs:
                rows[y].append((x0, color))
        self.starts, self.colors = [], []
        for r in rows:
            r.sort()
            self.starts.append([x for x, _ in r])
            self.colors.append([c for _, c in r])

    def __call__(self, x, y):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return None
        i = bisect_right(self.starts[y], x) - 1
        return self.colors[y][i]


def run_stats(runs):
    """rgb -> (pixel_count, cx, cy, (minx, miny, maxx, maxy))"""
    res = {}
    for color, rs in runs.items():
        n = sx = sy = 0
        minx = miny = 10 ** 9
        maxx = maxy = -1
        for y, x0, x1 in rs:
            k = x1 - x0
            n += k
            sx += (x0 + x1 - 1) * k / 2
            sy += y * k
            minx, maxx = min(minx, x0), max(maxx, x1 - 1)
            miny, maxy = min(miny, y), max(maxy, y)
        res[color] = (n, sx / n, sy / n, (minx, miny, maxx, maxy))
    return res


def load_loc_province_names(ref, lang="english"):
    """id -> name from every PROVnnn key in localization/<lang> (later files override, which
    matches the alphabetical loading order closely enough for matching purposes)."""
    tree = ls_tree(ref, f"localization/{lang}")
    files = sorted(p for p in tree if p.endswith(".yml"))
    blobs = read_blobs([tree[p][2] for p in files])
    names, sources = {}, {}
    for p in files:
        text, _, _ = decode(blobs[tree[p][2]])
        if "PROV" not in text:
            continue
        for m in PROV_LOC_RE.finditer(text):
            pid = int(m.group(1))
            names[pid] = m.group(2)
            sources.setdefault(pid, []).append(p)
    return names, sources


def _named_lists(ref, path, inner):
    import pdx
    text, _, _ = decode(show(ref, path))
    out = {}
    for n in pdx.parse(text).items:
        if n.key and n.is_block:
            lst = n.value.get(inner)
            if lst is not None and lst.is_block:
                out[n.key] = [str(v) for v in lst.value.values()]
    return out


def parse_areas(ref):
    return {k: [int(x) for x in v if x.isdigit()] for k, v in _named_lists(ref, "map_data/areas.txt", "provinces").items()}


def parse_regions(ref):
    return _named_lists(ref, "map_data/regions.txt", "areas")


def parse_default_map(ref):
    """kind -> set(ids) for sea_zones / wasteland / impassable_terrain / lakes / river_provinces"""
    text, _, _ = decode(show(ref, "map_data/default.map"))
    text = re.sub(r"#[^\n]*", "", text)
    res = {}
    for m in re.finditer(r"(\w+)\s*=\s*(LIST|RANGE)\s*\{([^}]*)\}", text):
        kind, typ, body = m.group(1), m.group(2), [int(x) for x in m.group(3).split()]
        s = res.setdefault(kind, set())
        if typ == "LIST":
            s.update(body)
        else:
            s.update(range(body[0], body[1] + 1))
    return res
