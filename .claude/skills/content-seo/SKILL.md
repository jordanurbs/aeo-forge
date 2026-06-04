---
name: Content SEO
version: 1.0.0
description: On-page content analysis framework including topic/keyword gap methodology, content quality and E-E-A-T evaluation, URL structure assessment, blog analysis, and competitor content comparison. Used by the AEO Strategist, Answer-Content Builder, and Content-Brief Builder agents.
---

# Content SEO Skill

This skill provides the framework for evaluating on-page content quality, identifying topic/keyword opportunities, and assessing E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) signals. For an AEO program, content quality bridges what the brand currently communicates with what it must communicate to be extracted and cited by AI answer engines. Topical depth and E-E-A-T are direct inputs to citation-worthiness.

## On-Page Content Analysis Framework

### Step 1: Identify Core Pages

For any business site, identify and analyze these page types:
- **Homepage** -- primary messaging, value proposition, navigation structure
- **Service/Product pages** -- individual service or product descriptions
- **About page** -- company story, team, credentials, trust signals
- **Contact page** -- accessibility, form presence, local info
- **Blog/Resource pages** -- content depth, publishing frequency, topical coverage
- **Location pages** (if local business) -- local content, NAP info

### Step 2: Evaluate Content Quality Per Page

For each core page, assess:

**Content Depth:**
- Word count (thin content = under 300 words for service pages)
- Topic completeness -- does the page fully answer the visitor's likely questions?
- Unique value -- does this page offer something competitors don't?

**Content Freshness:**
- Last modified date (if detectable)
- References to current year/season
- Outdated information (old pricing, discontinued services, past events listed as upcoming)

**Readability:**
- Sentence length (average should be 15-20 words)
- Paragraph length (2-4 sentences ideal for web)
- Use of subheadings to break up content
- Bullet points and lists for scannable content
- Jargon level appropriate for the target audience

**Content Formatting:**
- Headers used to structure content (not just for styling)
- Images support the text (not decorative stock photos)
- Internal links to related pages
- External links to authoritative sources (where appropriate)

### Step 3: Keyword Analysis

**Primary Keyword Identification:**
For each core page, identify what keyword it should target based on:
- Page title and H1
- URL structure
- Content focus
- Business type and location

**Keyword Usage Assessment:**
- Primary keyword in title tag: yes/no
- Primary keyword in H1: yes/no
- Primary keyword in first 100 words: yes/no
- Primary keyword in meta description: yes/no
- Primary keyword in URL: yes/no
- Natural keyword density (not stuffed): yes/no
- Related/semantic keywords present: yes/no

**Keyword Gap Methodology:**

1. **Identify the business's core services/products** from the site
2. **Map expected search terms** a customer would use to find each service
3. **Check which terms the site targets** (visible in titles, H1s, content)
4. **Identify gaps** -- services or terms with no dedicated page or content
5. **Prioritize gaps** by:
   - Search intent alignment (commercial > informational for service businesses)
   - Competition difficulty (local terms easier than national)
   - Business value (high-margin services first)

**Keyword Gap Report Format:**

| Gap | Expected Keyword | Current Status | Priority | Recommendation |
|-----|-----------------|----------------|----------|----------------|
| No dedicated page | "[service] in [city]" | Not targeted | High | Create dedicated service page |
| Thin content | "[service] cost" | Mentioned briefly | Medium | Expand pricing/value section |
| Missing content | "[industry] FAQ" | No FAQ page | Medium | Create FAQ targeting common questions |
| Blog opportunity | "how to choose a [service provider]" | No content | Low | Publish educational blog post |

## E-E-A-T Assessment Framework

E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) is how Google evaluates content quality. For local and small businesses, these signals are critical.

### Experience Signals

Evidence that the content creator has first-hand experience with the topic:
- Case studies with real results
- Before/after examples
- Customer success stories with specifics
- Portfolio or project gallery
- Process descriptions showing hands-on knowledge
- Industry-specific terminology used naturally (not forced)

**Rating:** Strong (multiple signals) / Moderate (1-2 signals) / Weak (none visible)

### Expertise Signals

Evidence of knowledge and skill in the field:
- Author bios with relevant credentials
- Professional certifications or licenses displayed
- Awards or industry recognition
- Educational background relevant to services
- Years of experience mentioned
- Technical depth in service descriptions
- Published thought leadership (blog, guest posts, speaking)

**Rating:** Strong / Moderate / Weak

### Authoritativeness Signals

Evidence that others recognize this business as an authority:
- Reviews on third-party platforms (Google, Yelp, industry-specific)
- Media mentions or press coverage
- Industry association memberships
- Partnerships or affiliations
- Backlink profile quality (inferred from mentions found)
- Social media following and engagement
- Awards from recognized organizations

**Rating:** Strong / Moderate / Weak

### Trustworthiness Signals

Evidence that visitors can trust this business:
- HTTPS (covered in technical SEO)
- Clear contact information (phone, email, address)
- Privacy policy present
- Terms of service present
- Money-back guarantee or satisfaction promise
- Professional design (not spammy or outdated)
- Testimonials with real names (not anonymous)
- BBB rating or equivalent
- Clear pricing or pricing transparency
- No deceptive patterns (hidden fees, misleading claims)

**Rating:** Strong / Moderate / Weak

### E-E-A-T Overall Score

| Rating | Score | Description |
|--------|-------|-------------|
| Strong | 8-10 | Multiple signals across all four categories |
| Moderate | 5-7 | Some signals present but gaps exist |
| Weak | 1-4 | Few or no E-E-A-T signals visible |

## URL Structure Assessment

**Good URL patterns:**
- Short and descriptive: `/services/kitchen-remodeling`
- Contains keywords: `/plumber-chicago`
- Hierarchical: `/blog/category/post-title`
- Lowercase with hyphens

**Problems to flag:**
- Long, parameter-heavy URLs: `/?p=123&cat=5`
- No keyword relevance: `/page1`, `/services1`
- Mixed case or underscores
- Duplicate content from URL variations (with/without trailing slash, www/non-www)
- Excessive depth: `/category/subcategory/sub-subcategory/page`

## Blog/Content Assessment

If the site has a blog or resource section:

**Publishing Cadence:**
- Posts in last 30 days: [count]
- Posts in last 90 days: [count]
- Total posts: [count]
- Rating: Active (monthly+) / Sporadic (quarterly) / Dormant (6+ months) / None

**Content Quality:**
- Average post length: [word count range]
- Topics aligned with business services: yes/partially/no
- Posts target specific keywords: yes/partially/no
- Internal links to service pages: yes/no
- Call to action in posts: yes/no
- Author attribution: yes/no

**Topical Authority:**
- Content clusters present (multiple posts on related topics): yes/no
- Pillar content (comprehensive guides): yes/no
- Supporting content (specific sub-topics): yes/no
- Internal linking between related posts: yes/no

## Competitor Content Comparison Format

When comparing content across competitors, use this format:

| Factor | Brand | Competitor 1 | Competitor 2 | Competitor 3 |
|--------|--------|--------------|--------------|--------------|
| Service pages | [count] | [count] | [count] | [count] |
| Blog posts | [count] | [count] | [count] | [count] |
| Average content depth | [rating] | [rating] | [rating] | [rating] |
| E-E-A-T signals | [rating] | [rating] | [rating] | [rating] |
| Keyword targeting | [rating] | [rating] | [rating] | [rating] |
| Content freshness | [rating] | [rating] | [rating] | [rating] |

## Content SEO Scoring

| Category | Weight | Good (8-10) | Needs Improvement (5-7) | Poor (1-4) |
|----------|--------|-------------|-------------------------|------------|
| Content Depth | 20% | 500+ words on service pages, thorough | 300-500 words, adequate | Under 300 words, thin |
| Keyword Targeting | 25% | Primary keyword in all key positions | Partial targeting | No apparent keyword strategy |
| E-E-A-T Signals | 25% | Strong across all four | Moderate with gaps | Weak or absent |
| Content Freshness | 10% | Updated within 6 months | Updated within 1 year | Over 1 year or no dates |
| URL Structure | 10% | Clean, keyword-rich URLs | Mostly clean | Poor URL structure |
| Blog/Content Marketing | 10% | Active, topically relevant | Sporadic or unfocused | No blog or dormant |

**Overall Content SEO Score:** Weighted average, mapped to 1-10 scale.

## Analysis & Plan Guidelines for Content SEO

1. **Reference actual content.** Quote specific headlines, sentences, or sections from the site. "The About page says 'We are a team of professionals' -- strengthen with named experts, credentials, and quantified case studies to raise E-E-A-T and citation-worthiness."
2. **Frame gaps as buildable plan items.** Tie each gap to a target page and an artifact type (answer-content, content-brief, schema). "No page answers '[priority buyer query]' -- competitors own this answer; create answer-first content + FAQ schema."
3. **Prioritize by AEO impact.** Lead with changes that most improve extractability and citation: answer-first rewrites of high-value pages, topical clusters, original data.
4. **Be specific.** "Add a 6-question FAQ block to /pricing answering the questions buyers ask AI assistants" is actionable. "Improve your content" is not.
5. **Connect content to citation.** "Original data (e.g., a benchmark report) makes the page citation-worthy, so AI engines reference the brand as the source." Avoid sales/conversion framing -- this is an internal build plan.
