# Presentation theme system

## Purpose

Provide a venue-aware appearance switch without rebuilding slides. Include three modes by default: `light`, `dark`, and `custom`. The custom mode represents the approved brand palette.

## Semantic tokens

Author components with semantic tokens rather than literal colors:

- `--deck-bg`: area outside the stage;
- `--slide-bg`: default slide background;
- `--surface` and `--surface-strong`: cards and emphasis;
- `--text` and `--text-muted`: primary and secondary text;
- `--line`: dividers and borders;
- `--accent` and `--accent-2`: actions and data emphasis;
- `--chart-1` through `--chart-5`: categorical data;
- `--shadow`: theme-appropriate depth;
- `--anchor-bg`, `--anchor-text`, and `--anchor-muted`: intentionally dark opening, divider, or closing slides.

Do not use `filter: invert()` for themes. Do not change geometry, font metrics, or content when switching.

## Theme behavior

- Light: optimized for bright rooms and small screens.
- Dark: optimized for auditoriums and low-light environments.
- Custom: approved brand tokens, not an uncontrolled collection of colors.
- A slide with `data-tone="anchor"` keeps deliberate high contrast for openings, dividers, or closings.

Apply the selected theme before first paint when possible. Switching must preserve current slide, current internal state, notes state, and edit state.

## Custom editor

Expose a compact dialog for background, surface, text, accent, and secondary accent. Validate colors before applying them. Offer a reset to the approved brand defaults. Mark edits as unsaved document changes.

## Persistence and export

- Store the current choice locally for the current deck.
- Serialize the chosen theme and custom tokens into saved HTML.
- Mirror the selection in `presentation-project-data.appearance`.
- PDF and PPTX export use an explicit selected theme; never depend on the viewer's operating-system preference.

## Visual QA

Test every available theme for text contrast, logo treatment, charts, hover/focus states, controls, data labels, and print. Prefer alternate logo assets; when unavailable, place the logo on a controlled neutral surface.
