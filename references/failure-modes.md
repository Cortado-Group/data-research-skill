# Failure Modes Reference

Detailed catalog of silent, expensive failures that AI data research agents
make in production. Each entry describes what you see vs what's actually
happening, and the rule that prevents it.

## Rate limit cascade

**What you see:** The pipeline eventually finishes.
**What's actually happening:** 200+ failed API calls hammering a rate-limited
endpoint with zero backoff. Every retry is immediate. Every failure is silent.
You find out when you get the bill.

**Fix:** Exponential backoff (1s, 2s, 4s), max 3 retries. On 429, stop entirely.

## Browser for text fetch

**What you see:** Results come back.
**What's actually happening:** A full Chromium browser is launched for every
request — to fetch plain text. The CPU overhead is orders of magnitude higher
than a simple HTTP call. The fix is five lines.

**Fix:** Default to HTTP fetch. Only use a headless browser when JS rendering
is actually required.

## Redundant URL fetches

**What you see:** Thorough research.
**What's actually happening:** No cache. Same URL, same response, fetched 3-4
times per entity. You paid for that content once but were billed four times.

**Fix:** Cache all responses keyed on full URL. Check cache before every fetch.

## Discarded error responses

**What you see:** The pipeline flagged some failures.
**What's actually happening:** The raw error response — the diagnostic artifact
you paid for — was quietly thrown away. The log says "error" but not *why*.

**Fix:** Always log the full raw response alongside the error status.

## Timeout kills completed work

**What you see:** Some rows didn't complete.
**What's actually happening:** Long-running research tasks finished their work
and then got cut off before the output was written. Completed work, zero output.
Full token cost, nothing to show.

**Fix:** Write rows incrementally as they complete, not in a batch at the end.

## Invalid JSON accepted

**What you see:** The pipeline ran.
**What's actually happening:** The model returned something shaped like JSON.
It wasn't valid. The pipeline accepted it, failed three steps later, and
re-ran the whole thing. Full token cost, twice.

**Fix:** Validate every response against the schema before marking it complete.

## Key name drift

**What you see:** Mostly consistent output.
**What's actually happening:** You asked for `company_name`. You got
`companyName`. Then `name`. Then `company`. Same prompt, different calls.
Valid data, silently discarded because the key didn't match.

**Fix:** `additionalProperties: false` in the output schema. The model either
matches the contract or the row fails loudly.

### Example strict schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["company_name", "website", "employee_count", "summary"],
  "additionalProperties": false,
  "properties": {
    "company_name":   { "type": "string" },
    "website":        { "type": "string", "format": "uri" },
    "employee_count": { "type": "integer", "minimum": 0 },
    "summary":        { "type": "string", "minLength": 20 }
  }
}
```

## Error results treated as trash

**What you see:** 15% error rate. You re-run. 12% error rate. You re-run again.
Eventually you get enough rows and move on.
**What's actually happening:** The errors are telling you exactly what's wrong —
the prompt is ambiguous, the schema doesn't handle a common edge case, or a
specific source is consistently returning a format the parser doesn't expect.
Nobody looks. The error rows get thrown away and re-run blindly, paying full
cost each time for the same failures.

The model will never stop to say "these errors have a pattern." It will
re-run the same broken prompt against the same broken source and produce the
same broken output, indefinitely. It treats every row as independent. You
shouldn't.

**Fix:** After every run, aggregate errors by type. Ask:
- Are the same fields failing repeatedly? → Tighten the prompt or loosen the schema constraint.
- Is a specific source returning unexpected formats? → Add source-specific parsing or skip it.
- Are timeouts clustered on certain entities? → Those entities need a different fetch strategy.
- Is the model inventing data for a specific field? → That field needs a stronger constraint or a `null` allowance.

The error rows are the cheapest research you'll ever do — you already paid for
them. Throwing them away and re-running is paying twice to learn nothing.

## No-code enrichment tools (Clay, etc.)

All the above failures also occur in no-code enrichment tools — but with no
recourse. You cannot adjust timeouts, clean malformed responses, retry with a
corrected prompt, or capture what the model actually returned.

The tool sees a bad response and writes one word: **Error.** Credit spent.
Row done. No stack trace, no raw response, nothing to build a handler from.

In code, failure is recoverable. In no-code enrichment tools, failure is
just cost. This is why owning the pipeline matters.

## Quick reference table

| Failure | Silent cost | Rule |
|---|---|---|
| Rate limit cascade | 200+ failed calls, full bill | Backoff + 429 stop |
| Browser for text fetch | 100x CPU overhead per call | Lightest tool first |
| Redundant URL fetches | 3-4x token/API cost | URL cache |
| Discarded error responses | Lost diagnostics, blind re-runs | Log raw responses |
| Timeout kills completed work | Full cost, zero output | Incremental persist |
| Invalid JSON accepted | Full pipeline re-run | Schema validation |
| Key name drift | Valid data silently dropped | Strict schema |
| Errors treated as trash | Repeated re-runs, same failures | Post-run error review |
