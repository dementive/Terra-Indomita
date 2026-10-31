"""Build maps/provinces.csv: every Invictus province ID -> the Terra-Indomita province ID that
covers the same land.

Method, in priority order:
  identity    same ID and same RGB in both definition.csv files
  color       the INV colour exists in TI under a different ID (TI renumbered it)
  overlap     project the INV province's pixels onto TI's provinces.png through a local affine
              transform fitted on identity provinces (TI's map is INV rescaled ~0.52x and
              shifted), then take the TI province that receives the most pixels; the name and
              terrain type of the winner are cross-checked to set the confidence.

Usage: python build_province_map.py <inv_ref> <ti_ref>
"""
import csv
import math
import os
import sys
import unicodedata

from mapdata import (RunLookup, load_definitions, load_loc_province_names, load_png_runs,
                     parse_default_map, run_stats)

HERE = os.path.dirname(__file__)
K_ANCHORS = 40
NAME_RADIUS = 220  # px in TI space between projected centroid and a same-name TI province
MAX_ANCHOR_RESIDUAL = 200  # px; same-ID provinces further than this from the fit were moved by TI


def norm(name):
    name = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower()
    return "".join(ch for ch in name if ch.isalnum())


def kind_of(pid, dm):
    for k in ("sea_zones", "river_provinces", "lakes", "wasteland", "impassable_terrain", "uninhabitable"):
        if pid in dm.get(k, ()):
            return {"sea_zones": "sea", "river_provinces": "river", "lakes": "lake"}.get(k, "waste")
    return "land"


def fit_axis(pairs, weights):
    sw = sum(weights)
    mx = sum(w * a for (a, _), w in zip(pairs, weights)) / sw
    my = sum(w * b for (_, b), w in zip(pairs, weights)) / sw
    sxx = sum(w * (a - mx) ** 2 for (a, _), w in zip(pairs, weights))
    sxy = sum(w * (a - mx) * (b - my) for (a, b), w in zip(pairs, weights))
    slope = sxy / sxx if sxx > 1e-9 else 0.52
    return slope, my - slope * mx


def main(inv_ref, ti_ref, out_name="provinces.csv"):
    defs_inv, defs_ti = load_definitions(inv_ref), load_definitions(ti_ref)
    rgb_to_ti = {}
    for pid, (rgb, _) in defs_ti.items():
        rgb_to_ti.setdefault(rgb, pid)
    loc_inv, _ = load_loc_province_names(inv_ref)
    loc_ti, src_ti = load_loc_province_names(ti_ref)
    dm_inv, dm_ti = parse_default_map(inv_ref), parse_default_map(ti_ref)

    def inv_name(pid):
        return loc_inv.get(pid) or defs_inv[pid][1]

    def ti_name_set(pid):
        # definition.csv is authoritative for TI; generic provincenames_l_english still carries
        # stale INV names for 8063-8113, so loc only counts below 8063 or from ti_/acb_ files
        names = {norm(defs_ti.get(pid, (0, ""))[1])}
        if pid < 8063 or any("/ti_" in f or "/acb_" in f for f in src_ti.get(pid, ())):
            names.add(norm(loc_ti.get(pid, "")))
        return names - {""}

    def ti_display(pid):
        return defs_ti[pid][1] if pid >= 8063 else (loc_ti.get(pid) or defs_ti[pid][1])

    name_index = {}
    for pid in defs_ti:
        for n in ti_name_set(pid):
            name_index.setdefault(n, set()).add(pid)
    generic = {n for n, ids in name_index.items() if len(ids) > 3}

    print("run-length encoding provinces.png (cached after first run)...", flush=True)
    _, _, runs_inv = load_png_runs(inv_ref)
    W, H, runs_ti = load_png_runs(ti_ref)
    ti_at = RunLookup(W, H, runs_ti)
    st_inv, st_ti = run_stats(runs_inv), run_stats(runs_ti)

    # anchors: identity provinces present in both images
    anchors = []
    for pid, (rgb, _) in defs_inv.items():
        if pid in defs_ti and defs_ti[pid][0] == rgb and rgb in st_inv and rgb in st_ti:
            a, b = st_inv[rgb], st_ti[rgb]
            if a[0] >= 30 and b[0] >= 8:
                anchors.append((a[1], a[2], b[1], b[2], a[0], pid))
    # TI moved a few same-ID-same-colour provinces elsewhere (e.g. 5961 became a Tibetan
    # impassable); drop anchors far off the global fit so they can't skew local fits
    for _ in range(3):
        gx = fit_axis([(a[0], a[2]) for a in anchors], [1] * len(anchors))
        gy = fit_axis([(a[1], a[3]) for a in anchors], [1] * len(anchors))
        res = [math.hypot(gx[0] * a[0] + gx[1] - a[2], gy[0] * a[1] + gy[1] - a[3]) for a in anchors]
        anchors = [a for a, r in zip(anchors, res) if r <= MAX_ANCHOR_RESIDUAL]
    res = sorted(res)
    print(f"global fit x'={gx[0]:.4f}x+{gx[1]:.1f}  y'={gy[0]:.4f}y+{gy[1]:.1f}  anchors={len(anchors)} "
          f"residual median={res[len(res)//2]:.1f}px p95={res[int(len(res)*.95)]:.1f}px max={res[-1]:.1f}px")
    anchor_ids = {a[5] for a in anchors}

    # bucket anchors for nearest-neighbour lookup
    cell = 128
    grid = {}
    for a in anchors:
        grid.setdefault((int(a[0]) // cell, int(a[1]) // cell), []).append(a)

    def local_fit(cx, cy):
        r = 1
        found = []
        while len(found) < K_ANCHORS and r < 70:
            found = [a for gxi in range(int(cx) // cell - r, int(cx) // cell + r + 1)
                     for gyi in range(int(cy) // cell - r, int(cy) // cell + r + 1)
                     for a in grid.get((gxi, gyi), ())]
            r += 1
        found.sort(key=lambda a: (a[0] - cx) ** 2 + (a[1] - cy) ** 2)
        near = found[:K_ANCHORS]
        if len(near) < 6:
            return gx, gy
        w = [1 / (1 + math.hypot(a[0] - cx, a[1] - cy)) for a in near]
        return fit_axis([(a[0], a[2]) for a in near], w), fit_axis([(a[1], a[3]) for a in near], w)

    rows = []
    for pid in sorted(defs_inv):
        rgb, dname = defs_inv[pid]
        name = inv_name(pid)
        ikind = kind_of(pid, dm_inv)
        if pid in defs_ti and defs_ti[pid][0] == rgb:
            relocated = False
            if pid not in anchor_ids and rgb in st_inv and rgb in st_ti:
                (ax, bx), (ay, by) = local_fit(st_inv[rgb][1], st_inv[rgb][2])
                d = math.hypot(ax * st_inv[rgb][1] + bx - st_ti[rgb][1], ay * st_inv[rgb][2] + by - st_ti[rgb][2])
                relocated = d > MAX_ANCHOR_RESIDUAL
            if not relocated:
                rows.append((pid, name, pid, ti_display(pid), "identity", "high", 1.0, ""))
                continue
        elif rgb in rgb_to_ti:
            tid = rgb_to_ti[rgb]
            rows.append((pid, name, tid, ti_display(tid), "color", "high", 1.0, "same colour, renumbered by TI"))
            continue
        if rgb not in st_inv:
            rows.append((pid, name, "", "", "unused", "none", 0, "not painted on INV provinces.png"))
            continue
        n, cx, cy, _ = st_inv[rgb]
        (ax, bx), (ay, by) = local_fit(cx, cy)
        votes = {}
        total = 0
        step = 1 if n < 400 else 2
        for y, x0, x1 in runs_inv[rgb]:
            if step == 2 and y % 2:
                continue
            ty = int(round(ay * y + by))
            if not 0 <= ty < H:
                continue
            for x in range(x0, x1, step):
                tx = int(round(ax * x + bx))
                if not 0 <= tx < W:
                    continue
                tid = rgb_to_ti.get(ti_at(tx, ty))
                if tid is not None:
                    votes[tid] = votes.get(tid, 0) + 1
                total += 1
        px, py = ax * cx + bx, ay * cy + by
        cands = set()
        for nm in {norm(name), norm(dname)} - {""} - generic:
            cands |= name_index.get(nm, set())
        near = sorted((math.hypot(st_ti[defs_ti[t][0]][1] - px, st_ti[defs_ti[t][0]][2] - py), t)
                      for t in cands if defs_ti[t][0] in st_ti)
        near = [(d, t) for d, t in near if d <= NAME_RADIUS]
        ranked = sorted(votes.items(), key=lambda kv: -kv[1])
        note = "; ".join(f"{t}:{v * 100 // max(total, 1)}%" for t, v in ranked[:4])
        if near:
            best = near[0][1]
            share = votes.get(best, 0) / max(total, 1)
            ambiguous = len(near) > 1 and near[1][0] < 2 * near[0][0] + 20
            method = "name+position"
            conf = "medium" if ambiguous else "high"
            note = f"name match {near[0][0]:.0f}px from projection" + (f"; other same-name {[t for _, t in near[1:]]}" if ambiguous else "") + "; " + note
        elif votes:
            ikind_land = ikind == "land"
            best, bv = ranked[0]
            share = bv / total
            method = "overlap"
            if ikind_land and kind_of(best, dm_ti) != "land":
                land = [(t, v) for t, v in ranked if kind_of(t, dm_ti) == "land" and v / total >= 0.15]
                if land:
                    best, share = land[0][0], land[0][1] / total
                    method = "overlap(land)"
            conf = "high" if share >= 0.85 else "medium" if share >= 0.6 else "low"
        else:
            rows.append((pid, name, "", "", "overlap", "none", 0, "projected outside TI map"))
            continue
        tkind = kind_of(best, dm_ti)
        if tkind != ikind:
            note += f"; kind {ikind}->{tkind}"
            if conf == "high" and method.startswith("overlap"):
                conf = "medium"
        rows.append((pid, name, best, ti_display(best), method, conf, round(share, 3), note))

    out = os.path.join(HERE, "maps", out_name)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # keep manual overrides from an existing file
    overrides = {}
    if os.path.exists(out):
        with open(out, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["method"] == "manual":
                    overrides[int(r["inv_id"])] = r
    with open(out, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["inv_id", "inv_name", "ti_id", "ti_name", "method", "confidence", "share", "note"])
        for r in rows:
            if r[0] in overrides:
                o = overrides[r[0]]
                wr.writerow([o[k] for k in ("inv_id", "inv_name", "ti_id", "ti_name", "method", "confidence", "share", "note")])
            else:
                wr.writerow(r)
    from collections import Counter
    print(Counter((r[4], r[5]) for r in rows).most_common())
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:4])
