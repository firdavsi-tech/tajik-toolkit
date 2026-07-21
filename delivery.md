# Tajik Toolkit — Output Delivery (DOCX and other formats)

See [SKILL.md](SKILL.md) for the strict rules this implements. This file is the concrete "how," not the "why."

---

## Rule 1: clean body text — a checklist before writing any output file

Before generating the document, scan the assembled content for anything that isn't the source text:

- Page/file/scan labels ("Саҳифаи N", "файл: 0007.png", "рақами чоп: 6")
- Method notes ("хониши мустақими vision", "барои санҷиши сифати...")
- Uncertainty prose ("дар аслаш норавшан аст", "бо эътимоди пурра хонда нашуд")
- Section headers added for your own orientation while transcribing that aren't in the source

None of this goes in the deliverable. If headers were used to keep track of which page was being transcribed while working, strip them before the final write — they were a working aid, not part of the output.

If uncertain readings need marking at all, agree on one minimal convention up front (e.g. a single bracketed placeholder) and use it silently — don't explain each occurrence inline. Explain the whole set of uncertain spots once, in the chat response, not in the file.

## Rule 2: real DOCX footnotes, not inline paragraphs

Using `docx` (docx-js): a footnote is a `FootnoteReferenceRun` inserted at the exact point in the body text where the source shows a footnote marker, paired with an entry in the document's `footnotes` config keyed by the same number. This renders as an actual Word footnote — reference mark in the body, note text at the bottom of the page, exactly like the source.

```js
const { Document, Paragraph, TextRun, FootnoteReferenceRun } = require("docx");

// In the paragraph where the source has a footnote marker:
new Paragraph({
  children: [
    new TextRun("...тавассути замхорию тарбияти волидайн ба ҳифзи \"Қуръон\"-и маҷид шарафёб гардидаанд"),
    new FootnoteReferenceRun(1),   // renders as a superscript "1" linked to footnote 1
    new TextRun(". Шарафи ҳифзи ..."),
  ],
});

// At the Document level, not inside a section's children array:
const doc = new Document({
  sections: [{ children: [...] }],
  footnotes: {
    1: { children: [new Paragraph({ children: [new TextRun("Ҳофизи Шерозӣ. Куллиёт...")] })] },
    2: { children: [new Paragraph({ children: [new TextRun("Абӯалӣ ибни Сино. Тадбири манзил...")] })] },
  },
});
```

**What NOT to do**: writing footnote text as plain `Paragraph` elements appended after the section's body text, styled smaller/italic to look footnote-like. That is not a footnote — it's inline text that happens to be styled differently, and it does not match поварақӣ placement (bottom of the page, linked to a specific point in the body) that the source document actually has.

## Rule 3: verify before declaring done

After writing the file, re-open it (unzip → read `word/document.xml`, or render if LibreOffice/pandoc is available) and check:

- No text run contains a page label, file name, or commentary phrase — grep the extracted text runs for suspicious substrings ("файл:", "Саҳифаи", "Эзоҳ:", "Изоҳ:") before calling the delivery done.
- Footnote reference marks appear in the body at the right points, and `footnotes` entries exist with matching numbers — not just a styled paragraph block.
- For a restoration (see [formatting.md](formatting.md)): headings carry both a real `HeadingLevel` and the explicit font/size override, and any RTL block has both `bidirectional` (paragraph) and `rightToLeft` (run).

Don't just generate and hand over — confirm what's actually in the file. This has caught real bugs before, including a footnote misattributed to the wrong page/word during a real restoration.
