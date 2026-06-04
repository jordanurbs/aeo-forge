---
name: AEO Optimization
version: 1.0.0
description: Answer Engine Optimization -- the star skill. Assessment framework + 2026 enterprise playbook for how brands appear in AI search engines (ChatGPT, Perplexity, Google AI Overviews, Gemini, Copilot, Claude). Covers structured data for AI, answer-ready content formats, entity authority, topical authority, citation-worthiness, scoring, schema stacking, and measurement. Used by the AEO Analyst, AEO Strategist, the artifact builders, and the Artifact Validator.
---

# AEO Optimization Skill (Answer Engine Optimization)

This is the centerpiece skill of the audit. AEO -- Answer Engine Optimization -- assesses how well a business is positioned to appear in AI-generated search results. This is the differentiator that makes the audit stand out. Most SEO agencies still don't assess this.

## Why AEO Matters

AI search engines are changing how people find businesses:
- **Google AI Overviews** appear above traditional search results for ~30% of queries
- **ChatGPT with browsing** and **SearchGPT** are used by millions for recommendations
- **Perplexity AI** provides cited, synthesized answers from multiple sources
- **Bing Copilot** integrates AI answers directly into search results
- **Claude** (via web search) provides researched recommendations

Traditional SEO optimizes for ranking in a list of links. AEO optimizes for being **cited as a source** in AI-generated answers. The mechanics are fundamentally different.

## How AI Search Engines Select Sources

Understanding this is critical to the assessment. AI engines don't rank pages -- they select sources to cite.

### Selection Criteria (What AI Engines Look For)

1. **Direct answer availability** -- Content that directly answers a question gets cited. AI engines prefer pages that contain clear, concise answers in the first few paragraphs, not pages that bury the answer under 1000 words of preamble.

2. **Structured data** -- JSON-LD schema helps AI engines understand what a page is about, what entity it describes, and what questions it answers. Pages with rich schema are more parseable.

3. **Entity clarity** -- AI engines need to understand what entity (business, person, concept) a page represents. Clear entity definitions through schema, consistent NAP, and Knowledge Panel presence help.

4. **Topical authority** -- AI engines assess whether a source is authoritative on a topic by looking at content depth, breadth of coverage, internal linking patterns, and external citations.

5. **Recency and freshness** -- AI engines prefer current information. Dated content, especially for queries with time-sensitive answers, gets deprioritized.

6. **Citation-worthiness** -- Content that contains original data, unique research, expert opinions, or specific claims with evidence is more likely to be cited than generic advice.

7. **Content format** -- Certain formats are more easily extractable by AI:
   - Definition paragraphs ("X is a...")
   - Numbered/bulleted lists
   - Comparison tables
   - Q&A format
   - Step-by-step instructions
   - Statistics with sources

### How Each AI Engine Differs

| Engine | Primary Source Behavior | Key Factors |
|--------|----------------------|-------------|
| **Google AI Overviews** | Synthesizes from top-ranking pages | Traditional SEO ranking matters most; structured data helps |
| **ChatGPT/SearchGPT** | Browses web, synthesizes from multiple sources | Prefers clear, authoritative, well-structured content |
| **Perplexity AI** | Cites specific sources with links | Values unique data, specific claims, and authoritative sources |
| **Bing Copilot** | Draws from Bing index + partner data | Bing SEO factors matter; structured data heavily weighted |
| **Claude (web search)** | Searches and synthesizes from multiple results | Values comprehensive, nuanced, well-sourced content |

## 2026 Enterprise AEO Playbook (Evidence-Based)

This section captures what actually moves AI citations as of 2026. It informs both assessment (planning stage) and artifact generation (build stage). Sources: Ahrefs 2026 schema study, the 2024 Princeton/Georgia Tech/IIT-Delhi GEO paper, and public statements from Google (Mueller/Illyes) on `llms.txt`.

### The Highest-Impact Levers (in order)

1. **Schema stacking.** FAQPage schema alone shows roughly +2.7x citation lift (≈41% vs 15% citation rate). The compounding win is *stacking* multiple JSON-LD types on a single key page: `Article` + `FAQPage` + `HowTo` + `Organization` + `BreadcrumbList` + `ItemList` (where applicable). Build a connected `@graph`, not isolated blocks.

2. **Answer-first content structure.** AI Overviews cite from a page's *opening content* roughly 55% of the time. Every key page and section should:
   - Lead with a direct answer in **40-60 words** at the very top.
   - Use **H2/H3 headings phrased as real user questions** ("What is X?", "How much does X cost?").
   - Use **short paragraphs (2-4 sentences)** and bulleted/numbered lists.
   - Avoid slow-building narrative before the answer.

3. **Visible-text / JSON-LD parity (compliance-critical).** FAQ/HowTo/Q&A schema must mirror the **visible, human-readable text on the page exactly**. Schema that describes content not visible on the page is a compliance risk and can be discounted or penalized. Always ship the matched pair (visible HTML + JSON-LD).

4. **Malformed schema is worse than none.** Some engines treat broken or invalid JSON-LD as a negative integrity/trust signal. Every JSON-LD block must be parsed and schema.org-validated before shipping.

5. **Entity / single source of truth.** AI engines reward a consistent, well-defined entity and penalize contradictory facts across a brand's properties. Maintain a canonical `Organization` definition with `sameAs` links to authoritative profiles (Wikipedia, Wikidata, LinkedIn, Crunchbase, official social), plus consistent name, description, founding info, and key stats everywhere they appear.

6. **Freshness.** Engines favor current information. Use `dateModified`, a visible "Last updated: [Month Year]", year-in-title where appropriate, and recent statistics. Refresh high-value pages on a quarterly cadence.

### Measurement Has Shifted (Rank -> Citation)

Traditional rank is no longer the primary KPI. Track:
- **Citation frequency** -- how often the brand is cited/recommended across ChatGPT, Perplexity, Google AI Overviews, Gemini, Copilot, Claude.
- **AI Overview / answer presence** for a tracked set of priority prompts.
- **AI-referred sessions** (referrers/user-agents from AI surfaces) and assisted conversions.
- **Crawler access** -- bot-log hits from `GPTBot`, `ClaudeBot`, `PerplexityBot`, `OAI-SearchBot`, `Google-Extended`.

A durable "answer footprint" -- the brand having complete, structured answers to its priority questions -- is the long-term goal, not raw content volume.

### Buyer-Journey Citation Mapping (B2B / Enterprise)

Map target answers across the journey so the brand is cited at every stage, not just bottom-funnel:
- **Pre-funnel:** discoverability + citability (indexable HTML + extractable answers).
- **TOFU:** narrative control + problem anchoring (the brand is part of the answer when buyers ask "why is X a problem").
- **MOFU:** category ownership + solution clarity.
- **BOFU:** competitive framing + definitive positioning.

### On `llms.txt` (Set Expectations Honestly)

`llms.txt` is **optional and low-priority** as of 2026. Google has publicly stated it does not support it, and major search/answer crawlers (GPTBot, PerplexityBot, Google-Extended) overwhelmingly do not fetch it (~10% of sites publish it; ~0.1% fetch rate). Its **one real use**: application/coding agents (Claude Desktop, claude.ai, Cursor, Continue) do respect it in retrieval flows. Generate it when useful for agent-facing docs, but never present it as a primary ranking or citation lever. For crawler access control, `robots.txt` remains the real standard.

### Off-Site Actions (Spec, Don't Build)

Some of the strongest entity/authority signals can't be built as files -- recommend them in the plan:
- Third-party editorial mentions and authoritative citations.
- Wikipedia/Wikidata entries (for qualifying entities).
- Consistent profiles on industry directories and review platforms.
- Original research/data that other sites cite.

## AEO Assessment Framework

### Criterion 1: Structured Data for AI (Weight: 15%)

**What to assess:**
- JSON-LD schema presence and completeness
- Business-relevant schema types (LocalBusiness, Service, Product, FAQPage, HowTo, Review)
- Schema accuracy (does it match actual page content?)
- Missing schema opportunities

**Scoring:**

| Score | Description |
|-------|-------------|
| 9-10 | Comprehensive schema covering all business entities, services, FAQs. Validated and accurate. |
| 7-8 | Core business schema present (Organization/LocalBusiness), some service/product schema |
| 5-6 | Basic schema present (Organization only) or schema has errors |
| 3-4 | Minimal schema (just website or breadcrumb) |
| 1-2 | No structured data at all |

### Criterion 2: Answer-Ready Content (Weight: 20%)

**What to assess:**
- Does the site have content that directly answers common questions about their services?
- Are answers formatted for extraction (short paragraphs, lists, tables)?
- Does the site have a FAQ page or FAQ sections on service pages?
- Are there "definition" paragraphs that explain what the business does?
- Are there how-to guides, comparison pages, or educational content?

**Answer-ready formats to look for:**
- **FAQ sections** with clear Q&A pairs
- **Definition paragraphs** ("Kitchen remodeling is the process of...")
- **Comparison tables** (Service A vs. Service B, or "What to look for in a...")
- **Numbered steps** ("How to choose a plumber: 1. Check licensing, 2. Read reviews...")
- **Statistics or data points** with sources
- **Expert quotes or opinions** attributed to named professionals

**Scoring:**

| Score | Description |
|-------|-------------|
| 9-10 | Multiple answer-ready content pieces, FAQ pages, how-to guides, comparison tables. Content is formatted for AI extraction. |
| 7-8 | Some FAQ content, a few answer-ready pages. Room for more structured answers. |
| 5-6 | Limited answer-ready content. Information exists but isn't formatted for extraction. |
| 3-4 | Minimal content. No FAQs, no structured answers. Content is marketing-focused, not answer-focused. |
| 1-2 | No content that an AI engine could extract a direct answer from. |

### Criterion 3: Entity Authority (Weight: 20%)

**What to assess:**
Entity authority is about whether AI engines recognize this business as a known, trusted entity.

- **Google Knowledge Panel**: Does the business have one? (Search for the business name in Google)
- **Directory presence**: Is the business listed on major directories (Google Business Profile, Yelp, BBB, industry-specific directories)?
- **Consistent NAP**: Is the business name, address, and phone number consistent across the web?
- **Authoritative mentions**: Is the business mentioned on news sites, industry publications, or authoritative blogs?
- **Social profiles**: Are official social media profiles linked and active?
- **Wikipedia/Wikidata**: For larger businesses -- is there an entry?

**Scoring:**

| Score | Description |
|-------|-------------|
| 9-10 | Knowledge Panel present, consistent directory listings, authoritative mentions, active social profiles |
| 7-8 | Strong directory presence, some authoritative mentions, no Knowledge Panel but strong entity signals |
| 5-6 | Listed on major directories, some inconsistencies, limited authoritative mentions |
| 3-4 | Few directory listings, inconsistent information, no authoritative mentions |
| 1-2 | Minimal or no web presence beyond the website itself |

### Criterion 4: Topical Authority (Weight: 20%)

**What to assess:**
Topical authority measures whether the site demonstrates deep knowledge on its core topics.

- **Content depth**: Does the site have comprehensive coverage of its core topics, or just surface-level service descriptions?
- **Content clusters**: Are there groups of related content linked together (pillar + supporting pages)?
- **Internal linking**: Do pages link to related pages on the same site?
- **Original data/research**: Does the site publish unique information, case studies, or original insights?
- **Content breadth**: Does the site cover the topic from multiple angles (how-to, comparison, cost, FAQ, case study)?
- **Publication consistency**: Is new content published regularly?

**Scoring:**

| Score | Description |
|-------|-------------|
| 9-10 | Deep content clusters, original data, regular publishing, comprehensive internal linking. Clear subject matter authority. |
| 7-8 | Good content depth on core topics, some clusters, moderate internal linking |
| 5-6 | Adequate content on core topics but no depth. No clusters or original data. |
| 3-4 | Thin content. Service descriptions only, no supporting content. |
| 1-2 | Minimal content. One-page or brochure-style site. |

### Criterion 5: Citation-Worthiness (Weight: 15%)

**What to assess:**
Citation-worthiness is about whether an AI engine would trust this site enough to cite it as a source.

- **Original data**: Does the site publish statistics, research, or data that doesn't exist elsewhere?
- **Expert credentials**: Are content creators identified with relevant expertise?
- **Specific claims**: Does the content make specific, verifiable claims (not vague generalities)?
- **Source attribution**: Does the site cite its own sources?
- **Unique perspective**: Does the content offer insights not available on competing sites?
- **Content quality**: Is the writing professional, factual, and well-organized?

**Scoring:**

| Score | Description |
|-------|-------------|
| 9-10 | Original data, named experts, specific claims with evidence, professional writing. Highly citable. |
| 7-8 | Some unique content, professional writing, some specific claims. Reasonably citable. |
| 5-6 | Professional but generic content. Nothing uniquely citable. |
| 3-4 | Thin or generic content with no unique value. Unlikely to be cited. |
| 1-2 | Poor quality, no unique information. Would not be cited. |

### Criterion 6: AI Search Visibility (Weight: 10%)

**What to assess:**
Attempt to test actual AI search visibility by considering:

- What would a user ask an AI assistant to find this type of business?
- Based on the site's content and authority, would it likely be surfaced?
- Are there obvious barriers (thin content, no schema, poor authority)?

**Test queries to consider:**
- "Best [service] in [city]"
- "How much does [service] cost in [city]?"
- "[Service provider] near me recommendations"
- "What should I look for in a [service provider]?"

**Scoring:**

| Score | Description |
|-------|-------------|
| 9-10 | Strong signals across all criteria. Likely to appear in AI search results for relevant queries. |
| 7-8 | Good signals. May appear for some queries, especially branded or specific ones. |
| 5-6 | Mixed signals. Unlikely to appear in AI results except for branded queries. |
| 3-4 | Weak signals. Very unlikely to appear in AI search results. |
| 1-2 | No AI search readiness. Invisible to AI engines. |

## AEO Scoring Methodology

### Per-Criterion Score: 1-10

Each criterion scored individually with evidence and justification.

### Overall AEO Score

Weighted average of all 6 criteria, mapped to 1-10 scale.

### Letter Grade Mapping

| Score | Grade | Label |
|-------|-------|-------|
| 9.0-10.0 | A+ | AI Search Leader |
| 8.0-8.9 | A | AI Search Ready |
| 7.0-7.9 | B+ | Above Average |
| 6.0-6.9 | B | Moderate Readiness |
| 5.0-5.9 | C+ | Below Average |
| 4.0-4.9 | C | Significant Gaps |
| 3.0-3.9 | D | Major Gaps |
| 1.0-2.9 | F | AI Search Invisible |

### Score Display Format

```
AI Search Readiness: C+ (5.4/10)

Structured Data:     ██░░░░░░░░  3/10  -- No schema markup found
Answer-Ready Content: ████░░░░░░  5/10  -- Some FAQ content, not optimized for extraction
Entity Authority:     ██████░░░░  7/10  -- Strong directory presence, no Knowledge Panel
Topical Authority:    ████░░░░░░  5/10  -- Service pages only, no depth content
Citation-Worthiness:  █████░░░░░  6/10  -- Professional writing, no original data
AI Search Visibility: ████░░░░░░  5/10  -- Mixed signals, limited discoverability
```

## AEO Recommendations Library

Organized by effort level. When writing the action plan, select recommendations based on the specific gaps found.

### Quick Wins (1-2 hours each)

- Add/repair FAQPage schema on existing FAQ content (highest single-page citation lever) -- ensure visible-text/JSON-LD parity
- Stack schema on key pages: add `Article` + `BreadcrumbList` + `Organization` alongside `FAQPage`/`HowTo`
- Rewrite the top of each key page as an answer-first block (40-60 word direct answer)
- Convert section headings to real user questions (H2/H3)
- Add a canonical `Organization` JSON-LD with `sameAs` to authoritative profiles
- Add comparison tables and "what to expect" numbered steps to key pages
- Add `dateModified` + visible "Last updated" to high-value pages
- Validate every JSON-LD block (malformed schema is worse than none)

### Medium Effort (1-2 days each)

- Build a comprehensive FAQ page targeting the brand's priority questions, each answered in 2-4 sentences
- Publish answer-first how-to and comparison content with HowTo/ItemList schema
- Create a cost/pricing guide with specific figures
- Add case studies with quantified outcomes and named experts
- Resolve cross-property fact inconsistencies (single source of truth for name, description, stats)
- Stand up an AI-visibility measurement loop (priority prompt set + tracking)
- Optimize existing content for answer-ready formatting

### High Effort (1-2 weeks each)

- Build content clusters around core topics (pillar + supporting pages) mapped to buyer-journey stages
- Develop original research or data that other sites will cite
- Implement edge-side schema injection (e.g., Cloudflare Worker) for at-scale deployment
- Build authoritative backlinks and editorial mentions through expert contributions and PR
- Develop video content optimized for AI search (transcripts, structured descriptions)
- Pursue Wikipedia/Wikidata entity presence and Knowledge Panel verification

## Analysis & Plan Guidelines for AEO

These guide the AEO Analyst (analysis) and AEO Strategist (plan). The output is internal work product, not a sales deliverable.

1. **Lead with the score.** Open the analysis with the AI Search Readiness score and the single biggest opportunity, criterion by criterion.
2. **Be evidence-based.** Every finding cites something actually observed on the site (or its absence). No generic claims.
3. **Show the gap concretely.** "When a buyer asks ChatGPT '[priority query],' the brand isn't cited -- competitor [Name] is, because they have answer-first content + FAQ schema and the brand doesn't."
4. **Be specific about what's missing.** "No FAQ schema, no answer-first content, no HowTo guides -- AI engines have nothing to extract for questions about [topic]."
5. **Make every finding buildable.** Tie each to a target page and the artifact type that fixes it (schema, answer-content, entity, metadata, content-brief), so it routes cleanly into the plan backlog.
6. **Prioritize by impact vs effort.** Favor the 2026 high-impact levers (schema stacking, answer-first rewrites, FAQ parity, entity/`sameAs`, freshness).
7. **Cover all six criteria** with evidence and recommendations; each gets its own subsection in the analysis.
