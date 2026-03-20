# Data Research Skill

A portable skill document you drop into any AI agent's system context to prevent the silent, expensive mistakes they make during data research and enrichment.

This is not a library or framework. It's a set of operating rules the model inherits the moment you give it the job.

## What it prevents

| Trap | What you actually pay for |
|---|---|
| Rate limit cascade | 200+ failed calls with zero backoff |
| Browser for text fetch | Full Chromium launched to fetch plain text |
| Redundant fetches | Same URL fetched 3-4x per entity, no cache |
| Discarded errors | Raw diagnostic response thrown away |
| Batch-and-flush | All results lost on crash (OOM at row 4,999) |
| Timeout data loss | Completed work never persisted |
| Invalid JSON accepted | Pipeline re-runs at full token cost |
| Key name drift | Valid data silently dropped (`company_name` vs `companyName`) |
| Errors treated as trash | Same failures repeated every run, never diagnosed |

## Usage

### With Claude Code

Drop `SKILL.md` into your project root or reference it in your `CLAUDE.md`:

```markdown
Follow the rules in SKILL.md for all data research tasks.
```

### With any LLM agent

Include the contents of `SKILL.md` in your system prompt or agent instructions before the task description.

### With OpenAI Agents / Custom GPTs

Paste the contents into your agent's instructions or upload as a knowledge file.

## What's in the repo

```
SKILL.md                                 The skill (what the AI reads)
scripts/validate_output.py               Runnable schema validator
references/failure-modes.md              Detailed trap catalog with fixes
references/example-schema-validation.md  Example prompt + validation walkthrough
docs/ai-wont-stop-itself.md              Blog post with full context
```

## Background

Read the full story: [AI Won't Stop Itself From Being Stupid: That's YOUR Job](docs/ai-wont-stop-itself.md)

## License

MIT
