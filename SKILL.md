---
name: data-research
description: >
  Use when building or running a data research or enrichment agent (any pipeline
  that fetches external data, calls APIs, and produces structured output rows).
  Covers web scraping, company enrichment, lead research, dataset augmentation,
  and any batch process where an LLM fetches, transforms, and outputs structured data.
effort-level: medium
user-invocable: true
---

# Data Research Skill

Operational guardrails for AI-driven data research pipelines. Every rule below
was learned from a real production failure.

- Full failure-mode catalog: [references/failure-modes.md](references/failure-modes.md)
- Example prompt + validation script: [references/example-schema-validation.md](references/example-schema-validation.md)
- Runnable validator: [scripts/validate_output.py](scripts/validate_output.py)

## Fetch rules

- **Cache all responses** keyed on full URL. Never fetch the same URL twice per session.
- **Default to HTTP fetch.** Only use a headless browser when JS rendering is required. Try HTTP first if unsure.
- **Exponential backoff on failure:** 1s, 2s, 4s. Max 3 retries per URL.
- **On HTTP 429 (rate limit):** stop retrying that endpoint and report. Never retry in a tight loop.
- **Enforce a call budget.** Track total external calls. Warn at 80%, stop at limit. Surface partial results rather than continuing blindly.

## Output rules

- Every response must conform **exactly** to the provided output schema. No extra keys, no renamed keys, no missing required fields.
- Treat the schema as `additionalProperties: false`. Key name drift (`company_name` vs `companyName`) is a failure.
- Uncertain values: use `null`. Never invent data, guess, or restructure the schema.
- Validate output against the schema **before** marking a row complete: required fields present, types correct, constraints satisfied.

## Error handling

- **Never discard a failed response.** Log the full raw output alongside the error. It's diagnostic data you paid for.
- On schema validation failure, report: raw output, which rule failed, which field(s).
- **Errors are signal, not trash.** After a run, review error rows for patterns. Repeated schema failures mean the prompt needs tightening. Repeated fetch failures mean the target or method needs changing. Do not accept an error rate; diagnose it. Every errored row is a feedback loop you either use or pay for again next run.

## Persistence rules

- **Write each row as it completes.** File, database, queue... anything durable. Do not accumulate results in memory and write once at the end.
- **Assume the process will crash.** OOM, rate limit escalation, unhandled exception, timeout: something will go wrong. When it does, every row completed before that point must already be saved.
- **Never hold an entire multi-step pipeline in memory.** If each row passes through ten processing stages, persist intermediate state. A failure at stage 9 of row 4,999 should not destroy rows 1-4,998.
- The model will default to "gather all, write all" because it looks clean. It is not clean. It is a bet that nothing goes wrong across thousands of calls, and that bet always loses.

## Completion criteria

A row is done when:

1. Response passed schema validation
2. All required fields present and correctly typed
3. Raw response (success or failure) logged
4. Result written to output store

An errored row is still done, but it must carry its diagnostic payload. `"Error"` alone is never acceptable.

## Pre-flight checklist

Before starting any data research run, confirm:

- [ ] Output schema defined with `additionalProperties: false`
- [ ] URL cache in place
- [ ] Retry logic: exponential backoff, max 3 attempts
- [ ] 429 handling stops retries (not accelerates them)
- [ ] Default fetch method is HTTP, not browser
- [ ] Call budget set and tracked
- [ ] Each row written to durable storage on completion (not batched in memory)
- [ ] Multi-step pipelines persist intermediate state between stages
- [ ] Error logging captures raw responses
- [ ] Schema validation runs before row completion
- [ ] Post-run error review planned (not just "re-run and hope")
