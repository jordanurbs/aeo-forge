# /aeo-build -- Generate AEO Artifacts (Stage 2)

Take the approved AEO improvement plan and the selected backlog items, and generate ready-to-ship artifacts the team deploys. Validate everything, then write an implementation manifest.

## Prerequisite

`/aeo-plan` has run: `output/<brand-slug>/plan/aeo-plan.md` exists and `output/<brand-slug>/plan.md` has a `## Build Selection`. If no selection is recorded, ask the user which item IDs to build (default: all Buildable P1 + P2).

## Input: $ARGUMENTS

Optionally a brand-slug and/or a list of item IDs to build. If absent, use the recorded selection.

## Context Rules (MANDATORY)

Follow CLAUDE.md context engineering: pass file PATHS to agents, agents write to disk, you track status only. You MAY read `plan/aeo-plan.md` and `plan.md` (gate artifacts) to route work; do NOT read agent/skill files.
Use absolute workspace-root-resolved paths in Task prompts, verify every expected output file after each agent returns, and retry once with the exact missing path before declaring a gap or blocker.

## Pipeline

### Phase B1: Load Selection & Route
1. Read `output/<brand-slug>/plan.md` (selected IDs) and `output/<brand-slug>/plan/aeo-plan.md` (item details).
2. Group selected Buildable items by `Artifact type` (`schema`, `answer-content`, `metadata`, `entity`, `measurement`, `content-brief`, `llms-txt`, `edge-injection`). `off-site` items are Spec-only -- no builder.
3. Check `Confidence state` or legacy `Run state` in `output/<brand-slug>/plan.md`. If it is `BLOCKED`, stop. If it is `PARTIAL_CONFIDENCE`, continue only after reporting the evidence gaps that will carry into the artifacts.
4. Create needed subdirs under `output/<brand-slug>/artifacts/`.
5. Write `output/<brand-slug>/artifacts/build-route.md` before spawning builders. Include selected IDs grouped by artifact type, responsible builder, expected output paths, `Build state: BUILD_IN_PROGRESS`, confidence state, run type/fixture mode, and the canonical entity contract (`Organization @id`, canonical page IDs, Person `@id`s, verified `sameAs`, and claims requiring approval).

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
    - Brand profile: /absolute/path/to/config/brand-profile.md
    - Plan: /absolute/path/to/output/<brand-slug>/plan/aeo-plan.md
    - Run config: /absolute/path/to/output/<brand-slug>/plan.md
    - Build route: /absolute/path/to/output/<brand-slug>/artifacts/build-route.md
    - AEO Analysis: /absolute/path/to/output/<brand-slug>/research/aeo-analysis.md
    - Site Crawl: /absolute/path/to/output/<brand-slug>/research/site-crawl.md
    ## Output Files (write these yourself)
    - /absolute/path/to/output/<brand-slug>/artifacts/content/*.md and *.html (for each answer-content item)
    ## Quality Requirements
    - Include the selected plan item ID (`AEO-xxx`) in every artifact.
    - Include a short evidence/source note for material claims using these labels: brand-profile, site-crawl, tool-data, competitor-analysis, aeo-analysis, inference.
    - Preserve fixture/sample-run boundaries from the run config.
    ## Return Format: Status, Files created, Issues.
```
After it returns, verify the expected answer-content files exist. If not, retry once with the exact missing paths.

Then spawn the remaining builders IN PARALLEL (only those with selected items):

- **Schema Builder** (max_turns: 20) -> `artifacts/schema/` (+ `artifacts/edge/` if edge-injection selected). Tell it to mirror the answer content for parity.
- **Metadata Builder** (max_turns: 12) -> `artifacts/metadata/meta-tags.md`
- **Entity Builder** (max_turns: 12) -> `artifacts/entity/knowledge-graph.json` + `consistency-report.md`
- **Measurement Builder** (max_turns: 10) -> `artifacts/measurement/*`
- **Content-Brief Builder** (max_turns: 15) -> `artifacts/content-briefs/*.md`
- **llms.txt Builder** (max_turns: 8, only if `llms-txt` selected) -> `artifacts/llms.txt`

Each spawn follows the context-safe pattern: agent reads its own instructions at `.claude/agents/<agent>.md` and the same input files (brand profile, plan, run config, build route, relevant research), writes its own outputs, returns Status/Files/Issues. Every builder prompt must require plan item IDs and source labels in its artifacts.

Schema/entity consistency requirements for builder prompts:
- Schema Builder and Entity Builder must use the canonical entity contract from `artifacts/build-route.md`.
- Schema Builder must not emit unverified `sameAs`, ratings, counts, certifications, or security claims.
- Schema Builder must avoid non-standard properties such as `WebPage.primaryEntity`; use valid schema.org properties such as `mainEntity`, `about`, `isPartOf`, and `publisher`.
- FAQPage/HowTo schema must have a same-stem visible companion or an explicitly linked visible content artifact so deterministic parity checks can find it.

After each parallel builder returns, verify every expected file for its selected artifact type exists. If any expected file is missing, retry that builder once with the exact missing path. If still missing, set `Build state: BUILD_BLOCKED` unless the item is explicitly optional and dropped in the manifest.

### Phase B3: Validation Gate (MANDATORY)
First run deterministic checks if the script is available:
```
python3 scripts/validate-artifacts.py output/<brand-slug> --write-report
```
Treat JSON parse failures, missing selected item coverage, per-artifact missing `AEO-xxx` references, missing source labels, non-stacked page schema, non-standard schema properties, inconsistent entity `@id` values, missing visible FAQ/HowTo companions, and detected schema/visible-text parity mismatches as `BUILD_BLOCKED`.

Then spawn **Artifact Validator** (max_turns: 20):
```
Task tool:
  description: "Validate artifacts"
  subagent_type: "general-purpose"
  max_turns: 20
  prompt: |
    You are the Artifact Validator for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/artifact-validator.md
    ## Inputs (read these yourself)
    - Plan + selection: /absolute/path/to/output/<brand-slug>/plan/aeo-plan.md, /absolute/path/to/output/<brand-slug>/plan.md
    - Build route: /absolute/path/to/output/<brand-slug>/artifacts/build-route.md
    - Deterministic validation report: /absolute/path/to/output/<brand-slug>/artifacts/validation.md
    - All artifacts: /absolute/path/to/output/<brand-slug>/artifacts/
    - Brand profile: /absolute/path/to/config/brand-profile.md
    - Research: /absolute/path/to/output/<brand-slug>/research/
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
    - Brand profile: /absolute/path/to/config/brand-profile.md
    - Plan + selection: /absolute/path/to/output/<brand-slug>/plan/aeo-plan.md, /absolute/path/to/output/<brand-slug>/plan.md
    - Build route: /absolute/path/to/output/<brand-slug>/artifacts/build-route.md
    - Deterministic validation report: /absolute/path/to/output/<brand-slug>/artifacts/validation.md
    - All artifacts: /absolute/path/to/output/<brand-slug>/artifacts/
    - AEO Analysis: /absolute/path/to/output/<brand-slug>/research/aeo-analysis.md
    ## Output Files (write these yourself)
    - /absolute/path/to/output/<brand-slug>/artifacts/README.md (manifest)
    - /absolute/path/to/output/<brand-slug>/report/internal-summary.md (optional)
    ## Return Format: Status, Files created, Issues.
```

Then:
1. Verify all expected artifact files exist for the selected items using `artifacts/build-route.md` and the deterministic validator.
2. Generate/update `output/<brand-slug>/README.md` (table of contents + deploy checklist).
3. Update `Build state` in `output/<brand-slug>/plan.md` or `artifacts/build-route.md`: `BUILD_COMPLETE`, `BUILD_PARTIAL`, or `BUILD_BLOCKED`.
4. Report results:
```
AEO artifacts built for [Brand].

- Confidence state: COMPLETE or PARTIAL_CONFIDENCE
- Build state: BUILD_COMPLETE or BUILD_PARTIAL
- Artifacts: output/<brand-slug>/artifacts/
- Manifest (how to deploy): output/<brand-slug>/artifacts/README.md
- Internal summary: output/<brand-slug>/report/internal-summary.md
- Validation report: output/<brand-slug>/artifacts/validation.md
- Evidence gaps: [none, or inherited gaps from plan.md]

Next:
1. Deploy schema + matching content blocks together (see manifest).
2. Apply metadata + entity graph (site-wide).
3. Stand up the measurement prompt set; re-run /aeo-plan quarterly.
```
