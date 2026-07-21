# Tajik Toolkit — Mixed-Script Text

See [SKILL.md](SKILL.md) for when to load this. Covers тадж+рус, тадж+англ, тадж+Arabic-script, Arabic-vs-Persian, and Pahlavi Latin-transliteration.

---

## Mixed script: Tajik + Russian + English

Tajik text mixed with Russian or English (common in bilingual documents, code-switched speech transcripts, technical text with English terms) needs segmentation before either language's conventions get applied:

- **Script boundary is the first, cheap signal**: Latin-script runs are almost certainly English (or a transliterated term); the ambiguity is entirely within Cyrillic-script runs, where it could be Tajik or Russian.
- **Within Cyrillic runs, the six Tajik-only letters are a strong Tajik signal** where present — but their *absence* doesn't mean Russian, since plenty of genuine Tajik text/sentences won't happen to use one of the six letters (see [orthography.md](orthography.md)). Fall back to vocabulary and grammar (izafat construction, Tajik-specific function words) to disambiguate when the letter signal is absent.
- **Don't apply one language's typography/register rules to the other's spans.** A Tajik sentence doesn't need a Russian-specific quote-nesting rule applied to it, and vice versa — keep rule sets scoped to their own spans.
- **English spans**: treat as English for spelling/grammar purposes; don't attempt Tajik-specific correction on them. Watch for transliterated proper nouns that look like English but are actually a Latin rendering of a Tajik or Russian name — these need the transliteration-consistency handling from [orthography.md](orthography.md), not English spellchecking.

## Mixed script: Tajik + Arabic script (confirmed real, not hypothetical)

Religious and classical-literature Tajik texts — tajwid manuals, Quran commentary, anything quoting Persian/Arabic classical sources — routinely mix printed Cyrillic Tajik with Arabic-script passages (Quranic verses, Arabic grammatical examples). Confirmed directly against a real scanned 1996 book (see [ocr-pipeline.md](ocr-pipeline.md) for the test): a two-column layout with Tajik questions in Cyrillic and Arabic-script Quranic examples side by side.

This is a fundamentally different problem from тадж/рус/англ mixing above — it isn't a letter-substitution or vocabulary-register question, it's a different script family entirely. A classical OCR engine approximating Tajik with `rus` cannot read Arabic script at all and produces pure noise for it, and that noise doesn't reliably self-identify as garbage after the fact (some of it still contains a stray Cyrillic-range character and slips past automated detection). Practical handling:

- **Don't attempt to "correct" Arabic-script noise using Tajik orthography rules** — г/к/х substitution logic doesn't apply; the output isn't misread Tajik, it's not Tajik at all.
- **For accurate transcription of the Arabic-script portion, use direct vision-based reading of that region** (per SKILL.md's OCR mode) rather than trusting any classical-OCR output there — this is the one case where the automated local pipeline isn't a degraded-but-usable fallback, it's simply not applicable.
- **When reporting extracted text from such a document, separate the two clearly** — don't present Arabic-script noise as if it were an uncertain Tajik reading; label it as a different script requiring separate handling.

## Arabic vs. Persian — don't conflate them just because the script looks similar

Persian (Farsi) uses a Perso-Arabic script with extra letters Arabic doesn't have (پ چ ژ گ) and different vocabulary and pronunciation despite sharing most of the alphabet. A Tajik text quoting the Qur'an is quoting Arabic; a Tajik text quoting Hofiz, Rumi, or another Persian classical author is quoting Persian — check which is actually intended from context (the cited author/source) rather than assuming "Arabic-looking script = Arabic." Both need the same "don't correct with Tajik rules, read directly" handling above, but mislabeling one as the other is its own kind of error worth avoiding, especially in a bibliography or citation entry where the source language matters. For restoration work, both render with the same RTL formatting (see [formatting.md](formatting.md)) — but identify the language correctly before treating it as either.

## Pahlavi (Middle Persian) Latin transliteration — explicit low-confidence zone

This is a specialized historical-linguistics domain, not general text editing, and it gets its own honesty flag distinct from the rest of this skill:

- Multiple competing Pahlavi transliteration conventions exist in scholarship (e.g. the systems associated with MacKenzie and with Nyberg differ in how they render certain consonants and vowels) — a Latin-transliterated Pahlavi string can look "wrong" under one convention while being correct under another. Don't silently normalize between conventions.
- **Ask which transliteration scheme is in use, or which source it's drawn from, before correcting anything** — this is squarely a "query, don't assert" case per SKILL.md's confidence calibration, more so than anything else this skill covers. Treat any specific claim about "the correct Pahlavi transliteration of X" as something to verify against a cited scholarly source, not something to generate from this model's own training data with confidence.
- If the actual need is modern Tajik text that merely cites or quotes Pahlavi/Old Iranian material (rather than editing Pahlavi transliteration itself), the Tajik-language surrounding text follows the normal rules in this skill; only the quoted Pahlavi span needs this heightened caution.
- If this comes up often enough to be worth building out properly, the right next step is getting a specific transliteration scheme and a small set of verified examples from the user or a cited source, rather than this skill guessing at scholarly convention from general training data.
