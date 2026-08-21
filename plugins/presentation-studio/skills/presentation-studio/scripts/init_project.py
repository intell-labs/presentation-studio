#!/usr/bin/env python3
"""Create the human-editable Presentation Studio project contract and review files."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def build_contract() -> dict:
    return {
        "schema_version": "1.4",
        "workflow": {
            "mode": "new",
            "current_phase": "purpose-audience",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        "project": {
            "title": "",
            "presentation_type": "",
            "language": "es",
            "presentation_date": "",
            "duration_minutes": None,
            "density": "unknown",
        },
        "audience": {
            "description": "",
            "decision_makers": [],
            "prior_knowledge": "",
            "concerns": [],
            "likely_objections": [],
        },
        "objective": {
            "decision_or_action": "",
            "discussion_focus": "",
            "one_day_takeaway": "",
        },
        "resources": [],
        "brand": {
            "confirmed": {},
            "inferred": {},
            "direction_summary": "",
            "usage_policy": {
                "names": [],
                "max_visible_marks_per_slide": 1,
                "max_text_mentions_when_mark_present": 0,
                "footer": "none",
                "text_mentions_use_neutral_color": True,
                "allow_logo_recolor": False,
                "exceptions": [],
            },
        },
        "appearance": {
            "default_theme": "light",
            "available_themes": ["light", "dark", "custom"],
            "brand_palette": {
                "locked": False,
                "primary": "#314cff",
                "secondary": "#00d9c8",
                "dark": "#071b29",
                "light": "#f7f9fb",
            },
            "theme_strategy": {
                "preserve_brand_colors": True,
                "inverse_anchor_slides": True,
            },
            "typography": {
                "families": [
                    {"id": "display", "label": "Título editorial", "stack": "Georgia, 'Times New Roman', serif"},
                    {"id": "body", "label": "Sans de marca", "stack": "'Avenir Next', 'Helvetica Neue', Arial, sans-serif"},
                    {"id": "system", "label": "Sistema", "stack": "system-ui, -apple-system, 'Segoe UI', sans-serif"},
                ],
                "bounds": {
                    "label": {"min": 14, "max": 180},
                    "body": {"min": 18, "max": 64},
                    "h3": {"min": 24, "max": 96},
                    "h2": {"min": 36, "max": 144},
                    "h1": {"min": 48, "max": 180},
                },
            },
            "custom_theme": {
                "name": "Marca",
                "background": "#071b29",
                "surface": "#0d2b3b",
                "text": "#f7f9fb",
                "accent": "#314cff",
                "accent_2": "#00d9c8",
            },
        },
        "communication_style": {
            "speaker_samples": [],
            "language_variant": "",
            "formality": "",
            "directness": "",
            "first_person": "",
            "preferred_terms": [],
            "avoid_terms": [],
            "selected_title_examples": [],
            "user_rewrites": [],
        },
        "expert_mode": {"primary": "", "secondary": [], "audience_side": []},
        "narrative": {"arc": "", "sections": []},
        "research": {
            "gaps": [],
            "sources": [],
            "facts": [],
            "calculations": [],
            "assumptions": [],
            "recommendations": [],
        },
        "slides": [],
        "visual_exploration": {
            "option_count": 3,
            "options": [],
            "selected": None,
            "gallery_qa": {"status": "pending", "report": "", "completed_viewports": [], "issues": []},
        },
        "features": {
            "default_view": "audience",
            "author_mode": True,
            "author_menu_always_visible": True,
            "editable_text": True,
            "preserve_browser_edits": True,
            "save_workflow": True,
            "safe_file_binding": True,
            "deep_links": True,
            "unified_control_cluster": True,
            "isolated_previews": True,
            "mobile_light_controls": True,
            "visual_geometry_qa": True,
            "all_state_rendering": True,
            "brand_usage_policy": True,
            "brand_palette_lock": True,
            "typography_spacing_qa": True,
            "typography_editor": True,
            "typography_bounds": True,
            "contextual_editor_toolbar": True,
            "per_element_text_style": True,
            "visual_style_editor": True,
            "gallery_visual_qa": True,
            "appearance_menu": True,
            "light_theme": True,
            "dark_theme": True,
            "custom_theme": True,
            "presenter_notes": False,
            "presenter_view": False,
            "timer": False,
            "login": False,
            "pdf_export": False,
            "pptx_export": False,
            "generated_illustrations": False,
        },
        "visual_qa": {
            "required_viewports": [
                {"name": "desktop", "width": 1440, "height": 900},
                {"name": "laptop", "width": 1280, "height": 720},
                {"name": "phone_portrait", "width": 390, "height": 844},
                {"name": "phone_landscape", "width": 844, "height": 390},
            ],
            "completed": [],
            "issues": [],
            "all_slides_rendered": False,
            "all_states_rendered": False,
            "safe_areas_passed": False,
            "typography_spacing_passed": False,
            "geometry_report": "",
            "overlap_exceptions": [],
            "harmony_review": {
                "status": "pending",
                "reviewer": "",
                "artifact": "",
                "reviewed_slides": [],
                "issues": [],
            },
        },
        "motion": {"opportunities": [], "approved": [], "rejected": [], "audit": []},
        "delivery": {
            "primary_format": "self-contained-html",
            "self_contained": True,
            "outputs": [],
            "route_evaluation": {
                "status": "pending",
                "host": "",
                "routes": [
                    {
                        "id": "self-contained-html",
                        "availability": "available",
                        "recommendation": "required",
                        "reason": "Canonical Presentation Studio output.",
                    },
                    {
                        "id": "hosted-site",
                        "availability": "unknown",
                        "recommendation": "conditional",
                        "reason": "",
                    },
                    {
                        "id": "native-presentation",
                        "availability": "unknown",
                        "recommendation": "conditional",
                        "reason": "",
                    },
                ],
                "user_selected": ["self-contained-html"],
                "approved": False,
                "notes": [],
            },
        },
        "approvals": {
            "brand": False,
            "voice": False,
            "expert_mode": False,
            "structure": False,
            "content": False,
            "style": False,
            "features": False,
            "final_text": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_directory", type=Path)
    parser.add_argument("--force", action="store_true", help="Replace existing starter files.")
    args = parser.parse_args()
    output = args.output_directory.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    files = {
        output / "presentation-project.json": json.dumps(build_contract(), ensure_ascii=False, indent=2) + "\n",
        output / "content-approved.md": "# Contenido aprobado\n\nPendiente de validación.\n",
        output / "style-decision.json": json.dumps({"selected": None, "notes": ""}, ensure_ascii=False, indent=2) + "\n",
        output / "feature-selection.json": json.dumps(
            {"approved": False, "features": {}, "delivery_routes": {}},
            ensure_ascii=False,
            indent=2,
        ) + "\n",
    }

    existing = [str(path) for path in files if path.exists()]
    if existing and not args.force:
        print("Refusing to replace existing files:")
        for path in existing:
            print(f"- {path}")
        return 2

    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
