# Tajik Toolkit — Orthography

See [SKILL.md](SKILL.md) for when to load this. This covers mechanics specific to Tajik Cyrillic; it does not attempt to be a complete grammar reference.

---

## The six Tajik-only letters

| Letter | Sound (rough) | Common wrong substitution | Why it happens |
|---|---|---|---|
| Ғ ғ | voiced uvular fricative | г | Visually similar; г is the nearest Russian letter |
| Қ қ | voiceless uvular stop | к | Same pattern — nearest Russian look-alike |
| Ҳ ҳ | voiceless pharyngeal/glottal | х | Russian х is the nearest available substitute on a Russian-only keyboard |
| Ҷ ҷ | voiced postalveolar affricate | ч or ж | Depends on which sound the substituter was aiming for |
| Ӣ ӣ | long і | и | The macron/breve gets dropped, especially by non-Tajik input methods |
| Ӯ ӯ | rounded back vowel, distinct from у | у | Same — diacritic dropped |

**Why this matters for editing, not just typing:** these substitutions change or destroy meaning — they aren't cosmetic. A text produced by OCR of a scanned document, dictation, copy-paste from a source without proper Tajik font/encoding support, or someone typing on a Russian-only keyboard will systematically show this pattern. When reviewing such a source, scan specifically for words that would make more sense with one of these six letters restored, rather than assuming the text is already using correct Tajik-specific characters throughout.

## Izafat construction

Tajik uses the izafat (-и / -йи) to link a noun to a following modifier or possessor (roughly parallel to Persian ezafe). Getting the connector wrong, dropping it, or misplacing it changes the grammatical relationship between the words it's supposed to link — treat it as a genuine grammar point, not a stylistic optional extra, when reviewing formal or literary text.

## Compound words and hyphenation

Tajik compounding conventions (when to write as one word, hyphenated, or as separate words) don't map directly from Russian compounding rules — don't apply Russian hyphenation instincts by default. When a document already hyphenates a term a particular way, follow that as an established convention (style-sheet principle from SKILL.md) rather than "correcting" it to a Russian-influenced pattern.

## Unicode normalization: Ӣ/Ӯ can be encoded two different ways

Ӣӣ and Ӯӯ each have two valid Unicode encodings that render identically but are different byte sequences: a single precomposed codepoint (NFC — U+04E2/U+04E3 for Ӯӯ, U+04EE/U+04EF... check the specific pair in use), or a base letter plus a combining diacritic as separate codepoints (NFD). Text assembled from different sources (typed fresh vs. copy-pasted from a PDF vs. output from an OCR engine) can mix both forms invisibly — visually identical, but `==` string comparison or exact-match tooling (like [check_consistency.py](scripts/check_consistency.py)'s name-grouping, or a TOC hyperlink matching a heading's exact text) will treat them as different strings.

**When building or checking a document programmatically, normalize to NFC first** (Python: `unicodedata.normalize("NFC", text)`) before any exact-match comparison — don't assume the source text arrived in one consistent form. This is a real risk for any script in this toolkit that does string matching on Tajik text, not just a theoretical concern.

## Transliteration of foreign and Russian-origin names

Names of people, places, and Russian-origin technical/institutional terms get rendered into Tajik Cyrillic with conventions that don't always match a straightforward Russian-to-Tajik letter swap — some established Soviet-era transliterations persist by convention even where a more literal rendering would differ. When a document already transliterates a recurring name a particular way, log it to the style sheet and stay consistent with it rather than re-deriving the "correct" transliteration each time it appears.
