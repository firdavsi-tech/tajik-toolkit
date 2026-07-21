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

## Bibliography / source list

Same body-text formatting (Palatino Linotype 12pt Justified) as the main text — the contract doesn't call out different formatting for this section, only that its *content* must match the source's actual entries exactly, in the source's order. Don't reformat citation style or "clean up" entries the source presents inconsistently — reproduce them as-is.

## Verification checklist before declaring a restoration done

Beyond [delivery.md](delivery.md)'s existing checks (no editorial commentary in the body, real footnotes present):

- [ ] Every heading paragraph has both a `HeadingLevel` and the explicit Palatino/16/Bold run override
- [ ] The TOC (if present) was generated from those headings, not typed manually
- [ ] Every Arabic/Persian block paragraph has `bidirectional: true` AND its runs have `rightToLeft: true`
- [ ] Body text runs specify `font: "Palatino Linotype", size: 24`; footnote runs specify `size: 20`
- [ ] Bibliography entries match the source's list one-to-one — count them against the source page if unsure
