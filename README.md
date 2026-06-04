# Enterprise AEO Builder

A Claude Code rig that helps an internal team continuously improve their brand's presence in AI search (ChatGPT, Perplexity, Google AI Overviews, Gemini, Copilot, Claude). It runs in two stages:

1. **Plan (`/aeo-plan`)** -- researches your site and competitors, runs a deep AEO analysis, and produces a prioritized, traceable **AEO improvement plan**. You review and approve it, and select which items to build.
2. **Build (`/aeo-build`)** -- generates **ready-to-ship artifacts** for the items you selected: stacked JSON-LD schema, answer-first content blocks, metadata, an entity knowledge graph, a measurement pack, content briefs, and (optionally) `llms.txt` and an edge-injection config. Everything is validated before an implementation manifest is written.

Then an ongoing **measurement loop (`/aeo-track`)** executes the prompt set against AI answer engines and tracks how often your brand is actually cited -- turning the manual measurement plan into a measured one.

This is an **internal tool**, not a sales asset. No cold outreach, cover letters, pricing, or "deliverable to sell" -- the output is work product your team ships.

**AEO is the whole point.** Every artifact targets being *cited* by answer engines, not just ranking in a list of links.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed and configured

## Setup

1. Clone this repo and open the `aeo-audit/` directory in Claude Code
2. Run `/setup` to configure your brand profile (domains, entity signals, AEO targets, tech stack, governance), or copy `config/brand-profile.example.md` to `config/brand-profile.md` and edit it
3. You're ready

## Usage

### Stage 1 -- Generate the plan

```
/aeo-plan
```

Runs the research + analysis pipeline and writes a prioritized improvement plan you approve:

1. **Web Crawler** -- crawls your site for technical + answer-readiness signals
2. **API Caller** -- PageSpeed, TLS/SSL, W3C, Wayback, WHOIS (real metrics, no fabrication)
3. **Competitor Researcher** -- benchmarks 2-3 competitors' AEO posture
4. **AEO Analyst** -- the centerpiece AI search readiness assessment
5. **AEO Strategist** -- synthesizes everything into `plan/aeo-plan.md` (prioritized, artifact-mapped backlog)

Then you review the plan and select which item IDs to build.

### Stage 2 -- Build the artifacts

```
/aeo-build
```

Generates and validates artifacts for the selected items:

- **Answer-Content Builder** -- answer-first FAQ/definition/comparison/how-to blocks
- **Schema Builder** -- stacked, validated JSON-LD per page (+ paste-ready snippets, optional edge-injection config)
- **Metadata Builder** -- titles, descriptions, OG/Twitter, freshness fields
- **Entity Builder** -- Organization knowledge graph (`sameAs`) + cross-domain consistency report
- **Measurement Builder** -- tracked prompt set + measurement plan + bot-log monitoring snippet
- **Content-Brief Builder** -- specs for net-new content your writers create
- **llms.txt Builder** -- optional, low-priority agent index
- **Artifact Validator** -- gate: JSON-LD validity, schema/visible-text parity, answer-first conformance, entity consistency, traceability
- **Manifest/Report Builder** -- implementation manifest (how to deploy each artifact) + optional internal stakeholder summary

### Stage 3 -- Track citations (the measurement loop)

```
/aeo-track
```

`/aeo-build` writes a *manual* measurement plan -- a prompt set you'd paste into engines by hand. `/aeo-track` turns it into a *measured* one: it executes the prompt set against AI answer engines, detects whether your brand is cited, captures who is cited instead, and updates a running scoreboard so you can watch citation frequency over time.

- **Keyless by default.** With no API keys it produces a manual-logging template plus an optional WebSearch directional proxy (clearly labeled lower-confidence) -- it never fails for a missing key.
- **Measured with a key.** Add a **Perplexity** key (recommended -- it returns answers *with* sources), and/or **OpenAI** (web search) or **SerpAPI** (Google AI Overviews proxy), via env var or `config/brand-profile.md`, to get real measured runs.
- **Honest labeling.** Every result is labeled "measured via [engine]" vs "directional proxy / manual". Citation detection is heuristic (domain/name matching) and says so.
- **Trend, not snapshot.** Re-run on cadence (monthly suggested); the scoreboard shows per-engine frequency, the delta vs the prior run, top uncited high-priority prompts, and competitors winning citations.

The deterministic engine orchestration lives in `scripts/run-citation-checks.py`; the **Citation Tracker** agent interprets the results and maintains the scoreboard.

## What You Get

```
output/<brand-slug>/
  README.md                          # Table of contents + deploy checklist
  plan.md                            # Run config + build selection
  research/
    site-crawl.md                    # Crawl analysis (technical + answer-readiness)
    tool-data.md                     # Raw API data
    competitor-analysis.md           # Competitor AEO benchmarking
    aeo-analysis.md                  # AEO deep-dive (the centerpiece)
  plan/
    aeo-plan.md                      # Prioritized improvement plan (APPROVAL GATE)
  artifacts/
    README.md                        # Implementation manifest
    build-route.md                   # Selected item routing + expected outputs
    validation.md                    # Deterministic validation report
    schema/                          # *.json + *.html snippets + INDEX.md
    content/                         # answer-first blocks (.md + .html, schema-matched)
    metadata/                        # meta-tags.md
    entity/                          # knowledge-graph.json + consistency-report.md
    measurement/                     # prompt-set.md + measurement-plan.md + bot-log-snippet
      citation-runs/                 # <date>.json + <date>.md (per /aeo-track run)
      citation-scoreboard.md         # running AI-citation frequency + trend
    content-briefs/                  # *.md
    llms.txt                         # optional, low-priority
    edge/                            # optional Cloudflare Worker / injection config
  report/
    internal-summary.*               # optional stakeholder summary
```

## What Actually Moves AI Citations (2026)

The rig is built around evidence-based levers, not 2023-era SEO:

- **Schema stacking** -- FAQPage alone shows ~+2.7x citation lift; stacking `Article + FAQPage + HowTo + Organization + BreadcrumbList + ItemList` on key pages compounds it.
- **Answer-first content** -- a direct 40-60 word answer at the top; question-form headings; AI Overviews cite opening content ~55% of the time.
- **Visible-text / JSON-LD parity** -- FAQ/HowTo schema must mirror visible text exactly; mismatches are a compliance risk.
- **Valid schema only** -- malformed JSON-LD is a negative trust signal, so every block is parsed and validated.
- **Entity / single source of truth** -- a canonical `Organization` with `sameAs` and consistent facts across properties.
- **Freshness** -- `dateModified`, visible "last updated", recent stats; quarterly refresh.
- **Measurement shift** -- track citation frequency / AI Overview presence / AI-referred sessions, not just rank.
- **`llms.txt`** is included but **optional and low-priority**: major search/answer crawlers largely ignore it; only application agents (Claude Desktop, Cursor) read it.

## Quality & Traceability

Every run should finish with an explicit state:

- **COMPLETE** -- all required research and selected artifacts exist.
- **PARTIAL_CONFIDENCE** -- useful output exists, but one or more research inputs or checks failed; gaps are listed in the plan/report.
- **BLOCKED** -- required evidence or validation is missing; artifacts should not ship.

Plan items and artifacts should label evidence sources as `brand-profile`, `site-crawl`, `tool-data`, `competitor-analysis`, `aeo-analysis`, or `inference`. Claims about ratings, customer counts, credentials, certifications, profiles, or entity facts must trace to supplied or observed evidence.

## Real API Data

| Tool | What It Provides |
|------|-----------------|
| Google PageSpeed Insights | Core Web Vitals (LCP, CLS, INP), performance score, mobile + desktop |
| TLS/SSL (curl -v) | TLS version, certificate details, cipher info |
| W3C HTML Validator | HTML validation errors/warnings |
| Wayback Machine | Site history, domain age indicator |
| WHOIS (RDAP -> Who-Dat -> whois) | Domain registration, age, expiration |

## Configuration

Your settings live in `config/brand-profile.md` (template: `config/brand-profile.example.md`). Run `/setup` to configure, or edit directly.

## Commands

| Command | What it does |
|---------|-------------|
| `/setup` | Configure the brand profile |
| `/aeo-plan` | Research + AEO analysis -> a prioritized improvement plan (approval gate) |
| `/aeo-build` | Generate validated artifacts for the selected plan items |
| `/aeo-track` | Run the prompt set against AI engines + track citation frequency over time (re-run on cadence) |

## Local Validation

After `/aeo-build`, run:

```
python3 scripts/validate-artifacts.py output/<brand-slug> --write-report
```

This performs deterministic checks for JSON parsing, selected item coverage, per-artifact `AEO-xxx` references, source labels, stacked page schema, schema/entity consistency, and FAQ/HowTo visible-text parity before the agent validation gate.

Smoke-test the validator with the included fixture:

```
python3 scripts/validate-artifacts.py fixtures/sample-output/acme-analytics
```
