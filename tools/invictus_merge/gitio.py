"""Thin git plumbing helpers. Everything reads objects straight from the TI repo, so
working-tree state and core.autocrlf never affect what the tools see."""
import os
import subprocess

TI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")


def git(*args, input=None, cwd=TI_ROOT, check=True):
    env = dict(os.environ, MSYS_NO_PATHCONV="1", GIT_TERMINAL_PROMPT="0")
    p = subprocess.run(["git", *args], cwd=cwd, input=input, capture_output=True, env=env)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.decode(errors='replace')}")
    return p.stdout


def rev_parse(ref):
    return git("rev-parse", ref).decode().strip()


def ls_tree(ref, *paths):
    """path -> (mode, type, sha) for every file under ref (recursive)."""
    out = git("ls-tree", "-r", "-z", ref, "--", *paths)
    res = {}
    for entry in out.split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        mode, typ, sha = meta.decode().split()
        res[path.decode("utf-8")] = (mode, typ, sha)
    return res


def read_blobs(shas):
    """sha -> bytes, via a single cat-file --batch process."""
    shas = list(dict.fromkeys(shas))
    if not shas:
        return {}
    data = git("cat-file", "--batch", input=("\n".join(shas) + "\n").encode())
    res, pos = {}, 0
    for sha in shas:
        nl = data.index(b"\n", pos)
        header = data[pos:nl].decode().split()
        size = int(header[2])
        res[sha] = data[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1
    return res


def show(ref, path):
    return git("show", f"{ref}:{path}")


def read_tree_files(ref, predicate=None):
    """path -> bytes for every file under ref matching predicate(path)."""
    tree = ls_tree(ref)
    wanted = {p: v for p, v in tree.items() if v[1] == "blob" and (predicate is None or predicate(p))}
    blobs = read_blobs([v[2] for v in wanted.values()])
    return {p: blobs[v[2]] for p, v in wanted.items()}


BOM = b"\xef\xbb\xbf"


def decode(raw):
    """bytes -> (text with \\n line endings, had_bom, used_crlf)."""
    bom = raw.startswith(BOM)
    if bom:
        raw = raw[3:]
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8", errors="surrogateescape")
    if crlf:
        text = text.replace("\r\n", "\n")
    return text, bom, crlf


def encode(text, bom, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    raw = text.encode("utf-8", errors="surrogateescape")
    return (BOM + raw) if bom else raw


def is_text_path(path):
    return path.lower().endswith((".txt", ".yml", ".csv", ".gui", ".gfx", ".asset", ".map", ".mod", ".shader", ".fxh", ".md", ".json", ".py", ".js", ".settings", ".sfx"))
