#!/usr/bin/env python3
"""
Automate the delivery.md / formatting.md verification checklist against a
generated .docx, instead of re-typing the same unzip+grep commands by hand
every time (as was done manually across several real restorations).

Checks:
  1. No forbidden commentary strings in the body text (delivery.md Rule 1)
  2. Real footnotes.xml exists, with content (delivery.md Rule 2)
  3. Palatino Linotype is actually used (formatting.md contract)
  4. At least one real Heading style is present, if headings were expected
  5. If Arabic/Persian RTL content is present, both rightToLeft and
     bidirectional markers exist in the XML (formatting.md RTL section)

This is a checklist automation, not a replacement for actually looking at
the content — a clean report here means the mechanical checks passed, not
that the transcription is accurate. Still cross-reference against the
source per restoration.md's method.
"""
import argparse
import re
import sys
import zipfile

FORBIDDEN_STRINGS = ["файл:", "Саҳифаи", "Эзоҳ:", "Изоҳ:", "<w:t>", "page_", "vision"]


def read_zip_entry(docx_path, entry_name):
    try:
        with zipfile.ZipFile(docx_path) as z:
            return z.read(entry_name).decode("utf-8")
    except KeyError:
        return None


def extract_text_runs(xml_content):
    return re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml_content, re.DOTALL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx_path")
    parser.add_argument("--expect-headings", action="store_true",
                         help="Fail if no real Heading style is found")
    parser.add_argument("--expect-rtl", action="store_true",
                         help="Fail if no rightToLeft/bidirectional markers are found")
    parser.add_argument("--expect-footnotes", action="store_true",
                         help="Fail if footnotes.xml is missing or empty")
    args = parser.parse_args()

    doc_xml = read_zip_entry(args.docx_path, "word/document.xml")
    if doc_xml is None:
        print("FAIL: could not read word/document.xml — is this a valid .docx?", file=sys.stderr)
        sys.exit(1)

    problems = []

    # Rule 1: clean body text
    texts = extract_text_runs(doc_xml)
    full_text = " ".join(texts)
    for forbidden in FORBIDDEN_STRINGS:
        if forbidden in full_text:
            problems.append(f"Body text contains forbidden string: {forbidden!r}")

    # formatting.md: Palatino Linotype actually used
    if "Palatino Linotype" not in doc_xml:
        problems.append("No 'Palatino Linotype' font reference found in document.xml — formatting contract not applied")

    # Headings
    heading_count = len(re.findall(r'w:val="Heading', doc_xml))
    if args.expect_headings and heading_count == 0:
        problems.append("--expect-headings set but no real Heading style found (heading paragraphs must use HeadingLevel.*, not just bold text)")

    # RTL
    has_rtl_run = "w:rtl" in doc_xml or "rightToLeft" in doc_xml
    has_bidi_para = "bidi" in doc_xml.lower()
    if args.expect_rtl:
        if not (has_rtl_run and has_bidi_para):
            problems.append(
                f"--expect-rtl set but RTL markers incomplete (run-level rtl found: {has_rtl_run}, "
                f"paragraph-level bidi found: {has_bidi_para}) — both are required, see formatting.md"
            )

    # Footnotes
    fn_xml = read_zip_entry(args.docx_path, "word/footnotes.xml")
    fn_texts = extract_text_runs(fn_xml) if fn_xml else []
    if args.expect_footnotes and not fn_texts:
        problems.append("--expect-footnotes set but word/footnotes.xml is missing or has no text content")

    print(f"Body text runs: {len(texts)} | Body chars: {len(full_text)}")
    print(f"Footnotes found: {len(fn_texts)}")
    print(f"Heading style references: {heading_count}")
    print(f"RTL markers — run-level: {has_rtl_run}, paragraph-level bidi: {has_bidi_para}")
    print()

    if problems:
        print(f"FAIL: {len(problems)} problem(s) found:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    else:
        print("PASS: all requested checks passed. This confirms the mechanical "
              "contract (no forbidden strings, fonts/styles present) — still "
              "verify content accuracy against the source separately.")


if __name__ == "__main__":
    main()
