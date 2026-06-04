# Brand Profile

Copy this file to `config/brand-profile.md` and fill it in (or run `/setup`). This is the single source of truth for the brand the rig optimizes. No pricing, no outreach -- this is an internal enterprise tool.

## Brand
- Brand name: [e.g., Acme Corp]
- Primary domain: [e.g., https://acme.com]
- Additional domains/subdomains: [docs.acme.com, blog.acme.com, or "none"]
- Industry / category: [e.g., B2B project-management SaaS]
- One-line description (canonical): [used verbatim in Organization schema and llms.txt]

## Entity Signals (single source of truth)
- Legal/registered name: [if different from brand name]
- Founders / key people: [names + titles, for Person/E-E-A-T schema]
- Founding year: [e.g., 2018]
- Authoritative profiles (sameAs): [Wikipedia, Wikidata, LinkedIn, Crunchbase, official social URLs]
- Key verifiable stats/claims: [e.g., "10,000+ customers", "SOC 2 Type II" -- only true, verifiable facts]

## AEO Targets
- Priority topics/entities the brand should own: [3-8 topics]
- Target AI queries (prompts to be cited for): [the real questions buyers ask AI assistants]
- Buyer-journey focus: [pre-funnel / TOFU / MOFU / BOFU -- where to concentrate]
- Competitors to benchmark against: [URLs, or "auto-find"]

## Tech Stack & Deployment (how artifacts get shipped)
- CMS / framework: [e.g., Next.js, WordPress, Webflow, Contentful]
- How schema is currently added: [hardcoded in templates / plugin / none]
- Edge/CDN available for schema injection: [Cloudflare Workers / Fastly / none]
- Who deploys changes: [Eng team / Marketing via CMS / agency]

## Content Governance
- Brand voice / style guide: [link or short description]
- Content owners / approvers: [roles or names]
- Review/approval process for published content: [short description]
- Refresh cadence target: [e.g., quarterly for high-value pages]

## Measurement
- Analytics platform: [GA4 / PostHog / Adobe / none]
- AI-visibility tools in use (if any): [e.g., Profound, Peec, none]
- KPIs that matter most: [citation frequency / AI-referred sessions / AI Overview presence]

## API Keys (optional)
- Google PageSpeed API key: [key, or "not provided" -- works without a key at lower rate limits]
