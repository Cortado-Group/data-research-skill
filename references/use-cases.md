# Use Cases

Concrete scenarios where this skill applies. Each one is a pipeline that
fetches external data, calls an LLM, and produces structured rows, exactly
the shape of pipeline that hits the failures in
[failure-modes.md](failure-modes.md).

## Lead and account enrichment

Turn a list of company names or domains into firmographic data: employee
count, industry, headquarters, founding year, tech stack.

- **Where it breaks:** No URL cache means the same company site gets fetched
  three times across separate lookups (name, domain, LinkedIn). Key name
  drift (`employee_count` vs `headcount`) silently drops fields the sales
  team never sees.
- **What the skill fixes:** URL cache per entity, a strict schema with
  `additionalProperties: false`, and `null` instead of a guessed headcount.

## Contact and persona research

Find a decision maker's role, tenure, and public activity ahead of outreach,
feeding tools like SDR call prep or persona-matched email drafting.

- **Where it breaks:** A full headless browser gets launched to read a
  LinkedIn-style profile that's really just static text, burning CPU on
  every single contact in a list of thousands.
- **What the skill fixes:** HTTP fetch by default, browser only when a page
  genuinely requires JS rendering.

## Investment and portfolio diligence

Research a target company's market position, competitors, and financial
signals for an investment memo or portfolio review.

- **Where it breaks:** A multi-hour research run gets cut off by a timeout
  after 40 of 50 companies are done, and the batch-and-flush pattern means
  all 40 completed rows are lost because nothing was persisted along the way.
- **What the skill fixes:** Write each company's result to durable storage
  as it completes. A timeout costs you the last row, not the whole run.

## Competitive and market intelligence

Aggregate competitor pricing pages, changelogs, or press releases into a
structured comparison table, refreshed on a schedule.

- **Where it breaks:** A scheduled job hits the same handful of competitor
  domains every run with no backoff, and eventually the target starts
  returning 429s that turn into a silent, permanent block.
- **What the skill fixes:** Exponential backoff, and a hard stop on 429
  instead of retrying into a ban.

## Dataset augmentation and cleanup

Take an existing CSV of records (companies, people, products) and fill in
missing fields, or normalize inconsistent ones, at row-scale.

- **Where it breaks:** The model returns a value shaped like valid JSON that
  isn't, the row is accepted anyway, and the mistake doesn't surface until a
  downstream step throws three stages later, forcing a full re-run at full
  token cost.
- **What the skill fixes:** Schema validation before a row is marked
  complete, catching the malformed row at the cheapest possible point.

## Document and transcript extraction

Pull structured claims (deal terms, meeting action items, contract clauses)
out of a batch of PDFs, transcripts, or emails.

- **What the skill fixes:** Raw error responses stay attached to any row
  that fails extraction, so a bad parse is diagnosable instead of just
  "Error." See the discarded error responses entry in
  [failure-modes.md](failure-modes.md).

## Compliance and list screening

Check a batch of entities (vendors, customers, counterparties) against
public registries, sanctions lists, or regulatory filings.

- **Where it breaks:** Errors get treated as noise: a 15% failure rate gets
  re-run blindly instead of being diagnosed, and the same ambiguous names
  fail the same way every time, at full cost, forever.
- **What the skill fixes:** Post-run error review by pattern, not blind
  re-runs. See error results treated as trash in
  [failure-modes.md](failure-modes.md).

## No-code enrichment tool replacement

Any of the above, currently run through a no-code enrichment tool (Clay and
similar), where a bad response just shows up as "Error" with no raw output
to debug.

- **What the skill fixes:** Everything above is recoverable in code and
  invisible in most no-code tools. Owning the pipeline is what makes
  diagnosis possible in the first place.

## What ties these together

Different domains, same five failure classes: uncached fetches, silent
batch loss, discarded diagnostics, schema drift, and errors treated as
disposable instead of informative. The rules in
[SKILL.md](../SKILL.md) apply the same way regardless of what's being
researched.
