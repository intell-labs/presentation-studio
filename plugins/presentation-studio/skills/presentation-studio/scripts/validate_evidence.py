#!/usr/bin/env python3
"""Validate external QA evidence without confusing automated checks with design approval."""
import json
from pathlib import Path
from design_contract import digest, contract_digest


def evidence_errors(html, project, report_path, review_path):
    errors = []
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        review = json.loads(review_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return [f"evidence.unreadable: {error}"]
    fingerprint = digest(html.read_bytes())
    if report.get("html_sha256") != fingerprint or review.get("html_sha256") != fingerprint:
        errors.append("evidence.stale-html: QA/review belongs to a different HTML revision.")
    if report.get("contract_sha256") != contract_digest(project):
        errors.append("evidence.stale-contract: design decisions changed after QA.")
    if review.get("report_sha256") != digest(report_path.read_bytes()):
        errors.append("evidence.stale-review: visual approval refers to a different QA report.")
    if report.get("failures") or report.get("review"):
        errors.append("evidence.failures: resolve automated failures and review items before delivery.")
    for layer in ("structure_runtime", "geometry", "resources", "decision_fidelity", "editorial_numeric"):
        if report.get("layers", {}).get(layer, {}).get("status") != "passed":
            errors.append(f"evidence.layer: {layer} has not passed.")
    shots = report.get("screenshots", [])
    if not shots:
        errors.append("evidence.screenshots: no rendered evidence; --no-screenshots is diagnostic only.")
    for shot in shots:
        path = Path(shot.get("path", ""))
        if not path.is_absolute():
            path = report_path.parent / path
        if not path.is_file() or digest(path.read_bytes()) != shot.get("sha256"):
            errors.append(f"evidence.screenshot: missing or changed capture {path.name}.")
    labels = {s.get("label") for s in shots}
    runs = report.get("runs", [])
    viewports = {"desktop", "laptop", "phone_portrait", "phone_landscape"}
    for slide in project.get("slides", []):
        count = sum(s.get("navigation") == "required" for s in slide.get("states", []))
        for viewport in viewports:
            for state in range(count + 1):
                if not any(r.get("slide") == slide["id"] and r.get("viewport", {}).get("name") == viewport
                           and r.get("state") == state and r.get("mode") == "audience" and r.get("label") in labels for r in runs):
                    errors.append(f"evidence.coverage: missing {slide['id']} state {state} at {viewport}.")
        for theme in project.get("appearance", {}).get("available_themes", []):
            if not any(r.get("slide") == slide["id"] and r.get("theme") == theme and r.get("label", "").startswith("desktop-theme-") and r.get("label") in labels for r in runs):
                errors.append(f"evidence.theme: missing {theme} capture for {slide['id']}.")
    if review.get("status") != "completed" or not review.get("reviewer"):
        errors.append("evidence.visual-review: visual judgment still pending.")
    if report.get("summary", {}).get("unmeasured") and (not isinstance(review.get("limitations"), str) or not review["limitations"].strip()):
        errors.append("evidence.limitations: unmeasured criteria need explicit review observations/limits.")
    reviews = {s.get("id"): s for s in review.get("slides", [])}
    for slide in project.get("slides", []):
        item = reviews.get(slide["id"], {})
        if item.get("status") != "approved" or any(not isinstance(item.get(k), str) or not item[k].strip()
                for k in ("hierarchy", "spacing", "brand_and_assets", "readability", "contrast", "editorial_numeric")):
            errors.append(f"evidence.visual-review: {slide['id']} needs actual per-slide observations, not a blanket pass.")
    return errors
