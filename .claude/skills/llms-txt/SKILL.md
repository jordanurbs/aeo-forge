---
name: llms.txt Authoring
version: 1.0.0
description: How to generate llms.txt and llms-full.txt, with honest 2026 expectations about adoption. Used by the llms.txt Builder agent. Optional, low-priority artifact -- valued by application/coding agents, ignored by major search/answer crawlers.
---

# llms.txt Authoring Skill

## Set Expectations First (2026 Reality)

`llms.txt` is an **optional, low-priority** artifact. Be honest about this in any plan or manifest entry:

- Google has publicly stated (Mueller, Illyes, 2025) it does **not** support `llms.txt` and has no plans to.
- Large-scale bot-log studies show major search/answer crawlers (`GPTBot`, `PerplexityBot`, `Google-Extended`, `OAI-SearchBot`) overwhelmingly **do not fetch** it (~10% of sites publish it; ~0.1% fetch rate).
- Its **one real use today:** application/coding agents (Claude Desktop, claude.ai, Cursor, Continue, some MCP integrations) respect it in retrieval flows. This makes it genuinely useful for **agent-facing documentation** (docs sites, API references, knowledge bases).
- For crawler **access control**, `robots.txt` is the real standard -- not `llms.txt`.

Generate it when the brand has docs/knowledge content that agents consume, or when the team simply wants the coverage. Never present it as a ranking or citation lever.

## File Format

`llms.txt` is Markdown placed at the site root (`/llms.txt`). Structure:

```markdown
# Brand Name

> One-sentence description of what the brand/site is and who it's for.

Optional short paragraph of additional context (no marketing fluff).

## Docs
- [Getting Started](https://brand.com/docs/getting-started): What it covers
- [API Reference](https://brand.com/docs/api): What it covers

## Guides
- [How to do X](https://brand.com/guides/x): What it covers

## Optional
- [Changelog](https://brand.com/changelog): Lower-priority links go here
```

Rules:
- Start with an H1 (the brand/project name).
- Follow with a `>` blockquote summary.
- Group links under H2 sections; each link is `[Title](absolute-url): short note`.
- The `## Optional` section signals lower-priority links an agent can skip.
- Use absolute URLs.

## llms-full.txt

`llms-full.txt` is a single concatenated Markdown file containing the full text of the key pages referenced in `llms.txt` (or a curated subset). Use it when you want agents to have full content without crawling individual pages. Keep it to genuinely useful reference content; do not dump the entire site.

## Generation Process

1. Read the brand profile (domains, priority topics, docs/knowledge URLs) and the site crawl.
2. Select the pages most useful to an agent answering questions about the brand (docs, guides, key product/service pages, FAQ).
3. Write `llms.txt` with grouped, annotated links.
4. Optionally write `llms-full.txt` with the concatenated Markdown of the highest-value pages.
5. In the manifest, label the artifact: "Optional. Read by application agents (Claude Desktop, Cursor); ignored by major search crawlers. Deploy at site root."
