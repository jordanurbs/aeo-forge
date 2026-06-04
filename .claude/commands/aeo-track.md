# /aeo-track -- Measure AI Citations (Stage 3, ongoing)

Execute the brand's prompt set against AI answer engines, detect whether the brand is cited, and update a running scoreboard so the team can track AI-citation frequency over time. This is the **measurement loop** that turns the manual prompt set from `/aeo-build` into a *measured* one. Re-run on cadence (monthly suggested).

## Prerequisite

A prompt set exists: `output/<brand-slug>/measurement/prompt-set.md` (from `/aeo-build`'s measurement output) or `artifacts/measurement/prompt-set.md`. If neither exists, the run falls back to `plan.md` priority queries, then the brand profile's target AI queries. If no prompts can be found anywhere, tell the user to run `/aeo-build` (or add Target AI queries to the profile) first.

Engine keys are **optional**. With no keys the run is **manual** (a logging template + an optional WebSearch directional proxy). With a Perplexity / OpenAI / SerpAPI key (env var or the gitignored `config/brand-profile.md`) the run is **measured**.

## Input: $ARGUMENTS

Optionally a brand-slug and/or an engine list (`perplexity,openai,serp`). If absent, use the most recent `output/<brand-slug>/` and all engines with available keys.

## Context Rules (MANDATORY)

Follow the Context Engineering rules in CLAUDE.md: pass file PATHS to the agent, the agent reads its own instructions and writes to disk, you track status only. Do NOT read agent/skill files yourself. You MAY read `plan.md` and the run JSON to route and summarize. Use absolute workspace-root-resolved paths in the Task prompt, and verify every expected output file after the agent returns (retry once with the exact missing path).

## Pipeline

### Phase 1: Locate & Confirm
1. Identify the `<brand-slug>` and confirm `output/<brand-slug>/` exists.
2. Confirm the prompt set source (prompt-set.md > plan.md priority queries > profile target queries) and the brand identifiers (name + domains) and competitors are available. Note fixture mode if `plan.md` says `Run type: fixture`.
3. Detect mode: check whether any engine key is present (env vars `PERPLEXITY_API_KEY` / `OPENAI_API_KEY` / `SERPAPI_KEY` / `SERPAPI_API_KEY` / `DATAFORSEO_KEY`, or the `## API Keys` section of `config/brand-profile.md`). Tell the user whether this will be a **measured** or **manual** run before proceeding.

### Phase 2: Run the deterministic script
4. Run:
   ```
   python3 scripts/run-citation-checks.py --brand-dir output/<brand-slug> --write-report
   ```
   This reads keys (env first, then profile), picks measured/manual mode, calls each available engine per prompt, runs heuristic citation detection, and writes `measurement/citation-runs/<date>.json` + `<date>.md` plus a deterministic draft of `measurement/citation-scoreboard.md`. It exits 0 even with no keys.
5. Verify `measurement/citation-runs/<date>.json` and `<date>.md` exist. If missing, re-run once; if still missing, report the script error and stop.

### Phase 3: Interpret + scoreboard (spawn the agent)
6. Spawn **Citation Tracker** (max_turns: 12):
```
Task tool:
  description: "Interpret citations + scoreboard"
  subagent_type: "general-purpose"
  max_turns: 12
  prompt: |
    You are the Citation Tracker for the Enterprise AEO Builder.
    Read your full instructions at: .claude/agents/citation-tracker.md

    ## Your Task
    Run (or confirm) the citation check, interpret the run JSON, finalize this run's
    detail markdown, and update the running scoreboard with trend vs the prior run,
    top uncited high-priority prompts, and competitors winning citations.

    ## Input Files (read these yourself)
    - Run config: /absolute/path/to/output/<brand-slug>/plan.md
    - Prompt set: /absolute/path/to/output/<brand-slug>/measurement/prompt-set.md (or artifacts/measurement/prompt-set.md)
    - Brand profile: /absolute/path/to/config/brand-profile.md
    - Competitor analysis: /absolute/path/to/output/<brand-slug>/research/competitor-analysis.md
    - This run JSON: /absolute/path/to/output/<brand-slug>/measurement/citation-runs/<date>.json
    - Prior runs: /absolute/path/to/output/<brand-slug>/measurement/citation-runs/*.json

    ## Output Files (write these yourself)
    - /absolute/path/to/output/<brand-slug>/measurement/citation-runs/<date>.md
    - /absolute/path/to/output/<brand-slug>/measurement/citation-scoreboard.md

    ## Quality Requirements
    - Honest labeling: "measured via [engine]" vs "directional proxy (model web search)" vs "manual". Never call a WebSearch proxy "measured".
    - Citation detection is heuristic; use the `aeo-analysis` source label and hedge name-only matches.
    - No secrets: keys come from env/profile; never echo a key into any output file.
    - Preserve fixture/sample-run boundaries from the run config (keep confidence PARTIAL_CONFIDENCE).

    ## Return Format
    Return ONLY: Status, Files created, Mode, Confidence, Issues.
```
7. After it returns, verify `measurement/citation-runs/<date>.md` and `measurement/citation-scoreboard.md` exist at the exact paths. Retry once with the missing path if not.

### Phase 4: Report
8. Read the scoreboard enough to summarize and report:
```
AI-citation tracking complete for [Brand].

- Mode: measured via [engines] | manual (no API keys)
- Confidence: COMPLETE | PARTIAL_CONFIDENCE
- Overall citation frequency: X% (cited/total)  [trend vs prior run: +/-/flat]
- Per engine: perplexity X% | openai Y% | serp Z%
- Biggest gaps: [top uncited high-priority prompts]
- Competitors winning citations: [who, where]
- Run detail: output/<brand-slug>/measurement/citation-runs/<date>.md
- Scoreboard: output/<brand-slug>/measurement/citation-scoreboard.md

Next: re-run /aeo-track on your cadence (monthly suggested) to track the trend.
Add a Perplexity key (env or config/brand-profile.md) for measured results if this was a manual run.
```

## Notes
- **Out of scope:** hosted dashboards / schedulers (the team re-runs `/aeo-track` on cadence) and paid-tool deep integrations beyond the listed adapters.
- **Transient outputs:** dated `citation-runs/<date>.json|md` for the bundled fixture are throwaway; do not commit them.
