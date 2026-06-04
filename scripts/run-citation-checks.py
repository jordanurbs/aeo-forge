#!/usr/bin/env python3
"""Execute a brand's prompt set against AI answer engines and record citations.

This is the deterministic half of Feature #2 (citation tracking). It mirrors the
split used by ``scripts/validate-artifacts.py``: this script does the mechanical
work (load prompts, call engine APIs, run heuristic citation detection, write
dated result files) while the ``citation-tracker`` agent interprets the JSON and
maintains the running scoreboard.

Design constraints (see docs/handoffs/02-citation-tracking.md):
- Keyless-safe. With NO API keys it writes a manual-logging template and exits 0.
  The agent's own WebSearch tool is the keyless "directional proxy"; this script
  cannot call it, so keyless mode produces the template for the human/agent.
- No secrets in the repo. Keys are read from environment variables first, then
  from ``config/brand-profile.md`` (which is gitignored).
- Honest labeling. Every result row is labeled "measured via <engine>" or
  "directional proxy / manual".
- Pure stdlib (``urllib``). No network at import time; all calls happen in main().

Usage:
  python3 scripts/run-citation-checks.py --brand-dir output/<brand-slug>
  python3 scripts/run-citation-checks.py --brand-dir output/<brand-slug> --engines perplexity,openai
  python3 scripts/run-citation-checks.py --brand-dir output/<brand-slug> --write-report
  python3 scripts/run-citation-checks.py --self-check
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO_ROOT / "config" / "brand-profile.md"

ALL_ENGINES = ("perplexity", "openai", "serp")
HTTP_TIMEOUT = 30  # seconds, per request

# Key resolution: env var name(s) first, then brand-profile labels.
ENGINE_KEY_SOURCES: dict[str, dict[str, Any]] = {
    "perplexity": {"env": ("PERPLEXITY_API_KEY",), "profile": ("perplexity api key", "perplexity key")},
    "openai": {"env": ("OPENAI_API_KEY",), "profile": ("openai api key", "openai key")},
    # SERP proxy for Google AI Overviews: SerpAPI preferred, DataForSEO fallback.
    "serp": {
        "env": ("SERPAPI_KEY", "SERPAPI_API_KEY", "DATAFORSEO_KEY"),
        "profile": ("serpapi key", "serpapi api key", "dataforseo key", "dataforseo api key"),
    },
}


# ---------------------------------------------------------------------------
# Small parsing helpers
# ---------------------------------------------------------------------------
def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def domain_of(url_or_host: str) -> str:
    """Normalize a URL or host to a bare lowercase registrable-ish host."""
    value = (url_or_host or "").strip().lower()
    if not value:
        return ""
    if "://" not in value:
        value = "http://" + value
    host = urllib.parse.urlparse(value).netloc
    host = host.split("@")[-1].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return host


def host_matches(brand_domains: list[str], url: str) -> bool:
    host = domain_of(url)
    if not host:
        return False
    for brand in brand_domains:
        if not brand:
            continue
        if host == brand or host.endswith("." + brand) or brand.endswith("." + host):
            return True
    return False


def parse_profile_keys(config_path: Path) -> dict[str, str]:
    """Read API keys from a brand-profile.md ``## API Keys`` section.

    Returns a mapping of lowercased label -> value. Skips placeholder values
    such as ``not provided``/``key``. Never raises if the file is absent.
    """
    keys: dict[str, str] = {}
    if not config_path.exists():
        return keys

    placeholders = {"", "not provided", "none", "n/a", "key", "[key, or \"not provided\"]"}
    for raw in read_text(config_path).splitlines():
        line = raw.strip()
        if not line.startswith("-") or ":" not in line:
            continue
        label, _, value = line.lstrip("-").partition(":")
        label = label.strip().lower()
        value = value.strip().strip("`")
        # Drop bracketed placeholder hints like "[key, or ...]".
        value = re.sub(r"\[.*?\]", "", value).strip()
        if value.lower() in placeholders:
            continue
        if "key" in label and value:
            keys[label] = value
    return keys


def resolve_keys(config_path: Path, env: dict[str, str]) -> dict[str, str]:
    """Return {engine: key} for every engine that has a key available."""
    profile_keys = parse_profile_keys(config_path)
    resolved: dict[str, str] = {}
    for engine, sources in ENGINE_KEY_SOURCES.items():
        value = ""
        for env_name in sources["env"]:
            if env.get(env_name):
                value = env[env_name].strip()
                break
        if not value:
            for label in sources["profile"]:
                if profile_keys.get(label):
                    value = profile_keys[label]
                    break
        if value:
            resolved[engine] = value
    return resolved


def field_from_md(text: str, label: str) -> str:
    """Pull a ``- Label: value`` field from a markdown doc (first match)."""
    pattern = re.compile(rf"^[\-\*\s]*{re.escape(label)}\s*:\s*(.+)$", re.I | re.M)
    match = pattern.search(text)
    if not match:
        return ""
    value = match.group(1).strip().strip("`")
    value = re.sub(r"\[.*?\]", "", value).strip()
    return value


def split_list(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[,;]\s*|\s*\n\s*", value)
    return [p.strip() for p in parts if p.strip()]


# ---------------------------------------------------------------------------
# Brand context loading
# ---------------------------------------------------------------------------
def load_brand_context(brand_dir: Path, config_path: Path) -> dict[str, Any]:
    """Assemble brand name, domains, competitors, and the prompt set.

    Reads from (in order of preference for each field): the run config
    ``plan.md``, the gitignored ``brand-profile.md`` (if present), and the
    competitor analysis research file. Always degrades gracefully.
    """
    plan_md = brand_dir / "plan.md"
    plan_text = read_text(plan_md) if plan_md.exists() else ""
    profile_text = read_text(config_path) if config_path.exists() else ""

    brand_name = (
        field_from_md(plan_text, "Brand")
        or field_from_md(profile_text, "Brand name")
        or brand_dir.name
    )

    primary_domain = (
        field_from_md(plan_text, "Primary domain")
        or field_from_md(profile_text, "Primary domain")
    )
    additional = field_from_md(profile_text, "Additional domains/subdomains")

    brand_domains: list[str] = []
    for candidate in [primary_domain, *split_list(additional)]:
        host = domain_of(candidate)
        if host and host not in brand_domains:
            brand_domains.append(host)

    competitors = load_competitors(brand_dir, profile_text)
    prompts, prompt_source = load_prompt_set(brand_dir, plan_text, profile_text)

    return {
        "brand_name": brand_name,
        "brand_domains": brand_domains,
        "competitors": competitors,
        "prompts": prompts,
        "prompt_source": prompt_source,
    }


def load_competitors(brand_dir: Path, profile_text: str) -> list[dict[str, str]]:
    """Collect competitor names + domains from research + profile."""
    competitors: list[dict[str, str]] = []
    seen: set[str] = set()

    def add(name: str, url: str = "") -> None:
        name = (name or "").strip()
        host = domain_of(url) if url else domain_of(name)
        key = (name.lower(), host)
        if key in seen or (not name and not host):
            return
        seen.add(key)
        competitors.append({"name": name, "domain": host})

    comp_md = brand_dir / "research" / "competitor-analysis.md"
    if comp_md.exists():
        text = read_text(comp_md)
        # Markdown links [Name](https://domain) are the most reliable signal.
        for name, url in re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", text):
            add(name, url)
        # Bare domains mentioned anywhere.
        for url in re.findall(r"https?://[^\s)\]]+", text):
            add("", url)

    profile_comp = field_from_md(profile_text, "Competitors to benchmark against")
    if profile_comp and profile_comp.lower() != "auto-find":
        for item in split_list(profile_comp):
            if item.startswith("http") or "." in item:
                add("", item)
            else:
                add(item)

    return competitors


PROMPT_SET_CANDIDATES = (
    Path("measurement") / "prompt-set.md",
    Path("artifacts") / "measurement" / "prompt-set.md",
)


def load_prompt_set(brand_dir: Path, plan_text: str, profile_text: str) -> tuple[list[str], str]:
    """Return (prompts, source-label). Falls back to priority queries."""
    for rel in PROMPT_SET_CANDIDATES:
        path = brand_dir / rel
        if path.exists():
            prompts = extract_prompts(read_text(path))
            if prompts:
                return prompts, str(rel)

    # Fallbacks: priority/target queries are real buyer questions.
    fallback = (
        field_from_md(plan_text, "Priority queries")
        or field_from_md(profile_text, "Target AI queries (prompts to be cited for)")
        or field_from_md(profile_text, "Target AI queries")
    )
    prompts = split_list(fallback)
    if prompts:
        source = "plan.md priority queries" if field_from_md(plan_text, "Priority queries") else "brand-profile target queries"
        return prompts, source

    return [], "none found"


def extract_prompts(text: str) -> list[str]:
    """Heuristically extract prompt strings from a prompt-set.md.

    Recognizes ``Prompt:`` lines, bolded ``**...**`` questions, quoted
    questions, and list/numbered items that read like questions. De-duplicates
    while preserving order.
    """
    prompts: list[str] = []
    seen: set[str] = set()

    def add(candidate: str) -> None:
        candidate = candidate.strip().strip("`").strip().strip('"').strip()
        candidate = re.sub(r"\s+", " ", candidate)
        if len(candidate) < 8 or len(candidate) > 300:
            return
        key = candidate.lower()
        if key in seen:
            return
        seen.add(key)
        prompts.append(candidate)

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^[\-\*\d\.\)\s]*\**\s*prompt\s*\**\s*:\s*(.+)$", line, re.I)
        if m:
            add(m.group(1))
            continue
        # Explicitly quoted question.
        q = re.match(r'^[\-\*\d\.\)\s]*"(.+\?)"\s*$', line)
        if q:
            add(q.group(1))
            continue
        # Plain list/numbered item that ends in a question mark.
        item = re.match(r"^[\-\*]\s+(.+\?)$", line) or re.match(r"^\d+[\.\)]\s+(.+\?)$", line)
        if item:
            add(re.sub(r"\*\*", "", item.group(1)))

    return prompts


# ---------------------------------------------------------------------------
# HTTP helper (stdlib only)
# ---------------------------------------------------------------------------
def http_json(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Make a JSON HTTP request and return parsed JSON. Raises on transport error."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:  # noqa: S310 (trusted endpoints)
        body = resp.read().decode("utf-8", errors="replace")
    return json.loads(body) if body else {}


# ---------------------------------------------------------------------------
# Engine adapters -- each returns (answer_text, source_urls) or raises
# ---------------------------------------------------------------------------
def query_perplexity(prompt: str, key: str) -> tuple[str, list[str]]:
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "Be precise and cite your sources."},
            {"role": "user", "content": prompt},
        ],
        "return_citations": True,
    }
    data = http_json(
        "POST",
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        payload=payload,
    )
    answer = ""
    choices = data.get("choices") or []
    if choices:
        answer = (choices[0].get("message") or {}).get("content", "") or ""
    sources: list[str] = []
    for url in data.get("citations") or []:
        if isinstance(url, str):
            sources.append(url)
    for item in data.get("search_results") or []:
        if isinstance(item, dict) and item.get("url"):
            sources.append(item["url"])
    return answer, dedupe(sources)


def query_openai(prompt: str, key: str) -> tuple[str, list[str]]:
    """OpenAI Responses API with the web_search tool."""
    payload = {
        "model": "gpt-4o-mini",
        "tools": [{"type": "web_search_preview"}],
        "input": prompt,
    }
    data = http_json(
        "POST",
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {key}"},
        payload=payload,
    )
    answer_parts: list[str] = []
    sources: list[str] = []
    for item in data.get("output") or []:
        if not isinstance(item, dict):
            continue
        for content in item.get("content") or []:
            if not isinstance(content, dict):
                continue
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                answer_parts.append(content["text"])
            for ann in content.get("annotations") or []:
                if isinstance(ann, dict) and ann.get("url"):
                    sources.append(ann["url"])
    # Convenience field some SDKs populate.
    if not answer_parts and data.get("output_text"):
        answer_parts.append(str(data["output_text"]))
    return "\n".join(answer_parts), dedupe(sources)


def query_serp(prompt: str, key: str) -> tuple[str, list[str]]:
    """Google SERP via SerpAPI; closest proxy to Google AI Overviews."""
    params = urllib.parse.urlencode({"engine": "google", "q": prompt, "api_key": key, "num": "10"})
    data = http_json("GET", f"https://serpapi.com/search.json?{params}")
    answer_parts: list[str] = []
    sources: list[str] = []
    overview = data.get("ai_overview") or {}
    for block in overview.get("text_blocks") or []:
        if isinstance(block, dict) and block.get("snippet"):
            answer_parts.append(block["snippet"])
    for ref in overview.get("references") or []:
        if isinstance(ref, dict) and ref.get("link"):
            sources.append(ref["link"])
    for result in data.get("organic_results") or []:
        if isinstance(result, dict) and result.get("link"):
            sources.append(result["link"])
            if not answer_parts and result.get("snippet"):
                answer_parts.append(result["snippet"])
    return " ".join(answer_parts), dedupe(sources)


ENGINE_ADAPTERS = {
    "perplexity": query_perplexity,
    "openai": query_openai,
    "serp": query_serp,
}
ENGINE_LABELS = {
    "perplexity": "measured via Perplexity API",
    "openai": "measured via OpenAI web search",
    "serp": "measured via Google SERP (SerpAPI, AI Overview proxy)",
}


def dedupe(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for v in values:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


# ---------------------------------------------------------------------------
# Citation detection (heuristic) -- documented in the citation-tracking skill
# ---------------------------------------------------------------------------
def detect_citation(
    answer_text: str,
    sources: list[str],
    brand_name: str,
    brand_domains: list[str],
    competitors: list[dict[str, str]],
) -> dict[str, Any]:
    """Return a citation verdict for one engine response.

    Rules (heuristic, string/domain matching with light normalization):
    - source-cited (strongest): a brand domain appears in the source URLs.
    - name-mentioned: the brand name appears in the answer text.
    - position: 1-based index of the first brand source URL (if source-cited).
    - competitors_cited: competitor names/domains found in sources or answer.
    """
    answer_lc = (answer_text or "").lower()

    position = None
    for index, url in enumerate(sources, start=1):
        if host_matches(brand_domains, url):
            position = index
            break
    source_cited = position is not None

    name_mentioned = False
    if brand_name:
        if re.search(rf"\b{re.escape(brand_name.lower())}\b", answer_lc):
            name_mentioned = True

    if source_cited:
        citation_type = "source-cited"
    elif name_mentioned:
        citation_type = "name-mentioned"
    else:
        citation_type = "not-cited"

    competitors_cited: list[str] = []
    for comp in competitors:
        name = (comp.get("name") or "").strip()
        domain = (comp.get("domain") or "").strip()
        hit = False
        if domain and any(host_matches([domain], url) for url in sources):
            hit = True
        elif domain and domain in answer_lc:
            hit = True
        elif name and re.search(rf"\b{re.escape(name.lower())}\b", answer_lc):
            hit = True
        if hit:
            label = name or domain
            if label and label not in competitors_cited:
                competitors_cited.append(label)

    return {
        "cited": source_cited or name_mentioned,
        "citation_type": citation_type,
        "position": position,
        "competitors_cited": competitors_cited,
    }


def summarize_answer(answer_text: str, limit: int = 220) -> str:
    text = re.sub(r"\s+", " ", answer_text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


# ---------------------------------------------------------------------------
# Run orchestration
# ---------------------------------------------------------------------------
def run_measured(context: dict[str, Any], engines: list[str], keys: dict[str, str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for prompt in context["prompts"]:
        for engine in engines:
            row: dict[str, Any] = {
                "prompt": prompt,
                "engine": engine,
                "label": ENGINE_LABELS[engine],
                "status": "ok",
                "cited": None,
                "citation_type": None,
                "position": None,
                "competitors_cited": [],
                "sources": [],
                "answer_summary": "",
                "error": None,
            }
            try:
                answer, sources = ENGINE_ADAPTERS[engine](prompt, keys[engine])
                verdict = detect_citation(
                    answer, sources, context["brand_name"], context["brand_domains"], context["competitors"]
                )
                row.update(verdict)
                row["sources"] = sources
                row["answer_summary"] = summarize_answer(answer)
            except urllib.error.HTTPError as exc:
                detail = ""
                try:
                    detail = exc.read().decode("utf-8", errors="replace")[:200]
                except Exception:  # noqa: BLE001
                    pass
                row["status"] = "error"
                row["error"] = f"HTTP {exc.code}: {detail or exc.reason}"
            except (urllib.error.URLError, TimeoutError) as exc:
                row["status"] = "error"
                row["error"] = f"network error: {exc}"
            except (ValueError, KeyError) as exc:
                row["status"] = "error"
                row["error"] = f"parse error: {exc}"
            results.append(row)
    return results


def run_manual(context: dict[str, Any], engines: list[str]) -> list[dict[str, Any]]:
    """No-key mode: one row per prompt x engine awaiting manual/WebSearch logging."""
    results: list[dict[str, Any]] = []
    for prompt in context["prompts"]:
        for engine in engines:
            results.append(
                {
                    "prompt": prompt,
                    "engine": engine,
                    "label": "directional proxy / manual (no API key)",
                    "status": "manual",
                    "cited": None,
                    "citation_type": None,
                    "position": None,
                    "competitors_cited": [],
                    "sources": [],
                    "answer_summary": "",
                    "error": None,
                }
            )
    return results


def build_summary(results: list[dict[str, Any]], engines: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    overall_cited = 0
    overall_total = 0
    for engine in engines:
        rows = [r for r in results if r["engine"] == engine and r["status"] == "ok"]
        cited = sum(1 for r in rows if r["cited"])
        total = len(rows)
        summary[engine] = {
            "cited": cited,
            "total": total,
            "frequency": round(cited / total, 3) if total else None,
        }
        overall_cited += cited
        overall_total += total
    summary["overall"] = {
        "cited": overall_cited,
        "total": overall_total,
        "frequency": round(overall_cited / overall_total, 3) if overall_total else None,
    }
    return summary


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------
def render_run_md(report: dict[str, Any]) -> str:
    lines = [
        f"# Citation Run: {report['brand']} -- {report['date']}",
        "",
        f"- Mode: **{report['mode']}**",
        f"- Engines attempted: {', '.join(report['engines_attempted']) or 'none'}",
        f"- Prompt source: {report['prompt_source']}",
        f"- Brand domains: {', '.join(report['brand_domains']) or 'none detected'}",
        f"- Source label: `aeo-analysis` (citation detection is heuristic; see citation-tracking skill)",
        "",
    ]

    if report["mode"] == "manual":
        lines += [
            "## Manual Logging Template (no API keys found)",
            "",
            "No engine API keys were found in environment variables or "
            "`config/brand-profile.md`, so this run is **manual / directional**. "
            "Either add a key (Perplexity recommended) and re-run, or have the "
            "`citation-tracker` agent run a directional WebSearch proxy, or paste "
            "each prompt into the engine yourself and fill in the table below.",
            "",
            "For each row record: did the engine **cite the brand domain in its "
            "sources** (strongest), merely **mention the brand by name**, or **not "
            "cite** it? Note any competitors cited instead.",
            "",
            "| Prompt | Engine | Cited? (Y/N) | source-cited / name-only | Competitors cited | Notes |",
            "|--------|--------|--------------|--------------------------|-------------------|-------|",
        ]
        for row in report["results"]:
            prompt = row["prompt"].replace("|", "\\|")
            lines.append(f"| {prompt} | {row['engine']} |  |  |  |  |")
        lines.append("")
        return "\n".join(lines)

    # Measured mode
    lines += ["## Per-Engine Citation Frequency", "", "| Engine | Cited | Total | Frequency |", "|--------|-------|-------|-----------|"]
    for engine in report["engines_attempted"]:
        stats = report["summary"].get(engine, {})
        freq = stats.get("frequency")
        freq_str = f"{freq:.0%}" if isinstance(freq, (int, float)) else "n/a"
        lines.append(f"| {engine} | {stats.get('cited', 0)} | {stats.get('total', 0)} | {freq_str} |")
    overall = report["summary"].get("overall", {})
    overall_freq = overall.get("frequency")
    overall_str = f"{overall_freq:.0%}" if isinstance(overall_freq, (int, float)) else "n/a"
    lines.append(f"| **overall** | {overall.get('cited', 0)} | {overall.get('total', 0)} | {overall_str} |")
    lines += ["", "## Results", "", "| Prompt | Engine | Cited | Type | Pos | Competitors cited | Answer summary |", "|--------|--------|-------|------|-----|-------------------|----------------|"]
    for row in report["results"]:
        prompt = row["prompt"].replace("|", "\\|")
        if row["status"] == "error":
            lines.append(f"| {prompt} | {row['engine']} | ERROR | {row.get('error', '')} | | | |")
            continue
        cited = "yes" if row["cited"] else "no"
        comps = ", ".join(row["competitors_cited"]) or "-"
        summary = (row["answer_summary"] or "").replace("|", "\\|")
        pos = row["position"] if row["position"] is not None else "-"
        lines.append(f"| {prompt} | {row['engine']} | {cited} | {row['citation_type']} | {pos} | {comps} | {summary} |")
    lines.append("")
    return "\n".join(lines)


def render_scoreboard(brand: str, runs_dir: Path) -> str:
    """Deterministic scoreboard draft from all citation-runs/*.json files."""
    runs: list[dict[str, Any]] = []
    for json_path in sorted(runs_dir.glob("*.json")):
        try:
            runs.append(json.loads(read_text(json_path)))
        except (ValueError, OSError):
            continue

    lines = [
        f"# Citation Scoreboard: {brand}",
        "",
        "Running AI-citation frequency across runs. Citation detection is "
        "heuristic (`aeo-analysis` source label). Re-run `/aeo-track` on cadence "
        "(monthly suggested). The `citation-tracker` agent enriches this draft "
        "with trend commentary, top uncited prompts, and competitor wins.",
        "",
        "## Overall Citation Frequency by Run",
        "",
        "| Date | Mode | Overall | Perplexity | OpenAI | SERP |",
        "|------|------|---------|------------|--------|------|",
    ]

    def cell(summary: dict[str, Any], engine: str) -> str:
        stats = (summary or {}).get(engine) or {}
        freq = stats.get("frequency")
        if not isinstance(freq, (int, float)):
            return "-"
        return f"{freq:.0%} ({stats.get('cited', 0)}/{stats.get('total', 0)})"

    for run in runs:
        summary = run.get("summary", {})
        lines.append(
            f"| {run.get('date', '?')} | {run.get('mode', '?')} | "
            f"{cell(summary, 'overall')} | {cell(summary, 'perplexity')} | "
            f"{cell(summary, 'openai')} | {cell(summary, 'serp')} |"
        )

    # Latest run detail: uncited prompts + competitors winning.
    if runs:
        latest = runs[-1]
        uncited = sorted({r["prompt"] for r in latest.get("results", []) if r.get("status") == "ok" and not r.get("cited")})
        comp_wins: dict[str, int] = {}
        for r in latest.get("results", []):
            for comp in r.get("competitors_cited", []):
                comp_wins[comp] = comp_wins.get(comp, 0) + 1

        lines += ["", f"## Latest Run ({latest.get('date', '?')}) -- Gaps", ""]
        if uncited:
            lines.append("**Uncited prompts (citation opportunities):**")
            lines += [f"- {p}" for p in uncited]
        else:
            lines.append("No uncited prompts recorded (or run was manual/empty).")
        lines += ["", "**Competitors winning citations:**"]
        if comp_wins:
            lines += [f"- {name} ({count})" for name, count in sorted(comp_wins.items(), key=lambda kv: -kv[1])]
        else:
            lines.append("- None detected.")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-check (tiny built-in unit test for citation detection)
# ---------------------------------------------------------------------------
def run_self_check() -> int:
    competitors = [{"name": "Competitor X", "domain": "competitorx.com"}]
    checks: list[tuple[str, bool]] = []

    v = detect_citation(
        "Acme Analytics is a strong option.",
        ["https://www.example.com/product", "https://competitorx.com/x"],
        "Acme Analytics",
        ["example.com"],
        competitors,
    )
    checks.append(("brand domain in sources => source-cited", v["citation_type"] == "source-cited" and v["cited"]))
    checks.append(("brand source position is 1", v["position"] == 1))
    checks.append(("competitor detected from source", v["competitors_cited"] == ["Competitor X"]))

    v = detect_citation(
        "You could try Acme Analytics for this.",
        ["https://competitorx.com/x"],
        "Acme Analytics",
        ["example.com"],
        competitors,
    )
    checks.append(("name in text only => name-mentioned", v["citation_type"] == "name-mentioned" and v["cited"]))

    v = detect_citation(
        "Use Competitor X instead.",
        ["https://competitorx.com/x"],
        "Acme Analytics",
        ["example.com"],
        competitors,
    )
    checks.append(("no brand => not-cited", v["citation_type"] == "not-cited" and not v["cited"]))

    checks.append(("domain normalization strips www", domain_of("https://WWW.Example.com:443/x") == "example.com"))
    checks.append(("host_matches subdomain", host_matches(["example.com"], "https://docs.example.com/a")))

    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    if failed:
        print(f"SELF-CHECK: FAILED ({len(failed)} of {len(checks)})")
        return 1
    print(f"SELF-CHECK: PASSED ({len(checks)} checks)")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    import os

    parser = argparse.ArgumentParser(description="Run a brand's prompt set against AI answer engines and record citations.")
    parser.add_argument("--brand-dir", type=Path, help="Path to output/<brand-slug> (or a fixture sample-output dir).")
    parser.add_argument("--engines", default="", help="Comma list: perplexity,openai,serp. Default: all with available keys.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Brand profile path (default: config/brand-profile.md).")
    parser.add_argument("--write-report", action="store_true", help="Also write/update measurement/citation-scoreboard.md (deterministic draft).")
    parser.add_argument("--date", default="", help="Override run date (YYYY-MM-DD); default today.")
    parser.add_argument("--self-check", action="store_true", help="Run built-in citation-detection self-tests and exit.")
    args = parser.parse_args(argv)

    if args.self_check:
        return run_self_check()

    if not args.brand_dir:
        parser.error("--brand-dir is required (unless --self-check).")

    brand_dir: Path = args.brand_dir
    if not brand_dir.exists():
        print(f"ERROR: brand dir not found: {brand_dir}")
        return 2

    run_date = args.date or _dt.date.today().isoformat()
    context = load_brand_context(brand_dir, args.config)

    if not context["prompts"]:
        print("ERROR: no prompts found. Add measurement/prompt-set.md, or Priority queries in plan.md, or Target AI queries in the brand profile.")
        return 2

    keys = resolve_keys(args.config, dict(os.environ))

    requested = [e.strip().lower() for e in args.engines.split(",") if e.strip()]
    if requested:
        unknown = [e for e in requested if e not in ALL_ENGINES]
        if unknown:
            parser.error(f"unknown engine(s): {', '.join(unknown)}. Valid: {', '.join(ALL_ENGINES)}")
    selected = requested or list(ALL_ENGINES)
    available = [e for e in selected if e in keys]

    mode = "measured" if available else "manual"
    if mode == "measured":
        engines_attempted = available
        results = run_measured(context, engines_attempted, keys)
    else:
        # Manual template covers the requested/known engines so the human/agent
        # has a row to fill for each. Default to the priority order.
        engines_attempted = selected
        results = run_manual(context, engines_attempted)

    summary = build_summary(results, engines_attempted) if mode == "measured" else {}

    report = {
        "brand": context["brand_name"],
        "brand_domains": context["brand_domains"],
        "date": run_date,
        "mode": mode,
        "engines_attempted": engines_attempted,
        "engines_available": list(keys.keys()),
        "competitors": context["competitors"],
        "prompt_source": context["prompt_source"],
        "prompt_count": len(context["prompts"]),
        "results": results,
        "summary": summary,
        "detection": "heuristic string/domain matching (source-cited > name-mentioned); see .claude/skills/citation-tracking/SKILL.md",
    }

    runs_dir = brand_dir / "measurement" / "citation-runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    json_path = runs_dir / f"{run_date}.json"
    md_path = runs_dir / f"{run_date}.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_run_md(report), encoding="utf-8")

    if args.write_report:
        scoreboard_path = brand_dir / "measurement" / "citation-scoreboard.md"
        scoreboard_path.write_text(render_scoreboard(context["brand_name"], runs_dir), encoding="utf-8")

    # Stdout summary.
    if mode == "manual":
        print("CITATION RUN: MANUAL MODE (no API keys found)")
        print(f"  Brand: {context['brand_name']}  |  prompts: {len(context['prompts'])}  |  prompt source: {context['prompt_source']}")
        print(f"  Wrote manual-logging template: {md_path}")
        print(f"  Wrote machine-readable skeleton: {json_path}")
        print("  Add a Perplexity/OpenAI/SerpAPI key (env or config/brand-profile.md) and re-run for measured results.")
    else:
        overall = summary.get("overall", {})
        freq = overall.get("frequency")
        freq_str = f"{freq:.0%}" if isinstance(freq, (int, float)) else "n/a"
        print(f"CITATION RUN: MEASURED via {', '.join(engines_attempted)}")
        print(f"  Brand: {context['brand_name']}  |  overall citation frequency: {freq_str} ({overall.get('cited', 0)}/{overall.get('total', 0)})")
        print(f"  Wrote: {json_path}")
        print(f"  Wrote: {md_path}")
        errors = [r for r in results if r["status"] == "error"]
        if errors:
            print(f"  WARNING: {len(errors)} engine call(s) failed; recorded in the run files.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
