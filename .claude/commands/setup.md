# /setup -- Brand Configuration Wizard

Walk the user through configuring their Enterprise AEO Builder instance. Fills out `config/brand-profile.md` with the brand's details, entity signals, AEO targets, tech stack, governance, and optional API keys. This is an internal tool -- there is no pricing, branding-for-sale, or outreach configuration.

## Input: $ARGUMENTS

No arguments expected. This is an interactive wizard.

## Context Rules (MANDATORY)

Follow the Context Engineering rules in CLAUDE.md:
- This command runs directly (no agent spawning needed)
- Write the completed profile to `config/brand-profile.md`
- A template lives at `config/brand-profile.example.md` for reference

## Pipeline

### Step 1: Welcome

Tell the user:

```
Welcome to the Enterprise AEO Builder setup.

I'll ask a few questions to configure the brand we'll be optimizing for AI
search. This is a one-time setup -- your answers are reused by /aeo-plan and
/aeo-build. You can edit config/brand-profile.md anytime.
```

### Step 2: Collect Information

Ask for the following. Use AskUserQuestion for choices. Collect in this order:

**Brand**
1. Brand name?
2. Primary domain?
3. Any additional domains/subdomains? (docs, blog, etc., or "none")
4. Industry / category?
5. One-line canonical description? (used verbatim in Organization schema and llms.txt)

**Entity Signals (single source of truth)**
6. Legal/registered name (if different)?
7. Founders / key people (names + titles)?
8. Founding year?
9. Authoritative profiles for `sameAs` (Wikipedia, Wikidata, LinkedIn, Crunchbase, social)?
10. Key verifiable stats/claims? (only true, verifiable facts -- these become schema)

**AEO Targets**
11. Priority topics/entities the brand should own?
12. Target AI queries -- the real questions buyers ask AI assistants?
13. Buyer-journey focus? (pre-funnel / TOFU / MOFU / BOFU)
14. Competitors to benchmark against? (URLs or "auto-find")

**Tech Stack & Deployment**
15. CMS / framework?
16. How is schema currently added? (templates / plugin / none)
17. Edge/CDN available for schema injection? (Cloudflare Workers / Fastly / none)
18. Who deploys changes? (Eng / Marketing via CMS / agency)

**Content Governance**
19. Brand voice / style guide? (link or short description)
20. Content owners / approvers?
21. Refresh cadence target? (e.g., quarterly)

**Measurement**
22. Analytics platform? (GA4 / PostHog / Adobe / none)
23. Any AI-visibility tools in use?

**API Keys (Optional)**
24. Google PageSpeed API key? (Free at https://developers.google.com/speed/docs/insights/v5/get-started)
    - If no: "It's optional -- PageSpeed works without a key at lower rate limits, fine for one brand at a time. You can add it later in config/brand-profile.md."

### Step 3: Write Profile

Write the completed profile to `config/brand-profile.md` using the structure in `config/brand-profile.example.md`, substituting the user's answers.

### Step 4: Confirm

Tell the user:

```
Setup complete. Your brand profile is saved at config/brand-profile.md.

Edit it anytime. Next:
1. Run /aeo-plan to research the brand and generate an AEO improvement plan.
2. Review and approve the plan (select which items to build).
3. Run /aeo-build to generate the artifacts your team will ship.

Tool permissions are pre-configured in .claude/settings.local.json.
```
