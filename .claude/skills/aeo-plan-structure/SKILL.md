---
name: AEO Plan Structure
version: 1.0.0
description: Structure and format for the enterprise AEO improvement plan (the planning-stage deliverable), the backlog item schema with artifact mapping and traceability, scoring display formats, and internal stakeholder reporting conventions. Used by the AEO Strategist, Manifest/Report Builder, and Artifact Validator agents.
---

# AEO Plan Structure Skill

Defines the structure of the AEO improvement plan -- the human-approved gate between the PLAN stage and the BUILD stage. This is an internal working document for an enterprise team, not a sales deliverable. It must be specific, prioritized, and traceable: every recommendation links to evidence and to the artifact that will implement it.

## The Plan Is the Gate

`plan/aeo-plan.md` is reviewed and approved by a human before any artifacts are built. The team selects which backlog items to build. The plan must therefore be:
- **Actionable:** each item is a concrete change, not a theme.
- **Traceable:** each item cites the evidence (research finding) that justifies it.
- **Buildable:** each item names the artifact type that implements it, so `/aeo-build` can route it.
- **Prioritized:** ranked by impact vs effort so the team can choose confidently.

## Backlog Item Schema (REQUIRED for every item)

Each plan item is a row/block with these fields:

| Field | Meaning |
|-------|---------|
| `ID` | Stable identifier (e.g., `AEO-001`) used by artifacts to reference back |
| `Title` | Concrete action ("Add stacked FAQPage+Article schema to /pricing") |
| `Evidence` | The specific finding that justifies it (cite research file + observation) |
| `Target pages` | The exact URLs/templates affected |
| `Artifact type` | `schema` / `answer-content` / `metadata` / `entity` / `measurement` / `content-brief` / `llms-txt` / `edge-injection` / `off-site` |
| `AEO criterion` | Which criterion it improves (Structured Data, Answer-Ready, Entity, Topical, Citation-Worthiness, Visibility) |
| `Impact` | High / Medium / Low (expected lift to AI citation) |
| `Effort` | Quick Win / Medium / High |
| `Owner` | Suggested role (Eng / Content / SEO / Marketing) |
| `Buildable` | Yes (rig generates an artifact) / Spec-only (off-site, team executes) |

`off-site` items (editorial mentions, Wikipedia/Wikidata, directory consistency) are `Spec-only` -- the plan describes them but `/aeo-build` does not generate a file for them.

## Plan Document Structure

```markdown
# AEO Improvement Plan: [Brand Name]

## AI Search Readiness: [Grade] ([Score]/10)
[2-3 sentence summary of where the brand stands and the single biggest opportunity.]

| Criterion | Score | Weight |
|-----------|-------|--------|
| Structured Data for AI | [X]/10 | 15% |
| Answer-Ready Content | [X]/10 | 20% |
| Entity Authority | [X]/10 | 20% |
| Topical Authority | [X]/10 | 20% |
| Citation-Worthiness | [X]/10 | 15% |
| AI Search Visibility | [X]/10 | 10% |
| **Overall** | **[X.X]/10** | **[Grade]** |

## Competitive Position
[Short table: brand vs competitors on overall AEO + key criteria, from competitor analysis.]

## Buyer-Journey Citation Map
[For B2B/enterprise: target answers the brand should own at pre-funnel / TOFU / MOFU / BOFU.]

## Prioritized Backlog

### P1 -- Quick Wins (High Impact, Low Effort)
| ID | Title | Evidence | Target pages | Artifact type | Criterion | Impact | Effort | Owner | Buildable |
|----|-------|----------|--------------|---------------|-----------|--------|--------|-------|-----------|
| AEO-001 | ... | ... | ... | schema | Structured Data | High | Quick Win | Eng | Yes |

### P2 -- Strategic Priorities (High Impact, Medium Effort)
[same columns]

### P3 -- Major Initiatives (High Impact, High Effort)
[same columns]

### P4 -- Easy Improvements (Medium Impact, Low Effort)
[same columns]

### P5 -- Backlog
[same columns]

## Measurement Plan
- Priority prompt set to track (the real queries this brand should be cited for).
- KPIs: citation frequency, AI Overview presence, AI-referred sessions, crawler access.
- Re-evaluation cadence (quarterly recommended).

## Build Selection
[Checklist the team marks to choose which IDs `/aeo-build` should generate artifacts for. Default: all P1 + P2 Buildable items.]
```

## Scoring Display

Use the AEO 1-10 scale and grade mapping from the `aeo-optimization` skill. For quick visual scanning:

```
AI Search Readiness: C+ (5.4/10)

Structured Data:      ██░░░░░░░░  3/10  -- No FAQ schema; Organization only
Answer-Ready Content: ████░░░░░░  5/10  -- Some FAQ text, not answer-first
Entity Authority:     ██████░░░░  7/10  -- Strong profiles, no sameAs graph
Topical Authority:    ████░░░░░░  5/10  -- Service pages only, no clusters
Citation-Worthiness:  █████░░░░░  6/10  -- Professional, no original data
AI Search Visibility: ████░░░░░░  5/10  -- Limited presence in tracked prompts
```

| Score | Grade | Label |
|-------|-------|-------|
| 9.0-10.0 | A+ | AI Search Leader |
| 8.0-8.9 | A | AI Search Ready |
| 7.0-7.9 | B+ | Above Average |
| 6.0-6.9 | B | Moderate Readiness |
| 5.0-5.9 | C+ | Below Average |
| 4.0-4.9 | C | Significant Gaps |
| 3.0-3.9 | D | Major Gaps |
| 1.0-2.9 | F | AI Search Invisible |

## Internal Reporting Tone

This is an internal enterprise document. Write for a mixed audience of marketers and engineers:
- **Direct and specific.** "Add FAQPage schema to /pricing with the 6 questions below" -- not "improve structured data."
- **Evidence-led.** Every claim references a finding. No generic statements.
- **No sales language.** No pricing, no outreach hooks, no "did the work first." This is a build plan.
- **Honest about effort and uncertainty.** Note where impact is high-confidence vs experimental (e.g., `llms.txt`).

## Optional Internal Stakeholder Summary

A short HTML or Markdown summary (`report/internal-summary.*`) for leadership: overall score, top 5 opportunities, what will be built this cycle, and the measurement plan. No branding-for-sale, no cover letter, no follow-up emails.
