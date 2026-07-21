# Tajik Toolkit — Book/Document Restoration

See [SKILL.md](SKILL.md) for when this mode applies. This is a *restoration* task, not extraction or proofreading in isolation — it combines OCR mode and editing mode under one strict deliverable contract.

---

## Method: correct by cross-referencing the source, not by reading once

**Step 0 — calibrate the page-number offset before transcribing anything.** A PDF/image file's page index and the book's own printed page numbers are almost never the same number (front matter, plates, blank pages shift the offset). Render a handful of pages spread across the file (e.g. file-page 1, 50, 100), read the printed page number actually visible on each, and derive the offset (`printed = file_page + N`, or piecewise if plates/blanks shift it partway through). Do this once, up front, and state the offset explicitly before starting — not by re-deriving it ad hoc every time a page reference comes up. If the user names a target range by printed page number, convert to file-page indices using this offset before rendering anything.

**Step 0.5 — read the source's table of contents in full before assigning any heading level.** If the source has a Мундариҷа/Оглавление/TOC, read it completely first and build the heading hierarchy (part → chapter → section) from that structure before touching page 1 of the body. Assigning H1/H2/H3 "by eye" one page at a time, without having seen the whole hierarchy in advance, produces inconsistent levels when a later page turns out to be a subsection of something already leveled wrong. If no TOC exists, scan ahead across several pages to see the typographic pattern (font size, numbering style, centering) before committing to levels, rather than deciding page-by-page.

1. Read each source page directly (vision) as the primary method — per SKILL.md's OCR mode.
2. Where a classical-OCR pass already exists, or where the text was previously transcribed, **compare against the source page image again** before finalizing — don't trust a single pass. This is collation, not one-shot transcription: the source image is the ground truth to check against, every time, not just the first time.
3. Reproduce the source's actual structure faithfully: paragraph breaks, footnote markers at their exact point in the body, heading hierarchy (per Step 0.5), table of contents entries, and bibliography/source-list entries — all as they appear in the original, not reorganized or "improved."
4. **Cross-verify spelled-out numbers/dates against their own parenthetical numerals.** Historical/religious texts routinely give a number both ways in the same breath — e.g. a Hijri date spelled out in words followed by a numeral in parens: "санаи асни ва саласин ва моъа (132 ҳ.)". Compute or check the spelled-out value against the numeral rather than assuming they agree; if a real mismatch turns up (an error in the printed source, or a misread on this pass), flag it in the chat — never silently pick one and drop the other.
5. Apply the confidence-calibration principle (SKILL.md) to anything genuinely unclear in the source (faded print, a library stamp over text, an ambiguous letter) — flag it in the chat response, per [delivery.md](delivery.md)'s strict rules: **never annotate uncertainty inline in the delivered document**.

## Supported source formats

PDF, PNG, TIFF, JPEG — PDF pages rendered to images via PyMuPDF (verified working), PNG/TIFF/JPEG read directly (as vision input, or as classical-OCR input per [ocr-pipeline.md](ocr-pipeline.md)).

**DJVU — now verified with a real round-trip test (2026-07-22), not just a theoretical claim.** DjVuLibre installed via `winget install DjVuLibre.DjView` (provides `ddjvu.exe`, typically at `C:\Program Files (x86)\DjVuLibre\ddjvu.exe` — not added to PATH automatically on Windows). Tested: a real Tajik page image → `c44` → `.djvu` → `scripts/djvu_to_pdf.py` (wraps `ddjvu -format=pdf`) → `.pdf` → opened and rendered correctly with PyMuPDF, text fully readable.

```bash
python scripts/djvu_to_pdf.py source.djvu converted.pdf
```

After conversion, the resulting PDF enters the exact same pipeline as any other PDF source — DJVU only affects this one conversion step, nothing downstream (vision reading, classical OCR fallback, correction, formatting are all identical from here).

**Rendering DPI — default and when to raise it.** Render PDF pages at 150 DPI by default (fast, sufficient for normal-size body text). Raise to 200+ DPI specifically when: the print is small (footnotes, dense tables, marginalia), the scan itself is low-contrast/faded, or a first pass at 150 DPI produced low-confidence readings in a specific region. Don't render the whole document at high DPI by default "to be safe" — it's slower for no benefit on pages that already read cleanly; re-render just the problem pages at higher DPI instead of upgrading the whole batch.

## Non-text source elements: ornamental borders, stamps, seals

Real scans carry visual elements that aren't text: ornamental page borders, printer's ornaments, library ownership stamps/seals over or near the text, marginal ink blots. Default rule, absent a different instruction from the user:

- **Decorative/structural elements that are part of the book's own design** (ornamental chapter-opening borders, printer's ornaments between sections) — skip silently. They carry no information the restored text needs to preserve, and inserting a described placeholder ("[орнаментальная рамка]") in the body would violate [delivery.md](delivery.md)'s clean-body-text rule.
- **Library/archive stamps, ownership seals, accession stamps** — skip from the body text (they're not part of the authored work), but mention them once in the chat response if one obscures text underneath, since that's a transcription-confidence flag, not a reason to preserve the stamp itself.
- **An element that actually obscures body text** (a stamp printed over a word, a seal covering part of a line) — treat the obscured text as a normal low-confidence/uncertain reading per the confidence-calibration principle, flagged in chat, not described inline in the document.
- **Never insert a placeholder image, caption, or bracketed description of a non-text element into the delivered document body** unless the user has explicitly asked for visual elements to be represented (e.g. actually embedding a plate/illustration as an `ImageRun`) — that's a distinct, opt-in request, not a default.

## Multi-volume and series consistency

Some sources are one volume of a numbered series (e.g. Gardizi's *Zayn al-Akhbar* as Kitobi XIII of the "Тоҷнома" series) rather than a standalone book. When that's the case:

- Carry the same style-sheet decisions (SKILL.md's editing-mode style sheet: transliteration choices, register calls, recurring formula translations from [glossary.md](glossary.md)) across volumes of the same series — don't re-derive them per volume as if starting fresh.
- If a prior volume's restoration (or its [case-log.md](case-log.md) entry) is available, check it before starting a new volume and reuse its decided conventions rather than making an independent judgment call that might diverge from the earlier one.
- Note the series name/number in the chat when starting a new volume so it's clear which series-level conventions apply — this doesn't go in the delivered document unless the source's own title page states it.

## Author's footnotes vs. later editor's/translator's footnotes

A source footnote is not automatically the original author's. Modern editions of classical texts routinely carry footnotes added by a modern editor or translator — e.g. "Тарҷумаи Маҳдии Илоҳии Қумшаӣ" marking a modern translator's note on an 11th-century text. Before transcribing a footnote as-is, check what it actually is:

- **Original author's footnote** (rare for genuinely old texts, common for modern ones) — transcribe as a normal footnote per the formatting contract.
- **Editor's/translator's footnote** — still a real footnote (anchor it properly, per [delivery.md](delivery.md)'s Rule 2), but don't attribute it to the original author if asked about authorship in the chat, and note in the chat (not the document body) which footnotes are editorial so the user isn't misled about what's original to the source text.
- If the source itself distinguishes them typographically (a different marker style, a labeled "прим. ред." / "тарҷумон" note) — preserve that distinction in the footnote text itself, since it's part of what the source actually says, not commentary being added.

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

## Case log: recording real findings for future sessions

[register.md](register.md) and [glossary.md](glossary.md) both say to grow from real cases rather than invented ones — but a case only helps a future session if it's actually written down somewhere. Log real findings to [case-log.md](case-log.md) as they come up during a restoration: a footnote-misattribution catch, a register judgment call made and why, a recurring name's settled transliteration, a genuinely ambiguous non-text element and how it was resolved, a page-offset or DPI decision for a specific source. Keep entries short (a few lines: what/where/decision), dated, and tied to the specific source document — this is a log, not a rewrite of the other reference files.

## Batch restoration across multiple source files

When restoring a whole book (many pages) or several documents:

- Discover and inventory source files read-only before any processing, scoped to a specific folder the user names, not a whole-drive sweep (per [ocr-pipeline.md](ocr-pipeline.md)'s own lesson from being run too broadly once).
- Process and verify a small sample first (a handful of pages) before committing to the full document — doubly important here since the formatting contract (headings, footnotes, RTL blocks) has more ways to go wrong than plain text extraction does.

**For a single large book (400+ pages):** don't attempt it as one uninterrupted pass. Work in fixed-size page batches (e.g. 10-30 pages per batch — the real *Zayn al-Akhbar* restoration worked in 10-page increments), and:

- Deliver and verify each batch's DOCX independently (`scripts/verify_docx.py`) before starting the next — catches a formatting/attribution error early instead of letting it compound across hundreds of pages.
- Log a one-line checkpoint to [case-log.md](case-log.md) after each batch (page range done, any open questions) so an interrupted session can resume from the last completed batch instead of re-reading pages that are already done.
- Keep the running style sheet (SKILL.md editing mode) and any series-level conventions (Multi-volume section above) visible across batches — a name transliterated one way in batch 1 must stay that way in batch 12.
