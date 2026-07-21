# Tajik Toolkit — Book/Document Restoration

See [SKILL.md](SKILL.md) for when this mode applies. This is a *restoration* task, not extraction or proofreading in isolation — it combines OCR mode and editing mode under one strict deliverable contract.

---

## Method: correct by cross-referencing the source, not by reading once

1. Read each source page directly (vision) as the primary method — per SKILL.md's OCR mode.
2. Where a classical-OCR pass already exists, or where the text was previously transcribed, **compare against the source page image again** before finalizing — don't trust a single pass. This is collation, not one-shot transcription: the source image is the ground truth to check against, every time, not just the first time.
3. Reproduce the source's actual structure faithfully: paragraph breaks, footnote markers at their exact point in the body, heading hierarchy, table of contents entries, and bibliography/source-list entries — all as they appear in the original, not reorganized or "improved."
4. Apply the confidence-calibration principle (SKILL.md) to anything genuinely unclear in the source (faded print, a library stamp over text, an ambiguous letter) — flag it in the chat response, per [delivery.md](delivery.md)'s strict rules: **never annotate uncertainty inline in the delivered document**.

## Supported source formats

PDF, PNG, TIFF, JPEG — PDF pages rendered to images via PyMuPDF (verified working), PNG/TIFF/JPEG read directly (as vision input, or as classical-OCR input per [ocr-pipeline.md](ocr-pipeline.md)).

**DJVU is not yet verified on this machine** — no DjVuLibre (`ddjvu`) binary and no Python DJVU binding are installed here. DJVU is a genuinely different format from PDF — it isn't a variant PyMuPDF or the existing pipeline can already open. Before treating a `.djvu` source the same way as a PDF:

1. Confirm a DJVU-to-image conversion path is actually available (typically `ddjvu -format=png` per page, from DjVuLibre — this needs installing, it isn't present by default). Ask before installing anything new.
2. Once page images exist, everything downstream (vision reading, classical OCR fallback, correction, formatting) is identical to the PNG/TIFF/JPEG path — DJVU only affects the first conversion step, nothing else.
3. Don't claim DJVU support is "the same as PDF" in practice until step 1 has actually been done and tested on a real DJVU file — the format's absence of any installed tooling here is a real gap, not a formality.

## Mixed-script scope

Builds on [mixed-script.md](mixed-script.md)'s тадж/рус/англ and тадж/Arabic-script handling. Two points specific to restoration:

- **Persian is not the same as Arabic script** — check which language is actually intended (a Quranic citation is Arabic; a citation from a Persian classical poet like Hofiz or Rumi is Persian) before formatting or correcting it. Both use the same RTL formatting in the output (see [formatting.md](formatting.md)), but mislabeling one as the other is its own error, especially in a bibliography entry.
- **Pahlavi Latin-transliteration** — unchanged low-confidence handling from [mixed-script.md](mixed-script.md): ask which transliteration scheme is in use before correcting anything.

## The formatting contract — MANDATORY, exact values

Fixed, not a suggestion to adapt per document. See [formatting.md](formatting.md) for the concrete docx-js implementation.

| Element | Font | Size | Style | Notes |
|---|---|---|---|---|
| Titles/chapter headings | Palatino Linotype | 16pt | Bold | Must use real Word Heading styles with outline level set, so they appear in Word's Navigation Pane and can drive an auto-generated Table of Contents — not just bold+16pt text with no style attached |
| Main body text | Palatino Linotype | 12pt | Justified | |
| Footnotes | Palatino Linotype | 10pt | Justified | Real DOCX footnotes anchored at the source's footnote-marker position — see [delivery.md](delivery.md) |
| Arabic/Persian text blocks | Palatino Linotype | 16pt | Bold, right-aligned | Right-to-left paragraph direction, not just right-aligned Latin-direction text — see [formatting.md](formatting.md) for the distinction |
| Table of contents | — | — | — | Must match the source's actual TOC entries and page structure; build it from the real Heading styles above, not a manually-typed list |
| Bibliography / source list | Palatino Linotype | 12pt (body) | Justified | Reproduce exactly as the source lists it — same entries, same order, same detail |

## Batch restoration across multiple source files

When restoring a whole book (many pages) or several documents:

- Discover and inventory source files read-only before any processing, scoped to a specific folder the user names, not a whole-drive sweep (per [ocr-pipeline.md](ocr-pipeline.md)'s own lesson from being run too broadly once).
- Process and verify a small sample first (a handful of pages) before committing to the full document — doubly important here since the formatting contract (headings, footnotes, RTL blocks) has more ways to go wrong than plain text extraction does.
