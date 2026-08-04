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

## Visual

- Every slide fits the fixed stage without scroll.
- No panel overlaps another or enters the navigation safe area.
- Typography remains readable at 1280 x 720 rendering and one phone viewport.
- Density and theme rhythm vary deliberately.
- Charts encode the intended relationship honestly.
- Interactive or hidden states have clear affordances.

## Runtime

- Arrow navigation consumes required internal states correctly.
- `on-demand` and `speaker-only` content does not hijack navigation.
- Deep links open the correct slide and state.
- Menu, editing, save status, and keyboard shortcuts work.
- Light, dark, and custom themes preserve contrast, charts, logos, and layout.
- Mobile controls do not obscure content.
- Reduced motion is supported.
- The document remains readable if animation fails.

## Self-contained check

- No fragile local absolute paths.
- Required images, icons, scripts, CSS, and fonts are embedded or intentionally documented.
- External URLs are limited to approved citations or source links.
- Run `scripts/bundle_html.py` for local assets and `scripts/validate_html.py` afterward.

## Final rendered-text check

Use the current HTML after browser editing:

1. Stop if unsaved changes remain.
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
