# Changelog

## v1.2.0 — 2026-07-22

**Fixed a real bug:** a literal `\n` inside a docx-js `TextRun`'s `text` does not render as a line break in Word (no `<w:br/>` is produced) — this had silently broken poetry-couplet formatting in a real delivered restoration. Documented the correct `break: 1` pattern in `formatting.md`, added a check for it to `verify_docx.py`, and fixed the affected build script and delivered document.

Added, from a review of prior restoration work:
- Non-text source elements (stamps, ornamental borders) — default handling in `restoration.md`
- TOC-first heading hierarchy — read the source's table of contents before assigning heading levels, instead of per-page guessing
- `case-log.md` — a place to log real cases found during restorations, since register.md/glossary.md's own "grow from real cases" principle had no file to grow into
- Multi-volume/series consistency guidance
- Page-number offset calibration as a mandatory documented first step
- Spelled-out vs. numeral date/number cross-verification (Hijri dates given both ways)
- `scripts/check_consistency.py` — scans a generated DOCX for the same proper name spelled two different ways
- Author's footnotes vs. later editor's/translator's footnotes distinction
- DPI rendering guidance (150 default, 200+ for small print/dense tables)
- Batching/checkpoint plan for 400+ page books

## v1.1.0 — 2026-07-21/22

- DJVU source support, verified with a real round-trip test (`scripts/djvu_to_pdf.py`, DjVuLibre's `ddjvu`)
- `scripts/verify_docx.py` — automates the delivery/formatting checklist against a generated DOCX
- Table formatting pattern added to `formatting.md` (flagged as a genuine gap in the original 8-point contract, not a silent default)
- `glossary.md` — recurring Arabic honorific formulas in historical/religious texts
- RapidOCR's actual model config verified directly (no Tajik model, same gap as Tesseract)

## v1.0.0 — 2026-07-21

Initial release: consolidates three previously separate skills (`tajik-text`, `tajik-ocr`, `tajik-book-restore`) into one, since in practice editing/OCR/restoration are used together on the same task, not separately.
