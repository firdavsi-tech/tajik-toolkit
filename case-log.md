# Tajik Toolkit — Case Log

See [restoration.md](restoration.md) for why this file exists: register.md and glossary.md say to grow from real cases, not invented ones, but a case only helps a future session if it's written down. Append short, dated entries here as real cases come up — don't rewrite the other reference files themselves for a one-off case.

Entry format: date, source document, what happened, what was decided. A few lines, not a paragraph.

---

## 2026-07-22 — docx-js: literal `\n` in a TextRun does not render as a line break

**Source:** discovered while re-checking the delivered *Тартил-ул-Қуръон* restoration (poetry couplets), confirmed with a minimal isolated test, not assumption.

**Finding:** `new TextRun({ text: "Line one,\nLine two." })` writes the literal `\n` character as-is inside `<w:t xml:space="preserve">`, with no `<w:br/>` element. Word does not reliably turn that into a visible line break. The correct pattern is `new TextRun({ text: "Line two.", break: 1 })` (confirmed against `docx`'s actual `dist/index.d.ts` — `IRunOptionsBase.break?: number` — and by inspecting the generated XML, which does produce a real `<w:br/>`).

**Decision:** documented in [formatting.md](formatting.md)'s new "Verse/poetry and multi-line text" section. Any prior restoration that used `\n` inside a single TextRun for verse/couplets (the *Тартил-ул-Қуръон* delivery did) needs its poetry paragraphs rebuilt with `break: 1` between lines.

## 2026-07-21 — Footnote misattribution, *Зайну-л-ахбор* (Gardizi), pages 100-110

**Source:** `kitobkhon-net-abusaid-gardezi.-zayn-ul-akhbor.pdf`, restoration of pp. 100-110.

**Finding:** footnotes "Ва Қарирӣ" / "Ҳадмаса" were initially attached to page 106 in the draft; re-checking against the source images showed they belong to page 107, split correctly alongside "Хизрона" on 106.

**Decision:** caught only by re-cross-referencing the source per restoration.md's core method (step 2) — reinforces that a single pass, even a careful one, isn't sufficient for footnote-to-page attribution in dense historical text with multiple footnotes per page.

## 2026-07-21 — RapidOCR has no Tajik model (verified directly, not assumed)

**Source:** general OCR-engine research for [ocr-engines.md](ocr-engines.md).

**Finding:** RapidOCR's actual `default_models.yaml` config ships a generic "cyrillic" recognition model but no "tajik"/"tgk" model — same gap as Tesseract, confirmed against the real config file rather than inferred from general reputation.

**Decision:** ocr-engines.md's RapidOCR row updated from "unconfirmed" to this verified finding.

## 2026-07-22 — DJVU→PDF round-trip verified with a real test

**Source:** general format-support gap noted in restoration.md ("DJVU — not yet verified").

**Finding:** a real Tajik page image → `c44` → `.djvu` → `scripts/djvu_to_pdf.py` (wraps DjVuLibre's `ddjvu -format=pdf`) → `.pdf` opened and rendered correctly in PyMuPDF, text fully readable.

**Decision:** restoration.md's DJVU section updated from a theoretical claim to a verified one.
