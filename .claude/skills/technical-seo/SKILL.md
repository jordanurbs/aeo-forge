---
name: Technical SEO
version: 1.0.0
description: Technical SEO methodology including site speed, meta tags, schema markup, crawlability, mobile usability, security, and free API integration patterns for PageSpeed Insights, SSL Labs, W3C Validator, Wayback Machine, and WHOIS. Used by the Web Crawler and API Caller agents to gather the technical signals that feed the AEO analysis and improvement plan.
---

# Technical SEO Skill

This skill covers the technical foundation an AEO program needs: crawlability and clean, fast, parseable pages are prerequisites for AI engines to extract and cite content. It includes manual inspection checklists, scoring criteria, and -- critically -- exact API integration patterns for pulling real metrics from free tools. These signals feed the AEO analysis (PLAN stage); they are not a standalone sales audit.

## API Integration Patterns

These are the five free APIs the API Caller invokes to get real, verifiable data. Each pattern includes the exact curl command, how to parse the response, and what constitutes good/needs-improvement/poor for each metric.

### 1. Google PageSpeed Insights

**Endpoint:** `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`

**Curl command (with optional API key):**
```bash
# With API key (higher rate limits):
curl -s "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://example.com&strategy=mobile&key=YOUR_API_KEY"

# Without API key (lower rate limits, fine for single audits):
curl -s "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://example.com&strategy=mobile"

# Desktop version (run both):
curl -s "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://example.com&strategy=desktop"
```

**Rate limit handling:**
- If no API key: add `sleep 5` between mobile and desktop calls to avoid 429 errors.
- If the first call (mobile) returns HTTP 429: skip the desktop call (both will be rate-limited). Note in tool-data.md that desktop was skipped due to rate limiting.
- If you have an API key, you can run both calls without a pause.

**Key response fields:**
- `lighthouseResult.categories.performance.score` -- Overall performance score (0-1, multiply by 100)
- `lighthouseResult.audits['largest-contentful-paint'].numericValue` -- LCP in milliseconds
- `lighthouseResult.audits['cumulative-layout-shift'].numericValue` -- CLS score
- `lighthouseResult.audits['interaction-to-next-paint'].numericValue` -- INP in milliseconds
- `lighthouseResult.audits['first-contentful-paint'].numericValue` -- FCP in milliseconds
- `lighthouseResult.audits['total-blocking-time'].numericValue` -- TBT in milliseconds
- `lighthouseResult.audits['speed-index'].numericValue` -- Speed Index in milliseconds

**Scoring thresholds:**

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| Performance Score | 90-100 | 50-89 | 0-49 |
| LCP | < 2500ms | 2500-4000ms | > 4000ms |
| CLS | < 0.1 | 0.1-0.25 | > 0.25 |
| INP | < 200ms | 200-500ms | > 500ms |
| FCP | < 1800ms | 1800-3000ms | > 3000ms |
| TBT | < 200ms | 200-600ms | > 600ms |

**What to report:** Overall score (mobile + desktop), each Core Web Vital with its value and rating, specific recommendations from the audit results.

### 2. TLS/SSL Inspection

**Primary method: curl -v (always works, instant results):**
```bash
# Extract TLS/SSL info via curl verbose mode
curl -sv --max-time 10 "https://example.com" 2>&1 | grep -E '(SSL connection|subject:|issuer:|expire date:|TLSv|HTTP/)'
```

**Key fields from curl -v output:**
- `SSL connection using TLSv1.3` -- TLS version
- `subject: CN=example.com` -- Certificate subject
- `issuer: C=US; O=Let's Encrypt; CN=R3` -- Certificate issuer
- `expire date:` -- Certificate expiration
- `HTTP/2 200` or `HTTP/1.1 200` -- Protocol and status

**Bonus method: SSL Labs (single attempt, cached results only):**
```bash
# Try SSL Labs cache ONCE -- do not poll, do not wait
curl -s "https://api.ssllabs.com/api/v3/analyze?host=example.com&fromCache=on&maxAge=24"
```

If SSL Labs returns a cached result with `status: "READY"`, extract the grade from `endpoints[0].grade`. If it returns anything else (DNS, IN_PROGRESS, ERROR, or the API is at capacity), skip it and rely on the curl -v results. Do NOT poll or retry.

**Scoring (based on curl -v findings):**

| Finding | Rating |
|---------|--------|
| TLSv1.3 + valid cert + HTTPS redirect | Excellent |
| TLSv1.2 + valid cert | Good |
| TLSv1.1 or older | Needs Work |
| Expired or self-signed cert | Poor |
| No HTTPS | Critical |

If SSL Labs grade is available from cache, include it as a bonus data point.

**What to report:** TLS version, certificate issuer and expiration, HTTPS redirect status, SSL Labs grade (if available from cache). If SSL Labs was unavailable, note: "Detailed vulnerability assessment requires SSL Labs API, which was unavailable during this audit."

### 3. W3C HTML Validator

**Endpoint:** `https://validator.w3.org/nu/?out=json`

**Curl command:**
```bash
curl -s "https://validator.w3.org/nu/?doc=https://example.com&out=json"
```

**Key response fields:**
- `messages` -- Array of validation messages
- Each message has: `type` (error/warning/info), `message`, `firstLine`, `lastLine`

**How to parse:**
```
Count errors: messages where type === "error"
Count warnings: messages where type === "info" and subType === "warning"
```

**Scoring:**

| Errors | Rating |
|--------|--------|
| 0 | Excellent -- fully valid HTML |
| 1-5 | Good -- minor issues |
| 6-15 | Needs improvement -- noticeable issues |
| 16+ | Poor -- significant HTML problems |

**What to report:** Error count, warning count, top 5 most critical errors with their messages, overall HTML validity rating.

### 4. Wayback Machine

**Endpoint:** `https://archive.org/wayback/available`

**Curl command:**
```bash
curl -s "https://archive.org/wayback/available?url=example.com"
```

**Key response fields:**
- `archived_snapshots.closest.available` -- Whether snapshots exist (true/false)
- `archived_snapshots.closest.timestamp` -- Oldest available snapshot date (YYYYMMDDHHmmss)
- `archived_snapshots.closest.url` -- URL of the snapshot

**What to report:** Whether the site has historical snapshots, approximate first appearance date (indicates domain history/age), number of snapshots if available.

### 5. WHOIS (Fallback Chain)

Try these sources in order. Use the first one that returns valid data:

**Source A: RDAP (preferred -- standardized, no rate limits):**
```bash
curl -s "https://rdap.org/domain/example.com"
```

Key RDAP fields:
- `events` array -- look for `eventAction: "registration"` (created date) and `eventAction: "expiration"` (expiry date)
- `entities` array -- look for `roles: ["registrar"]` for registrar info
- `nameservers` array -- name server list

**Source B: Who-Dat (fallback if RDAP fails):**
```bash
curl -s "https://who-dat.as93.net/example.com"
```

Key Who-Dat fields:
- `domain.created_date` -- Domain registration date
- `domain.expiration_date` -- Domain expiration date
- `registrar.name` -- Registrar name
- `domain.name_servers` -- Name servers

**Source C: whois CLI (last resort):**
```bash
whois example.com
```

Parse the text output for: Creation Date, Expiration Date, Registrar, Name Server lines.

**What to report:** Domain age (years since created), registrar, expiration date (flag if expiring within 90 days), name servers. Note which source provided the data.

---

## Manual Technical SEO Checklist

Beyond the API data, the Web Crawler also performs manual inspection of the HTML. Use WebFetch to load the page and analyze:

### Meta Tags

**Title Tag:**
- Present: yes/no
- Length: [count] characters (optimal: 50-60)
- Contains primary keyword: yes/no
- Unique and descriptive: yes/no
- Rating: Good / Needs Improvement / Missing

**Meta Description:**
- Present: yes/no
- Length: [count] characters (optimal: 150-160)
- Contains primary keyword: yes/no
- Includes call to action: yes/no
- Rating: Good / Needs Improvement / Missing

**Viewport Meta:**
- Present: yes/no (required for mobile)
- Correct value: `width=device-width, initial-scale=1`

**Canonical Tag:**
- Present: yes/no
- Self-referencing: yes/no
- Rating: Good / Missing

**Open Graph Tags:**
- og:title present: yes/no
- og:description present: yes/no
- og:image present: yes/no
- og:url present: yes/no
- Rating: Complete / Partial / Missing

### Heading Structure

- H1 present: yes/no
- H1 count: [number] (should be 1)
- H1 contains primary keyword: yes/no
- Heading hierarchy logical (H1 > H2 > H3, no skips): yes/no
- Total headings: H1:[n], H2:[n], H3:[n], H4+:[n]

### Schema Markup (Structured Data)

Check for JSON-LD or microdata:
- Schema present: yes/no
- Schema types found: [list -- e.g., LocalBusiness, Organization, WebSite, BreadcrumbList, FAQPage, Product, Service]
- Schema valid: yes/no (check for required properties)
- Missing recommended schemas for this business type: [list]

**Recommended schemas by brand type:**
- SaaS / software: Organization, WebSite, SoftwareApplication, Article, FAQPage, BreadcrumbList
- B2B / professional services: Organization, Service, Person (experts), Article, FAQPage, BreadcrumbList
- E-commerce: Product, Organization, BreadcrumbList, FAQPage, ItemList
- Content / media: Organization, Article, Person, FAQPage, BreadcrumbList
- Local/multi-location: LocalBusiness, Organization, BreadcrumbList, FAQPage

For AEO, stack multiple relevant types in a single `@graph` per key page rather than emitting one block (see the schema-authoring skill).

### Crawlability

- robots.txt accessible: yes/no
- robots.txt blocks important pages: yes/no
- XML sitemap present: yes/no (check /sitemap.xml)
- Sitemap referenced in robots.txt: yes/no

### Mobile Usability

- Viewport meta tag present: yes/no
- Responsive design indicators (media queries, flexible layouts): yes/no
- Text readable without zooming: yes/no
- Tap targets appropriately sized: yes/no

### Image Optimization

- Images have alt attributes: [count with / count without]
- Images use modern formats (WebP, AVIF): yes/no
- Images appear to use lazy loading: yes/no
- Large images detected: [any images that appear unoptimized based on URL patterns]

### Security

- HTTPS: yes/no
- Mixed content (HTTP resources on HTTPS page): yes/no
- Security headers present: check for X-Content-Type-Options, X-Frame-Options, Content-Security-Policy

---

## Technical SEO Scoring

| Category | Weight | Good (8-10) | Needs Improvement (5-7) | Poor (1-4) |
|----------|--------|-------------|-------------------------|------------|
| Site Speed (PageSpeed API) | 20% | Score 90+ | Score 50-89 | Score <50 |
| Core Web Vitals | 15% | All green | 1-2 yellow | Any red |
| SSL/Security | 10% | Grade A/A+ | Grade B | Grade C or lower |
| Meta Tags | 15% | All present, optimized | Most present | Missing critical tags |
| Heading Structure | 10% | Logical hierarchy | Minor issues | No H1 or broken hierarchy |
| Schema Markup | 10% | Relevant schemas present | Partial | No schema |
| HTML Validity | 5% | 0-5 errors | 6-15 errors | 16+ errors |
| Crawlability | 5% | Sitemap + robots.txt | One missing | Both missing |
| Mobile Usability | 5% | Fully responsive | Some issues | Not mobile-friendly |
| Image Optimization | 5% | Alt tags, modern formats | Partial optimization | No optimization |

**Overall Technical SEO Score:** Weighted average, mapped to 1-10 scale.

---

## Analysis Guidelines for Technical SEO

When recording technical findings for the AEO analysis and plan:

1. **Lead with the data.** State the actual metric (PageSpeed score, SSL grade, error count), then interpret it.
2. **Reference the specific page.** "The homepage scored 67 on mobile PageSpeed" not "the site has room for improvement."
3. **Tie it to AEO impact where relevant.** Slow, invalid, or uncrawlable pages are harder for AI engines to fetch, parse, and cite. Note when a technical gap blocks AEO (e.g., "render-blocked content hides the answer text from crawlers").
4. **Produce buildable findings.** Frame each as a candidate plan item with a target page and the artifact type that fixes it (e.g., metadata, schema), so the AEO Strategist can route it.
5. **Cite the source + date.** "(Source: Google PageSpeed Insights API, [date])" / "(Source: SSL Labs, Grade A)". Never fabricate a metric.
