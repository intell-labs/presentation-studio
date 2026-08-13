#!/usr/bin/env python3
"""Run structural, syntax, runtime, and release checks for PPT Studio."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "presentation-studio"
SKILL = PLUGIN / "skills" / "ppt-presentation-studio"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_json_and_versions(errors: list[str]) -> None:
    paths = [
        ROOT / ".agents" / "plugins" / "marketplace.json",
        ROOT / ".claude-plugin" / "marketplace.json",
        PLUGIN / ".codex-plugin" / "plugin.json",
        PLUGIN / ".claude-plugin" / "plugin.json",
        ROOT / "release" / "manifest.json",
        ROOT / "release" / "vendor-lock.json",
        SKILL / "references" / "project.schema.json",
    ]
    values: dict[Path, dict] = {}
    for path in paths:
        try:
            values[path] = read_json(path)
        except Exception as error:  # noqa: BLE001
            errors.append(f"Invalid JSON {path.relative_to(ROOT)}: {error}")
    if errors:
        return
    expected = values[ROOT / "release" / "manifest.json"]["version"]
    version_paths = [
        PLUGIN / ".codex-plugin" / "plugin.json",
        PLUGIN / ".claude-plugin" / "plugin.json",
    ]
    for path in version_paths:
        version = values[path].get("version")
        if version != expected:
            errors.append(f"Version drift in {path.relative_to(ROOT)}")
    if not isinstance(expected, str) or not re.fullmatch(r"\d+\.\d+\.\d+", expected):
        errors.append("Release version must use plain MAJOR.MINOR.PATCH without date or build suffixes.")
    claude_entry = values[ROOT / ".claude-plugin" / "marketplace.json"]["plugins"][0]
    if claude_entry.get("version") != expected:
        errors.append("Version drift in Claude marketplace.")
    openai_entry = values[ROOT / ".agents" / "plugins" / "marketplace.json"]["plugins"][0]
    if openai_entry.get("source", {}).get("path") != "./plugins/presentation-studio":
        errors.append("OpenAI marketplace source path is invalid.")
    if claude_entry.get("source") != "./plugins/presentation-studio":
        errors.append("Claude marketplace source path is invalid.")


def check_skill(errors: list[str]) -> None:
    skill_md = SKILL / "SKILL.md"
    source = skill_md.read_text(encoding="utf-8")
    if not source.startswith("---\nname: ppt-presentation-studio\n"):
        errors.append("SKILL.md frontmatter is invalid.")
    if source.count("\n---\n") < 1:
        errors.append("SKILL.md frontmatter is not closed.")
    for reference in SKILL.joinpath("references").glob("*.md"):
        if reference.name not in source and reference.name not in {"brand-research.md", "conversation-flow.md"}:
            errors.append(f"Reference is not routed from SKILL.md: {reference.name}")
    disallowed = [
        SKILL / "assets" / "vendor",
        SKILL / "references" / "vendor",
        SKILL / "scripts" / "vendor",
        ROOT / "third_party",
    ]
    for path in disallowed:
        if path.exists():
            errors.append(f"External vendor directory remains: {path.relative_to(ROOT)}")
    lock = read_json(ROOT / "release" / "vendor-lock.json")
    if lock.get("bundled_external_code") is not False:
        errors.append("Reference lock must declare bundled_external_code=false.")
    for item in lock.get("references", []):
        if item.get("included_paths"):
            errors.append(f"External paths are bundled for {item.get('name')}.")


def check_python(errors: list[str]) -> None:
    for path in sorted((ROOT / "scripts").glob("*.py")) + sorted((SKILL / "scripts").glob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as error:
            errors.append(f"Python syntax error in {path.relative_to(ROOT)}: {error}")


def run_command(command: list[str], errors: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        errors.append("Command failed: " + " ".join(command) + "\n" + result.stdout + result.stderr)


def main() -> int:
    errors: list[str] = []
    check_json_and_versions(errors)
    check_skill(errors)
    check_python(errors)
    runtime = SKILL / "assets" / "runtime" / "base-deck.html"
    run_command([sys.executable, str(SKILL / "scripts" / "validate_html.py"), str(runtime), "--strict"], errors)

    with tempfile.TemporaryDirectory() as temporary:
        run_command([sys.executable, str(SKILL / "scripts" / "init_project.py"), temporary], errors)
        project = Path(temporary) / "presentation-project.json"
        if project.exists():
            data = read_json(project)
            if data.get("schema_version") != "1.4":
                errors.append("Starter project schema version is stale.")
            data["project"]["title"] = "Validation deck"
            data["project"]["presentation_type"] = "corporate"
            data["audience"]["description"] = "Decision makers"
            data["audience"]["prior_knowledge"] = "General context"
            data["objective"]["decision_or_action"] = "Approve next step"
            data["objective"]["discussion_focus"] = "Evidence"
            data["objective"]["one_day_takeaway"] = "Clear decision"
            data["expert_mode"]["primary"] = "Presentation strategist"
            data["narrative"]["arc"] = "Context to decision"
            data["slides"] = [{
                "id": "hoja-01",
                "purpose": "Open",
                "takeaway": "Why now",
                "title": "Decision",
                "content": [],
                "evidence": [],
                "visual_form": "hero",
                "speaker_notes": "",
                "states": [],
                "open_questions": [],
            }]
            data["visual_exploration"]["selected"] = "option-a"
            data["visual_exploration"]["gallery_qa"] = {
                "status": "completed",
                "report": "work/gallery-qa/report.json",
                "completed_viewports": ["desktop", "laptop", "phone_portrait", "phone_landscape"],
                "issues": [],
            }
            data["visual_qa"]["completed"] = [
                "desktop", "laptop", "phone_portrait", "phone_landscape"
            ]
            data["visual_qa"]["all_slides_rendered"] = True
            data["visual_qa"]["all_states_rendered"] = True
            data["visual_qa"]["safe_areas_passed"] = True
            data["visual_qa"]["typography_spacing_passed"] = True
            data["visual_qa"]["geometry_report"] = "work/visual-qa/report.json"
            data["visual_qa"]["harmony_review"] = {
                "status": "completed",
                "reviewer": "structural-test",
                "artifact": "work/visual-qa/review.html",
                "reviewed_slides": ["hoja-01"],
                "issues": [],
            }
            data["delivery"]["route_evaluation"].update({
                "status": "completed",
                "host": "validation",
                "approved": True,
            })
            for route in data["delivery"]["route_evaluation"]["routes"]:
                if route["id"] != "self-contained-html":
                    route.update({
                        "availability": "unavailable",
                        "recommendation": "not-recommended",
                        "reason": "Not required by the validation fixture.",
                    })
            data["approvals"] = {key: True for key in data["approvals"]}
            project.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            run_command([
                sys.executable,
                str(SKILL / "scripts" / "validate_project.py"),
                str(project),
                "--phase",
                "delivery",
            ], errors)

    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests" / "structural"))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        errors.append("Structural unit tests failed.")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PPT Studio passes cross-target validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
