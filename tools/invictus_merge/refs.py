"""Finding and rewriting ID references (provinces, characters, tags, areas/regions) in mod text.

Every finder yields (kind, value, start, end) where [start, end) is the span of the value
itself, so rewrites only ever touch the ID and never the surrounding syntax."""
import re

import pdx

PROVINCE_KEYS = ("province_id", "owns", "owns_or_subject_owns", "capital", "set_capital", "set_state_capital",
                 "add_road_towards", "has_road_towards", "location", "province", "goto_location", "birth_province",
                 "PATH_TARGET", "CAPITAL", "NEW_CAPITAL_LOCATION")
SCRIPT_PROV_RES = [
    re.compile(r"(?<![\w.])p:(\d+)\b"),
    re.compile(r"(?<![\w.:$])(?:" + "|".join(PROVINCE_KEYS) + r")\s*(?:=|!=|<=|>=|<|>)\s*\"?(\d+)\b(?![.:])"),
]
PROV_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_])PROV(\d+)(?=[_:$\"\s\]\.'#]|$)")
LOC_GETPROV_RE = re.compile(r"GetProvince\('\(int32\)(\d+)'\)")
PROVINCE_NAMES_KEY_RE = re.compile(r"^(\s*)(\d+)(?=\s*=)", re.M)

CHAR_RES = [
    re.compile(r"(?<![\w.])char:(\d+)\b"),
    re.compile(r"GetCharacter\('\(int32\)(\d+)'\)"),
    re.compile(r"\bdeify_ruler\s*=\s*\"?(\d+)\b"),
]
RULER_TERM_CHAR_RE = re.compile(r"\bcharacter\s*=\s*(\d+)\b")

AREA_RES = [
    (re.compile(r"(?<![\w.])area:(\w+)"), "area"),
    (re.compile(r"(?<![\w.])region:(\w+)"), "region"),
    (re.compile(r"\bis_in_area\s*=\s*(\w+)"), "area"),
    (re.compile(r"\bis_in_region\s*=\s*(\w+)"), "region"),
]


def comment_spans(text):
    """[start, end) spans of # comments outside quoted strings (yml files have none we care about)."""
    spans = []
    for m in pdx.TOKEN_RE.finditer(text):
        if m.lastgroup == "comment":
            spans.append((m.start(), m.end()))
    return spans


def in_spans(pos, spans):
    lo, hi = 0, len(spans)
    while lo < hi:
        mid = (lo + hi) // 2
        if spans[mid][1] <= pos:
            lo = mid + 1
        else:
            hi = mid
    return lo < len(spans) and spans[lo][0] <= pos < spans[lo][1]


def is_loc(path):
    return path.endswith(".yml")


LOC_KEY_PROV_RE = re.compile(r"^\s*PROV(\d+)", re.M)


def province_refs(path, text, include_name_defs=True):
    """-> [(id, start, end)] of province IDs referenced in text. include_name_defs=False skips
    province-name definitions (loc keys `PROVn...:` and common/province_names entries)."""
    out = []
    if is_loc(path):
        key_starts = set() if include_name_defs else {m.start(1) for m in LOC_KEY_PROV_RE.finditer(text)}
        for rx in (LOC_GETPROV_RE, PROV_TOKEN_RE):
            out += [(int(m.group(1)), m.start(1), m.end(1)) for m in rx.finditer(text) if m.start(1) not in key_starts]
        return sorted(out, key=lambda r: r[1])
    if path.startswith("common/province_names/") and not include_name_defs:
        return []
    if path.startswith("setup/characters/"):
        rxs = [SCRIPT_PROV_RES[0]]  # only p:N (governorships); numeric keys there are characters
    else:
        rxs = SCRIPT_PROV_RES
    for rx in rxs:
        out += [(int(m.group(1)), m.start(1), m.end(1)) for m in rx.finditer(text)]
    out += [(int(m.group(1)), m.start(1), m.end(1)) for m in PROV_TOKEN_RE.finditer(text)]
    if path.startswith("common/province_names/"):
        out += [(int(m.group(2)), m.start(2), m.end(2)) for m in PROVINCE_NAMES_KEY_RE.finditer(text)]
    if re.match(r"setup/main/.*great_works.*\.txt$", path):
        root = pdx.parse(text)
        for top in root.items:
            if top.key == "provinces" and top.is_block:
                out += [(int(n.key), n.key_start, n.key_end) for n in top.value.items if n.key and n.key.isdigit()]
    return sorted(set(out), key=lambda r: r[1])


def character_refs(path, text):
    out = []
    for rx in CHAR_RES:
        out += [(int(m.group(1)), m.start(1), m.end(1)) for m in rx.finditer(text)]
    if path.startswith("setup/post_character/"):
        out += [(int(m.group(1)), m.start(1), m.end(1)) for m in RULER_TERM_CHAR_RE.finditer(text)]
    return sorted(set(out), key=lambda r: r[1])


def area_region_refs(text):
    out = []
    for rx, kind in AREA_RES:
        out += [(kind, m.group(1), m.start(1), m.end(1)) for m in rx.finditer(text)]
    return sorted(set(out), key=lambda r: r[2])


def tag_token_res(tags):
    alt = "|".join(sorted(tags, key=len, reverse=True))
    return {
        "script": re.compile(rf"(?:(?<=c:)|(?<![\w.:'\"$\-/]))({alt})(?![\w.'\"$\-/:])|(?<=c:)({alt})(?=\.)"),
        "quoted": re.compile(rf"(?<=\")({alt})(?=\")"),
        "getcountry": re.compile(rf"(?<=GetCountry\(')({alt})(?='\))"),
        "lockey": re.compile(rf"^(\s*)({alt})(?=(?:_ADJ|_DEF)?:)", re.M),
    }


def tag_refs(path, text, rxs):
    out = []
    if is_loc(path):
        out += [(m.group(2), m.start(2), m.end(2)) for m in rxs["lockey"].finditer(text)]
        out += [(m.group(1), m.start(1), m.end(1)) for m in rxs["getcountry"].finditer(text)]
        return out
    for m in rxs["script"].finditer(text):
        g = 1 if m.group(1) else 2
        out.append((m.group(g), m.start(g), m.end(g)))
    if path.startswith("setup/characters/"):
        out += [(m.group(1), m.start(1), m.end(1)) for m in rxs["quoted"].finditer(text)]
    out += [(m.group(1), m.start(1), m.end(1)) for m in rxs["getcountry"].finditer(text)]
    return sorted(set(out), key=lambda r: r[1])


def rewrite(text, refs, fn):
    """refs: [(value, start, end)]; fn(value) -> new value (str) or None to keep.
    Returns (new_text, [(old, new, line_no)])."""
    edits, log = [], []
    for val, s, e in refs:
        new = fn(val)
        if new is not None and str(new) != str(val):
            edits.append((s, e, str(new)))
            log.append((val, new, text.count("\n", 0, s) + 1))
    if not edits:
        return text, log
    # drop overlaps defensively (same span found by two finders)
    edits.sort()
    clean, last = [], -1
    for s, e, r in edits:
        if s >= last:
            clean.append((s, e, r))
            last = e
    return pdx.splice(text, clean), log
