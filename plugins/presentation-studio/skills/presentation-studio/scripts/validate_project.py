#!/usr/bin/env python3
"""Validate Presentation Studio phase gates without external Python packages."""

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
    "visual_exploration", "features", "visual_qa", "motion", "delivery", "approvals",
}

REQUIRED_SLIDE_KEYS = {
    "id", "purpose", "takeaway", "title", "content", "evidence", "visual_form",
    "speaker_notes", "states", "open_questions",
}

NAVIGATION_TYPES = {"required", "on-demand", "speaker-only", "decorative"}
DELIVERY_ROUTE_IDS = {"self-contained-html", "hosted-site", "native-presentation"}
DELIVERY_AVAILABILITY = {"available", "unavailable", "unknown"}
DELIVERY_RECOMMENDATIONS = {"required", "recommended", "conditional", "not-recommended"}


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

    if data.get("schema_version") != "1.4":
        errors.append("schema_version must be 1.4.")

    brand = data.get("brand", {})
    usage_policy = brand.get("usage_policy", {})
    for key in (
        "names", "max_visible_marks_per_slide", "max_text_mentions_when_mark_present",
        "footer", "text_mentions_use_neutral_color", "allow_logo_recolor", "exceptions",
    ):
        if key not in usage_policy:
            errors.append(f"brand.usage_policy is missing {key}.")
    if usage_policy.get("footer") not in {"none", "descriptor-only", "branded-approved"}:
        errors.append("brand.usage_policy.footer is invalid.")

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
    brand_palette = appearance.get("brand_palette", {})
    for token in ("locked", "primary", "secondary", "dark", "light"):
        if token not in brand_palette:
            errors.append(f"appearance.brand_palette is missing {token}.")
    theme_strategy = appearance.get("theme_strategy", {})
    if theme_strategy.get("preserve_brand_colors") is not True:
        errors.append("appearance.theme_strategy must preserve brand colors.")
    if theme_strategy.get("inverse_anchor_slides") is not True:
        errors.append("appearance.theme_strategy must invert anchor-slide polarity.")
    typography = appearance.get("typography", {})
    families = typography.get("families", [])
    if not families:
        errors.append("appearance.typography.families must define at least one approved family.")
    for index, family in enumerate(families, start=1):
        for key in ("id", "label", "stack"):
            if not isinstance(family, dict) or not family.get(key):
                errors.append(f"appearance.typography.families[{index}] is missing {key}.")
    bounds = typography.get("bounds", {})
    for role in ("label", "body", "h3", "h2", "h1"):
        values = bounds.get(role, {})
        minimum, maximum = values.get("min"), values.get("max")
        if not isinstance(minimum, (int, float)) or not isinstance(maximum, (int, float)) or minimum < 10 or maximum > 220 or minimum >= maximum:
            errors.append(f"appearance.typography.bounds.{role} must define a safe min/max range between 10 and 220 px.")
    if brand_palette.get("locked") is True:
        if str(custom_theme.get("accent", "")).lower() != str(brand_palette.get("primary", "")).lower():
            errors.append("Locked custom-theme accent differs from the approved primary brand color.")
        if str(custom_theme.get("accent_2", "")).lower() != str(brand_palette.get("secondary", "")).lower():
            errors.append("Locked custom-theme accent_2 differs from the approved secondary brand color.")

    features = data.get("features", {})
    if features.get("default_view") not in {"audience", "author"}:
        errors.append("features.default_view must be audience or author.")
    required_runtime_features = {
        "author_mode", "editable_text", "preserve_browser_edits", "save_workflow",
        "author_menu_always_visible", "safe_file_binding", "deep_links", "unified_control_cluster", "isolated_previews",
        "mobile_light_controls",
        "visual_geometry_qa", "all_state_rendering", "brand_usage_policy", "brand_palette_lock",
        "typography_spacing_qa", "typography_editor", "typography_bounds",
        "contextual_editor_toolbar", "per_element_text_style", "visual_style_editor",
        "gallery_visual_qa",
    }
    for feature in sorted(required_runtime_features):
        if features.get(feature) is not True:
            errors.append(f"Required runtime feature is not enabled: {feature}")

    visual_qa = data.get("visual_qa", {})
    gallery_qa = data.get("visual_exploration", {}).get("gallery_qa", {})
    required_viewports = {"desktop", "laptop", "phone_portrait", "phone_landscape"}
    configured_viewports = {
        viewport.get("name") for viewport in visual_qa.get("required_viewports", [])
        if isinstance(viewport, dict)
    }
    errors.extend(
        f"Missing required visual QA viewport: {name}"
        for name in sorted(required_viewports - configured_viewports)
    )
    if args.phase == "delivery":
        completed_viewports = set(visual_qa.get("completed", []))
        errors.extend(
            f"Visual QA is not complete: {name}"
            for name in sorted(required_viewports - completed_viewports)
        )
        if visual_qa.get("all_slides_rendered") is not True:
            errors.append("Visual QA did not render every slide.")
        if visual_qa.get("all_states_rendered") is not True:
            errors.append("Visual QA did not render every required state including state zero.")
        if visual_qa.get("safe_areas_passed") is not True:
            errors.append("Visual QA safe-area checks are not complete.")
        if visual_qa.get("typography_spacing_passed") is not True:
            errors.append("Visual QA typography and spacing checks are not complete.")
        if not visual_qa.get("geometry_report"):
            errors.append("Visual QA geometry report is missing.")
        harmony = visual_qa.get("harmony_review", {})
        if harmony.get("status") != "completed":
            errors.append("Visual harmony review is not complete.")
        if not harmony.get("reviewer") or not harmony.get("artifact"):
            errors.append("Visual harmony review must record reviewer and artifact.")
        reviewed_slides = set(harmony.get("reviewed_slides", []))
        planned_slides = {slide.get("id") for slide in data.get("slides", []) if slide.get("id")}
        for slide_id in sorted(planned_slides - reviewed_slides):
            errors.append(f"Visual harmony review is missing slide: {slide_id}")
        if visual_qa.get("issues") or harmony.get("issues"):
            errors.append("Visual QA still contains unresolved issues.")
        if gallery_qa.get("status") not in {"completed", "not-required"}:
            errors.append("Visual exploration gallery QA is not complete.")
        if gallery_qa.get("status") == "completed":
            completed_gallery_viewports = set(gallery_qa.get("completed_viewports", []))
            for name in sorted(required_viewports - completed_gallery_viewports):
                errors.append(f"Gallery QA is not complete: {name}")
            if not gallery_qa.get("report"):
                errors.append("Gallery QA report is missing.")
            if gallery_qa.get("issues"):
                errors.append("Gallery QA still contains unresolved issues.")

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

    route_evaluation = data.get("delivery", {}).get("route_evaluation")
    if route_evaluation is None:
        if args.phase in {"build", "delivery"}:
            warnings.append("Legacy project has no delivery.route_evaluation; confirm the delivery route manually.")
    elif not isinstance(route_evaluation, dict):
        errors.append("delivery.route_evaluation must be an object.")
    else:
        routes = route_evaluation.get("routes", [])
        if not isinstance(routes, list) or not routes:
            errors.append("delivery.route_evaluation.routes must contain at least one route.")
            routes = []
        route_ids: list[str] = []
        for index, route in enumerate(routes, start=1):
            if not isinstance(route, dict):
                errors.append(f"Delivery route {index} must be an object.")
                continue
            raw_route_id = route.get("id")
            route_id = raw_route_id if isinstance(raw_route_id, str) else ""
            route_ids.append(route_id)
            if route_id not in DELIVERY_ROUTE_IDS:
                errors.append(f"Delivery route {index} has an invalid id: {route_id}.")
            if route.get("availability") not in DELIVERY_AVAILABILITY:
                errors.append(f"Delivery route {route_id or index} has invalid availability.")
            if route.get("recommendation") not in DELIVERY_RECOMMENDATIONS:
                errors.append(f"Delivery route {route_id or index} has an invalid recommendation.")
            if "reason" not in route or not isinstance(route.get("reason"), str):
                errors.append(f"Delivery route {route_id or index} must record a reason.")
        if len(route_ids) != len(set(route_ids)):
            errors.append("Delivery route IDs must be unique.")
        if "self-contained-html" not in route_ids:
            errors.append("Delivery routing must evaluate the canonical self-contained HTML route.")

        selected = route_evaluation.get("user_selected", [])
        if not isinstance(selected, list) or not selected:
            errors.append("delivery.route_evaluation.user_selected must contain at least one route.")
            selected = []
        if any(not isinstance(route, str) for route in selected):
            errors.append("Selected delivery routes must be strings.")
        selected_ids = {route for route in selected if isinstance(route, str)}
        invalid_selected = sorted(selected_ids - DELIVERY_ROUTE_IDS)
        errors.extend(f"Invalid selected delivery route: {route}." for route in invalid_selected)
        if "self-contained-html" not in selected_ids:
            errors.append("The canonical self-contained HTML route must remain selected.")
        unavailable = {
            route.get("id") for route in routes
            if isinstance(route, dict) and route.get("availability") == "unavailable"
        }
        errors.extend(
            f"Selected delivery route is unavailable: {route}."
            for route in sorted(selected_ids & unavailable)
        )
        if not isinstance(route_evaluation.get("host"), str):
            errors.append("delivery.route_evaluation.host must be a string.")
        if not isinstance(route_evaluation.get("notes"), list) or any(
            not isinstance(note, str) for note in route_evaluation.get("notes", [])
        ):
            errors.append("delivery.route_evaluation.notes must be an array of strings.")
        if args.phase in {"build", "delivery"}:
            if route_evaluation.get("status") != "completed":
                errors.append("Delivery route evaluation is not complete.")
            if route_evaluation.get("approved") is not True:
                errors.append("Delivery routes are not approved by the user.")
            if not route_evaluation.get("host"):
                errors.append("Delivery route evaluation must record the host.")
            for route in routes:
                if not isinstance(route, dict):
                    continue
                if route.get("availability") == "unknown":
                    errors.append(f"Delivery route availability is unresolved: {route.get('id')}.")
                if not str(route.get("reason", "")).strip():
                    errors.append(f"Delivery route is missing its evaluation reason: {route.get('id')}.")

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
