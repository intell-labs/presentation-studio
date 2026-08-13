# Presentation theme system

## Purpose

Provide a venue-aware appearance switch without rebuilding slides. Include three modes by default: `light`, `dark`, and `custom`. The custom mode represents the approved brand palette. Themes may change neutral backgrounds, surfaces, text polarity, and shadows; they must never substitute, tint, pastelize, or otherwise mutate approved brand colors.

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
- `--brand-primary`, `--brand-secondary`, `--brand-dark`, and `--brand-light`: exact approved brand colors shared unchanged by every theme.

Do not use `filter: invert()` for themes. Do not change geometry, font metrics, or content when switching.

## Theme behavior

- Light: optimized for bright rooms and small screens; key `data-tone="anchor"` slides use a dark inverse treatment.
- Dark: optimized for auditoriums and low-light environments; key `data-tone="anchor"` slides use a light inverse treatment.
- Custom: a curated composition from approved brand tokens, not an uncontrolled collection of colors.
- Brand accent and chart colors remain byte-for-byte equivalent across all three modes. When a color is unsuitable for small text on a given background, choose another exact approved brand color for the text role instead of creating a lighter or darker variant.

Apply the selected theme before first paint when possible. Switching must preserve current slide, current internal state, notes state, and edit state.

## Custom editor

When no brandbook exists, expose a compact dialog for provisional background, surface, text, accent, and secondary accent. When a brandbook or approved palette exists, set `appearance.brand_palette.locked` to `true`, show the palette read-only, ignore stale local overrides, and serialize the exact approved values. Mark permitted edits as unsaved document changes.

## Persistence and export

- Store the current choice locally for the current deck.
- Serialize the chosen theme and custom tokens into saved HTML.
- Mirror the selection in `presentation-project-data.appearance`.
- PDF and PPTX export use an explicit selected theme; never depend on the viewer's operating-system preference.

## Visual QA

Test every available theme for text contrast, logo treatment, charts, hover/focus states, controls, data labels, and print. Fail delivery if `--accent` or `--accent-2` resolves to a color outside the locked brand palette, or if light/dark anchor polarity is not inverted. Prefer alternate logo assets; when unavailable, place the logo on a controlled neutral surface.
