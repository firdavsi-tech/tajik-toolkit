#!/usr/bin/env python3
"""
Convert a DJVU file to PDF using DjVuLibre's ddjvu, so it can enter the same
PyMuPDF-based page-rendering pipeline already used for PDF sources.

Verified working (2026-07-22): a real Tajik book page was rendered to an
image, converted to .djvu with c44, converted back to .pdf with this script's
method, and opened successfully with PyMuPDF — full round trip, not just a
theoretical claim. Requires DjVuLibre installed (`winget install
DjVuLibre.DjView` on Windows, provides ddjvu.exe alongside the viewer).
"""
import argparse
import os
import subprocess
import sys


def find_ddjvu():
    """ddjvu may not be on PATH even after install (confirmed on Windows —
    DjVuLibre's winget package doesn't add itself to PATH). Check common
    install locations before falling back to PATH resolution."""
    candidates = [
        r"C:\Program Files (x86)\DjVuLibre\ddjvu.exe",
        r"C:\Program Files\DjVuLibre\ddjvu.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return "ddjvu"  # rely on PATH if not found above


def convert(djvu_path, pdf_path):
    ddjvu = find_ddjvu()
    result = subprocess.run(
        [ddjvu, "-format=pdf", djvu_path, pdf_path],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        print(f"ERROR: ddjvu failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(pdf_path):
        print("ERROR: ddjvu reported success but no output file was created", file=sys.stderr)
        sys.exit(1)
    print(f"Converted: {djvu_path} -> {pdf_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("djvu_file", help="Path to the source .djvu file")
    parser.add_argument("pdf_file", help="Path to write the converted .pdf file")
    args = parser.parse_args()
    convert(args.djvu_file, args.pdf_file)
    print("Now use the same PDF pipeline as any other PDF source "
          "(render pages via PyMuPDF, per ocr-pipeline.md / restoration.md).", file=sys.stderr)


if __name__ == "__main__":
    main()
