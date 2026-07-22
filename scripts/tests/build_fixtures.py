#!/usr/bin/env python3
"""
Build two minimal .docx fixtures by hand-writing OOXML directly into a zip —
no Node/docx-js dependency, so this test suite runs anywhere Python does.

  clean.docx  — passes every verify_docx.py / check_consistency.py check:
                real Heading1, real footnote, real bidi+rtl RTL block, a
                verse line break done correctly with <w:br/>, no forbidden
                strings, no name-spelling inconsistencies.
  broken.docx — deliberately fails every check at once: a forbidden
                commentary string, a literal "\n" inside a <w:t> run (the
                real bug this toolkit fixed), no heading style, no RTL
                markers, no footnotes.xml at all, and two known
                name-spelling inconsistencies for check_consistency.py to
                catch (letter-confusion and near-duplicate).

These are intentionally NOT full Word-compliant documents (no styles.xml
heading definitions, no proper footnote separator parts) — they exist only
to exercise this toolkit's own verification scripts, not to be opened in
Word. Good enough for that purpose is the actual bar here.
"""
import os
import zipfile

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
{footnotes_override}</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

DOC_RELS_WITH_FOOTNOTES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>
</Relationships>
"""

DOC_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
{body}
  </w:body>
</w:document>
"""

FOOTNOTES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:footnote w:id="1">
    <w:p><w:r><w:rPr><w:rFonts w:ascii="Palatino Linotype" w:hAnsi="Palatino Linotype"/><w:sz w:val="20"/></w:rPr>
    <w:t>Ҳофизи Шерозӣ. Куллиёт. — Душанбе: Ирфон, 1983. — С.135.</w:t></w:r></w:p>
  </w:footnote>
</w:footnotes>
"""


def build_clean_body():
    return """
    <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:rPr><w:rFonts w:ascii="Palatino Linotype" w:hAnsi="Palatino Linotype"/><w:b/><w:sz w:val="32"/></w:rPr>
      <w:t>Боби якум</w:t></w:r></w:p>
    <w:p><w:pPr><w:jc w:val="both"/></w:pPr>
      <w:r><w:rPr><w:rFonts w:ascii="Palatino Linotype" w:hAnsi="Palatino Linotype"/><w:sz w:val="24"/></w:rPr>
      <w:t>Ин матни асосист, тибқи қарордоди форматгузорӣ.</w:t></w:r></w:p>
    <w:p><w:pPr><w:jc w:val="both"/></w:pPr>
      <w:r><w:rPr><w:rFonts w:ascii="Palatino Linotype" w:hAnsi="Palatino Linotype"/><w:sz w:val="24"/></w:rPr>
      <w:t>Матни бо поварақӣ</w:t></w:r>
      <w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteReference w:id="1"/></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="Palatino Linotype" w:hAnsi="Palatino Linotype"/><w:sz w:val="24"/></w:rPr><w:t>.</w:t></w:r></w:p>
    <w:p><w:pPr><w:bidi/><w:jc w:val="right"/></w:pPr>
      <w:r><w:rPr><w:rtl/><w:rFonts w:ascii="Palatino Linotype" w:hAnsi="Palatino Linotype"/><w:b/><w:sz w:val="32"/></w:rPr>
      <w:t>&#1603;&#1614;&#1576;&#1616;&#1610;&#1615;&#1585;&#1618;</w:t></w:r></w:p>
    <w:p><w:pPr><w:jc w:val="both"/></w:pPr>
      <w:r><w:rPr><w:rFonts w:ascii="Palatino Linotype" w:hAnsi="Palatino Linotype"/><w:i/><w:sz w:val="24"/></w:rPr>
      <w:t xml:space="preserve">Субҳ хезиву саломат талабӣ чун Ҳофиз,</w:t></w:r>
      <w:r><w:rPr><w:rFonts w:ascii="Palatino Linotype" w:hAnsi="Palatino Linotype"/><w:i/><w:sz w:val="24"/></w:rPr>
      <w:br/><w:t xml:space="preserve">Ҳар чӣ кардам, ҳама аз давлати "Қуръон" кардам.</w:t></w:r></w:p>
    """


def build_broken_body():
    return """
    <w:p><w:pPr><w:jc w:val="both"/></w:pPr>
      <w:r><w:t>Саҳифаи 7 (файл: 0007.png, рақами чоп: 6)</w:t></w:r></w:p>
    <w:p><w:pPr><w:jc w:val="both"/></w:pPr>
      <w:r><w:t xml:space="preserve">Субҳ хезиву саломат талабӣ чун Ҳофиз,
Ҳар чӣ кардам, ҳама аз давлати "Қуръон" кардам.</w:t></w:r></w:p>
    <w:p><w:pPr><w:jc w:val="both"/></w:pPr>
      <w:r><w:t>Ин боби бе сарлавҳаи расмист.</w:t></w:r></w:p>
    <w:p><w:pPr><w:jc w:val="both"/></w:pPr>
      <w:r><w:t>Гафур ба хона рафт. Пас аз як соат Ғафур бозгашт. Гафур хаста буд.</w:t></w:r></w:p>
    <w:p><w:pPr><w:jc w:val="both"/></w:pPr>
      <w:r><w:t>Аббос омад. Аббоса низ омад.</w:t></w:r></w:p>
    """


def write_docx(path, body_xml, with_footnotes):
    content_types = CONTENT_TYPES.format(
        footnotes_override='  <Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>\n' if with_footnotes else ""
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/document.xml", DOC_XML_TEMPLATE.format(body=body_xml))
        if with_footnotes:
            z.writestr("word/_rels/document.xml.rels", DOC_RELS_WITH_FOOTNOTES)
            z.writestr("word/footnotes.xml", FOOTNOTES_XML)


def build(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    clean_path = os.path.join(output_dir, "clean.docx")
    broken_path = os.path.join(output_dir, "broken.docx")
    write_docx(clean_path, build_clean_body(), with_footnotes=True)
    write_docx(broken_path, build_broken_body(), with_footnotes=False)
    return clean_path, broken_path


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    clean_path, broken_path = build(out)
    print(f"Wrote {clean_path}")
    print(f"Wrote {broken_path}")
