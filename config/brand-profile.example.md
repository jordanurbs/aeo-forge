# Brand Profile

Copy this file to `config/brand-profile.md` and fill it in (or run `/setup`). This is the single source of truth for the brand the rig optimizes. No pricing, no outreach -- this is an internal enterprise tool.

## Brand
- Brand name: [e.g., Acme Corp]
- Primary domain: [e.g., https://acme.com]
- Additional domains/subdomains: [docs.acme.com, blog.acme.com, or "none"]
- Sitemap URL: [e.g., https://acme.com/sitemap.xml, or "not provided"]
- Industry / category: [e.g., B2B project-management SaaS]
- One-line description (canonical): [used verbatim in Organization schema and llms.txt]
- Primary markets/locales: [e.g., United States / en-US, Canada / en-CA]

## Entity Signals (single source of truth)
- Legal/registered name: [if different from brand name]
- Canonical Organization @id: [e.g., https://acme.com/#organization]
- Logo URL: [e.g., https://acme.com/logo.svg]
- Founders / key people: [names + titles, for Person/E-E-A-T schema]
- Founding year: [e.g., 2018]
- Authoritative profiles (sameAs): [Wikipedia, Wikidata, LinkedIn, Crunchbase, official social URLs]
- Key verifiable stats/claims: [e.g., "10,000+ customers", "SOC 2 Type II" -- only true, verifiable facts]
- Source-of-truth pages for entity facts: [About page, security page, press kit, docs, or "not provided"]

## AEO Targets
- Priority topics/entities the brand should own: [3-8 topics]
- Target AI queries (prompts to be cited for): [the real questions buyers ask AI assistants]
- Buyer-journey focus: [pre-funnel / TOFU / MOFU / BOFU -- where to concentrate]
- Priority URLs to audit/build for: [homepage, pricing, product pages, docs, comparison pages]
- Competitors to benchmark against: [URLs, or "auto-find"]

## Tech Stack & Deployment (how artifacts get shipped)
- CMS / framework: [e.g., Next.js, WordPress, Webflow, Contentful]
- How schema is currently added: [hardcoded in templates / plugin / none]
- Edge/CDN available for schema injection: [Cloudflare Workers / Fastly / none]
- Preferred artifact format: [CMS HTML, Markdown, JSON-LD snippets, code PR, edge config]
- Who deploys changes: [Eng team / Marketing via CMS / agency]
- Deployment constraints: [e.g., no inline scripts, CMP requirements, template lock-in, or "none"]

## Content Governance
- Brand voice / style guide: [link or short description]
- Content owners / approvers: [roles or names]
- Review/approval process for published content: [short description]
- Refresh cadence target: [e.g., quarterly for high-value pages]
- Regulated-claim constraints: [legal/compliance rules, industry restrictions, or "none"]
- Prohibited claims/phrases: [claims the builders must not make]
- Required disclaimers: [copy that must appear on certain pages, or "none"]

## Measurement
- Analytics platform: [GA4 / PostHog / Adobe / none]
- AI-visibility tools in use (if any): [e.g., Profound, Peec, none]
- KPIs that matter most: [citation frequency / AI-referred sessions / AI Overview presence]
- Bot-log access: [available / not available / unknown]
- Baseline reporting source: [dashboard/report URL, spreadsheet, or "not provided"]

## API Keys (optional)
- Google PageSpeed API key: [key, or "not provided" -- works without a key at lower rate limits]
- Keyword-volume API (optional): [DataForSEO base64 "login:password", Semrush key, or "not provided" -- enables numeric search volume in demand signals; without it, demand is derived from free Google Autocomplete + People-Also-Ask]

## Evidence & Confidence (optional but recommended)
- Known crawl blockers: [login walls, geofencing, robots limits, JS-rendered pages, or "none"]
- Pages that must not be changed: [URLs or patterns, or "none"]
- Claims requiring manual approval: [security, compliance, customer counts, performance claims, or "none"]
- Current known AEO/SEO issues: [brief list, links to audits, or "not provided"]
