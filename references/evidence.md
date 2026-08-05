# Why This Matters: The Evidence

This skill exists because the failures in `failure-modes.md` are not hypothetical.
They show up in published research, vendor postmortems, and industry surveys, over
and over, at real cost. This page collects the numbers.

## Enterprise AI projects mostly fail, and data is the reason

- RAND Corporation found that 80.3% of enterprise AI projects fail to deliver
  their promised business value.
- MIT's NANDA research (2025) reported that 95% of generative AI pilots failed
  to produce measurable financial returns.
- Gartner reports that 85% of failed AI projects cite poor data quality as a
  root cause, and that only 12% of organizations have data of sufficient
  quality to support AI applications.
- Gartner predicts that 60% of AI projects lacking AI ready data will be
  abandoned through 2026.

Poor data quality is not a side issue. It is the single most cited cause of
failure across every major survey on the topic. A pipeline that silently
drops rows, accepts malformed JSON, or loses key names between calls (see
`failure-modes.md`) is manufacturing exactly the kind of bad data these
reports are describing.

## Autonomous agents fail roughly half the time, for structural reasons

- A benchmark spanning 34 tasks across popular open source agent frameworks
  found an average task completion rate of about 50%.
- An analysis of 1,600+ annotated agent traces across seven frameworks found
  that specification failures (41.8%) and inter agent coordination failures
  (36.9%) dominate. Only 21% of failures trace back to infrastructure. Most of
  the loss comes from ambiguous instructions and broken handoffs, not broken
  servers.
- Researchers observed that failures compound nonlinearly with task length,
  and that adding more scaffolding does not reliably fix it. A bigger model
  does not fix an unbounded retry loop.

## Unmanaged failures turn into unmanaged cost

- Unmanaged rate limiting is widely cited as the leading cause of agent
  failures in production, because a single unhandled 429 cascades into
  retries, then into crashed workers, then into a bill nobody expected.
- A documented coding agent task that should have used roughly 180K tokens
  spiked to 2.1M tokens (a 12x cost increase) after hitting ambiguous input
  and retrying blindly instead of stopping to ask.
- A reported case from mid 2026 has an unattended agent running up a $6,531
  cloud bill on a task that should have cost a fraction of that, with no human
  in the loop to notice the spend climbing.

None of these are exotic failures. They are the rate limit cascade, the
batch and flush, and the error treated as trash, described plainly, at
production scale.

## Sources

- [RAND Corporation, enterprise AI value delivery, cited via Folio3 AI](https://www.folio3.ai/blog/ai-project-failure-rate-stats)
- [MIT NANDA 2025 generative AI pilot research, cited via SR Analytics](https://sranalytics.io/blog/why-95-of-ai-projects-fail/)
- [Gartner data quality and AI readiness findings, cited via Connected Paths](https://connectedpaths.com/insights/ai-project-failure-statistics/)
- [Autonomous agent benchmark task completion rate](https://quantumzeitgeist.com/ai-agents-fail-half-the-time-new-benchmark-reveals-weaknesses/)
- [Specification and coordination failure taxonomy across agent frameworks](https://arxiv.org/pdf/2607.05775)
- [Rate limiting as leading cause of agent production failures](https://www.openlegion.ai/en/learn/ai-agent-rate-limiting)
- [12x token cost spike case study](https://www.nexgismo.com/blog/ai-agent-budget-guards-stop-runaway-api-costs)
