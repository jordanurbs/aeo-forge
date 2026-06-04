---
name: Demand Signals
version: 1.0.0
description: Methodology for gathering real demand signals (prompt/query expansions, People-Also-Ask, and optional keyword search volume) and turning them into a Demand tier that weights backlog prioritization. Free sources by default (Google Autocomplete, web search) with optional paid keyword-volume APIs (DataForSEO, Semrush). Used by the Demand Researcher agent and the AEO Strategist.
---

# Demand Signals Skill

AEO success is citation-based, not volume-based -- but prioritization still benefits from knowing which topics and prompts have real demand. This skill gathers demand signals and normalizes them into a **Demand tier** the AEO Strategist uses to weight the backlog: a high-demand topic with a citability gap is a stronger plan item than a low-demand one.

## What "Demand" Means Here

Two complementary signals:
1. **Prompt demand** -- how often people actually ask the brand's target questions of search/AI (proxied by query expansions, autocomplete breadth, and People-Also-Ask coverage).
2. **Keyword volume** -- estimated monthly search volume for the topic terms, when a keyword-data API key is available.

Neither is a ranking lever. They are *prioritization inputs* only. Always label the source and confidence.

## Source Tiers (use what's available)

### Tier A -- Free, always available (no key)

**1. Google Autocomplete / Suggest** (query expansion + demand breadth proxy):
```bash
# Firefox client returns clean JSON: [query, [suggestions...]]
curl -s "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&q=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' "product analytics")"
```
- Run for each priority topic and each target AI query.
- Optional "alphabet soup" for breadth: append " a", " b", ... or " how", " best", " vs", " cost" to surface more variants.
- More distinct, relevant suggestions = broader demand around that topic.

**2. People-Also-Ask / related questions** (prompt demand proxy):
- Use WebSearch on each priority query; capture related questions and "people also ask" style follow-ups that appear.
- Record the actual questions surfaced. These are real prompts to target with answer-first content + FAQ schema.
- Hedge: "surfaced in our search at [date]; coverage varies."

**3. Competitor coverage** (demand confirmation):
- From `competitor-analysis.md`: if multiple competitors publish dedicated content for a query, that's demand confirmation (someone validated it's worth answering).

### Tier B -- Optional, paid (only if a key is in the brand profile)

**DataForSEO** (Keywords Data -- Google Ads search volume):
```bash
# Basic auth: base64("login:password") in the brand profile as the DataForSEO key
curl -s -X POST "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live" \
  -H "Authorization: Basic $DATAFORSEO_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"keywords":["product analytics","revenue analytics"],"location_code":2840,"language_code":"en"}]'
```
Parse `tasks[].result[].search_volume`, `competition`, `cpc`.

**Semrush** (phrase volume; returns CSV):
```bash
curl -s "https://api.semrush.com/?type=phrase_this&key=$SEMRUSH_KEY&phrase=product%20analytics&database=us&export_columns=Ph,Nq,Cp,Co"
```
`Nq` = monthly volume.

If a key is present, attach numeric monthly volume per topic. If not, skip Tier B and derive demand from Tier A only -- this is expected and fine.

## Normalizing to a Demand Tier

Produce a `Demand` value per priority topic / target query:

| Demand | With keyword volume (Tier B) | Without volume (Tier A only) |
|--------|------------------------------|------------------------------|
| **High** | High monthly volume for the category, or strong volume + competitor coverage | Many relevant autocomplete variants + PAA present + multiple competitors cover it |
| **Medium** | Moderate volume | Some autocomplete variants OR PAA present OR some competitor coverage |
| **Low** | Low/negligible volume | Few/no variants, no PAA, little competitor coverage |
| **Unknown** | -- | No signal could be gathered (note the gap) |

Always pair the tier with its basis, e.g. "High (Tier A: 18 autocomplete variants, 6 PAA questions, 3/3 competitors cover) [demand-signals]" or "Medium (Tier B: 1,300 MSV, DataForSEO) [demand-signals]".

## Output Conventions

Write `research/demand-signals.md` as a table the AEO Strategist can join to backlog items by topic/query:

```markdown
# Demand Signals: [Brand]
Source tier used: [A only | A+B] | Keyword API: [DataForSEO / Semrush / none] | Date: [date]

## Priority Topics / Target Queries
| Topic / Query | Demand | Volume (if any) | Autocomplete variants (sample) | PAA / related questions | Competitor coverage | Source |
|---------------|--------|-----------------|--------------------------------|-------------------------|---------------------|--------|
| product analytics | High | 1,300 MSV | "product analytics tools", "product analytics vs web analytics" | "What is product analytics?" | 3/3 | demand-signals (A+B) |

## New Prompts Discovered (worth targeting)
- [Question surfaced via autocomplete/PAA that the brand should own]

## Notes & Gaps
- [Rate limits, no key, locales not covered, hedged confidence]
```

## Rules

- **Prioritization input only.** Never present demand as a ranking factor or guarantee.
- **Label sources + confidence.** Every demand value cites Tier A/B and the basis. Use the `demand-signals` source label.
- **Hedge volume without a key.** Tier A is directional, not a measurement -- say so.
- **Respect fixture mode.** For fixture/sample runs, use illustrative numbers and keep confidence at PARTIAL.
- **Feed the plan, don't rank pages.** The output exists to weight the backlog and surface new prompts to target.
