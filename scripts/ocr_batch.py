#!/usr/bin/env python3
"""
Run OCR over a manifest produced by find_scanned_files.py (or a single file/
directory), using the local Tesseract pipeline (image-to-text skill,
`rus` language as the closest available approximation to Tajik — no `tgk`
trained model exists anywhere, verified against Tesseract's official repos).

This is the fully-automatic local path. It does NOT silently "correct" the
six Tajik-only letters (Ғ ғ Қ қ Ҳ ҳ Ҷ ҷ Ӣ ӣ Ӯ ӯ) — it flags words that are
plausible substitution candidates (by character pattern and by low OCR
confidence) for a human or a follow-up model pass to judge, per this skill's
confidence-calibration principle. See ../../tajik-text/orthography.md for
the correction judgment itself.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_TO_TEXT_SH = os.path.join(
    os.path.dirname(os.path.dirname(SCRIPT_DIR)),  # .../skills
    "image-to-text", "scripts", "image-to-text.sh"
)

# Letters that a `rus`-trained model substitutes for four of the six
# Tajik-only letters (Ғ→г, Қ→к, Ҳ→х, Ҷ→ч/ж).
#
# IMPORTANT, found by testing on a real scanned book (not just a synthetic
# one-sentence test): on dense running Tajik text, г/к/х/ч/ж are simply
# common consonants — pattern-matching on them flags roughly 80% of words
# on a real page, which is not a useful "review candidate" signal, it's
# most of the document. This is the same failure the original design made
# with и/у (also excluded, for the same reason) — it just took real text,
# not a short synthetic sentence, to expose that г/к/х/ч/ж have the same
# problem. Kept here for the (rare) short/sparse-text case — titles,
# headers, single lines — where the false-positive rate is manageable; do
# not expect it to be useful triage on a full page of body text. Low
# confidence remains the primary usable signal there, weak as it is.
SUBSTITUTION_CANDIDATE_CHARS = set("гГкКхХчЧжЖ")
LOW_CONFIDENCE_THRESHOLD = 70.0  # empirically, substituted letters sometimes
                                  # (not always — roughly 1 in 4 in testing)
                                  # depress word-confidence; a corroborating
                                  # signal, not a reliable detector on its own
SPARSE_TEXT_WORD_THRESHOLD = 15  # below this word count, pattern-flagging is
                                  # still usably selective; above it, expect
                                  # most flags to be noise (see note above)
GARBAGE_CONFIDENCE_THRESHOLD = 15.0  # very low confidence + short/symbol-
                                       # heavy token is more likely a
                                       # non-Cyrillic region (e.g. Arabic
                                       # script) Tesseract had no chance on
                                       # at all, not a letter substitution


def find_image_to_text_script():
    if os.path.isfile(IMAGE_TO_TEXT_SH):
        return IMAGE_TO_TEXT_SH
    # Fallback: search common install roots
    for base in (os.path.expanduser("~/.agents/skills"), os.path.expanduser("~/.claude/skills")):
        candidate = os.path.join(base, "image-to-text", "scripts", "image-to-text.sh")
        if os.path.isfile(candidate):
            return candidate
    return None


def render_pdf_pages(pdf_path, out_dir, dpi=300):
    """Render each page of a PDF to a PNG using PyMuPDF. Returns list of image paths."""
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    pages = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=matrix)
        out_path = os.path.join(out_dir, f"page_{i+1:04d}.png")
        pix.save(out_path)
        pages.append(out_path)
    doc.close()
    return pages


def find_bash():
    """On Windows, a bare 'bash' can resolve to the WSL launcher stub in
    System32 instead of Git Bash, which fails with no WSL distro installed.
    Prefer a known Git Bash path; fall back to PATH resolution."""
    candidates = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return "bash"


BASH_EXE = find_bash()


def run_ocr_on_image(image_path, lang, image_to_text_sh):
    # Explicit utf-8: on Windows, subprocess text-mode otherwise decodes with
    # the system codepage (e.g. cp1252/cp866), corrupting Cyrillic output.
    result = subprocess.run(
        [BASH_EXE, image_to_text_sh, image_path, lang],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120
    )
    if result.returncode != 0:
        return {"ok": False, "error": result.stderr.strip() or "OCR script failed", "text": ""}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "Could not parse OCR output", "text": "", "raw": result.stdout}
    return {"ok": True, **data}


def is_cyrillic_alpha(text):
    return any("а" <= c.lower() <= "я" or c.lower() in "ёйъь" for c in text)


def flag_words(words):
    """Returns (flagged, likely_non_cyrillic). Pattern-based letter-
    substitution flagging is only applied when the page is sparse (titles,
    headers) — on dense body text it flags most of the page and stops being
    useful (see SUBSTITUTION_CANDIDATE_CHARS comment). Separately, very-low-
    confidence tokens with no recognizable Cyrillic letters are reported as
    "likely_non_cyrillic_script" — this is a different, unfixable-by-this-
    pipeline problem (e.g. Arabic-script Quranic examples in a tajwid text),
    not a letter-substitution candidate, and should not be conflated with one."""
    is_sparse = len(words) <= SPARSE_TEXT_WORD_THRESHOLD
    flagged = []
    likely_non_cyrillic = []

    for w in words:
        text = w.get("text", "")
        conf = w.get("confidence", 100)

        if conf < GARBAGE_CONFIDENCE_THRESHOLD and not is_cyrillic_alpha(text):
            likely_non_cyrillic.append({"text": text, "confidence": conf})
            continue

        has_candidate_char = any(c in SUBSTITUTION_CANDIDATE_CHARS for c in text)
        low_conf = conf < LOW_CONFIDENCE_THRESHOLD
        if (is_sparse and has_candidate_char) or low_conf:
            flagged.append({
                "text": text,
                "confidence": conf,
                "reason": "contains_substitution_candidate_letter" if (is_sparse and has_candidate_char) else "low_confidence",
            })

    return flagged, likely_non_cyrillic


def process_file(file_path, lang, image_to_text_sh, tmp_root):
    ext = os.path.splitext(file_path)[1].lower()
    per_page_results = []

    if ext == ".pdf":
        with tempfile.TemporaryDirectory(dir=tmp_root) as page_dir:
            try:
                pages = render_pdf_pages(file_path, page_dir)
            except Exception as e:
                return {"path": file_path, "ok": False, "error": f"PDF render failed: {e}"}
            for page_path in pages:
                ocr = run_ocr_on_image(page_path, lang, image_to_text_sh)
                per_page_results.append(ocr)
    else:
        ocr = run_ocr_on_image(file_path, lang, image_to_text_sh)
        per_page_results.append(ocr)

    full_text_parts = []
    all_flagged = []
    all_non_cyrillic = []
    page_errors = []
    for i, r in enumerate(per_page_results):
        if not r.get("ok"):
            page_errors.append(f"page {i+1}: {r.get('error', 'unknown error')}")
            continue
        full_text_parts.append(r.get("text", ""))
        flagged, non_cyrillic = flag_words(r.get("words", []))
        for f in flagged:
            f["page"] = i + 1
        for nc in non_cyrillic:
            nc["page"] = i + 1
        all_flagged.extend(flagged)
        all_non_cyrillic.extend(non_cyrillic)

    ok = bool(full_text_parts)  # succeeded if at least one page produced output
    return {
        "path": file_path,
        "ok": ok,
        "error": "; ".join(page_errors) if page_errors and not ok else None,
        "pages": len(per_page_results),
        "text": "\n\n".join(full_text_parts),
        "flagged_words": all_flagged,
        "flagged_count": len(all_flagged),
        "non_cyrillic_regions": all_non_cyrillic,
        "non_cyrillic_count": len(all_non_cyrillic),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", help="Path to a manifest JSON from find_scanned_files.py")
    parser.add_argument("--file", action="append", help="Individual file to process (repeatable)")
    parser.add_argument("--lang", default="rus", help="Tesseract language code (default: rus, closest to Tajik)")
    parser.add_argument("--output-dir", required=True, help="Directory to write per-file .txt and the summary report")
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N files (for a test run)")
    args = parser.parse_args()

    image_to_text_sh = find_image_to_text_script()
    if not image_to_text_sh:
        print("ERROR: could not locate image-to-text.sh. Is the image-to-text skill installed "
              "and has `npm install` been run in its scripts/ directory?", file=sys.stderr)
        sys.exit(1)

    files = []
    if args.manifest:
        with open(args.manifest, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        files = [entry["path"] for entry in manifest["files"]]
    if args.file:
        files.extend(args.file)

    if not files:
        print("ERROR: no input files. Pass --manifest or --file.", file=sys.stderr)
        sys.exit(1)

    if args.limit:
        files = files[:args.limit]

    os.makedirs(args.output_dir, exist_ok=True)
    tmp_root = os.path.join(args.output_dir, "_tmp_pdf_pages")
    os.makedirs(tmp_root, exist_ok=True)

    summary = {"processed": 0, "failed": 0, "total_flagged_words": 0, "results": []}

    for i, file_path in enumerate(files):
        print(f"[{i+1}/{len(files)}] {file_path}", file=sys.stderr)
        if not os.path.isfile(file_path):
            print(f"  skip: not found", file=sys.stderr)
            continue
        result = process_file(file_path, args.lang, image_to_text_sh, tmp_root)
        summary["results"].append({
            "path": result["path"], "ok": result["ok"],
            "pages": result.get("pages", 0), "flagged_count": result.get("flagged_count", 0),
        })
        if result["ok"]:
            summary["processed"] += 1
            summary["total_flagged_words"] += result.get("flagged_count", 0)
            summary["total_non_cyrillic_regions"] = summary.get("total_non_cyrillic_regions", 0) + result.get("non_cyrillic_count", 0)
            out_name = os.path.splitext(os.path.basename(file_path))[0] + ".txt"
            out_path = os.path.join(args.output_dir, out_name)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(result["text"])
                if result["flagged_words"]:
                    f.write("\n\n--- FLAGGED FOR REVIEW (possible Ғ/Қ/Ҳ/Ҷ substitution or low confidence) ---\n")
                    for fw in result["flagged_words"]:
                        f.write(f"page {fw['page']}: \"{fw['text']}\" (confidence {fw['confidence']}, {fw['reason']})\n")
                if result["non_cyrillic_regions"]:
                    f.write("\n\n--- LIKELY NON-CYRILLIC CONTENT (e.g. Arabic script) — NOT recognized, needs vision-based reading ---\n")
                    for nc in result["non_cyrillic_regions"]:
                        f.write(f"page {nc['page']}: garbage token \"{nc['text']}\" (confidence {nc['confidence']}) — Tesseract likely saw non-Cyrillic script here\n")
        else:
            summary["failed"] += 1
            print(f"  FAILED: {result.get('error', 'unknown error (no pages produced output)')}", file=sys.stderr)

    try:
        os.rmdir(tmp_root)
    except OSError:
        pass  # not empty or already cleaned by TemporaryDirectory context managers

    summary_path = os.path.join(args.output_dir, "_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Processed {summary['processed']}, failed {summary['failed']}, "
          f"{summary['total_flagged_words']} words flagged for review across all files.", file=sys.stderr)
    print(f"Per-file text saved to: {args.output_dir}", file=sys.stderr)
    print(f"Summary: {summary_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
