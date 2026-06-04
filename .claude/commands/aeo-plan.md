# /aeo-plan -- AEO Improvement Plan (Stage 1)

Research the brand's AI search readiness and produce a prioritized, traceable, artifact-mapped improvement plan. The plan is a human-approved gate: after it's generated, the team reviews it and selects which items to build with `/aeo-build`.

## Input: $ARGUMENTS

If no arguments, read `config/brand-profile.md` first, then confirm/collect:
1. Brand URL(s) (default: primary domain from profile)
2. Competitors (URLs or "auto-find"; default from profile)
3. Priority topics / target AI queries (default from profile)

## Context Rules (MANDATORY)

Follow the Context Engineering rules in CLAUDE.md:
- Do NOT read agent or skill files yourself
- Pass file PATHS to agents, not contents
- Agents write to disk directly; you track status and file paths only

## Pipeline

### Phase 1: Input & Setup
1. Read `config/brand-profile.md`.
2. Confirm brand URL(s), competitors, and priority topics/queries with the user.
3. Create `brand-slug` (lowercase, hyphens). Create `output/<brand-slug>/` with subdirs `research/` and `plan/`.
4. Present the plan-run scope and wait for approval.
5. Save run config to `output/<brand-slug>/plan.md`: domains, competitor URLs, priority queries, date, PageSpeed API key (if in profile).

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
    - Brand profile: config/brand-profile.md
    - Run config: output/<brand-slug>/plan.md

    ## Output Files (write these yourself)
    - output/<brand-slug>/research/site-crawl.md

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
    - Run config: output/<brand-slug>/plan.md

    ## Output Files (write these yourself)
    - output/<brand-slug>/research/tool-data.md

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
    - Brand profile: config/brand-profile.md
    - Run config: output/<brand-slug>/plan.md

    ## Output Files (write these yourself)
    - output/<brand-slug>/research/competitor-analysis.md

    ## Return Format
    Return ONLY: Status, Files created, Issues.
```

9. Verify `research/site-crawl.md`, `research/tool-data.md`, `research/competitor-analysis.md` exist.
10. **Recovery:** for any missing file, re-spawn the responsible agent (max_turns: 10) with: "Your previous run exhausted turns before writing output. Read your agent instructions at [path] and write output to [path] immediately." If still missing, write a minimal placeholder noting the gap and proceed.

### Phase 2.5: AEO Analysis

11. Spawn **AEO Analyst** (max_turns: 15):
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
    - Brand profile: config/brand-profile.md
    - Run config: output/<brand-slug>/plan.md
    - Site Crawl: output/<brand-slug>/research/site-crawl.md
    - Tool Data: output/<brand-slug>/research/tool-data.md
    - Competitor Analysis: output/<brand-slug>/research/competitor-analysis.md

    ## Output Files (write these yourself)
    - output/<brand-slug>/research/aeo-analysis.md

    ## Return Format
    Return ONLY: Status, Files created, Issues.
```

12. Verify `research/aeo-analysis.md` exists.

### Phase 3: Plan Synthesis

13. Spawn **AEO Strategist** (max_turns: 15):
```
Task tool:
  description: "Synthesize AEO improvement plan"
  subagent_type: "general-purpose"
  max_turns: 15
  prompt: |
    You are the AEO Strategist for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/aeo-strategist.md

    ## Your Task
    Synthesize all research into output/<brand-slug>/plan/aeo-plan.md -- a prioritized, traceable, artifact-mapped backlog using the aeo-plan-structure skill.

    ## Input Files (read these yourself)
    - Brand profile: config/brand-profile.md
    - Run config: output/<brand-slug>/plan.md
    - Site Crawl: output/<brand-slug>/research/site-crawl.md
    - Tool Data: output/<brand-slug>/research/tool-data.md
    - Competitor Analysis: output/<brand-slug>/research/competitor-analysis.md
    - AEO Analysis: output/<brand-slug>/research/aeo-analysis.md

    ## Output Files (write these yourself)
    - output/<brand-slug>/plan/aeo-plan.md

    ## Return Format
    Return ONLY: Status, Files created, Issues.
```

14. Verify `plan/aeo-plan.md` exists.

### Phase 4: Approval Gate (MANDATORY)

15. Read `plan/aeo-plan.md` enough to summarize for the user (you MAY read this file -- it is the gate artifact, not an agent/skill file).
16. Present to the user:
    - Overall AEO score + grade
    - Top opportunities (P1/P2)
    - The Buildable item IDs and recommended default selection (all Buildable P1 + P2)
17. Ask the user to **approve** and **select item IDs to build**.
18. Record the selection in `output/<brand-slug>/plan.md` under `## Build Selection`.
19. Report and STOP:
```
AEO plan ready for [Brand].

- Plan: output/<brand-slug>/plan/aeo-plan.md
- Research: output/<brand-slug>/research/

Next: run /aeo-build to generate artifacts for the selected items.
```
Do NOT generate artifacts in this command.
