---
name: Artifact QA Checklist
version: 2.0.0
description: Consolidated validation criteria for the Artifact Validator agent -- JSON-LD validity, schema/visible-text parity, answer-first conformance, entity consistency, measurement completeness, and plan traceability. This is the ONLY skill file the Validator needs to read.
---

# Artifact QA Checklist (Enterprise AEO Builder)

Everything needed to validate the build-stage artifacts. You do NOT need the individual domain skills -- all criteria are consolidated here.

## Reading / Checking Strategy (CRITICAL)

1. **Selection first:** read `plan/aeo-plan.md` (item details) and `plan.md` (`## Build Selection`) to know which item IDs must have artifacts.
2. **Validate machine-readable artifacts before prose:** JSON first (schema + entity), then content parity, then everything else.
3. **Use Bash/Grep before deep reading:**
   - `python3 -c "import json,sys; json.load(open(sys.argv[1]))" <file>` for every JSON file.
   - Grep FAQ/HowTo answer text from schema against `artifacts/content/` files for parity.
   - Grep for `{{` placeholders and for plan item IDs (`AEO-`) to confirm traceability.

---

## Hard Gates (any failure = CRITICAL block)

1. **Valid JSON-LD.** Every `.json` in `artifacts/schema/` and `artifacts/entity/` parses. Malformed JSON-LD is worse than none -- fix or drop.
2. **Schema/visible-text parity.** Every `FAQPage`/`HowTo`/`QAPage`/`Review` node's text appears verbatim as visible content in `artifacts/content/`.
3. **No fabricated facts.** Ratings, counts, credentials, `sameAs` trace to the brand profile or research evidence.
4. **Completeness.** Every selected Buildable item ID has at least one corresponding artifact.
5. **No placeholders.** No `{{...}}` or `[TODO]` left in any shipped artifact.

---

## Schema Checks

- [ ] Valid JSON + schema.org-conformant (`@type`, required props, ISO-8601 dates, absolute URLs)
- [ ] Key pages use a stacked `@graph` (Organization/WebPage/BreadcrumbList + primary type + FAQ/HowTo where applicable)
- [ ] `@id` cross-references resolve (e.g., WebPage.about -> Organization @id)
- [ ] Organization `@id` matches the Entity Builder's knowledge graph
- [ ] `dateModified` present where relevant
- [ ] `.html` snippet present for each `.json`; `INDEX.md` maps files -> page URLs -> plan item IDs

## Content Checks

- [ ] Answer-first: direct 40-60 word answer leads each block
- [ ] Headings phrased as real user questions; short paragraphs (2-4 sentences)
- [ ] FAQ/HowTo visible text matches the corresponding schema exactly (parity)
- [ ] Brand voice applied; no generic filler; claims attributed
- [ ] Each file headers its plan item ID + target page

## Metadata Checks

- [ ] Per-page title (~50-60 chars), description (~140-160 chars), OG/Twitter, canonical, freshness
- [ ] Consistent with schema + entity facts (no contradictions)
- [ ] Answer/intent-led, not keyword-stuffed

## Entity & Consistency Checks

- [ ] `knowledge-graph.json` valid; canonical Organization (+ Person nodes) with accurate `sameAs`
- [ ] `consistency-report.md` present; contradictions across profile/site/domains listed with recommended canonical values
- [ ] No unverifiable `sameAs` or invented stats

## Measurement Checks

- [ ] `prompt-set.md` uses the brand's real target queries (not generic), tagged by buyer-journey stage
- [ ] `measurement-plan.md` names KPIs (citation frequency, AI Overview presence, AI-referred sessions, crawler access) + cadence
- [ ] `bot-log-snippet.md` lists AI user agents and a verification method

## Content-Brief Checks

- [ ] One brief per selected `content-brief` item; includes target query, answer-first summary, question-form outline, schema to apply, citation hooks, success criteria

## llms.txt Checks (if present)

- [ ] Valid format (H1 + `>` summary + annotated H2 link groups; absolute URLs)
- [ ] Labeled optional/low-priority; not presented as a ranking lever
- [ ] Deploy location noted (site root)

## Traceability & Manifest Readiness

- [ ] Every artifact references its plan item ID (`AEO-xxx`)
- [ ] All selected Buildable items covered; gaps explicitly noted
- [ ] `off-site`/Spec-only items are NOT expected to have generated files

---

## Severity Levels

- **CRITICAL** (block): invalid JSON, parity failure, fabricated facts, missing artifact for a selected item, broken `@id` references, placeholders in shipped artifacts.
- **IMPORTANT** (note, may not block): weak answer-first conformance, thin entity graph, generic content, missing freshness fields, inconsistent metadata.

Do NOT flag minor stylistic preferences. Focus on the top 5-10 most impactful issues. Block on any CRITICAL.

## Common Failure Patterns (Grep/Bash for These)

| Pattern | Meaning | Check |
|---------|---------|-------|
| JSON parse error | Malformed JSON-LD (worse than none) | `python3 -c "import json,...` per file |
| Schema text not in content/ | Parity violation | Grep answer text against content files |
| `{{` in artifacts | Unreplaced placeholder | `Grep "{{"` in artifacts/ |
| No `AEO-` reference | Lost traceability | Grep `AEO-` per artifact |
| Invented rating/count | Fabricated data | Cross-check brand-profile.md + research |
| `sameAs` 404 | Unverifiable entity link | Spot-check URLs |
