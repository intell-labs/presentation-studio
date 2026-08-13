# Quality gates

## Content

- Every claim has evidence, an explicit assumption, or a clear recommendation label.
- Numbers reconcile across slides.
- Dates, currencies, units, names, and acronyms are consistent.
- The narrative leads to the requested decision.
- No slide exists only to fill space.

## Voice

- Titles match the approved speaker profile.
- Copy avoids generic AI phrasing.
- Regional and technical vocabulary is authentic.
- Speaker notes sound spoken, not like a report.

## Brand and assets

- Approved logo version and palette are used.
- Images are sharp at presentation size.
- Official or approved resources replace low-quality placeholders.
- Attribution, confidentiality, and usage constraints are recorded.
- Every slide respects the recorded brand-usage policy. A logo counts as a visible brand mention.
- A slide with a visible logo does not repeat the brand name in its kicker, footer, or decorative text unless an approved exception exists.
- Textual brand mentions use neutral body color and do not imitate or alter the wordmark.

## Visual

- Every slide fits the fixed stage without scroll.
- No panel overlaps another or enters the navigation safe area.
- Typography remains readable at desktop 1440 x 900, laptop 1280 x 720, phone portrait 390 x 844, and phone landscape 844 x 390.
- Every editable text stays within its configured semantic font-size bounds: label, body, H3, H2, or H1. The generic body minimum is 18 px on the fixed 1920 x 1080 stage.
- No rendered text intersects another text block, number badge, circle, card, or other painted surface.
- Multiline headings use a readable line-height range of approximately 0.92–1.32; multiline body copy uses approximately 1.18–1.68 unless an explicit typographic review documents an exception.
- Related text stacks have enough breathing room to scan without becoming disconnected; use `data-qa-text-stack="balanced"` where the relationship matters.
- Density and theme rhythm vary deliberately.
- Charts encode the intended relationship honestly.
- Interactive or hidden states have clear affordances.
- Anchor slides, content slides, and data slides have deliberate visual rhythm; the deck does not repeat one generic card layout.
- Titles, claims, caveats, and calls to action use the approved speaker voice rather than generic AI phrasing.
- Every independent block has a QA region annotation; unannotated absolute-positioned content blocks delivery.
- Text, panels, footers, connectors, decorative rules, and deck chrome do not intersect unless the overlap is explicitly allowed.
- Related connector segments are proportional in length, thickness, color, and axis, and strict connectors terminate at their declared anchors.
- Every flex/grid layout resists intrinsic-width overflow; long labels cannot push siblings outside the stage.
- State zero and every progressive state look intentional and complete. Hidden nodes cannot leave orphan connectors or stranded decoration.
- Lists, processes, tables, and timelines have a deliberate terminal treatment and do not look like unfinished scaffolding.

## Runtime

- Arrow navigation consumes required internal states correctly.
- `on-demand` and `speaker-only` content does not hijack navigation.
- Deep links open the correct slide and state.
- The only desktop chrome is one bottom-right cluster ordered previous, counter, next, menu.
- The icon menu opens up and left, closes on outside click and Escape, and returns focus to its trigger.
- The Author section is always discoverable; its actions switch from audience state into author state before editing or writing.
- Every implemented shortcut is shown beside the matching menu option and matches actual keyboard behavior.
- Clicking an editable text component opens a viewport-safe contextual toolbar that identifies the selected copy and exposes approved family, bounded size, color, emphasis, alignment, reset, and the full typography editor.
- Clicking or double-clicking a safe visual component opens a viewport-safe toolbar for fill, border, radius, shadow, opacity, and reset without making brand marks or connectors generically recolorable.
- The full per-element typography editor opens from the Author menu and exposes approved family, bounded size, weight, leading, tracking, color, alignment, italic, and reset controls.
- Author mode, editing, save status, safe file binding, and keyboard shortcuts work.
- Regeneration through `preserve_edits.py` retains browser-changed copy, per-text styles, and safe visual styles, accepts untouched generator updates, and creates a backup before overwrite.
- Light, dark, and custom themes preserve exact approved brand colors, contrast, charts, logos, and layout; light/dark anchor slides use opposite polarity.
- Mobile portrait and landscape show arrows only and do not obscure content.
- Reduced motion is supported.
- Reduced transparency and increased contrast preferences remain usable.
- The document remains readable if animation fails.
- `python3 scripts/validate_html.py presentation.html --strict` passes; a missing PPT Studio runtime contract blocks delivery.

## Rendered viewport matrix

Static source checks are necessary but insufficient. Render the actual final file and inspect screenshots at all four required sizes:

| View | Size | Required checks |
|---|---:|---|
| Desktop | 1440 x 900 | stage centering, footer alignment, menu anchoring, author and audience modes |
| Laptop | 1280 x 720 | no clipping, readable type, no control overlap |
| Phone portrait | 390 x 844 | uniform stage scaling, arrows only, safe-area clearance |
| Phone landscape | 844 x 390 | arrows only, no viewport clipping, usable 44 px targets |

For each viewport render every slide and every required state, including state zero. Also open every on-demand panel, dialog, theme, and author menu at least once. Sampling representative slides is insufficient. Record completed viewport names, slide/state coverage, geometry report, and harmony review in `visual_qa` before the delivery gate.

When visual exploration produces a comparison gallery, run `scripts/qa_gallery.cjs` on every option at the same four viewports. The initial option must be fully visible without interaction, compact layouts must use one readable column, and each preview must carry an addressable name such as `Opción A-1`.

## Self-contained check

- No fragile local absolute paths.
- Required images, icons, scripts, CSS, and fonts are embedded or intentionally documented.
- External URLs are limited to approved citations or source links.
- Run `scripts/bundle_html.py` for local assets and `scripts/validate_html.py` afterward.

## Final rendered-text check

Use the current HTML after browser editing:

1. Stop if unsaved changes remain or the generator would overwrite the saved browser version.
2. Extract visible text.
3. Review accents, spelling, punctuation, capitalization, agreement, proper names, dates, numbers, currencies, acronyms, terminology, duplicate fragments, and double spaces.
4. Present sensitive corrections as a diff.
5. Apply approved corrections.
6. Re-render because corrected text may change layout.
7. Repeat overflow and navigation checks.

## Security and privacy

- Treat client resources as confidential unless told otherwise.
- Never expose credentials, private source paths, hidden notes, or internal project JSON in public metadata.
- Explain that client-side login is a deterrent, not secure access control; recommend authenticated hosting for real confidentiality.

## Licensing and originality

- Use the original PPT Studio runtime and references.
- Do not bundle source, assets, templates, or instruction files from external presentation repositories.
- Preserve the Apache-2.0 license, `NOTICE`, generator metadata, and discreet About panel in runtime or source distributions.
- Confirm the generator is `PPT Studio by intellbits`, the generator URL is `https://intellbits.com`, and the About panel states that the runtime is Apache-2.0.
- Do not place an intellbits watermark or permanent brand mark on slides unless the user explicitly requests it.
- Follow `TRADEMARKS.md` when naming or branding a fork or commercial wrapper.
- Record approved third-party fonts, images, logos, and their usage constraints in the project contract.

## Delivery report

Report:

- final file and format;
- slide count;
- chosen direction;
- selected features;
- content and text QA status;
- self-contained status;
- known limitations;
- navigation and save instructions.
- viewport matrix results and any remaining caveats.
