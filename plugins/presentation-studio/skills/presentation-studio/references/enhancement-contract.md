# Decision fidelity: new decks and enhancements

Read before modifying an existing deck or translating an approved visual reference.
The contract records this user's decisions; it does not prescribe six logos, two
columns, gradients, or universal symmetry for every presentation.

## 1. Establish the baseline before editing

Identify the canonical saved HTML and generator. If a published version or browser
export is also supplied, compare revisions before choosing the baseline. Preserve
approved text and edits; change only the requested scope. Do not rediscover valid
assets or rebuild a completed deck simply to use a new runtime.

Run `python3 scripts/design_contract.py existing.html --output asset-inventory.json`.
This inventories slide images and inline SVGs, including unlabelled assets; it does
not alter HTML, download resources, or inventory CSS backgrounds. Inspect CSS
backgrounds, external SVG symbols, fonts and image treatments separately. Resolve
unverified assets before claiming they are preserved. Record the baseline HTML hash
and **all** distinct inventory hashes under `design_contract.baseline_sha256` and
`baseline_asset_hashes`. Do not make the inventory from the already-reduced deck.

Before writing, declare `update` (same deliverable), `variant` (independent v2), or
`merge` (combine revisions). A requested executive v2 never replaces v1 by default.
Preserve a common baseline **before** user/agent divergence; record input paths and
hashes. Reconcile only after generating the candidate:

```bash
python3 scripts/preserve_edits.py saved-user.html candidate.html --base common-base.html --scope text --mode variant --output executive-v2.html
```

`--scope text` imports edited copy into the candidate's layout, leaving its CSS,
runtime and inline styles unchanged. `--scope all` also reconciles tracked inline
styles; it does not merge arbitrary stylesheet or JavaScript changes. Without a base,
browser-stamped hashes can identify unchanged fields; ambiguous divergence stops.
Do not resolve conflicts by selecting the newest timestamp or reassigning baselines.
Inspect the JSON report's preserved/modified/removed/added/conflict lists, decide
conflicts with the user when meaning is uncertain, then retry. Deleted or newly
inserted edited IDs may require a deliberate structural integration first.

Overwriting an existing output requires the automatic recoverable backup; variants
require a new path. Maintain original-to-variant slide/content mapping with reasons
for omissions. Validate the final canonical HTML after reconciliation. If a `dist`
copy is required, copy that saved artifact without regeneration, then verify byte
equality with `cmp source/presentation.html dist/presentation.html` (use actual paths).

For each original asset record `keep`, `replace`, or `remove` with a reason. Use
`add` only for new assets. Each retained organization keeps its original usable logo;
reducing a list is not permission to replace its identities with text. Research only
missing/poor resources. Confirm material uncertain client/project associations with
one concise question; a logo or website alone does not prove a business relationship.

```json
{
  "id": "client-a-logo",
  "kind": "logo",
  "decision": "keep",
  "reason": "Client remains in the approved shortlist; original logo is usable.",
  "baseline_sha256": "<inventory fingerprint>",
  "sha256": "<same fingerprint for keep>",
  "slides": ["hoja-07"],
  "source": "approved source asset",
  "display": {"fit": "contain", "padding_px": 20, "radius_px": 24,
              "background": "theme-safe neutral", "usage": "identity"}
}
```

Add `data-asset-id="client-a-logo"` to the actual `<img>` or `<svg>`, not its empty
container. Reusable logo holders use `object-fit:contain`, consistent boxes, and
optical padding per asset. Never stretch, recolor or redraw logos to force uniformity.
Record source/resolution and intended display size; flag third-party sources.
Theme-specific variants need separate IDs, a `themes` list restricting visible use,
reasons and explicit visual review.

## 2. Translate the approved reference into decisions

In `design_contract.composition`, record the reference, adopted/rejected properties
and why: margins, header/body/footer bands, alignment axes, spacing scale and rules
for equivalent elements. Use measurable `checks` only where equivalence is intended:

```json
{"slide":"hoja-07","boxes":["logo-a","logo-b","logo-c"],
 "property":"width","value_px":180,"tolerance_px":2}
```

Properties: width, height, left, right, top, bottom, gap-x, gap-y. Values/tolerances
are fixed-stage pixels. Gap checks use boxes in declared spatial order. A different
optical logo width is not a failure if its container dimensions are intentionally equal.

For deliberate shared bands and spacing, add optional measurable constraints:

```json
{"clearances":[{"slide":"hoja-02","a":"content","b":"footer","min_px":32}],
 "shared_regions":[{"box":"footer","slides":["hoja-02","hoja-03"],
                    "properties":["left","width","height"],"tolerance_px":2}]}
```

These belong in `design_contract.composition`. Footer/brand/chrome spacing is
measured separately from collision detection. Use actual wrapping heights and local,
documented exceptions; do not fix one page with a global offset that breaks another.
Optional `.ps-layout`, `.ps-content`, `.ps-footer` helpers establish three bands, not
a mandatory aesthetic. Text in circles needs `data-qa-shape="ellipse"`: fitting the
rectangular bounding box is insufficient.

In `design_contract.visual_system`, each entry is an object with `decision`
(keep/adapt/remove/not-applicable), `reason`, and `source` (required for keep/adapt).
Record decisions and evidence
for backgrounds, gradients, icons, surfaces and image treatment. Preserve the full
brand system, not just hexadecimal colors. Recover original SVG service icons before
substituting numbers or generic symbols. Keep exact base colors separate from alpha
overlays; gradients are optional brand decisions, not mandatory decoration.

Choose layout from information relationships. Service catalogs group icon, title and
description locally; comparison tables align shared variables. Five services can use
two columns with an intentional sixth empty slot if approved, not a forced sixth item.
Record that choice and its reason in each slide's `visual_form` and purpose.

## 3. Encode roles, themes, cases and readability

Every slide declares `role` (cover/section/content/data/closing) and `tone`
(anchor/content). DOM uses matching `data-slide-role` and `data-tone`. With the
inversion strategy enabled, cover and closing are anchors. QA compares contract to
DOM **before** checking colors, so missing all anchor attributes cannot pass silently.

`appearance.available_themes` is the sole enabled-theme list. It drives menu order,
keyboard cycling, storage fallback, serialization and QA. `["light","dark"]` means
exactly two selectable themes. The brand palette still applies to both; it does not
require a third mode. Never hide extra modes using deck-specific CSS or fork QA.

Cases record `id`, `client`, `project`, `function`, `confirmation` (confirmed/pending),
and `evidence_asset_ids`. Preserve confirmed names verbatim; pending associations
remain in open questions, not presented as verified experience.

Approve `design_contract.readability` for speaker-led, reading-first or mixed use,
including `max_words_per_slide`, `supporting_text_min_px` and reasoned per-slide
exceptions. Suggested starting points, not universal approvals: speaker-led 65 words
and 24–28 px supporting text; reading-first 120 words and 18–24 px. Reduce secondary
copy, split or regroup before shrinking type. These stage checks cannot certify
distance readability: inspect at the expected physical use. Mark screenshots as
illustrative or legible evidence; readable UI details need a crop/zoom if necessary.
Use optional `readability.by_role` overrides (e.g. cover versus data) before per-slide
exceptions. A cover normally needs much less text than a comparison. Do not squeeze
the original narrative into fewer slides without selecting priority and preserving
essential caveats. See `content-clarity.md`.

## 4. Verify the actual final artifact

Separate statuses cover structure/runtime, geometry, resources, decision fidelity,
editorial/numeric checks, and visual judgment. No automated pass implies good
hierarchy, verified business facts or branding. Preservation has its own reconciliation
report. State counts are rendered states, not a count of independent quality criteria.
`validate_html.py --strict` checks asset hashes/identity and slide-role assignment;
`qa_runtime.cjs` also checks visible resources, configured themes, declared alignment
and density. Technical reports always leave visual judgment pending.

Finalize embedded/external decisions, then run QA. Its `report.json` contains the
HTML SHA-256, decision fingerprint and screenshot hashes. Review screenshots and
write a **separate** `visual-review.json`:

```json
{"html_sha256":"<SHA-256 of reviewed HTML>","report_sha256":"<SHA-256 of report.json>",
 "reviewer":"reviewer name","status":"completed","slides":[
   {"id":"hoja-01","status":"approved","hierarchy":"Observed title/evidence order…",
    "spacing":"Observed margins and rhythm…","brand_and_assets":"Observed identities and tones…",
    "readability":"Observed use-specific legibility; limitations…",
    "contrast":"Observed text/surface pairs in each theme, including muted copy and complex backgrounds…",
    "editorial_numeric":"Checked audience copy, figure meaning/units/sources and visible caveats…"}
 ]}
```

Never generate blanket observations or mark screenshots inspected without viewing
them. The delivery validator requires all three files, matching hashes, complete
viewport/theme/state coverage and per-slide observations. Any HTML byte change
invalidates its evidence. Report hashes stay outside HTML to avoid a circular hash.
QA-only metadata may be updated in the external contract; design decisions may not.
List complex paint, unannotated regions and other `summary.unmeasured` criteria in
the visual review's `limitations` and inspect them explicitly. Never label them as
automatically passed. A reviewable draft is not a client-approved delivery; state the
actual gate status rather than treating screenshot generation as acceptance.

Canonical builds must reproduce the candidate. Put layout corrections in the build
source, not a chain of post-generation patches; run edit preservation before QA.
Verify a second build gives the same output and no duplicate IDs/rules/metadata.
Runtime tests wait for observable menu visibility and completed finite animations,
not a guessed sleep. Never copy QA into a project to patch its timing/theme list.

## Migration from schema 1.4

Existing exported HTML does not auto-update. For a requested enhancement only, add
`design_contract`, slide roles/tones and the enabled theme list from approved choices;
set schema to 1.5. Reuse the current protected runtime only if needed, preserve saved
edits and verify unchanged copy/assets. Do not relabel old QA as new evidence.
