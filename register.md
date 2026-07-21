# Tajik Toolkit — Register and Loanword Choices

See [SKILL.md](SKILL.md) for when to load this.

---

## Why this file is short on purpose

A deep, prescriptive catalog of stop-words and calques with prescribed replacements (the way some Russian-language editing tools do it) would need a named author's editorial expertise and cited sources to carry that authority. Producing an equivalent large catalog for Tajik here — with the same implied authority — would risk asserting specific "wrong → correct" pairs this model isn't confident enough in to state as fact for a lower-resource language. That's a worse outcome than a shorter, honestly-scoped list. If the user has (or can point to) an actual Tajik style guide or corpus, that should override anything in this file.

## The general pattern worth flagging

Tajik administrative, technical, and journalistic writing inherited a layer of vocabulary and phrasing from the Soviet era via Russian — direct loanwords, calqued official phrasing, and Russian-influenced sentence patterns. Post-independence usage has moved parts of this back toward native Tajik or (post-)Persian-origin vocabulary, but not uniformly, and not in every register — some Russian-origin terms remain the standard, unmarked choice, especially for modern technical/institutional concepts that never had an established Tajik equivalent before the Soviet period.

**The judgment call, every time:** is a given Russian-origin term or calqued phrase (a) the standard, expected choice in this register, (b) a marked "Sovietism" a modern editor would likely flag, or (c) genuinely ambiguous. Don't default to "native is always better" any more than "keep it as-is is always safer" — both are wrong defaults. State which of the three you think applies and why, and let the user's judgment (or a cited style guide) settle it when it's genuinely close.

## What to actually do when reviewing

1. Note where a Russian-origin term or obviously Russian-calqued sentence structure appears.
2. Ask: does this register — a legal document, a news article, personal correspondence, marketing copy — have an established convention here? Official/legal Tajik retains more Russian-origin institutional vocabulary than literary or journalistic Tajik typically does.
3. If genuinely unsure, present it as a query with reasoning rather than silently substituting a "more native" alternative you're not confident is actually better in context.
4. Log the decision to the document's style sheet once made, so the same term doesn't get relitigated inconsistently later.

## Building this out further

If this file sees real use, the right way to strengthen it is to log actual judgment calls made in real documents (with the reasoning that resolved them) rather than pre-populating a speculative list now. That keeps the catalog grounded in cases actually verified against real text and real user feedback, instead of invented examples.
