# HTML runtime features

## Defaults

Include by default:

- fixed 1920 x 1080 stage scaled uniformly;
- keyboard and button navigation;
- `#hoja-NN` deep links;
- editable user-facing text;
- a contextual per-element text and visual-style toolbar plus a full typography editor constrained to approved families and readable semantic ranges;
- one bottom-right `previous · counter · next · menu` control cluster;
- unsaved-change indicator;
- save and save-as workflow;
- light, dark, and brand-custom themes;
- audience view by default, an always-visible Author menu section, and an explicit author state;
- edit preservation across regeneration;
- arrows-only mobile controls;
- fullscreen;
- reduced-motion support.

Ask only about optional features that are relevant: notes, presenter view, timer, overview, login, offline font embedding, PDF, PPTX, or generated illustrations.

## Controls menu

Keep primary previous/next navigation visible. The only desktop chrome is one control cluster ordered `previous · counter · next · menu`, aligned to the stage's lower-right content edge or footer. The icon menu is anchored to that cluster and opens upward and leftward. Do not create a second floating menu trigger, duplicate dots, or a separate toolbar.

Use native buttons with visible focus, accessible names, 44 x 44 minimum hit targets, inline SVG icons, pointer-down feedback, and restrained, interruptible menu motion. Close the menu on outside click and Escape and return focus to its trigger.

Possible items:

- Edit text;
- Typography for the selected element (`Alt/⌥ Y`): family, size, weight, leading, tracking, alignment, and italic;
- Save;
- Save as;
- Notes;
- Presenter view;
- Timer;
- Overview;
- Export PDF;
- Export PPTX;
- Appearance: Light, Dark, Brand;
- Edit brand theme;
- Fullscreen;
- Licenses and source;
- Keyboard help.

Hide unavailable modules rather than showing dead controls. Display each available keyboard shortcut as a compact `<kbd>` chip beside its menu item. Theme switching belongs inside this menu and also uses `T`. Keep the Author section present in audience and author states; invoking edit, save, save-as, file binding, or brand-theme editing explicitly activates author state. `?author=1` or `E` enables author mode directly; serializing a deck always returns its active state to audience mode.

## Editing contract

Every user-facing string must have a stable `data-edit-id`. Controls, generated page counters, speaker-only notes, and legal metadata are excluded unless explicitly editable.

The runtime stamps each editable node with `data-edit-baseline`. Preserve that attribute when changing layouts. Use `scripts/preserve_edits.py` whenever a generator updates an existing deck so unchanged generator copy can evolve while real browser edits survive.

When edit mode begins:

- make editable nodes contenteditable;
- show a clear but unobtrusive edit state;
- mark the document dirty on `input`;
- display `Cambios sin guardar`;
- prefix the browser title with a dot when dirty;
- warn before unload.

### Contextual per-element editing

Entering edit mode stamps safe visual targets with stable `data-style-id` values. A click on a `data-edit-id` selects that exact text component and opens a floating toolbar close to it. The toolbar identifies the selected copy and exposes approved family, bounded font size, text color, bold, italic, alignment, reset, and a route into the complete typography dialog. Native in-place text editing remains active; the toolbar never replaces the caret or browser text selection.

A click or double click on a safe `data-style-id` surface opens visual controls for fill or transparent background, border color, border width and style, radius, shadow preset, opacity, and reset. Auto-stamp only independent `data-qa-box` content regions; exclude headers, footers, brand marks, connectors, decorations, and any node with `data-edit-style="false"`. Authors may explicitly opt in another component with `data-edit-style` and may supply a stable `data-style-id` and `data-style-label`.

Keep the toolbar outside the transformed fixed stage. Position it above or below the selected component and clamp it to the viewport. At compact widths it becomes a readable bottom sheet with 44 px controls and no horizontal overflow. Clicking text always takes precedence over selecting its containing surface. Escape, leaving edit mode, changing slides, or the close button clears the transient selection.

Inline text and visual style changes are document changes. The runtime records independent content, text-style, and visual-style baselines so `scripts/preserve_edits.py` can carry browser decisions across structural regeneration without freezing untouched generator styles.

### Full per-element typography

Store the approved family list and semantic size bounds in `appearance.typography`. The runtime must never invent an unapproved brand font. Selecting **Tipografía del elemento** enters edit mode, asks the author to select one `data-edit-id`, and opens a native dialog for family, size, weight, line-height, letter-spacing, text color, alignment, italic, and reset. Inline adjustments are document changes and must survive serialization and regeneration.

Use these generic fallback bounds when no brand-specific scale has been approved: labels 14–180 px, body 18–64 px, H3 24–96 px, H2 36–144 px, and H1 48–180 px. A deck may narrow these ranges, but the configured minimum must remain readable and the maximum must protect the composition. Clamp editor inputs to the active semantic range and run rendered QA after changes because a legal font size can still create overflow or collisions.

## Save behavior

The browser cannot infer and overwrite an arbitrary local path without user permission.

Use this order:

1. If a previously authorized file handle exists, write to it on `Cmd/Ctrl+S`.
2. Otherwise offer `Vincular archivo existente` or `Guardar como…` through the File System Access API when available.
3. If unsupported or denied, download a complete updated HTML copy.
4. Before binding an existing file, verify that it is a compatible Presentation Studio deck and require confirmation if its title differs.
5. Never claim a fallback download overwrote the original.

Serialize the current DOM, including user edits and embedded project data, while removing transient open-menu and edit-mode states.

Theme changes are document changes. Mark them dirty, serialize the selected theme and custom tokens, and include them in downloaded or directly saved HTML.

## Internal states and arrow navigation

Classify every hidden or progressive state:

- `required`: part of the presentation path;
- `on-demand`: opened only through an explicit trigger;
- `speaker-only`: notes or presenter material;
- `decorative`: never consumes navigation.

On next:

1. reveal the next unrevealed `required` state;
2. otherwise move to the next slide.

On previous:

1. reverse the last revealed `required` state;
2. otherwise move to the previous slide at its final required state.

Support `#hoja-05/estado-02`. Ensure controls, deep links, overview, and exported state remain consistent.

## Export behavior

- PDF may use browser print or a bundled render script; motion becomes static.
- PPTX is optional because it adds weight and may reduce fidelity. Include its module only after confirmation.
- For progressive states, ask whether export should use final state only or split required states into separate pages.

## Mobile

Do not reflow slide content. Scale the fixed stage uniformly and reserve a compact strip outside it. On narrow or coarse-pointer screens show only previous and next buttons; hide counter, menu, status, and author chrome. Keep each visual button within a 44 x 44 hit target.

## Audience and author views

- Normal delivery opens in `audience` mode.
- Audience mode exposes the Author section for discoverability, but author actions explicitly transition the local runtime into author state before editing or writing.
- Author mode is explicit through `?author=1` or `E`.
- The generated HTML and every saved copy must reset to audience mode.
- Optional authentication is independent from author mode. A client-side gate is not real access control.

## Themes

Read `theme-system.md`. Every generated deck includes light, dark, and custom theme support unless the user explicitly requests a single locked theme. Never implement dark mode with CSS inversion.
