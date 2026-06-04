# Enterprise AEO Builder -- AI Search Optimization Assistant & Builder

## What This Is

A multi-agent rig that helps an internal enterprise team continuously improve their own brand's presence in AI search (ChatGPT, Perplexity, Google AI Overviews, Gemini, Copilot, Claude). It runs in two stages:

- **Stage 1 -- Plan (`/aeo-plan`)**: Research the brand's site + competitors, run a deep AEO analysis, and produce a prioritized, traceable **AEO improvement plan** (`plan/aeo-plan.md`). This is a human-approved gate.
- **Stage 2 -- Build (`/aeo-build`)**: Take the approved plan and selected backlog items, and generate **ready-to-ship artifacts** the team drops into their site/CMS: stacked JSON-LD schema, answer-first content blocks, metadata, an entity knowledge graph, a measurement pack, content briefs, and (optionally) `llms.txt` and an edge-injection config. Everything is validated before an implementation manifest is written.

This is an **internal tool**, not a sales asset. There is no cold outreach, cover letter, pricing, or "deliverable to sell." The output is work product an enterprise team ships.

**AEO is the whole point.** The plan leads with AI search readiness, and every artifact targets being *cited* by answer engines -- not just ranking in a list of links.

## Quick Start

- `/setup` -- Configure the brand profile (domains, entity signals, AEO targets, tech stack, governance). Run once.
- `/aeo-plan` -- Research + AEO analysis -> a prioritized improvement plan (the approval gate).
- `/aeo-build` -- Generate validated artifacts for the plan items the team selected.

## The Agent Team

| Agent | Role | Stage |
|-------|------|-------|
| **Web Crawler** | Crawls the brand's site + key pages via WebFetch (meta, schema, headings, answer-readiness) | Plan |
| **API Caller** | Calls free APIs (PageSpeed, TLS/SSL, W3C, Wayback, WHOIS) via curl for real metrics | Plan |
| **Competitor Researcher** | Benchmarks 2-3 competitors' AEO posture | Plan |
| **AEO Analyst** | Deep-dive AI search readiness assessment -- the star analysis | Plan |
| **AEO Strategist** | Synthesizes research into the prioritized, artifact-mapped improvement plan | Plan |
| **Schema Builder** | Generates stacked, validated JSON-LD per page (+ paste-ready snippets) | Build |
| **Answer-Content Builder** | Answer-first FAQ/definition/comparison/how-to blocks (HTML matched to schema) | Build |
| **Metadata Builder** | Titles, meta descriptions, OG/Twitter tags, freshness fields per page | Build |
| **Entity Builder** | Organization knowledge graph (`sameAs`) + cross-domain fact-consistency report | Build |
| **Measurement Builder** | Tracked prompt set + AI-visibility measurement plan + bot-log monitoring snippet | Build |
| **Content-Brief Builder** | Specs for net-new content the team writes | Build |
| **llms.txt Builder** | Optional `llms.txt`/`llms-full.txt` (labeled low-priority) | Build |
| **Artifact Validator** | **GATE**: validates JSON-LD validity, visible-text parity, answer-first conformance, entity consistency, traceability | Build |
| **Manifest/Report Builder** | Implementation manifest + optional internal stakeholder summary | Build |

## Context Engineering (CRITICAL)

### Rules for the Orchestrator (YOU)

1. **NEVER read skill files yourself.** Skills are for agents, at `.claude/skills/*/SKILL.md`.
2. **NEVER read agent definition files yourself.** Pass the agent file path in the Task prompt so the agent reads its own instructions, at `.claude/agents/*.md`.
3. **Pass file PATHS, not file CONTENTS** to agents. Tell the agent: "Read the file at `<path>`."
4. **Agents write directly to disk.** You do NOT receive generated content back.
5. **Track status, not content.** After an agent finishes, you need: (a) status, (b) file paths, (c) issues. NOT file contents.
6. **The Validator reads from disk.** Pass it the output directory path.
7. **For artifacts, spawn ONE builder per artifact type.** Each spawn writes its own files.
8. **Use max_turns on Task calls.** Web Crawler: 18, API Caller: 15, Competitor Researcher: 12, AEO Analyst: 15, AEO Strategist: 15, Schema Builder: 20, Answer-Content Builder: 20, Metadata Builder: 12, Entity Builder: 12, Measurement Builder: 10, Content-Brief Builder: 15, llms.txt Builder: 8, Artifact Validator: 20, Manifest/Report Builder: 15.

### How to Spawn Agents (Context-Safe Pattern)

CORRECT -- agent reads its own files, writes to disk:
```
Task tool:
  subagent_type: "general-purpose"
  prompt: |
    You are the [Agent Name] for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/<agent>.md

    ## Your Task
    [Brief task description]

    ## Input Files (read these yourself)
    - Brand profile: config/brand-profile.md
    - Plan: output/<brand-slug>/plan/aeo-plan.md
    - [Other inputs]: <path>

    ## Output Files (write these yourself)
    - <path-to-output>

    ## Return Format
    Return ONLY:
    - Status: SUCCESS or FAILED
    - Files created: [list of paths]
    - Issues: [any problems encountered]
```

WRONG -- orchestrator reads everything and pastes it in (doubles context usage).

## Workflow: /aeo-plan (Stage 1)

### Phase 1: Input & Planning
1. Read `config/brand-profile.md` for brand details, domains, AEO targets, competitors, tech stack.
2. Confirm/collect: brand URL(s), competitors (or "auto-find"), priority topics/queries.
3. Create `brand-slug`; create `output/<brand-slug>/` with subdirs: `research/`, `plan/`.
4. Present the plan-run scope, wait for approval.
5. Save run config to `output/<brand-slug>/plan.md` (domains, competitors, scope, date, PageSpeed key if present).

### Phase 2: Research (3 in parallel)
6. Spawn **Web Crawler** (max_turns: 18) -> `research/site-crawl.md`
7. Spawn **API Caller** (max_turns: 15) -> `research/tool-data.md`
8. Spawn **Competitor Researcher** (max_turns: 12) -> `research/competitor-analysis.md`
9. Verify all three exist. For any missing file: re-spawn with max_turns: 10 and a focused prompt; if still missing, write a minimal placeholder noting the gap and proceed.

### Phase 2.5: AEO Analysis
10. Spawn **AEO Analyst** (max_turns: 15) -> `research/aeo-analysis.md`. Verify it exists.

### Phase 3: Plan Synthesis
11. Spawn **AEO Strategist** (max_turns: 15) -> `plan/aeo-plan.md` (prioritized, artifact-mapped backlog with the schema from the `aeo-plan-structure` skill). Verify it exists.

### Phase 4: Approval Gate (MANDATORY)
12. Present the plan summary to the user: overall AEO score, top opportunities, and the P1/P2 buildable items.
13. Ask the user to **review/approve** and **select which item IDs to build** (default: all Buildable P1 + P2).
14. Record the selection in `output/<brand-slug>/plan.md` under a `## Build Selection` section.
15. STOP. Do not build artifacts until the user runs `/aeo-build` (or explicitly approves continuing).

## Workflow: /aeo-build (Stage 2)

Runs only after `plan/aeo-plan.md` exists and items are selected.

### Phase B1: Load Selection
1. Read `output/<brand-slug>/plan.md` (selected IDs) and `plan/aeo-plan.md` (item details).
2. Create `artifacts/` subdirs as needed: `schema/`, `content/`, `metadata/`, `entity/`, `measurement/`, `content-briefs/`, and optionally `edge/`.
3. Group selected items by `Artifact type`.

### Phase B2: Build Artifacts (parallel by type)
4. Spawn **Schema Builder** (max_turns: 20) for `schema` items -> `artifacts/schema/*.json` + snippets + `INDEX.md`
5. Spawn **Answer-Content Builder** (max_turns: 20) for `answer-content` items -> `artifacts/content/*.md` (+ matching HTML)
6. Spawn **Metadata Builder** (max_turns: 12) for `metadata` items -> `artifacts/metadata/meta-tags.md`
7. Spawn **Entity Builder** (max_turns: 12) for `entity` items -> `artifacts/entity/knowledge-graph.json` + `consistency-report.md`
8. Spawn **Measurement Builder** (max_turns: 10) for `measurement` items -> `artifacts/measurement/*`
9. Spawn **Content-Brief Builder** (max_turns: 15) for `content-brief` items -> `artifacts/content-briefs/*.md`
10. If `llms-txt` selected: spawn **llms.txt Builder** (max_turns: 8) -> `artifacts/llms.txt` (+ `llms-full.txt`)
11. If `edge-injection` selected: have the Schema Builder also emit `artifacts/edge/` config.
12. Coordinate parity: Schema Builder and Answer-Content Builder must produce matched FAQ/HowTo pairs. Spawn Answer-Content first or pass shared item details so the visible text and JSON-LD match exactly.

### Phase B3: Validation Gate (MANDATORY)
13. Spawn **Artifact Validator** (model: opus, max_turns: 20). It checks every artifact (see checklist below).
14. If APPROVED: proceed. If BLOCKED: re-spawn the responsible builder(s) with the specific issues. Max 2 iterations. Malformed JSON-LD must be fixed or dropped -- never shipped.

### Phase B4: Manifest & Output
15. Spawn **Manifest/Report Builder** (max_turns: 15) -> `artifacts/README.md` (implementation manifest) + optional `report/internal-summary.*`.
16. Verify all expected artifact files exist.
17. Generate/update `output/<brand-slug>/README.md` (table of contents + deploy checklist).
18. Report results: what was built, where it goes, and how to deploy + measure.

## Validation Gate Checklist (Artifact Validator Owns This)

### Schema
- [ ] Every `.json` artifact is valid JSON (parses) and schema.org-conformant
- [ ] Key pages use a stacked `@graph` (not isolated single types)
- [ ] FAQ/HowTo/Review schema has a matching visible-HTML block (parity)
- [ ] No fabricated ratings/counts/credentials -- all trace to brand profile or site evidence
- [ ] Cross-referenced `@id` values resolve

### Content
- [ ] Answer-first: direct 40-60 word answer at the top of each block
- [ ] Headings phrased as real user questions; short paragraphs
- [ ] Visible FAQ/HowTo text matches the corresponding JSON-LD exactly
- [ ] Brand voice/style adhered to; no fabricated claims

### Entity & Consistency
- [ ] Organization knowledge graph present with accurate `sameAs`
- [ ] Cross-domain facts (name, description, stats) are consistent; contradictions flagged

### Measurement
- [ ] Priority prompt set present and specific to the brand
- [ ] Measurement plan names KPIs and cadence; bot-log snippet included

### Traceability & Completeness
- [ ] Every artifact references the plan item ID (`AEO-xxx`) it satisfies
- [ ] All selected Buildable items have a corresponding artifact
- [ ] Manifest maps each artifact to its target page + deploy method
- [ ] `llms.txt` (if present) labeled optional/low-priority

## Output Structure

```
output/<brand-slug>/
  README.md                          # Table of contents + deploy checklist
  plan.md                            # Run config + build selection
  research/
    site-crawl.md                    # Manual crawl analysis
    tool-data.md                     # Raw API data
    competitor-analysis.md           # Competitor benchmarking
    aeo-analysis.md                  # AEO deep-dive (the centerpiece)
  plan/
    aeo-plan.md                      # Prioritized improvement plan (APPROVAL GATE)
  artifacts/
    README.md                        # Implementation manifest
    schema/                          # *.json + *.html snippets + INDEX.md
    content/                         # answer-first FAQ/definitions/comparisons/how-to (.md + .html)
    metadata/                        # meta-tags.md (per-page title/description/OG + freshness)
    entity/                          # knowledge-graph.json + consistency-report.md
    measurement/                     # prompt-set.md + measurement-plan.md + bot-log-snippet
    content-briefs/                  # *.md
    llms.txt, llms-full.txt          # optional, low-priority
    edge/                            # optional Cloudflare Worker / injection config
  report/
    internal-summary.*               # optional stakeholder summary
```

## Skills (Domain Knowledge)

| Skill | Location | Used By |
|-------|----------|---------|
| AEO Optimization | `.claude/skills/aeo-optimization/SKILL.md` | AEO Analyst, AEO Strategist, builders, Validator |
| Technical SEO | `.claude/skills/technical-seo/SKILL.md` | Web Crawler, API Caller |
| Content SEO | `.claude/skills/content-seo/SKILL.md` | AEO Strategist, Answer-Content/Content-Brief Builders |
| Local SEO | `.claude/skills/local-seo/SKILL.md` | Competitor Researcher (optional for local brands) |
| Schema Authoring | `.claude/skills/schema-authoring/SKILL.md` | Schema Builder, Entity Builder, Metadata Builder, Validator |
| llms.txt Authoring | `.claude/skills/llms-txt/SKILL.md` | llms.txt Builder |
| AEO Plan Structure | `.claude/skills/aeo-plan-structure/SKILL.md` | AEO Strategist, Manifest/Report Builder |
| Artifact QA Checklist | `.claude/skills/qas-checklist/SKILL.md` | Artifact Validator (ONLY skill the Validator reads) |

## File Reference

| What | Where |
|------|-------|
| This file (orchestration hub) | `CLAUDE.md` |
| Commands | `.claude/commands/aeo-plan.md`, `aeo-build.md`, `setup.md` |
| Plan agents | `.claude/agents/web-crawler.md`, `api-caller.md`, `competitor-researcher.md`, `aeo-analyst.md`, `aeo-strategist.md` |
| Build agents | `.claude/agents/schema-builder.md`, `answer-content-builder.md`, `metadata-builder.md`, `entity-builder.md`, `measurement-builder.md`, `content-brief-builder.md`, `llms-txt-builder.md`, `artifact-validator.md`, `manifest-builder.md` |
| Skills | `.claude/skills/aeo-optimization/`, `technical-seo/`, `content-seo/`, `local-seo/`, `schema-authoring/`, `llms-txt/`, `aeo-plan-structure/`, `qas-checklist/` |
| Brand config | `config/brand-profile.md` (template: `config/brand-profile.example.md`) |
| Output | `output/<brand-slug>/` |
