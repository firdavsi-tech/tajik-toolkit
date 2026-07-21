#!/usr/bin/env python3
"""
Discover candidate scanned-document files across all drives.

Read-only: lists matching files, does not open/OCR/modify anything.
Run ocr_batch.py separately against the resulting manifest to actually
extract text.
"""
import argparse
import json
import os
import string
import sys
import time

DEFAULT_EXTENSIONS = {
    ".pdf", ".png", ".tiff", ".tif", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"
}

# Directories that are never scanned-document sources and are slow/noisy/
# permission-heavy to walk. Skipped by default; override with --no-exclude
# or --include-dir to widen scope deliberately.
DEFAULT_EXCLUDE_DIR_NAMES = {
    "windows", "program files", "program files (x86)", "programdata",
    "$recycle.bin", "system volume information", "node_modules",
    ".git", ".svn", "venv", ".venv", "__pycache__",
    "appdata",  # covers Local/Roaming/LocalLow app caches & temp under user profiles
}


def iter_drives():
    if os.name != "nt":
        yield "/"
        return
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            yield drive


def is_excluded(dirname: str, exclude_names: set) -> bool:
    return dirname.lower() in exclude_names


def find_files(roots, extensions, exclude_names, max_files=None, quiet=False):
    results = []
    scanned_dirs = 0
    start = time.time()

    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root, topdown=True, onerror=lambda e: None):
            # Prune excluded directories in-place so os.walk doesn't descend into them.
            dirnames[:] = [d for d in dirnames if not is_excluded(d, exclude_names)]
            scanned_dirs += 1

            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in extensions:
                    fpath = os.path.join(dirpath, fname)
                    try:
                        stat = os.stat(fpath)
                        size = stat.st_size
                        mtime = stat.st_mtime
                    except OSError:
                        continue
                    results.append({
                        "path": fpath,
                        "ext": ext,
                        "size_bytes": size,
                        "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)),
                    })
                    if max_files and len(results) >= max_files:
                        return results, scanned_dirs, time.time() - start

            if not quiet and scanned_dirs % 500 == 0:
                print(f"  ...scanned {scanned_dirs} directories, {len(results)} candidates so far", file=sys.stderr)

    return results, scanned_dirs, time.time() - start


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", default=None,
                         help="Specific root path to scan (repeatable). Default: all drives.")
    parser.add_argument("--ext", action="append", default=None,
                         help="Additional file extension to include, e.g. --ext .heic")
    parser.add_argument("--no-exclude", action="store_true",
                         help="Do not skip the default system/noise directories (slow, not recommended)")
    parser.add_argument("--max-files", type=int, default=None,
                         help="Stop after finding this many files (for a quick sample)")
    parser.add_argument("--output", default=None,
                         help="Write the manifest JSON here (default: print to stdout)")
    args = parser.parse_args()

    extensions = set(DEFAULT_EXTENSIONS)
    if args.ext:
        extensions.update(e if e.startswith(".") else f".{e}" for e in args.ext)

    exclude_names = set() if args.no_exclude else DEFAULT_EXCLUDE_DIR_NAMES
    roots = args.root if args.root else list(iter_drives())

    print(f"Scanning roots: {roots}", file=sys.stderr)
    print(f"Extensions: {sorted(extensions)}", file=sys.stderr)
    print(f"Excluding directory names: {sorted(exclude_names) if exclude_names else '(none)'}", file=sys.stderr)

    results, scanned_dirs, elapsed = find_files(roots, extensions, exclude_names, args.max_files)

    manifest = {
        "roots": roots,
        "extensions": sorted(extensions),
        "directories_scanned": scanned_dirs,
        "elapsed_seconds": round(elapsed, 1),
        "file_count": len(results),
        "files": results,
    }

    output_json = json.dumps(manifest, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"Found {len(results)} candidate files in {scanned_dirs} directories ({elapsed:.1f}s).", file=sys.stderr)
        print(f"Manifest written to: {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
