#!/usr/bin/env python3
"""Deterministic checks for generated AEO artifacts.

Usage:
  python3 scripts/validate-artifacts.py output/<brand-slug>
  python3 scripts/validate-artifacts.py output/<brand-slug> --write-report
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any


AEO_ID_RE = re.compile(r"\bAEO-\d+\b")
SOURCE_LABELS = {
    "brand-profile",
    "site-crawl",
    "tool-data",
    "competitor-analysis",
    "aeo-analysis",
    "inference",
}
SOURCE_RE = re.compile(r"\b(" + "|".join(sorted(SOURCE_LABELS)) + r")\b")
EXPECTED_BY_ARTIFACT_TYPE = {
    "answer-content": ("artifacts/content/*.md", "artifacts/content/*.html"),
    "schema": ("artifacts/schema/*.json", "artifacts/schema/INDEX.md"),
    "metadata": ("artifacts/metadata/meta-tags.md",),
    "entity": ("artifacts/entity/knowledge-graph.json", "artifacts/entity/consistency-report.md"),
    "measurement": (
        "artifacts/measurement/prompt-set.md",
        "artifacts/measurement/measurement-plan.md",
        "artifacts/measurement/bot-log-snippet.md",
    ),
    "content-brief": ("artifacts/content-briefs/*.md",),
    "llms-txt": ("artifacts/llms.txt",),
    "edge-injection": ("artifacts/edge/*",),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_tags(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return normalize(value)


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def selected_item_ids(plan_md: Path) -> set[str]:
    if not plan_md.exists():
        return set()

    text = read_text(plan_md)
    match = re.search(r"^## Build Selection\b(?P<body>.*?)(?:^## |\Z)", text, flags=re.M | re.S)
    if match:
        return set(AEO_ID_RE.findall(match.group("body")))

    return set()


def selected_item_types(plan_md: Path, aeo_plan_md: Path) -> dict[str, str]:
    """Map selected AEO item IDs to artifact types from the approval-gate plan."""
    selected_ids = selected_item_ids(plan_md)
    if not selected_ids or not aeo_plan_md.exists():
        return {}

    item_types: dict[str, str] = {}
    header_cells: list[str] = []
    for line in read_text(aeo_plan_md).splitlines():
        if line.startswith("|") and "Artifact type" in line:
            header_cells = [normalize(cell) for cell in line.strip().strip("|").split("|")]
            continue

        if not line.startswith("| AEO-"):
            continue

        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if not header_cells or len(cells) < 2:
            continue

        item_id = cells[0]
        try:
            artifact_type_index = header_cells.index("artifact type")
        except ValueError:
            continue
        if artifact_type_index >= len(cells):
            continue

        artifact_type = cells[artifact_type_index]
        if item_id in selected_ids:
            item_types[item_id] = artifact_type

    return item_types


def artifact_files(artifacts_dir: Path) -> list[Path]:
    if not artifacts_dir.exists():
        return []

    return sorted(
        path
        for path in artifacts_dir.rglob("*")
        if path.is_file()
        and path.name != "validation.md"
        and path.suffix.lower() in {".json", ".md", ".html", ".txt", ".js"}
    )


def iter_graph_nodes(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        graph = data.get("@graph")
        if isinstance(graph, list):
            return [node for node in graph if isinstance(node, dict)]
        return [data]
    if isinstance(data, list):
        return [node for node in data if isinstance(node, dict)]
    return []


def schema_text_values(node: dict[str, Any]) -> list[str]:
    values: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in {"text", "name", "description", "headline", "answer"}:
                    if isinstance(nested, str):
                        values.append(nested)
                walk(nested)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(node)
    return values


def find_nearest_visible_text(schema_path: Path, artifacts_dir: Path) -> str:
    candidates = [
        schema_path.with_suffix(".html"),
        schema_path.with_suffix(".md"),
        artifacts_dir / "content" / f"{schema_path.stem}.html",
        artifacts_dir / "content" / f"{schema_path.stem}.md",
        artifacts_dir / "content" / f"{schema_path.stem}-faq.html",
        artifacts_dir / "content" / f"{schema_path.stem}-faq.md",
        artifacts_dir / "content" / "homepage-faq.html",
        artifacts_dir / "content" / "homepage-faq.md",
    ]

    text_parts: list[str] = []
    for candidate in candidates:
        if candidate.exists():
            text_parts.append(strip_tags(read_text(candidate)))

    return " ".join(text_parts)


def matching_files(root: Path, pattern: str) -> list[Path]:
    return sorted(root.glob(pattern))


def render_report(errors: list[str], warnings: list[str]) -> str:
    status = "BLOCKED" if errors else "PASSED"
    lines = [
        "# Artifact Validation Report",
        "",
        f"Validation: **{status}**",
        "",
        "## Errors",
        "",
    ]

    if errors:
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings", ""])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")

    lines.append("")
    return "\n".join(lines)


def validate_run(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    plan_md = root / "plan.md"
    aeo_plan_md = root / "plan" / "aeo-plan.md"
    artifacts_dir = root / "artifacts"

    if not plan_md.exists():
        errors.append(f"Missing run config: {plan_md}")
    if not aeo_plan_md.exists():
        errors.append(f"Missing AEO plan: {aeo_plan_md}")
    if not artifacts_dir.exists():
        errors.append(f"Missing artifacts directory: {artifacts_dir}")
        return errors, warnings

    selected_ids = selected_item_ids(plan_md)
    if not selected_ids:
        warnings.append("No selected AEO item IDs found under ## Build Selection in plan.md.")
    selected_types = selected_item_types(plan_md, aeo_plan_md)

    files = artifact_files(artifacts_dir)
    if not files:
        errors.append(f"No artifact files found in {artifacts_dir}.")
        return errors, warnings

    artifact_text_by_file = {path: read_text(path) for path in files}
    all_artifact_text = "\n".join(artifact_text_by_file.values())

    for item_id in sorted(selected_ids):
        if item_id not in all_artifact_text:
            errors.append(f"Selected item {item_id} is not referenced by any artifact.")

    for item_id in sorted(selected_ids):
        artifact_types = [
            value.strip()
            for value in selected_types.get(item_id, "").split(",")
            if value.strip()
        ]
        if not artifact_types:
            warnings.append(f"Selected item {item_id} has no parsed artifact type in plan/aeo-plan.md.")
            continue

        for artifact_type in artifact_types:
            expected_patterns = EXPECTED_BY_ARTIFACT_TYPE.get(artifact_type)
            if not expected_patterns:
                if artifact_type != "off-site":
                    warnings.append(f"Selected item {item_id} uses unknown artifact type: {artifact_type}.")
                continue

            if not any(matching_files(root, pattern) for pattern in expected_patterns):
                errors.append(
                    f"Selected item {item_id} ({artifact_type}) has no expected artifact files "
                    f"matching: {', '.join(expected_patterns)}."
                )

    for path, text in artifact_text_by_file.items():
        rel_path = path.relative_to(root)
        if not AEO_ID_RE.search(text):
            errors.append(f"{rel_path} does not reference an AEO item ID.")
        if path.suffix.lower() in {".json", ".md", ".html", ".txt"} and not SOURCE_RE.search(text):
            errors.append(f"{rel_path} does not include a recognized evidence/source label.")

    person_ids_by_name: dict[str, set[str]] = {}
    for json_path in sorted(artifacts_dir.rglob("*.json")):
        rel_path = json_path.relative_to(root)
        try:
            data = json.loads(read_text(json_path))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel_path} is invalid JSON: {exc}")
            continue

        nodes = iter_graph_nodes(data)
        if json_path.parent.name == "schema":
            if not isinstance(data, dict) or "@graph" not in data:
                errors.append(f"{rel_path} should use a stacked @graph for page schema.")
            if not nodes:
                errors.append(f"{rel_path} has no schema nodes.")

        for node in nodes:
            node_type = normalize(node.get("@type"))
            if node_type == "webpage" and "primaryEntity" in node:
                errors.append(f"{rel_path} uses non-standard WebPage.primaryEntity; use mainEntity/about instead.")

            if node_type == "person" and node.get("name") and node.get("@id"):
                person_ids_by_name.setdefault(normalize(node["name"]), set()).add(str(node["@id"]))

            founder = node.get("founder")
            if isinstance(founder, dict) and founder.get("name") and founder.get("@id"):
                person_ids_by_name.setdefault(normalize(founder["name"]), set()).add(str(founder["@id"]))

        visible_text = find_nearest_visible_text(json_path, artifacts_dir)
        parity_nodes = [
            node
            for node in nodes
            if normalize(node.get("@type")) in {"faqpage", "howto"}
            or normalize(node.get("@type")).replace(" ", "") in {"faqpage", "howto"}
        ]
        for node in parity_nodes:
            if not visible_text:
                errors.append(f"{rel_path} contains FAQ/HowTo schema but no nearby visible HTML/Markdown was found.")
                continue
            for value in schema_text_values(node):
                normalized = normalize(value)
                if normalized and len(normalized) > 24 and normalized not in visible_text:
                    errors.append(f"{rel_path} may have schema/visible-text parity drift: {value[:80]!r}")

    for name, person_ids in sorted(person_ids_by_name.items()):
        if len(person_ids) > 1:
            errors.append(f"Person entity {name!r} uses inconsistent @id values: {', '.join(sorted(person_ids))}.")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated AEO artifacts.")
    parser.add_argument("output_dir", type=Path, help="Path to output/<brand-slug>")
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write artifacts/validation.md with deterministic validation results.",
    )
    args = parser.parse_args()

    root = args.output_dir
    errors, warnings = validate_run(root)
    if args.write_report:
        report_path = root / "artifacts" / "validation.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(render_report(errors, warnings), encoding="utf-8")

    if errors:
        print("VALIDATION: BLOCKED")
        for error in errors:
            print(f"ERROR: {error}")
    else:
        print("VALIDATION: PASSED")

    for warning in warnings:
        print(f"WARNING: {warning}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
