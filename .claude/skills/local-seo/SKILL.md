---
name: Local SEO
version: 1.0.0
description: Local SEO methodology covering Google Business Profile, NAP consistency, citations, reviews, local keywords, local pack factors, and scorecard format. Used by the Competitor Researcher agent. OPTIONAL -- applies only to brands with physical locations or geographic service areas; skip for purely-online brands.
---

# Local SEO Skill

**Optional skill.** Use it only when the brand has physical locations or a geographic service area. For purely-online enterprise brands, skip local SEO entirely -- the entity/consistency and answer-content work carries the AEO program instead.

This skill covers local SEO assessment for brands that serve a geographic area. Local signals (Local Pack, Google Maps, location queries) and consistent NAP also feed entity authority, which matters for AI search: AI assistants increasingly surface local recommendations, and a consistent local entity reinforces the brand's single source of truth.

## Google Business Profile (GBP) Audit

### What to Check

**Profile Completeness:**
- Business name: matches website exactly? yes/no
- Address: complete and accurate? yes/no
- Phone number: matches website? yes/no
- Website URL: correct and working? yes/no
- Business category: primary category set? yes/no
- Additional categories: relevant extras added? yes/no
- Business description: filled out? yes/no (max 750 chars)
- Business hours: set and current? yes/no
- Special hours: holidays set? yes/no
- Service area: defined (if service-area business)? yes/no
- Attributes: relevant ones selected? yes/no

**Media:**
- Profile photo: present and professional? yes/no
- Cover photo: present? yes/no
- Additional photos: count and recency
- Videos: any present? yes/no
- Photo quality: professional vs. phone snapshots

**Engagement Features:**
- Posts: recent posts (within 7 days)? yes/no
- Posts frequency: weekly / monthly / sporadic / never
- Q&A: questions answered? yes/no
- Products/Services: listed? yes/no
- Messaging: enabled? yes/no
- Booking: enabled (if applicable)? yes/no

**GBP Scoring:**

| Score | Description |
|-------|-------------|
| 9-10 | Fully optimized: all fields complete, regular posts, photos, active Q&A |
| 7-8 | Well set up: core fields complete, some posts, adequate photos |
| 5-6 | Basic setup: name/address/phone/hours, minimal other info |
| 3-4 | Minimal: claimed but barely filled out |
| 1-2 | Not claimed or not found |

## NAP Consistency Assessment

NAP = Name, Address, Phone. Consistency across the web is a critical local ranking factor.

### Key Directories to Check

**Tier 1 (must check):**
- Google Business Profile
- Bing Places
- Apple Maps
- Yelp
- Facebook Business Page
- BBB (Better Business Bureau)

**Tier 2 (check if relevant):**
- Yellow Pages / YP.com
- Angi (formerly Angie's List)
- HomeAdvisor (home services)
- Healthgrades / Zocdoc (healthcare)
- Avvo / FindLaw (legal)
- TripAdvisor (hospitality)
- OpenTable (restaurants)
- Industry-specific directories

### What to Check Per Directory

- Listed: yes/no
- Business name: exact match / slight variation / wrong
- Address: exact match / variation / wrong / missing
- Phone number: exact match / wrong / missing
- Website URL: correct / wrong / missing
- Business hours: match GBP? yes/no/missing

### NAP Consistency Scoring

| Score | Description |
|-------|-------------|
| 9-10 | Consistent across all Tier 1 directories and most Tier 2 |
| 7-8 | Consistent on Tier 1, some minor variations on Tier 2 |
| 5-6 | Consistent on most Tier 1, noticeable variations elsewhere |
| 3-4 | Inconsistencies on Tier 1 directories |
| 1-2 | Major inconsistencies or missing from most directories |

### NAP Report Format

| Directory | Listed | Name Match | Address Match | Phone Match | URL Present |
|-----------|--------|------------|---------------|-------------|-------------|
| Google Business | Yes | Exact | Exact | Exact | Yes |
| Yelp | Yes | Exact | Missing suite # | Exact | Yes |
| Facebook | Yes | Exact | Exact | Old number | No |
| BBB | No | -- | -- | -- | -- |

## Citations Assessment

Citations are mentions of the business's NAP on other websites (directories, news articles, association sites, etc.).

**What to assess:**
- Total citation count (estimated): high (50+), moderate (20-49), low (1-19), none
- Citation quality: are citations on authoritative sites or low-quality directories?
- Citation accuracy: do the citations have correct, current information?
- Structured vs. unstructured citations

## Reviews Assessment

### Review Metrics

| Platform | Count | Average Rating | Most Recent |
|----------|-------|----------------|-------------|
| Google | [n] | [x.x] / 5 | [date] |
| Yelp | [n] | [x.x] / 5 | [date] |
| Facebook | [n] | [x.x] / 5 | [date] |
| [Industry-specific] | [n] | [x.x] / 5 | [date] |

### Review Quality Assessment

- **Volume**: How many reviews compared to competitors?
- **Recency**: Are reviews recent (within 3 months)?
- **Rating**: Average rating (below 4.0 is a red flag)
- **Response rate**: Does the business respond to reviews? What percentage?
- **Response quality**: Are responses personalized or copy-paste?
- **Negative review handling**: Professional and constructive? Defensive? No response?
- **Review velocity**: Is the review rate increasing, stable, or declining?

### Review Scoring

| Score | Description |
|-------|-------------|
| 9-10 | 50+ reviews, 4.5+ average, recent, business responds to most, handles negatives well |
| 7-8 | 20+ reviews, 4.0+ average, mostly recent, responds to some |
| 5-6 | 10-20 reviews, 3.5+ average, some are older, limited responses |
| 3-4 | Under 10 reviews, or average below 3.5, or very old reviews |
| 1-2 | No reviews or exclusively negative reviews |

## Local Keyword Assessment

### Target Keywords to Evaluate

For any local business, assess visibility for these keyword patterns:
- `[service] in [city]`
- `[service] near me`
- `[service] [city] [state]`
- `best [service] in [city]`
- `[service] cost [city]`
- `emergency [service] [city]` (if applicable)
- `[service] reviews [city]`

### Local Content Assessment

- Location pages: Does the site have city/area-specific pages? yes/no
- Local content: Does the content reference local landmarks, events, or specifics? yes/no
- Local keywords: Are city/region names used naturally in content? yes/no
- Service area pages: If multi-location, does each location have its own page? yes/no

## Local Pack Factors

The Local Pack (3-pack of map results) is driven by three primary factors:

### 1. Relevance
- Business category matches search intent
- GBP description contains relevant keywords
- Website content aligns with search terms

### 2. Distance
- Business proximity to searcher or search location
- Service area defined appropriately

### 3. Prominence
- Review count and quality
- Citation volume and accuracy
- Website SEO strength
- Online authority (backlinks, mentions)

## Local SEO Scorecard Format

Use this format for the Local SEO section of the report:

```markdown
## Local SEO Scorecard

### Overall Local SEO Score: [X]/10

| Category | Score | Key Finding |
|----------|-------|-------------|
| Google Business Profile | [X]/10 | [One-line summary] |
| NAP Consistency | [X]/10 | [One-line summary] |
| Citations | [X]/10 | [One-line summary] |
| Reviews | [X]/10 | [One-line summary] |
| Local Content | [X]/10 | [One-line summary] |
| Local Keywords | [X]/10 | [One-line summary] |
```

## Local SEO Overall Scoring

| Category | Weight |
|----------|--------|
| Google Business Profile | 25% |
| NAP Consistency | 20% |
| Reviews | 20% |
| Citations | 15% |
| Local Content | 10% |
| Local Keywords | 10% |

## Analysis Guidelines for Local SEO

1. **Be specific about which directories.** "Listed on Yelp and Google but missing from BBB, Angi, and Facebook Business" is actionable. "Improve directory presence" is not.
2. **Compare to competitors.** "Competitor [Name] has 87 Google reviews at 4.7 stars vs the brand's 12 at 4.2 -- a gap affecting Local Pack and local AI recommendations."
3. **Reference real review content.** "Three negative reviews mention long wait times -- a specific issue to address."
4. **Flag NAP inconsistencies by directory.** Inconsistent NAP is an entity-consistency problem; route it to the Entity Builder. Show the table of what's right and wrong where.
5. **Skip if not applicable.** For purely-online brands, state that local SEO does not apply and move on -- do not pad the plan with irrelevant local items.
