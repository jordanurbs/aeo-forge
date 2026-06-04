# /aeo-plan -- AEO Improvement Plan (Stage 1)

Research the brand's AI search readiness and produce a prioritized, traceable, artifact-mapped improvement plan. The plan is a human-approved gate: after it's generated, the team reviews it and selects which items to build with `/aeo-build`.

## Input: $ARGUMENTS

If no arguments, read `config/brand-profile.md` first, then confirm/collect:
1. Brand URL(s) (default: primary domain from profile)
2. Competitors (URLs or "auto-find"; default from profile)
3. Priority topics / target AI queries (default from profile)
4. Priority URLs and source-of-truth pages (default from profile, if provided)

## Context Rules (MANDATORY)

Follow the Context Engineering rules in CLAUDE.md:
- Do NOT read agent or skill files yourself
- Pass file PATHS to agents, not contents
- Agents write to disk directly; you track status and file paths only
- Prefer absolute workspace-root-resolved output paths in Task prompts
- Verify every expected output file after each agent returns; retry once with the exact missing path before proceeding

## Pipeline

### Phase 1: Input & Setup
1. Read `config/brand-profile.md`.
2. Confirm brand URL(s), priority URLs, competitors, and priority topics/queries with the user.
3. Create `brand-slug` (lowercase, hyphens). Create `output/<brand-slug>/` with subdirs `research/` and `plan/`.
4. Present the plan-run scope and wait for approval.
5. Save run config to `output/<brand-slug>/plan.md`: domains, priority URLs, source-of-truth pages, competitor URLs, priority queries, date, PageSpeed API key (if in profile), `Run type` (`production`, `fixture`, or `sample dry run`), `Confidence state: COMPLETE`, and `Build state: NOT_STARTED`.

### Phase 2: Research (3 in parallel)

6. Spawn **Web Crawler** (max_turns: 18):
```
Task tool:
  description: "Crawl brand site via WebFetch"
  subagent_type: "general-purpose"
  max_turns: 18
  prompt: |
    You are the Web Crawler for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/web-crawler.md

    ## Your Task
    Crawl the brand's site and key pages via WebFetch to extract technical + answer-readiness signals (meta, headings, schema, images, crawlability, answer-first formatting).

    ## Input Files (read these yourself)
    - Brand profile: /absolute/path/to/config/brand-profile.md
    - Run config: /absolute/path/to/output/<brand-slug>/plan.md

    ## Output Files (write these yourself)
    - /absolute/path/to/output/<brand-slug>/research/site-crawl.md

    ## Return Format
    Return ONLY: Status, Files created, Issues.
```

7. Spawn **API Caller** IN PARALLEL (max_turns: 15):
```
Task tool:
  description: "Call free technical APIs"
  subagent_type: "general-purpose"
  max_turns: 15
  prompt: |
    You are the API Caller for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/api-caller.md

    ## Your Task
    Call PageSpeed, TLS/SSL, W3C, Wayback, WHOIS via curl for real metrics.

    ## Input Files (read these yourself)
    - Run config: /absolute/path/to/output/<brand-slug>/plan.md

    ## Output Files (write these yourself)
    - /absolute/path/to/output/<brand-slug>/research/tool-data.md

    ## Return Format
    Return ONLY: Status, Files created, Issues.
```

8. Spawn **Competitor Researcher** IN PARALLEL (max_turns: 12):
```
Task tool:
  description: "Benchmark competitors' AEO"
  subagent_type: "general-purpose"
  max_turns: 12
  prompt: |
    You are the Competitor Researcher for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/competitor-researcher.md

    ## Your Task
    Find/analyze 2-3 competitors and benchmark their AEO posture on the brand's priority topics.

    ## Input Files (read these yourself)
    - Brand profile: /absolute/path/to/config/brand-profile.md
    - Run config: /absolute/path/to/output/<brand-slug>/plan.md

    ## Output Files (write these yourself)
    - /absolute/path/to/output/<brand-slug>/research/competitor-analysis.md

    ## Return Format
    Return ONLY: Status, Files created, Issues.
```

9. Verify `research/site-crawl.md`, `research/tool-data.md`, `research/competitor-analysis.md` exist at the exact expected paths.
10. **Recovery:** for any missing file, re-spawn the responsible agent (max_turns: 10) with: "Your previous run returned before the expected file was available. Read your agent instructions at [absolute agent path] and write output to [absolute missing output path] immediately." If still missing, write a minimal placeholder noting the gap, update `output/<brand-slug>/plan.md` to `Confidence state: PARTIAL_CONFIDENCE`, and proceed only if the remaining evidence can support a useful plan.
11. Maintain a `## Evidence Gaps` section in `output/<brand-slug>/plan.md` listing failed/missing research inputs, API rate-limit failures, crawl blocks, and competitor coverage gaps.

### Phase 2.5: AEO Analysis

12. Spawn **AEO Analyst** (max_turns: 15):
```
Task tool:
  description: "Deep-dive AEO analysis"
  subagent_type: "general-purpose"
  max_turns: 15
  prompt: |
    You are the AEO Analyst for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/aeo-analyst.md

    ## Your Task
    Produce the centerpiece AI search readiness assessment.

    ## Input Files (read these yourself)
    - Brand profile: /absolute/path/to/config/brand-profile.md
    - Run config: /absolute/path/to/output/<brand-slug>/plan.md
    - Site Crawl: /absolute/path/to/output/<brand-slug>/research/site-crawl.md
    - Tool Data: /absolute/path/to/output/<brand-slug>/research/tool-data.md
    - Competitor Analysis: /absolute/path/to/output/<brand-slug>/research/competitor-analysis.md

    ## Output Files (write these yourself)
    - /absolute/path/to/output/<brand-slug>/research/aeo-analysis.md

    ## Return Format
    Return ONLY: Status, Files created, Issues.
```

13. Verify `research/aeo-analysis.md` exists. If missing after one focused retry, set `Confidence state: BLOCKED` and stop; do not synthesize a plan without the AEO analysis.

### Phase 3: Plan Synthesis

14. Spawn **AEO Strategist** (max_turns: 15):
```
Task tool:
  description: "Synthesize AEO improvement plan"
  subagent_type: "general-purpose"
  max_turns: 15
  prompt: |
    You are the AEO Strategist for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/aeo-strategist.md

    ## Your Task
    Synthesize all research into /absolute/path/to/output/<brand-slug>/plan/aeo-plan.md -- a prioritized, traceable, artifact-mapped backlog using the aeo-plan-structure skill. Every plan item must include evidence/source labels: brand-profile, site-crawl, tool-data, competitor-analysis, aeo-analysis, or inference.

    ## Input Files (read these yourself)
    - Brand profile: /absolute/path/to/config/brand-profile.md
    - Run config: /absolute/path/to/output/<brand-slug>/plan.md
    - Site Crawl: /absolute/path/to/output/<brand-slug>/research/site-crawl.md
    - Tool Data: /absolute/path/to/output/<brand-slug>/research/tool-data.md
    - Competitor Analysis: /absolute/path/to/output/<brand-slug>/research/competitor-analysis.md
    - AEO Analysis: /absolute/path/to/output/<brand-slug>/research/aeo-analysis.md

    ## Output Files (write these yourself)
    - /absolute/path/to/output/<brand-slug>/plan/aeo-plan.md

    ## Return Format
    Return ONLY: Status, Files created, Issues.
```

15. Verify `plan/aeo-plan.md` exists at the exact expected path.

### Phase 4: Approval Gate (MANDATORY)

16. Read `plan/aeo-plan.md` enough to summarize for the user (you MAY read this file -- it is the gate artifact, not an agent/skill file).
17. Present to the user:
    - Confidence state (`COMPLETE`, `PARTIAL_CONFIDENCE`, or `BLOCKED`)
    - Overall AEO score + grade, or a score range if evidence is incomplete
    - Evidence gaps that affect confidence
    - Top opportunities (P1/P2)
    - The Buildable item IDs and recommended default selection (all Buildable P1 + P2)
18. Ask the user to **approve** and **select item IDs to build**.
19. Record the selection in `output/<brand-slug>/plan.md` under `## Build Selection`; keep `Build state: NOT_STARTED` until `/aeo-build` starts.
20. Report and STOP:
```
AEO plan ready for [Brand].

- Plan: output/<brand-slug>/plan/aeo-plan.md
- Research: output/<brand-slug>/research/

Next: run /aeo-build to generate artifacts for the selected items.
```
Do NOT generate artifacts in this command.
