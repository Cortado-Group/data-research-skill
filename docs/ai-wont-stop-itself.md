---
title: "AI Won't Stop Itself From Being Stupid: That's YOUR Job"
published: true
description: >
  LLMs are completion engines, not judgment engines. Here's what that costs
  in production, and the reusable skill that stops you from paying tuition twice.
tags: ai, llm, productivity, devops
cover_image:
---

Everyone says you don't need developers anymore.

Coding is dying. AI writes better code than humans. Anyone can ship software
now. Just describe what you want and let the model handle it.

The AI companies love this narrative. They should. It's great for token sales.

Because here's what "just let AI handle it" actually looks like in production.
None of these are edge cases. All of them are expensive. And every single one
is **invisible to someone who handed the problem to AI and walked away.**

---

## The failures. What you see. What's actually happening.

### Rate limit cascade

**What you see:** The pipeline is quietly working away.  
**What's actually happening:** 200+ failed API calls hammering a rate-limited
endpoint with zero backoff. Every retry is immediate. Every failure is silent.
You walk away thinking progress is being made. You come back to nothing.
You're starting over.

---

### Playwright spinning up for a text fetch

**What you see:** Results come back.  
**What's actually happening:** A full Chromium browser is being launched for
every single request... to fetch plain text. The CPU overhead is absurd. The
fix is five lines. The model never suggested it.

---

### Re-fetching the same URLs four times per company

**What you see:** Thorough research.  
**What's actually happening:** No cache. The model has no memory within a run
that it already retrieved something. Each subtask goes back to the same URL
independently, as if it's the first time. Same request, same response, four
times, burning time and compute on work that was already done.

---

### Throwing away error results

**What you see:** Some rows failed. Moving on.  
**What's actually happening:** The model returned something malformed, the
pipeline labeled it garbage and discarded it, without logging what the
response actually said. No record. No pattern. No handler.

Bad outputs are data. They tell you exactly where your prompt breaks, where
your schema has gaps, where your downstream handling makes bad assumptions.
Throw them away and you're not just losing a row. You're guaranteeing you'll
lose the same row the same way every time you run.

The only path to a more reliable pipeline is understanding why it fails.
You can't do that if you're in the habit of quietly deleting the evidence.

---

### Batch-and-flush: accumulate everything, lose everything

**What you see:** The pipeline is chugging through 5,000 rows. Impressive.
**What's actually happening:** Every result is being held in memory. Nothing is
written until the end. The model thinks this is efficient: gather all the data,
write all the data, one clean operation.

It's not efficient. It's a bet that nothing will go wrong across 5,000 API
calls, 5,000 parses, and 5,000 schema validations. That bet always loses.

An OOM at row 4,999. A rate limit that escalates to a block. A malformed
response that throws an unhandled exception. A multi-step process where
transition data lives in memory through ten stages per row, and one bad stage
flushes everything. The pipeline doesn't degrade gracefully. It doesn't save
what it has. It just dies, and takes every completed row with it.

The model will never suggest flushing to disk after each row. It optimizes for
the clean path. But production is not the clean path. Production is the path
where something always goes sideways, and the only question is whether you
saved your work before it did.

Write each row as it completes. Append to a file, insert to a database, push
to a queue. It doesn't matter how. What matters is that when the crash comes
(and it will), you lose one row instead of all of them.

---

### Timeouts killing mid-response

**What you see:** Some rows didn't complete.
**What's actually happening:** Long-running research tasks finished their work
and then got cut off before the output was written. Completed work, zero
output. Full token cost, nothing to show.

---

### No schema validation

**What you see:** The pipeline ran.  
**What's actually happening:** The model returned something shaped like JSON.
It wasn't valid. The pipeline accepted it, failed three steps later, and
re-ran the whole thing. Full token cost, twice.

---

### Key name drift

**What you see:** Mostly consistent output.  
**What's actually happening:** You asked for `company_name`. You got
`companyName`. Then `name`. Then `company`. Same prompt, different calls.
Valid data, silently discarded because the key didn't match.

`additionalProperties: false` in your output schema kills this instantly.
The model learns the contract or the row fails loudly, not quietly downstream.

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

---

## It gets worse in no-code enrichment tools

Everything above assumes you own the code. You can add backoff. You can cache.
You can validate the schema. The fixes exist. You just have to write them.

Now try doing this in Clay, or any AI enrichment tool that runs on credits.

Same model. Same failure modes. But now:

- You can't adjust the timeout
- You can't clean a malformed response before it hits the pipeline
- You can't retry with a corrected prompt
- You can't capture what the model actually returned

The tool sees a bad response and writes one word in your column: **Error.**

That's it. Credit spent. Row done. You can burn through your entire credit
budget, populate 25% of your rows with "Error," and have absolutely no idea
what went wrong, because the tool didn't keep the receipt.

No stack trace. No raw response. Nothing to build a handler from. The only
artifact of a failed enrichment is the fact that it failed.

At least in code, failure is recoverable. In no-code enrichment tools,
failure is just cost.

---

## What developers actually do

None of these failures are mysterious. Any working developer looks at that
list and immediately thinks: *of course, you need backoff, you need a cache,
you need schema validation.* That's not genius. That's experience.

But you can't notice what you don't know to look for.

Someone who "just wrote software" with AI doesn't see 200 failed API calls;
they see a working demo. They don't see token burn from redundant fetches;
they see results. They don't see data loss from dropped errors; they see the
pipeline finishing.

The AI companies are not unhappy about this. Every redundant call is a
billable token. Every re-run from missing validation is revenue. The model
has no incentive to be efficient. It has no incentive to be correct.
It just completes.

The developer in the room is the one who says "wait, that's stupid," and
then writes the code to make sure it doesn't happen again.

---

## Stop paying that tuition twice

Once you've learned these lessons, you shouldn't have to re-learn them on
every new build.

The right pattern: encode everything you know into a **Data Research Skill**
: a portable markdown document you drop into any new agent's system context.
Not a library. Not a framework. A transferable set of operating rules the
model inherits the moment you give it the job.

The full skill is in the repo below. Here it is inline for those who don't
want to go get it:

---

{% github Cortado-Group/data-research-skill %}

---

```markdown
# Data Research Skill

You are operating as a data research agent. Before executing any task,
internalize these rules completely. They exist because models in this role
consistently make expensive, silent mistakes. These rules are the fix.

---

## Fetch rules

- Never fetch the same URL more than once per session. Cache all responses
  keyed on URL. If you have a result, use it.
- Always implement exponential backoff on failed requests:
  attempt 1 → 1s, attempt 2 → 2s, attempt 3 → 4s. Max 3 retries.
- If an endpoint returns rate-limit errors (429), stop and report.
  Do not retry in a tight loop.
- Do not use a headless browser unless the target page requires JavaScript
  rendering. Default to lightweight HTTP fetch.
- Enforce a hard call budget per run. If you approach the limit, stop and
  surface what you have rather than continuing blindly.

---

## Output rules

- Every response must conform exactly to the output schema provided.
  No additional keys. No renamed keys. No missing required fields.
- If you are uncertain about a value, use null. Do not invent data,
  abbreviate field names, or restructure the schema.
- Key name drift is a failure mode. `company_name` is not `companyName`
  is not `name`. Use the exact key specified. Every time.

---

## Error handling

- Never discard a failed or malformed response. Log the raw output
  alongside the error. The content of a failed response is diagnostic data.
- If a response fails schema validation, flag it with:
  - The raw model output
  - Which validation rule it failed
  - The field(s) involved
  Do not silently mark the row as failed and move on.
- Errors are signal, not trash. After a run, review error rows for patterns.
  Repeated schema failures mean the prompt needs tightening. Repeated fetch
  failures mean the target or method needs changing. Do not accept an error
  rate; diagnose it. Every errored row is a feedback loop you either use
  or pay for again next run.

---

## Persistence rules

- Write each row to output as it completes (file, database, queue, anything
  durable). Do not accumulate results in memory and write once at the end.
- Assume the process will crash. OOM, rate limit escalation, unhandled
  exception, timeout: something will go wrong. When it does, every row
  completed before that point must already be saved.
- Never hold transition data for a multi-step row pipeline entirely in memory.
  If each row passes through ten processing stages, persist intermediate
  state. A failure at stage 9 of row 4,999 should not destroy stages 1-10
  of rows 1-4,998.

---

## What "done" means

A row is not done when the model returned something.
A row is done when:
- The response passed schema validation
- All required fields are present and correctly typed
- The raw response (success or failure) has been logged
- The result has been written to the output

A row that errored is still done, but it must carry its diagnostic payload.
"Error" with no context is not an acceptable output.
```

---

## Determinism is the whole game

Code is deterministic. Given the same input, it returns the same output.
Every time. That's not a feature; it's the foundation every reliable system
is built on.

AI is not deterministic. Same prompt, different run, different output... by
design. That's not a bug in the model. It's fundamental to how these systems
work. And it means every pipeline that hands off to a model
has introduced a source of variance that code alone cannot see coming.

This is where cheaper, faster models deserve specific scrutiny.

Smaller models (the ones that cost a fraction of the price and return results
in milliseconds) are genuinely useful. But the tradeoff isn't just capability.
It's predictability. A cheaper model is more likely to drift on key names, more
likely to hallucinate a field, more likely to return something that's *shaped*
like the right answer without actually being one. The variance is higher. The
failure rate is higher. And because it's fast and cheap, you're probably running
it at higher volume, which means more failures, more often, more quietly.

The guardrails aren't just good practice. They're the deterministic layer that
sits on top of a non-deterministic system and enforces a contract the model
cannot enforce on its own:

- Schema validation says: *this shape, every time, or it doesn't count*
- Error logging says: *every failure leaves a record, no exceptions*
- Caching says: *same input, same result; we're not asking twice*
- Call budgets say: *this far and no further, regardless of what the model wants to do*

None of those rules come from the model. The model doesn't know they exist.
They're code (deterministic, predictable, enforced) wrapped around something
that is none of those things.

That's the architecture. Not AI *or* code. AI *with* a deterministic corrective
layer that keeps the variance from becoming your problem.

The cheaper the model, the more important that layer becomes.

---

## Show your worth

The model will never be the one who says "wait, that's stupid."

That's a human call. It always has been. And in a world where anyone can
ship a working demo in an afternoon, the people who catch the stupid early
(before the token bill arrives, before the pipeline silently fails, before
25% of your rows say Error) are the ones whose value is obvious.

AI didn't kill that skill. It made it rarer. And rarer means worth more.

Show your worth by catching what the model missed.

---

*David Russell is Distinguished Innovation Fellow at
[Cortado Group](https://cortadogroup.ai), where he spends an unreasonable
amount of time writing code that argues with other code.*
