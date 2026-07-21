# Tajik Toolkit — OCR Engine Comparison

See [SKILL.md](SKILL.md) for the decision tree this feeds into. Findings from studying seven existing OCR skills.

---

## Vision-LLM-based (prompt-guided — the recommended category for Tajik)

| Option | Notes |
|---|---|
| This model's own vision | No setup, no API key, no image leaves the conversation. Best default for single images / moderate volume. Prompt explicitly: state the text is Tajik, name the six extra Cyrillic letters, ask for verbatim transcription. |
| PaddleOCR-VL (via SiliconFlow or similar) | A real model, promptable. Read credentials from an environment variable only — never as a CLI argument (shell history/process listings aren't safe for a credential). Sends the full image to a third-party cloud endpoint — say so before using it. |
| DeepSeek-OCR (via SiliconFlow or similar) | Same category, same caveats — promptable vision model, cloud-dependent, needs explicit credential handling. |

**Why this category first:** these aren't limited to a fixed set of trained languages the way classical engines are. A custom prompt naming the six Tajik-specific letters and noting the mixed-script possibility (see [mixed-script.md](mixed-script.md)) gives the model information a classical engine's architecture has no way to use at all.

## Classical trained OCR (fallback — offline/no-cloud-budget only)

| Option | Tajik support | Notes |
|---|---|---|
| Tesseract (`image-to-text` skill, local) | None — verified against `tessdata_fast` and `tessdata_contrib`, no `tgk.traineddata` exists | Use `rus` as the closest approximation; expect systematic misreads of the six Tajik-only letters; always follow with the correction pass in [orthography.md](orthography.md). |
| RapidOCR (local) | Unconfirmed — not verified here; treat as the same situation as Tesseract unless independently checked | Same fallback-and-correct pattern applies until Tajik support is actually confirmed. |
| PaddleOCR classical / PP-OCRv5 (official cloud API) | Unconfirmed for Tajik specifically | Requires a paid access token and sends images to a cloud API — a real cost and privacy tradeoff for something whose Tajik coverage isn't independently verified either. |

**Why this category is the fallback, not the default:** even where installable and free (Tesseract, RapidOCR), the underlying issue — no trained Tajik model — doesn't go away. It's a legitimate choice for offline/bulk work where the vision-LLM approach isn't practical, but go in expecting to need the correction pass, not expecting clean output.

## PDF handling

Convert each PDF page to an image first (PyMuPDF is a reliable, verified-working choice), then run whichever engine from above per page, then reassemble in page order. A multi-engine auto-switch pattern (try local first, escalate to cloud if the result looks too short/weak) is reasonable — decide the switch explicitly and tell the user, don't silently swap engines without saying so.

## Security notes carried over from source-skill review

- Never accept an API key as a command-line argument — shell history and process listings are not a safe place for a credential. Environment variable only.
- Never let a script `pip install` packages on its own initiative without confirmation — ask first, install explicitly.
- Sending images to a cloud OCR API means that data leaves the machine — say so before doing it, the same way any other upload gets flagged.
