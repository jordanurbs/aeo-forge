---
name: Citation Tracking
version: 1.0.0
description: Methodology for executing a brand's prompt set against AI answer engines (Perplexity, OpenAI web search, Google AI Overviews via SERP) and detecting whether the brand is cited over time. Covers the engine adapter request/response patterns, heuristic citation-detection rules, the scoreboard format and scoring, trend tracking, and honest-labeling rules. Free keyless fallback (manual logging + WebSearch directional proxy) by default; optional keys unlock measured runs. Used by the Citation Tracker agent and the /aeo-track command.
---

# Citation Tracking Skill

AEO success is citation-based: the question is not "do we rank?" but "do AI answer engines *cite* us when buyers ask their questions?". The measurement-builder writes a *manual* prompt set; this skill turns it into a *measured* one. It executes the prompt set against AI engines, detects whether the brand is cited (and who is cited instead), and records the result over time so the team can watch citation frequency move.

The deterministic half lives in `scripts/run-citation-checks.py` (mirroring `scripts/validate-artifacts.py`): the script does the mechanical work -- load prompts, call engine APIs, run heuristic citation detection, write dated result files -- while the **Citation Tracker** agent interprets the JSON and maintains the running scoreboard. This skill documents what the script does so agents and humans read the output correctly.

## What "Citation" Means Here

For each prompt × engine response, detection produces one of three verdicts, strongest first:

1. **source-cited** (strongest) -- a brand domain appears in the response's source/citation URLs. This is the real AEO win: the engine pointed at the brand.
2. **name-mentioned** -- the brand name appears in the answer *text* but no brand domain is in the sources. The engine knows the brand but didn't link it.
3. **not-cited** -- neither. (Note any competitors cited instead.)

`cited = (source-cited OR name-mentioned)`. Always preserve the *type*, not just the boolean -- a source-cited result is a far stronger signal than a name mention.

Detection is **heuristic** (string/domain matching with light normalization). It will miss paraphrases and brand mentions the matcher can't normalize, and it can over-count generic brand names. Say so. Use the `aeo-analysis` source label for every citation verdict.

## Modes & Honest Labeling

The feature must run with NO API keys. The script resolves keys, then picks a mode:

| Mode | When | Label on every row |
|------|------|--------------------|
| **measured** | At least one engine key is available | `measured via Perplexity API` / `measured via OpenAI web search` / `measured via Google SERP (SerpAPI, AI Overview proxy)` |
| **manual** | No keys found | `directional proxy / manual (no API key)` |

In **manual** mode the script writes a manual-logging template (a table with one row per prompt × engine) and exits 0 -- it never hard-fails for a missing key. The human pastes prompts into each engine and fills the table, **or** the Citation Tracker agent runs its own `WebSearch` as a *directional proxy* (clearly lower-confidence, never labeled "measured").

Never blur the line: "measured via [engine]" is an API result; "directional proxy" is the agent's web search standing in for an engine. Keep confidence at `PARTIAL_CONFIDENCE` for any run that is manual or partly directional.

## Engine Adapters

Each adapter is optional and gated on its key being present. Implement/trust them in priority order: **Perplexity first** (it returns answers *with* citations -- the best signal), then OpenAI, then SERP. Each returns `(answer_text, source_urls)` or records a graceful per-engine failure (HTTP error, timeout, parse error) and continues.

### Key resolution (no secrets in the repo)

Keys are read from **environment variables first**, then from the `## API Keys` section of `config/brand-profile.md` (which is gitignored). Placeholder values like `not provided` / `key` are ignored.

| Engine | Env var(s) | brand-profile label(s) |
|--------|-----------|------------------------|
| `perplexity` | `PERPLEXITY_API_KEY` | `Perplexity API key` |
| `openai` | `OPENAI_API_KEY` | `OpenAI API key` |
| `serp` | `SERPAPI_KEY`, `SERPAPI_API_KEY`, `DATAFORSEO_KEY` | `SerpAPI key`, `DataForSEO key` |

### 1. Perplexity (highest value)

```
POST https://api.perplexity.ai/chat/completions
Authorization: Bearer <PERPLEXITY_API_KEY>
{
  "model": "sonar",
  "messages": [
    {"role": "system", "content": "Be precise and cite your sources."},
    {"role": "user", "content": "<prompt>"}
  ],
  "return_citations": true
}
```
Extract the answer from `choices[0].message.content`. Extract sources from `citations[]` (list of URL strings) and `search_results[].url`. De-duplicate, preserving order.

### 2. OpenAI web search

```
POST https://api.openai.com/v1/responses
Authorization: Bearer <OPENAI_API_KEY>
{
  "model": "gpt-4o-mini",
  "tools": [{"type": "web_search_preview"}],
  "input": "<prompt>"
}
```
Walk `output[].content[]`: text from items whose `type` is `output_text`/`text`; source URLs from each content item's `annotations[].url` (the web-search citations). Falls back to `output_text` if present.

### 3. Google AI Overviews (SERP proxy)

No official AI Overviews API; SerpAPI is the closest proxy.

```
GET https://serpapi.com/search.json?engine=google&q=<prompt>&api_key=<SERPAPI_KEY>&num=10
```
Prefer the `ai_overview` block: text from `ai_overview.text_blocks[].snippet`, sources from `ai_overview.references[].link`. Fall back to `organic_results[].link` (+ first snippet) when no AI Overview is returned. Treat this as a *proxy* for AI Overviews, not the Overview itself.

## Citation Detection Rules

Implemented in `detect_citation()`; document the rules and edge cases here.

**Domain normalization (`domain_of`)** -- lowercases, adds a scheme if missing, strips `userinfo@`, port, and a leading `www.`. So `https://WWW.Example.com:443/x` -> `example.com`.

**Brand/host matching (`host_matches`)** -- a source URL matches a brand domain if the normalized host is equal to, a subdomain of, or a parent of the brand domain. So `docs.example.com` matches brand `example.com`, and vice versa. Brand domains come from the brand profile's primary + additional domains.

**Verdict per response:**
- **source-cited** if any source URL host matches a brand domain. `position` = the 1-based index of the first matching source URL (prominence proxy).
- **name-mentioned** if the brand name appears in the answer text as a whole word (`\bbrand\b`, case-insensitive) and it isn't already source-cited.
- **not-cited** otherwise.

**Competitors cited** -- from `research/competitor-analysis.md` (markdown links + bare domains) plus profile competitors. A competitor counts as cited if its domain appears in the sources, its domain string appears in the answer text, or its name appears as a whole word in the answer text. Record the name (or domain) once.

**Answer summary** -- whitespace-collapsed answer truncated to ~220 chars for context in the run detail.

**Known edge cases / limits to disclose:**
- Short or generic brand names can false-positive on the word-boundary text match.
- A brand cited only as plain text (no link) is `name-mentioned`, never `source-cited` -- that's intended (weaker signal).
- Paraphrased recommendations with no name/domain string are missed.
- `position` reflects source order returned by the engine, not on-screen placement.

## Scoring

**Citation frequency = cited prompts / total answered prompts**, computed per engine and overall, over rows with `status == ok` (errors and manual rows are excluded from the denominator). The JSON stores `frequency` rounded to 3 decimals (or `null` when total is 0); render it as a percentage in markdown.

```
per engine:  {engine: {cited, total, frequency}}
overall:     {cited: sum, total: sum, frequency}
```

Frequency is the headline KPI. Pair it with the *type* mix (how many were source-cited vs name-only) and the trend vs the prior run -- a flat frequency can hide a shift from name-mentions to real source citations (good) or the reverse (bad).

## Output Files

The script writes, under `output/<brand-slug>/measurement/citation-runs/`:
- `<YYYY-MM-DD>.json` -- machine-readable run (brand, domains, date, mode, engines attempted/available, competitors, prompt source/count, per-row results, summary, detection note). The Citation Tracker reads this.
- `<YYYY-MM-DD>.md` -- human-readable run detail (per-engine frequency table + per-prompt results table, or the manual-logging template).

With `--write-report` it also writes a deterministic draft of:
- `../citation-scoreboard.md` -- running trend across all runs in `citation-runs/`.

The dated run files are **transient fixture artifacts** when produced against `fixtures/sample-output/...` -- do not commit those.

## Scoreboard Format

`citation-scoreboard.md` is the running trend the team watches. The script drafts it deterministically from every `citation-runs/*.json`; the Citation Tracker agent enriches it with interpretation. Structure:

```markdown
# Citation Scoreboard: [Brand]

Running AI-citation frequency across runs. Citation detection is heuristic
(`aeo-analysis` source label). Re-run /aeo-track on cadence (monthly suggested).

## Overall Citation Frequency by Run
| Date | Mode | Overall | Perplexity | OpenAI | SERP |
|------|------|---------|------------|--------|------|
| 2026-06-04 | measured | 33% (1/3) | 33% (1/3) | - | - |

## Latest Run (2026-06-04) -- Gaps
**Uncited prompts (citation opportunities):**
- [high-priority prompt the brand should win]

**Competitors winning citations:**
- Competitor X (2)
```

The agent adds, on top of the deterministic draft:
- **Trend vs previous run** -- up/down/flat per engine and overall, with the delta.
- **Top uncited high-priority prompts** -- ranked by buyer-journey importance, mapped back to plan items / content to create.
- **Competitors winning citations** -- who keeps getting cited where the brand isn't, and on which prompts.
- **Type mix** -- source-cited vs name-mentioned share, and whether it's improving.

## Rules

- **Measurement, not ranking.** Citation frequency is the AEO KPI; never present it as a Google rank or a guarantee.
- **Label the mode.** Every row and the scoreboard say "measured via [engine]" or "directional proxy / manual". Never call a WebSearch proxy "measured".
- **Detection is heuristic.** State it. Use the `aeo-analysis` source label and hedge name-only matches.
- **No secrets.** Keys come from env or the gitignored profile. Never echo a key into any output file or commit one.
- **Graceful degradation.** A missing key -> manual mode (exit 0). A failed engine call -> recorded failure, other engines continue. No prompts -> clear error telling the user where to add them.
- **Respect fixture mode.** For fixture/sample runs, keep confidence `PARTIAL_CONFIDENCE`, treat numbers as illustrative, and don't commit the dated run files.
- **Trend over snapshot.** One run is a baseline; value comes from re-running on cadence and reading the delta.
