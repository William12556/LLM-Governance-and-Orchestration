# AEL Context Budget Report

Generated: 2026-04-28 12:34:09
Model: Devstral-Small-2-24B-Instruct-2512
Context window: 393,216 tokens

## Initial task load
Estimated tokens at task start: 462 tokens (0.1% of window)
Headroom available: 392,754 tokens

## Budget thresholds
Warn at:  314,572 tokens (80%)
Abort at: 373,555 tokens (95%)

## Iteration estimates
Estimated accumulation per iteration: ~300 tokens
Iterations before warn threshold:  ~1047
Iterations before abort threshold: ~1243

## Guidance for Strategic Domain
When authoring the next tactical_brief or T04 prompt:

- Current initial load is 0.1% of context window
- Each Ralph Loop phase iteration accumulates ~300 tokens
- Recommended tactical_brief size: ≤1,000 tokens
- Avoid embedding large design documents or code blocks in the brief
- Context pressure symptoms: duplicate tool calls, repeated reads, verbose responses
- If symptoms appear, reduce brief size and restart with --mode reset
