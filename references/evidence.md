# Why This Matters: The Evidence

This skill exists because the failures in `failure-modes.md` are not hypothetical.
They show up in published research, vendor postmortems, and industry surveys, over
and over, at real cost. This page collects the numbers, linked at the point of
each claim.

## Enterprise AI projects mostly fail, and data is the reason

- RAND Corporation interviewed 65 experienced data scientists and found that
  more than 80% of AI projects fail, roughly twice the failure rate of non-AI
  IT projects, with data quality limitations named as one of five root causes
  ([RAND, 2024](https://www.rand.org/pubs/research_reports/RRA2680-1.html)).
- MIT NANDA found that despite $30 to $40 billion in enterprise generative AI
  investment, 95% of pilots produced no measurable financial return
  ([MIT NANDA, "The GenAI Divide," 2025](https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf)).
- Gartner predicts that through 2026, organizations will abandon 60% of AI
  projects that lack AI ready data, and found that 63% of organizations
  either lack, or are unsure they have, the right data management practices
  for AI
  ([Gartner, "Lack of AI-Ready Data Puts AI Projects at Risk," 2025](https://www.gartner.com/en/newsroom/press-releases/2025-02-26-lack-of-ai-ready-data-puts-ai-projects-at-risk)).

Poor data quality is not a side issue. It is the single most cited cause of
failure across every major survey on the topic. A pipeline that silently
drops rows, accepts malformed JSON, or loses key names between calls (see
`failure-modes.md`) is manufacturing exactly the kind of bad data these
reports are describing.

## Autonomous agents fail roughly half the time, for structural reasons

- A 34 task benchmark across three open source agent frameworks and two LLM
  backbones found an average task completion rate of about 50%, with a
  failure taxonomy spanning planning errors, execution errors, and incorrect
  responses
  ([Lu, Li, and Huo, "Exploring Autonomous Agents," 2025](https://arxiv.org/abs/2508.13143)).
- An analysis of 1,600+ annotated agent traces across seven frameworks found
  that specification failures (41.8%) and inter agent coordination failures
  (36.9%) dominate, with only about 21% of failures tracing back to
  infrastructure, meaning most of the loss comes from ambiguous instructions
  and broken handoffs, not broken servers
  ([agent failure taxonomy study](https://arxiv.org/pdf/2607.05775)).
- The same study found that failures compound nonlinearly with task length,
  and that adding more scaffolding does not reliably fix it. A bigger model
  does not fix an unbounded retry loop
  ([agent failure taxonomy study](https://arxiv.org/pdf/2607.05775)).

## Unmanaged failures turn into unmanaged cost

- Unmanaged rate limiting is identified as the leading cause of agent
  failures in production, because a single unhandled 429 cascades into
  retries, then into crashed workers, then into a bill nobody expected
  ([OpenLegion, "AI Agent Rate Limiting," 2026](https://www.openlegion.ai/en/learn/ai-agent-rate-limiting)).
- A documented coding agent task that should have used roughly 180K tokens
  spiked to 2.1M tokens, a 12x cost increase, after hitting ambiguous input
  and retrying blindly instead of stopping to ask
  ([Nexgismo, "AI Agent Budget Guards," 2026](https://www.nexgismo.com/blog/ai-agent-budget-guards-stop-runaway-api-costs)).

None of these are exotic failures. They are the rate limit cascade, the
batch and flush, and the error treated as trash, described plainly, at
production scale.
