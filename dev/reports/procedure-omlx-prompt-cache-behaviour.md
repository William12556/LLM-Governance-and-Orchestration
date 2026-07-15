Created: 2026 July 15

# oMLX Prompt-Cache Behaviour — Test Procedure

---

## Table of Contents

[1.0 Objective](<#1.0 objective>)
[2.0 Hypotheses](<#2.0 hypotheses>)
[3.0 Variables and Controls](<#3.0 variables and controls>)
[4.0 Test Conditions](<#4.0 test conditions>)
[5.0 Procedure](<#5.0 procedure>)
[6.0 Measurement](<#6.0 measurement>)
[7.0 Interpretation and Decision Matrix](<#7.0 interpretation and decision matrix>)
[8.0 Confounds and Precautions](<#8.0 confounds and precautions>)
[Version History](<#version history>)

---

## 1.0 Objective

Determine whether the oMLX inference server reuses prefix (KV) cache computation across separate `/v1/chat/completions` requests, and quantify the latency effect of prefix stability.

The result gates a proposed `orchestrator.py` change. The F25 iteration-countdown injection mutates `messages[0]` every iteration (`messages[0]["content"] = system_prompt + status`), which changes the prompt prefix on each call. If oMLX performs cross-request prefix caching, this mutation forfeits reuse and inflates prefill cost per iteration. If oMLX does not cache across requests, the mutation is cost-neutral and the change carries no benefit.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Hypotheses

- **H1:** oMLX reuses prefix KV-cache across sequential requests. A request sharing a long identical prefix with an immediately prior request exhibits materially lower prompt-eval time / time-to-first-token (TTFT) than a request whose prefix diverges early.
- **H0 (null):** No cross-request prefix reuse. Prompt-eval time is independent of prefix stability; identical-prefix and mutated-prefix requests produce equivalent prefill timing.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Variables and Controls

- **Independent variable:** prefix stability — one of {stable, mutated, cold}.
- **Dependent variables:** prompt-eval time (preferred) or client-side TTFT; total request latency (secondary).
- **Controlled constants:**
  - Single model, queried by explicit model ID (do not rely on oMLX `is_default`).
  - `max_tokens = 1`, `temperature = 0`, `stream = true`, identical decoding parameters across all requests.
  - Warm model (exclude first-load latency; discard warm-up requests).
  - No model reload between requests within a set.
  - Single-threaded issuance; machine otherwise quiescent.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Test Conditions

Let `P` be a fixed, large prefix (target ~2,000–4,000 tokens) authored as a single system message. Size must exceed any plausible minimum-cache threshold.

- **Condition S (stable prefix — models the proposed fix):** system content = `P` (unchanged); a short trailing user message varies per request (`A`, `B`). The shared prefix spans the entire system message.
- **Condition M (mutated prefix — models current F25):** system content = `P + "<status:N>"` where `N` varies per request; trailing user message varies (`A`, `B`). Divergence occurs inside the system message, shortening the shared prefix.
- **Condition C (cold — uncached baseline):** each request uses a unique large prefix (`P1`, `P2`) sharing no common head. Establishes full uncached prefill cost.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Procedure

1. Confirm oMLX is running and the target model is loaded and warm; verify via `GET /v1/models`.
2. Construct prefix `P` (stable system text padded to the target token size). Record its token count.
3. **Condition S:** issue request 1 (`P` + trailing `A`), then immediately issue request 2 (`P` + trailing `B`). Record timing for request 2.
4. **Condition M:** issue request 1 (`P + status:1` + `A`), then request 2 (`P + status:2` + `B`). Record timing for request 2.
5. **Condition C:** issue request 1 (`P1`), then request 2 (`P2`). Record timing for request 2.
6. Repeat steps 3–5 `K` times (K ≥ 10). Discard the first repetition of each condition (warm-up).
7. Aggregate per condition: median and interquartile range of the dependent variable.

A minimal client (direct `AsyncOpenAI` against `base_url`, `stream=True`, `time.monotonic()` around first-chunk arrival) is sufficient. `curl` with `--no-buffer` against `/v1/chat/completions` is an acceptable alternative for TTFT. The `omlx` MCP tools are not recommended here — their timing granularity is too coarse to isolate prefill.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Measurement

Priority order for the dependent variable:

1. **Server-reported prompt-eval timing.** If oMLX logs or returns per-request prompt token count and prompt-eval duration (or prompt tokens/sec), use it — this isolates prefill from generation directly.
2. **Client-side TTFT.** With `stream=true` and `max_tokens=1`, measure wall-clock time from request send to first streamed content chunk. TTFT is dominated by prefill when output is a single token.

Record per request: condition, repetition index, prompt token count, prompt-eval time (if available), TTFT (ms).

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Interpretation and Decision Matrix

Compare medians across conditions:

- **Cross-request caching confirmed (reject H0):** S request-2 prefill is materially below C. Reuse exists.
- **Mutation forfeits reuse (supports the fix):** S benefits but M ≈ C. Early divergence defeats the cache — the F25 pattern pays full prefill each iteration.
- **No cross-request caching (accept H0):** S ≈ M ≈ C. Prefix stability is irrelevant at the server layer.

Decisions:

- **S << C and M ≈ C** → implement the F25 prefix fix (relocate the volatile status to a trailing message; keep the system prefix static). Route as a source change through the T03 → T02 → T04 triple. Expected saving ≈ per-iteration prefill delta × iterations per phase.
- **S ≈ M ≈ C** → no orchestrator prefix change. Redirect effort to speculative decoding and reviewer-model downsizing, which do not depend on prefix reuse.
- **S << C but M also << C** → mutation does not sit early enough to matter; re-examine where divergence actually falls in the tokenised prefix before drawing a conclusion.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Confounds and Precautions

- **Cache scope.** oMLX may cache only within a process or session. Keep a single server process alive across all requests; do not restart or reload the model mid-run.
- **Minimum-prefix threshold.** Some implementations skip caching below a token floor. The large `P` mitigates this; if results are null, retry with a larger `P` before accepting H0.
- **Eviction under load.** Concurrent requests may evict cache entries. Issue strictly single-threaded.
- **Tokenisation of divergence point.** Confirm the Condition M status marker actually changes tokens early in the sequence; a marker that tokenises identically to padding would understate the effect.
- **Generation contamination.** Hold `max_tokens = 1` so generation time does not mask prefill differences.
- **Warm-up.** The first request after model load includes weight-warm and allocation costs unrelated to prefix caching; always discard it.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-07-15 | Initial procedure |

---

Copyright (c) 2026 William Watson. MIT License.
