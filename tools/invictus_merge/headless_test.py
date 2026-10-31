"""Let the AI play a mod headless for a few game years and collect the logs.

`imperator.exe -nographics -handsoff` starts the 450 AUC campaign with no window and lets the AI
play every country (found by the IRSE project, C:\\Users\\dm\\dev\\irse\\docs\\re\\cli-automation.md).
The game never quits on its own, so a probe mod adds scripted tests that log
`OK - <name> ( <date> )` to logs/scripted_tests.log: one marker per game year, to see how far the
game got, plus the checks in headless/ti_checks.txt. The game is killed once the target year's
marker appears or the timeout passes. dlc_load.json is restored afterwards.

Usage: python headless_test.py [--years 10] [--timeout 1200] [--mod-path DIR] [--label NAME]
                               [--compare OTHER_ERROR_LOG]

--mod-path defaults to this checkout; point it at the Invictus checkout to get a baseline of
Invictus's own runtime errors, then pass that run's error.log as --compare.
"""
import argparse
import collections
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

GAME_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\ImperatorRome"
EXE = os.path.join(GAME_DIR, "binaries", "imperator.exe")
DOCS = r"C:\Users\dm\Documents\Paradox Interactive\Imperator"
LOGS = os.path.join(DOCS, "logs")
DLC_LOAD = os.path.join(DOCS, "dlc_load.json")
HERE = os.path.dirname(os.path.abspath(__file__))
TI_ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
START_YEAR = 450
PROBE = "zz_ti_headless_probe"
TARGET = "zz_ti_headless_target"
TEST_RE = re.compile(r"^(OK|FAILED|SKIPPED)\s*-\s*(.+?)\s*\(\s*([^)]+?)\s*\)\s*$")


def game_running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq imperator.exe", "/NH"], capture_output=True, text=True).stdout
    return "imperator.exe" in out.lower()


def write(path, text, bom=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8-sig" if bom else "ascii", newline="\r\n") as f:
        f.write(text)


def deploy(mod_path, years):
    """Write the target and probe descriptors and the probe mod into Documents/mod."""
    mod_dir = os.path.join(DOCS, "mod")
    probe_dir = os.path.join(mod_dir, PROBE)
    fwd = lambda p: p.replace("\\", "/")
    write(os.path.join(mod_dir, TARGET + ".mod"), f'name="headless test target"\nsupported_version="2.*"\npath="{fwd(mod_path)}"\n')
    write(os.path.join(mod_dir, PROBE + ".mod"), f'name="headless test probe"\nsupported_version="2.*"\npath="{fwd(probe_dir)}"\n')
    write(os.path.join(probe_dir, "descriptor.mod"), 'name="headless test probe"\nsupported_version="2.*"\n')
    markers = "".join(
        f"ti_probe_year_{y} = {{\n\tsuite = \"ti_probe\"\n\tinterval = monthly\n\tsuccess = {{ current_date >= {y}.1.1 }}\n\tfailure = {{ always = no }}\n}}\n\n"
        for y in range(START_YEAR + 1, START_YEAR + years + 1))
    checks = open(os.path.join(HERE, "headless", "ti_checks.txt"), encoding="utf-8").read()
    write(os.path.join(probe_dir, "common", "scripted_tests", "ti_probe.txt"), markers + checks, bom=True)


def undeploy():
    mod_dir = os.path.join(DOCS, "mod")
    for name in (TARGET + ".mod", PROBE + ".mod"):
        p = os.path.join(mod_dir, name)
        if os.path.exists(p):
            os.remove(p)
    shutil.rmtree(os.path.join(mod_dir, PROBE), ignore_errors=True)


def test_results():
    path = os.path.join(LOGS, "scripted_tests.log")
    res = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8", errors="replace"):
            m = TEST_RE.match(line.strip())
            if m:
                res[m.group(2)] = (m.group(1), m.group(3))
    return res


def entries(path):
    """error.log entries (a timestamped line plus its indented continuation lines), timestamps removed."""
    out, cur = [], None
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        m = re.match(r"^\[[0-9:]+\]\[([^\]]+)\]: (.*)", line)
        if m:
            cur = [m.group(1).split(":")[0] + ": " + m.group(2)]
            out.append(cur)
        elif cur is not None and line.strip():
            cur.append(line.strip())
    return [" || ".join(e) for e in out]


def normalize(entry):
    """Drop line numbers and object ids, so the same error in a file both mods share still matches."""
    return re.sub(r"line: \d+", "line: N", re.sub(r"\(\s*\d+\s*\)|\[\d{3,}\]|\b\d{4,}\b", "#", entry))


def summarize(log, compare=None, top=60):
    counts = collections.Counter(normalize(e) for e in entries(log))
    print(f"\nerror.log: {sum(counts.values())} entries, {len(counts)} distinct")
    if compare:
        known = {normalize(e) for e in entries(compare)}
        counts = collections.Counter({e: n for e, n in counts.items() if e not in known})
        print(f"not in {compare}: {sum(counts.values())} entries, {len(counts)} distinct")
    for e, n in counts.most_common(top):
        print(f"{n:5} {e[:300]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=int, default=10)
    ap.add_argument("--timeout", type=int, default=1200, help="seconds")
    ap.add_argument("--mod-path", default=TI_ROOT)
    ap.add_argument("--label", default="ti")
    ap.add_argument("--out", default=os.path.join(tempfile.gettempdir(), "ti_headless"))
    ap.add_argument("--compare")
    a = ap.parse_args()
    if game_running():
        sys.exit("imperator.exe is already running; close it first")
    backup = open(DLC_LOAD, "rb").read() if os.path.exists(DLC_LOAD) else None
    target = START_YEAR + a.years
    results, t0 = {}, time.time()
    try:
        deploy(a.mod_path, a.years)
        with open(DLC_LOAD, "w", encoding="ascii") as f:
            json.dump({"enabled_mods": [f"mod/{TARGET}.mod", f"mod/{PROBE}.mod"], "disabled_dlcs": []}, f)
        tests_log = os.path.join(LOGS, "scripted_tests.log")
        if os.path.exists(tests_log):
            os.remove(tests_log)
        proc = subprocess.Popen([EXE, "-nographics", "-handsoff"], cwd=os.path.dirname(EXE),
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"launched {os.path.basename(a.mod_path)} headless; waiting for {target}.1.1 (timeout {a.timeout}s)", flush=True)
        reached = None
        try:
            while time.time() - t0 < a.timeout:
                if proc.poll() is not None:
                    print(f"game exited on its own (code {proc.returncode})")
                    break
                results = test_results()
                years = [int(n.rsplit("_", 1)[1]) for n in results if n.startswith("ti_probe_year_")]
                if years and max(years) != reached:
                    reached = max(years)
                    print(f"  reached {reached} after {time.time() - t0:.0f}s", flush=True)
                if reached == target:
                    break
                time.sleep(2)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
    finally:
        if backup is not None:
            open(DLC_LOAD, "wb").write(backup)
        undeploy()
    results = test_results()
    out = os.path.join(a.out, a.label)
    os.makedirs(out, exist_ok=True)
    for name in ("error.log", "game.log", "debug.log", "scripted_tests.log"):
        src = os.path.join(LOGS, name)
        if os.path.exists(src):
            shutil.copy2(src, out)
    print(f"\nwall time {time.time() - t0:.0f}s; logs copied to {out}")
    for name, (status, date) in sorted(results.items()):
        if not name.startswith("ti_probe_year_"):
            print(f"{status:7} {name} ({date})")
    summarize(os.path.join(out, "error.log"), a.compare)


if __name__ == "__main__":
    main()
