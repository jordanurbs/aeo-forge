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

Ask for the following. Use AskQuestion for structured choices. Collect in this order:

**Brand**
1. Brand name?
2. Primary domain?
3. Any additional domains/subdomains? (docs, blog, etc., or "none")
4. Sitemap URL? (or "not provided")
5. Industry / category?
6. One-line canonical description? (used verbatim in Organization schema and llms.txt)
7. Primary markets/locales? (e.g., United States / en-US, or "not provided")

**Entity Signals (single source of truth)**
8. Legal/registered name (if different)?
9. Canonical Organization `@id`? (default: primary domain + `/#organization`)
10. Logo URL?
11. Founders / key people (names + titles)?
12. Founding year?
13. Authoritative profiles for `sameAs` (Wikipedia, Wikidata, LinkedIn, Crunchbase, social)?
14. Key verifiable stats/claims? (only true, verifiable facts -- these become schema)
15. Source-of-truth pages for entity facts? (About, security, press kit, docs)

**AEO Targets**
16. Priority topics/entities the brand should own?
17. Target AI queries -- the real questions buyers ask AI assistants?
18. Buyer-journey focus? (pre-funnel / TOFU / MOFU / BOFU)
19. Priority URLs to audit/build for?
20. Competitors to benchmark against? (URLs or "auto-find")

**Tech Stack & Deployment**
21. CMS / framework?
22. How is schema currently added? (templates / plugin / none)
23. Edge/CDN available for schema injection? (Cloudflare Workers / Fastly / none)
24. Preferred artifact format? (CMS HTML / Markdown / JSON-LD snippets / code PR / edge config)
25. Who deploys changes? (Eng / Marketing via CMS / agency)
26. Deployment constraints? (no inline scripts, CMP requirements, template lock-in, or "none")

**Content Governance**
27. Brand voice / style guide? (link or short description)
28. Content owners / approvers?
29. Review/approval process for published content?
30. Refresh cadence target? (e.g., quarterly)
31. Regulated-claim constraints? (legal/compliance rules, or "none")
32. Prohibited claims/phrases?
33. Required disclaimers? (or "none")

**Measurement**
34. Analytics platform? (GA4 / PostHog / Adobe / none)
35. Any AI-visibility tools in use?
36. KPIs that matter most?
37. Bot-log access? (available / not available / unknown)
38. Baseline reporting source? (dashboard/report URL, spreadsheet, or "not provided")

**Evidence & Confidence**
39. Known crawl blockers? (login walls, geofencing, robots limits, JS-rendered pages, or "none")
40. Pages that must not be changed? (URLs/patterns, or "none")
41. Claims requiring manual approval? (security, compliance, customer counts, performance claims, or "none")
42. Current known AEO/SEO issues? (brief list or "not provided")

**API Keys (Optional)**
43. Google PageSpeed API key? (Free at https://developers.google.com/speed/docs/insights/v5/get-started)
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
