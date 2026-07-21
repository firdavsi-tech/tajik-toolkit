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

- **No OCR engine has a trained Tajik language model** — verified directly against Tesseract's official data repos. Classical OCR (Tesseract, PaddleOCR-classic) can only approximate Tajik with Russian, which systematically misreads the six Tajik-only Cyrillic letters (Ғ ғ Қ қ Ҳ ҳ Ҷ ҷ Ӣ ӣ Ӯ ӯ). Vision-LLM-based OCR can be told about the alphabet directly in a prompt instead — a real workaround classical OCR can't offer.
- **Register and script judgment calls are genuine, not mechanical** — Soviet-era loanwords vs. native/Persian vocabulary, Arabic vs. Persian quotations that share a script but aren't the same language, Pahlavi transliteration conventions that vary by scholarly source.
- **Restoring a real document needs a strict formatting contract**, not just correct text — real Word Heading styles (so a Table of Contents can be generated), real anchored footnotes, right-to-left Arabic/Persian blocks.

Built and validated against real material, not just synthetic tests: a 49-page 1996 tajwid manual (mixed Tajik Cyrillic + Arabic-script Quranic examples) and a 416-page 11th-century historical chronicle (Gardizi's *Zayn al-Akhbar*) — including catching and fixing a real footnote-misattribution error during restoration by re-checking against the source scan.

## What's inside

| File | Covers |
|---|---|
| `SKILL.md` | Confidence calibration, mode selection (edit / OCR / restore), strict output-delivery rules |
| `orthography.md` | The six Tajik-only letters, izafat, compounding, transliteration |
| `register.md` | Soviet-era loanword vs. native/Persian register judgment calls |
| `mixed-script.md` | Tajik+Russian+English, Tajik+Arabic-script, Arabic-vs-Persian, Pahlavi transliteration |
| `ocr-engines.md` | Vision-LLM vs. classical OCR engine comparison and security notes |
| `ocr-pipeline.md` | Tested pipeline, empirical failure-mode findings, output contract |
| `restoration.md` | Cross-reference-the-source correction method, supported formats (PDF/DJVU/PNG/TIFF/JPEG), formatting contract |
| `formatting.md` | Concrete docx-js implementation (verified against actual type definitions, not assumed) |
| `delivery.md` | Clean-body-text and real-footnote verification checklist |
| `scripts/find_scanned_files.py` | Read-only, cross-drive discovery of scanned-document files |
| `scripts/ocr_batch.py` | Local Tesseract batch OCR with PDF rendering and letter-substitution flagging |

## License

MIT
