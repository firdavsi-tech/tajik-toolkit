#!/usr/bin/env python3
"""
Scan a generated .docx for the same proper name spelled two different ways
across the whole document — a gap SKILL.md's "style sheet" concept names
but had no tool to actually check. Two detection passes:

  1. Letter-confusion grouping: normalizes the six Tajik-only letters
     (Ғ/Г, Қ/К, Ҳ/Х, Ҷ/Ч/Ж, Ӣ/И, Ӯ/У) to a shared signature. If a signature
     maps to more than one distinct surface spelling actually present in
     the document, both are almost certainly the same name written
     inconsistently (e.g. "Гафур" and "Ғафур").
  2. Near-duplicate check: capitalized words of similar length with a small
     edit distance (transliteration variants like "Абусаид" / "Абу Саид"
     won't share a length, so this is a narrower net than pass 1).

This is a candidate list for review, not a verdict — a real distinct name
can legitimately share a signature with another (rare, but possible), and
short/common capitalized words (sentence-initial words, single-use names)
produce noise. Cross-check flagged pairs against the source per
restoration.md's method before "fixing" anything.
"""
import argparse
import re
import sys
import zipfile
from collections import defaultdict

CONFUSION_MAP = str.maketrans({
    "ғ": "г", "Ғ": "Г",
    "қ": "к", "Қ": "К",
    "ҳ": "х", "Ҳ": "Х",
    "ҷ": "ч", "Ҷ": "Ч",
    "ӣ": "и", "Ӣ": "И",
    "ӯ": "у", "Ӯ": "У",
})

# Words too short or too common to be useful proper-noun candidates.
MIN_WORD_LEN = 4
STOPWORDS_START = {"Ин", "Он", "Ва", "Аз", "Бо", "То", "Дар", "Ба", "Ки", "Чи", "Он"}


def read_zip_entry(docx_path, entry_name):
    try:
        with zipfile.ZipFile(docx_path) as z:
            return z.read(entry_name).decode("utf-8")
    except KeyError:
        return None


def extract_body_text(docx_path):
    doc_xml = read_zip_entry(docx_path, "word/document.xml")
    if doc_xml is None:
        return None
    runs = re.findall(r"<w:t[^>]*>(.*?)</w:t>", doc_xml, re.DOTALL)
    return " ".join(runs)


def capitalized_words(text):
    # Cyrillic + Tajik-specific letters, capitalized first letter.
    pattern = r"[А-ЯЁӢӮҒҚҲҶ][а-яёӣӯғқҳҷ]{%d,}" % (MIN_WORD_LEN - 1)
    return [w for w in re.findall(pattern, text) if w not in STOPWORDS_START]


def edit_distance_at_most(a, b, limit=2):
    if abs(len(a) - len(b)) > limit:
        return False
    # Simple DP Levenshtein, early-exit not needed at this scale.
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[-1] <= limit


def main():
    # Windows console codepages (cp1252/cp1256/etc.) can't encode Cyrillic —
    # force UTF-8 stdout so this doesn't crash mid-report on real Tajik names.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("docx_path")
    parser.add_argument("--min-count", type=int, default=1,
                         help="Only report a spelling if it occurs at least this many times (default 1)")
    args = parser.parse_args()

    text = extract_body_text(args.docx_path)
    if text is None:
        print("FAIL: could not read word/document.xml — is this a valid .docx?", file=sys.stderr)
        sys.exit(1)

    words = capitalized_words(text)
    counts = defaultdict(int)
    for w in words:
        counts[w] += 1

    surface_forms = [w for w, c in counts.items() if c >= args.min_count]

    # Pass 1: letter-confusion signature grouping.
    by_signature = defaultdict(set)
    for w in surface_forms:
        by_signature[w.translate(CONFUSION_MAP)].add(w)

    signature_conflicts = {sig: forms for sig, forms in by_signature.items() if len(forms) > 1}

    # Pass 2: near-duplicate edit distance among remaining distinct words.
    distinct = sorted(set(surface_forms))
    edit_conflicts = []
    seen_pairs = set()
    for i, a in enumerate(distinct):
        for b in distinct[i + 1:]:
            if a.translate(CONFUSION_MAP) == b.translate(CONFUSION_MAP):
                continue  # already reported in pass 1
            if edit_distance_at_most(a, b, limit=1):
                pair = tuple(sorted((a, b)))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    edit_conflicts.append(pair)

    print(f"Capitalized word occurrences scanned: {len(words)} | distinct forms: {len(distinct)}")
    print()

    if not signature_conflicts and not edit_conflicts:
        print("No candidate spelling inconsistencies found. This does not guarantee correctness — "
              "a name used only once, or spelled wrong the same way throughout, won't be caught here.")
        return

    if signature_conflicts:
        print(f"Letter-confusion candidates ({len(signature_conflicts)}) — likely the same name, "
              "one or more instances using the wrong Tajik-specific letter:")
        for sig, forms in sorted(signature_conflicts.items()):
            details = ", ".join(f"{w} ({counts[w]}x)" for w in sorted(forms))
            print(f"  - {details}")
        print()

    if edit_conflicts:
        print(f"Near-duplicate candidates ({len(edit_conflicts)}) — similar spellings, edit distance <= 1 "
              "(review against the source; could be two different names, not one misspelled):")
        for a, b in edit_conflicts:
            print(f"  - {a} ({counts[a]}x) / {b} ({counts[b]}x)")

    print()
    print("This is a candidate list, not a verdict — cross-check each pair against the source "
          "per restoration.md's method before treating either spelling as the error.")


if __name__ == "__main__":
    main()
