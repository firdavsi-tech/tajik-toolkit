# Tajik Toolkit — DOCX Formatting Implementation

See [restoration.md](restoration.md) for the formatting contract this implements. Uses `docx` (docx-js) — see the general `docx` skill for setup/verification gotchas; this file covers only the restoration-specific patterns.

**Verified, not guessed:** the `rightToLeft` (TextRun) and `bidirectional` (Paragraph) properties below were confirmed by inspecting `docx`'s actual `dist/index.d.ts` type definitions directly, not assumed from general familiarity with the library.

---

## Body text: Palatino Linotype 12pt, Justified

```js
new Paragraph({
  alignment: AlignmentType.JUSTIFIED,
  children: [new TextRun({ text: "...", font: "Palatino Linotype", size: 24 })], // size is in half-points: 12pt = 24
});
```

## Headings: Palatino Linotype 16pt Bold, real Word heading styles

The heading must carry BOTH the structural heading level (so it shows in Word's Navigation Pane and can drive an auto-generated TOC) AND the explicit font override — one without the other fails the contract:

```js
new Paragraph({
  heading: HeadingLevel.HEADING_1,   // gives it outline level — required for Navigation Pane / TOC
  children: [new TextRun({ text: "Боби якум", font: "Palatino Linotype", size: 32, bold: true })], // 16pt = 32 half-points
});
```

Using `heading: HeadingLevel.HEADING_1` alone applies docx-js's *default* heading style (usually a different font/size) — it will show in the Navigation Pane but won't match the Palatino/16/Bold requirement until the explicit `TextRun` override above is also applied. Match the heading level to the source's actual hierarchy (part/chapter/section), not a flat single level for everything.

**Auto-generating the Table of Contents from these headings:**

```js
const { TableOfContents } = require("docx");
// Insert near the top of the document:
new TableOfContents("Мундариҷа", { hyperlink: true, headingStyleRange: "1-3" })
```

This only picks up paragraphs that actually used `heading: HeadingLevel.*` — confirming the contract's other half of the requirement (structural heading, not just bold 16pt text) is what makes the TOC possible at all.

## Footnotes: Palatino Linotype 10pt, Justified, real footnotes

Building on [delivery.md](delivery.md) (which establishes *that* footnotes must be real, anchored footnotes, not paragraphs) — add the font spec here:

```js
const footnotes = {
  1: {
    children: [new Paragraph({
      alignment: AlignmentType.JUSTIFIED,
      children: [new TextRun({ text: "Ҳофизи Шерозӣ. Куллиёт...", font: "Palatino Linotype", size: 20 })], // 10pt = 20 half-points
    })],
  },
};
// referenced in body via FootnoteReferenceRun(1), exactly as in delivery.md's example
```

## Arabic/Persian text blocks: Palatino Linotype 16pt Bold, right-to-left

This needs both the run-level and paragraph-level RTL flags — one alone is insufficient. `rightToLeft` on the run affects how that run's script is rendered/measured; `bidirectional` on the paragraph sets the paragraph's base direction so right-alignment is *actually* right-to-left flow, not just Latin-direction text pushed to the right margin:

```js
new Paragraph({
  bidirectional: true,
  alignment: AlignmentType.RIGHT,
  children: [new TextRun({
    text: "كَبِيرْ - تَدْبِيرْ",
    font: "Palatino Linotype",
    size: 32,   // 16pt
    bold: true,
    rightToLeft: true,
  })],
});
```

Before applying this, confirm per [mixed-script.md](mixed-script.md) whether the passage is actually Arabic or actually Persian — both use this same RTL formatting, but don't apply Tajik-orthography correction logic to either (that's a different script/language entirely).

### Quranic ayat citations specifically

A Qur'anic verse quoted inline (distinct from a general Arabic/Persian block above) conventionally gets set off with the ornamental bracket pair ﴾ ﴿ (U+FD3E/U+FD3F, not a regular parenthesis) around the Arabic text, and is often centered rather than right-aligned when it's a standalone cited verse rather than part of a running RTL paragraph:

```js
new Paragraph({
  bidirectional: true,
  alignment: AlignmentType.CENTER,
  children: [new TextRun({
    text: "﴾ إِنَّ هَـٰذَا الْقُرْآنَ يَهْدِي لِلَّتِي هِيَ أَقْوَمُ ﴿",
    font: "Palatino Linotype",
    size: 32,
    bold: true,
    rightToLeft: true,
  })],
});
```

Only apply the bracket pair to an actual Qur'anic citation, not to general Arabic/Persian quotations — using it on a Hofiz couplet, for instance, would misrepresent a Persian poet's line as scripture. Reproduce the source's own convention if it already brackets citations differently (a different bracket glyph, or none at all) rather than imposing this as a default.

## Verse/poetry and multi-line text: never use `\n` inside a TextRun

**A confirmed real bug, not a theoretical concern:** a literal `\n` character inside a `TextRun`'s `text` string (e.g. `new TextRun({ text: "Line one,\nLine two." })`, used for Hofiz couplets in a real restoration) gets written into `<w:t xml:space="preserve">` as-is, with **no `<w:br/>` element** — confirmed by generating a minimal test file and inspecting the raw XML. Word does not reliably render a bare `\n` inside text content as a visible line break; it requires an actual `<w:br/>` element.

**The correct pattern** — confirmed against `docx`'s actual `dist/index.d.ts` (`IRunOptionsBase.break?: number`) and by inspecting the generated XML, which does produce a real `<w:br/>`:

```js
new Paragraph({
  alignment: AlignmentType.JUSTIFIED,
  children: [
    new TextRun({ text: "Субҳ хезиву саломат талабӣ чун Ҳофиз,", font: "Palatino Linotype", size: 24 }),
    new TextRun({ text: "Ҳар чӣ кардам, ҳама аз давлати \"Қуръон\" кардам.", font: "Palatino Linotype", size: 24, break: 1 }),
  ],
});
```

`break: 1` on a run inserts a `<w:br/>` before that run's own text — chain more runs the same way for a multi-line verse block. Never split verse lines with a literal `\n` character, and never rely on `xml:space="preserve"` to make whitespace do a line break's job — see [case-log.md](case-log.md) for the real case this was caught from, including which already-delivered document needs its poetry paragraphs rebuilt.

## Bibliography / source list

Same body-text formatting (Palatino Linotype 12pt Justified) as the main text — the contract doesn't call out different formatting for this section, only that its *content* must match the source's actual entries exactly, in the source's order. Don't reformat citation style or "clean up" entries the source presents inconsistently — reproduce them as-is.

## Tables (gap found in real use, not in the original contract)

The original 8-point formatting contract (SKILL.md/restoration.md) covers body, headings, footnotes, and RTL blocks — it does not specify tables, even though real restoration work has needed them (Gardizi's *Zayn al-Akhbar* includes several dense genealogical tables spanning multiple pages). Until the user specifies otherwise, apply this default: table cells use a smaller size than body text (10pt / size 20, matching footnote size, since dense tables read better compact) at the same Palatino Linotype font, and header cells (row/column labels) are bold with light shading for visual separation:

```js
const { Table, TableRow, TableCell, WidthType } = require("docx");

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 1100, type: WidthType.DXA },
    shading: opts.header ? { type: "clear", fill: "D9D9D9" } : undefined,
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: text || "", font: "Palatino Linotype", size: 20, bold: !!opts.header })],
    })],
  });
}

new Table({
  width: { size: 9000, type: WidthType.DXA },
  columnWidths: [1400, 1100, 1100],   // must sum to the table's width, and match cell widths exactly — a docx-js gotcha, not optional
  rows: [
    new TableRow({ children: [cell("", { header: true, width: 1400 }), cell("Col A", { header: true }), cell("Col B", { header: true })] }),
    new TableRow({ children: [cell("Row label", { header: true, width: 1400 }), cell("data"), cell("data")] }),
  ],
});
```

**A genuine flag, not a made-up rule:** this default (10pt cells, centered, shaded header) is a reasonable choice made once real tables showed up, not something the user specified in the original 8-point contract. If a restoration involves tables, confirm this default is acceptable before committing to it at scale, the same way any other formatting assumption should be checked when the contract doesn't cover a case explicitly.

**Dense tabular proper-noun data carries more transcription risk than flowing prose** — a single misaligned cell in a genealogical table misattributes real historical data, which is a more consequential error than a typo in a sentence. Flag dense tables for extra source cross-referencing specifically (per [restoration.md](restoration.md)'s method), not just the standard one-pass check.

## Running headers/footers and page numbers matching the source

**Not in the original 8-point contract — a genuine flag, like the tables section above, not a default to apply silently.** A full-book restoration's source often has running headers (book/chapter title) and printed page numbers; the contract doesn't say whether the restored DOCX should reproduce them. Confirm with the user before adding headers/footers — a small excerpt restoration ("pages 100-110") may not want a running header referencing a book title never introduced in the excerpt, while a full-book restoration might.

If confirmed wanted, the docx-js pattern:

```js
const { Header, Footer, PageNumber } = require("docx");

const doc = new Document({
  sections: [{
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Тартил-ул-Қуръон", font: "Palatino Linotype", size: 20 })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ children: [PageNumber.CURRENT], font: "Palatino Linotype", size: 20 })],
        })],
      }),
    },
    children,
  }],
});
```

Word's own page-numbering starts at 1 for the section regardless of the source's printed page numbers. If the file needs to *display* the source's actual printed number rather than Word's own running count, set it explicitly via `properties.page.pageNumbers.start` (confirmed against `docx`'s actual `dist/index.d.ts` — `ISectionPropertiesOptionsBase.page.pageNumbers: IPageNumberTypeAttributes`) using the offset already calibrated in restoration.md's Step 0:

```js
sections: [{
  properties: { page: { pageNumbers: { start: 100 } } },  // matches the source's own printed page number
  headers: { ... }, footers: { ... }, children,
}],
```

## Verification checklist before declaring a restoration done

Beyond [delivery.md](delivery.md)'s existing checks (no editorial commentary in the body, real footnotes present) — and use `scripts/verify_docx.py` to automate the mechanical parts of this rather than re-typing the same unzip+grep commands by hand:

- [ ] Every heading paragraph has both a `HeadingLevel` and the explicit Palatino/16/Bold run override
- [ ] The TOC (if present) was generated from those headings, not typed manually
- [ ] Every Arabic/Persian block paragraph has `bidirectional: true` AND its runs have `rightToLeft: true`
- [ ] Body text runs specify `font: "Palatino Linotype", size: 24`; footnote runs specify `size: 20`
- [ ] Table cells specify `font: "Palatino Linotype"` at whatever size was agreed (default 20, per the tables section above)
- [ ] Bibliography entries match the source's list one-to-one — count them against the source page if unsure
- [ ] No verse/multi-line text uses a literal `\n` inside a `TextRun`'s `text` — every internal line break uses `break: 1` on the following run (see the Verse/poetry section above; `scripts/verify_docx.py` now checks for this automatically)

```bash
python scripts/verify_docx.py output.docx --expect-headings --expect-footnotes --expect-rtl
```

(Only pass the `--expect-*` flags that actually apply to the document being checked — a restoration with no Arabic/Persian content shouldn't be checked with `--expect-rtl`.)
