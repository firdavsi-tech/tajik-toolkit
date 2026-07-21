# Tajik Toolkit — OCR Pipeline, Scripts, and Output Contract

See [SKILL.md](SKILL.md) for the decision tree this feeds into.

---

## The core problem, verified

No OCR engine ships a trained Tajik language model. Checked directly against Tesseract's official `tessdata_fast` and `tessdata_contrib` repositories (via GitHub's API, not a guess): Russian (`rus`) and Persian (`fas`) exist, Tajik (`tgk`) does not, in either. Any OCR pipeline built on Tesseract has to approximate Tajik with the `rus` model, and that approximation has a specific, predictable failure mode: the six Tajik-only letters (see [orthography.md](orthography.md)) don't exist in the `rus` model's training data, so it will systematically misread them as their nearest Russian look-alike (ғ→г, қ→к, ҳ→х, ҷ→ч or ж, ӣ→и, ӯ→у).

**Before running an OCR pipeline on Tajik text, consider the alternative:** for a single image or a small amount of text, this model's own vision capability has real exposure to Tajik as a language, unlike a Russian-trained OCR model that has never seen these letters. Reserve the pipeline below for bulk/batch processing where reading each image directly isn't practical.

## Working scripts (tested, not just described)

`scripts/find_scanned_files.py` and `scripts/ocr_batch.py` implement the fully-automatic local path. Both were built and verified against real test images/PDFs — including two bugs the testing caught that pure code review wouldn't have: Python's subprocess resolving `bash` to the Windows WSL launcher stub instead of Git Bash (fixed by pointing at `C:\Program Files\Git\bin\bash.exe` explicitly), and Windows subprocess text-mode corrupting Cyrillic output by decoding with the system codepage instead of UTF-8 (fixed with explicit `encoding="utf-8"`).

**Discovery** (read-only, fast — lists candidates without opening/OCRing anything):

```bash
python scripts/find_scanned_files.py --output manifest.json
# or scope it: --root "D:\Documents" --root "E:\Scans"
```

Skips noisy/irrelevant system directories by default (Windows, Program Files, ProgramData, AppData, node_modules, .git, venvs, recycle bin). Override with `--no-exclude` if a genuine need to look there arises. Scope this to a specific folder the user names by default — don't sweep a whole drive unless that's actually what's needed (a whole-drive scan once produced 481K candidate files, most of them irrelevant).

**OCR** (the slow step — actually runs Tesseract per file/page):

```bash
python scripts/ocr_batch.py --manifest manifest.json --output-dir ./ocr_out --limit 20   # test on a sample first
python scripts/ocr_batch.py --manifest manifest.json --output-dir ./ocr_out              # full run
```

Run with `--limit` on a small sample first, especially after a broad discovery scan — a manifest of thousands of files means thousands of Tesseract invocations, which is genuinely slow. Check the sample's flagged-word rate and a few `.txt` outputs before committing to the full run.

**Correction logic in `ocr_batch.py`**, in plain terms: for every occurrence of г, к, х, ч, ж in the raw output, consider whether context suggests it should have been ғ, қ, ҳ, ҷ instead. This needs real lexical/contextual judgment, not a blind find-replace. и/у (substitutes for ӣ/ӯ) are deliberately **not** pattern-matched — see the empirical findings below for why.

## Empirically verified failure mode (not just predicted)

Tested directly: rendering "Ғафур хеҷ вақт ӯро надид" and running it through the `rus`-approximation pipeline produced "Гафур хеч вакт уро надид" — every pattern-detectable substitution occurred exactly as predicted. One substituted word ("Гафур") also showed a real confidence dip (39.7% vs 90%+ for unaffected words) — but the other two substituted words stayed at 90%+ confidence, so **confidence alone is a corroborating signal, not a reliable detector**.

**Known gap, stated plainly:** и and у (the substitutes for Ӣ and Ӯ) are deliberately excluded from pattern-matching because they're among the most common vowels in both languages; flagging every word containing them produces almost no signal. This means Ӣ/Ӯ substitutions are the weakest-covered case in the automated pass — worth a heavier manual/vision-based spot-check specifically for those two letters.

## Second empirical test: a real scanned book, not a synthetic sentence

Tested against a real 1996 Tajik book (49-page scan, mixed printed Cyrillic body text and Arabic-script Quranic examples — a tajwid/recitation manual). This surfaced two things the single-sentence synthetic test hadn't:

**Pattern-based flagging is not useful on dense body text.** г/к/х/ч/ж are just common Tajik consonants — on a real paragraph, roughly 80% of words contain at least one and get flagged, which stops being a "review candidate" list and becomes "most of the page." The script now only applies pattern-matching when a page is sparse (≤15 words — titles, headers, short captions); on dense text it relies on the confidence signal alone.

**Tajik text mixed with Arabic-script content is real, not hypothetical, and Tesseract cannot help with it at all.** A two-column page (Tajik question | Arabic-script Quranic example) produced readable Tajik on the left and pure garbage on the right — not a letter-substitution problem, a completely different script family the `rus` model has zero training on. The script flags obvious garbage tokens as `non_cyrillic_regions`, but this detection is necessarily imperfect (some Arabic-script noise still contains a stray Cyrillic-range character and slips past the classifier) — see [mixed-script.md](mixed-script.md) for the real fix (isolate the region, read it directly).

## Output contract

Regardless of which engine is used, structure the result the same way:

```json
{
  "ok": true,
  "text": "full extracted text, verbatim",
  "regions": [
    { "text": "line or region text", "confidence": 0.0, "flagged": false }
  ],
  "engine": "vision-direct | vision-api:<name> | classical:<name>",
  "corrections_applied": ["list of orthography corrections made, if any"]
}
```

- `ok: false` with an `error` field on failure — never blend an error message into `text` where it could be mistaken for actual document content.
- **Always show the complete `text` to the user**, no truncation beyond what's genuinely unmanageable.
- `regions[].flagged` marks anything below a confidence threshold, or any letter-substitution correction applied with less than full confidence — surface these separately rather than mixing silent corrections with uncertain ones.

## Batch / multi-image processing

Process images independently and collect results keyed by filename, continuing past individual failures rather than aborting the whole batch. Report a summary (N processed, M flagged for review, K failed) rather than only the raw per-file dump.

## Scanned PDF pipeline

1. Convert each page to an image (PyMuPDF is a verified-working reference).
2. Run the chosen engine (from [ocr-engines.md](ocr-engines.md)) per page.
3. Reassemble in page order, preserving a page boundary marker in intermediate working notes (never in the final delivered document — see [delivery.md](delivery.md)).
4. If mixed Tajik/Russian/English/Arabic content is expected, apply [mixed-script.md](mixed-script.md)'s segmentation per page, not just once at the end — script mixing often varies page to page.

## When to escalate from classical to vision-based mid-task

If using a classical engine as the offline fallback and the output looks implausible — unusually short relative to the image's apparent text density, or containing runs of characters that don't form recognizable Tajik/Russian words — that's the concrete signal to stop and either switch to a vision-LLM approach or flag the page for manual review, rather than passing along a low-quality transcription as if it were reliable.
