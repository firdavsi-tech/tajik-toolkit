#!/usr/bin/env python3
"""
Regression test for verify_docx.py and check_consistency.py themselves.

Until now these were only smoke-tested by hand against the user's real,
private restoration files — which don't ship with this public repo, so a
future edit to either script had no way to be checked for regressions.
This builds two small synthetic fixtures (scripts/tests/build_fixtures.py,
no Node/docx-js needed) and asserts the scripts behave as documented:

  - clean.docx must PASS verify_docx.py with all --expect-* flags, and
    report no name-spelling candidates from check_consistency.py.
  - broken.docx must FAIL verify_docx.py and report each specific known
    problem (forbidden string, literal \\n, missing heading/RTL/footnotes),
    and check_consistency.py must report the two known name inconsistencies
    seeded into it (Гафур/Ғафур letter-confusion, Аббос/Аббоса near-dup).

Run: python scripts/tests/run_tests.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_fixtures import build  # noqa: E402

SCRIPTS_DIR = Path(__file__).parent.parent


def run(args):
    result = subprocess.run(
        [sys.executable, *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return result.returncode, result.stdout + result.stderr


def check(condition, label, failures):
    status = "ok" if condition else "FAIL"
    print(f"  [{status}] {label}")
    if not condition:
        failures.append(label)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        clean_path, broken_path = build(tmp)

        print("verify_docx.py against clean.docx (expect PASS):")
        code, out = run([str(SCRIPTS_DIR / "verify_docx.py"), clean_path,
                          "--expect-headings", "--expect-footnotes", "--expect-rtl"])
        check(code == 0, "exit code 0", failures)
        check("PASS" in out, "reports PASS", failures)

        print("\nverify_docx.py against broken.docx (expect FAIL with all 6 problems):")
        code, out = run([str(SCRIPTS_DIR / "verify_docx.py"), broken_path,
                          "--expect-headings", "--expect-footnotes", "--expect-rtl"])
        check(code == 1, "exit code 1", failures)
        check("файл:" in out, "catches forbidden string 'файл:'", failures)
        check("Саҳифаи" in out, "catches forbidden string 'Саҳифаи'", failures)
        check("literal newline" in out, "catches literal \\n inside a text run", failures)
        check("Palatino Linotype" in out and "No 'Palatino Linotype'" in out, "catches missing Palatino Linotype", failures)
        check("no real Heading style found" in out, "catches missing heading style", failures)
        check("RTL markers incomplete" in out, "catches missing RTL markers", failures)
        check("footnotes.xml is missing" in out, "catches missing footnotes.xml", failures)

        print("\ncheck_consistency.py against clean.docx (expect no candidates):")
        code, out = run([str(SCRIPTS_DIR / "check_consistency.py"), clean_path])
        check(code == 0, "exit code 0", failures)
        check("No candidate spelling inconsistencies found" in out, "reports no candidates", failures)

        print("\ncheck_consistency.py against broken.docx (expect known pairs):")
        code, out = run([str(SCRIPTS_DIR / "check_consistency.py"), broken_path])
        check("Гафур" in out and "Ғафур" in out, "catches Гафур/Ғафур letter-confusion", failures)
        check("Аббос" in out and "Аббоса" in out, "catches Аббос/Аббоса near-duplicate", failures)

    print()
    if failures:
        print(f"FAIL: {len(failures)} check(s) failed: {failures}")
        sys.exit(1)
    print("PASS: all regression checks passed.")


if __name__ == "__main__":
    main()
