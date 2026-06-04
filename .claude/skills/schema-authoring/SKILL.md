---
name: Schema Authoring
version: 1.0.0
description: JSON-LD authoring patterns for AEO -- stacked schema graphs, required/recommended properties per type, visible-text parity rules, validation workflow, and paste-ready embed snippets. Used by the Schema Builder, Entity Builder, Metadata Builder, and Artifact Validator agents.
---

# Schema Authoring Skill (JSON-LD for AEO)

This skill defines how to author production-grade, validated JSON-LD that increases the probability of being cited by AI answer engines. It is used at the BUILD stage to generate drop-in artifacts.

## Core Principles

1. **Stack, don't isolate.** Connect multiple types in a single `@graph` per key page rather than emitting one block. A typical key page stacks `Organization` (or `WebSite`), `WebPage`, `BreadcrumbList`, `Article` (or the page's primary type), and `FAQPage`/`HowTo` where the visible content supports it.
2. **Parity is mandatory.** `FAQPage`, `HowTo`, `QAPage`, and `Review` schema MUST mirror visible, human-readable text on the page exactly. Never mark up content that is not visible. When you generate FAQ schema, also generate the matching visible HTML block.
3. **Valid or nothing.** Malformed JSON-LD is a negative trust signal. Every block must be valid JSON and schema.org-conformant before it ships.
4. **Use stable IDs.** Give entities `@id` values (e.g., `https://brand.com/#organization`) so blocks can reference each other across pages and build a coherent knowledge graph.
5. **Be accurate.** Only assert facts that are true and verifiable from the brand profile or the live site. No invented ratings, counts, or credentials.

## Stacked Graph Template (key page)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://brand.com/#organization",
      "name": "Brand Name",
      "url": "https://brand.com/",
      "logo": "https://brand.com/logo.png",
      "sameAs": [
        "https://www.linkedin.com/company/brand",
        "https://www.wikidata.org/wiki/Qxxxx"
      ]
    },
    {
      "@type": "WebPage",
      "@id": "https://brand.com/page/#webpage",
      "url": "https://brand.com/page/",
      "name": "Page Title",
      "isPartOf": { "@id": "https://brand.com/#website" },
      "about": { "@id": "https://brand.com/#organization" },
      "dateModified": "2026-06-04"
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://brand.com/" },
        { "@type": "ListItem", "position": 2, "name": "Page", "item": "https://brand.com/page/" }
      ]
    },
    {
      "@type": "FAQPage",
      "@id": "https://brand.com/page/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is X?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "X is ... (40-60 words, matches the visible answer on the page exactly)."
          }
        }
      ]
    }
  ]
}
```

## Type Reference (required + recommended properties)

| Type | When to use | Required | Recommended |
|------|-------------|----------|-------------|
| `Organization` | Every brand (canonical entity) | `name`, `url` | `logo`, `sameAs`, `description`, `founder`, `foundingDate`, `contactPoint` |
| `LocalBusiness` (subtype) | Physical/local locations | `name`, `address`, `telephone` | `geo`, `openingHoursSpecification`, `priceRange`, `sameAs` |
| `WebSite` | Site-wide | `name`, `url` | `potentialAction` (SearchAction), `publisher` |
| `WebPage` | Each indexed page | `url`, `name` | `dateModified`, `isPartOf`, `about`, `primaryImageOfPage` |
| `Article` / `BlogPosting` | Editorial/blog content | `headline`, `author`, `datePublished` | `dateModified`, `image`, `publisher`, `mainEntityOfPage` |
| `FAQPage` | Pages with visible Q&A | `mainEntity[Question/acceptedAnswer]` | -- (parity required) |
| `HowTo` | Procedural content | `name`, `step[]` | `totalTime`, `supply`, `tool`, `image` |
| `Product` | Product pages | `name` | `offers`, `aggregateRating` (only if real), `brand`, `sku` |
| `Service` | Service offerings | `name`, `provider` | `areaServed`, `serviceType`, `offers` |
| `BreadcrumbList` | Any nested page | `itemListElement[]` | -- |
| `ItemList` | Ranked lists/directories | `itemListElement[]` | `numberOfItems` |
| `Person` | Author/expert bios (E-E-A-T) | `name` | `jobTitle`, `worksFor`, `sameAs`, `knowsAbout`, `alumniOf` |

## Answer Text Rules (for FAQ/HowTo)

- Each answer: a direct, self-contained 40-60 word response.
- First sentence answers the question completely; following sentences add context.
- No marketing fluff, no "contact us to learn more" as the answer.
- The `text`/step value must equal the visible text on the page (parity).

## Paste-Ready Embed Snippet

Wrap each page's graph for direct insertion into `<head>`:

```html
<script type="application/ld+json">
{ ...the @graph object... }
</script>
```

## Validation Workflow (run before shipping)

1. **JSON validity:** parse with a strict parser. Recommended: `python3 -c "import json,sys; json.load(open(sys.argv[1]))" file.json`.
2. **Schema.org conformance:** every node has a valid `@type`; required properties present; correct value types (dates ISO-8601, URLs absolute).
3. **Parity:** for FAQ/HowTo/Review, confirm a matching visible-HTML block was generated.
4. **No fabricated data:** ratings/counts/credentials must trace to the brand profile or site evidence.
5. **IDs resolve:** cross-references (`@id`) used in one block are defined somewhere in the artifact set.

A block that fails any check must be fixed or dropped -- never shipped.

## Output Conventions

- One `.json` file per target page (named by URL slug), containing the page's `@graph`.
- One `.html` snippet per page wrapping the graph in a `<script type="application/ld+json">` tag.
- When FAQ/HowTo schema is generated, also write the matching visible-HTML block to the content artifacts.
- A `schema/INDEX.md` mapping each file to its target page URL and the plan item it satisfies.
