# Rendered visual QA

Visual QA has two independent layers. Both are required.

## Layer 1: deterministic geometry

Run:

```bash
node scripts/qa_runtime.cjs presentation.html --project presentation-project.json
```

The script must render every slide at state zero and after each required reveal. It checks all configured viewports in audience mode, every slide in author mode, and every theme on desktop.

Blocking failures include:

- content outside the fixed stage;
- text intersecting other text or a painted visual surface;
- multiline line-height outside readable heading/body bounds;
- font sizes below or above the configured semantic bounds for label, body, H3, H2, and H1;
- annotated text stacks whose elements are too tightly spaced;
- intrinsic flex/grid overflow;
- intersections between independent `data-qa-box` regions;
- text or content intersecting the footer or control cluster;
- visible connectors whose declared endpoints are hidden;
- strict connectors that miss their anchors or related connector segments with inconsistent length, thickness, or axis;
- branded footers or duplicate visible brand mentions that violate `brand.usage_policy`;
- brand-name text using an accent color when neutral text is required;
- a state-zero composition that hides every required progressive element and therefore looks unfinished;
- missing QA annotations on independent visual blocks;
- console errors or broken deep links.

Use `data-qa-overlap="allow"` only for intentional containment. It is not a generic escape hatch. Record every exception in `visual_qa.overlap_exceptions` with the slide, elements, and reason.

The output directory contains `report.json`, `review.html`, and screenshots. `review.html` is a contact-sheet gallery, not a replacement for the JSON gate.

Use `data-qa-text-stack="balanced"` for vertically related labels, headings, and supporting copy. Use `data-qa-connector-group` and `data-qa-connector-geometry="strict"` for diagrams where proportional lines and exact endpoint alignment are part of the visual meaning.

Multiline body copy must normally stay between `1.18` and `1.68` line-height; headings between `0.92` and `1.32`. A short display label may opt into `data-qa-line-height="compact"` (`0.95`–`1.35`), but paragraphs must never use that exception.

The report must also exercise the Author typography dialog and verify that every control is visible, the selected text remains identifiable, approved font families are populated, and the size input exposes a valid semantic min/max range.

Exercise the contextual editor on desktop and phone portrait. Click an editable text component and verify the selected copy, family, bounded size, color, emphasis, alignment, reset, and full-editor route. Click a safe visual component and verify fill, transparent background, border, radius, shadow, opacity, and reset. Both toolbars must stay inside the viewport; desktop controls must not require horizontal scrolling, and compact mode must remain readable as a bottom sheet.

## Layer 2: harmony and completion review

Inspect all final-state screenshots and every state-zero screenshot. Review intermediate states whenever composition changes meaningfully.

Progressive disclosure must not turn state zero into an empty template. Prefer a faint structural preview, reserved visual scaffold, or another composed resting state. Use `data-qa-state-zero="intentional"` only when a deliberately sparse opening has been visually reviewed and its emptiness is the narrative device.

For each slide assess:

1. **Closure:** the slide looks finished, not like a partially populated template.
2. **Balance:** visual mass and negative space feel intentional.
3. **Hierarchy:** title, takeaway, evidence, and action have a clear order.
4. **Alignment:** related elements share deliberate edges or centers.
5. **Rhythm:** spacing and repetition support the information shape.
6. **Connectors:** lines terminate at visible nodes and never cut through text.
7. **Safe areas:** footer and chrome do not compete with content.
8. **Brand restraint:** the brand is present only where it adds orientation or credibility.

Record:

```json
{
  "visual_qa": {
    "all_slides_rendered": true,
    "all_states_rendered": true,
    "safe_areas_passed": true,
    "geometry_report": "work/visual-qa/report.json",
    "harmony_review": {
      "status": "completed",
      "reviewer": "Codex vision",
      "artifact": "work/visual-qa/review.html",
      "reviewed_slides": ["hoja-01"],
      "issues": []
    }
  }
}
```

`needs-review` is not a delivery pass. Resolve or explicitly document every uncertain composition.

## Repair loop

Use a bounded loop:

1. regenerate a candidate;
2. preserve real browser edits;
3. run strict HTML validation;
4. run rendered geometry QA;
5. inspect the gallery;
6. fix layout or brand policy violations;
7. repeat until both layers pass.

Do not shrink all typography as a blanket fix. Prefer better grouping, shorter copy, layout restructuring, or fewer simultaneous elements.
