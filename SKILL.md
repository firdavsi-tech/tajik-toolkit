---
name: tajik-toolkit
description: Complete toolkit for Tajik-language (тоҷикӣ) text — editing and proofreading, OCR extraction from images/scans/PDFs, and full book restoration to a formatted DOCX matching the source. Covers mixed Tajik/Russian/English/Arabic/Persian text and Latin-transliterated Pahlavi. Use when writing, editing, correcting, reviewing, extracting, or restoring Tajik text or documents, or translating into/out of Tajik.
version: 1.1.0
---

# Tajik Toolkit

One skill covering three layers of the same problem: **editing** Tajik text you already have, **extracting** Tajik text from an image/scan/PDF, and **restoring** a whole scanned document into a formatted DOCX matching the source. Consolidated from three separate skills (`tajik-text`, `tajik-ocr`, `tajik-book-restore`) built and tested over several real tasks, including a real 49-page tajwid manual and a real 416-page 11th-century historical chronicle (Gardizi's *Zayn al-Akhbar*).

## Calibrate confidence before touching anything (do this first, always)

Tajik is a lower-resource language for this model compared to Russian, English, or major Persian corpora. Treat that as a real constraint, not a formality:

- **High confidence, act directly:** the six Tajik-specific Cyrillic letters and their common confusions (see [orthography.md](orthography.md)), basic grammar, obvious typos, spacing/punctuation mechanics.
- **Medium confidence, propose + flag:** register choices (Soviet-era loanword vs. native/Persian-origin alternative — see [register.md](register.md)), which spelling variant is more standard, domain terminology.
- **Low confidence, query rather than assert:** claims about current official style-guide rules that aren't independently verifiable here, or Pahlavi transliteration conventions (see [mixed-script.md](mixed-script.md)). Say "I believe X, but this is worth checking" rather than presenting it as settled fact.

## Which mode applies

| Situation | Use |
|---|---|
| You already have Tajik text (typed, pasted, or from a prior transcription) and need to fix/review it | Editing mode — below, plus [orthography.md](orthography.md), [register.md](register.md), [mixed-script.md](mixed-script.md) |
| You have an image, scan, or PDF and need the text out of it | OCR mode — [ocr-engines.md](ocr-engines.md), [ocr-pipeline.md](ocr-pipeline.md) |
| You need a whole scanned book/document turned into a properly formatted DOCX matching the source (headings, footnotes, TOC, bibliography) | Restoration mode — [restoration.md](restoration.md), [formatting.md](formatting.md) |

These aren't mutually exclusive — restoration mode uses OCR mode's extraction and editing mode's correction rules underneath, per its own method.

## Editing mode

**Voice preservation and minimal edit:** before changing anything, check — is this an error, or a deliberate choice? Regional dialect forms, intentional informality, and rhetorical repetition are not errors. Apply the smallest edit that fixes an actual problem.

**Error vs. choice, and the style sheet:** fix silently when the correction is unambiguous and preserves meaning and voice. Query when the change could alter meaning, register, or an intentional non-standard form. Build a running style sheet for anything decided once (loanword spelling variant, name transliteration, quote-mark convention) so later instances in the same document stay consistent. Follow a document's existing conventions rather than imposing a different house style.

**Verification for high-stakes text:** for a quick correction, one careful pass is enough. For a document where meaning-drift matters (official correspondence, published text, translation), mentally back-translate the result and check it still says what the author meant. Delegate the verification pass to a subagent if the document is long.

**Review vs. rewrite:** when checking or proofreading, return the corrected version plus a change list — don't silently overwrite the source. Rewrite in place only when explicitly asked.

**Output:** corrected text (or updated file, `UPDATED_` prefix), a change list grouped by pattern where an issue repeats, queries called out separately from silent corrections, anything below the confidence threshold stated as uncertain.

## OCR mode — the core insight

There are two fundamentally different kinds of OCR:

1. **Classical trained OCR** (Tesseract, PaddleOCR-classic, RapidOCR): a fixed model trained per language. No Tajik model exists anywhere — verified directly against Tesseract's official `tessdata_fast`/`tessdata_contrib` repos via GitHub's API. The only workaround is approximating with the nearest language (`rus`), which systematically misreads the six Tajik-only letters.
2. **Vision-LLM-based OCR** (this model's own vision, PaddleOCR-VL, DeepSeek-OCR): reads the image guided by a text prompt, not a fixed trained character set — so it can be told about an unsupported language's alphabet directly. A real workaround classical OCR cannot offer.

**Default to option 2.** For a single image or small batch: describe/paste the image and transcribe directly, noting explicitly that it's Tajik (Cyrillic + Ғ ғ Қ қ Ҳ ҳ Ҷ ҷ Ӣ ӣ Ӯ ӯ). No script, no API key needed. Reserve the classical-engine fallback ([ocr-pipeline.md](ocr-pipeline.md)'s `scripts/`) for bulk/offline processing, and expect to need the correction pass in [orthography.md](orthography.md) afterward. See [ocr-engines.md](ocr-engines.md) for the full engine comparison and [ocr-pipeline.md](ocr-pipeline.md) for tested usage, empirical findings, and the output contract.

## Restoration mode

A restoration corrects by **cross-referencing the source repeatedly**, not one-shot transcription — and delivers under a fixed formatting contract, not plain text. See [restoration.md](restoration.md) for the method and supported formats, [formatting.md](formatting.md) for the concrete DOCX implementation (Palatino Linotype per element, real Heading styles for TOC, real footnotes, RTL Arabic/Persian blocks).

## Output delivery — STRICT rules, no exceptions

These were violated in real use once and the user flagged it explicitly. Non-negotiable:

1. **The delivered document contains the source text and nothing else.** No page/file labels, no method preambles, no commentary about how the transcription was made or what's uncertain — anywhere in the document body. All of that belongs in the chat response, never in the file.
2. **Footnotes are real footnotes**, anchored at the source's marker position (`FootnoteReferenceRun` + `footnotes` config in docx-js) — never plain paragraphs appended after a section.
3. **Uncertain readings get a minimal, silent, pre-agreed marker if any** — not inline prose explaining the uncertainty. Explain uncertainty once, in the chat, not in the file.

See [delivery.md](delivery.md) for the full checklist and verification steps (grep the output for forbidden strings before declaring done).

## Rules adopted from the 12+ skills this was built from, and why

- **Always show complete extracted/corrected text, never silently truncate** — the user needs the full content; a "here's a preview" silently loses data.
- **Surface explicit success/error state**, never blend an error into the text output where it could be mistaken for content.
- **Per-region confidence, not a single blended score** — flag specific low-confidence spans for review.
- **No silent dependency auto-installation, no API keys as CLI arguments, no hardcoded single cloud provider** — ask before installing, read credentials from environment variables only, always offer the local/offline option alongside any cloud option.

## Supporting files

| File | Load when |
|---|---|
| [orthography.md](orthography.md) | Checking letter confusions, izafat/hyphenation, or transliteration of names |
| [register.md](register.md) | A register/loanword judgment call comes up |
| [glossary.md](glossary.md) | Recurring Arabic honorific formulas (салла-л-Лоҳу алайҳи ва саллам, etc.) in historical/religious texts |
| [mixed-script.md](mixed-script.md) | Text mixes Tajik with Russian/English/Arabic/Persian, or quotes Pahlavi in Latin transliteration |
| [ocr-engines.md](ocr-engines.md) | Choosing a specific OCR engine/API |
| [ocr-pipeline.md](ocr-pipeline.md) | Running the classical-OCR fallback scripts, batch/PDF processing, or the output contract |
| [restoration.md](restoration.md) | Restoring a whole scanned book/document — method, supported source formats (PDF/DJVU — now verified via a real round-trip test/PNG/TIFF/JPEG) |
| [formatting.md](formatting.md) | Generating the DOCX for a restoration — concrete docx-js patterns, including tables |
| [delivery.md](delivery.md) | Before writing any output file — clean-body-text and real-footnote checklist; run `scripts/verify_docx.py` to automate it |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/find_scanned_files.py` | Read-only, cross-drive discovery of scanned-document files |
| `scripts/ocr_batch.py` | Local Tesseract batch OCR with PDF rendering and letter-substitution flagging |
| `scripts/djvu_to_pdf.py` | Converts DJVU to PDF (via DjVuLibre's `ddjvu`) so it enters the same pipeline as any PDF source |
| `scripts/verify_docx.py` | Automates the delivery/formatting checklist against a generated DOCX — forbidden strings, real footnotes, fonts, headings, RTL markers |
