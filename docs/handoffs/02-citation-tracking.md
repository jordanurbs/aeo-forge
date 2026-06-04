# Handoff: Automated Prompt Execution + Citation Tracking (Feature #2)

This is a self-contained spec for a fresh agent/conversation to implement Feature #2 end to end. You have no prior context; everything you need is here. Read `CLAUDE.md` first to learn the rig's conventions, then implement exactly what this spec describes.

## Background

This repo (**Enterprise AEO Builder**, repo `jordanurbs/aeo-forge`) is a Claude Code multi-agent rig that runs in two stages:
- `/aeo-plan` -> researches a brand and writes a prioritized AEO improvement plan.
- `/aeo-build` -> generates validated, drop-in AEO artifacts.

Today the rig defines a **prompt set** and a **manual** measurement plan (see `.claude/agents/measurement-builder.md`, which writes `output/<brand-slug>/artifacts/measurement/prompt-set.md`). It never actually runs those prompts against AI engines. Feature #1 (already merged/in PR) added demand signals. **Feature #2 (this task)** turns the manual measurement plan into a *measured* one: actually execute the prompt set against AI answer engines and record whether the brand is cited, over time.

## Goal

Given a brand's prompt set, automatically query AI answer engines, detect whether the brand is cited/recommended, capture which sources/competitors are cited instead, and write a dated results file plus a running scoreboard so the team can track AI-citation frequency over time.

## Design Principles (match the existing rig)

1. **Markdown-agent rig + deterministic script split.** Mirror the existing pattern where `scripts/validate-artifacts.py` does deterministic work and an agent interprets results. Real API orchestration belongs in a Python script (`scripts/run-citation-checks.py`); interpretation/scoreboard belongs to an agent.
2. **Keyless-safe.** Must run with NO API keys: fall back to a manual-logging template + a directional proxy using the agent's own WebSearch. Keys unlock real engine queries. Never hard-fail because a key is missing.
3. **No secrets in the repo.** Read keys from `config/brand-profile.md` and/or environment variables. Never commit keys. Confirm `config/brand-profile.md` stays gitignored (it is).
4. **Honest labeling.** Distinguish "measured via [engine] API" from "directional proxy (model web search)". Citation detection is heuristic; say so.
5. **Evidence + traceability.** Reuse the `Confidence state` / source-label conventions from `CLAUDE.md`.

## Engine Adapters (implement in priority order)

| Engine | How | Key (brand-profile) | Why |
|--------|-----|---------------------|-----|
| **Perplexity** | `POST https://api.perplexity.ai/chat/completions` model `sonar` (or current) | `Perplexity API key` | Returns answers **with citations/sources** -- best signal for citation tracking |
| **OpenAI web search** | Responses API with `web_search` tool (current model) | `OpenAI API key` | Answers + cited URLs |
| **Google AI Overviews** | SERP via DataForSEO SERP API or SerpAPI (`ai_overview`/organic) | `SerpAPI key` or reuse DataForSEO key | Closest proxy to Google AI Overviews; no official API |
| **Keyless fallback** | Use the agent's `WebSearch` tool as a directional proxy | none | Lets the feature run without keys (clearly labeled lower-confidence) |

Implement Perplexity first (highest value), then OpenAI, then SERP. Each adapter is optional and gated on its key being present.

## Citation Detection

For each prompt × engine response, determine:
- **Brand cited?** True if the brand's primary domain (or additional domains from `brand-profile.md`) appears in the returned source/citation URLs, OR the brand name is recommended in the answer text. Track which (source-cited vs name-mentioned -- source-cited is stronger).
- **Position/prominence:** where in the answer/sources the brand appears (if available).
- **Competitors cited:** match competitor domains/names (from `output/<brand-slug>/research/competitor-analysis.md`) present in the response.
- **Answer summary:** 1-2 lines of what the engine said, for context.

Detection is heuristic (string/domain matching + light normalization). Document the rules and edge cases.

## Deliverables (create these)

### 1. `scripts/run-citation-checks.py`
- Inputs: `--brand-dir output/<brand-slug>` (reads prompt set, brand domains/name, competitors), optional `--engines perplexity,openai,serp`, `--write-report`.
- Reads keys from env vars first, then `config/brand-profile.md`. If no keys: writes a manual-logging template and exits 0 with a clear "no keys; manual mode" note.
- For each prompt × available engine: call the API, capture answer + sources, run citation detection.
- Writes machine-readable `output/<brand-slug>/measurement/citation-runs/<YYYY-MM-DD>.json` and a human-readable `<YYYY-MM-DD>.md`.
- Pure stdlib if feasible (`urllib`); if `requests` is needed, note it. No network at import time. Handle timeouts, rate limits, and per-engine failures gracefully (record the failure, continue).

### 2. `.claude/skills/citation-tracking/SKILL.md`
- Engine adapter request/response patterns (exact endpoints, payloads, how to extract citations), citation-detection rules, the scoreboard format, scoring (citation frequency = cited prompts / total prompts, per engine and overall), trend tracking, and honest-labeling rules. Follow the structure/voice of existing skills (e.g., `technical-seo`, `demand-signals`).

### 3. `.claude/agents/citation-tracker.md`
- Reads the skill, runs `scripts/run-citation-checks.py` (or guides manual mode), interprets the JSON, and writes:
  - `output/<brand-slug>/measurement/citation-runs/<date>.md` (this run's detail; the script may draft it, the agent finalizes interpretation)
  - `output/<brand-slug>/measurement/citation-scoreboard.md` (running scoreboard: per-run citation frequency by engine, trend vs previous runs, top uncited high-priority prompts, competitors winning citations)
- Follows the agent file structure used across `.claude/agents/*` (First Steps, Inputs, Outputs, Return Format, Process, Rules, Tools). Honors fixture mode + confidence states.

### 4. `/aeo-track` command: `.claude/commands/aeo-track.md`
- Prereq: a prompt set exists (from `/aeo-build`'s measurement output, or fall back to `brand-profile.md` target queries).
- Phase 1: locate/confirm the prompt set + brand identifiers + competitors.
- Phase 2: run the deterministic script.
- Phase 3: spawn the `citation-tracker` agent to interpret + write the scoreboard.
- Phase 4: report citation frequency, trend, biggest gaps, and competitor wins. Recommend re-running on the brand's cadence (monthly suggested).
- Match the structure of `.claude/commands/aeo-plan.md` / `aeo-build.md` (absolute-path Task prompts, context-safe spawning).

### 5. Wiring + docs
- `config/brand-profile.example.md` and `fixtures/sample-brand-profile.md`: add the new optional keys under `## API Keys` (Perplexity, OpenAI, SerpAPI -- DataForSEO key may already exist from Feature #1).
- `.claude/commands/setup.md`: add questions for the new optional keys.
- `CLAUDE.md`: add `citation-tracker` to the agent team (a third stage -- call it **Track** -- or note it as an ongoing-measurement command), add the `citation-tracking` skill to the skills table, add `/aeo-track` to commands + file reference, extend the output-structure tree with `measurement/citation-runs/` and `citation-scoreboard.md`.
- `README.md`: document `/aeo-track` and the measurement loop (manual -> measured).
- `.claude/settings.local.json`: ensure `Bash(python3:*)`, `Bash(curl:*)`, `WebSearch`, `WebFetch(domain:*)` are allowed (they are). Add any new tool perms only if needed.

## Output Structure (additions)
```
output/<brand-slug>/measurement/
  prompt-set.md                 # existing (from measurement-builder)
  measurement-plan.md           # existing
  citation-runs/
    <YYYY-MM-DD>.json           # machine-readable run results
    <YYYY-MM-DD>.md             # human-readable run detail
  citation-scoreboard.md        # running trend across runs
```

## Acceptance Criteria
- [ ] `python3 scripts/run-citation-checks.py --brand-dir fixtures/sample-output/acme-analytics` runs with NO keys and produces a manual-mode template without error (exit 0).
- [ ] With a Perplexity key set (env or profile), it queries Perplexity for each prompt and records cited/not-cited + sources.
- [ ] Citation detection correctly flags the brand domain appearing in sources (add a tiny unit/self-check or documented manual check).
- [ ] `/aeo-track` produces `citation-scoreboard.md` with per-engine citation frequency and a trend vs the prior run.
- [ ] No secrets committed; keys read from env/profile; `config/brand-profile.md` stays gitignored.
- [ ] CLAUDE.md, README, setup, brand-profile example + fixture all updated consistently. No dangling references.
- [ ] Honest labeling throughout: "measured via [engine]" vs "directional proxy".

## Process for the implementing agent
1. You are already on branch `feat/citation-tracking` (based on `harden-aeo-harness-validation`). Do all work here. Do NOT touch `feat/demand-signals` or `main`.
2. Implement the deliverables above. Keep commits focused.
3. Run the keyless acceptance check.
4. Commit, `git push -u origin feat/citation-tracking`.
5. Open a PR with `gh pr create --repo jordanurbs/aeo-forge --base harden-aeo-harness-validation --head feat/citation-tracking` with a clear summary + test plan. Do NOT merge.
6. Report the PR URL.

## Out of Scope
- Building a hosted dashboard or scheduler (the team re-runs `/aeo-track` on cadence).
- Paid-tool deep integrations beyond the adapters listed.
- Changing the plan/build stages (this is a new, additive measurement capability).
