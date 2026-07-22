# tajik-toolkit

A complete Claude Code skill for Tajik-language (тоҷикӣ) text: editing and proofreading, OCR extraction from images/scans/PDFs, and full book restoration to a formatted DOCX matching the source. Covers mixed Tajik/Russian/English/Arabic/Persian text and Latin-transliterated Pahlavi.

Consolidates three previously separate skills — [`tajik-text`](https://github.com/firdavsi-tech/tajik-text), [`tajik-ocr`](https://github.com/firdavsi-tech/tajik-ocr), and [`tajik-book-restore`](https://github.com/firdavsi-tech/tajik-book-restore) — into one, since in practice the three layers (edit what you have / extract from an image / restore a whole document) are used together, not separately. Those three repos remain available individually if you only need one layer.

## Install

```bash
npx skills add <owner>/tajik-toolkit -g -y
```

Or manually: copy this repo's contents into `~/.claude/skills/tajik-toolkit/`.

## Why this exists

Tajik is a lower-resource language for LLMs and for OCR tooling alike:

- **No OCR engine has a trained Tajik language model** — verified directly against Tesseract's official data repos, and against RapidOCR's actual model config. Classical OCR can only approximate Tajik with a generic Cyrillic/Russian model, which systematically misreads the six Tajik-only Cyrillic letters (Ғ ғ Қ қ Ҳ ҳ Ҷ ҷ Ӣ ӣ Ӯ ӯ). Vision-LLM-based OCR can be told about the alphabet directly in a prompt instead — a real workaround classical OCR can't offer.
- **Register and script judgment calls are genuine, not mechanical** — Soviet-era loanwords vs. native/Persian vocabulary, Arabic vs. Persian quotations that share a script but aren't the same language, Pahlavi transliteration conventions that vary by scholarly source.
- **Restoring a real document needs a strict formatting contract**, not just correct text — real Word Heading styles (so a Table of Contents can be generated), real anchored footnotes, right-to-left Arabic/Persian blocks.

Built and validated against real material, not just synthetic tests: a 49-page 1996 tajwid manual (mixed Tajik Cyrillic + Arabic-script Quranic examples) and a 416-page 11th-century historical chronicle (Gardizi's *Zayn al-Akhbar*) — including catching and fixing a real footnote-misattribution error during restoration by re-checking against the source scan.

## What's inside

| File | Covers |
|---|---|
| `SKILL.md` | Confidence calibration, mode selection (edit / OCR / restore), strict output-delivery rules |
| `orthography.md` | The six Tajik-only letters, izafat, compounding, transliteration |
| `register.md` | Soviet-era loanword vs. native/Persian register judgment calls |
| `glossary.md` | Recurring Arabic honorific formulas in historical/religious texts |
| `mixed-script.md` | Tajik+Russian+English, Tajik+Arabic-script, Arabic-vs-Persian, Pahlavi transliteration |
| `ocr-engines.md` | Vision-LLM vs. classical OCR engine comparison and security notes |
| `ocr-pipeline.md` | Tested pipeline, empirical failure-mode findings, output contract |
| `restoration.md` | Cross-reference-the-source correction method (page-offset calibration, TOC-first heading hierarchy, number/date cross-checks), supported formats (PDF/DJVU — verified via real round-trip test/PNG/TIFF/JPEG, DPI guidance), non-text elements, multi-volume series, author-vs-editor footnotes, large-book batching, formatting contract |
| `formatting.md` | Concrete docx-js implementation (verified against actual type definitions, not assumed), including table formatting and verse/poetry line breaks |
| `delivery.md` | Clean-body-text and real-footnote verification checklist |
| `case-log.md` | Log of real cases found during restorations (register calls, footnote-attribution catches, formatting bugs) — grows over time, not invented |
| `scripts/find_scanned_files.py` | Read-only, cross-drive discovery of scanned-document files |
| `scripts/ocr_batch.py` | Local Tesseract batch OCR with PDF rendering and letter-substitution flagging |
| `scripts/djvu_to_pdf.py` | Converts DJVU to PDF via DjVuLibre's `ddjvu`, tested with a real round-trip |
| `scripts/verify_docx.py` | Automates the delivery/formatting checklist against a generated DOCX, including a check for the literal-`\n`-in-TextRun line-break bug |
| `scripts/check_consistency.py` | Scans a generated DOCX for the same proper name spelled two different ways across the document |
| `scripts/tests/run_tests.py` | Regression suite for the two scripts above, against synthetic fixtures (no Node/docx-js needed) |
| `CHANGELOG.md` | What changed between versions |

## License

MIT
