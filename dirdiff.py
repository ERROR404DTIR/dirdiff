#!/usr/bin/env python3
"""dirdiff - compare two directories by content. One file, zero dependencies."""
import argparse
import fnmatch
import hashlib
import json
import os
import sys

__version__ = "1.0.0"
DEFAULT_IGNORE = [".git", "__pycache__", "node_modules", ".DS_Store"]


def skip(name, patterns):
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def walk(root, patterns):
    found = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not skip(d, patterns))
        for name in files:
            if skip(name, patterns):
                continue
            full = os.path.join(base, name)
            found[os.path.relpath(full, root).replace(os.sep, "/")] = full
    return found


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_same(a, b, quick):
    try:
        if os.path.getsize(a) != os.path.getsize(b):
            return False
        if quick:
            return int(os.path.getmtime(a)) == int(os.path.getmtime(b))
        return sha256(a) == sha256(b)
    except OSError:
        return False


def compare(dir_a, dir_b, patterns, quick=False):
    fa, fb = walk(dir_a, patterns), walk(dir_b, patterns)
    only_a = sorted(set(fa) - set(fb))
    only_b = sorted(set(fb) - set(fa))
    changed, same = [], 0
    for rel in sorted(set(fa) & set(fb)):
        if is_same(fa[rel], fb[rel], quick):
            same += 1
        else:
            changed.append(rel)
    return {"only_a": only_a, "only_b": only_b, "changed": changed, "same": same}


def paint(text, code, on):
    return f"\033[{code}m{text}\033[0m" if on else text


def main(argv=None):
    ap = argparse.ArgumentParser(prog="dirdiff", description="Compare two directories by content.")
    ap.add_argument("a", help="first directory (A)")
    ap.add_argument("b", help="second directory (B)")
    ap.add_argument("-i", "--ignore", action="append", metavar="GLOB",
                    help="glob to ignore, repeatable (added to the defaults)")
    ap.add_argument("--no-default-ignore", action="store_true",
                    help="do not ignore .git, __pycache__, node_modules, .DS_Store")
    ap.add_argument("-q", "--quick", action="store_true",
                    help="compare size + mtime instead of hashing (faster)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args(argv)

    for d in (args.a, args.b):
        if not os.path.isdir(d):
            print(f"dirdiff: not a directory: {d}", file=sys.stderr)
            return 2

    patterns = ([] if args.no_default_ignore else list(DEFAULT_IGNORE)) + (args.ignore or [])
    res = compare(args.a, args.b, patterns, args.quick)
    differs = bool(res["only_a"] or res["only_b"] or res["changed"])

    if args.json:
        print(json.dumps(res, indent=2))
        return 1 if differs else 0

    color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    for rel in res["only_a"]:
        print(paint(f"- {rel}", "31", color))
    for rel in res["only_b"]:
        print(paint(f"+ {rel}", "32", color))
    for rel in res["changed"]:
        print(paint(f"~ {rel}", "33", color))
    print(
        f"\n{len(res['only_a'])} only in A, {len(res['only_b'])} only in B, "
        f"{len(res['changed'])} changed, {res['same']} identical"
    )
    return 1 if differs else 0


if __name__ == "__main__":
    sys.exit(main())
