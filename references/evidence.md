# Why This Matters: The Evidence

This skill exists because the failures in `failure-modes.md` are not hypothetical.
They show up in published research, vendor postmortems, and industry surveys, over
and over, at real cost. This page collects the numbers.

## Enterprise AI projects mostly fail, and data is the reason

- [RAND Corporation](https://www.rand.org/pubs/research_reports/RRA2680-1.html)
  interviewed 65 experienced data scientists and found that more than 80% of
  AI projects fail, roughly twice the failure rate of non-AI IT projects. Data
  quality limitations were one of five root causes identified.
- [MIT NANDA's "State of AI in Business 2025" report](https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf)
  found that despite $30 to $40 billion in enterprise generative AI
  investment, 95% of pilots produced no measurable financial return.
- [Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-02-26-lack-of-ai-ready-data-puts-ai-projects-at-risk)
  predicts that through 2026, organizations will abandon 60% of AI projects
  that lack AI ready data, and found that 63% of organizations either lack, or
  are unsure they have, the right data management practices for AI.

Poor data quality is not a side issue. It is the single most cited cause of
failure across every major survey on the topic. A pipeline that silently
drops rows, accepts malformed JSON, or loses key names between calls (see
`failure-modes.md`) is manufacturing exactly the kind of bad data these
reports are describing.

## Autonomous agents fail roughly half the time, for structural reasons

- [Lu, Li, and Huo (2025)](https://arxiv.org/abs/2508.13143) built a 34 task
  benchmark across three open source agent frameworks and two LLM backbones,
  finding an average task completion rate of about 50%. Their failure
  taxonomy spans planning errors, execution errors, and incorrect responses.
- [An analysis of 1,600+ annotated agent traces across seven frameworks](https://arxiv.org/pdf/2607.05775)
  found that specification failures (41.8%) and inter agent coordination
  failures (36.9%) dominate. Only about 21% of failures trace back to
  infrastructure. Most of the loss comes from ambiguous instructions and
  broken handoffs, not broken servers.
- The same research found that failures compound nonlinearly with task
  length, and that adding more scaffolding does not reliably fix it. A bigger
  model does not fix an unbounded retry loop.

## Unmanaged failures turn into unmanaged cost

- [OpenLegion's analysis of agent rate limiting](https://www.openlegion.ai/en/learn/ai-agent-rate-limiting)
  identifies unmanaged rate limiting as the leading cause of agent failures in
  production, because a single unhandled 429 cascades into retries, then into
  crashed workers, then into a bill nobody expected.
- [A documented case](https://www.nexgismo.com/blog/ai-agent-budget-guards-stop-runaway-api-costs)
  describes a coding agent task that should have used roughly 180K tokens
  spiking to 2.1M tokens, a 12x cost increase, after hitting ambiguous input
  and retrying blindly instead of stopping to ask.

None of these are exotic failures. They are the rate limit cascade, the
batch and flush, and the error treated as trash, described plainly, at
production scale.

## Sources

- [RAND Corporation: The Root Causes of Failure for Artificial Intelligence Projects and How They Can Succeed](https://www.rand.org/pubs/research_reports/RRA2680-1.html)
- [MIT NANDA: The GenAI Divide, State of AI in Business 2025](https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf)
- [Gartner: Lack of AI Ready Data Puts AI Projects at Risk](https://www.gartner.com/en/newsroom/press-releases/2025-02-26-lack-of-ai-ready-data-puts-ai-projects-at-risk)
- [Lu, Li, and Huo: Exploring Autonomous Agents, A Closer Look at Why They Fail When Completing Tasks](https://arxiv.org/abs/2508.13143)
- [Specification and coordination failure taxonomy across agent frameworks](https://arxiv.org/pdf/2607.05775)
- [OpenLegion: AI Agent Rate Limiting, Quota Control, Circuit Breakers, and Budget Caps](https://www.openlegion.ai/en/learn/ai-agent-rate-limiting)
- [Nexgismo: AI Agent Budget Guards, How to Stop Runaway API Costs](https://www.nexgismo.com/blog/ai-agent-budget-guards-stop-runaway-api-costs)
