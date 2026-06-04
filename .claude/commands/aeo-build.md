# /aeo-build -- Generate AEO Artifacts (Stage 2)

Take the approved AEO improvement plan and the selected backlog items, and generate ready-to-ship artifacts the team deploys. Validate everything, then write an implementation manifest.

## Prerequisite

`/aeo-plan` has run: `output/<brand-slug>/plan/aeo-plan.md` exists and `output/<brand-slug>/plan.md` has a `## Build Selection`. If no selection is recorded, ask the user which item IDs to build (default: all Buildable P1 + P2).

## Input: $ARGUMENTS

Optionally a brand-slug and/or a list of item IDs to build. If absent, use the recorded selection.

## Context Rules (MANDATORY)

Follow CLAUDE.md context engineering: pass file PATHS to agents, agents write to disk, you track status only. You MAY read `plan/aeo-plan.md` and `plan.md` (gate artifacts) to route work; do NOT read agent/skill files.

## Pipeline

### Phase B1: Load Selection & Route
1. Read `output/<brand-slug>/plan.md` (selected IDs) and `output/<brand-slug>/plan/aeo-plan.md` (item details).
2. Group selected Buildable items by `Artifact type` (`schema`, `answer-content`, `metadata`, `entity`, `measurement`, `content-brief`, `llms-txt`, `edge-injection`). `off-site` items are Spec-only -- no builder.
3. Create needed subdirs under `output/<brand-slug>/artifacts/`.

### Phase B2: Build (order matters for parity)

First spawn **Answer-Content Builder** (max_turns: 20) so visible text exists before schema mirrors it:
```
Task tool:
  description: "Build answer-first content blocks"
  subagent_type: "general-purpose"
  max_turns: 20
  prompt: |
    You are the Answer-Content Builder for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/answer-content-builder.md
    ## Input Files (read these yourself)
    - Brand profile: config/brand-profile.md
    - Plan: output/<brand-slug>/plan/aeo-plan.md
    - Run config: output/<brand-slug>/plan.md
    - AEO Analysis: output/<brand-slug>/research/aeo-analysis.md
    - Site Crawl: output/<brand-slug>/research/site-crawl.md
    ## Output Files (write these yourself)
    - output/<brand-slug>/artifacts/content/*.md and *.html (for each answer-content item)
    ## Return Format: Status, Files created, Issues.
```

Then spawn the remaining builders IN PARALLEL (only those with selected items):

- **Schema Builder** (max_turns: 20) -> `artifacts/schema/` (+ `artifacts/edge/` if edge-injection selected). Tell it to mirror the answer content for parity.
- **Metadata Builder** (max_turns: 12) -> `artifacts/metadata/meta-tags.md`
- **Entity Builder** (max_turns: 12) -> `artifacts/entity/knowledge-graph.json` + `consistency-report.md`
- **Measurement Builder** (max_turns: 10) -> `artifacts/measurement/*`
- **Content-Brief Builder** (max_turns: 15) -> `artifacts/content-briefs/*.md`
- **llms.txt Builder** (max_turns: 8, only if `llms-txt` selected) -> `artifacts/llms.txt`

Each spawn follows the context-safe pattern: agent reads its own instructions at `.claude/agents/<agent>.md` and the same input files (brand profile, plan, run config, relevant research), writes its own outputs, returns Status/Files/Issues.

### Phase B3: Validation Gate (MANDATORY)
Spawn **Artifact Validator** (model: opus, max_turns: 20):
```
Task tool:
  description: "Validate artifacts"
  subagent_type: "general-purpose"
  model: "opus"
  max_turns: 20
  prompt: |
    You are the Artifact Validator for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/artifact-validator.md
    ## Inputs (read these yourself)
    - Plan + selection: output/<brand-slug>/plan/aeo-plan.md, output/<brand-slug>/plan.md
    - All artifacts: output/<brand-slug>/artifacts/
    - Brand profile: config/brand-profile.md
    - Research: output/<brand-slug>/research/
    ## Return Format
    ## VALIDATION: APPROVED (or BLOCKED with specific issues)
```
- If APPROVED: proceed.
- If BLOCKED: re-spawn the responsible builder(s) with the specific issues. Max 2 iterations. Malformed JSON-LD or parity failures MUST be fixed or the artifact dropped before proceeding.

### Phase B4: Manifest & Output
Spawn **Manifest/Report Builder** (max_turns: 15):
```
Task tool:
  description: "Build implementation manifest"
  subagent_type: "general-purpose"
  max_turns: 15
  prompt: |
    You are the Manifest/Report Builder for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/manifest-builder.md
    ## Inputs (read these yourself)
    - Brand profile: config/brand-profile.md
    - Plan + selection: output/<brand-slug>/plan/aeo-plan.md, output/<brand-slug>/plan.md
    - All artifacts: output/<brand-slug>/artifacts/
    - AEO Analysis: output/<brand-slug>/research/aeo-analysis.md
    ## Output Files (write these yourself)
    - output/<brand-slug>/artifacts/README.md (manifest)
    - output/<brand-slug>/report/internal-summary.md (optional)
    ## Return Format: Status, Files created, Issues.
```

Then:
1. Verify all expected artifact files exist for the selected items.
2. Generate/update `output/<brand-slug>/README.md` (table of contents + deploy checklist).
3. Report results:
```
AEO artifacts built for [Brand].

- Artifacts: output/<brand-slug>/artifacts/
- Manifest (how to deploy): output/<brand-slug>/artifacts/README.md
- Internal summary: output/<brand-slug>/report/internal-summary.md

Next:
1. Deploy schema + matching content blocks together (see manifest).
2. Apply metadata + entity graph (site-wide).
3. Stand up the measurement prompt set; re-run /aeo-plan quarterly.
```
