#!/usr/bin/env python3
"""Create the human-editable PPT Studio project contract and review files."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def build_contract() -> dict:
    return {
        "schema_version": "1.1",
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
        "brand": {"confirmed": {}, "inferred": {}, "direction_summary": ""},
        "appearance": {
            "default_theme": "light",
            "available_themes": ["light", "dark", "custom"],
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
        "visual_exploration": {"option_count": 3, "options": [], "selected": None},
        "features": {
            "editable_text": True,
            "save_workflow": True,
            "deep_links": True,
            "discreet_controls_menu": True,
            "mobile_light_controls": True,
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
        "motion": {"opportunities": [], "approved": [], "rejected": [], "audit": []},
        "delivery": {"primary_format": "self-contained-html", "self_contained": True, "outputs": []},
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
        output / "feature-selection.json": json.dumps({"approved": False, "features": {}}, ensure_ascii=False, indent=2) + "\n",
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
