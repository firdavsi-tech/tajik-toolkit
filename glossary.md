# Tajik Toolkit — Recurring Arabic Honorific Formulas

See [SKILL.md](SKILL.md) for when to load this. Historical/religious Tajik texts (chronicles, tafsir, hadith collections, biographical works) repeat a small set of standard Arabic honorific formulas constantly — dozens of times per chapter in some genres. Getting these consistently right matters more than most vocabulary because they're so frequent: one wrong spelling repeated 40 times across a restoration is a much bigger consistency problem than a single rare word.

Unlike [register.md](register.md)'s Sovietism judgment calls, these are **not** ambiguous or register-dependent — they're fixed, universally standardized Islamic formulas with one correct transliteration into Tajik Cyrillic. High confidence, not a judgment call.

---

## The core formulas

| Tajik Cyrillic | Used after | Meaning |
|---|---|---|
| салла-л-Лоҳу алайҳи ва саллам (often abbreviated (с) or (с.а.в.с) in running text) | The Prophet Muhammad's name | "God's blessings and peace be upon him" (ṣallā llāhu ʿalayhi wa sallam) |
| алайҳи-с-салом (abbreviated (а)) | A prophet's name (other than Muhammad) | "peace be upon him" ('alayhi as-salām) |
| разийа-л-Лоҳи анҳу (masc.) / разийа-л-Лоҳи анҳо (fem.) | A companion's (ṣaḥāba) name | "may God be pleased with him/her" (raḍiya llāhu 'anhu/'anhā) |
| раҳмату-л-Лоҳи алайҳ | A deceased respected person's name | "God's mercy be upon him" (raḥmatu llāhi 'alayhi) — used for scholars/notables, not exclusively prophets/companions |
| таъоло / азза ва ҷалла | After "Худо"/"Аллоҳ" (God) | "the Exalted" / "Mighty and Majestic" — honorific epithets for God |

## Practical handling

- **These formulas are near-boilerplate — verify the specific spelling against how the source document itself renders it**, since some older or regionally-set texts use slightly different orthographic conventions (e.g. hyphenation of "ал-"/"-л-", spacing around abbreviated parenthetical forms). Match the source's own convention rather than "correcting" it to a different but also-valid rendering — this is a style-sheet case per [SKILL.md](SKILL.md)'s editing-mode principle.
- **Abbreviated forms in running text** — a source may write the full formula once and then abbreviate with just "(с)" or "(а)" on subsequent occurrences of the same name. Preserve this pattern rather than expanding every abbreviation or abbreviating every full form; follow what the specific source does.
- **These are Arabic phrases transliterated into Tajik Cyrillic, not Arabic-script text** — they don't trigger [mixed-script.md](mixed-script.md)'s Arabic-script/RTL handling. They stay in the normal body-text formatting (Palatino Linotype 12pt Justified per [restoration.md](restoration.md)'s contract) like the rest of the Tajik prose around them.

## Building this out further

This list covers the formulas that actually recurred in the one real historical chronicle restored so far (Gardizi's *Zayn al-Akhbar*). Like [register.md](register.md), the right way to grow this is by logging additional formulas actually encountered in future real texts — not by pre-populating a longer list of formulas that haven't been verified against a real source yet.
