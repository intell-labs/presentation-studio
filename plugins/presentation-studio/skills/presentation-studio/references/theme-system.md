# Presentation theme system

## Purpose

Provide a venue-aware appearance switch without rebuilding slides. Use `appearance.available_themes` as the sole ordered list of selectable modes, with `default_theme` included in that list. The starter offers `light`, `dark`, and `custom`; retain only the modes approved for this deck. The brand palette applies to every enabled mode and does not require a custom mode. Themes may change neutral backgrounds, surfaces, text polarity, and shadows; they must never substitute, tint, pastelize, or otherwise mutate approved brand colors.

## Semantic tokens

Author components with semantic tokens rather than literal colors:

- `--deck-bg`: area outside the stage;
- `--slide-bg`: default slide background;
- `--surface` and `--surface-strong`: cards and emphasis;
- `--text` and `--text-muted`: primary and secondary text;
- `--local-text`, `--local-muted`, `--local-accent-readable`: foregrounds on the actual slide/card surface; inverse anchors use their own readable accent, not the global theme accent;
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
- Brand accent and chart base colors remain byte-for-byte equivalent across all enabled modes. Text roles are independent: when an accent fails contrast, use a readable local neutral or another verified approved color. Do not force a brand accent into small text. Any approved accessible text-color variant is a separate semantic token, never a replacement for the brand base color.

Apply the selected theme before first paint when possible. Switching must preserve current slide, current internal state, notes state, and edit state.

## Custom editor

When no brandbook exists, expose a compact dialog for provisional background, surface, text, accent, and secondary accent. When a brandbook or approved palette exists, set `appearance.brand_palette.locked` to `true`, show the palette read-only, ignore stale local overrides, and serialize the exact approved values. Mark permitted edits as unsaved document changes.

## Persistence and export

- Store the current choice locally for the current deck. A stale disabled choice resolves to the approved default, never re-enables an extra mode.
- The enabled list drives menu, keyboard cycle, serialization and QA. Palette editing must not activate a disabled theme.
- Serialize the chosen theme and custom tokens into saved HTML.
- Mirror the selection in `presentation-project-data.appearance`.
- PDF and PPTX export use an explicit selected theme; never depend on the viewer's operating-system preference.

## Visual QA

Test every available theme for text contrast, logo treatment, charts, hover/focus states, controls, data labels, and print. Fail delivery if `--accent` or `--accent-2` resolves to a color outside the locked brand palette, or if light/dark anchor polarity is not inverted. Prefer alternate logo assets; when unavailable, place the logo on a controlled neutral surface.

### Mandatory contrast gate

- Evaluate each text/surface pair, not just "light theme" versus "dark theme". A dark card on a white slide still needs its own light foreground; an inverse light card in dark mode needs dark text. Inherit paired local foreground tokens and reset them when changing a container's background.
- Require at least **4.5:1 for normal text** and **3:1 for large text** (24 CSS px, or 18.66 px bold, at rendered scale). These are minimums, not a reason to fade supporting copy to the threshold. Muted text, labels, footnotes and accents must also pass. Prefer stronger contrast for projected presentations.
- Check the effective background and painted foreground after transparency and inheritance. A contrast ratio for the brand hex codes alone proves nothing about a tinted card, photo or highlighted state.
- Test default, hover, focus and selected states where styles change, every enabled theme, and saved/reopened manual color edits. Do not silently rewrite the user's chosen colors; flag failures and patch the scoped text/surface pairing during an authorized enhancement.
- For photos, gradients and complex overlays, inspect the area behind the entire text. Prefer a controlled opaque text surface or a verified scrim when readability varies. Unmeasured contrast stays pending; an absence of automatic failures is not approval.
- `qa_runtime.cjs` measures visible text runs, including nested spans and SVG labels, and reports failed pairs with text, foreground, effective background and ratio. Unannotated copy must not escape contrast checks. Supply a specific `contrast` observation per slide in `visual-review.json`, including review of any unmeasured backgrounds. Unresolved illegibility blocks delivery.
