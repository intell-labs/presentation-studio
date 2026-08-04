#!/usr/bin/env python3
"""Validate PPT Studio phase gates without external Python packages."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PHASE_GATES = {
    "discovery": ["brand", "voice", "expert_mode"],
    "content": ["brand", "voice", "expert_mode", "structure", "content"],
    "style": ["brand", "voice", "expert_mode", "structure", "content", "style"],
    "build": ["brand", "voice", "expert_mode", "structure", "content", "style", "features"],
    "delivery": ["brand", "voice", "expert_mode", "structure", "content", "style", "features", "final_text"],
}

REQUIRED_TOP_LEVEL = {
    "schema_version", "workflow", "project", "audience", "objective", "resources", "brand",
    "appearance", "communication_style", "expert_mode", "narrative", "research", "slides",
    "visual_exploration", "features", "motion", "delivery", "approvals",
}

REQUIRED_SLIDE_KEYS = {
    "id", "purpose", "takeaway", "title", "content", "evidence", "visual_form",
    "speaker_notes", "states", "open_questions",
}

NAVIGATION_TYPES = {"required", "on-demand", "speaker-only", "decorative"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--phase", choices=PHASE_GATES, default="delivery")
    args = parser.parse_args()
    data = json.loads(args.project.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []

    missing = sorted(REQUIRED_TOP_LEVEL - set(data))
    errors.extend(f"Missing top-level key: {key}" for key in missing)

    if data.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1.")

    appearance = data.get("appearance", {})
    valid_themes = {"light", "dark", "custom"}
    if appearance.get("default_theme") not in valid_themes:
        errors.append("appearance.default_theme must be light, dark, or custom.")
    available_themes = appearance.get("available_themes", [])
    if not available_themes or not set(available_themes).issubset(valid_themes):
        errors.append("appearance.available_themes must contain valid themes.")
    custom_theme = appearance.get("custom_theme", {})
    for token in ("name", "background", "surface", "text", "accent", "accent_2"):
        if not custom_theme.get(token):
            errors.append(f"appearance.custom_theme is missing {token}.")

    approvals = data.get("approvals", {})
    for gate in PHASE_GATES[args.phase]:
        if approvals.get(gate) is not True:
            errors.append(f"Approval gate is not complete: {gate}")

    slides = data.get("slides", [])
    ids = [slide.get("id") for slide in slides]
    if len(ids) != len(set(ids)):
        errors.append("Slide IDs must be unique.")
    if args.phase in {"style", "build", "delivery"} and not slides:
        errors.append("No slides are planned.")

    for index, slide in enumerate(slides, start=1):
        missing_slide_keys = sorted(REQUIRED_SLIDE_KEYS - set(slide))
        errors.extend(f"Slide {index} is missing key: {key}." for key in missing_slide_keys)
        for key in ("id", "purpose", "takeaway", "title", "visual_form"):
            if not slide.get(key):
                errors.append(f"Slide {index} is missing {key}.")
        slide_id = slide.get("id", "")
        if slide_id and not re.fullmatch(r"hoja-[0-9]{2,}", slide_id):
            errors.append(f"Slide {index} has an invalid id: {slide_id}.")
        for state_index, state in enumerate(slide.get("states", []), start=1):
            if not state.get("id"):
                errors.append(f"Slide {slide_id or index}, state {state_index}, is missing id.")
            if state.get("navigation") not in NAVIGATION_TYPES:
                errors.append(
                    f"Slide {slide_id or index}, state {state_index}, has invalid navigation: "
                    f"{state.get('navigation')}."
                )
        if data.get("approvals", {}).get("content") and slide.get("open_questions"):
            warnings.append(f"Slide {slide.get('id', index)} still has open questions.")

    if data.get("delivery", {}).get("primary_format") == "self-contained-html" and not data.get("delivery", {}).get("self_contained"):
        errors.append("Primary format is self-contained HTML but self_contained is false.")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"Project contract passes the {args.phase} gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
